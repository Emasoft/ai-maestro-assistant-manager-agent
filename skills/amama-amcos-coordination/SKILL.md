---
name: amama-amcos-coordination
description: Use when coordinating with the Chief of Staff (COS) for approval requests and autonomous operation delegation. Trigger with COS coordination requests.
version: 2.3.2
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: false
---

# COS Coordination Skill

## Overview

Enables AMAMA to coordinate with COS-assigned agents. A COS is an existing registered agent assigned as operational coordinator within a team via Team API. See [references/cos-definition.md](references/cos-definition.md).

## Prerequisites

1. Target agent in AI Maestro registry (`GET /api/agents`)
2. AI Maestro messaging available
3. A team exists or will be created

## Instructions

1. **Assign COS** — `PATCH /api/teams/$TEAM_ID/chief-of-staff`. See `references/creating-amcos-instance.md`.
2. **Create Teams/Agents** — `POST /api/agents/register`, `POST /api/teams`. See `references/creating-amcos-procedure.md`.
3. **Approvals** — Evaluate, respond. See [references/approval-request-flow.md](references/approval-request-flow.md).
  - When COS-Assigned Agent Sends Approval Requests
  - Request Categories
  - Related Documents
4. **Respond** — Send decision. See [references/approval-response-workflow.md](references/approval-response-workflow.md).
  - Decision Options
  - When to Use Each Decision
  - Response Format
  - Field Descriptions
  - Response Workflow
5. **Delegation** — Grant/revoke autonomy. See [references/delegation-rules.md](references/delegation-rules.md).
  - What is Autonomous Mode
  - Delegation Configuration
  - Granting Autonomous Mode
  - Grant Parameters
  - Revoking Autonomous Mode
  - Revocation Message
  - Revocation Reasons
  - Operations That ALWAYS Require AMAMA Approval
6. **Completions** — Handle notifications. See `references/completion-notifications.md`.
7. **ACK** — Require ACK 30-60s. See [references/ack-protocol.md](references/ack-protocol.md).
  - ACK Timeout Requirements
  - ACK Message Format
  - Handling Missing ACK
  - ACK Verification Checklist

Copy this checklist and track your progress:

- [ ] Identify operation type
- [ ] Verify target agent is registered
- [ ] Prepare API payload
- [ ] Execute API call or send message
- [ ] Wait for ACK (30-60s)
- [ ] Log result and update state

## Output

| Operation | Output |
|-----------|--------|
| Assign COS | Agent assigned as COS for team |
| Create team | Team created, agents assigned |
| Grant autonomy | Scope confirmed by COS agent |
| Revoke autonomy | COS agent notified |

## Error Handling

See [references/error-handling.md](references/error-handling.md). Escalate on: decision failure, critical failure, security concern, or timeout.

## Examples

**Input:** `PATCH /api/teams/team-backend/chief-of-staff` with `{"agentId":"amcos-chief-of-staff"}`

**Output:** `{"team":"team-backend","chiefOfStaff":"amcos-chief-of-staff","status":"assigned"}`

See [references/workflow-examples.md](references/workflow-examples.md) for full examples.
  - Example 1: User Requests New Project
  - Example 2: AMCOS Requests Approval (Low Risk)
  - Example 3: AMCOS Requests Approval (High Risk)
  - Example 4: User Requests Status
  - Example 5: COS Role Assignment Failure
  - COS Role Assignment Failure Recovery Protocol
  - Handoff Pattern

## Resources

- [references/message-formats.md](references/message-formats.md) - JSON formats
  - AMCOS Approval Request Format
  - Field Descriptions
  - AMAMA Response Format
  - Autonomy Messages
  - Grant Message
  - Revoke Message
  - Completion Notification Format
  - Field Descriptions
- `references/ai-maestro-message-templates.md` - Templates
- `references/success-criteria.md` - Success criteria
- [references/workflow-checklists.md](references/workflow-checklists.md) - Checklists
  - Checklist: Creating New Team
  - Checklist: Assigning COS Role
  - Checklist: Processing AMCOS Approval Request
  - Checklist: Routing User Request to AMCOS
  - Checklist: Providing Status to User
- `references/spawn-failure-recovery.md` - Recovery

**Skills:** `amama-approval-workflows`, `amama-role-routing`
**Commands:** `/amama-respond-to-amcos`, `/amama-orchestration-status`
