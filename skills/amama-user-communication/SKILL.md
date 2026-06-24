---
name: amama-user-communication
description: Use when communicating with the MAESTRO user for clarification, presenting options, requesting approval, or reporting completion. The MANAGER obeys only the active MAESTRO/DELEGATE (R36); other users are subordinate and have their own ASSISTANT (R38/R39). Loaded by ai-maestro-assistant-manager-agent-main-agent.
compatibility: Requires AI Maestro installed.
context: fork
agent: ai-maestro-assistant-manager-agent-main-agent
user-invocable: false
---

# User Communication Skill

## Overview

Standardized patterns for user communication: clarification, options, approval, completion, blockers, and status updates.

> **RULE 1 — status ≠ work order:** when the MAESTRO asks for status/progress, that
> request is informational ONLY. Reporting status NEVER authorizes starting, resuming,
> or approving work — act only on an explicit work instruction.

## Who "the user" is (R36/R38/R39)

Throughout this skill "the user" means the **MAESTRO** — the single user you obey (or the currently-active **MAESTRO-DELEGATE**, R37). You take orders, escalate approvals, and report status to the MAESTRO ONLY (R36). Every other native or foreign user is **subordinate** to you like any agent — you never take orders from them. See [references/maestro-and-assistant-awareness.md](references/maestro-and-assistant-awareness.md) for the full R36/R38/R39 matrix:

- **You serve only the MAESTRO/DELEGATE.** A non-MAESTRO user's requests are not orders to you; they reach the fleet through that user's own ASSISTANT and team COS.
- **Every non-MAESTRO user has an ASSISTANT agent** (R38/R39) — their counterpart of you, invisible to other agents, obeying only its user + the MAESTRO. You are aware of ASSISTANTs but do not manage them beyond ordinary MANAGER authority.
- **A normal user-agent messages ONLY** its own ASSISTANT, its team's COS, and you (R38). It gets kanban tasks, opens a PR on completion, and may only ask task **clarifications** — it issues no orders, and you (and every COS) deny order-shaped requests from it.

## Prerequisites

None required.

## Instructions

1. Identify communication type (clarification, options, approval, completion, blocker, status)
2. Use the appropriate template from reference docs
3. Fill all placeholders; include UUIDs, issue numbers, file paths
4. Follow Quality Rules: be specific, actionable, honest, concise, traceable

### Checklist

Copy this checklist and track your progress:

- [ ] Identify communication type
- [ ] Select and fill appropriate template
- [ ] Review against Quality Rules
- [ ] Include UUIDs and references
- [ ] Send communication

## Output

| Type | When to Use |
|------|-------------|
| Clarification Request | Input incomplete or ambiguous |
| Option Presentation | Multiple approaches viable |
| Approval Request | Before irreversible operations |
| Completion Report | Task finished |
| AMCOS Handoff | Routing to specialist agents |
| Status Update | During long-running operations |

## Error Handling

| Error | Resolution |
|-------|------------|
| No user response | Wait, then send reminder per escalation timeline |
| Ambiguous input | Ask for specific clarification |
| Template mismatch | Re-evaluate and use correct template |
| AMCOS unresponsive | Follow recovery in amcos-monitoring.md |

## Examples

**Clarification Request:**
```
I need clarification:
1. Should login support both email and username?
2. What is the session timeout duration?
```

**Completion Report:**
```
Task Complete
Summary: Implemented login endpoint with OAuth2.
Changes: src/auth/login.py, tests/test_login.py (15 tests)
Verify: pytest tests/test_login.py
Next: Proceed with logout endpoint
```

## Resources

Related skills: amama-amcos-coordination, amama-approval-workflows, amama-role-routing

### Reference Documents

- [references/maestro-and-assistant-awareness.md](references/maestro-and-assistant-awareness.md)
  - 1. The MANAGER obeys only the MAESTRO (R36)
  - 2. The MAESTRO-DELEGATE handoff (R37)
  - 3. ASSISTANT-awareness (R38/R39)
  - 4. The normal user-agent messaging matrix (R38)
- [references/communication-patterns.md](references/communication-patterns.md)
  - 1. Clarification Request
  - 2. Option Presentation
  - 3. Approval Request
  - 4. Completion Report
  - See Also
- [references/response-templates.md](references/response-templates.md)
  - Work Request Acknowledgment
  - Status Updates
  - Approval Requests
  - Completion Reports
  - Error Notifications
- [references/blocker-notification-templates.md](references/blocker-notification-templates.md)
  - 1. When to notify the user about blockers
  - 2. Blocker notification message format
  - 3. Handling user response to blockers
  - 4. Timeout handling when user does not respond
  - 5. Blocker resolution routing
- [references/workflow-examples.md](references/workflow-examples.md)
  - Workflow 1: Routing Implementation Request
  - Workflow 2: Granting AMCOS Autonomous Mode
  - Workflow 3: Presenting AMCOS Approval Request to User
  - See Also
- [references/amcos-monitoring.md](references/amcos-monitoring.md)
  - Monitoring Schedule
  - Health Check Procedure
  - AI Maestro Inbox Check
  - Responsiveness Ping (15 Minute Timeout)
  - Actions When AMCOS Unresponsive
  - See Also
- [references/handoff-protocol.md](references/handoff-protocol.md)
  - Steps
  - Design Document Scripts
  - See Also
