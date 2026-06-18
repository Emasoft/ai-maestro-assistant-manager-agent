---
name: amama-approval-workflows
description: Use when handling governance approvals via GovernanceRequest API for team, agent lifecycle, and COS decisions. Trigger with approval requests.
context: fork
agent: amama-assistant-manager-main-agent
---

# Approval Workflows Skill

## Overview

GovernanceRequest API workflows. Two tracks:
- **Governance** (this skill): Team, COS, agent lifecycle, transfers.
- **Operational** (`amama-amcos-coordination`): Deploys, merges, tests.

## Prerequisites

- AI Maestro v2+ reachable via the frozen `aimaestro-governance.sh` CLI
- `$AID_AUTH` present — the CLI resolves it internally. The SERVER runs the
  3-check authz (R28): AID identity → MANAGER title → the approval/mandate token
  in your portfolio enclave. You NEVER supply a governance/sudo password (R32) —
  see references/governance-password.md
- Writable state file and `docs_dev/handoffs`

## Instructions

1. Poll pending (`aimaestro-governance.sh requests --status pending`)
2. Parse type per references/governance-request-types.md
3. Present to MANAGER using template
4. Call `aimaestro-governance.sh approve`/`reject` — AID-authorized (R28). For a
   cross-host / sudo-gated request, surface it to the MAESTRO to action via the UI
   (R32); do NOT supply a password yourself
5. Verify transition per references/state-machine.md
6. Update state per references/state-tracking.md
7. Notify requesting agent

## Output

| Outcome | Action |
|---------|--------|
| Approve | Call approve, update, notify |
| Reject | Call reject, update, notify |
| Info needed | Query, re-present |
| Timeout 24h | Auto-reject per expiry-workflow |
| Rate limit | Queue, wait, retry |

## Error Handling

| Error | Fix |
|-------|-----|
| `401` | `$AID_AUTH` missing/invalid — stop, surface it; never fall back to unauthenticated calls |
| `403` | Op needs more than the MANAGER title (sudo-gated / cross-host) — surface to the MAESTRO via UI (R32) |
| `429` | Wait 60s, retry |
| `404` | Check request ID |
| `409` | Refresh status |

## Examples

**Input:** `aimaestro-governance.sh approve <id> [--approver <MANAGER-UUID>]` (AID-authorized, R28)

**Output:** `{"status":"approved","updatedAt":"2026-03-08T10:00:00Z","approvedBy":"MANAGER"}`

See [references/examples.md](references/examples.md) for more.

Copy this checklist and track your progress:

- [ ] Verify `$AID_AUTH` present (server runs the 3-check authz, R28)
- [ ] Poll pending GovernanceRequests (`aimaestro-governance.sh requests --status pending`)
- [ ] Parse type, present to MANAGER
- [ ] Wait for decision
- [ ] Call `aimaestro-governance.sh approve`/`reject` (AID-authorized; sudo-gated → surface to MAESTRO, R32)
- [ ] Verify state transition
- [ ] Update state file, notify agent

## Resources

- [references/governance-request-types.md](references/governance-request-types.md) - Request types
  - add-to-team, remove-from-team, assign-cos (MANAGER, R29), remove-cos (MANAGER, R29), transfer-agent, create-agent, delete-agent, configure-agent
- [references/api-endpoints.md](references/api-endpoints.md) - API endpoints
  - List Pending Requests, Get a Specific Request, Approve a Request (MANAGER only)
  - Reject a Request (MANAGER only), Submit a Transfer Request, Transfer Request Handling (M5)
- [references/state-machine.md](references/state-machine.md) - State machine
  - States, Transitions, Plugin Prefix Reference
- [references/state-tracking.md](references/state-tracking.md) - State tracking
  - State File Schema, Proactive Monitoring
- [references/escalation-rules.md](references/escalation-rules.md) - Escalation
  - Auto-Reject Conditions, Auto-Approve Conditions (NEVER by default)
  - Escalation Triggers, User Notification, Workflow Checklist
- [references/governance-password.md](references/governance-password.md) - Password is USER/UI-only (R32)
  - Who uses it, Security Rules
- [references/legacy-approval-types.md](references/legacy-approval-types.md) - Operational approvals (messaging-based)
  - Push Approval, Merge Approval, Publish Approval, Security Approval, Design Approval — routed to the team's COS
- [references/expiry-workflow.md](references/expiry-workflow.md) - Expiry
  - Expiry Check Schedule, Expiry Workflow Steps, Expiry Configuration
- [references/examples.md](references/examples.md) - Examples
  - Example 1: Approving a Team Membership Request
  - Example 2: Handling a Transfer Request, Example 3: Rejecting a Dangerous Request
- references/rule-14-enforcement.md - RULE 14: immutable user requirements
- [references/best-practices.md](references/best-practices.md) - Best practices
  - Always Verify Before Reporting, Maintain Records Consistently, Clear Communication with User
  - Risk-Aware Approval Decisions, Scope Management, Error Handling, Timeliness
