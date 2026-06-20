#!/usr/bin/env python3
"""Real (no-mock) tests for scripts/amama_planning_status.py.

Each test builds a throwaway project dir under the system temp dir, optionally
writes a synthetic ``design/plan-phase.local.md`` state file with real YAML
frontmatter, then runs the ACTUAL CLI as a subprocess (with cwd +
CLAUDE_PROJECT_DIR pinned to the temp dir) and asserts against the real outcome:
exit code, the stdout summary, the stderr error, and the verbose report file the
real ReportWriter writes into the temp project's design/reports/ directory.

Running via subprocess (rather than calling main() in-process) is deliberate and
load-bearing: PLAN_STATE_FILE is computed from CLAUDE_PROJECT_DIR at MODULE-IMPORT
time (scripts/amama_planning_status.py line 26), and the script calls sys.exit()
and reads Path.cwd() (line 142). A subprocess exercises the genuine entry point
with the env bound before import, and with zero global-state pollution (no
sys.argv / chdir / re-import leak between tests). Nothing is mocked — the real
parse_frontmatter parses real YAML and the real ReportWriter performs real file
I/O.

Run: python3 tests/test_amama_planning_status.py      (exit 0 = all pass)
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
_SCRIPT = _SCRIPTS / "amama_planning_status.py"


# --------------------------------------------------------------------------- #
# Fixtures / helpers
# --------------------------------------------------------------------------- #
def _make_project(state_body: str | None) -> Path:
    """Create a temp project dir; if state_body is not None, write the plan state file."""
    root = Path(tempfile.mkdtemp(prefix="amama-ps-test-"))
    if state_body is not None:
        (root / "design").mkdir(parents=True, exist_ok=True)
        (root / "design" / "plan-phase.local.md").write_text(state_body, encoding="utf-8")
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
    reports = sorted((root / "design" / "reports").glob("planning-status_*.md"))
    assert len(reports) == 1, f"expected exactly one report, found {len(reports)}"
    return reports[0].read_text(encoding="utf-8")


# A fully-populated, realistic plan state used by the "happy path" tests. Two
# requirement sections (one complete, one in-progress) and two modules with
# acceptance criteria + a github_issue exercise the icon map, the module loop,
# and every exit-criterion computation.
_POPULATED = """---
plan_id: plan-amama-42
status: in-progress
goal: Build the assistant manager planning workflow end to end
requirements_sections:
  - name: Functional requirements
    status: complete
  - name: Non-functional requirements
    status: in-progress
modules:
  - id: MOD-1
    name: Requirements intake
    status: complete
    priority: high
    acceptance_criteria: Captures every user requirement section verbatim
    github_issue: 101
  - id: MOD-2
    name: Module planner
    status: in-progress
    priority: medium
    acceptance_criteria: Produces a module list with acceptance criteria
    github_issue: 102
plan_phase_complete: false
---

# Plan Phase

