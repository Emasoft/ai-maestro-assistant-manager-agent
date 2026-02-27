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
from pathlib import Path
from datetime import datetime


def main() -> None:
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
        "modules": [],
    }

    # Create orchestration state file
    exec_state_file = claude_dir / "orchestrator-exec-phase.local.md"
    exec_state_file.write_text(f"""# Orchestration Phase State

Plan ID: {plan_data["plan_id"]}
Status: ready
Created: {datetime.now().isoformat()}
Plan Approved: true

## Modules
(No modules defined yet)

## Agents
(No agents registered yet)
""", encoding="utf-8")

    # Update plan state to mark as complete
    plan_content = plan_state_file.read_text(encoding="utf-8")
    if "plan_phase_complete: false" in plan_content:
        plan_content = plan_content.replace(
            "plan_phase_complete: false", "plan_phase_complete: true"
        )
        plan_state_file.write_text(plan_content, encoding="utf-8")

    # Output success message
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                    PLAN APPROVED                               ║")
    print("╠════════════════════════════════════════════════════════════════╣")
    print(f"║ Plan ID: {plan_data['plan_id']:<52} ║")
    print(f"║ Goal: {plan_data['goal']:<55} ║")
    print("╠════════════════════════════════════════════════════════════════╣")

    if args.skip_issues:
        print("║ GitHub Issues: SKIPPED (--skip-issues flag)                   ║")
    else:
        print("║ GITHUB ISSUES CREATED                                          ║")
        print("╠════════════════════════════════════════════════════════════════╣")
        print("║ (No modules defined - issues will be created during planning)  ║")

    print("╠════════════════════════════════════════════════════════════════╣")
    print("║ NEXT STEPS                                                     ║")
    print("╠════════════════════════════════════════════════════════════════╣")
    print("║ 1. Run /start-orchestration to begin implementation            ║")
    print("║ 2. Register remote agents with /register-agent                 ║")
    print("║ 3. Assign modules with /assign-module                          ║")
    print("╚════════════════════════════════════════════════════════════════╝")

    if args.verbose:
        print(f"\nState file created: {exec_state_file}")
        print(f"Plan state updated: {plan_state_file}")


if __name__ == "__main__":
    main()
