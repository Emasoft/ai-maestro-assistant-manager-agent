---
name: amama-orchestration-status
description: "View Orchestration Phase progress - modules, agents, assignments, verification status"
argument-hint: "[--verbose] [--agents-only] [--modules-only]"
allowed-tools: ["Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/amama_orchestration_status.py:*)"]
---

# Orchestration Status Command

View the current status of Orchestration Phase including module progress, agent assignments, and verification status.

## Usage

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/amama_orchestration_status.py" $ARGUMENTS
```

## What This Command Shows

1. **Phase Status**: Current orchestration state
2. **Module Progress**: Completion status of each module
3. **Agent Registry**: Registered AI and human agents
4. **Active Assignments**: Current module-agent mappings
5. **Instruction Verification**: Status of understanding confirmation
6. **Progress Polling**: Last poll times and issue reports
7. **Verification Loops**: PR verification countdown

## Output Format

The script prints a concise summary to stdout and writes the full detailed table to a report file:

```
[DONE] orchestration-status - Plan: plan-20260108-143022, Status: executing, Progress: 1/3
Report: design/reports/orchestration-status_20260108_143022.md
```

The full report file contains the detailed ASCII table with module status, agent registry, active assignments, and verification status.

## Options

| Option | Description |
|--------|-------------|
| `--verbose` | Show detailed polling history and criteria |
| `--agents-only` | Show only agent information |
| `--modules-only` | Show only module status |

## Key Metrics

- **Modules Completed**: X/Y (percentage)
- **Active Assignments**: Currently working agents
- **Verification Status**: Pre-implementation confirmation
- **Poll Compliance**: Time since last progress check
- **Issues Reported**: Problems raised during polling

## Related Commands

- `/amama-approve-plan` - Approve plan and transition to orchestration
- `/amama-planning-status` - View planning phase status
- `/amama-respond-to-amcos` - Respond to COS approval requests
