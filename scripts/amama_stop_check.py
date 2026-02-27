#!/usr/bin/env python3
"""
eama_stop_check.py - Stop hook to block exit until coordination work is complete.

Stop hook that prevents assistant-manager from exiting with incomplete work:
1. Pending user approvals not yet obtained
2. Active handoffs to other roles not acknowledged
3. Claude Tasks with pending/in-progress status
4. Unread AI Maestro messages requiring response
5. GitHub Issues assigned to assistant-manager not closed

Dependencies: Python 3.8+ stdlib only

Usage (as Claude Code hook):
    Receives JSON via stdin from Stop hook event.
    Returns JSON with decision to allow or block exit.

Exit codes:
    0 - Allow exit (no blocking issues found, or JSON output with allow decision)
    2 - Block exit (JSON output with block decision and reason)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def get_memory_root(cwd: str) -> Path:
    """Get the Emasoft Assistant Manager memory root directory."""
    return Path(cwd) / ".claude" / "eama"


def check_ai_maestro_inbox() -> tuple[int, list[str]]:
    """Check AI Maestro inbox for unread messages.

    Note: amp-send is a send-only CLI. Message retrieval is not supported
    by the AMP CLI, so this function always returns zero unread messages.

    Returns:
        Tuple of (unread_count, list of message subjects)
    """
    return 0, []


def check_claude_tasks(memory_root: Path) -> tuple[int, list[str]]:
    """Check for pending or in-progress Claude Tasks.

    Looks for tasks.md or similar task tracking files.

    Returns:
        Tuple of (pending_count, list of task descriptions)
    """
    pending_tasks = []

    # Check tasks.md in memory root
    tasks_path = memory_root / "tasks.md"
    if tasks_path.exists():
        try:
            content = tasks_path.read_text(encoding="utf-8")
            # Look for tasks marked as pending or in-progress
            for line in content.split("\n"):
                line_lower = line.lower()
                if any(
                    marker in line_lower
                    for marker in [
                        "[ ]",
                        "[pending]",
                        "[in-progress]",
                        "status: pending",
                        "status: in-progress",
                    ]
                ):
                    # Extract task description
                    task_desc = line.strip().lstrip("-").lstrip("*").strip()
                    if task_desc and len(task_desc) < 100:
                        pending_tasks.append(task_desc[:80])
        except (OSError, UnicodeDecodeError):
            pass

    # Also check activeContext.md for in-flight tasks
    active_path = memory_root / "activeContext.md"
    if active_path.exists():
        try:
            content = active_path.read_text(encoding="utf-8")
            # Look for "In-Flight" or "Active Tasks" sections with items
            in_section = False
            for line in content.split("\n"):
                if "## In-Flight" in line or "## Active Tasks" in line:
                    in_section = True
                    continue
                if in_section:
                    if line.startswith("##"):
                        break
                    if line.strip().startswith("-") and "[ ]" in line:
                        task_desc = line.strip().lstrip("-").strip()
                        if task_desc and task_desc not in pending_tasks:
                            pending_tasks.append(task_desc[:80])
        except (OSError, UnicodeDecodeError):
            pass

    return len(pending_tasks), pending_tasks


def check_pending_approvals(memory_root: Path) -> tuple[int, list[str]]:
    """Check for pending user approvals.

    Looks for approval requests in activeContext.md or approvals.md.

    Returns:
        Tuple of (pending_count, list of approval descriptions)
    """
    pending_approvals = []

    # Check approvals.md
    approvals_path = memory_root / "approvals.md"
    if approvals_path.exists():
        try:
            content = approvals_path.read_text(encoding="utf-8")
            for line in content.split("\n"):
                line_lower = line.lower()
                if "pending" in line_lower and (
                    "approval" in line_lower or "[ ]" in line
                ):
                    desc = line.strip().lstrip("-").lstrip("*").strip()
                    if desc and len(desc) < 100:
                        pending_approvals.append(desc[:80])
        except (OSError, UnicodeDecodeError):
            pass

    # Check activeContext.md for approval markers
    active_path = memory_root / "activeContext.md"
    if active_path.exists():
        try:
            content = active_path.read_text(encoding="utf-8")
            in_section = False
            for line in content.split("\n"):
                if "## Pending Approvals" in line or "## Awaiting Approval" in line:
                    in_section = True
                    continue
                if in_section:
                    if line.startswith("##"):
                        break
                    if line.strip().startswith("-"):
                        desc = line.strip().lstrip("-").strip()
                        if desc and desc not in pending_approvals:
                            pending_approvals.append(desc[:80])
        except (OSError, UnicodeDecodeError):
            pass

    return len(pending_approvals), pending_approvals


def check_active_handoffs(memory_root: Path) -> tuple[int, list[str]]:
    """Check for active handoffs to other roles not yet acknowledged.

    Returns:
        Tuple of (pending_count, list of handoff descriptions)
    """
    pending_handoffs = []

    # Check handoffs directory
    handoffs_dir = memory_root / "handoffs"
    if handoffs_dir.exists() and handoffs_dir.is_dir():
        for handoff_file in handoffs_dir.glob("*.md"):
            try:
                content = handoff_file.read_text(encoding="utf-8")
                # Check if handoff is pending (not acknowledged)
                if (
                    "status: pending" in content.lower()
                    or "acknowledged: false" in content.lower()
                ):
                    # Extract handoff target from filename or content
                    desc = f"Handoff: {handoff_file.stem}"
                    pending_handoffs.append(desc)
            except (OSError, UnicodeDecodeError):
                pass

    # Also check activeContext.md for handoff markers
    active_path = memory_root / "activeContext.md"
    if active_path.exists():
        try:
            content = active_path.read_text(encoding="utf-8")
            in_section = False
            for line in content.split("\n"):
                if "## Active Handoffs" in line or "## Pending Handoffs" in line:
                    in_section = True
                    continue
                if in_section:
                    if line.startswith("##"):
                        break
                    if (
                        line.strip().startswith("-")
                        and "acknowledged" not in line.lower()
                    ):
                        desc = line.strip().lstrip("-").strip()
                        if desc and desc not in pending_handoffs:
                            pending_handoffs.append(desc[:80])
        except (OSError, UnicodeDecodeError):
            pass

    return len(pending_handoffs), pending_handoffs


def check_github_issues() -> tuple[int, list[str]]:
    """Check for GitHub Issues assigned to assistant-manager not closed.

    Uses gh CLI to query issues.

    Returns:
        Tuple of (open_count, list of issue titles)
    """
    open_issues = []

    try:
        # Query open issues assigned to current user with assistant-manager label
        result = subprocess.run(
            [
                "gh",
                "issue",
                "list",
                "--state",
                "open",
                "--label",
                "assistant-manager",
                "--json",
                "title,number",
                "--limit",
                "10",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            issues = json.loads(result.stdout)
            for issue in issues:
                title = issue.get("title", "Untitled")
                number = issue.get("number", "?")
                open_issues.append(f"#{number}: {title[:60]}")
    except (
        subprocess.TimeoutExpired,
        json.JSONDecodeError,
        subprocess.SubprocessError,
        FileNotFoundError,
    ):
        pass

    return len(open_issues), open_issues


def build_blocking_response(issues: dict[str, Any]) -> dict[str, Any]:
    """Build the JSON response for blocking exit.

    Args:
        issues: Dictionary of issue categories and their details

    Returns:
        JSON-serializable dict with block decision
    """
    # Build reason string
    reason_parts = []

    if issues.get("unread_messages", 0) > 0:
        reason_parts.append(f"{issues['unread_messages']} unread message(s)")
    if issues.get("pending_tasks", 0) > 0:
        reason_parts.append(f"{issues['pending_tasks']} pending task(s)")
    if issues.get("pending_approvals", 0) > 0:
        reason_parts.append(f"{issues['pending_approvals']} pending approval(s)")
    if issues.get("active_handoffs", 0) > 0:
        reason_parts.append(f"{issues['active_handoffs']} active handoff(s)")
    if issues.get("github_issues", 0) > 0:
        reason_parts.append(f"{issues['github_issues']} open GitHub issue(s)")

    reason = "Cannot exit: " + ", ".join(reason_parts)

    return {
        "decision": "block",
        "reason": reason,
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Incomplete coordination work",
        },
        "details": issues,
    }


def main() -> int:
    """Main entry point for Stop hook.

    Checks for incomplete coordination work and blocks exit if found.

    Returns:
        Exit code: 0 for allow, 2 for block
    """
    # Read hook input from stdin
    try:
        stdin_data = sys.stdin.read()
        if stdin_data.strip():
            hook_input = json.loads(stdin_data)
        else:
            hook_input = {}
    except json.JSONDecodeError:
        hook_input = {}

    # Get working directory from input or environment
    cwd = hook_input.get("cwd", os.getcwd())
    memory_root = get_memory_root(cwd)

    # Collect all blocking issues
    issues: dict[str, Any] = {}

    # 1. Check AI Maestro inbox
    unread_count, unread_subjects = check_ai_maestro_inbox()
    if unread_count > 0:
        issues["unread_messages"] = unread_count
        issues["unread_subjects"] = unread_subjects

    # 2. Check Claude Tasks
    tasks_count, tasks_list = check_claude_tasks(memory_root)
    if tasks_count > 0:
        issues["pending_tasks"] = tasks_count
        issues["pending_tasks_list"] = tasks_list

    # 3. Check pending approvals
    approvals_count, approvals_list = check_pending_approvals(memory_root)
    if approvals_count > 0:
        issues["pending_approvals"] = approvals_count
        issues["pending_approvals_list"] = approvals_list

    # 4. Check active handoffs
    handoffs_count, handoffs_list = check_active_handoffs(memory_root)
    if handoffs_count > 0:
        issues["active_handoffs"] = handoffs_count
        issues["active_handoffs_list"] = handoffs_list

    # 5. Check GitHub Issues (only if gh CLI is available)
    gh_count, gh_list = check_github_issues()
    if gh_count > 0:
        issues["github_issues"] = gh_count
        issues["github_issues_list"] = gh_list

    # Decision: block if any issues found
    if issues:
        response = build_blocking_response(issues)
        print(json.dumps(response, indent=2))
        return 2  # Block exit

    # No issues - allow exit
    return 0


if __name__ == "__main__":
    sys.exit(main())
