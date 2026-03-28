---
name: amama-github-routing
description: Use when routing GitHub operations (issues, PRs, projects, releases) to specialists via team labels. Trigger with GitHub requests.
version: 2.3.2
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: false
---

# GitHub Operation Routing Skill

## Overview

Routes GitHub operations to specialists via `team:{teamId}` labels, syncing to `tasks-{teamId}.json`. AMIA (Integrator, default), AMAA (Architect, design), AMOA (Orchestrator, modules).

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- AI Maestro messaging system running
- Task files at `$AGENT_DIR/teams/tasks-{teamId}.json`
- AMIA, AMAA, and AMOA agents available

## Instructions

1. Identify operation type (issue, PR, kanban, or release)
2. Determine owning team and apply `team:{teamId}` label
3. Check for design or module context affecting routing
4. Consult the decision tree for the operation type
5. Prepare handoff with required fields and team label
6. Route via AI Maestro to the target agent (all routing goes through COS)
7. Sync status to `$AGENT_DIR/teams/tasks-{teamId}.json`
8. Track handoff status and verify completion

Default: AMIA. Route to AMAA/AMOA only with design/module context. PRs/releases always AMIA.

Copy this checklist and track your progress:

- [ ] Identify operation type
- [ ] Apply team label
- [ ] Consult decision tree
- [ ] Prepare and send handoff
- [ ] Sync task file
- [ ] Verify completion

## Output

```
[ROUTED] GitHub {operation_type} -> {target_agent}
Team: {team_label} | Handoff: {status}
Task Sync: {sync_status} -> {new_task_status}
Reference: {tracking_id}
```

## Error Handling

- **Ambiguous routing**: Default to AMIA, ask user if unclear
- **Missing team label**: Infer from ownership; do NOT route until applied
- **Agent unavailable**: Queue handoff, notify user, retry, escalate on failure
- **Task sync failure**: Log, queue retry, reconcile on next success
- **Cross-team violation**: Block, log, escalate

See error-handling.md for full procedures.

## Examples

**Bug report**: "Create issue for login timeout" -> team:backend -> AMIA. Output: `[ROUTED] issue -> AMIA | team:backend | #52`

**Cross-team blocked**: AMOA-frontend closes #45 (team:backend) -> blocked. Output: `[BLOCKED] Cross-team denied`

See routing-examples.md for more.

## Resources

### Reference Files

- [team-boundaries-and-labels.md](references/team-boundaries-and-labels.md)
  - Team Label Rules
  - Team Label Application
  - Team Boundary Enforcement Decision
- [task-system-sync.md](references/task-system-sync.md)
  - Task Status Model
  - Task File Format
  - Sync Operations
  - Bidirectional Sync Rules
  - Status Mapping: GitHub Kanban Columns to AI Maestro Statuses
- [decision-trees-and-routing.md](references/decision-trees-and-routing.md)
  - Issue Operations Decision Tree
  - Pull Request Operations Decision Tree
  - Kanban/Projects Operations Decision Tree
  - Release Operations Decision Tree
- [handoff-templates-and-uuid.md](references/handoff-templates-and-uuid.md)
  - For AMIA (Integrator) GitHub Handoffs
  - For AMAA (Architect) Design-GitHub Handoffs
  - For AMOA (Orchestrator) Module-GitHub Handoffs
  - UUID Tracking Across GitHub Operations
- [routing-examples.md](references/routing-examples.md)
  - Example 1: Routing a Bug Report Issue to AMIA with Team Label
  - Example 2: Kanban Card Move with Task Sync
  - Example 3: Routing a Design-Linked Card to AMAA
  - Example 4: Cross-Team Operation Blocked
- [proactive-kanban-monitoring.md](references/proactive-kanban-monitoring.md)
  - Proactive Kanban Monitoring
  - Monitoring Schedule
  - Changes to Monitor
  - Monitoring Procedure
  - Kanban Monitoring Checklist
  - Error Handling
- [error-handling.md](references/error-handling.md)
  - Ambiguous Routing
  - Missing Context
  - Missing Team Label
  - Agent Unavailable
  - Task Sync Failures
  - Cross-Team Boundary Violation
