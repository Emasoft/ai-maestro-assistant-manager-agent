---
name: amama-amcos-coordination
description: Use when coordinating with COS for approvals and delegation. Trigger with COS coordination requests. Loaded by ai-maestro-assistant-manager-agent-main-agent
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: false
---

# COS Coordination Skill

## Overview

Coordinates with COS-assigned agents. See [cos-definition](references/cos-definition.md).

## Prerequisites

1. Target agent in AI Maestro registry (`aimaestro-agent.sh list`)
2. AI Maestro messaging available
3. A team exists or will be created

## Instructions

1. **Create team + COS** — You (MANAGER) create the team yourself with `aimaestro-teams.sh create` (R29, no user approval); the server auto-creates the team's COS, which you then wake and grant its mandate. See [creating-amcos-instance](references/creating-amcos-instance.md).
   > Why the MANAGER Creates the COS · How to Create the COS · When to Create the COS · Post-Creation Steps · Cross-Host COS Assignment
2. **Create the 5 base members** — A team is FROZEN until its COS + 5 base members exist (R31). You create teams + AUTONOMOUS/MAINTAINER; the COS, under your team-creation mandate (R30), creates the 5 base members + project MEMBERs (MEMBER-titled on the member-agent role plugin). See [creating-amcos-procedure](references/creating-amcos-procedure.md).
   > Overview · Key Principles · Agent Registration · Team Creation · COS Creation · Step-by-Step Procedure · Success Criteria · Troubleshooting · Related Documents
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
6. **Completions** — Handle notifications. See [completion-notifications](references/completion-notifications.md).
   > When AMCOS Sends Completion Notifications · Processing Completion Notifications · User Notification Rules
7. **ACK** — Require ACK 30-60s. See [references/ack-protocol.md](references/ack-protocol.md).
  - ACK Timeout Requirements
  - ACK Message Format
  - Handling Missing ACK
  - ACK Verification Checklist

Checklist: identify op type → verify agent registered → run the frozen CLI (`aimaestro-agent.sh` / `aimaestro-teams.sh`) → await ACK (30-60s).

## Output

| Operation | Output |
|-----------|--------|
| Create team + COS | Team created (R29), COS auto-created and woken |
| Grant COS mandate | COS mandate confirmed (R30) |
| Grant autonomy | Scope confirmed by COS |
| Revoke autonomy | COS agent notified |

## Error Handling

See [references/error-handling.md](references/error-handling.md). Escalate on: decision failure, critical failure, security concern, or timeout.

## Examples

**Input:** User provides a repository; you create team-1 via `aimaestro-teams.sh create` (R29)

**Output:** The server auto-creates the COS; you verify with `aimaestro-teams.sh show team-1` returning `{"chiefOfStaff":"amcos-cos","status":"assigned"}`, then wake it and grant its mandate (R30)

See [references/workflow-examples.md](references/workflow-examples.md) for full examples.
  - Example 1: User Requests New Project
  - Example 2: AMCOS Requests Approval (Low Risk)
  - Example 3: AMCOS Requests Approval (High Risk)
  - Example 4: User Requests Status
  - Example 5: Team + COS Creation Failure
  - Team + COS Creation Failure Recovery Protocol
  - Handoff Pattern

## Resources

- [references/message-formats.md](references/message-formats.md) - JSON formats
  > AMCOS Approval Request Format · AMAMA Response Format · Autonomy Messages · Completion Notification Format
- [ai-maestro-message-templates](references/ai-maestro-message-templates.md) - Templates
  > Receiving Messages · Sending Approval-Related Messages · Requesting Information from AMCOS · Delegating Work to AMCOS · Standard AI Maestro Messaging Patterns
- [success-criteria](references/success-criteria.md) - Success criteria
  > Success: User Request Understood · Success: Project and Team Creation Complete · Success: AMCOS Created and Ready · Success: Approval Processed · Success: Status Reported · General Success Verification Principles
- [references/workflow-checklists.md](references/workflow-checklists.md) - Checklists
  - Checklist: Creating New Team
  - Checklist: Granting the COS Mandate
  - Checklist: Processing AMCOS Approval Request
  - Checklist: Routing User Request to AMCOS
  - Checklist: Providing Status to User
- [spawn-failure-recovery](references/spawn-failure-recovery.md) - Recovery
  > Overview · Team + COS Creation Failure Recovery Protocol · Communication Breakdown Recovery · Approval Request Handling Failures · Agent Creation Failures (General) · Logging and Audit Trail · Timeliness Requirements · Example Scenarios · Summary