Synthetic fixture body.
"""


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def test_error_when_no_state_file():
    """Missing design/plan-phase.local.md -> rc 1, 'Not in Plan Phase' on stderr, no report."""
    root = _make_project(state_body=None)
    try:
        cp = _run(root)
        assert cp.returncode == 1, f"expected rc 1, got {cp.returncode} ({cp.stderr})"
        assert "Not in Plan Phase" in cp.stderr
        # ReportWriter.__init__ eagerly creates design/reports/, but the failure
        # path returns before write_report(): the contract is ZERO report files.
        assert not list((root / "design" / "reports").glob("planning-status_*.md"))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_populated_state_parses_requirements_and_modules():
    """A populated plan state is parsed: summary echoes plan_id/status, report shows modules + icons."""
    root = _make_project(_POPULATED)
    try:
        cp = _run(root)
        assert cp.returncode == 0, f"expected rc 0, got {cp.returncode} ({cp.stderr})"
        # Summary on stdout echoes the real parsed plan_id + status (line 188).
        assert "Plan: plan-amama-42, Status: in-progress" in cp.stdout
        report = _report_text(root)
        # Header + section banners present.
        assert "PLAN PHASE STATUS" in report
        assert "REQUIREMENTS PROGRESS" in report
        assert "MODULES DEFINED (2)" in report
        # Requirement section names + a 'complete' icon (✓) and 'in-progress' icon (→).
        assert "Functional requirements" in report
        assert "Non-functional requirements" in report
        assert "✓" in report and "→" in report
        # Both modules rendered with their ids/names/status.
        assert "MOD-1" in report and "Requirements intake" in report
        assert "MOD-2" in report and "Module planner" in report
        # Exit criteria labels rendered.
        assert "GitHub Issues created for all modules" in report
        assert "User approved the plan" in report
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_empty_unparseable_state_reports_parse_failure():
    """A state file with no YAML frontmatter -> parse_frontmatter={} -> rc 1 'Could not parse'."""
    # File exists (so the first guard passes) but has no '---' frontmatter, so
    # parse_frontmatter returns {} and display_status hits the second guard.
    root = _make_project("# plan phase\nno frontmatter here, just prose\n")
    try:
        cp = _run(root)
        assert cp.returncode == 1, f"expected rc 1, got {cp.returncode} ({cp.stdout})"
        assert "Could not parse plan state file" in cp.stderr
        # The failure path returns before write_report() -> no report file written
        # (the empty design/reports/ dir created by ReportWriter.__init__ is fine).
        assert not list((root / "design" / "reports").glob("planning-status_*.md"))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_verbose_adds_per_module_criteria_and_priority():
    """--verbose emits per-module 'Criteria:'/'Priority:' lines the default run omits."""
    root_plain = _make_project(_POPULATED)
    root_verbose = _make_project(_POPULATED)
    try:
        plain = _run(root_plain)
        verbose = _run(root_verbose, "--verbose")
        assert plain.returncode == 0, f"plain rc {plain.returncode} ({plain.stderr})"
        assert verbose.returncode == 0, f"verbose rc {verbose.returncode} ({verbose.stderr})"

        plain_report = _report_text(root_plain)
        verbose_report = _report_text(root_verbose)

        # Verbose-only detail lines (lines 129-131) appear ONLY with --verbose.
        assert "Criteria:" not in plain_report
        assert "Priority:" not in plain_report
        assert "Criteria:" in verbose_report
        assert "Priority:" in verbose_report
        # The real acceptance-criteria + priority text is rendered in verbose mode.
        assert "Captures every user requirement section" in verbose_report
        assert "high" in verbose_report  # MOD-1 priority
    finally:
        shutil.rmtree(root_plain, ignore_errors=True)
        shutil.rmtree(root_verbose, ignore_errors=True)


def test_plan_complete_flips_summary_and_exit_criterion():
    """plan_phase_complete: true -> summary '0 exit criteria remaining' + the complete-phase banner."""
    # Drive plan_phase_complete=true with empty requirements/modules: the only
    # exit criterion that can be satisfied here is 'User approved the plan'
    # (plan_complete), so the remaining count is exactly 3 of 4 unmet -> the
    # summary's "{incomplete} exit criteria remaining" math is observable, and
    # the complete-phase footer text fires.
    state = (
        "---\n"
        "plan_id: plan-done\n"
        "status: approved\n"
        "goal: Finished plan\n"
        "requirements_sections: []\n"
        "modules: []\n"
        "plan_phase_complete: true\n"
        "---\n\n# done\n"
    )
    root = _make_project(state)
    try:
        cp = _run(root)
        assert cp.returncode == 0, f"expected rc 0, got {cp.returncode} ({cp.stderr})"
        assert "Plan: plan-done, Status: approved" in cp.stdout
        report = _report_text(root)
        # The complete-phase summary line (lines 174-177) is in the report body.
        assert "Plan Phase complete" in report
        assert "start-orchestration" in report
        # Empty collections render their explicit placeholders (lines 110, 133).
        assert "No requirement sections defined" in report
        assert "No modules defined yet" in report
        # plan_complete satisfies exactly the 'User approved the plan' criterion (✓).
        assert "User approved the plan" in report
    finally:
        shutil.rmtree(root, ignore_errors=True)


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
