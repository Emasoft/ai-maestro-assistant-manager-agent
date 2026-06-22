#!/usr/bin/env python3
"""Real (no-mock) tests for scripts/amama_approve_plan.py.

Each test builds a throwaway project under the system temp dir, populates it
with synthetic ``.claude`` state + ``USER_REQUIREMENTS.md``, runs the ACTUAL
``main()`` (which reads ``$CLAUDE_PROJECT_DIR`` and ``sys.argv``), and asserts against
the real filesystem outcome (exec-phase state file written, plan state mutated,
error exits when prerequisites are missing). Nothing is mocked: ``ReportWriter``
runs for real, its output pinned into the temp tree via ``CLAUDE_PROJECT_DIR``
so the repo is never polluted.

Run: python3 tests/test_amama_approve_plan.py      (exit 0 = all pass)
"""

from __future__ import annotations

import contextlib
import io
import os
import shutil
import sys
import tempfile
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import amama_approve_plan as ap  # noqa: E402  # pyright: ignore[reportMissingImports]
from _harness import run_standalone  # noqa: E402


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
@contextlib.contextmanager
def temp_project(*, with_plan: bool = True, with_requirements: bool = True,
                 plan_incomplete: bool = True):
    """Yield a fresh project root with synthetic plan-phase state + requirements.

    ``with_plan`` / ``with_requirements`` toggle each prerequisite so the error
    branches can be exercised. ``plan_incomplete`` controls whether the plan
    state carries ``plan_phase_complete: false`` (the conditional-flip branch).
    Runs ``main()`` from inside the dir (cwd) with ``CLAUDE_PROJECT_DIR`` pinned
    here so ReportWriter writes into the temp tree, then restores all globals.
    """
    root = Path(tempfile.mkdtemp(prefix="ap-test-"))
    claude_dir = root / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    if with_plan:
        complete_flag = "false" if plan_incomplete else "true"
        (claude_dir / "orchestrator-plan-phase.local.md").write_text(
            "---\n"
            "phase: plan\n"
            f"plan_phase_complete: {complete_flag}\n"
            "---\n\n# Plan Phase State\n\nSynthetic fixture.\n",
            encoding="utf-8",
        )
    if with_requirements:
        (root / "USER_REQUIREMENTS.md").write_text(
            "# User Requirements\n\nBuild the thing.\n", encoding="utf-8",
        )
    saved_cwd = Path.cwd()
    saved_argv = sys.argv[:]
    saved_env = os.environ.get("CLAUDE_PROJECT_DIR")
    os.chdir(root)
    os.environ["CLAUDE_PROJECT_DIR"] = str(root)
    try:
        yield root
    finally:
        os.chdir(saved_cwd)
        sys.argv[:] = saved_argv
        if saved_env is None:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            os.environ["CLAUDE_PROJECT_DIR"] = saved_env
        shutil.rmtree(root, ignore_errors=True)


def _run(*argv: str) -> int:
    """Run ap.main() with the given CLI args (suppressing stdout); return rc."""
    sys.argv[:] = ["amama_approve_plan.py", *argv]
    with contextlib.redirect_stdout(io.StringIO()):
        return ap.main()


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def test_approve_happy_path_creates_exec_state_and_flips_plan():
    """Happy path: exec-phase state file is written and plan flips to complete."""
    with temp_project(plan_incomplete=True) as root:
        rc = _run()
        assert rc == 0
        exec_state = root / ".claude" / "orchestrator-exec-phase.local.md"
        assert exec_state.exists()
        text = exec_state.read_text(encoding="utf-8")
        assert "Status: ready" in text
        assert "Plan Approved: true" in text
        assert text.startswith("# Orchestration Phase State")
        # the conditional-flip branch ran: false -> true in the plan state
        plan_state = (root / ".claude" / "orchestrator-plan-phase.local.md").read_text()
        assert "plan_phase_complete: true" in plan_state
        assert "plan_phase_complete: false" not in plan_state


def test_missing_plan_state_exits_nonzero_and_writes_nothing():
    """Missing plan-phase state file: main() exits 1 and creates no exec state."""
    with temp_project(with_plan=False) as root:
        raised = None
        with contextlib.redirect_stderr(io.StringIO()) as err:
            try:
                _run()
            except SystemExit as exc:
                raised = exc.code
        assert raised == 1
        assert "No plan phase state file" in err.getvalue()
        assert not (root / ".claude" / "orchestrator-exec-phase.local.md").exists()


def test_missing_requirements_exits_nonzero_and_writes_nothing():
    """Missing USER_REQUIREMENTS.md: main() exits 1 before creating exec state."""
    with temp_project(with_requirements=False) as root:
        raised = None
        with contextlib.redirect_stderr(io.StringIO()) as err:
            try:
                _run()
            except SystemExit as exc:
                raised = exc.code
        assert raised == 1
        assert "USER_REQUIREMENTS.md not found" in err.getvalue()
        assert not (root / ".claude" / "orchestrator-exec-phase.local.md").exists()


def test_already_complete_plan_is_left_untouched():
    """Edge: a plan already marked complete keeps its flag (no false->true replace)."""
    with temp_project(plan_incomplete=False) as root:
        before = (root / ".claude" / "orchestrator-plan-phase.local.md").read_text()
        rc = _run()
        assert rc == 0
        # exec state still produced on the happy path
        assert (root / ".claude" / "orchestrator-exec-phase.local.md").exists()
        # plan state unchanged: it had no `false` flag to flip, so byte-identical
        after = (root / ".claude" / "orchestrator-plan-phase.local.md").read_text()
        assert after == before
        assert "plan_phase_complete: true" in after


if __name__ == "__main__":
    sys.exit(run_standalone(globals()))
