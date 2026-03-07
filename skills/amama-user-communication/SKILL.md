---
name: amama-user-communication
description: Use when communicating with users for clarification, presenting options, requesting approval, or reporting completion. Trigger with user requests or communication needs.
version: 2.3.2
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: false
triggers:
  - when clarifying requirements
  - when presenting options to user
  - when requesting approval
  - when reporting completion
---

# User Communication Skill

## Overview

Provides standardized patterns for communicating with users: clarification requests, option presentations, approval requests, completion reports, blocker notifications, and status updates. For AMCOS coordination procedures, see the amama-amcos-coordination skill.

## Prerequisites

None required. This skill provides communication patterns that can be used immediately.

## Instructions

1. Identify the communication type needed (clarification, options, approval, completion, blocker, status)
2. Use the appropriate template. See [references/communication-patterns.md](references/communication-patterns.md) for detailed templates
3. Fill in all placeholders with specific information
4. Follow the Quality Rules below for clarity
5. Include relevant UUIDs, issue numbers, and file paths for traceability

### Checklist

- [ ] Identify communication type
- [ ] Select and fill appropriate template
- [ ] Review against Quality Rules
- [ ] Include UUIDs and references
- [ ] Send communication

## Output

| Type | When to Use |
|------|-------------|
| Clarification Request | User input is incomplete or ambiguous |
| Option Presentation | Multiple approaches are viable |
| Approval Request | Before significant or irreversible operations |
| Completion Report | Task or subtask is finished |
| AMCOS Handoff | Routing work to specialist agents |
| Status Update | During long-running operations |

## Blocker Communication

When tasks are blocked, notify the user IMMEDIATELY. See [references/blocker-notification-templates.md](references/blocker-notification-templates.md) for full templates, escalation timelines, and resolution routing.

| Blocker Type | Timing | Severity |
|--------------|--------|----------|
| Critical-path <48h deadline | Immediate | Critical |
| Cascade blocker (multiple tasks) | Immediate | High |
| Requires user credentials/access | Immediate | High |
| Non-critical, no deadline | Next status report | Medium |
| Technical (agents can resolve) | No notification | N/A |

## Quality Rules

1. **Be Specific**: Never say "some files" -- list them
2. **Be Actionable**: Always tell user what to do next
3. **Be Honest**: Admit uncertainty, don't guess
4. **Be Concise**: Use bullets, avoid walls of text
5. **Be Traceable**: Include UUIDs, issue numbers

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| No user response | User inactive | Wait, then send reminder per escalation timeline |
| Ambiguous user input | Unclear response | Ask for specific clarification |
| Template mismatch | Wrong pattern selected | Re-evaluate and use correct template |
| AMCOS unresponsive | Session crashed or network issue | Follow recovery procedure in [references/amcos-monitoring.md](references/amcos-monitoring.md) |

## Examples

### Clarification Request
```
I need clarification on the following:
1. Should the login support both email and username?
2. What is the session timeout duration?

Please provide:
- Your preference for login identifiers
- Timeout in minutes (e.g., 30, 60, 120)
```

### Completion Report
```
**Task Complete**
Summary: Implemented user login endpoint with OAuth2 support.
Changes made:
- src/auth/login.py: Added login handler
- tests/test_login.py: Added 15 test cases
Verification: Run `pytest tests/test_login.py`
Next steps: Proceed with logout endpoint
```

## Resources

Related skills: amama-amcos-coordination, amama-approval-workflows, amama-role-routing, shared/message_templates.md

### Reference Documents

- [references/communication-patterns.md](references/communication-patterns.md) -- Detailed templates for all types
- [references/response-templates.md](references/response-templates.md) -- Response templates with guidelines
- [references/blocker-notification-templates.md](references/blocker-notification-templates.md) -- Blocker formats, escalation, resolution routing
- [references/workflow-examples.md](references/workflow-examples.md) -- Full workflow examples
- [references/amcos-monitoring.md](references/amcos-monitoring.md) -- AMCOS health monitoring and recovery
- [references/handoff-protocol.md](references/handoff-protocol.md) -- Handoff protocol and design doc scripts
