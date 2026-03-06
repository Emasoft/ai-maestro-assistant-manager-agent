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

## Prerequisites

- GitHub CLI (`gh`) must be installed and authenticated
- AI Maestro messaging system must be running
- AI Maestro team task files at `~/.aimaestro/teams/tasks-{teamId}.json`
- AMIA, AMAA, and AMOA agents must be available

## Instructions

1. Identify the type of GitHub operation requested (issue, PR, kanban, release)
2. Determine the owning team and apply team label
3. Use the appropriate decision tree to determine routing
4. Check for design or module context that affects routing
5. Create handoff document with required content (including team label)
6. Send handoff to the appropriate specialist via AI Maestro
7. Sync Kanban status changes with AI Maestro task system (`~/.aimaestro/teams/tasks-{teamId}.json`)
8. Track the handoff status

## Checklist

Copy this checklist and track your progress:

- [ ] Identify GitHub operation type (issue/PR/kanban/release)
- [ ] Determine owning team and apply team label
- [ ] Check for design or module context
- [ ] Consult appropriate decision tree (issue/PR/kanban/release)
- [ ] Determine target agent (AMIA/AMAA/AMOA/AMAMA)
- [ ] Prepare handoff document with required fields and team label
- [ ] Include UUID tracking if design/module linked
- [ ] Route through COS-assigned agent (all specialist routing goes through COS, never directly to specialists)
- [ ] Sync task status to `~/.aimaestro/teams/tasks-{teamId}.json`
- [ ] Log routing decision
- [ ] Track handoff status
- [ ] Verify operation completion

## Overview

This skill provides decision trees for routing GitHub operations to the appropriate specialist role while enforcing team boundaries via labels and syncing all task state changes with AI Maestro's centralized task system.

Specialist roles:
- **AMIA** (Integrator Agent) - Primary GitHub handler
- **AMAA** (Architect Agent) - Design-linked GitHub operations
- **AMOA** (Orchestrator Agent) - Module-related GitHub operations

## Team Boundaries and Labels

All GitHub issues must have a `team:{teamId}` label. Every issue needs exactly one team label before routing. Cross-team operations require AMAMA escalation.

Key rules:
- **No routing without a team label** - determine and apply before proceeding
- **Team labels determine visibility** - agents only operate on their team's issues
- **Cross-team = escalation** - agents cannot modify other teams' issues without AMAMA approval

For full team label rules, application commands, and the boundary enforcement decision tree, see [team-boundaries-and-labels.md](references/team-boundaries-and-labels.md).

## AI Maestro Task System Sync

All Kanban card movements and issue status changes sync to `~/.aimaestro/teams/tasks-{teamId}.json`. AI Maestro uses a 5-status pipeline: `backlog` -> `pending` -> `in_progress` -> `review` -> `completed`.

Sync is bidirectional: GitHub changes update the task file, and AI Maestro task changes update GitHub Kanban cards.

For the full status model, task file format, sync operations, and status mapping, see [task-system-sync.md](references/task-system-sync.md).

## Primary Routing Principle

**AMIA is the default GitHub handler.** Route to AMAA or AMOA only when the operation has design or module context. All routing must respect team boundaries.

## Master Decision Tree

```
GitHub operation requested
          │
          ▼
┌────────────────────────────┐
│  Enforce team boundary     │
│  (see Team Boundaries)     │
└──────────────┬─────────────┘
               │
               ▼
┌────────────────────────────┐
│  What type of operation?   │
└──────────────┬─────────────┘
               │
    ┌──────────┼──────────┬──────────────┐
    │          │          │              │
    ▼          ▼          ▼              ▼
 ISSUE       PR      KANBAN/PROJECT   RELEASE
    │          │          │              │
    ▼          ▼          ▼              ▼
[Issue      [PR        [Project       [Release
 Tree]       Tree]      Tree]          Tree]
    │          │          │              │
    └──────────┴──────────┴──────────────┘
               │
               ▼
    ┌────────────────────────┐
    │ Sync to AI Maestro     │
    │ task system             │
    └────────────────────────┘
```

