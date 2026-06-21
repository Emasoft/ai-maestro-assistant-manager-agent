#!/usr/bin/env python3
"""Real (no-mock) tests for scripts/amama_state_paths.py — the C1 regression guard.

C1 was a writer/reader path mismatch: ``amama_approve_plan`` wrote
``.claude/orchestrator-{plan,exec}-phase.local.md`` while ``amama_notify_agent``
and ``amama_planning_status`` read ``design/{exec,plan}-phase.local.md``, so
``/notify-agent`` and ``/planning-status`` always reported "not in phase" even
right after ``/approve-plan``. These tests pin the single source of truth (the
path shape + ``$CLAUDE_PROJECT_DIR`` rooting) AND prove the writer and the
readers now agree end to end: a real ``approve-plan`` run produces a state file
that ``orchestration-status`` and ``planning-status`` actually read back.

Run: python3 tests/test_amama_state_paths.py      (exit 0 = all pass)
"""

from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import amama_state_paths as sp  # noqa: E402  # pyright: ignore[reportMissingImports]
from _harness import run_standalone  # noqa: E402


@contextlib.contextmanager
def _project_dir(root: Path):
    """Pin $CLAUDE_PROJECT_DIR to root for the duration, then restore it."""
    saved = os.environ.get("CLAUDE_PROJECT_DIR")
    os.environ["CLAUDE_PROJECT_DIR"] = str(root)
    try:
        yield
    finally:
        if saved is None:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            os.environ["CLAUDE_PROJECT_DIR"] = saved


def test_paths_are_claude_orchestrator_prefixed():
    """Both state files resolve under <root>/.claude/orchestrator-*-phase.local.md."""
    root = Path(tempfile.mkdtemp(prefix="sp-shape-")).resolve()
    try:
        assert sp.plan_state_path(root) == root / ".claude" / "orchestrator-plan-phase.local.md"
        assert sp.exec_state_path(root) == root / ".claude" / "orchestrator-exec-phase.local.md"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_project_root_prefers_claude_project_dir():
    """project_root() resolves $CLAUDE_PROJECT_DIR; the default-arg paths follow it."""
    root = Path(tempfile.mkdtemp(prefix="sp-env-")).resolve()
    try:
        with _project_dir(root):
            assert sp.project_root() == root
            assert sp.plan_state_path() == root / ".claude" / "orchestrator-plan-phase.local.md"
            assert sp.exec_state_path() == root / ".claude" / "orchestrator-exec-phase.local.md"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_writer_and_readers_agree_end_to_end():
    """C1 regression: approve-plan's output is read back by BOTH orchestration-status
    and planning-status — neither reports 'not in phase' (the paths now agree)."""
    root = Path(tempfile.mkdtemp(prefix="sp-e2e-")).resolve()
    try:
        (root / ".claude").mkdir(parents=True, exist_ok=True)
        # Pre-create the plan-phase state the way /start-planning would.
        sp.plan_state_path(root).write_text(
            "---\nphase: plan\nplan_phase_complete: false\n---\n\n# Plan\n",
            encoding="utf-8",
        )
        (root / "USER_REQUIREMENTS.md").write_text("# Reqs\n", encoding="utf-8")
        env = {**os.environ, "CLAUDE_PROJECT_DIR": str(root)}

        def run(script: str, *argv: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [sys.executable, str(_SCRIPTS / script), *argv],
                cwd=str(root), env=env, capture_output=True, text=True,
            )

        # 1. Writer: approve the plan -> writes the exec-phase state file.
        approve = run("amama_approve_plan.py", "--skip-issues")
        assert approve.returncode == 0, approve.stderr
        assert sp.exec_state_path(root).exists()

        # 2. Reader (exec): orchestration-status must NOT report "not in phase".
        orch = run("amama_orchestration_status.py")
        assert orch.returncode == 0, orch.stderr
        assert "Not in Orchestration Phase" not in orch.stderr

        # 3. Reader (plan): planning-status reads the same plan state the writer flipped.
        plan = run("amama_planning_status.py")
        assert plan.returncode == 0, plan.stderr
        assert "Not in Plan Phase" not in plan.stderr
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(run_standalone(globals()))
