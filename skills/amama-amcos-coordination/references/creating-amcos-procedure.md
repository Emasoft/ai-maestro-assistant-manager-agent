# Team Creation and Agent Registration Procedure

## Contents

- [Overview](#overview)
- [Key Principles](#key-principles)
- [Agent Registration](#agent-registration)
- [Team Creation](#team-creation)
- [COS Assignment](#cos-assignment)
- [Step-by-Step Procedure](#step-by-step-procedure)
- [Success Criteria](#success-criteria)
- [Troubleshooting](#troubleshooting)
- [Related Documents](#related-documents)

## Overview

This document describes the step-by-step procedure for registering agents and coordinating team setup with the user. ONLY the USER can create teams and assign COS roles. AMAMA recommends and requests these actions from the user.

## Key Principles

1. **Agents must exist before assignment** - An agent must be registered in the AI Maestro agent registry before it can be added to a team or assigned the COS role
2. **Teams organize agents** - Teams group agents and define coordination boundaries
3. **One COS per closed team** - Each closed team can have exactly one COS-assigned agent
4. **Team registry is persistent** - Teams are stored in `~/.aimaestro/teams/registry.json`
5. **USER is the authority** - Only the USER can create teams and assign COS roles. AMAMA recommends and requests these actions from the user.

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

### Team Creation (USER-ONLY)

**AMAMA cannot create teams.** Request the user to create the team via the AI Maestro dashboard. Provide the user with the recommended team name, description, type, and member agents so they can create it.

### Team Required Parameters

| Parameter | Purpose | Example Value |
|-----------|---------|---------------|
| `name` | Team name (unique) | `svgbbox-development` |
| `description` | Team purpose | `"SVG bounding box library development team"` |
| `type` | Access model | `open` or `closed` |
| `agentIds` | Initial member agents | `["coordinator-alpha", "dev-agent-1"]` |

### Team Types

| Type | Description | COS Allowed |
|------|-------------|-------------|
| `open` | Any registered agent can join | No |
| `closed` | Invite-only, managed membership | Yes (one COS) |

**Only closed teams can have a COS-assigned agent.** Open teams use ad-hoc coordination without a designated coordinator.

### Verify Team Creation

After the user creates the team, verify it exists:

```
GET $AIMAESTRO_API/api/teams
```


---

## COS Assignment (USER-ONLY)

**AMAMA cannot assign COS roles.** After the user creates the team, recommend a COS candidate and request the user to assign COS via the AI Maestro dashboard.

See [creating-amcos-instance.md](creating-amcos-instance.md) for COS role details including cross-host scenarios.

---

## Step-by-Step Procedure

### Step 1: Register Agent

If the target agent is not already in the registry, register it using `aimaestro-agent.sh` or the `ai-maestro-agents-management` skill.

**Verify**: `GET /api/agents` lists the agent.


### Step 2: Request User to Create Team

**AMAMA cannot create teams.** Request the user to create the team via the dashboard with the recommended configuration:

- **Recommended name**: `project-alpha-team`
- **Recommended description**: "Development team for project alpha"
- **Recommended type**: `closed`
- **Recommended members**: `coordinator-alpha`

**Verify**: After the user creates the team, confirm via `GET /api/teams`. Note the returned `teamId`.


### Step 3: Request User to Assign COS Role

**AMAMA cannot assign COS roles.** Recommend a COS candidate and request the user to assign COS via the dashboard.

- **Recommended COS**: `coordinator-alpha`
- **Team**: The team created in Step 2

**Verify**: After the user assigns COS, confirm via `GET /api/teams/{teamId}` that `chiefOfStaff` is set to the agent.

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
- [ ] User created team via dashboard (team ID available via `GET /api/teams`)
- [ ] Team stored in `~/.aimaestro/teams/registry.json`
- [ ] User assigned COS via dashboard
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
3. If team has existing COS, request user to unassign the current COS via dashboard first
4. Verify team type is `closed` (open teams cannot have COS)
5. Request user to retry COS assignment via dashboard

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
