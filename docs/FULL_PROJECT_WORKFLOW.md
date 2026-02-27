# Team-Based Project Workflow

## Workflow Phases

### Phase 1: Team Creation

| Step | Actor | Action | API |
|------|-------|--------|-----|
| 1 | Manager | Create GitHub repo + team | `POST /api/teams` |
| 2 | Manager | Assign COS to team | `POST /api/teams/{id}/cos` |
| 3 | COS | Propose member roster | GovernanceRequest to manager |
| 4 | Manager | Approve roster | `POST /api/governance/approve` |
| 5 | COS | Add members to team | `POST /api/teams/{id}/members` |

### Phase 2: Design

| Step | Actor | Action |
|------|-------|--------|
| 6 | Manager | Send requirements to COS |
| 7 | COS | Assign design task to architect-skilled member |
| 8 | Member | Create design document |
| 9 | COS | Forward design to manager |
| 10 | Manager | Get user approval; send approved design to COS |

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
| 16 | COS | Move tasks: `todo` -> `in-progress` |
| 17 | Members | Complete work, notify COS |
| 18 | COS | Approve PR creation |
| 19 | Members | Create PRs |

### Phase 5: Review

| Step | Actor | Action |
|------|-------|--------|
| 20 | COS | Request review from integrator-skilled member |
| 21 | Member | Review PR, merge or reject |
| 22 | COS | Handle failures: reassign, move back to `in-progress` |

### Phase 6: Completion

| Step | Actor | Action |
|------|-------|--------|
| 23 | COS | Move task through: `ai-review` -> `merge-release` -> `done` |
| 24 | COS | For big tasks: route through `human-review` (via manager) |
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

## Kanban Columns

| # | Column | Code | Route |
|---|--------|------|-------|
| 1 | Backlog | `backlog` | Entry point |
| 2 | Todo | `todo` | Prioritized, ready |
| 3 | In Progress | `in-progress` | Active work |
| 4 | AI Review | `ai-review` | Integrator reviews |
| 5 | Human Review | `human-review` | Big tasks only |
| 6 | Merge/Release | `merge-release` | Approved |
| 7 | Done | `done` | Complete |
| 8 | Blocked | `blocked` | Any stage |

## Task Routing

- **Small**: `in-progress` -> `ai-review` -> `merge-release` -> `done`
- **Big**: `in-progress` -> `ai-review` -> `human-review` -> `merge-release` -> `done`

## Communication

All inter-agent communication via AI Maestro messaging API (`POST /api/messages`).
GitHub used for: repos, issues, PRs, project boards.
