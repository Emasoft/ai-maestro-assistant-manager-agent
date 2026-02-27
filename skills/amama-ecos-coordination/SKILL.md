---
name: amama-amcos-coordination
description: Use when coordinating with the Chief of Staff (COS) for approval requests and autonomous operation delegation. Trigger with COS coordination requests.
version: 2.0.0
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-main
user-invocable: false
triggers:
  - COS-assigned agent sends an approval request via AI Maestro
  - AMAMA needs to grant or revoke autonomous mode for a COS-assigned agent
  - COS-assigned agent reports completion of delegated operations
  - User requests to configure COS delegation rules
  - AMAMA needs to assign or unassign the COS role to an existing agent
  - AMAMA needs to create a new team and assign agents to it
---

# COS Coordination Skill

## Overview

This skill enables the Assistant Manager (AMAMA) to coordinate with COS-assigned agents (Chief of Staff role). A COS-assigned agent acts as the operational coordinator that can either request approval for operations or operate autonomously within granted boundaries.

**Key governance change (v2):** AMAMA no longer spawns new AMCOS instances. Instead, AMAMA assigns the COS role to an existing registered agent via the AI Maestro Team API. Each closed team can have one COS-assigned agent.

## Prerequisites

Before using this skill, ensure:
1. Target agent already exists in the AI Maestro agent registry (`GET /api/agents`)
2. AI Maestro messaging is available
3. A team exists (or will be created) to which the COS role applies
4. Approval workflow is understood

## Instructions

1. Identify coordination type needed
2. If assigning COS role: verify agent exists in registry, then assign via Team API
3. If creating a team: use the Team Creation API
4. Send appropriate message to the COS-assigned agent
5. Wait for acknowledgment
6. Process COS-assigned agent response

### Checklist

Copy this checklist and track your progress:

- [ ] Identify coordination type (assign-cos/create-team/register-agent/grant/revoke/respond)
- [ ] Verify target agent exists in registry (for COS assignment)
- [ ] Prepare AI Maestro API call or message payload
- [ ] Execute API call or send message
- [ ] Wait for acknowledgment
- [ ] Process and log response

## Output

| Operation | Output |
|-----------|--------|
| Assign COS role | Agent assigned as COS for the specified team |
| Create team | Team created in registry, agents assigned |
| Register agent | Agent registered in AI Maestro agent registry |
| Grant autonomy | Autonomy scope confirmed by COS-assigned agent |
| Revoke autonomy | Autonomy revoked, COS-assigned agent notified |

## Table of Contents

1. What is a COS-Assigned Agent and Its Relationship with AMAMA
2. Assigning the COS Role (AMAMA Exclusive Responsibility)
3. Creating Teams and Registering Agents
4. Approval Request Flow from COS-Assigned Agent to AMAMA
5. Responding to COS Approval Requests
6. Delegation Rules for Autonomous Operation
7. AI Maestro Message Formats for COS Communication
8. Completion Notifications from COS-Assigned Agent
9. Error Handling and Escalation

---

## 1. What is a COS-Assigned Agent and Its Relationship with AMAMA

### Definition

A COS-assigned agent is an existing registered agent that has been given the Chief of Staff role within a team. The COS role designates the agent as the operational coordinator for that team, managing day-to-day tasks. The COS sits between AMAMA and the specialized roles (Architect, Orchestrator, Integrator).

### Hierarchy

```
USER
  |
AMAMA (Assistant Manager) - User's direct interface
  |
COS-assigned agent (Chief of Staff role) - Operational coordinator for a team
  |
+-- EAA (Architect)
+-- EOA (Orchestrator)
+-- EIA (Integrator)
```

### Responsibilities Split

| Role | Responsibilities |
|------|------------------|
| AMAMA | User communication, final approvals, high-level decisions, COS assignment |
| COS-assigned agent | Task coordination, routine operations, delegation management within team |

### Key Difference from v1

In v1, AMAMA spawned dedicated AMCOS instances. In v2, AMAMA assigns the COS role to an already-registered agent. The agent retains its identity but gains additional COS responsibilities and constraints for the team it is assigned to.

---

## 2. Assigning the COS Role (AMAMA Exclusive Responsibility)

AMAMA is the ONLY agent authorized to assign the COS role, ensuring single point of authority and role constraint enforcement.

See [creating-ecos-instance.md](references/creating-ecos-instance.md):
- Why only AMAMA can assign the COS role -> Section 1
- How to assign the COS role to an existing agent -> Section 2
- When to assign the COS role -> Section 3
- What to do after assigning the COS role -> Section 4
- Cross-host COS assignment via GovernanceRequest -> Section 5

---

## 3. Creating Teams and Registering Agents

Before assigning a COS, a team must exist and the target agent must be registered.

### Agent Registration

Register a new agent in AI Maestro via the Agent Creation API:

```bash
curl -X POST "$AIMAESTRO_API/api/agents/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "agent-session-name",
    "workingDirectory": "~/agents/agent-session-name/",
    "role": "member"
  }'
```

