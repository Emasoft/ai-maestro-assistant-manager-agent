---
name: amama-amcos-coordination
description: Use when coordinating with the Chief of Staff (COS) for approval requests and autonomous operation delegation. Trigger with COS coordination requests.
version: 2.3.2
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: false
triggers:
  - COS agent sends approval request or completion report
  - AMAMA needs to grant/revoke autonomy or assign/unassign COS role
  - User requests COS delegation configuration
  - AMAMA needs to create a team and assign agents
---

# COS Coordination Skill

## Overview

Enables AMAMA to coordinate with COS-assigned agents (Chief of Staff role). A COS agent is an existing registered agent assigned as operational coordinator within a team, between AMAMA and specialist roles.

**v2:** AMAMA assigns COS role to existing agents via Team API (no longer spawns instances). See [references/cos-definition.md](references/cos-definition.md) for hierarchy.

## Prerequisites

1. Target agent exists in AI Maestro registry (`GET /api/agents`)
2. AI Maestro messaging is available
3. A team exists (or will be created) for the COS role
4. Approval workflow is understood

## Instructions

1. **Assign COS Role** — Verify agent exists, assign via `PATCH /api/teams/$TEAM_ID/chief-of-staff`, send initialization message, verify ACK. AMAMA is the ONLY agent authorized. See [references/creating-amcos-instance.md](references/creating-amcos-instance.md).
2. **Create Teams and Register Agents** — Register agents via `POST /api/agents/register`, create teams via `POST /api/teams`. See [references/creating-amcos-procedure.md](references/creating-amcos-procedure.md).
3. **Handle Approval Requests** — COS agents request approval for critical operations, policy exceptions, resource allocation, and conflicts. See [references/approval-request-flow.md](references/approval-request-flow.md).
4. **Respond to Approvals** — Respond with `approve`, `deny`, or `defer` including request_id and optional conditions. See [references/approval-response-workflow.md](references/approval-response-workflow.md).
5. **Manage Delegation** — Grant/revoke autonomous mode to let COS agents proceed without per-operation approval. See [references/delegation-rules.md](references/delegation-rules.md).
6. **Process Completions** — COS agents notify AMAMA on completion. Decide whether to notify user based on operation type. See [references/completion-notifications.md](references/completion-notifications.md).
7. **Message Acknowledgment** — All COS messages require ACK within timeout (30-60s). Retry once on timeout, then escalate to user. See [references/ack-protocol.md](references/ack-protocol.md).

### Checklist

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

## Error Handling

Common errors: agent not in registry (register first), COS not found (check session), message failures (check AI Maestro status), team not found (create first). Escalate to user when: cannot decide autonomously, critical failure reported, security concern, or timeout. See [references/error-handling.md](references/error-handling.md) for full error tables and audit trail format.

## Examples

**Approve a deployment:** Receive request from COS inbox, evaluate risk, send `{type: "approval_decision", request_id: "cos-req-123", decision: "approve"}`, wait for ACK.

See [references/examples.md](references/examples.md) and [references/workflow-examples.md](references/workflow-examples.md).

## Resources

- [references/message-formats.md](references/message-formats.md) - Message JSON formats
- [references/ai-maestro-message-templates.md](references/ai-maestro-message-templates.md) - Templates
- [references/success-criteria.md](references/success-criteria.md) - Success criteria
- [references/workflow-checklists.md](references/workflow-checklists.md) - Checklists
- [references/spawn-failure-recovery.md](references/spawn-failure-recovery.md) - Failure recovery

**Skills:** `amama-approval-workflows`, `amama-role-routing`
**Commands:** `/amama-respond-to-amcos`, `/amama-orchestration-status`
