#!/usr/bin/env python3
"""Real (no-mock) tests for scripts/amama_stop_check.py.

amama_stop_check.py is a Claude Code *Stop* hook: it reads a JSON event on
stdin, queries two external CLIs (``amp-inbox --count`` and ``gh issue list``)
to decide whether coordination work is still pending, and either ALLOWS the
stop (exit 0, no output) or BLOCKS it (exit 2 + a block-decision JSON on stdout
plus a written report file).

These tests exercise the REAL decision logic with NO Python mocks. Instead of
patching ``subprocess``/``check_*`` (which would bypass the very subprocess +
JSON-parsing + decision code under test), each test prepends a throwaway dir of
tiny REAL executables to ``$PATH`` so the script's ``subprocess.run(["amp-inbox",
...])`` / ``subprocess.run(["gh", ...])`` resolve to deterministic local
stand-ins. Real fork/exec, real stdout parsing, real branch selection — only the
remote service is replaced by a controlled local endpoint. stdin is driven with
real payloads and stdout/exit code are asserted against the real hook contract.

Run: python3 tests/test_amama_stop_check.py      (exit 0 = all pass)
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import stat
import tempfile
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
import sys

sys.path.insert(0, str(_SCRIPTS))

import amama_stop_check as sc  # noqa: E402  # pyright: ignore[reportMissingImports]


# --------------------------------------------------------------------------- #
# Fixtures — a real PATH-injected CLI sandbox + a real stdin/stdout driver
# --------------------------------------------------------------------------- #
def _write_exec(path: Path, body: str) -> None:
    """Write an executable POSIX shell stub and chmod +x it (a real binary on PATH)."""
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


@contextlib.contextmanager
def hook_env(*, amp_stdout: str = "0", amp_rc: int = 0,
             gh_stdout: str = "[]", gh_rc: int = 0,
             provide_amp: bool = True, provide_gh: bool = True):
    """Yield (project_dir, run) with amp-inbox/gh shadowed by real PATH executables.

    ``run(stdin_text)`` feeds a real stdin payload to ``sc.main()``, captures the
    real stdout, and returns ``(exit_code, stdout_text)``. ``CLAUDE_PROJECT_DIR``
    is pinned to a throwaway dir so the block-path report write lands there.
    """
    sandbox = Path(tempfile.mkdtemp(prefix="amama-stop-"))
    bindir = sandbox / "bin"
    bindir.mkdir(parents=True)
    project = sandbox / "project"
    project.mkdir()

    if provide_amp:
        # exit with amp_rc after printing amp_stdout — a real `amp-inbox --count` stand-in
        _write_exec(bindir / "amp-inbox", f"#!/bin/sh\nprintf '%s\\n' '{amp_stdout}'\nexit {amp_rc}\n")
    if provide_gh:
        # `gh` ignores args and prints the canned JSON array — a real `gh issue list` stand-in
        gh_literal = gh_stdout.replace("'", "'\\''")
        _write_exec(bindir / "gh", f"#!/bin/sh\nprintf '%s' '{gh_literal}'\nexit {gh_rc}\n")

    saved = {k: os.environ.get(k) for k in ("PATH", "CLAUDE_PROJECT_DIR")}
    # Put our sandbox FIRST so the script resolves these names to our stubs, not the
    # real machine CLIs (both of which exist here and would be non-deterministic).
    os.environ["PATH"] = f"{bindir}{os.pathsep}{os.environ['PATH']}"
    os.environ["CLAUDE_PROJECT_DIR"] = str(project)

    def run(stdin_text: str) -> tuple[int, str]:
        # Feed a real stdin payload and capture the real stdout the hook emits.
        out = io.StringIO()
        old_stdin = sys.stdin
        sys.stdin = io.StringIO(stdin_text)
        try:
            with contextlib.redirect_stdout(out):
                rc = sc.main()
        finally:
            sys.stdin = old_stdin
        return rc, out.getvalue()

    try:
        yield project, run
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(sandbox, ignore_errors=True)


# --------------------------------------------------------------------------- #
# Tests — the real allow / block / edge / malformed decision branches
# --------------------------------------------------------------------------- #
def test_allow_stop_when_no_pending_work():
    """Clean inbox (0) + no open issues → main() returns 0 and emits no stdout (allow)."""
    with hook_env(amp_stdout="0", gh_stdout="[]") as (_proj, run):
        rc, out = run('{"hook_event_name": "Stop"}')
        assert rc == 0, f"expected allow (0), got {rc}"
        assert out.strip() == "", f"allow path must be silent, got: {out!r}"


def test_block_stop_on_unread_messages():
    """Unread inbox count (5) → main() returns 2 with a block decision + a written report."""
    with hook_env(amp_stdout="5", gh_stdout="[]") as (project, run):
        rc, out = run("{}")
        assert rc == 2, f"unread messages must block (2), got {rc}"
        payload = json.loads(out)
        assert payload["decision"] == "block"
        assert "5 unread message(s)" in payload["reason"]
        assert payload["hookSpecificOutput"]["permissionDecision"] == "deny"
        # the real block path writes a detailed report under design/reports/
        report = Path(payload["report"])
        assert report.exists() and report.parent == project / "design" / "reports"
        saved = json.loads(report.read_text(encoding="utf-8"))
        assert saved["details"]["unread_messages"] == 5


def test_block_stop_on_open_github_issues():
    """Open assistant-manager issues from `gh` JSON → main() returns 2 citing GitHub issues."""
    issues = json.dumps([{"title": "Wire up approval queue", "number": 42},
                         {"title": "Fix kanban round-trip", "number": 43}])
    with hook_env(amp_stdout="0", gh_stdout=issues) as (_proj, run):
        rc, out = run('{"hook_event_name": "Stop"}')
        assert rc == 2, f"open issues must block (2), got {rc}"
        payload = json.loads(out)
        assert payload["decision"] == "block"
        assert "2 open GitHub issue(s)" in payload["reason"]


def test_subagent_exit_is_always_allowed():
    """An event carrying agent_id (a subagent) short-circuits to allow (0) before any CLI runs."""
    # If the short-circuit regresses, these stubs would BLOCK — so reaching rc==0 proves
    # the agent_id branch fired and the inbox/gh checks were never consulted.
    with hook_env(amp_stdout="9", gh_stdout=json.dumps([{"title": "x", "number": 1}])) as (project, run):
        rc, out = run('{"hook_event_name": "Stop", "agent_id": "sub-123"}')
        assert rc == 0, f"subagent stop must be allowed (0), got {rc}"
        assert out.strip() == "", "subagent allow path must be silent"
        # no report written because the blocking branch was never entered
        assert not (project / "design" / "reports").exists()


def test_malformed_stdin_falls_back_and_does_not_crash():
    """Non-JSON stdin is tolerated (treated as {}) — checks still run; clean CLIs → allow (0)."""
    with hook_env(amp_stdout="0", gh_stdout="[]") as (_proj, run):
        rc, out = run("this is not json at all {{{")
        assert rc == 0, f"malformed input with clean state must allow (0), got {rc}"
        assert out.strip() == "", "no blocking issues → silent allow"


# --------------------------------------------------------------------------- #
# Runner + result table
# --------------------------------------------------------------------------- #
_SLOW: set[str] = set()  # none of these are slow; placeholder for the 🐌 marker convention


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
        snail = " 🐌" if fn.__name__ in _SLOW else ""
        desc = (fn.__doc__ or "").strip().split("\n")[0] + snail
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
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
