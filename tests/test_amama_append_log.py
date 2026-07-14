#!/usr/bin/env python3
"""Real (no-mock) tests for scripts/amama_append_log.py.

Each test runs the ACTUAL append against a throwaway temp dir and asserts the
real filesystem outcome: an entry is appended (not overwritten), prior content is
preserved, a newline delimiter is ensured, and the CLI prints ONLY the short
``wrote <id> to <path>`` confirmation (never the growing log — the K9 fix).

Run: python3 tests/test_amama_append_log.py      (exit 0 = all pass)
"""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
import tempfile
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import amama_append_log as al  # noqa: E402  # pyright: ignore[reportMissingImports]
from _harness import run_standalone  # noqa: E402


def test_append_creates_and_preserves_prior_entries():
    """append_entry creates the log (incl. parent dir), then appends without overwriting earlier records."""
    d = Path(tempfile.mkdtemp(prefix="al-test-"))
    try:
        log = d / "sub" / "session.log"  # parent dir does not exist yet
        al.append_entry(log, '{"id": 1}')
        al.append_entry(log, '{"id": 2}\n')  # already newline-terminated
        assert log.read_text(encoding="utf-8") == '{"id": 1}\n{"id": 2}\n'
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_append_preserves_existing_file_and_leaves_no_temp():
    """Appending to a pre-existing multi-line log keeps all old bytes, adds one line, leaves no temp litter."""
    d = Path(tempfile.mkdtemp(prefix="al-test-"))
    try:
        log = d / "session.log"
        log.write_text("old line 1\nold line 2\n", encoding="utf-8")
        al.append_entry(log, "new line 3")
        assert log.read_text(encoding="utf-8") == "old line 1\nold line 2\nnew line 3\n"
        assert list(d.glob("*.tmp*")) == []
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_cli_prints_only_confirmation():
    """The CLI writes the entry and prints EXACTLY one 'wrote <id> to <path>' line — never the log body."""
    d = Path(tempfile.mkdtemp(prefix="al-test-"))
    try:
        log = d / "session.log"
        log.write_text("secret prior content that must not be echoed\n", encoding="utf-8")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = al.main([str(log), '{"turn": 7}', "--id", "turn-7"])
        out = buf.getvalue()
        assert rc == 0
        assert out == f"wrote turn-7 to {log}\n"
        assert "secret prior content" not in out  # the log body never reaches stdout
        assert log.read_text(encoding="utf-8").endswith('{"turn": 7}\n')
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_cli_stdin_entry():
    """--stdin reads the entry from stdin (supports multi-line JSON records)."""
    d = Path(tempfile.mkdtemp(prefix="al-test-"))
    try:
        log = d / "session.log"
        buf = io.StringIO()
        saved_stdin = sys.stdin
        sys.stdin = io.StringIO('{"multi":\n  "line"}')
        try:
            with contextlib.redirect_stdout(buf):
                rc = al.main([str(log), "--stdin", "--id", "e1"])
        finally:
            sys.stdin = saved_stdin
        assert rc == 0
        assert log.read_text(encoding="utf-8") == '{"multi":\n  "line"}\n'
        assert buf.getvalue() == f"wrote e1 to {log}\n"
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(run_standalone(globals()))
