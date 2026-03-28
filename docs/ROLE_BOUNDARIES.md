# AI Maestro Role Boundaries

## 4-Title System

| Title | Singleton | Scope | Primary Function |
|-------|-----------|-------|------------------|
| `MANAGER` | Yes (per host) | Organization-wide | User interface, approval authority |
| `CHIEF-OF-STAFF` | One per team | Team-scoped | Agent coordination within team |
| `ORCHESTRATOR` | One per team | Team-scoped | Primary kanban manager, task distribution |
| `MEMBER` | Many per team | Task-scoped | Execution; skills determine specialization |

## Title Hierarchy

```
User <-> MANAGER <-> CHIEF-OF-STAFF <-> ORCHESTRATOR <-> MEMBER(s)
                                    \-> MEMBER(s)
ORCHESTRATOR can also message MANAGER directly (no COS relay needed)
```

## Permission Matrix

| Action | MANAGER | CHIEF-OF-STAFF | ORCHESTRATOR | MEMBER |
|--------|---------|----------------|--------------|--------|
| Talk to user | YES | NO | NO | NO |
| Create teams | YES | NO | NO | NO |
| Assign COS to team | YES | NO | NO | NO |
| Approve GovernanceRequests | YES | NO | NO | NO |
| Coordinate team members | NO | YES | YES | NO |
| Submit GovernanceRequests | NO | YES | NO | NO |
| Assign tasks to members | NO | NO | YES | NO |
| Manage kanban (primary) | NO | NO | YES | NO |
| Manage kanban (secondary) | YES | YES | — | NO |
| Request agent replacement | NO | YES | NO | NO |
| Message MANAGER directly | — | YES | YES | NO |
| Execute tasks | NO | NO | NO | YES |
| Create PRs | NO | NO | NO | YES |
| Report progress | NO | NO | YES (to COS/MANAGER) | YES (to ORCHESTRATOR) |

## Governance Flow

```
MEMBER needs X -> ORCHESTRATOR escalates -> COS submits GovernanceRequest -> MANAGER approves/rejects
```

All significant operations require GovernanceRequest approval from MANAGER.

## Teams

**All teams are closed.** There are no open teams. Each agent belongs to at most ONE team at a time.

| Property | Value |
|----------|-------|
| COS Required | Yes (one per team) |
| Description | Formal coordination via assigned COS |

## Key Constraints

- MANAGER NEVER executes technical work
- COS NEVER communicates with user directly
- MEMBERs NEVER bypass COS to reach MANAGER (except ORCHESTRATOR, which can message MANAGER directly)
- ORCHESTRATOR is the PRIMARY kanban manager; COS and MANAGER are secondary
- Skills on a MEMBER determine its specialization (architect, implementer, tester, etc.)
- One COS per team; MANAGER can reassign COS between teams
- Each agent belongs to at most ONE team at a time
