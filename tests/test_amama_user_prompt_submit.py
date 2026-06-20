#!/usr/bin/env python3
"""Real (no-mock) tests for scripts/amama_user_prompt_submit.py.

amama_user_prompt_submit.py is a Claude Code *UserPromptSubmit* hook: it reads a
JSON event on stdin, drops cron-injected turns (prompts whose text starts with a
known ``[<plugin>-<event>]`` prefix), and otherwise POSTs an empty body to the AI
Maestro server's ``/api/sessions/me/user-input`` presence endpoint with a
``Bearer $AID_AUTH`` header. It is fail-soft and always exits 0.

These tests use NO Python mocks. The network branch is exercised against a REAL
``http.server`` bound to ``127.0.0.1`` on an ephemeral port; the script is driven
exactly as the harness drives it — a real subprocess fed real stdin JSON with
``AIMAESTRO_API``/``AID_AUTH`` set in the child env — and we assert the real HTTP
request the server actually received (method, path, Authorization header) plus the
real exit code. The filter/skip branches are asserted by confirming the server
received *zero* requests. Only the remote service is replaced by a controlled
local endpoint; fork/exec, stdin parsing, the denylist filter, urllib POST, and
exit code are all the genuine code under test.

Run: python3 tests/test_amama_user_prompt_submit.py      (exit 0 = all pass)
"""

from __future__ import annotations

import contextlib
import http.server
import json
import subprocess
import sys
import threading
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import amama_user_prompt_submit as ups  # noqa: E402  # pyright: ignore[reportMissingImports]

_SCRIPT = _SCRIPTS / "amama_user_prompt_submit.py"


# --------------------------------------------------------------------------- #
# Fixtures — a REAL localhost presence endpoint + a real subprocess driver
# --------------------------------------------------------------------------- #
class _PresenceHandler(http.server.BaseHTTPRequestHandler):
    """Record every received request on the server, then reply with the 200 contract."""

    def do_POST(self) -> None:  # noqa: N802  (BaseHTTPRequestHandler API)
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length) if length else b""
        self.server.received.append(  # type: ignore[attr-defined]
            {
                "method": "POST",
                "path": self.path,
                "authorization": self.headers.get("Authorization", ""),
                "body": body,
            }
        )
        payload = json.dumps({"recorded_at_epoch": 1_700_000_000}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_args: object) -> None:  # silence the default stderr access log
        return


