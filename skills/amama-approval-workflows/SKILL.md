---
name: amama-approval-workflows
description: Use when handling governance approvals via GovernanceRequest API (team membership, agent lifecycle, COS assignment). Trigger with pending governance requests.
version: 2.3.0
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

This skill provides the Assistant Manager (AMAMA) with structured workflows for handling **governance** approval requests through the GovernanceRequest API.

**Two approval tracks exist in AI Maestro:**

| Track | Scope | Mechanism | Skill |
|-------|-------|-----------|-------|
| **Governance approvals** | Team membership, COS assignment, agent lifecycle, transfers | GovernanceRequest API (`POST /api/v1/governance/requests/{id}/approve`) | This skill (`amama-approval-workflows`) |
| **Operational approvals** | Deployments, merges, test runs, routine AMCOS operations | Message-based flow (`approval_request` / `approval_decision` messages) | `amama-amcos-coordination` skill |

Governance approvals use typed GovernanceRequest objects with a defined state machine. Operational approvals use the message-based flow described in `amama-amcos-coordination/references/message-formats.md`.

## Prerequisites

- AI Maestro v2+ with Governance API running at `$AIMAESTRO_API` (default: `http://localhost:23000`)
- Governance password must be set (see Governance Password Management below)
- AMAMA must have access to `docs_dev/handoffs/` directory
- State file must be writable for local approval tracking

## Governance Password Management

The governance password authenticates MANAGER approval/rejection actions. It is required before any GovernanceRequest can be approved or rejected.

### Initial Setup

Set the governance password on first use:

```bash
curl -X POST "$AIMAESTRO_API/api/governance/password" \
  -H "Content-Type: application/json" \
  -d '{"password": "<governance-password>"}'
```

- The password is bcrypt-hashed and stored in `~/.aimaestro/governance.json`
- To change the password, provide `currentPassword` and `password` in the request body

### Security Rules

- NEVER store the governance password in plaintext in any file, log, or message
- NEVER include the governance password in AI Maestro messages between agents
- The password is provided by the user at runtime or read from a secure environment variable
- **Rate limiting**: 5 failed attempts trigger a 60-second cooldown (`429 Too Many Requests`)

## Instructions

1. Poll or receive webhook notifications for GovernanceRequests with status `pending`
2. Parse the GovernanceRequest to determine its type
3. Present the request to the user (MANAGER) using the appropriate template
4. On user decision, call the approve or reject API endpoint with the governance password
5. Verify the status transition completed successfully
6. Update local approval state tracking
7. Notify the requesting agent of the outcome

## Plugin Prefix Reference

| Role | Prefix | Plugin Name |
|------|--------|-------------|
| Assistant Manager | `amama-` | AI Maestro Assistant Manager Agent |
| Architect | `amaa-` | AI Maestro Architect Agent |
| Orchestrator | `amoa-` | AI Maestro Orchestrator Agent |
| Integrator | `amia-` | AI Maestro Integrator Agent |

## GovernanceRequest State Machine

Every GovernanceRequest follows this state machine:

```
pending --> remote-approved --> dual-approved --> executed
   |               |
   |        pending --> local-approved --> dual-approved --> executed
   |
   +---> rejected
```

### States

| State | Description |
|-------|-------------|
| `pending` | Request created, awaiting approval |
| `remote-approved` | Approved by remote authority, awaiting MANAGER |
| `local-approved` | Approved by MANAGER, awaiting remote authority |
| `dual-approved` | Both local and remote approvals obtained |
| `executed` | The approved operation has been carried out |
| `rejected` | Request denied by MANAGER or auto-rejected |

### Transitions

- `pending` -> `remote-approved`: Remote authority approves first
- `pending` -> `local-approved`: MANAGER approves first
- `pending` -> `rejected`: MANAGER rejects, or auto-rejection (expiry)
- `remote-approved` -> `dual-approved`: MANAGER provides the second approval
- `local-approved` -> `dual-approved`: Remote authority provides the second approval
- `dual-approved` -> `executed`: The system executes the approved operation

## GovernanceRequest Types

Eight governance request types are supported: `add-to-team`, `remove-from-team`, `assign-cos`, `remove-cos`, `transfer-agent`, `create-agent`, `delete-agent`, `configure-agent`.

Each type has a specific payload schema and presentation template. See [references/governance-request-types.md](references/governance-request-types.md) for full details including payloads and MANAGER presentation templates.
  - Contents
  - add-to-team
  - remove-from-team
  - assign-cos
  - remove-cos

## GovernanceRequest API Endpoints

The API provides endpoints for listing, retrieving, approving, and rejecting GovernanceRequests, plus a dedicated transfer submission endpoint. See [references/api-endpoints.md](references/api-endpoints.md) for full endpoint documentation with curl examples.
  - List Pending Requests
  - Get a Specific Request
  - Approve a Request (MANAGER only)
  - Reject a Request (MANAGER only)
  - Submit a Transfer Request
  - Transfer Request Handling (M5)

**Key endpoints**:
- `GET /api/v1/governance/requests?status=pending` - List pending requests
- `GET /api/v1/governance/requests/{id}` - Get specific request
- `POST /api/v1/governance/requests/{id}/approve` - Approve (MANAGER only)
- `POST /api/v1/governance/requests/{id}/reject` - Reject (MANAGER only)
- `POST /api/governance/transfers` - Submit transfer request

## Legacy Approval Types

Five legacy approval types from v1 are supported for backward compatibility: push, merge, publish, security, and design. These use the standard AI Maestro messaging system rather than the GovernanceRequest API. See [references/legacy-approval-types.md](references/legacy-approval-types.md) for workflows and presentation templates.
  - Contents
  - Push Approval
  - Merge Approval
  - Publish Approval
  - Security Approval
  - Design Approval

