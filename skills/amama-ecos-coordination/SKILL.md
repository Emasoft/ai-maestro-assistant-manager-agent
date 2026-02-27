---
name: amama-amcos-coordination
description: Use when coordinating with the Chief of Staff (AMCOS) for approval requests and autonomous operation delegation. Trigger with AMCOS coordination requests.
version: 1.0.0
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-main
user-invocable: false
triggers:
  - AMCOS sends an approval request via AI Maestro
  - AMAMA needs to grant or revoke autonomous mode for AMCOS
  - AMCOS reports completion of delegated operations
  - User requests to configure AMCOS delegation rules
---

# AMCOS Coordination Skill

## Overview

This skill enables the Assistant Manager (AMAMA) to coordinate with the Chief of Staff (AMCOS) component. AMCOS acts as the operational coordinator that can either request approval for operations or operate autonomously within granted boundaries.

## Prerequisites

Before using this skill, ensure:
1. AMCOS agent is running or can be created
2. AI Maestro messaging is available
3. Approval workflow is understood

## Instructions

1. Identify coordination type needed
2. Send appropriate message to AMCOS
3. Wait for acknowledgment
4. Process AMCOS response

### Checklist

Copy this checklist and track your progress:

- [ ] Identify coordination type (create/grant/revoke/respond)
- [ ] Prepare AI Maestro message payload
- [ ] Send message to AMCOS
- [ ] Wait for acknowledgment
- [ ] Process and log response

## Output

| Operation | Output |
|-----------|--------|
| Create AMCOS | AMCOS agent spawned, registered |
| Grant autonomy | Autonomy scope confirmed |
| Revoke autonomy | Autonomy revoked, AMCOS notified |

## Table of Contents

1. What is AMCOS and Its Relationship with AMAMA
2. Creating AMCOS (AMAMA Exclusive Responsibility)
3. Approval Request Flow from AMCOS to AMAMA
4. Responding to AMCOS Approval Requests
5. Delegation Rules for Autonomous Operation
6. AI Maestro Message Formats for AMCOS Communication
7. Completion Notifications from AMCOS
8. Error Handling and Escalation

---

## 1. What is AMCOS and Its Relationship with AMAMA

### Definition

AMCOS (AI Maestro Chief of Staff) is a coordination component that manages day-to-day operational tasks. It sits between AMAMA and the specialized roles (Architect, Orchestrator, Integrator).

### Hierarchy

```
USER
  |
AMAMA (Assistant Manager) - User's direct interface
  |
AMCOS (Chief of Staff) - Operational coordinator
  |
+-- EAA (Architect)
+-- EOA (Orchestrator)
+-- EIA (Integrator)
```

### Responsibilities Split

| Component | Responsibilities |
|-----------|------------------|
| AMAMA | User communication, final approvals, high-level decisions |
| AMCOS | Task coordination, routine operations, delegation management |

---

## 2. Creating AMCOS (AMAMA Exclusive Responsibility)

AMAMA is the ONLY agent authorized to create AMCOS, ensuring single point of authority and role constraint enforcement.

See [creating-amcos-instance.md](references/creating-amcos-instance.md):
- When to create a new AMCOS instance -> Section 1.3
- How to spawn AMCOS with proper constraints -> Section 1.2
- Why only AMAMA can create AMCOS -> Section 1.1
- What to do after creating AMCOS -> Section 1.4

---

## 3. Approval Request Flow from AMCOS to AMAMA

### When AMCOS Sends Approval Requests

AMCOS sends approval requests to AMAMA when:

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

## 4. Responding to AMCOS Approval Requests

AMAMA responds with: `approved`, `rejected`, or `needs-revision`. The response includes request_id, decision, optional comment, and conditions.

See [approval-response-workflow.md](references/approval-response-workflow.md):
- When AMCOS sends an approval request -> Section 1
- How to format the response message -> Section 2
- What evaluation criteria to use -> Section 3
- When to escalate to user -> Section 3

---

## 5. Delegation Rules for Autonomous Operation

Autonomous mode allows AMCOS to proceed with certain operation types without requesting approval for each one. AMAMA controls delegation via grant/revoke messages.

See [delegation-rules.md](references/delegation-rules.md):
- When to grant autonomous mode to AMCOS -> Section 2
- How to configure delegation rules -> Section 2
- When to revoke autonomous mode -> Section 3
- What operations always require approval -> Section 4

---

## 6. AI Maestro Message Formats for AMCOS Communication

All AMCOS coordination happens via AI Maestro messages with specific JSON formats.

See [message-formats.md](references/message-formats.md):
- When formatting an approval request from AMCOS -> Section 1
- When formatting an approval response from AMAMA -> Section 2
- When formatting an autonomy grant/revoke message -> Section 3
- When formatting a completion notification -> Section 4

---

## 7. Completion Notifications from AMCOS

AMCOS notifies AMAMA when operations complete. User notification depends on operation type and user preferences.

See [completion-notifications.md](references/completion-notifications.md):
- When AMCOS sends completion notifications -> Section 1
- How to process completion notifications -> Section 2
- When to notify the user about completions -> Section 3

