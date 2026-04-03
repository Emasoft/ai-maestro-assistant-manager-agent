---
name: amama-user-communication
description: Use when communicating with users for clarification, presenting options, requesting approval, or reporting completion. Trigger with user requests or communication needs. Loaded by ai-maestro-assistant-manager-agent-main-agent.
version: 2.3.2
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: false
---

# User Communication Skill

## Overview

Standardized patterns for user communication: clarification, options, approval, completion, blockers, and status updates.

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
