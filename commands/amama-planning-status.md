---
name: amama-planning-status
description: "View Plan Phase progress - requirements completion, modules defined, exit criteria status"
argument-hint: "[--verbose]"
allowed-tools: ["Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/amama_planning_status.py:*)"]
---

# Planning Status Command

View the current status of Plan Phase including requirements progress, module definitions, and exit criteria.

## Usage

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/amama_planning_status.py" $ARGUMENTS
```

## What This Command Shows

1. **Phase Status**: Current phase state (drafting/reviewing/approved)
2. **Goal**: The locked user goal
3. **Requirements Progress**: Completion status of each requirement section
4. **Modules Defined**: List of modules with their status and acceptance criteria
5. **Exit Criteria**: Checklist of conditions required to transition

## Output Format

The script prints a concise summary to stdout and writes the full detailed table to a report file:

```
[DONE] planning-status - Plan: plan-20260108-143022, Status: drafting, 4 exit criteria remaining
Report: design/reports/planning-status_20260108_143022.md
```

The full report file contains the detailed ASCII table with requirements progress, module definitions, and exit criteria checklist.

## Options

- `--verbose`: Show detailed acceptance criteria for each module

## When to Use

- After entering plan phase to verify initialization
- During planning to track progress
- Before `/amama-approve-plan` to verify all criteria met

## Related Commands

- `/amama-approve-plan` - Transition to Orchestration Phase
- `/amama-orchestration-status` - View orchestration phase status
