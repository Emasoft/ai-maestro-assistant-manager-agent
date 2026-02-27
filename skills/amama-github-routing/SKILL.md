---
name: amama-github-routing
description: Use when routing GitHub operations (issues, PRs, projects, releases) to the appropriate specialist agent. Enforces team boundaries via labels and syncs Kanban with AI Maestro task system. Trigger with GitHub-related requests.
version: 2.0.0
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
- [ ] Send handoff via AI Maestro
- [ ] Sync task status to `~/.aimaestro/teams/tasks-{teamId}.json`
- [ ] Log routing decision
- [ ] Track handoff status
- [ ] Verify operation completion

## Table of Contents

1. [Team Boundaries and Labels](#team-boundaries-and-labels)
2. [AI Maestro Task System Sync](#ai-maestro-task-system-sync)
3. [Primary Routing Principle](#primary-routing-principle)
4. [Master Decision Tree](#master-decision-tree)
5. [Issue Operations Decision Tree](#issue-operations-decision-tree)
   - 5.1 [Issue Routing Matrix](#issue-routing-matrix)
6. [Pull Request Operations Decision Tree](#pull-request-operations-decision-tree)
   - 6.1 [PR Routing Matrix](#pr-routing-matrix)
7. [Kanban/Projects Operations Decision Tree](#kanbanprojects-operations-decision-tree)
   - 7.1 [Kanban Routing Matrix](#kanban-routing-matrix)
8. [Release Operations Decision Tree](#release-operations-decision-tree)
   - 8.1 [Release Routing Matrix](#release-routing-matrix)
9. [Handoff Content Requirements](#handoff-content-requirements)
   - 9.1 [For AMIA (Integrator) GitHub Handoffs](#for-eia-integrator-github-handoffs)
   - 9.2 [For AMAA (Architect) Design-GitHub Handoffs](#for-eaa-architect-design-github-handoffs)
   - 9.3 [For AMOA (Orchestrator) Module-GitHub Handoffs](#for-eoa-orchestrator-module-github-handoffs)
10. [UUID Tracking Across GitHub Operations](#uuid-tracking-across-github-operations)
    - 10.1 [UUID Reference Format in GitHub](#uuid-reference-format-in-github)
    - 10.2 [Searching by UUID](#searching-by-uuid)
11. [Error Handling](#error-handling)
    - 11.1 [Ambiguous Routing](#ambiguous-routing)
    - 11.2 [Missing Context](#missing-context)
    - 11.3 [Agent Unavailable](#agent-unavailable)
    - 11.4 [Task Sync Failures](#task-sync-failures)
12. [References](#references)

---

## Overview

This skill provides decision trees for routing GitHub operations to the appropriate specialist role while enforcing team boundaries via labels and syncing all task state changes with AI Maestro's centralized task system.

Specialist roles:
- **AMIA** (Integrator Agent) - Primary GitHub handler
- **AMAA** (Architect Agent) - Design-linked GitHub operations
- **AMOA** (Orchestrator Agent) - Module-related GitHub operations

## Team Boundaries and Labels

All GitHub issues must be tagged with a team label to enforce team boundaries. Team labels follow the format `team:{teamId}`.

### Team Label Rules

1. **Every issue MUST have exactly one team label** - Issues without team labels are invalid and must be labeled before routing.
2. **Team labels determine visibility** - Agents only see and operate on issues belonging to their team.
3. **Cross-team operations require explicit approval** - An agent from team-A cannot modify issues labeled `team:team-B` without AMAMA escalation.
4. **Label format**: `team:{teamId}` (e.g., `team:frontend`, `team:backend`, `team:infra`, `team:design`)

### Team Label Application

When creating or routing an issue:

```bash
# Add team label on issue creation
gh issue create --title "Fix login timeout" --label "bug,team:backend"

# Add team label to existing issue
gh issue edit 42 --add-label "team:frontend"

# Query issues for a specific team
gh issue list --label "team:backend"
```

### Team Boundary Enforcement Decision

```
GitHub operation received
          │
          ▼
┌────────────────────────────┐
│  Does issue have team      │
│  label?                    │
└──────────────┬─────────────┘
        ┌──────┴──────┐
        │ YES         │ NO
        ▼             ▼
┌──────────────┐  ┌──────────────────────┐
│ Does the     │  │ Determine owning     │
│ requesting   │  │ team from context:   │
│ agent belong │  │ - Module ownership   │
│ to this team?│  │ - Design ownership   │
└──────┬───────┘  │ - User specification │
       │          └──────────┬───────────┘
  ┌────┴────┐                │
  │YES  │NO │          Apply team label
  ▼     ▼   │          then proceed
PROCEED  ESCALATE            │
         to AMAMA            ▼
         for cross-    PROCEED with
         team approval routing
```

## AI Maestro Task System Sync

All Kanban card movements and issue status changes must be synced with AI Maestro's task system at `~/.aimaestro/teams/tasks-{teamId}.json`.

### Task Status Model

AI Maestro uses a 5-status pipeline for all tasks:

| Status | Description | GitHub Kanban Column | Transitions From | Transitions To |
|--------|-------------|---------------------|------------------|----------------|
| `backlog` | Identified but not yet prioritized | Backlog | (entry) | `pending` |
| `pending` | Prioritized and ready to be picked up | To Do / Ready | `backlog` | `in_progress` |
| `in_progress` | Actively being worked on | In Progress | `pending` | `review` |
| `review` | Work complete, awaiting review/approval | In Review | `in_progress` | `completed`, `in_progress` |
| `completed` | Done and verified | Done | `review` | (terminal) |

### Task File Format

**Location**: `~/.aimaestro/teams/tasks-{teamId}.json`

```json
{
  "teamId": "backend",
  "lastUpdated": "2025-01-30T15:00:00Z",
  "tasks": [
    {
      "id": "task-uuid-001",
      "githubIssue": 45,
      "githubRepo": "owner/repo",
      "title": "Implement user auth",
      "status": "in_progress",
      "assignedAgent": "amoa-backend-auth",
      "teamLabel": "team:backend",
      "designUuid": "abc-123",
      "moduleUuid": "def-456",
      "statusHistory": [
        {"status": "backlog", "timestamp": "2025-01-28T10:00:00Z", "actor": "amama-main"},
        {"status": "pending", "timestamp": "2025-01-29T09:00:00Z", "actor": "amama-main"},
        {"status": "in_progress", "timestamp": "2025-01-30T14:00:00Z", "actor": "amoa-backend-auth"}
      ],
      "createdAt": "2025-01-28T10:00:00Z",
      "updatedAt": "2025-01-30T14:00:00Z"
    }
  ]
}
```

### Sync Operations

Every GitHub status change triggers a sync to the task file:

```bash
# Read current task state
TASK_FILE="$HOME/.aimaestro/teams/tasks-${TEAM_ID}.json"

# Update task status (using jq for atomic JSON update)
jq --arg taskId "$TASK_ID" --arg newStatus "$NEW_STATUS" --arg actor "$SESSION_NAME" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '(.tasks[] | select(.id == $taskId)) |= (
    .status = $newStatus |
    .updatedAt = $ts |
    .statusHistory += [{"status": $newStatus, "timestamp": $ts, "actor": $actor}]
  ) | .lastUpdated = $ts' \
  "$TASK_FILE" > "${TASK_FILE}.tmp" && mv "${TASK_FILE}.tmp" "$TASK_FILE"
```

### Bidirectional Sync Rules

| Direction | Trigger | Action |
|-----------|---------|--------|
| GitHub to AI Maestro | Kanban card moved | Update `tasks-{teamId}.json` with new status |
| GitHub to AI Maestro | Issue closed | Set task status to `completed` |
| GitHub to AI Maestro | Issue reopened | Set task status to `in_progress` |
| AI Maestro to GitHub | Task status changed via API | Move corresponding Kanban card |
| AI Maestro to GitHub | New task created | Create GitHub issue with team label |

### Status Mapping: GitHub Kanban Columns to AI Maestro Statuses

| GitHub Kanban Column | AI Maestro Status |
|---------------------|-------------------|
| Backlog | `backlog` |
| To Do / Ready | `pending` |
| In Progress | `in_progress` |
| In Review / Review | `review` |
| Done / Closed | `completed` |

If a GitHub project uses custom column names, AMAMA must maintain a mapping in:
`~/.aimaestro/teams/kanban-column-map-{teamId}.json`

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

## Issue Operations Decision Tree

```
┌─────────────────────────────────┐
│ Issue operation requested       │
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ Does issue have team label?     │
│ If NO: determine team, apply    │
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ Is this linked to a design doc? │
└───────────────┬─────────────────┘
        ┌───────┴───────┐
        │ YES           │ NO
        ▼               ▼
┌───────────────┐  ┌─────────────────────┐
│ What action?  │  │ Is this a module    │
└───────┬───────┘  │ implementation task?│
        │          └──────────┬──────────┘
    ┌───┴───┐          ┌──────┴───────┐
    │       │          │ YES          │ NO
    ▼       ▼          ▼              ▼
CREATE   UPDATE   ┌──────────┐   ┌──────────┐
LINK     LINK     │ Route to │   │ Route to │
    │       │     │ AMOA      │   │ AMIA      │
    │       │     └──────────┘   └──────────┘
    ▼       ▼
┌──────────────┐
│ Route to AMAA │
│ with design  │
│ UUID         │
└──────────────┘
        │
        ▼
┌──────────────────────────┐
│ Sync new issue/status    │
│ to tasks-{teamId}.json   │
└──────────────────────────┘
```

### Issue Routing Matrix

| Scenario | Route To | Handoff Content | Team Label |
|----------|----------|-----------------|------------|
| Create bug report | AMIA | Issue template, reproduction steps | Required: `team:{teamId}` |
| Create feature request | AMIA | Issue template, requirements | Required: `team:{teamId}` |
| Create issue FROM design | AMAA | Design UUID, section reference | Inherit from design team |
| Link existing issue to design | AMAA | Issue number, design UUID | Verify team match |
| Update issue labels/status | AMIA | Issue number, changes | Verify team ownership |
| Close issue with verification | AMIA | Issue number, verification results | Sync `completed` to task file |
| Create module task issue | AMOA | Module UUID, task details | Inherit from module team |
| Track implementation progress | AMOA | Issue number, module UUID | Sync status to task file |

## Pull Request Operations Decision Tree

```
┌─────────────────────────────────┐
│ PR operation requested          │
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ What operation type?            │
└───────────────┬─────────────────┘
                │
    ┌───────────┼───────────┬────────────┐
    │           │           │            │
    ▼           ▼           ▼            ▼
 CREATE      REVIEW      MERGE       UPDATE
    │           │           │            │
    ▼           ▼           ▼            ▼
┌────────┐ ┌────────┐ ┌────────┐  ┌────────┐
│ Route  │ │ Route  │ │ Route  │  │ Route  │
│ to AMIA │ │ to AMIA │ │ to AMIA │  │ to AMIA │
└────────┘ └────────┘ └────────┘  └────────┘
    │           │           │            │
    └───────────┴───────────┴────────────┘
                │
                ▼
    ┌────────────────────────────────┐
    │ On merge: sync linked issues   │
    │ to `review` or `completed`     │
    └────────────────────────────────┘
```

**Note**: All PR operations go to AMIA. AMIA may consult with AMAA for design validation or AMOA for implementation verification. PR merges trigger task status sync for linked issues.

### PR Routing Matrix

| Operation | Route To | Handoff Content | Task Sync |
|-----------|----------|-----------------|-----------|
| Create PR | AMIA | Branch, description, linked issues, team label | Linked issues to `review` |
| Review PR | AMIA | PR number, review criteria | None |
| Request changes | AMIA | PR number, requested changes | Linked issues back to `in_progress` |
| Approve PR | AMIA | PR number, approval notes | None |
| Merge PR | AMIA | PR number, merge strategy | Linked issues to `completed` |
| Close PR without merge | AMIA | PR number, reason | Linked issues back to `in_progress` |

## Kanban/Projects Operations Decision Tree

```
┌─────────────────────────────────┐
│ Kanban/Project operation        │
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ What operation type?            │
└───────────────┬─────────────────┘
                │
    ┌───────────┼───────────┬───────────────┐
    │           │           │               │
    ▼           ▼           ▼               ▼
  SYNC      CREATE       MOVE           STATUS
  BOARD      ITEM        CARD           QUERY
    │           │           │               │
    ▼           ▼           ▼               ▼
┌────────┐ ┌─────────────────────┐   ┌──────────┐
│ Route  │ │ Is item a design    │   │ Handle   │
│ to AMIA │ │ or module?          │   │ locally  │
│ + sync │ └──────────┬──────────┘   │ (AMAMA)  │
│ task   │            │              └──────────┘
│ file   │    ┌───────┴───────┐
└────────┘    │ DESIGN        │ MODULE
              ▼               ▼
        ┌──────────┐   ┌──────────┐
        │ Route to │   │ Route to │
        │ AMAA      │   │ AMOA      │
        │ + sync   │   │ + sync   │
        │ task file│   │ task file│
        └──────────┘   └──────────┘
```

**All card movements MUST be synced to `~/.aimaestro/teams/tasks-{teamId}.json`.**

### Kanban Routing Matrix

| Operation | Route To | Handoff Content | Task Sync |
|-----------|----------|-----------------|-----------|
| Sync board with GitHub | AMIA | Project ID, sync scope | Full reconciliation with task file |
| Create design card | AMAA | Design UUID, card details, team label | Create task entry as `backlog` |
| Create module card | AMOA | Module UUID, card details, team label | Create task entry as `backlog` |
| Move card (non-specific) | AMIA | Card ID, target column, team label | Update task status |
| Move design card | AMAA | Card ID, design context | Update task status |
| Move module card | AMOA | Card ID, module context | Update task status |
| Query board status | AMAMA (local) | Project ID | Read from task file for fast response |
| Archive completed items | AMIA | Project ID, archive criteria | Remove `completed` tasks older than threshold |

### Kanban-to-Task Sync Procedure

When a Kanban card moves:

1. Identify the GitHub issue linked to the card
2. Determine the team from the issue's `team:{teamId}` label
3. Map the target Kanban column to an AI Maestro status
4. Update `~/.aimaestro/teams/tasks-{teamId}.json`:
   - Set `status` to the new AI Maestro status
   - Append to `statusHistory`
   - Update `updatedAt` timestamp
5. If the task does not exist in the file, create it
6. Validate the status transition is legal (see Status Model above)

## Release Operations Decision Tree

```
┌─────────────────────────────────┐
│ Release operation requested     │
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ All operations go to AMIA        │
│ (Integrator owns releases)      │
└───────────────┬─────────────────┘
                │
                ▼
          ┌──────────┐
          │ Route to │
          │ AMIA      │
          └──────────┘
                │
                ▼
    ┌────────────────────────────┐
    │ On release: sync all       │
    │ included issues to         │
    │ `completed` in task files  │
    └────────────────────────────┘
```

### Release Routing Matrix

| Operation | Route To | Handoff Content | Task Sync |
|-----------|----------|-----------------|-----------|
| Create release | AMIA | Version, changelog, assets | Mark included issues `completed` |
| Draft release notes | AMIA | Version, commit range | None |
| Tag version | AMIA | Tag name, commit SHA | None |
| Publish release | AMIA | Release ID, publish settings | Mark included issues `completed` |
| Update release | AMIA | Release ID, changes | None |

## Handoff Content Requirements

### For AMIA (Integrator) GitHub Handoffs

```markdown
## GitHub Operation Handoff

**Operation Type**: [issue|pr|kanban|release]
**Action**: [create|update|close|merge|sync|etc.]
**Target**: [repo, issue number, PR number, project ID]
**Team Label**: team:{teamId}

### Details
- Specific operation parameters
- Any linked references

### Expected Outcome
- What success looks like
- Verification criteria

### Task Sync Required
- AI Maestro task status to set: [backlog|pending|in_progress|review|completed]
- Task file: ~/.aimaestro/teams/tasks-{teamId}.json
```

### For AMAA (Architect) Design-GitHub Handoffs

```markdown
## Design-GitHub Link Handoff

**Design UUID**: [uuid]
**Design Path**: [path to design doc]
**GitHub Target**: [issue/card number or ID]
**Team Label**: team:{teamId}

### Link Context
- Why this link exists
- What the GitHub item represents in the design

### Expected Outcome
- Design doc updated with GitHub reference
- GitHub item updated with design reference

### Task Sync Required
- AI Maestro task status to set: [backlog|pending|in_progress|review|completed]
- Task file: ~/.aimaestro/teams/tasks-{teamId}.json
```

### For AMOA (Orchestrator) Module-GitHub Handoffs

```markdown
## Module-GitHub Handoff

**Module UUID**: [uuid]
**Design Reference**: [design UUID]
**GitHub Target**: [issue/card number or ID]
**Team Label**: team:{teamId}

### Implementation Context
- Module's role in overall implementation
- Dependencies on other modules

### Task Details
- Specific implementation task
- Acceptance criteria

### Task Sync Required
- AI Maestro task status to set: [backlog|pending|in_progress|review|completed]
- Task file: ~/.aimaestro/teams/tasks-{teamId}.json
```

## UUID Tracking Across GitHub Operations

### UUID Reference Format in GitHub

When creating GitHub items linked to designs/modules, include UUID reference and team label:

**In Issue Body**:
```markdown
<!-- AMAMA-LINK: design-uuid=abc123 -->
<!-- AMAMA-LINK: module-uuid=def456 -->
<!-- AMAMA-TEAM: team:backend -->
```

**In PR Description**:
```markdown
## Related Design
Design UUID: `abc123` (path: `design/feature-x/DESIGN.md`)
Team: `team:backend`

## Implementing Modules
- Module UUID: `def456` (component-a)
- Module UUID: `ghi789` (component-b)
```

**In Kanban Card Notes**:
```
DESIGN: abc123
MODULE: def456
TEAM: backend
```

### Searching by UUID

AMAMA can find GitHub items by UUID using:
```bash
gh issue list --search "AMAMA-LINK: design-uuid=abc123"
gh pr list --search "Design UUID: abc123"
gh issue list --label "team:backend" --search "AMAMA-LINK: module-uuid=def456"
```

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
4. If task file is corrupted, rebuild from GitHub issue state:
   ```bash
   # Rebuild task file from GitHub for a team
   gh issue list --label "team:${TEAM_ID}" --state all --json number,title,state,labels \
     | jq '[.[] | {id: ("task-gh-" + (.number|tostring)), githubIssue: .number, title: .title, status: (if .state == "CLOSED" then "completed" else "in_progress" end)}]'
   ```

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

### Example 1: Routing a Bug Report Issue to AMIA with Team Label

```
# User request
"Create an issue for the login timeout bug"

# AMAMA decision process
1. Operation type: ISSUE
2. Determine team: login → backend team
3. Apply label: team:backend
4. Is linked to design doc? NO
5. Is module implementation task? NO
6. Route to: AMIA

# Handoff content
## GitHub Operation Handoff

**Operation Type**: issue
**Action**: create
**Target**: main repo
**Team Label**: team:backend

### Details
- Title: Login timeout bug
- Labels: bug, high-priority, team:backend
- Body: Users experiencing timeout after 30 seconds

### Expected Outcome
- Issue created with appropriate labels including team:backend
- Issue number returned

### Task Sync Required
- AI Maestro task status to set: backlog
- Task file: ~/.aimaestro/teams/tasks-backend.json

# Output
[ROUTED] GitHub issue → AMIA
Team: team:backend
Handoff: Sent
Task Sync: Synced → backlog
Reference: #52
```

### Example 2: Kanban Card Move with Task Sync

```
# User request
"Move issue #45 to In Review on the kanban board"

# AMAMA decision process
1. Operation type: KANBAN (MOVE CARD)
2. Check team label on #45: team:backend
3. Map "In Review" column → AI Maestro status: review
4. Route to: AMIA

# Task sync
Update ~/.aimaestro/teams/tasks-backend.json:
- Task linked to #45: status "in_progress" → "review"
- Append to statusHistory

# Output
[ROUTED] GitHub kanban → AMIA
Team: team:backend
Handoff: Sent
Task Sync: Synced → review
Reference: #45
```

### Example 3: Routing a Design-Linked Card to AMAA

```
# User request
"Create a kanban card for the authentication design"

# AMAMA decision process
1. Operation type: KANBAN
2. Determine team from design ownership: team:design
3. Is item design or module? DESIGN
4. Route to: AMAA

# Task sync
Create entry in ~/.aimaestro/teams/tasks-design.json with status: backlog

# Output
[ROUTED] GitHub kanban → AMAA
Team: team:design
Handoff: Sent
Task Sync: Synced → backlog
Reference: design-uuid-abc123
```

### Example 4: Cross-Team Operation Blocked

```
# Agent AMOA-frontend attempts to close issue #45 (labeled team:backend)

# AMAMA enforcement
1. Check: AMOA-frontend team = frontend
2. Check: Issue #45 team label = team:backend
3. MISMATCH: Block operation

# Output
[BLOCKED] Cross-team operation denied
Agent: AMOA-frontend (team:frontend)
Target: Issue #45 (team:backend)
Action required: AMAMA approval for cross-team operation
```

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
