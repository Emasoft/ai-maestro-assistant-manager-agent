---
name: amama-approval-workflows
description: Use when handling governance approvals via GovernanceRequest API for team, agent lifecycle, and COS decisions. Trigger with approval requests.
version: 2.3.2
context: fork
agent: amama-assistant-manager-main-agent
---

# Approval Workflows Skill

## Overview

GovernanceRequest API workflows. Two tracks:
- **Governance** (this skill): Team, COS, agent lifecycle, transfers.
- **Operational** (`amama-amcos-coordination`): Deploys, merges, tests.

## Prerequisites

- AI Maestro v2+ at `$AIMAESTRO_API`
- Password set per references/governance-password.md
- Writable state file and `docs_dev/handoffs`

## Instructions

1. Poll pending (`GET /api/v1/governance/requests?status=pending`)
2. Parse type per references/governance-request-types.md
3. Present to MANAGER using template
4. Call approve/reject endpoint with password
5. Verify transition per references/state-machine.md
6. Update state per references/state-tracking.md
7. Notify requesting agent

Endpoints: references/api-endpoints.md

## Output

| Outcome | Action |
|---------|--------|
| Approve | Call approve, update, notify |
| Reject | Call reject, update, notify |
| Info needed | Query, re-present |
| Timeout 24h | Auto-reject per references/expiry-workflow.md |
| Rate limit | Queue, wait, retry |

## Error Handling

| Error | Fix |
|-------|-----|
| `401` | Re-enter password |
| `429` | Wait 60s, retry |
| `404` | Check request ID |
| `409` | Refresh status |
| No password | references/governance-password.md |

## Examples

**Input:** `POST /api/v1/governance/requests/{id}/approve` with `{"password":"***","approvedBy":"MANAGER","notes":"Approved after review"}`

**Output:** `{"status":"approved","updatedAt":"2026-03-08T10:00:00Z","approvedBy":"MANAGER"}`

See [references/examples.md](references/examples.md) for more.

Copy this checklist and track your progress:

- [ ] Verify password set
- [ ] Poll pending GovernanceRequests
- [ ] Parse type, present to MANAGER
- [ ] Wait for decision
- [ ] Call approve/reject endpoint
- [ ] Verify state transition
- [ ] Update state file, notify agent

## Resources

- [references/governance-request-types.md](references/governance-request-types.md) - Request types
  - 1. add-to-team, 2. remove-from-team, 3. assign-cos, 4. remove-cos
  - 5. transfer-agent, 6. create-agent, 7. delete-agent, 8. configure-agent
- [references/api-endpoints.md](references/api-endpoints.md) - API endpoints
  - List Pending Requests, Get a Specific Request
  - Approve a Request (MANAGER only), Reject a Request (MANAGER only)
  - Submit a Transfer Request, Transfer Request Handling (M5)
- [references/state-machine.md](references/state-machine.md) - State machine
  - States, Transitions, Plugin Prefix Reference
- [references/state-tracking.md](references/state-tracking.md) - State tracking
  - State File Schema, Proactive Monitoring
- [references/escalation-rules.md](references/escalation-rules.md) - Escalation
  - Auto-Reject Conditions, Auto-Approve Conditions (NEVER by default)
  - Escalation Triggers, User Notification, Workflow Checklist
- [references/governance-password.md](references/governance-password.md) - Password
  - Initial Setup, Security Rules
- [references/legacy-approval-types.md](references/legacy-approval-types.md) - Legacy v1
  - Push Approval, Merge Approval, Publish Approval
  - Security Approval, Design Approval
- [references/expiry-workflow.md](references/expiry-workflow.md) - Expiry
  - Expiry Check Schedule, Expiry Workflow Steps, Expiry Configuration
- [references/examples.md](references/examples.md) - Examples
  - Example 1: Approving a Team Membership Request
  - Example 2: Handling a Transfer Request, Example 3: Rejecting a Dangerous Request
- references/rule-14-enforcement.md - RULE 14: immutable user requirements
- [references/best-practices.md](references/best-practices.md) - Best practices
  - 1. Always Verify Before Reporting, 2. Maintain Records Consistently
  - 3. Clear Communication with User, 4. Risk-Aware Approval Decisions
  - 5. Scope Management, 6. Error Handling, 7. Timeliness