## Decision Trees and Routing Matrices

All operation-specific decision trees and routing matrices are in [decision-trees-and-routing.md](references/decision-trees-and-routing.md):
  - Contents
  - Issue Operations Decision Tree
  - Issue Routing Matrix
  - Pull Request Operations Decision Tree
  - PR Routing Matrix
  - Kanban/Projects Operations Decision Tree

- **Issue Operations** - Routes to AMIA (default), AMAA (design-linked), or AMOA (module tasks). Includes issue routing matrix.
- **Pull Request Operations** - All PR operations route to AMIA. AMIA consults AMAA/AMOA as needed. PR merges trigger task sync.
- **Kanban/Projects Operations** - Board sync to AMIA, design cards to AMAA, module cards to AMOA, status queries handled locally. Includes Kanban-to-Task sync procedure.
- **Release Operations** - All release operations route to AMIA (Integrator owns releases). Releases sync included issues to `completed`.

## Handoff Content Requirements

Each specialist agent requires specific handoff content. Templates are available in [handoff-templates-and-uuid.md](references/handoff-templates-and-uuid.md):
  - For AMIA (Integrator) GitHub Handoffs
  - For AMAA (Architect) Design-GitHub Handoffs
  - For AMOA (Orchestrator) Module-GitHub Handoffs
  - UUID Tracking Across GitHub Operations

- **AMIA handoffs**: Operation type, action, target, team label, details, expected outcome, task sync status
- **AMAA handoffs**: Design UUID, design path, GitHub target, team label, link context, expected outcome
- **AMOA handoffs**: Module UUID, design reference, GitHub target, team label, implementation context, task details

## UUID Tracking Across GitHub Operations

Design and module UUIDs are embedded in GitHub items (issue bodies, PR descriptions, Kanban card notes) using `AMAMA-LINK` comment tags. UUIDs enable cross-referencing between designs, modules, and GitHub items.

