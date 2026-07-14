#!/usr/bin/env python3
"""Real (no-mock) tests for scripts/amama_user_prompt_submit.py.

amama_user_prompt_submit.py is a Claude Code *UserPromptSubmit* hook: it reads a
JSON event on stdin, drops cron-injected turns (prompts whose text starts with a
known ``[<plugin>-<event>]`` prefix), and otherwise records the user's last-input
timestamp through the FROZEN CLI — ``aimaestro-agent.sh session user-input`` —
never a direct ``/api/`` call (R23, IRON). It is fail-soft and always exits 0.

These tests use NO Python mocks. The CLI branch is exercised against a REAL
executable stub named ``aimaestro-agent.sh``, placed first on the child's
``PATH``, which appends its own argv to a file. The script is driven exactly as
the harness drives it — a real subprocess fed real stdin JSON with a real child
env — and we assert the real invocation the stub actually received (argv) plus
the real exit code. The filter/skip branches are asserted by confirming the stub
was invoked *zero* times. Only the external CLI is replaced by a controlled
local one; fork/exec, stdin parsing, the denylist filter, ``shutil.which``
resolution, the subprocess call, and the exit code are all genuine code under
test.

Regression guard (repo #21 / ai-maestro R23.7-8): this hook used to hand-roll
``POST /api/sessions/me/user-input`` with its own bearer header, coupling the
plugin to a server route it does not own. It sat under a stale
``DECOUPLE-BLOCKED`` marker waiting for a CLI verb that had *already shipped*.
These tests pin the CLI contract so it cannot silently regress to a direct POST.

Run: python3 tests/test_amama_user_prompt_submit.py      (exit 0 = all pass)
"""

from __future__ import annotations

import contextlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import amama_user_prompt_submit as ups  # noqa: E402  # pyright: ignore[reportMissingImports]
from _harness import run_standalone  # noqa: E402

_SCRIPT = _SCRIPTS / "amama_user_prompt_submit.py"

# The hook resolves this exact name via shutil.which(); the stub must match it.
_CLI_NAME = "aimaestro-agent.sh"


# --------------------------------------------------------------------------- #
# Fixtures — a REAL executable CLI stub on PATH + a real subprocess driver
# --------------------------------------------------------------------------- #
@contextlib.contextmanager
def cli_stub(*, stdout_noise: str = "", exit_code: int = 0):
    """Yield (bin_dir, calls_file) with a real executable `aimaestro-agent.sh` on it.

    The stub appends its argv (one call per line) to calls_file, so we assert on
    the invocation the hook *actually* made rather than on a mock's bookkeeping.
    """
    d = Path(tempfile.mkdtemp(prefix="cli-stub-"))
    try:
        calls = d / "calls.txt"
        stub = d / _CLI_NAME
        stub.write_text(
            "#!/bin/sh\n"
            f'printf "%s\\n" "$*" >> "{calls}"\n'
            + (f'printf "%s" "{stdout_noise}"\n' if stdout_noise else "")
            + f"exit {exit_code}\n",
            encoding="utf-8",
        )
        stub.chmod(0o755)
        yield d, calls
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _calls_of(calls_file: Path) -> list[str]:
    """The argv lines the stub actually recorded (empty list if never invoked)."""
    if not calls_file.exists():
        return []
    return [ln for ln in calls_file.read_text(encoding="utf-8").splitlines() if ln.strip()]


def _run_hook(
    stdin_text: str,
    *,
    bin_dir: Path | None,
    aid_auth: str | None,
) -> subprocess.CompletedProcess[str]:
    """Run the script as Claude Code would: real subprocess, real stdin JSON, real child env."""
    base_path = "/usr/bin:/bin:/usr/sbin:/sbin"
    env = {"PATH": f"{bin_dir}{os.pathsep}{base_path}" if bin_dir else base_path}
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
def test_normal_user_prompt_invokes_frozen_cli():
    """A genuine user prompt with AID_AUTH set invokes `aimaestro-agent.sh session user-input` exactly once."""
    with cli_stub() as (bin_dir, calls):
        payload = json.dumps({"hook_event_name": "UserPromptSubmit", "prompt": "fix the login bug"})
        proc = _run_hook(payload, bin_dir=bin_dir, aid_auth="secret-token-123")
        assert proc.returncode == 0, f"hook must exit 0; got {proc.returncode}, stderr={proc.stderr!r}"
        assert proc.stdout == "", f"hook is fire-and-forget; expected empty stdout, got {proc.stdout!r}"
        made = _calls_of(calls)
        assert len(made) == 1, f"genuine prompt must record presence exactly once; got {len(made)}"
        assert made[0] == "session user-input", f"must call the frozen verb; got {made[0]!r}"


def test_hook_never_calls_the_api_directly():
    """The hook contains no /api/ URL and no bearer header — the CLI owns auth and the route (R23)."""
    src = _SCRIPT.read_text(encoding="utf-8")
    assert "/api/" not in src, "R23 (IRON): a plugin must never call the server's HTTP surface directly"
    assert "Authorization" not in src, "the CLI resolves auth; the plugin must not assemble a bearer header"
    assert "urllib" not in src, "the direct-POST path must be gone, not merely unused"


