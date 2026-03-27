# GovernanceRequest Types Reference

This document details all GovernanceRequest types, their triggers, payloads, and presentation templates.

## Contents

- [1. add-to-team](#1-add-to-team)
- [2. remove-from-team](#2-remove-from-team)
- [3. assign-cos](#3-assign-cos)
- [4. remove-cos](#4-remove-cos)
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

## 3. assign-cos (USER-ONLY)

**Trigger**: A COS (Chief of Staff) role needs to be assigned to an agent for a team.

**USER-ONLY OPERATION**: Only the user can assign COS roles. AMAMA can receive and forward the user's decision but cannot approve or execute COS assignment. The user performs this action via the AI Maestro dashboard.

**Request payload** (for reference only -- executed by user, not by AMAMA):
```json
{
  "type": "assign-cos",
  "agentId": "<agent-uuid>",
  "teamId": "<team-uuid>",
  "requestedBy": "<requesting-agent-id>",
  "reason": "<justification>"
}
```

## 4. remove-cos (USER-ONLY)

**Trigger**: A COS role needs to be revoked from an agent.

**USER-ONLY OPERATION**: Only the user can remove COS roles. AMAMA can receive and forward the user's decision but cannot approve or execute COS removal. The user performs this action via the AI Maestro dashboard.

**Request payload** (for reference only -- executed by user, not by AMAMA):
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

**Who can approve**: MANAGER, or the COS of the destination team.

## 6. create-agent

**Trigger**: A new agent needs to be provisioned.

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