For UUID reference formats and search commands, see [handoff-templates-and-uuid.md](references/handoff-templates-and-uuid.md#uuid-tracking-across-github-operations).
  - UUID Tracking Across GitHub Operations
  - For AMIA (Integrator) GitHub Handoffs
  - For AMAA (Architect) Design-GitHub Handoffs

## Error Handling

### Ambiguous Routing

If operation could go to multiple agents:
1. Default to AMIA (most GitHub operations)
2. Ask user for clarification if design/module context unclear
3. Log routing decision for audit

### Missing Context

If handoff lacks required information:
1. Query user for missing details
2. Search locally (design search) before asking
3. Include "INCOMPLETE" flag in handoff for receiving agent

### Missing Team Label

If an issue has no team label:
1. Check the module/design ownership for team inference
2. Check the requesting agent's team affiliation
3. If still ambiguous, ask the user to assign a team
4. Do NOT route until a team label is applied

### Agent Unavailable

If target agent is not responding:
1. Queue the handoff
2. Notify user of delay
3. Retry after configured interval
4. Escalate to user if repeated failures

### Task Sync Failures

If task file sync fails:
1. Log the failure with timestamp and intended state change
2. Queue the sync for retry
3. On next successful operation, reconcile queued syncs
4. If task file is corrupted, rebuild from GitHub issue state using `gh issue list --label "team:${TEAM_ID}" --state all --json` and jq

### Cross-Team Boundary Violation

If an agent attempts to modify an issue outside its team:
1. Block the operation
2. Log the violation attempt
3. Notify AMAMA for escalation
4. AMAMA may approve the cross-team operation or redirect

## Output

After routing a GitHub operation, AMAMA should produce:

| Output Element | Content |
|----------------|---------|
| **Routing Decision** | Which agent (AMIA/AMAA/AMOA/AMAMA) received the operation |
| **Operation Type** | Issue/PR/Kanban/Release |
| **Team Label** | The team label applied to the operation |
| **Handoff Status** | Sent/Queued/Failed |
| **Task Sync Status** | Synced/Pending/Failed |
| **Tracking Reference** | UUID or GitHub item number for follow-up |

**Format**:
```
[ROUTED] GitHub {operation_type} → {target_agent}
Team: {team_label}
Handoff: {status}
Task Sync: {sync_status} → {new_task_status}
Reference: {tracking_id}
```

## Examples

For detailed worked examples, see [routing-examples.md](references/routing-examples.md):
  - Example 1: Routing a Bug Report Issue to AMIA with Team Label
  - Example 2: Kanban Card Move with Task Sync
  - Example 3: Routing a Design-Linked Card to AMAA
  - Example 4: Cross-Team Operation Blocked

1. **Bug report to AMIA** - Standard issue creation with team label and task sync to `backlog`
2. **Kanban card move** - Moving an issue to "In Review" with bidirectional task sync
3. **Design-linked card to AMAA** - Creating a Kanban card linked to a design document
4. **Cross-team operation blocked** - Agent from team:frontend denied access to team:backend issue

**For proactive kanban monitoring procedures, see [proactive-kanban-monitoring.md](references/proactive-kanban-monitoring.md):**
- [Monitoring Schedule](references/proactive-kanban-monitoring.md#monitoring-schedule) - Polling GitHub Project API for card changes
- [Changes to Monitor](references/proactive-kanban-monitoring.md#changes-to-monitor) - Status changes, new assignees, new comments, card creation/archival
- [Monitoring Procedure](references/proactive-kanban-monitoring.md#monitoring-procedure) - Snapshot capture, comparison, change processing, state update
- [Kanban Monitoring Checklist](references/proactive-kanban-monitoring.md#kanban-monitoring-checklist) - Step-by-step verification checklist
- [Error Handling](references/proactive-kanban-monitoring.md#error-handling) - Auth failures, missing snapshots, rate limits

## Resources

- Role Routing SKILL (see amama-role-routing skill)
- Proactive Handoff Protocol (see amama-session-memory references)
- Handoff Template (see shared templates directory)
- AI Maestro Task System - `~/.aimaestro/teams/tasks-{teamId}.json`
- AI Maestro Team Configuration - `~/.aimaestro/teams/`

### Reference Files

| File | Content |
|------|---------|
| [team-boundaries-and-labels.md](references/team-boundaries-and-labels.md) | Team label rules, application commands, boundary enforcement decision tree |
| [task-system-sync.md](references/task-system-sync.md) | Task status model, file format, sync operations, bidirectional sync rules, status mapping |
| [decision-trees-and-routing.md](references/decision-trees-and-routing.md) | Issue, PR, Kanban, and Release decision trees and routing matrices |
| [handoff-templates-and-uuid.md](references/handoff-templates-and-uuid.md) | Handoff templates for AMIA/AMAA/AMOA and UUID tracking format |
| [routing-examples.md](references/routing-examples.md) | Worked examples of routing decisions |
| [proactive-kanban-monitoring.md](references/proactive-kanban-monitoring.md) | Proactive Kanban monitoring schedule, procedures, and error handling |

**decision-trees-and-routing.md sections:**
  - Contents
  - Issue Operations Decision Tree
  - Issue Routing Matrix
  - Pull Request Operations Decision Tree
  - PR Routing Matrix
  - Kanban/Projects Operations Decision Tree

**handoff-templates-and-uuid.md sections:**
  - For AMIA (Integrator) GitHub Handoffs
  - For AMAA (Architect) Design-GitHub Handoffs
  - For AMOA (Orchestrator) Module-GitHub Handoffs
  - UUID Tracking Across GitHub Operations

**routing-examples.md sections:**
  - Example 1: Routing a Bug Report Issue to AMIA with Team Label
  - Example 2: Kanban Card Move with Task Sync
  - Example 3: Routing a Design-Linked Card to AMAA
  - Example 4: Cross-Team Operation Blocked
