# GitHub Routing Examples

## Table of Contents

- [Example 1: Routing a Bug Report Issue to AMIA with Team Label](#example-1-routing-a-bug-report-issue-to-amia-with-team-label)
- [Example 2: Kanban Card Move with Task Sync](#example-2-kanban-card-move-with-task-sync)
- [Example 3: Routing a Design-Linked Card to AMAA](#example-3-routing-a-design-linked-card-to-amaa)
- [Example 4: Cross-Team Operation Blocked](#example-4-cross-team-operation-blocked)

## Example 1: Routing a Bug Report Issue to AMIA with Team Label

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

## Example 2: Kanban Card Move with Task Sync

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

## Example 3: Routing a Design-Linked Card to AMAA

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

## Example 4: Cross-Team Operation Blocked

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
