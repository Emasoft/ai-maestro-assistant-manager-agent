#!/usr/bin/env python3
"""
Assistant Manager Planning Status Script

Displays the current status of Plan Phase including requirements progress,
module definitions, and exit criteria completion.

Usage:
    python3 am_planning_status.py
    python3 am_planning_status.py --verbose
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import yaml

from amama_report_writer import ReportWriter

# Plan phase state file location
PLAN_STATE_FILE = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")) / "design" / "plan-phase.local.md"


def parse_frontmatter(file_path: Path) -> dict:
    """Parse YAML frontmatter from a markdown file."""
    if not file_path.exists():
        return {}

    content = file_path.read_text(encoding="utf-8")

    # Check for frontmatter delimiters
    if not content.startswith("---"):
        return {}

    # Find the closing delimiter
    end_index = content.find("---", 3)
    if end_index == -1:
        return {}

    # Extract and parse YAML
    yaml_content = content[3:end_index].strip()
    try:
        return yaml.safe_load(yaml_content) or {}
    except yaml.YAMLError:
        return {}


def get_status_icon(status: str) -> str:
    """Return an icon for the given status."""
    icons = {
        "complete": "✓",
        "in-progress": "→",
        "pending": " ",
        "planned": "○",
        "drafting": "○",
        "reviewing": "→",
        "approved": "✓",
    }
    return icons.get(status, "?")


def display_status(verbose: bool = False) -> bool:
    """Display the current plan phase status. Writes verbose output to report file, prints summary to stdout."""
    writer = ReportWriter("planning-status")
    lines: list[str] = []

    if not PLAN_STATE_FILE.exists():
        writer.print_failure("Not in Plan Phase - run /start-planning to begin")
        return False

    data = parse_frontmatter(PLAN_STATE_FILE)
    if not data:
        writer.print_failure("Could not parse plan state file")
        return False

    plan_id = data.get("plan_id", "unknown")
    status = data.get("status", "unknown")
    goal = data.get("goal", "No goal set")
    requirements_sections = data.get("requirements_sections", [])
    modules = data.get("modules", [])
    plan_complete = data.get("plan_phase_complete", False)

    # Build header
    lines.append("╔" + "═" * 66 + "╗")
    lines.append("║" + "PLAN PHASE STATUS".center(66) + "║")
    lines.append("╠" + "═" * 66 + "╣")
    lines.append(f"║ Plan ID: {plan_id:<55} ║")
    lines.append(f"║ Status: {status:<56} ║")
    lines.append(f"║ Goal: {goal[:54]:<56} ║")
    if len(goal) > 54:
        lines.append(f"║       {goal[54:108]:<58} ║")

    # Requirements progress
    lines.append("╠" + "═" * 66 + "╣")
    lines.append("║" + "REQUIREMENTS PROGRESS".center(66) + "║")
    lines.append("╠" + "═" * 66 + "╣")

    if requirements_sections:
        for section in requirements_sections:
            name = section.get("name", "Unknown")
            sect_status = section.get("status", "pending")
            icon = get_status_icon(sect_status)
            lines.append(f"║ [{icon}] {name:<30} - {sect_status:<25} ║")
    else:
        lines.append("║ No requirement sections defined                                  ║")

    # Modules
    lines.append("╠" + "═" * 66 + "╣")
    module_count = len(modules)
    lines.append(f"║ MODULES DEFINED ({module_count})".ljust(66) + " ║")
    lines.append("╠" + "═" * 66 + "╣")

    if modules:
        for i, module in enumerate(modules, 1):
            mod_id = module.get("id", "unknown")
            mod_name = module.get("name", mod_id)
            mod_status = module.get("status", "pending")
            priority = module.get("priority", "medium")
            icon = get_status_icon(mod_status)
            line = f"║ {i}. {mod_id:<12} - {mod_name:<20} [{mod_status}]"
            lines.append(f"{line:<66} ║")

            if verbose:
                criteria = module.get("acceptance_criteria", "No criteria defined")
                lines.append(f"║    Criteria: {criteria[:50]:<52} ║")
                lines.append(f"║    Priority: {priority:<52} ║")
    else:
        lines.append("║ No modules defined yet                                           ║")
        lines.append("║ Use /add-requirement module <name> to add modules                ║")

    # Exit criteria
    lines.append("╠" + "═" * 66 + "╣")
    lines.append("║" + "EXIT CRITERIA".center(66) + "║")
    lines.append("╠" + "═" * 66 + "╣")

    # Calculate exit criteria status
    req_file_exists = Path("USER_REQUIREMENTS.md").exists()
    all_req_complete = (
        all(s.get("status") == "complete" for s in requirements_sections)
        if requirements_sections
        else False
    )
    all_modules_have_criteria = (
        all(m.get("acceptance_criteria") for m in modules) if modules else False
    )
    has_modules = len(modules) > 0

    criteria_status = [
        ("USER_REQUIREMENTS.md complete", req_file_exists and all_req_complete),
        (
            "All modules defined with acceptance criteria",
            has_modules and all_modules_have_criteria,
        ),
        (
            "GitHub Issues created for all modules",
            all(m.get("github_issue") for m in modules) if modules else False,
        ),
        ("User approved the plan", plan_complete),
    ]

    for criterion, met in criteria_status:
        icon = "✓" if met else " "
        lines.append(f"║ [{icon}] {criterion:<60} ║")

    lines.append("╚" + "═" * 66 + "╝")

    # Summary
    incomplete = sum(1 for _, met in criteria_status if not met)
    if plan_complete:
        lines.append(
            "\n✓ Plan Phase complete. Run /start-orchestration to begin implementation."
        )
    else:
        lines.append(
            f"\n{incomplete} exit criteria remaining. Complete them to approve the plan."
        )

    # Write verbose output to report file
    report_content = "# Planning Status Report\n\n```\n" + "\n".join(lines) + "\n```\n"
    report_path = writer.write_report(report_content)

    # Print concise summary to stdout
    summary = f"Plan: {plan_id}, Status: {status}, {incomplete} exit criteria remaining"
    writer.print_summary(summary, report_path)

    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Display Plan Phase status")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed module information"
    )

    args = parser.parse_args()
    success = display_status(verbose=args.verbose)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
