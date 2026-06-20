#!/usr/bin/env python3
"""Real (no-mock) tests for scripts/amama_session_start.py.

``amama_session_start.py`` is a Claude Code SessionStart hook: it reads the hook
payload as JSON from stdin, discards it (memory is now recall-on-demand, not
auto-loaded), and exits 0. There are exactly three real branches: a normal
session start (no ``agent_id``), a subagent run (payload carries ``agent_id``),
and a malformed-stdin fallback that must NOT crash. Each test drives the ACTUAL
script — either via ``subprocess`` over real stdin (the true hook contract: JSON
in, exit code out) or by calling ``main()`` in-process with a real patched
``sys.stdin`` — and asserts the real exit code / stdout. Nothing is mocked.

Run: python3 tests/test_amama_session_start.py      (exit 0 = all pass)
"""

from __future__ import annotations

import contextlib
import io
import subprocess
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import amama_session_start as ss  # noqa: E402  # pyright: ignore[reportMissingImports]

_SCRIPT = _SCRIPTS / "amama_session_start.py"


def _run_hook(stdin_text: str) -> subprocess.CompletedProcess[str]:
    """Run the script exactly as Claude Code would: real subprocess, stdin JSON."""
    return subprocess.run(
        [sys.executable, str(_SCRIPT)],
        input=stdin_text,
        capture_output=True,
        text=True,
        check=False,
    )


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def test_normal_session_start_exits_zero_silently():
    """A real SessionStart payload (no agent_id) over subprocess stdin exits 0 with empty stdout."""
    payload = '{"hook_event_name": "SessionStart", "session_id": "abc-123", "cwd": "/tmp"}'
    proc = _run_hook(payload)
    assert proc.returncode == 0, f"expected exit 0, got {proc.returncode}; stderr={proc.stderr!r}"
    # The hook loads nothing, so it must emit nothing on stdout.
    assert proc.stdout == "", f"expected empty stdout, got {proc.stdout!r}"


def test_subagent_run_short_circuits():
    """A payload carrying agent_id takes the subagent early-return branch and still exits 0."""
    # Drive main() in-process with a REAL stdin so the agent_id branch executes for coverage,
    # then corroborate the same branch end-to-end via subprocess.
    original_stdin = sys.stdin
    sys.stdin = io.StringIO('{"agent_id": "sub-agent-7", "hook_event_name": "SessionStart"}')
    try:
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = ss.main()
    finally:
        sys.stdin = original_stdin
    assert rc == 0
    assert out.getvalue() == ""
    # End-to-end: same payload through the real process boundary.
    proc = _run_hook('{"agent_id": "sub-agent-7"}')
    assert proc.returncode == 0
    assert proc.stdout == ""


def test_malformed_stdin_does_not_crash():
    """Invalid JSON on stdin is swallowed (treated as empty payload) and the hook exits 0, not 1."""
    proc = _run_hook("this is { not valid json ]]")
    assert proc.returncode == 0, (
        f"malformed stdin must not crash the hook; got exit {proc.returncode}, "
        f"stderr={proc.stderr!r}"
    )
    assert proc.stdout == ""
    # Empty stdin (common for SessionStart) is also a valid, exit-0 path.
    assert _run_hook("").returncode == 0


# --------------------------------------------------------------------------- #
# Runner + result table
# --------------------------------------------------------------------------- #
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
        try:
            fn()
            rows.append((fn.__name__, "PASS", desc))
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
