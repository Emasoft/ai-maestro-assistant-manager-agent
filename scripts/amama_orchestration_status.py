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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from amama_report_writer import ReportWriter


def main() -> int:
    """Main entry point for orchestration status."""
    parser = argparse.ArgumentParser(description="View Orchestration Phase progress")
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
        print(
            "ERROR: Not in Orchestration Phase. Run /approve-plan first.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Read state file (minimal parsing)
    state_content = exec_state_file.read_text(encoding="utf-8")

    # Extract basic info (simple parsing)
    plan_id = "plan-unknown"
    status = "ready"
    modules_complete = 0  # TODO: Implement real module tracking via AI Maestro API
    modules_total = 0  # TODO: Implement real module tracking via AI Maestro API

    for line in state_content.split("\n"):
        if line.startswith("Plan ID:"):
            plan_id = line.split(":", 1)[1].strip()
        elif line.startswith("Status:"):
            status = line.split(":", 1)[1].strip()

    # Collect verbose output into a buffer for the report file
    lines: list[str] = []

    if not args.agents_only:
        lines.append("╔════════════════════════════════════════════════════════════════╗")
        lines.append("║                 ORCHESTRATION PHASE STATUS                     ║")
        lines.append("╠════════════════════════════════════════════════════════════════╣")
        lines.append(f"║ Plan ID: {plan_id:<52} ║")
        lines.append(f"║ Status: {status:<55} ║")
        lines.append(
            f"║ Progress: {modules_complete}/{modules_total} modules complete (0%)                        ║"
        )
        lines.append("╠════════════════════════════════════════════════════════════════╣")

    if not args.agents_only:
        lines.append("║ MODULE STATUS                                                  ║")
        lines.append("╠════════════════════════════════════════════════════════════════╣")
        lines.append("║ (No modules defined yet)                                       ║")
        lines.append("╠════════════════════════════════════════════════════════════════╣")

    if not args.modules_only:
        lines.append("║ REGISTERED AGENTS                                              ║")
        lines.append("╠════════════════════════════════════════════════════════════════╣")
        lines.append("║ AI Agents:                                                     ║")
        lines.append("║   (No AI agents registered)                                    ║")
        lines.append("║ Human Developers:                                              ║")
        lines.append("║   (No human developers registered)                             ║")
        lines.append("╠════════════════════════════════════════════════════════════════╣")

    if not args.modules_only:
        lines.append("║ ACTIVE ASSIGNMENTS                                             ║")
        lines.append("╠════════════════════════════════════════════════════════════════╣")
        lines.append("║ (No active assignments)                                        ║")
        lines.append("╚════════════════════════════════════════════════════════════════╝")

    if args.verbose:
        lines.append(f"\nState file: {exec_state_file}")
        lines.append(
            f"Last updated: {datetime.fromtimestamp(exec_state_file.stat().st_mtime).isoformat()}"
        )

    # Write verbose output to report file, print only summary to stdout
    writer = ReportWriter("orchestration-status")
    report_content = "\n".join(lines)
    report_path = writer.write_report(report_content)
    writer.print_summary(
        f"Plan: {plan_id}, Status: {status}, Progress: {modules_complete}/{modules_total}",
        report_path,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
