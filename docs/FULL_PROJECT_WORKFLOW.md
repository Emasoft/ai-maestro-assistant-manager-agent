# Team-Based Project Workflow

## Workflow Phases

### Phase 1: Team Creation

| Step | Actor | Action | API |
|------|-------|--------|-----|
| 1 | MANAGER | Create GitHub repo + team | `POST /api/teams` |
| 2 | MANAGER | Assign COS to team | `PATCH /api/teams/{id}/chief-of-staff` |
| 3 | COS | Propose member roster | GovernanceRequest to MANAGER |
| 4 | MANAGER | Approve roster | `POST /api/v1/governance/requests/{id}/approve` |
| 5 | COS | Add members to team | `POST /api/teams/{id}/members` |

### Phase 2: Design

| Step | Actor | Action |
|------|-------|--------|
| 6 | MANAGER | Send requirements to COS |
| 7 | COS | Assign design task to architect-skilled member |
| 8 | Member | Create design document |
| 9 | COS | Forward design to manager |
| 10 | MANAGER | Get user approval; send approved design to COS |

### Phase 3: Task Planning

| Step | Actor | Action |
|------|-------|--------|
| 11 | COS | Decompose design into tasks |
| 12 | COS | Create task issues on GitHub kanban |
| 13 | COS | Assign tasks to members |
| 14 | Members | Request clarifications if needed |

### Phase 4: Implementation

| Step | Actor | Action |
|------|-------|--------|
| 15 | Members | Work on assigned tasks |
| 16 | COS | Move tasks: `pending` -> `in_progress` |
| 17 | Members | Complete work, notify COS |
| 18 | COS | Approve PR creation |
| 19 | Members | Create PRs |

### Phase 5: Review

| Step | Actor | Action |
|------|-------|--------|
| 20 | COS | Request review from integrator-skilled member |
| 21 | Member | Review PR, merge or reject |
| 22 | COS | Handle failures: reassign, move back to `in_progress` |

### Phase 6: Completion

| Step | Actor | Action |
|------|-------|--------|
| 23 | COS | Move task to `review` then `completed` |
| 24 | COS | For big tasks: escalate review to manager before completing |
| 25 | COS | Report completion to manager |
| 26 | COS | Assign next task to available member |

## Governance Touchpoints

| Event | Requires GovernanceRequest |
|-------|---------------------------|
| Team creation | No (manager action) |
| COS assignment | No (manager action) |
| Member roster approval | Yes |
| Agent replacement | Yes |
| Design approval | Yes (user via manager) |
| Big task human review | Yes (user via manager) |

## Task Statuses

| # | Status | Code | Description |
|---|--------|------|-------------|
| 1 | Backlog | `backlog` | Entry point, not yet prioritized |
| 2 | Pending | `pending` | Prioritized, ready to start |
| 3 | In Progress | `in_progress` | Active work |
| 4 | Review | `review` | Under review (AI or human) |
| 5 | Completed | `completed` | Done |

## Task Routing

- **Small**: `in_progress` -> `review` -> `completed`
- **Big**: `in_progress` -> `review` (escalate to manager) -> `completed`

## Communication

All inter-agent communication via AI Maestro messaging API (`POST /api/messages`).
GitHub used for: repos, issues, PRs, project boards.