---

## Error Handling

### Common Errors

| Error | Symptom | Solution |
|-------|---------|----------|
| AMCOS not found | No response to messages | Verify AMCOS session exists, create if needed |
| Message send failure | AI Maestro API error | Check AI Maestro service status |
| Invalid approval format | AMCOS rejects response | Review message format in Section 4 |
| Autonomy grant failed | AMCOS doesn't acknowledge grant | Verify AMCOS has latest plugin version |
| Duplicate request ID | Request ID collision | Use unique UUID for each request |

### Error Scenarios

| Error | Cause | AMAMA Action |
|-------|-------|-------------|
| AMCOS unresponsive | AMCOS session crashed or network issue | Alert user, attempt restart |
| Request timeout | AMAMA took too long to respond | Auto-escalate to user |
| Invalid request format | Malformed message from AMCOS | Return error, request retry |
| Scope exceeded | AMCOS attempted unauthorized operation | Revoke autonomy, alert user |
| Conflicting requests | Multiple requests for same resource | Queue and resolve sequentially |

### Escalation to User

AMAMA escalates to user when:

1. Cannot make autonomous decision
2. Request involves user-defined critical operations
3. AMCOS reports critical failure
4. Security concern detected
5. Request timeout approaching

### Audit Trail

All AMCOS interactions are logged:

```yaml
ecos_audit_log:
  - timestamp: "ISO-8601"
    event_type: "request|response|grant|revoke|complete"
    request_id: "amcos-req-{uuid}"
    details: "Event description"
    user_involved: true|false
```

---

## Examples

For complete examples of AMCOS coordination flows, see [examples.md](references/examples.md):
- When handling a deployment approval request -> Example 1
- When granting autonomous mode for development -> Example 2
- When processing a completion notification -> Example 3

---

## Message Acknowledgment Protocol

All messages sent to AMCOS require acknowledgment (ACK) to ensure reliable communication. Different message types have different ACK timeout requirements.

### ACK Timeout Requirements

| Message Type | ACK Timeout | Retry Behavior | Escalation |
|--------------|-------------|----------------|------------|
| Approval decisions | 30 seconds | Retry once after timeout | Escalate to user if no ACK after retry |
| Work requests | 60 seconds | Retry once after timeout | Escalate to user if no ACK after retry |
| Health check pings | 60 seconds | No retry | Log as unresponsive |
| Status queries | 30 seconds | Retry once after timeout | Report timeout to user |
| Autonomy grant/revoke | 30 seconds | Retry once after timeout | Escalate to user if no ACK after retry |

### ACK Message Format

AMCOS must respond with an ACK message within the timeout period. The ACK message arrives via the `agent-messaging` skill with the following structure:

- **Sender**: `amcos-<project-name>`
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
- **Recipient**: `amcos-<project-name>`
- **Subject**: "RETRY: <original-subject>"
- **Content**: Same as original message, plus `retry_of` (original message ID) and `retry_count` (1)
- **Priority**: `high`

**Verify**: confirm message delivery via the skill's sent messages feature.

**Step 3: Escalate if Still No ACK**
If no ACK after retry:

1. **Log the failure** in `docs_dev/sessions/ack-failures.md`
2. **Alert the user**:
   ```
   AMCOS Communication Failure

   Message: <subject>
   Sent: <timestamp>
   Retry: <retry-timestamp>
   Status: No acknowledgment received

   AMCOS may be unresponsive. Options:
   - [Check AMCOS Health] - Send health ping
   - [Retry Again] - Send message again
   - [Respawn AMCOS] - Terminate and recreate AMCOS session
   ```
3. **Do not assume message was processed** - treat as failed delivery

### ACK Verification Checklist

- [ ] Message sent with unique message ID
- [ ] Timer started at send time
- [ ] ACK received within timeout period
- [ ] ACK references correct original message ID
- [ ] ACK status recorded in communication log

## Related Commands

- `/amama-respond-to-ecos` - Respond to pending AMCOS approval requests
- `/amama-configure-amcos-delegation` - Configure AMCOS delegation rules
- `/amama-orchestration-status` - View status including AMCOS operations

## Resources

**Related Skills:**
- `amama-approval-workflows` - General approval workflow patterns
- `amama-role-routing` - Role routing and handoff patterns

**Related Documentation:**
- AI Maestro message templates in plugin shared directory
- AMCOS role boundaries documentation

### Reference Documents

- [references/ai-maestro-message-templates.md](references/ai-maestro-message-templates.md) - AI Maestro inter-agent message templates
- [references/success-criteria.md](references/success-criteria.md) - AMCOS coordination success criteria
- [references/workflow-checklists.md](references/workflow-checklists.md) - AMCOS coordination checklists
- [references/creating-amcos-procedure.md](references/creating-amcos-procedure.md) - Creating AMCOS procedure
- [references/workflow-examples.md](references/workflow-examples.md) - End-to-end workflow examples
- [references/spawn-failure-recovery.md](references/spawn-failure-recovery.md) - Agent spawn failure recovery