## Approval State Tracking

All GovernanceRequests are tracked both in the API and in the local state file for redundancy:

```yaml
governance_requests:
  - id: "gov-{uuid}"
    type: "<request-type>"
    requested_by: "<agent-id>"
    requested_at: "ISO-8601"
    status: "pending" | "remote-approved" | "local-approved" | "dual-approved" | "executed" | "rejected"
    manager_decision: null | "approve" | "reject"
    decided_at: null | "ISO-8601"
    conditions: []
    notes: ""
    payload: {}

legacy_approvals:
  - id: "approval-{uuid}"
    type: "push" | "merge" | "publish" | "security" | "design"
    requested_by: "<role>"
    requested_at: "ISO-8601"
    status: "pending" | "approved" | "rejected"
    user_decision: null | "approve" | "reject" | "request_changes"
    decided_at: null | "ISO-8601"
    conditions: []
    notes: ""
```

## Escalation Rules

### Auto-Reject Conditions
- GovernanceRequest older than 24 hours without response
- Requesting agent session terminated
- Blocking security vulnerability detected
- Governance password rate-limit exceeded (requests queued until cooldown ends)

### Auto-Approve Conditions (NEVER by default)
- No auto-approve without explicit user configuration
- All governance requests require MANAGER decision

### Escalation Triggers
- Security-related GovernanceRequest (delete-agent, configure-agent with security changes)
- GovernanceRequest with "urgent" priority flag
- Multiple failed governance password attempts (potential breach)
- Transfer request contested by source team COS

## Approval Expiry Workflow

Requests pending longer than 24 hours are auto-rejected. The expiry check runs hourly. See [references/expiry-workflow.md](references/expiry-workflow.md) for the full expiry workflow, including API calls, state updates, notifications, and configuration options.
  - Expiry Check Schedule
  - Expiry Workflow Steps
  - Expiry Configuration

## User Notification

When a GovernanceRequest is created:
1. Display the request prominently with its type and payload summary
2. If user is idle, send periodic reminders
3. Block the requested operation until MANAGER decides
4. Log all requests and decisions to both the API and local state

## Examples

See [references/examples.md](references/examples.md) for complete worked examples including:
  - Example 1: Approving a Team Membership Request
  - Example 2: Handling a Transfer Request
  - Example 3: Rejecting a Dangerous Request

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid governance password | Prompt MANAGER to re-enter password |
| `429 Too Many Requests` | Rate limit exceeded (5 failed attempts) | Wait 60 seconds, then retry |
| `404 Not Found` | GovernanceRequest ID does not exist | Verify request ID; may be already processed |
| `409 Conflict` | Invalid state transition | Refresh request status and present current state |
| Governance password not set | `~/.aimaestro/governance.json` missing | Run initial password setup |
| Transfer contested | Source COS escalates objection | Present both sides to MANAGER |
| State file write failure | Permissions or disk issue | Retry 3 times, then escalate |

## Output

| Outcome | Status | Action |
|---------|--------|--------|
| MANAGER approves | `local-approved` or `dual-approved` | Call approve endpoint, update state, notify requesting agent |
| MANAGER rejects | `rejected` | Call reject endpoint, update state, notify requesting agent |
| MANAGER requests more info | `pending` (unchanged) | Query additional details, re-present to MANAGER |
| Timeout (24 hours) | `rejected` | Auto-reject via API, notify requesting agent |
| Rate limit hit | `pending` (unchanged) | Queue the action, wait for cooldown, then retry |

## Checklist

Copy this checklist and track your progress:

- [ ] Verify governance password is set
- [ ] Poll for pending GovernanceRequests via API
- [ ] Parse request type
- [ ] Present GovernanceRequest to MANAGER using appropriate template
- [ ] Wait for MANAGER decision
- [ ] Call approve or reject API endpoint with governance password
- [ ] Verify state transition completed
- [ ] Update local approval state tracking file
- [ ] Notify requesting agent of the outcome
- [ ] Log the request and decision to approval-log.md
- [ ] Handle errors, rate limits, and timeouts

## Resources

### Reference Documents

- [references/governance-request-types.md](references/governance-request-types.md) - All 8 GovernanceRequest types with payloads and templates
  - Contents
  - add-to-team
  - remove-from-team
  - assign-cos
  - remove-cos
- [references/api-endpoints.md](references/api-endpoints.md) - API endpoints with curl examples and transfer handling
  - List Pending Requests
  - Approve a Request (MANAGER only)
  - Submit a Transfer Request
- [references/legacy-approval-types.md](references/legacy-approval-types.md) - Legacy v1 approval workflows (push, merge, publish, security, design)
  - Contents
  - Push Approval
  - Merge Approval
  - Publish Approval
  - Security Approval
  - Design Approval
- [references/expiry-workflow.md](references/expiry-workflow.md) - Approval expiry workflow and configuration
  - Expiry Check Schedule
  - Expiry Workflow Steps
  - Expiry Configuration
- [references/examples.md](references/examples.md) - Worked examples of approval/rejection flows
  - Example 1: Approving a Team Membership Request
  - Example 2: Handling a Transfer Request
  - Example 3: Rejecting a Dangerous Request
- [references/rule-14-enforcement.md](references/rule-14-enforcement.md) - RULE 14: User Requirements Are Immutable
  - 1 When handling user requirements in any workflow
  - 2 When detecting potential requirement deviations
  - 3 When a technical constraint conflicts with a requirement
  - 4 When documenting requirement compliance
- [references/best-practices.md](references/best-practices.md) - Approval workflow best practices
  - 1. Always Verify Before Reporting
  - 2. Maintain Records Consistently
  - 3. Clear Communication with User
