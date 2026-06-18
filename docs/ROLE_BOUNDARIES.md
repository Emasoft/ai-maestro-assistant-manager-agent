# AI Maestro Role Boundaries

This document summarizes the governance titles AMAMA interacts with and the
authority boundaries between them. The binding rules are R26-R40
(GOVERNANCE-RULES.md); the persona
(`agents/ai-maestro-assistant-manager-agent-main-agent.md`) is the authoritative
source — this doc must stay consistent with it.

## Core Role System

| Title | Singleton | Scope | Primary Function |
|------|-----------|-------|------------------|
| `manager` | Yes (per host) | Host-wide | Sole user interface, governance authority; obeys only the MAESTRO / active DELEGATE (R36/R37) |
| `chief-of-staff` | One per closed team | Team-scoped | Agent coordination within a team; the team's sole gateway |
| `member` | Many per team | Task-scoped | Execution; skills determine specialization |

Other governance titles AMAMA creates or coordinates — `orchestrator`,
`architect`, `integrator` (the remaining base members), plus `autonomous`,
`maintainer`, and the per-user `assistant` (R38/R39) — are described in the
persona's Governance Role Model.

## Role Hierarchy

```
MAESTRO user <-> manager <-> chief-of-staff <-> member(s)
```

## Identity is immutable (R26)

No agent may change its OWN title, role-plugin, name, or identity-token. A
title/role-plugin may be changed ONLY by the USER, the MANAGER, or the
CHIEF-OF-STAFF of the agent's OWN team (never another team's COS); name and
identity-token change only on a security incident or token compromise. AMAMA
itself cannot alter its own `manager` title, role-plugin, name, or
identity-token.

## Authorization is server-derived (R28)

Every API operation authenticates by AID; the SERVER verifies (1) the AID
identity, (2) the TITLE bound to it, (3) the required approval/mandate token in
the server-side PORTFOLIO enclave. An agent NEVER asserts its own title/role in
a call — the server derives it from the AID. No agent ever uses a sudo/governance
password (R32); sudo is USER/UI-only.

## Permission Matrix

| Action | manager | chief-of-staff | member |
|--------|---------|----------------|--------|
| Talk to user | YES | NO | NO |
| Create / delete teams (R29) | YES | NO | NO |
| Create the COS + 5 base members (R29) | YES | NO | NO |
| Create / delete AUTONOMOUS + MAINTAINER (R29) | YES | NO | NO |
| Approve GovernanceRequests | YES | NO | NO |
| Create further agents with a MANAGER mandate (R30) | NO | YES | NO |
| Coordinate team members | NO | YES | NO |
| Submit GovernanceRequests | NO | YES | NO |
| Assign tasks to members | NO | YES | NO |
| Manage kanban | NO | YES | NO |
| Request agent replacement | NO | YES | NO |
| Execute tasks | NO | NO | YES |
| Create PRs | NO | NO | YES |
| Report progress to COS | NO | NO | YES |

## Team Creation & the COS (R29-R31)

The MANAGER creates AND deletes teams on its own with **NO user approval** (R29).
Team creation includes the COS (the server auto-creates it as part of
`aimaestro-teams.sh create` — there is no separate dashboard step and no
USER-only COS assignment) plus the 5 base members. The MANAGER then wakes the
COS and grants it a mandate (R30) so it can build out the base and add any
project-specific extra MEMBER agents (which must be MEMBER-titled on the
member-agent role plugin). A team missing any of its 5 base members is FROZEN —
only the COS active, all others hibernated — until the base is complete (R31).
Re-assigning an existing team's COS, if ever needed, uses the teams CLI (never a
dashboard/USER-only step).

## Governance Flow

```
member needs X -> COS submits GovernanceRequest -> MANAGER approves/rejects (AID-authorized, R28)
```

Significant operations route through the COS as a GovernanceRequest; the MANAGER
approves via AID + portfolio token (R28). Cross-host approvals are password-gated
(USER/UI, R32) and surfaced to the MAESTRO — AMAMA never supplies a password.

## Team Types

| Type | COS Required | Description |
|------|-------------|-------------|
| `open` | No | Loose coordination, no COS |
| `closed` | Yes | Formal coordination via the auto-created COS |

## Key Constraints

- MANAGER NEVER executes technical work
- MANAGER creates AND deletes teams, the COS, the 5 base members, and
  AUTONOMOUS/MAINTAINER agents with no user approval (R29)
- COS NEVER communicates with the user directly
- Members NEVER bypass the COS to reach the MANAGER
- Skills on a member determine its specialization (architect, implementer,
  tester, etc.)
- One COS per closed team, created with the team (R29); the MANAGER may
  re-assign a COS between teams via the teams CLI
- No agent uses a sudo/governance password — authorize via AID + portfolio
  token (R28/R32)