def test_system_injected_cron_prompt_is_filtered_no_cli():
    """A cron-injected prompt ([janitor-heartbeat] prefix) is recognized and must NOT invoke the CLI."""
    # In-process: the pure denylist predicate is True for every known system prefix...
    for prefix in ups.SYSTEM_PROMPT_PREFIXES:
        assert ups._is_system_injected(json.dumps({"prompt": f"  {prefix} do the chore"})) is True
    # ...and end-to-end the real subprocess must short-circuit before the CLI is spawned.
    with cli_stub() as (bin_dir, calls):
        payload = json.dumps({"hook_event_name": "UserPromptSubmit", "prompt": "[janitor-heartbeat] tick"})
        proc = _run_hook(payload, bin_dir=bin_dir, aid_auth="secret-token-123")
        assert proc.returncode == 0
        assert _calls_of(calls) == [], "system-injected turn must not reset the presence clock (zero calls)"


def test_malformed_stdin_fails_open_and_still_invokes_cli():
    """Unparseable stdin is treated as NOT system-injected (fail-open) so presence is still recorded, hook exits 0."""
    # The predicate must fail OPEN on garbage (returning True would silently drop a real user's presence write).
    assert ups._is_system_injected("this is { not valid json ]]") is False
    assert ups._is_system_injected(json.dumps(["not", "a", "dict"])) is False
    assert ups._is_system_injected(json.dumps({"prompt": 12345})) is False  # non-str prompt
    with cli_stub() as (bin_dir, calls):
        proc = _run_hook("this is { not valid json ]]", bin_dir=bin_dir, aid_auth="secret-token-123")
        assert proc.returncode == 0, f"malformed stdin must not crash the hook; got {proc.returncode}"
        assert _calls_of(calls) == ["session user-input"], "fail-open: a malformed payload still records presence"


def test_no_aid_auth_skips_silently_without_spawning_cli():
    """Without AID_AUTH the session isn't AI Maestro-managed: the hook skips the CLI entirely and exits 0."""
    with cli_stub() as (bin_dir, calls):
        payload = json.dumps({"hook_event_name": "UserPromptSubmit", "prompt": "a perfectly real user prompt"})
        proc = _run_hook(payload, bin_dir=bin_dir, aid_auth=None)  # AID_AUTH unset in child env
        assert proc.returncode == 0, f"unmanaged session must still exit 0; got {proc.returncode}"
        assert proc.stdout == ""
        assert _calls_of(calls) == [], "no AID_AUTH means nothing to record — the CLI must never be spawned"


def test_missing_cli_degrades_silently():
    """On a host with no aimaestro-agent.sh on PATH the hook degrades silently and still exits 0."""
    payload = json.dumps({"hook_event_name": "UserPromptSubmit", "prompt": "a real prompt on a non-maestro host"})
    proc = _run_hook(payload, bin_dir=None, aid_auth="secret-token-123")  # CLI absent from PATH
    assert proc.returncode == 0, f"a missing CLI must never block prompt submission; got {proc.returncode}"
    assert proc.stdout == "", f"degradation must be silent; got {proc.stdout!r}"


def test_cli_output_never_leaks_into_the_prompt_context():
    """A noisy or failing CLI must not leak stdout — a UserPromptSubmit hook's stdout is injected into the user's turn."""
    # This is why the subprocess call uses capture_output=True: anything the CLI prints
    # would otherwise be silently prepended to the user's prompt as context.
    with cli_stub(stdout_noise="ERROR: 401 unauthorized blah blah", exit_code=1) as (bin_dir, calls):
        payload = json.dumps({"hook_event_name": "UserPromptSubmit", "prompt": "real prompt"})
        proc = _run_hook(payload, bin_dir=bin_dir, aid_auth="secret-token-123")
        assert proc.returncode == 0, "a failing CLI is non-fatal — presence is best-effort"
        assert proc.stdout == "", f"CLI output must NEVER reach the prompt context; leaked {proc.stdout!r}"
        assert _calls_of(calls) == ["session user-input"], "the CLI was still invoked"


# --------------------------------------------------------------------------- #
# Slow tests (real subprocess + real CLI-stub round-trips) get a 🐌 marker.
# --------------------------------------------------------------------------- #
_SLOW = {
    "test_normal_user_prompt_invokes_frozen_cli",
    "test_system_injected_cron_prompt_is_filtered_no_cli",
    "test_malformed_stdin_fails_open_and_still_invokes_cli",
    "test_no_aid_auth_skips_silently_without_spawning_cli",
    "test_missing_cli_degrades_silently",
    "test_cli_output_never_leaks_into_the_prompt_context",
}


if __name__ == "__main__":
    sys.exit(run_standalone(globals(), slow=_SLOW))
