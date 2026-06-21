#!/usr/bin/env python3
"""
amama_stop_check.py - Stop hook to block exit until coordination work is complete.

Stop hook that prevents assistant-manager from exiting with incomplete work:
1. Unread AI Maestro messages requiring response
2. GitHub Issues assigned to assistant-manager not closed

The old activeContext/tasks/approvals/handoffs memory-bank reads were retired
(TRDD-8707e849): pending tasks/approvals/handoffs are now surfaced by the AI
Maestro inbox, the proposal-approvals lifecycle, and the `design/tasks/` /
`design/proposals/` TRDD columns — so this hook no longer reads the bank.

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
from datetime import datetime
from pathlib import Path
from typing import Any


def check_ai_maestro_inbox() -> tuple[int, list[str]]:
    """Check AI Maestro inbox for unread messages via the canonical `amp-inbox` CLI.

    Routes through the stable script layer (NOT a direct server-API call) per the
    frozen-interface architecture: `amp-inbox --count` prints the unread count for
    this agent (resolved from the agent's own config) as a bare integer, exit 0.
    """
    try:
        result = subprocess.run(
            ["amp-inbox", "--count"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            count = int(result.stdout.strip())
            if count > 0:
                return count, [f"{count} unread message(s)"]
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError, FileNotFoundError, OSError):
        pass
    return 0, []


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

    # Skip blocking for subagents — only block main agent exits (2.1.69+: agent_id present means subagent)
    if hook_input.get("agent_id"):
        return 0

    # Working directory — used only as the report-write fallback below.
    cwd = hook_input.get("cwd", os.getcwd())

    # Collect all blocking issues
    issues: dict[str, Any] = {}

    # 1. Check AI Maestro inbox
    unread_count, unread_subjects = check_ai_maestro_inbox()
    if unread_count > 0:
        issues["unread_messages"] = unread_count
        issues["unread_subjects"] = unread_subjects

    # 2. Check GitHub Issues (only if gh CLI is available)
    gh_count, gh_list = check_github_issues()
    if gh_count > 0:
        issues["github_issues"] = gh_count
        issues["github_issues_list"] = gh_list

    # Decision: block if any issues found
    if issues:
        response = build_blocking_response(issues)
        # Write full details to report file, minimize stdout JSON for token savings
        try:
            # reports/ is gitignored (design/reports/ is NOT) so the block report —
            # which embeds message subjects + issue titles — never lands in a
            # committable path. Timestamp carries the %z GMT offset per the
            # agent-reports-location rule.
            project_dir = os.environ.get("CLAUDE_PROJECT_DIR", cwd)
            report_dir = Path(project_dir) / "reports" / "stop-check"
            report_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S%z")
            report_path = report_dir / f"stop_check_{ts}.md"
            report_path.write_text(json.dumps(response, indent=2), encoding="utf-8")
            # Minimal stdout: counts only, no lists, no indentation
            minimal = {
                "decision": response["decision"],
                "reason": response["reason"],
                "hookSpecificOutput": response["hookSpecificOutput"],
                "report": str(report_path),
            }
            print(json.dumps(minimal, separators=(",", ":")))
        except OSError:
            # Fallback: output full response if report write fails
            print(json.dumps(response, indent=2))
        return 2  # Block exit

    # No issues - allow exit
    return 0


def _entry() -> None:
    sys.exit(main())


if __name__ == "__main__":
    _entry()
