# Workflow Examples

## Table of Contents
- [Workflow 1: Routing Implementation Request](#workflow-1-routing-implementation-request)
- [Workflow 2: Granting AMCOS Autonomous Mode](#workflow-2-granting-amcos-autonomous-mode)
- [Workflow 3: Presenting AMCOS Approval Request to User](#workflow-3-presenting-amcos-approval-request-to-user)
- [See Also](#see-also)

Detailed workflow examples for user communication scenarios.

---

## Workflow 1: Routing Implementation Request

```
User: "I need to implement a new authentication module for the project. It should support OAuth2 and JWT tokens."

AMAMA Response: "I understand you need a new authentication module with OAuth2 and JWT support. Let me route this to the Orchestrator for implementation.

Creating handoff file and routing to AMCOS for delegation to the Orchestrator agent, or directly to the Orchestrator if urgent. The authentication module will be implemented with the specified requirements."
```

## Workflow 2: Granting AMCOS Autonomous Mode

```
User: "Let AMCOS handle routine development tasks for the next 4 hours while I'm in a meeting."

AMAMA Response: "I'll grant AMCOS autonomous mode for routine development operations with a 4-hour expiration.

Sending autonomy grant to AMCOS with scope limited to routine-operation and minor-decision types on feature/* branches. AMCOS will operate autonomously for these tasks but will still notify you of important completions and request approval for any critical operations."

[Send AI Maestro message with autonomy_grant type]
```

## Workflow 3: Presenting AMCOS Approval Request to User

```
[AMCOS sends approval request for staging deployment]

AMAMA presents to user:

## AMCOS Approval Request

**Operation**: Deploy v2.1.0 to staging environment
**Risk Level**: Medium (reversible)
**Affected Resources**: staging-server, staging-db
**Related Issues**: #89, #92
**AMCOS Recommendation**: Approve

Do you approve this deployment?
- [Approve] - AMCOS will proceed
- [Reject] - AMCOS will cancel
- [Needs Revision] - AMCOS will modify request
```

---

## See Also

- [communication-patterns.md](communication-patterns.md) - Core communication templates
- [response-templates.md](response-templates.md) - Standard response templates