@contextlib.contextmanager
def presence_server():
    """Yield (base_url, received_list) for a real HTTP server on 127.0.0.1:<ephemeral>."""
    server = http.server.HTTPServer(("127.0.0.1", 0), _PresenceHandler)
    server.received = []  # type: ignore[attr-defined]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[0], server.server_address[1]
        yield f"http://{host}:{port}", server.received  # type: ignore[attr-defined]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _run_hook(stdin_text: str, *, api_base: str, aid_auth: str | None) -> subprocess.CompletedProcess[str]:
    """Run the script as Claude Code would: real subprocess, real stdin JSON, real child env."""
    env = {"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "AIMAESTRO_API": api_base}
    if aid_auth is not None:
        env["AID_AUTH"] = aid_auth
    return subprocess.run(
        [sys.executable, str(_SCRIPT)],
        input=stdin_text,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def test_normal_user_prompt_posts_presence_with_bearer():
    """A genuine user prompt with AID_AUTH set fires a real POST to the presence endpoint with the bearer header."""
    with presence_server() as (base, received):
        payload = json.dumps({"hook_event_name": "UserPromptSubmit", "prompt": "fix the login bug"})
        proc = _run_hook(payload, api_base=base, aid_auth="secret-token-123")
        assert proc.returncode == 0, f"hook must exit 0; got {proc.returncode}, stderr={proc.stderr!r}"
        assert proc.stdout == "", f"hook is fire-and-forget; expected empty stdout, got {proc.stdout!r}"
        assert len(received) == 1, f"genuine prompt must record presence exactly once; got {len(received)}"
        req = received[0]
        assert req["method"] == "POST"
        assert req["path"] == "/api/sessions/me/user-input"
        assert req["authorization"] == "Bearer secret-token-123"
        assert req["body"] == b"", "presence write sends an empty body (Content-Length: 0)"


def test_system_injected_cron_prompt_is_filtered_no_post():
    """A cron-injected prompt ([janitor-heartbeat] prefix) is recognized and must NOT touch the presence endpoint."""
    # In-process: the pure denylist predicate is True for every known system prefix...
    for prefix in ups.SYSTEM_PROMPT_PREFIXES:
        assert ups._is_system_injected(json.dumps({"prompt": f"  {prefix} do the chore"})) is True
    # ...and end-to-end the real subprocess must short-circuit before any HTTP request fires.
    with presence_server() as (base, received):
        payload = json.dumps({"hook_event_name": "UserPromptSubmit", "prompt": "[janitor-heartbeat] tick"})
        proc = _run_hook(payload, api_base=base, aid_auth="secret-token-123")
        assert proc.returncode == 0
        assert received == [], "system-injected turn must not reset the presence clock (zero requests)"


def test_malformed_stdin_fails_open_and_still_posts():
    """Unparseable stdin is treated as NOT system-injected (fail-open) so presence is still recorded, hook exits 0."""
    # The predicate must fail OPEN on garbage (returning True would silently drop a real user's presence write).
    assert ups._is_system_injected("this is { not valid json ]]") is False
    assert ups._is_system_injected(json.dumps(["not", "a", "dict"])) is False
    assert ups._is_system_injected(json.dumps({"prompt": 12345})) is False  # non-str prompt
    with presence_server() as (base, received):
        proc = _run_hook("this is { not valid json ]]", api_base=base, aid_auth="secret-token-123")
        assert proc.returncode == 0, f"malformed stdin must not crash the hook; got {proc.returncode}"
        assert len(received) == 1, "fail-open: a malformed payload still records presence (user is not idle)"
        assert received[0]["authorization"] == "Bearer secret-token-123"


def test_no_aid_auth_skips_silently_without_network():
    """Without AID_AUTH the session isn't AI Maestro-managed: the hook skips the POST entirely and exits 0."""
    with presence_server() as (base, received):
        payload = json.dumps({"hook_event_name": "UserPromptSubmit", "prompt": "a perfectly real user prompt"})
        proc = _run_hook(payload, api_base=base, aid_auth=None)  # AID_AUTH unset in child env
        assert proc.returncode == 0, f"unmanaged session must still exit 0; got {proc.returncode}"
        assert proc.stdout == ""
        assert received == [], "no AID_AUTH means nothing to record — the endpoint must never be hit"


# --------------------------------------------------------------------------- #
# Runner + result table
# --------------------------------------------------------------------------- #
_SLOW = {"test_normal_user_prompt_posts_presence_with_bearer",
         "test_system_injected_cron_prompt_is_filtered_no_post",
         "test_malformed_stdin_fails_open_and_still_posts",
         "test_no_aid_auth_skips_silently_without_network"}


def _table(rows: list[tuple[str, str, str]]) -> str:
    name_w = max(len(r[0]) for r in rows)
    desc_w = max(len(r[2]) for r in rows)
    top = f"┏━{'━' * name_w}━┳━━━━━━━━┳━{'━' * desc_w}━┓"
    head = f"┃ {'Test':<{name_w}} ┃ Status ┃ {'Description':<{desc_w}} ┃"
    sep = f"┡━{'━' * name_w}━╇━━━━━━━━╇━{'━' * desc_w}━┩"
    bot = f"└─{'─' * name_w}─┴────────┴─{'─' * desc_w}─┘"
    out = [top, head, sep]
    for name, status, desc in rows:
        out.append(f"│ {name:<{name_w}} │ {status:<6} │ {desc:<{desc_w}} │")
    out.append(bot)
    return "\n".join(out)


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    rows: list[tuple[str, str, str]] = []
    failed = 0
    for fn in tests:
        desc = (fn.__doc__ or "").strip().split("\n")[0]
        marker = " 🐌" if fn.__name__ in _SLOW else ""
        try:
            fn()
            rows.append((fn.__name__, "PASS", f"{desc}{marker}"))
        except AssertionError as exc:
            failed += 1
            rows.append((fn.__name__, "FAIL", f"{desc}  [{exc}]"))
        except Exception as exc:  # noqa: BLE001
            failed += 1
            rows.append((fn.__name__, "ERROR", f"{desc}  [{type(exc).__name__}: {exc}]"))
    print(_table(rows))
    print(f"\n{len(tests) - failed}/{len(tests)} passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
