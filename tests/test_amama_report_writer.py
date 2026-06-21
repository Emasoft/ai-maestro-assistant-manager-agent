#!/usr/bin/env python3
"""Real (no-mock) tests for scripts/amama_report_writer.py.

Each test instantiates the ACTUAL ``ReportWriter`` against a throwaway temp
directory (via ``CLAUDE_PROJECT_DIR``), runs the real methods, and asserts the
real filesystem outcome (file written under ``reports/<component>/``, timestamped
filename shape, content round-trip) and the real stdout/stderr summary format.

Run: python3 tests/test_amama_report_writer.py      (exit 0 = all pass)
"""

from __future__ import annotations

import contextlib
import io
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import amama_report_writer as arw  # noqa: E402  # pyright: ignore[reportMissingImports]
from _harness import run_standalone  # noqa: E402

# Filename shape the script promises: "<script_name>_<YYYYMMDD_HHMMSS>.md"
_FILENAME_RE = re.compile(r"^(?P<name>.+)_(?P<ts>\d{8}_\d{6}[+-]\d{4})\.md$")


@contextlib.contextmanager
def temp_project():
    """Yield a fresh temp dir pinned as CLAUDE_PROJECT_DIR; restore env + clean up."""
    # .resolve() so the dir matches project_root()'s canonical (symlink-resolved)
    # path — on macOS mkdtemp yields /var/... but project_root() resolves it to
    # /private/var/..., which would break a Path-equality assert otherwise.
    root = Path(tempfile.mkdtemp(prefix="arw-test-")).resolve()
    prev = os.environ.get("CLAUDE_PROJECT_DIR")
    os.environ["CLAUDE_PROJECT_DIR"] = str(root)
    try:
        yield root
    finally:
        if prev is None:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            os.environ["CLAUDE_PROJECT_DIR"] = prev
        shutil.rmtree(root, ignore_errors=True)


def test_writes_report_under_project_reports():
    """Happy path: write_report creates a timestamped .md under <project>/reports/<component>/ with exact content."""
    with temp_project() as root:
        writer = arw.ReportWriter("amama_planning_status")
        content = "# Planning status\n\nfull verbose body\nwith multiple lines\n"
        path = writer.write_report(content)

        # Real file, real location, real content (no mocks).
        assert path.exists() and path.is_file()
        assert path.parent == root / "reports" / "amama_planning_status"
        assert path.read_text(encoding="utf-8") == content

        # Filename shape: "<script_name>_<YYYYMMDD_HHMMSS>.md".
        m = _FILENAME_RE.match(path.name)
        assert m is not None, f"filename {path.name!r} does not match the documented shape"
        assert m.group("name") == "amama_planning_status"
        # Path returned by write_report is exactly the one get_report_path computes.
        assert path == writer.get_report_path()
        # Timestamp is frozen at construction → repeated get_report_path is stable.
        assert writer.get_report_path() == writer.get_report_path()


def test_writes_under_cwd_when_project_dir_unset():
    """With CLAUDE_PROJECT_DIR unset, project_root() falls back to cwd, so the report
    lands under <cwd>/reports/<component>/ — NOT /tmp (the silent fallback was removed
    for fail-fast)."""
    prev = os.environ.get("CLAUDE_PROJECT_DIR")
    saved_cwd = Path.cwd()
    root = Path(tempfile.mkdtemp(prefix="arw-cwd-")).resolve()
    os.environ.pop("CLAUDE_PROJECT_DIR", None)
    os.chdir(root)
    try:
        writer = arw.ReportWriter("amama_stop_check")
        written = writer.write_report("fallback body\n")
        assert written.exists()
        assert written.parent == root / "reports" / "amama_stop_check"
        assert written.read_text(encoding="utf-8") == "fallback body\n"
        assert _FILENAME_RE.match(written.name) is not None
    finally:
        os.chdir(saved_cwd)
        if prev is None:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            os.environ["CLAUDE_PROJECT_DIR"] = prev
        shutil.rmtree(root, ignore_errors=True)


def test_summary_and_failure_print_expected_format():
    """print_summary → stdout '[DONE] <name> - <summary>' + 'Report:'; print_failure → same on stderr with '[FAILED]'."""
    with temp_project():
        writer = arw.ReportWriter("amama_orchestration_status")
        report_path = writer.write_report("body\n")

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            writer.print_summary("3 agents idle", report_path)
        stdout = out.getvalue()
        assert "[DONE] amama_orchestration_status - 3 agents idle" in stdout
        assert f"Report: {report_path}" in stdout

        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            writer.print_failure("planning dir missing", report_path)
        stderr = err.getvalue()
        assert "[FAILED] amama_orchestration_status - planning dir missing" in stderr
        assert f"Report: {report_path}" in stderr

        # report_path is optional: omitting it prints no "Report:" line.
        out2 = io.StringIO()
        with contextlib.redirect_stdout(out2):
            writer.print_summary("no path given")
        assert "Report:" not in out2.getvalue()


if __name__ == "__main__":
    sys.exit(run_standalone(globals()))