**Verify**: confirm the agent appears in `GET /api/agents` with correct status.

### Team Creation

Create a team via the Team Creation API:

```bash
curl -X POST "$AIMAESTRO_API/api/teams" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "team-name",
    "description": "Team purpose description",
    "type": "closed",
    "agentIds": ["agent-id-1", "agent-id-2"]
  }'
```

| Parameter | Purpose | Values |
|-----------|---------|--------|
| `name` | Team identifier | Descriptive team name |
| `description` | Team purpose | Free text |
| `type` | Team access model | `open` (any agent can join) or `closed` (invite only) |
| `agentIds` | Initial team members | Array of registered agent IDs |

**Verify**: confirm the team appears in `GET /api/teams` and the team registry at `~/.aimaestro/teams/registry.json`.

Teams are stored in `~/.aimaestro/teams/registry.json`.

See [creating-ecos-procedure.md](references/creating-ecos-procedure.md) for the full step-by-step procedure.

---

## 4. Approval Request Flow from COS-Assigned Agent to AMAMA

### When COS-Assigned Agent Sends Approval Requests

A COS-assigned agent sends approval requests to AMAMA when:

1. **Critical Operations**: Actions that affect production, security, or user data
2. **Policy Exceptions**: Operations outside delegated autonomy boundaries
3. **Resource Allocation**: Major resource commitments (time, budget, infrastructure)
4. **Conflict Resolution**: When specialized roles disagree on approach
5. **User-Impacting Changes**: Any change that affects user experience

### Request Categories

| Category | Description | Default: Requires AMAMA Approval |
|----------|-------------|--------------------------------|
| `critical-operation` | Production deployments, database migrations | Always |
| `policy-exception` | Deviation from standard procedures | Always |
| `resource-allocation` | Budget, infrastructure, timeline changes | Always |
| `conflict-resolution` | Inter-role disagreements | Always |
| `routine-operation` | Standard development tasks | Delegatable |
| `minor-decision` | Low-impact choices | Delegatable |

---

## 5. Responding to COS Approval Requests

AMAMA responds with: `approved`, `rejected`, or `needs-revision`. The response includes request_id, decision, optional comment, and conditions.

See [approval-response-workflow.md](references/approval-response-workflow.md):
- When a COS-assigned agent sends an approval request -> Section 1
- How to format the response message -> Section 2
- What evaluation criteria to use -> Section 3
- When to escalate to user -> Section 3

---

## 6. Delegation Rules for Autonomous Operation

Autonomous mode allows a COS-assigned agent to proceed with certain operation types without requesting approval for each one. AMAMA controls delegation via grant/revoke messages.

See [delegation-rules.md](references/delegation-rules.md):
- When to grant autonomous mode to a COS-assigned agent -> Section 2
- How to configure delegation rules -> Section 2
- When to revoke autonomous mode -> Section 3
- What operations always require approval -> Section 4

---

## 7. AI Maestro Message Formats for COS Communication

All COS coordination happens via AI Maestro messages with specific JSON formats.

See [message-formats.md](references/message-formats.md):
- When formatting an approval request from COS-assigned agent -> Section 1
- When formatting an approval response from AMAMA -> Section 2
- When formatting an autonomy grant/revoke message -> Section 3
- When formatting a completion notification -> Section 4

---

## 8. Completion Notifications from COS-Assigned Agent

A COS-assigned agent notifies AMAMA when operations complete. User notification depends on operation type and user preferences.

See [completion-notifications.md](references/completion-notifications.md):
- When COS-assigned agent sends completion notifications -> Section 1
- How to process completion notifications -> Section 2
- When to notify the user about completions -> Section 3

---

## Error Handling

### Common Errors

| Error | Symptom | Solution |
|-------|---------|----------|
| Agent not in registry | `404` on COS assignment | Register agent first via `POST /api/agents/register` |
| COS-assigned agent not found | No response to messages | Verify agent session exists, check AI Maestro registry |
| Message send failure | AI Maestro API error | Check AI Maestro service status |
| Invalid approval format | COS-assigned agent rejects response | Review message format in Section 7 |
| Autonomy grant failed | COS-assigned agent doesn't acknowledge grant | Verify agent has latest plugin version |
| Duplicate request ID | Request ID collision | Use unique UUID for each request |
| Team not found | `404` on team operations | Create team first via `POST /api/teams` |
| COS already assigned | Team already has a COS | Unassign current COS before assigning new one |

### Error Scenarios

| Error | Cause | AMAMA Action |
|-------|-------|-------------|
| COS-assigned agent unresponsive | Agent session crashed or network issue | Alert user, attempt restart |
| Request timeout | AMAMA took too long to respond | Auto-escalate to user |
| Invalid request format | Malformed message from COS-assigned agent | Return error, request retry |
| Scope exceeded | COS-assigned agent attempted unauthorized operation | Revoke autonomy, alert user |
| Conflicting requests | Multiple requests for same resource | Queue and resolve sequentially |
| Cross-host assignment failure | GovernanceRequest rejected | Check governance policies, retry or escalate |

