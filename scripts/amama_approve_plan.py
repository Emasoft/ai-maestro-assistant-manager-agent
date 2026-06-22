#!/usr/bin/env python3
"""
Approve Plan Command - Transition from Plan Phase to Orchestration Phase

This script handles the plan -> orchestration phase transition:
1. Validates prerequisites (plan-phase state file + USER_REQUIREMENTS.md)
2. Writes the orchestration-phase state file
3. Marks the plan phase complete
4. Outputs a transition summary

NOTE: this command does NOT create GitHub issues. An earlier draft advertised
per-module issue creation that was never implemented (``modules`` was hardcoded
empty); the false claim and its dead ``--skip-issues`` flag were removed so the
command's contract matches its behaviour (fail-fast / honesty — no stub that
lies). Per-module issue creation, if wanted later, is a separate feature with
its own design.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from amama_atomic_write import atomic_write
from amama_report_writer import ReportWriter
from amama_state_paths import exec_state_path, plan_state_path, project_root


def main() -> int:
    """Main entry point for plan approval."""
    parser = argparse.ArgumentParser(
        description="Approve plan and transition to Orchestration Phase"
    )
    # No options: parse only to enable -h/--help and to fail-fast on any
    # unknown argument. This command is a pure phase transition driven by the
    # state files; the previous --verbose/--skip-issues flags were dead (never
    # read / never created issues) and were removed.
    parser.parse_args()

    # Project root + the canonical phase-state files. One source of truth —
    # the writer and every reader MUST resolve these the same way (the C1 bug
    # was a writer/reader path mismatch); see amama_state_paths.
    project_dir = project_root()

    # Check for plan phase state file
    plan_state_file = plan_state_path(project_dir)
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
    }

    # Create orchestration state file
    exec_state_file = exec_state_path(project_dir)
    atomic_write(
        exec_state_file,
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
    )

    # Update plan state to mark as complete
    plan_content = plan_state_file.read_text(encoding="utf-8")
    if "plan_phase_complete: false" in plan_content:
        plan_content = plan_content.replace(
            "plan_phase_complete: false", "plan_phase_complete: true"
        )
        atomic_write(plan_state_file, plan_content)

    # Build verbose output for report file
    lines = []
    lines.append("╔════════════════════════════════════════════════════════════════╗")
    lines.append("║                    PLAN APPROVED                               ║")
    lines.append("╠════════════════════════════════════════════════════════════════╣")
    lines.append(f"║ Plan ID: {plan_data['plan_id']:<52} ║")
    lines.append(f"║ Goal: {plan_data['goal']:<55} ║")
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
