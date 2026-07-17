#!/usr/bin/env python3
"""Canonical phase-state file locations for the AMAMA plan/orchestration workflow.

Single source of truth: the plan-approval writer (amama_approve_plan) and every
reader (amama_orchestration_status, amama_notify_agent, amama_planning_status)
MUST resolve these two files the SAME way. When they did not, the writer created
``.claude/orchestrator-*-phase.local.md`` while two readers looked under
``design/*-phase.local.md``, so ``/notify-agent`` and ``/planning-status`` always
reported "not in phase" even right after ``/approve-plan`` (bug C1). Import these
helpers; never hardcode the paths.

Project root resolution: ``$CLAUDE_PROJECT_DIR`` (the canonical root the harness
sets), falling back to the current directory only when it is unset. ``Path.cwd()``
alone is wrong when a slash command runs from a project subdirectory.
"""

from __future__ import annotations

import os
from pathlib import Path

_PLAN_STATE_NAME = "orchestrator-plan-phase.local.md"
_EXEC_STATE_NAME = "orchestrator-exec-phase.local.md"


def project_root() -> Path:
    """Return the canonical project root: $CLAUDE_PROJECT_DIR, else the current dir."""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()


def plan_state_path(root: Path | None = None) -> Path:
    """Plan-phase state file: written by /approve-plan, read by /planning-status."""
    return (root or project_root()) / ".claude" / _PLAN_STATE_NAME


def exec_state_path(root: Path | None = None) -> Path:
    """Orchestration-phase state file: written by /approve-plan, read by /orchestration-status and /notify-agent."""
    return (root or project_root()) / ".claude" / _EXEC_STATE_NAME
