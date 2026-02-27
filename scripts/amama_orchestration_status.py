#!/usr/bin/env python3
"""
Orchestration Status Command - View Orchestration Phase progress

This script displays:
1. Phase status
2. Module progress
3. Agent registry
4. Active assignments
5. Instruction verification
6. Progress polling
7. Verification loops
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime


def main():
    """Main entry point for orchestration status."""
    parser = argparse.ArgumentParser(
        description="View Orchestration Phase progress"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed polling history and criteria",
    )
    parser.add_argument(
        "--agents-only",
        action="store_true",
        help="Show only agent information",
    )
    parser.add_argument(
        "--modules-only",
        action="store_true",
        help="Show only module status",
    )

    args = parser.parse_args()

    # Get project directory from environment or current directory
    project_dir = Path.cwd()
    claude_dir = project_dir / ".claude"

    # Check for orchestration phase state file
    exec_state_file = claude_dir / "orchestrator-exec-phase.local.md"
    if not exec_state_file.exists():
        print("ERROR: Not in Orchestration Phase. Run /approve-plan first.", file=sys.stderr)
        sys.exit(1)

    # Read state file (minimal parsing)
    state_content = exec_state_file.read_text(encoding="utf-8")

    # Extract basic info (simple parsing)
    plan_id = "plan-unknown"
    status = "ready"
    modules_complete = 0
    modules_total = 0

    for line in state_content.split("\n"):
        if line.startswith("Plan ID:"):
            plan_id = line.split(":", 1)[1].strip()
        elif line.startswith("Status:"):
            status = line.split(":", 1)[1].strip()

    # Output status
    if not args.agents_only:
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║                 ORCHESTRATION PHASE STATUS                     ║")
        print("╠════════════════════════════════════════════════════════════════╣")
        print(f"║ Plan ID: {plan_id:<52} ║")
        print(f"║ Status: {status:<55} ║")
        print(f"║ Progress: {modules_complete}/{modules_total} modules complete (0%)                        ║")
        print("╠════════════════════════════════════════════════════════════════╣")

    if not args.agents_only:
        print("║ MODULE STATUS                                                  ║")
        print("╠════════════════════════════════════════════════════════════════╣")
        print("║ (No modules defined yet)                                       ║")
        print("╠════════════════════════════════════════════════════════════════╣")

    if not args.modules_only:
        print("║ REGISTERED AGENTS                                              ║")
        print("╠════════════════════════════════════════════════════════════════╣")
        print("║ AI Agents:                                                     ║")
        print("║   (No AI agents registered)                                    ║")
        print("║ Human Developers:                                              ║")
        print("║   (No human developers registered)                             ║")
        print("╠════════════════════════════════════════════════════════════════╣")

    if not args.modules_only:
        print("║ ACTIVE ASSIGNMENTS                                             ║")
        print("╠════════════════════════════════════════════════════════════════╣")
        print("║ (No active assignments)                                        ║")
        print("╚════════════════════════════════════════════════════════════════╝")

    if args.verbose:
        print(f"\nState file: {exec_state_file}")
        print(f"Last updated: {datetime.fromtimestamp(exec_state_file.stat().st_mtime).isoformat()}")


if __name__ == "__main__":
    main()
