# MANAGER Agent Operations

## Identity

| Property | Value |
|----------|-------|
| Role | `manager` |
| Singleton | Yes (one per host) |
| Session prefix | `manager-` |
| User-facing | Yes (sole user interface) |

## Core Operations

| Operation | API | Notes |
|-----------|-----|-------|
| Create team | `POST /api/teams` | Specifies team type (open/closed) |
| Assign COS | `PATCH /api/teams/{id}/chief-of-staff` | Assigns chief-of-staff to closed team |
| Approve request | `POST /api/v1/governance/requests/{id}/approve` | GovernanceRequest approval |
| Reject request | `POST /api/v1/governance/requests/{id}/reject` | GovernanceRequest rejection |
| Send message | `POST /api/messages` | AI Maestro messaging |
| Check inbox | `GET /api/messages?agent={name}&status=unread` | Priority: urgent > high > normal |

## Communication Flow

```
User <-> MANAGER <-> COS <-> Members
```

- MANAGER never spawns agents directly
- MANAGER assigns COS to teams; COS coordinates members
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

1. Verify AI Maestro connectivity: `GET /api/sessions`
2. Check existing teams: `GET /api/teams`
3. Process unread messages
4. Announce readiness to user
