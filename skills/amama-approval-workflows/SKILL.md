---
name: amama-approval-workflows
description: Use when handling governance approvals via GovernanceRequest API (team membership, agent lifecycle, COS assignment). Trigger with pending governance requests.
version: 2.3.2
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: false
triggers:
  - A GovernanceRequest is created with status "pending"
  - An agent or COS submits a transfer request
  - MANAGER needs to approve/reject a governance operation
  - Quality gates or security gates require MANAGER authorization
---

# Approval Workflows Skill

## Overview

Structured workflows for handling **governance** approval requests through the GovernanceRequest API. Two approval tracks exist:

- **Governance approvals** (this skill): Team membership, COS assignment, agent lifecycle, transfers. Uses GovernanceRequest API (`POST /api/v1/governance/requests/{id}/approve`).
- **Operational approvals** (`amama-amcos-coordination` skill): Deployments, merges, test runs. Uses message-based flow.

## Prerequisites

- AI Maestro v2+ with Governance API at `$AIMAESTRO_API` (default: `http://localhost:23000`)
- Governance password must be set. See [references/governance-password.md](references/governance-password.md)
- AMAMA must have access to `docs_dev/handoffs/` directory
- State file must be writable for local approval tracking

## Instructions

1. Poll for GovernanceRequests with status `pending` (`GET /api/v1/governance/requests?status=pending`)
2. Parse request type (8 types supported). See [references/governance-request-types.md](references/governance-request-types.md)
3. Present to MANAGER using the appropriate template
4. On decision, call approve/reject endpoint with governance password
5. Verify state transition completed. See [references/state-machine.md](references/state-machine.md)
6. Update local state tracking. See [references/state-tracking.md](references/state-tracking.md)
7. Notify requesting agent of the outcome

**Key API endpoints:**
- `GET /api/v1/governance/requests?status=pending` - List pending
- `POST /api/v1/governance/requests/{id}/approve` - Approve
- `POST /api/v1/governance/requests/{id}/reject` - Reject
- `POST /api/v1/governance/transfers` - Submit transfer

Full endpoint docs: [references/api-endpoints.md](references/api-endpoints.md)

## Output

| Outcome | Status | Action |
|---------|--------|--------|
| MANAGER approves | `local-approved` or `dual-approved` | Call approve endpoint, update state, notify agent |
| MANAGER rejects | `rejected` | Call reject endpoint, update state, notify agent |
| MANAGER requests info | `pending` (unchanged) | Query details, re-present |
| Timeout (24h) | `rejected` | Auto-reject, notify agent. See [references/expiry-workflow.md](references/expiry-workflow.md) |
| Rate limit hit | `pending` (unchanged) | Queue action, wait for cooldown, retry |

## Error Handling

| Error | Resolution |
|-------|------------|
| `401 Unauthorized` | Prompt MANAGER to re-enter governance password |
| `429 Too Many Requests` | Wait 60 seconds, then retry |
| `404 Not Found` | Verify request ID; may be already processed |
| `409 Conflict` | Refresh request status and present current state |
| Password not set | Run initial setup per [references/governance-password.md](references/governance-password.md) |

## Examples

**Approve a team membership request:**
```bash
# Poll, then approve
curl -X POST "$AIMAESTRO_API/api/v1/governance/requests/gov-abc123/approve" \
  -H "Content-Type: application/json" \
  -d '{"password": "***", "approvedBy": "MANAGER", "notes": "Approved"}'
```

More examples: [references/examples.md](references/examples.md)

## Resources

- [references/governance-request-types.md](references/governance-request-types.md) - All 8 request types with payloads and templates
- [references/api-endpoints.md](references/api-endpoints.md) - API endpoints with curl examples
- [references/state-machine.md](references/state-machine.md) - State machine, transitions, plugin prefixes
- [references/state-tracking.md](references/state-tracking.md) - Local state file schema, proactive monitoring
- [references/escalation-rules.md](references/escalation-rules.md) - Auto-reject/escalation rules, notification, checklist
- [references/governance-password.md](references/governance-password.md) - Password setup and security rules
- [references/legacy-approval-types.md](references/legacy-approval-types.md) - Legacy v1 approval workflows
- [references/expiry-workflow.md](references/expiry-workflow.md) - Approval expiry workflow and configuration
- [references/examples.md](references/examples.md) - Worked examples of approval/rejection flows
- [references/rule-14-enforcement.md](references/rule-14-enforcement.md) - RULE 14: User Requirements Are Immutable
- [references/best-practices.md](references/best-practices.md) - Approval workflow best practices
