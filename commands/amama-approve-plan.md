---
name: amama-approve-plan
description: "Approve the plan and transition from Plan Phase to Orchestration Phase"
argument-hint: ""
allowed-tools: ["Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/amama_approve_plan.py:*)"]
---

# Approve Plan Command

Mark the plan as approved and transition from Plan Phase to Orchestration Phase. This is the critical transition point that enables implementation.

## Usage

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/amama_approve_plan.py"
```

This command takes no arguments.

## What This Command Does

1. **Validates prerequisites**
   - The plan-phase state file (`.claude/orchestrator-plan-phase.local.md`) exists
   - `USER_REQUIREMENTS.md` exists

2. **Writes the orchestration-phase state file**
   - Creates `.claude/orchestrator-exec-phase.local.md` with `Status: ready` and `Plan Approved: true`

3. **Marks the plan phase complete**
   - Flips `plan_phase_complete: false` → `true` in the plan-phase state file (idempotent — a plan already marked complete is left byte-identical)

4. **Outputs a transition summary**
   - Prints a one-line summary to stdout; writes the full table to a report file under `reports/plan-approval/`

> This command does **not** create GitHub issues. An earlier draft advertised per-module issue creation that was never implemented (`modules` was hardcoded empty); the false claim and its dead `--skip-issues` flag were removed so the command's contract matches its behaviour. Per-module issue creation, if wanted later, is a separate feature with its own design.

## Prerequisites

Before running this command:
- [ ] `USER_REQUIREMENTS.md` must exist
- [ ] You must be in the Plan Phase (the plan-phase state file must exist)

Use `/amama-planning-status` to verify.

## Transition Flow

```
Plan Phase State File (.claude/orchestrator-plan-phase.local.md)
    |
    | /amama-approve-plan validates prerequisites
    v
plan_phase_complete: true
    |
    v
Orchestration Phase State File (.claude/orchestrator-exec-phase.local.md)
    |
    v
Orchestration Phase begins
```

## Output Example

The script prints a concise summary to stdout and writes the full table to a report file:

```
[DONE] approve-plan - Plan plan-20260108-143022 approved. State files created.
Report: reports/plan-approval/20260108_143022-plan-approval.md
```

## Error Conditions

| Error | Cause | Solution |
|-------|-------|----------|
| "No plan phase state file found" | Not in Plan Phase | Run `/start-planning` first |
| "USER_REQUIREMENTS.md not found" | File doesn't exist | Create the requirements document |

## Related Commands

- `/amama-planning-status` - Verify prerequisites
- `/amama-orchestration-status` - View orchestration phase status
