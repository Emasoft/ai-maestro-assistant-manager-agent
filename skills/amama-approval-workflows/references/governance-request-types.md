# GovernanceRequest Types Reference

This document details all GovernanceRequest types, their triggers, payloads, and presentation templates.

## Contents

- [1. add-to-team](#1-add-to-team)
- [2. remove-from-team](#2-remove-from-team)
- [3. assign-cos (MANAGER, R29)](#3-assign-cos-manager-r29)
- [4. remove-cos (MANAGER, R29)](#4-remove-cos-manager-r29)
- [5. transfer-agent](#5-transfer-agent)
- [6. create-agent](#6-create-agent)
- [7. delete-agent](#7-delete-agent)
- [8. configure-agent](#8-configure-agent)

## 1. add-to-team

**Trigger**: An agent needs to be added to a team.

**Request payload**:
```json
{
  "type": "add-to-team",
  "agentId": "<agent-uuid>",
  "teamId": "<team-uuid>",
  "role": "<role-in-team>",
  "requestedBy": "<requesting-agent-id>",
  "reason": "<justification>"
}
```

**Present to MANAGER**:
```
## Governance Request: Add Agent to Team

**Request ID**: {id}
**Type**: add-to-team
**Agent**: {agentId} ({agent_name})
**Team**: {teamId} ({team_name})
**Role**: {role}
**Requested By**: {requestedBy}
**Reason**: {reason}

Approve adding this agent to the team?
- [Approve] - Add agent to team
- [Reject] - Deny request
```

## 2. remove-from-team

**Trigger**: An agent needs to be removed from a team.

**Request payload**:
```json
{
  "type": "remove-from-team",
  "agentId": "<agent-uuid>",
  "teamId": "<team-uuid>",
  "requestedBy": "<requesting-agent-id>",
  "reason": "<justification>"
}
```

## 3. assign-cos (MANAGER, R29)

**Trigger**: A team needs its CHIEF-OF-STAFF.

**MANAGER OPERATION (R29)**: The COS is created by the MANAGER as part of team
creation — `aimaestro-teams.sh create` auto-provisions it — with **no user
approval and no dashboard step**. Re-assigning an existing team's COS to a
different agent uses the teams CLI; AMAMA performs it AID-authorized (R28),
never via a sudo password (R32). A team without its COS + 5 base members is
FROZEN until complete (R31). This GovernanceRequest type therefore arises only
when a peer/cross-host flow routes a COS change for dual-manager approval — the
local MANAGER decides it on its AID basis.

**Request payload**:
```json
{
  "type": "assign-cos",
  "agentId": "<agent-uuid>",
  "teamId": "<team-uuid>",
  "requestedBy": "<requesting-agent-id>",
  "reason": "<justification>"
}
```

## 4. remove-cos (MANAGER, R29)

**Trigger**: A team's COS assignment needs to be revoked.

**MANAGER OPERATION (R29)**: The MANAGER manages the COS as part of team
lifecycle — AID-authorized (R28), no user approval, no governance password
(R32). Removing the COS without replacing it leaves the team FROZEN (R31), so
pair it with re-assignment. As with assign-cos, a GovernanceRequest of this type
appears only in a cross-host flow needing dual-manager approval.

**Request payload**:
```json
{
  "type": "remove-cos",
  "agentId": "<agent-uuid>",
  "teamId": "<team-uuid>",
  "requestedBy": "<requesting-agent-id>",
  "reason": "<justification>"
}
```

## 5. transfer-agent

**Trigger**: An agent needs to be moved from one team to another.

**Request payload**:
```json
{
  "type": "transfer-agent",
  "agentId": "<agent-uuid>",
  "fromTeamId": "<source-team-uuid>",
  "toTeamId": "<destination-team-uuid>",
  "requestedBy": "<requesting-agent-id>",
  "note": "<transfer-justification>"
}
```

**Present to MANAGER**:
```
## Governance Request: Transfer Agent

**Request ID**: {id}
**Type**: transfer-agent
**Agent**: {agentId} ({agent_name})
**From Team**: {fromTeamId} ({from_team_name})
**To Team**: {toTeamId} ({to_team_name})
**Requested By**: {requestedBy}
**Note**: {note}

Approve transferring this agent between teams?
- [Approve] - Execute transfer
- [Reject] - Deny transfer
```

**Who can approve**: MANAGER (AID-authorized, R28), or the COS of the destination team (via its portfolio mandate token, R28/R30).

## 6. create-agent

**Trigger**: A new agent needs to be provisioned.

**Authority (R29/R30)**: The MANAGER creates agents AID-authorized, no user
approval — the 5 base members at team creation, plus AUTONOMOUS / MAINTAINER. A
COS may create agents only under a MANAGER mandate (R30), and any extra agent it
adds must be **MEMBER-titled on the member-agent role plugin** — neither the
MANAGER nor a COS may create a non-MEMBER team agent. This GovernanceRequest type
covers cross-host / dual-manager provisioning flows.

**Request payload**:
```json
{
  "type": "create-agent",
  "agentName": "<agent-name>",
  "agentType": "<agent-type>",
  "teamId": "<target-team-uuid>",
  "requestedBy": "<requesting-agent-id>",
  "reason": "<justification>",
  "config": {}
}
```

## 7. delete-agent

**Trigger**: An agent needs to be decommissioned.

**Authority (R29/R31)**: The MANAGER deletes agents AID-authorized, no user
approval. Deleting a base member without replacing it FREEZES the team (R31) —
restore the 5-member base before resuming. This GovernanceRequest type covers
cross-host / dual-manager decommission flows.

**Request payload**:
```json
{
  "type": "delete-agent",
  "agentId": "<agent-uuid>",
  "requestedBy": "<requesting-agent-id>",
  "reason": "<justification>"
}
```

## 8. configure-agent

**Trigger**: An agent's configuration needs to be modified.

**Request payload**:
```json
{
  "type": "configure-agent",
  "agentId": "<agent-uuid>",
  "changes": {},
  "requestedBy": "<requesting-agent-id>",
  "reason": "<justification>"
}
```