### Escalation to User

AMAMA escalates to user when:

1. Cannot make autonomous decision
2. Request involves user-defined critical operations
3. COS-assigned agent reports critical failure
4. Security concern detected
5. Request timeout approaching

### Audit Trail

All COS interactions are logged:

```yaml
cos_audit_log:
  - timestamp: "ISO-8601"
    event_type: "assign-cos|unassign-cos|request|response|grant|revoke|complete"
    request_id: "cos-req-{uuid}"
    team_id: "team-{uuid}"
    agent_id: "agent-{uuid}"
    details: "Event description"
    user_involved: true|false
```

---

## Examples

For complete examples of COS coordination flows, see [examples.md](references/examples.md):
- When handling a deployment approval request -> Example 1
- When granting autonomous mode for development -> Example 2
- When processing a completion notification -> Example 3

---

## Message Acknowledgment Protocol

All messages sent to a COS-assigned agent require acknowledgment (ACK) to ensure reliable communication. Different message types have different ACK timeout requirements.

### ACK Timeout Requirements

| Message Type | ACK Timeout | Retry Behavior | Escalation |
|--------------|-------------|----------------|------------|
| Approval decisions | 30 seconds | Retry once after timeout | Escalate to user if no ACK after retry |
| Work requests | 60 seconds | Retry once after timeout | Escalate to user if no ACK after retry |
| Health check pings | 60 seconds | No retry | Log as unresponsive |
| Status queries | 30 seconds | Retry once after timeout | Report timeout to user |
| Autonomy grant/revoke | 30 seconds | Retry once after timeout | Escalate to user if no ACK after retry |

### ACK Message Format

The COS-assigned agent must respond with an ACK message within the timeout period. The ACK message arrives via the `agent-messaging` skill with the following structure:

- **Sender**: The COS-assigned agent's session name
- **Subject**: "ACK: <original-subject>"
- **Priority**: `normal`
- **Content fields**:
  - `type`: `ack`
  - `original_message_id`: The message ID of the original message being acknowledged
  - `status`: One of `received` (message received), `processing` (actively working on it), or `completed` (action done)
  - `timestamp`: ISO-8601 timestamp of the acknowledgment

### Handling Missing ACK

**Step 1: Wait for Timeout**
- Start timer when message is sent
- Check inbox for ACK message at timeout

**Step 2: Retry Once**

Resend the original message with a retry flag using the `agent-messaging` skill:
- **Recipient**: The COS-assigned agent's session name
- **Subject**: "RETRY: <original-subject>"
- **Content**: Same as original message, plus `retry_of` (original message ID) and `retry_count` (1)
- **Priority**: `high`

**Verify**: confirm message delivery via the skill's sent messages feature.

**Step 3: Escalate if Still No ACK**
If no ACK after retry:

1. **Log the failure** in `docs_dev/sessions/ack-failures.md`
2. **Alert the user**:
   ```
   COS-Assigned Agent Communication Failure

   Agent: <agent-session-name>
   Team: <team-name>
   Message: <subject>
   Sent: <timestamp>
   Retry: <retry-timestamp>
   Status: No acknowledgment received

   The COS-assigned agent may be unresponsive. Options:
   - [Check Agent Health] - Send health ping
   - [Retry Again] - Send message again
   - [Reassign COS] - Unassign COS role and assign to different agent
   ```
3. **Do not assume message was processed** - treat as failed delivery

### ACK Verification Checklist

- [ ] Message sent with unique message ID
- [ ] Timer started at send time
- [ ] ACK received within timeout period
- [ ] ACK references correct original message ID
- [ ] ACK status recorded in communication log

## Related Commands

- `/amama-respond-to-cos` - Respond to pending COS approval requests
- `/amama-configure-cos-delegation` - Configure COS delegation rules
- `/amama-orchestration-status` - View status including COS operations
- `/amama-assign-cos` - Assign COS role to an existing agent
- `/amama-create-team` - Create a new team

## Resources

**Related Skills:**
- `amama-approval-workflows` - General approval workflow patterns
- `amama-role-routing` - Role routing and handoff patterns

**Related Documentation:**
- AI Maestro message templates in plugin shared directory
- COS role boundaries documentation
- AI Maestro Team API documentation

### Reference Documents

- [references/ai-maestro-message-templates.md](references/ai-maestro-message-templates.md) - AI Maestro inter-agent message templates
- [references/success-criteria.md](references/success-criteria.md) - COS coordination success criteria
- [references/workflow-checklists.md](references/workflow-checklists.md) - COS coordination checklists
- [references/creating-ecos-instance.md](references/creating-ecos-instance.md) - Assigning COS role procedure
- [references/creating-ecos-procedure.md](references/creating-ecos-procedure.md) - Team creation and agent registration procedure
- [references/workflow-examples.md](references/workflow-examples.md) - End-to-end workflow examples
- [references/spawn-failure-recovery.md](references/spawn-failure-recovery.md) - Agent and COS assignment failure recovery
