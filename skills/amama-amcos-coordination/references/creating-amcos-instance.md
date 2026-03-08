# Assigning the COS Role (AMAMA Exclusive Responsibility)

## Table of Contents
- [1. Why AMAMA Assigns the COS Role](#1-why-amama-assigns-the-cos-role)
  - [Key Difference from v1 (Spawning AMCOS)](#key-difference-from-v1-spawning-amcos)
- [2. How to Assign the COS Role](#2-how-to-assign-the-cos-role)
  - [Prerequisites](#prerequisites)
  - [Assignment API Call](#assignment-api-call)
  - [Unassigning COS](#unassigning-cos)
  - [Naming Convention for COS-Assigned Agents](#naming-convention-for-cos-assigned-agents)
- [3. When to Assign the COS Role](#3-when-to-assign-the-cos-role)
- [4. Post-Assignment Steps](#4-post-assignment-steps)
  - [Initialization Message](#initialization-message)
  - [Verification Checklist](#verification-checklist)
- [5. Cross-Host COS Assignment](#5-cross-host-cos-assignment)
  - [When Cross-Host Assignment Is Needed](#when-cross-host-assignment-is-needed)
  - [GovernanceRequest for COS Assignment](#governancerequest-for-cos-assignment)
  - [GovernanceRequest Lifecycle](#governancerequest-lifecycle)
  - [Cross-Host Limitations](#cross-host-limitations)

---

## 1. Why AMAMA Assigns the COS Role

AMAMA is the ONLY agent authorized to assign the COS (Chief of Staff) role. This ensures:

1. **Single point of authority** - Only the user's representative can designate an operational coordinator
2. **Role constraint enforcement** - The COS role is assigned with proper governance via the Team API
3. **Audit trail** - All COS assignments are traceable to AMAMA approval
4. **No rogue coordinators** - An agent cannot self-assign the COS role

### Key Difference from v1 (Spawning AMCOS)

In v1, AMAMA spawned a new dedicated AMCOS instance. In v2:
- The target agent must **already exist** in the AI Maestro agent registry
- AMAMA **assigns the COS role** to that agent within a specific team
- The agent retains its original identity but gains COS responsibilities
- No new process/session is spawned; the existing agent is augmented

---

## 2. How to Assign the COS Role

### Prerequisites

1. The target agent must be registered in AI Maestro (`GET /api/agents` must list it)
2. A team must exist (`GET /api/teams` must list it) with type `closed`
3. The team must not already have a COS assigned (one COS per closed team)
4. The target agent should be a member of the team

### Assignment API Call

Assign the COS role via the Team API:

```bash
TEAM_ID="<team-id>"
AGENT_ID="<agent-id>"

curl -X PATCH "$AIMAESTRO_API/api/teams/$TEAM_ID/chief-of-staff" \
  -H "Content-Type: application/json" \
  -d "{
    \"agentId\": \"$AGENT_ID\"
  }"
```

**Expected Response:**

```json
{
  "teamId": "<team-id>",
  "chiefOfStaff": "<agent-id>",
  "assignedBy": "amama-session-name",
  "assignedAt": "2026-02-27T10:00:00Z"
}
```

**Verify**: confirm the team's `chiefOfStaff` field is set by checking `GET /api/teams/$TEAM_ID`.

### Unassigning COS

To unassign a COS (before reassigning to a different agent):

```bash
curl -X PATCH "$AIMAESTRO_API/api/teams/$TEAM_ID/chief-of-staff" \
  -H "Content-Type: application/json" \
  -d '{ "agentId": null }'
```

### Naming Convention for COS-Assigned Agents

The agent keeps its original session name. There is no special naming requirement for COS-assigned agents. The COS role is a property of the team membership, not the agent identity.

However, for clarity in messaging and logs, AMAMA may refer to the agent as:
- `<agent-session-name> (COS for <team-name>)`

---

## 3. When to Assign the COS Role

| Scenario | Action |
|----------|--------|
| **New team created** | Assign COS when a closed team needs an operational coordinator |
| **Previous COS unresponsive** | Unassign current COS, assign role to a different agent |
| **Team restructuring** | Reassign COS as team composition changes |
| **Never duplicate** | Only ONE COS per closed team at any time |
| **Open teams** | Open teams do not have a COS; coordination is ad-hoc |

---

## 4. Post-Assignment Steps

After assigning the COS role:

1. **Verify assignment** - Check `GET /api/teams/$TEAM_ID` to confirm `chiefOfStaff` is set
2. **Send initialization message** - Notify the agent of its new COS role using the `agent-messaging` skill
3. **Confirm role acceptance** - Wait for the agent to acknowledge its COS responsibilities
4. **Log the assignment** - Record in the team audit log

### Initialization Message

Send a COS role notification to the agent using the `agent-messaging` skill:
- **Recipient**: The agent's session name
- **Subject**: "COS Role Assignment"
- **Content**:
  - `type`: `cos-role-assignment`
  - `team_id`: The team ID
  - `team_name`: The team name
  - `expected_role`: `chief-of-staff`
  - `responsibilities`: "Coordinate agents within this team. Manage task delegation and approval workflows."
- **Priority**: `high`

**Verify**: The agent should respond confirming it has accepted the COS role and loaded its role constraints.

### Verification Checklist

- [ ] Agent exists in AI Maestro registry
- [ ] Team exists and is of type `closed`
- [ ] Team does not already have a COS (or previous COS was unassigned)
- [ ] `PATCH /api/teams/$TEAM_ID/chief-of-staff` succeeded
- [ ] `GET /api/teams/$TEAM_ID` confirms `chiefOfStaff` set to correct agent
- [ ] Initialization message sent to agent
- [ ] Agent acknowledged COS role

---

## 5. Cross-Host COS Assignment

When the target agent is on a different host (remote AI Maestro instance), the assignment requires a GovernanceRequest.

### When Cross-Host Assignment Is Needed

- The agent is registered on a different AI Maestro instance
- The team spans multiple hosts
- Network boundaries separate AMAMA from the target agent

### GovernanceRequest for COS Assignment

Submit a GovernanceRequest of type `assign-cos`:

```bash
curl -X POST "$AIMAESTRO_API/api/v1/governance/requests" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "assign-cos",
    "requestedBy": "amama-session-name",
    "targetAgent": "<remote-agent-id>",
    "targetTeam": "<team-id>",
    "remoteHost": "<remote-aimaestro-url>",
    "justification": "Team requires operational coordinator on remote host"
  }'
```

**Expected Response:**

```json
{
  "requestId": "gov-req-<uuid>",
  "status": "pending",
  "type": "assign-cos",
  "createdAt": "2026-02-27T10:00:00Z"
}
```

### GovernanceRequest Lifecycle

1. **Pending** - Request submitted, awaiting governance approval
2. **Approved** - Governance policy allows the assignment; AI Maestro executes it on the remote host
3. **Rejected** - Governance policy denies the assignment; AMAMA is notified with reason
4. **Executed** - Assignment completed on remote host; AMAMA receives confirmation

**Verify**: Poll `GET /api/v1/governance/requests/$REQUEST_ID` until status is `approved` and then `executed`.

### Cross-Host Limitations

- Messaging latency may be higher across hosts
- ACK timeouts should be increased for cross-host COS agents
- Health check intervals should account for network latency
