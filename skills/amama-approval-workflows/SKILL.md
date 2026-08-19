---
name: amama-approval-workflows
description: Use when handling governance approvals via GovernanceRequest API for team, agent lifecycle, and COS decisions. Trigger with approval requests.
context: fork
background: false
user-invocable: false
agent: ai-maestro-assistant-manager-agent-main-agent
---

# Approval Workflows Skill

> **Never call the ai-maestro server API directly.** No skill, agent, command, hook, MCP config, bundled script, or setting may issue a request to `/api/…`, nor instruct an agent to (R23.1). Every server interaction goes through the frozen CLI layer installed with ai-maestro — `~/.local/bin/aimaestro-*.sh`, `amp-*.sh`, `aid-*.sh` (R23.2).
>
> Two independent reasons, and either alone invites a workaround:
> 1. **The CLI runs the pipeline, governance and audit gates that a raw route bypasses.** A direct call is *unaudited even when it works* — it succeeds and leaves no trace in the ledgers the fleet is governed by.
> 2. **Server routes are renameable; the CLI interface is frozen** (R23.4). Route-coupled code breaks silently on a server release, and the breakage surfaces as an agent that has quietly stopped working.
>
> There is **no element-level exception — not even for the core `ai-maestro-plugin`** (R23.5). The boundary is the script layer, not any particular plugin.

## Overview

GovernanceRequest API workflows. Two tracks:
- **Governance** (this skill): Team, COS, agent lifecycle, transfers.
- **Operational** (`amama-amcos-coordination`): Deploys, merges, tests.

**Tier ladder:** these approvals sit on the canonical required-permissions ladder in
`~/.claude/rules/trdd-design-tasks.md` + the seeded `.claude/rules/aimaestro-trdd-approval.md` (Tier 0 agent-independent → 1 COS → 2 MANAGER →
3 USER/MAESTRO; operationalized by the `amama-proposal-approvals` skill). A request only the
user can grant is **Tier 3 = escalate-to-MAESTRO**.

## Prerequisites

- AI Maestro v2+ reachable via the frozen `aimaestro-governance.sh` CLI
- `$AID_AUTH` present — the CLI resolves it internally. The SERVER runs the
  3-check authz (R28): AID identity → MANAGER title → the approval/mandate token
  in your portfolio enclave. You NEVER supply a governance/sudo password (R32) —
  see references/governance-password.md
- Writable state file and `docs_dev/handoffs`

## Instructions

1. Poll pending (`aimaestro-governance.sh requests --status pending > /tmp/amama-pending.json`); surface only count + ids; the full record is already in that JSON — filter it with `jq '.[] | select(.id == "<id>")'` (there is no per-id fetch verb)
2. Parse type per references/governance-request-types.md
3. Present to MANAGER using template
4. Route by request kind:
   - **TRDD approvals** (proposal → planned, refusals): `aimaestro-trdd.sh approve <trdd-id> --approver <who> --rationale <r>` / `aimaestro-trdd.sh refuse <trdd-id> --reason <r>` — AID-authorized (R28); approving mints the portfolio token that `aimaestro-trdd.sh verify` checks.
   - **GovernanceRequests** (team / agent lifecycle, COS, titles): `aimaestro-governance.sh approve|reject` is **password-gated by design** — the governance password is USER authority and never passes through a model (R32). Record your verdict, then surface the request to the MAESTRO to action via the UI or their logged-in CLI session; do NOT supply a password yourself.
   - **Team transfers**: `aimaestro-governance.sh transfer resolve <transferId> --action approve|reject` (MANAGER or destination-COS authority).
5. Verify transition per references/state-machine.md (TRDDs: `aimaestro-trdd.sh verify <id>`)
6. Update state per references/state-tracking.md
7. Notify requesting agent

## Output

| Outcome | Action |
|---------|--------|
| Approve | TRDD: `aimaestro-trdd.sh approve`; GovernanceRequest: verdict + surface to MAESTRO; update, notify |
| Reject | TRDD: `aimaestro-trdd.sh refuse --reason`; GovernanceRequest: verdict + surface to MAESTRO; update, notify |
| Info needed | Query, re-present |
| Timeout 24h | Auto-reject per expiry-workflow |
| Rate limit | Queue, wait, retry |
| Server unreachable (CLI exits non-zero) | Do NOT stall silently: record the verdict in the TRDD's `## Approval log` (the corpus is offline-writable; `trddgrep` still works), queue the `aimaestro-trdd.sh approve` token mint for retry, and surface the outage to the MAESTRO in the same breath |

## Error Handling

| Error | Fix |
|-------|-----|
| `401` | `$AID_AUTH` missing/invalid — stop, surface it; never fall back to unauthenticated calls |
| `403` | Op needs more than the MANAGER title (sudo-gated / cross-host) — surface to the MAESTRO via UI (R32) |
| `429` | Wait 60s, retry |
| `404` | Check request ID |
| `409` | Refresh status |

## Examples

**Input (TRDD approval):** `aimaestro-trdd.sh approve <trdd-id> --approver MANAGER --rationale "<r>"` (AID-authorized, R28)

**Input (GovernanceRequest, actioned by the MAESTRO):** `aimaestro-governance.sh approve <id> --password <P> [--approver <MANAGER-UUID>]` — password = USER authority; never supplied by an agent (R32)

**Output:** `{"status":"approved","updatedAt":"2026-03-08T10:00:00Z","approvedBy":"MANAGER"}`

See [references/examples.md](references/examples.md) for more.

Copy this checklist and track your progress:

- [ ] Verify `$AID_AUTH` present (server runs the 3-check authz, R28)
- [ ] Poll pending GovernanceRequests (`aimaestro-governance.sh requests --status pending > <file>`; surface only count + ids)
- [ ] Parse type, present to MANAGER
- [ ] Wait for decision
- [ ] Execute the verdict: TRDD → `aimaestro-trdd.sh approve|refuse` (AID-authorized, R28); GovernanceRequest → surface to MAESTRO (password-gated, R32); transfer → `aimaestro-governance.sh transfer resolve`
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
