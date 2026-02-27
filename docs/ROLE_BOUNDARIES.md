# AI Maestro Role Boundaries

## 3-Role System

| Role | Singleton | Scope | Primary Function |
|------|-----------|-------|------------------|
| `manager` | Yes (per host) | Organization-wide | User interface, approval authority |
| `chief-of-staff` | One per closed team | Team-scoped | Agent coordination within team |
| `member` | Many per team | Task-scoped | Execution; skills determine specialization |

## Role Hierarchy

```
User <-> manager <-> chief-of-staff <-> member(s)
```

## Permission Matrix

| Action | manager | chief-of-staff | member |
|--------|---------|----------------|--------|
| Talk to user | YES | NO | NO |
| Create teams | YES | NO | NO |
| Assign COS to team | YES | NO | NO |
| Approve GovernanceRequests | YES | NO | NO |
| Coordinate team members | NO | YES | NO |
| Submit GovernanceRequests | NO | YES | NO |
| Assign tasks to members | NO | YES | NO |
| Manage kanban | NO | YES | NO |
| Request agent replacement | NO | YES | NO |
| Execute tasks | NO | NO | YES |
| Create PRs | NO | NO | YES |
| Report progress to COS | NO | NO | YES |

## Governance Flow

```
member needs X -> COS submits GovernanceRequest -> manager approves/rejects
```

All significant operations require GovernanceRequest approval from manager.

## Team Types

| Type | COS Required | Description |
|------|-------------|-------------|
| `open` | No | Loose coordination, no COS |
| `closed` | Yes | Formal coordination via assigned COS |

## Key Constraints

- Manager NEVER executes technical work
- COS NEVER communicates with user directly
- Members NEVER bypass COS to reach manager
- Skills on a member determine its specialization (architect, implementer, tester, etc.)
- One COS per closed team; manager can reassign COS between teams
