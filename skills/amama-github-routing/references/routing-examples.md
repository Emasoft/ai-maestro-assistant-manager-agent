# GitHub Routing Examples

## Table of Contents

- [Example 1: Routing a Bug Report Issue to AMIA with Team Label](#example-1-routing-a-bug-report-issue-to-amia-with-team-label)
- [Example 2: Kanban Card Move with Task Sync](#example-2-kanban-card-move-with-task-sync)
- [Example 3: Routing a Design-Linked Card to AMAA](#example-3-routing-a-design-linked-card-to-amaa)
- [Example 4: Cross-Team Operation Blocked](#example-4-cross-team-operation-blocked)
- [Example 5: Task Blocked by a Dependency, Then Unblocked](#example-5-task-blocked-by-a-dependency-then-unblocked)
- [Example 6: A Failed Task Is Retried, Not Archived](#example-6-a-failed-task-is-retried-not-archived)

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
- AI Maestro task column to set: backburner
- Task file: ~/.aimaestro/teams/tasks-backend.json

# Output
[ROUTED] GitHub issue → AMIA
Team: team:backend
Handoff: Sent
Task Sync: Synced → backburner
Reference: #52
```

## Example 2: Kanban Card Move with Task Sync

```
# User request
"Move issue #45 to AI Review on the kanban board"

# AMAMA decision process
1. Operation type: KANBAN (MOVE CARD)
2. Check team label on #45: team:backend
3. Map "AI Review" column → AI Maestro column: ai_review
4. Verify the transition is legal: testing → ai_review requires all gates PASSED
5. Route to: AMIA

# Task sync
Update ~/.aimaestro/teams/tasks-backend.json:
- Task linked to #45: column "testing" → "ai_review"
- Append to columnHistory

# Output
[ROUTED] GitHub kanban → AMIA
Team: team:backend
Handoff: Sent
Task Sync: Synced → ai_review
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
Create entry in ~/.aimaestro/teams/tasks-design.json with column: backburner

# Output
[ROUTED] GitHub kanban → AMAA
Team: team:design
Handoff: Sent
Task Sync: Synced → backburner
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

## Example 5: Task Blocked by a Dependency, Then Unblocked

```
# User request
"#61 can't proceed until the email service lands in #58"

# AMAMA decision process
1. Operation type: KANBAN (MOVE CARD)
2. blocked-by on #61 becomes non-empty (#58) → the task MUST move to `blocked`
3. Route to: AMIA

# Task sync (block)
Update ~/.aimaestro/teams/tasks-backend.json for the task linked to #61:
- Stash the CURRENT column first: preBlockColumn = "dev"
- Then set column = "blocked", blockedBy = ["#58"]

# Output
[ROUTED] GitHub kanban → AMIA
Team: team:backend
Handoff: Sent
Task Sync: Synced → blocked (preBlockColumn: dev)
Reference: #61

# Later: #58 merges, blocked-by empties
# Task sync (unblock) — restore the STASHED column; never guess one
- column = preBlockColumn ("dev"), preBlockColumn = null, blockedBy = []

# Output
Task Sync: Synced → dev (restored from preBlockColumn)
Reference: #61
```

## Example 6: A Failed Task Is Retried, Not Archived

```
# Trigger
CI on #45 fails; AMIA reports the gate failure

# AMAMA decision process
1. Move the task to `failed` — it records the failed attempt
2. `failed` is NOT terminal and is NOT archived: the card STAYS on the board
3. Once the cause is fixed, the task returns to `dev` and is retried
4. Only an explicit user decision to give up converts it to `cancelled`
   (an archival lifecycle value, NOT one of the 17 board columns)

# Task sync
- column "testing" → "failed"    (the attempt failed)
- column "failed"  → "dev"       (retry after the fix — the normal path)

# Output
[ROUTED] GitHub kanban → AMIA
Team: team:backend
Handoff: Sent
Task Sync: Synced → failed (stays on the board; retry via dev)
Reference: #45
```
