#!/usr/bin/env python3
"""Real (no-mock) tests for scripts/amama_orchestration_status.py.

Each test builds a throwaway project dir under the system temp dir, optionally
writes a synthetic ``.claude/orchestrator-exec-phase.local.md`` state file, then
runs the ACTUAL CLI as a subprocess (with cwd + CLAUDE_PROJECT_DIR pinned to the
temp dir) and asserts against the real outcome: exit code, the stdout summary,
the stderr error, and the verbose report file the real ReportWriter writes.

Running via subprocess (rather than calling main() in-process) is deliberate:
the script reads Path.cwd() and calls sys.exit(), so a subprocess exercises the
genuine entry point with zero global-state pollution (no sys.argv / chdir leak
between tests). Nothing is mocked — the real ReportWriter performs real file I/O
into the temp project's design/reports/ directory.

Run: python3 tests/test_amama_orchestration_status.py      (exit 0 = all pass)
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
_SCRIPT = _SCRIPTS / "amama_orchestration_status.py"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import run_standalone  # noqa: E402


# --------------------------------------------------------------------------- #
# Fixtures / helpers
# --------------------------------------------------------------------------- #
def _make_project(state_body: str | None) -> Path:
    """Create a temp project dir; if state_body is not None, write the state file."""
    root = Path(tempfile.mkdtemp(prefix="amama-os-test-"))
    (root / ".claude").mkdir(parents=True, exist_ok=True)
    if state_body is not None:
        (root / ".claude" / "orchestrator-exec-phase.local.md").write_text(state_body, encoding="utf-8")
    return root


def _run(root: Path, *argv: str) -> subprocess.CompletedProcess[str]:
    """Invoke the real CLI with cwd + CLAUDE_PROJECT_DIR pinned to the temp project."""
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(root)}
    return subprocess.run(
        [sys.executable, str(_SCRIPT), *argv],
        cwd=str(root),
        env=env,
        capture_output=True,
        text=True,
    )


def _report_text(root: Path) -> str:
    """Return the single written report file's content (asserts exactly one exists)."""
    reports = sorted((root / "design" / "reports").glob("orchestration-status_*.md"))
    assert len(reports) == 1, f"expected exactly one report, found {len(reports)}"
    return reports[0].read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def test_error_when_no_state_file():
    """Missing orchestrator-exec-phase state file -> rc 1, stderr message, no report."""
    root = _make_project(state_body=None)
    try:
        cp = _run(root)
        assert cp.returncode == 1, f"expected rc 1, got {cp.returncode}"
        assert "Not in Orchestration Phase" in cp.stderr
        assert not (root / "design" / "reports").exists()
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_populated_state_parses_plan_and_status():
    """A state file with Plan ID:/Status: is parsed into the summary AND the report."""
    root = _make_project("Plan ID: plan-42\nStatus: in-progress\n")
    try:
        cp = _run(root, "--verbose")
        assert cp.returncode == 0, f"expected rc 0, got {cp.returncode} ({cp.stderr})"
        # Summary line on stdout echoes the real parsed values.
        assert "Plan: plan-42, Status: in-progress" in cp.stdout
        # Verbose report contains the parsed values + the verbose state-file footer.
        report = _report_text(root)
        assert "Plan ID: plan-42" in report
        assert "Status: in-progress" in report
        assert "ORCHESTRATION PHASE STATUS" in report
        assert "State file:" in report  # --verbose footer present
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_empty_state_file_falls_back_to_defaults():
    """An existing state file with no Plan ID:/Status: lines uses defaults plan-unknown/ready."""
    root = _make_project("# orchestrator exec phase\nsome unrelated content\n")
    try:
        cp = _run(root)
        assert cp.returncode == 0, f"expected rc 0, got {cp.returncode} ({cp.stderr})"
        assert "Plan: plan-unknown, Status: ready" in cp.stdout
        report = _report_text(root)
        assert "Plan ID: plan-unknown" in report
        assert "Status: ready" in report
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_agents_only_flag_omits_module_sections():
    """--agents-only keeps the AGENTS section but drops the header/MODULE sections."""
    root = _make_project("Plan ID: plan-7\nStatus: ready\n")
    try:
        agents = _run(root, "--agents-only")
        assert agents.returncode == 0, f"rc {agents.returncode} ({agents.stderr})"
        a_report = _report_text(root)
        assert "REGISTERED AGENTS" in a_report  # agents section kept
        assert "ORCHESTRATION PHASE STATUS" not in a_report  # header dropped
        assert "MODULE STATUS" not in a_report  # module section dropped

        # Contrast: --modules-only is the mirror image (header/modules kept, agents dropped).
        root2 = _make_project("Plan ID: plan-7\nStatus: ready\n")
        try:
            mods = _run(root2, "--modules-only")
            assert mods.returncode == 0, f"rc {mods.returncode} ({mods.stderr})"
            m_report = _report_text(root2)
            assert "MODULE STATUS" in m_report
            assert "REGISTERED AGENTS" not in m_report
        finally:
            shutil.rmtree(root2, ignore_errors=True)
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(run_standalone(globals()))
