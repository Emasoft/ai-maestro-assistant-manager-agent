---
name: amama-github-routing
description: Use when routing GitHub operations (issues, PRs, projects, releases) to specialists via team labels. Trigger with GitHub requests.
version: 2.3.2
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: false
triggers:
  - User requests GitHub operation (issues, PRs, projects, Kanban)
  - GitHub webhook event requires agent action
  - Kanban card status change requires AI Maestro task sync
---

# GitHub Operation Routing Skill

## Overview

Routes GitHub operations (issues, PRs, Kanban, releases) to the correct specialist agent while enforcing team boundaries via `team:{teamId}` labels and syncing task state to AI Maestro's `~/.aimaestro/teams/tasks-{teamId}.json`.

**Specialist roles**: AMIA (Integrator, default GitHub handler), AMAA (Architect, design-linked ops), AMOA (Orchestrator, module-related ops).

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- AI Maestro messaging system running
- Task files at `~/.aimaestro/teams/tasks-{teamId}.json`
- AMIA, AMAA, and AMOA agents available

## Instructions

1. Identify operation type (issue/PR/kanban/release)
2. Determine owning team and apply `team:{teamId}` label (no routing without it)
3. Check for design or module context affecting routing
4. Consult the decision tree for the operation type. See [decision-trees-and-routing.md](references/decision-trees-and-routing.md)
5. Prepare handoff with required fields and team label. See [handoff-templates-and-uuid.md](references/handoff-templates-and-uuid.md)
6. Route via AI Maestro to the target agent (all routing goes through COS)
7. Sync status to `tasks-{teamId}.json`. See [task-system-sync.md](references/task-system-sync.md)
8. Track handoff status and verify completion

**Primary rule**: AMIA is the default. Route to AMAA/AMOA only when design/module context exists. All routing respects team boundaries. See [team-boundaries-and-labels.md](references/team-boundaries-and-labels.md).

**Routing summary**:
- **Issues**: AMIA (default), AMAA (design-linked), AMOA (module tasks)
- **PRs**: Always AMIA (consults AMAA/AMOA as needed)
- **Kanban**: AMIA (board sync), AMAA (design cards), AMOA (module cards), AMAMA (status queries)
- **Releases**: Always AMIA

## Output

After routing, produce:

```
[ROUTED] GitHub {operation_type} -> {target_agent}
Team: {team_label}
Handoff: {status}
Task Sync: {sync_status} -> {new_task_status}
Reference: {tracking_id}
```

## Error Handling

- **Ambiguous routing**: Default to AMIA, ask user if design/module context unclear
- **Missing team label**: Infer from module/design ownership; do NOT route until applied
- **Missing context**: Query user, search locally, flag handoff as "INCOMPLETE"
- **Agent unavailable**: Queue handoff, notify user, retry, escalate on repeated failure
- **Task sync failure**: Log, queue retry, reconcile on next success
- **Cross-team violation**: Block, log, escalate to AMAMA

See [error-handling.md](references/error-handling.md) for full procedures.

## Examples

**Bug report to AMIA**: User says "Create issue for login timeout bug." AMAMA determines team:backend, no design/module link, routes to AMIA with task sync to `backlog`. Output: `[ROUTED] GitHub issue -> AMIA | Team: team:backend | Task Sync: backlog | Ref: #52`

**Cross-team blocked**: AMOA-frontend tries to close issue #45 (team:backend). AMAMA blocks, logs violation, requires AMAMA approval. Output: `[BLOCKED] Cross-team operation denied`

See [routing-examples.md](references/routing-examples.md) for more examples including Kanban moves and design-linked cards.

## Resources

- Role Routing SKILL (see amama-role-routing skill)
- Proactive Handoff Protocol (see amama-session-memory references)
- AI Maestro Task System: `~/.aimaestro/teams/tasks-{teamId}.json`

### Reference Files

| File | Content |
|------|---------|
| [team-boundaries-and-labels.md](references/team-boundaries-and-labels.md) | Team label rules, boundary enforcement |
| [task-system-sync.md](references/task-system-sync.md) | Task status model, sync operations |
| [decision-trees-and-routing.md](references/decision-trees-and-routing.md) | Issue/PR/Kanban/Release decision trees |
| [handoff-templates-and-uuid.md](references/handoff-templates-and-uuid.md) | Handoff templates, UUID tracking |
| [routing-examples.md](references/routing-examples.md) | Worked routing examples |
| [proactive-kanban-monitoring.md](references/proactive-kanban-monitoring.md) | Kanban monitoring procedures |
| [error-handling.md](references/error-handling.md) | Detailed error handling procedures |
