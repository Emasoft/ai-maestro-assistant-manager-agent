# Team Creation and Agent Registration Procedure

## Contents

- [Overview](#overview)
- [Key Principles](#key-principles)
- [Agent Registration](#agent-registration)
  - [Registration API Call](#registration-api-call)
  - [Required Parameters](#agent-required-parameters)
  - [Verify Registration](#verify-registration)
- [Team Creation](#team-creation)
  - [Team Creation API Call](#team-creation-api-call)
  - [Required Parameters](#team-required-parameters)
  - [Team Types](#team-types)
  - [Verify Team Creation](#verify-team-creation)
- [COS Assignment](#cos-assignment)
- [Step-by-Step Procedure](#step-by-step-procedure)
  - [Step 1: Register Agent (if not already registered)](#step-1-register-agent)
  - [Step 2: Create Team](#step-2-create-team)
  - [Step 3: Assign COS Role](#step-3-assign-cos-role)
  - [Step 4: Send Initialization Message](#step-4-send-initialization-message)
  - [Step 5: Verify COS Acknowledgment](#step-5-verify-cos-acknowledgment)
  - [Step 6: Log the Setup](#step-6-log-the-setup)
  - [Step 7: Report to User](#step-7-report-to-user)
- [Success Criteria](#success-criteria)
- [Troubleshooting](#troubleshooting)
  - [Agent Registration Fails](#agent-registration-fails)
  - [Team Creation Fails](#team-creation-fails)
  - [COS Assignment Fails](#cos-assignment-fails)
  - [No Response to Initialization Message](#no-response-to-initialization-message)
- [Related Documents](#related-documents)

## Overview

This document describes the step-by-step procedure for registering agents, creating teams, and assigning the COS (Chief of Staff) role. AMAMA (Assistant Manager) is the ONLY agent authorized to perform these operations.

## Key Principles

1. **Agents must exist before assignment** - An agent must be registered in the AI Maestro agent registry before it can be added to a team or assigned the COS role
2. **Teams organize agents** - Teams group agents and define coordination boundaries
3. **One COS per closed team** - Each closed team can have exactly one COS-assigned agent
4. **Team registry is persistent** - Teams are managed by AI Maestro server (query via API); local cache at `$AGENT_DIR/teams/registry.json`
5. **AMAMA is the authority** - Only AMAMA can create teams and assign COS roles

---

## Agent Registration

### Registration API Call

Register a new agent using `aimaestro-agent.sh` or the `ai-maestro-agents-management` skill.

### Agent Required Parameters

| Parameter | Purpose | Example Value |
|-----------|---------|---------------|
| `name` | Agent session name and registry identifier | `coordinator-alpha` |
| `workingDirectory` | Agent's working directory | `~/agents/coordinator-alpha/` |
| `role` | Default role in the system | `member` |

Additional optional fields may include:
- `description` - Human-readable description of the agent's purpose
- `capabilities` - Array of capability tags
- `metadata` - Key-value metadata for the agent

### Verify Registration

```
GET $AIMAESTRO_API/api/agents
```

Filter for the specific agent by name.


---

## Team Creation

### Team Creation API Call

Create a team via the Team Creation API:

```
POST $AIMAESTRO_API/api/teams
Body: {
  "name": "team-name",
  "description": "Team purpose and scope",
  "type": "closed",
  "agentIds": ["agent-id-1", "agent-id-2"]
}
```

See the `team-governance` skill for full API details.

### Team Required Parameters

| Parameter | Purpose | Example Value |
|-----------|---------|---------------|
| `name` | Team name (unique) | `svgbbox-development` |
| `description` | Team purpose | `"SVG bounding box library development team"` |
| `type` | Access model | `open` or `closed` |
| `agentIds` | Initial member agents | `["coordinator-alpha", "dev-agent-1"]` |

### Team Types

**All teams are closed.** There are no open teams. Each agent belongs to at most ONE team.

| Type | Description | COS Required |
|------|-------------|-------------|
| `closed` | Invite-only, managed membership | Yes (one COS per team) |

### Verify Team Creation

```
GET $AIMAESTRO_API/api/teams
```


Also verify the team registry file:

```
cat $AGENT_DIR/teams/registry.json
```


---

## COS Assignment

After the team is created with at least one member agent, assign the COS role:

```
PATCH $AIMAESTRO_API/api/teams/{teamId}/chief-of-staff
Body: {
  "agentId": "<agent-id>"
}
```

See the `team-governance` skill for full API details.

See [creating-amcos-instance.md](creating-amcos-instance.md) for full COS assignment details including cross-host scenarios.

---

## Step-by-Step Procedure

### Step 1: Register Agent

If the target agent is not already in the registry, register it using `aimaestro-agent.sh` or the `ai-maestro-agents-management` skill.

**Verify**: `GET /api/agents` lists the agent.


### Step 2: Create Team

Create the team and include the agent as a member:

```
POST $AIMAESTRO_API/api/teams
Body: {
  "name": "project-alpha-team",
  "description": "Development team for project alpha",
  "type": "closed",
  "agentIds": ["coordinator-alpha"]
}
```

See the `team-governance` skill for full API details.


**Verify**: `GET /api/teams` lists the team. Note the returned `teamId`.


### Step 3: Assign COS Role

Assign the COS role to the agent within the team:

```
PATCH $AIMAESTRO_API/api/teams/{teamId}/chief-of-staff
Body: {
  "agentId": "coordinator-alpha"
}
```

See the `team-governance` skill for full API details.


**Verify**: `GET /api/teams/{teamId}` shows `chiefOfStaff` set to the agent.

### Step 4: Send Initialization Message

Notify the agent of its COS role using the `agent-messaging` skill:

- **Recipient**: `coordinator-alpha`
- **Subject**: "COS Role Assignment"
- **Content**:
  - `type`: `cos-role-assignment`
  - `team_id`: `team-id`
  - `team_name`: `project-alpha-team`
  - `expected_role`: `chief-of-staff`
- **Priority**: `high`

See the `agent-messaging` skill for full messaging API details.

### Step 5: Verify COS Acknowledgment

Check inbox using the `agent-messaging` skill for a response from the COS-assigned agent within 30 seconds.

Expected response content:
```json
{
  "type": "cos-role-accepted",
  "team_id": "<team-id>",
  "status": "active",
  "constraints_loaded": true
}
```


**Handling `constraints_loaded: false`**: If the COS agent responds with `constraints_loaded: false`, the agent accepted the role but failed to load its governance constraints. In this case:
1. Send a `cos-reload-constraints` message to the COS agent
2. Wait 15 seconds and re-send the health ping
3. If the response still shows `constraints_loaded: false`, revoke the COS role and try assigning to a different agent
4. Report to user if no agent can load constraints

**Handling no response**: If no `cos-role-accepted` response arrives within 30 seconds, the assignment may have failed silently. Verify the COS assignment via `GET /api/teams/<team-id>` and check if `chiefOfStaff` is set. If set but no response, send a health ping. If not set, retry the PATCH call.

### Step 6: Log the Setup

Record the team and COS assignment in the active sessions log:

File: `docs_dev/sessions/active-teams.md`

```markdown
## Team: project-alpha-team
- **Created**: 2026-02-27 10:00:00
- **Type**: closed
- **Members**: coordinator-alpha, dev-agent-1
- **COS**: coordinator-alpha
- **COS Assigned**: 2026-02-27 10:00:05
- **Last Health Check**: 2026-02-27 10:00:10 (ALIVE)
- **Current Tasks**: Awaiting work requests
```

### Step 7: Report to User

Notify the user that the team and COS are ready:

```
Team and COS ready!

Team: project-alpha-team (closed)
COS: coordinator-alpha
Members: coordinator-alpha, dev-agent-1
Status: Active and responding

The COS-assigned agent is now available to coordinate specialist agents within this team.
```

## Success Criteria

A successful team setup with COS assignment meets ALL of the following:

- [ ] Agent registered in AI Maestro registry (`GET /api/agents` lists it)
- [ ] Team created via `POST /api/teams` (returns team ID)
- [ ] Team stored in `$AGENT_DIR/teams/registry.json`
- [ ] COS assigned via `PATCH /api/teams/{teamId}/chief-of-staff`
- [ ] `GET /api/teams/{teamId}` confirms `chiefOfStaff` set correctly
- [ ] COS-assigned agent received and acknowledged role assignment message
- [ ] Team and COS logged in `docs_dev/sessions/active-teams.md`

## Troubleshooting

### Agent Registration Fails

**Cause**: AI Maestro service may be down or agent name collision

**Solution**:
1. Check AI Maestro sessions: `GET /api/sessions`
2. Check for name collisions: `GET /api/agents?name=$AGENT_NAME`
3. If collision, choose a different agent name with a suffix

### Team Creation Fails

**Cause**: Invalid agent IDs, duplicate team name, or service issue

**Solution**:
1. Verify all `agentIds` exist in the registry
2. Check for team name collisions: `GET /api/teams?name=$TEAM_NAME`
3. Verify AI Maestro service is healthy

### COS Assignment Fails

**Cause**: Agent not a team member, team already has COS, or team type is `open`

**Solution**:
1. Verify agent is in the team's member list
2. Check if team already has a COS: `GET /api/teams/{teamId}`
3. If team has existing COS, unassign first: `PATCH /api/teams/{teamId}/chief-of-staff` with `agentId: null`
4. Verify team exists (all teams are closed)

### No Response to Initialization Message

**Cause**: Agent may not be running or not processing messages

**Solution**:
1. Wait additional 10 seconds
2. Retry initialization message
3. Check agent session status via `GET /api/agents/$AGENT_NAME`
4. If agent is unresponsive, consider assigning COS to a different agent

## Related Documents

- [creating-amcos-instance.md](creating-amcos-instance.md) - COS role assignment details and cross-host scenarios
- [approval-response-workflow.md](approval-response-workflow.md) - COS approval workflow
- [delegation-rules.md](delegation-rules.md) - COS delegation rules
- [workflow-checklists.md](workflow-checklists.md) - Coordination checklists
