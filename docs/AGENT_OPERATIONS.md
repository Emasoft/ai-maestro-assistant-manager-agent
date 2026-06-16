# MANAGER Agent Operations

## Identity

| Property | Value |
|----------|-------|
| Role | `manager` |
| Singleton | Yes (one per host) |
| Session prefix | `manager-` |
| User-facing | Yes (sole user interface) |

## Core Operations

| Operation | CLI | Notes |
|-----------|-----|-------|
| Create team | `aimaestro-teams.sh create --name N [--type T]` | Specifies team type (open/closed) |
| Assign COS | USER assigns COS via dashboard | COS assignment is USER-only; MANAGER only recommends candidates |
| Approve request | `aimaestro-governance.sh approve <id> --password P` | GovernanceRequest approval |
| Reject request | `aimaestro-governance.sh reject <id> --password P [--reason R]` | GovernanceRequest rejection |
| Send message | `amp-send …` | AI Maestro messaging |
| Check inbox | `amp-inbox` | Priority: urgent > high > normal |

## Communication Flow

```
User <-> MANAGER <-> COS <-> Members
```

- MANAGER never spawns agents directly
- USER assigns COS to teams via dashboard; MANAGER recommends COS candidates; COS coordinates members
- All governance approvals go through GovernanceRequest API

## Message Priority

| Priority | Use Case |
|----------|----------|
| `urgent` | User-blocking, critical bugs |
| `high` | Feature requests, important questions |
| `normal` | Status updates, routine coordination |

## Responsibilities

- Receive and translate user requests
- Create teams via AI Maestro API
- Assign COS to closed teams
- Approve/reject GovernanceRequests from COS
- Report progress to user in plain language
- Set priorities based on user needs

## MANAGER Does NOT

- Execute technical tasks
- Spawn agents directly
- Write code or run tests
- Manage kanban boards

## Task Status Reference

AI Maestro uses 5 task statuses:

| Status | Code | Label |
|--------|------|-------|
| Backlog | `backlog` | `status:backlog` |
| Pending | `pending` | `status:pending` |
| In Progress | `in_progress` | `status:in-progress` |
| Review | `review` | `status:review` |
| Completed | `completed` | `status:completed` |

## Agent Creation

- **Predefined roles**: Use the AI Maestro simple wizard (`aimaestro-agent.sh`)
- **Custom/specialized agents**: Route to Haephestos v2 for specialized agent type creation

## Session Lifecycle

1. Verify AI Maestro connectivity: `aimaestro-agent.sh list` (non-zero exit ⇒ server unreachable)
2. Check existing teams: `aimaestro-teams.sh list`
3. Process unread messages
4. Announce readiness to user
