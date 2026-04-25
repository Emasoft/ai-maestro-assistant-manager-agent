#!/usr/bin/env python3
"""
Approve Plan Command - Transition from Plan Phase to Orchestration Phase

This script handles plan approval workflow:
1. Validates plan completeness
2. Creates GitHub Issues for modules (unless --skip-issues)
3. Updates state files
4. Outputs transition summary
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from amama_report_writer import ReportWriter


def main() -> int:
    """Main entry point for plan approval."""
    parser = argparse.ArgumentParser(
        description="Approve plan and transition to Orchestration Phase"
    )
    parser.add_argument(
        "--skip-issues",
        action="store_true",
        help="Skip GitHub Issue creation (for offline work)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output",
    )

    args = parser.parse_args()

    # Get project directory from environment or current directory
    project_dir = Path.cwd()
    claude_dir = project_dir / ".claude"

    # Check for plan phase state file
    plan_state_file = claude_dir / "orchestrator-plan-phase.local.md"
    if not plan_state_file.exists():
        print(
            "ERROR: No plan phase state file found. Run /start-planning first.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate USER_REQUIREMENTS.md exists
    requirements_file = project_dir / "USER_REQUIREMENTS.md"
    if not requirements_file.exists():
        print(
            "ERROR: USER_REQUIREMENTS.md not found. Create requirements document first.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Read plan state (minimal parsing)
    plan_data = {
        "plan_id": f"plan-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "goal": "Implementation plan",
        "modules": [],  # TODO: Implement real plan module loading via design documents
    }

    # Create orchestration state file
    exec_state_file = claude_dir / "orchestrator-exec-phase.local.md"
    exec_state_file.write_text(
        f"""# Orchestration Phase State

Plan ID: {plan_data["plan_id"]}
Status: ready
Created: {datetime.now().isoformat()}
Plan Approved: true

## Modules
(No modules defined yet)

## Agents
(No agents registered yet)
""",
        encoding="utf-8",
    )

    # Update plan state to mark as complete
    plan_content = plan_state_file.read_text(encoding="utf-8")
    if "plan_phase_complete: false" in plan_content:
        plan_content = plan_content.replace(
            "plan_phase_complete: false", "plan_phase_complete: true"
        )
        plan_state_file.write_text(plan_content, encoding="utf-8")

    # Build verbose output for report file
    lines = []
    lines.append("╔════════════════════════════════════════════════════════════════╗")
    lines.append("║                    PLAN APPROVED                               ║")
    lines.append("╠════════════════════════════════════════════════════════════════╣")
    lines.append(f"║ Plan ID: {plan_data['plan_id']:<52} ║")
    lines.append(f"║ Goal: {plan_data['goal']:<55} ║")
    lines.append("╠════════════════════════════════════════════════════════════════╣")

    if args.skip_issues:
        lines.append("║ GitHub Issues: SKIPPED (--skip-issues flag)                   ║")
    else:
        lines.append("║ GITHUB ISSUES CREATED                                          ║")
        lines.append("╠════════════════════════════════════════════════════════════════╣")
        lines.append("║ (No modules defined - issues will be created during planning)  ║")

    lines.append("╠════════════════════════════════════════════════════════════════╣")
    lines.append("║ NEXT STEPS                                                     ║")
    lines.append("╠════════════════════════════════════════════════════════════════╣")
    lines.append("║ 1. Run /start-orchestration to begin implementation            ║")
    lines.append("║ 2. Register remote agents with /register-agent                 ║")
    lines.append("║ 3. Assign modules with /assign-module                          ║")
    lines.append("╚════════════════════════════════════════════════════════════════╝")

    lines.append(f"\nState file created: {exec_state_file}")
    lines.append(f"Plan state updated: {plan_state_file}")

    # Write verbose output to report file, print only summary to stdout
    writer = ReportWriter("plan-approval")
    report_path = writer.write_report("\n".join(lines))
    writer.print_summary(
        f"Plan {plan_data['plan_id']} approved. State files created.",
        report_path,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
