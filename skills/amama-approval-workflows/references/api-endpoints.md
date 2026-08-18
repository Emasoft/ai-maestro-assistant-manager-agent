# GovernanceRequest CLI Reference

All governance operations route through the frozen `aimaestro-governance.sh`
CLI (R23). The CLI resolves AID auth internally — no `Authorization` header is
ever passed by hand. The SERVER runs the 3-check authz on every call (R28): it
verifies your AID identity, the MANAGER title bound to it, and the required
approval/mandate token in your portfolio enclave. You NEVER assert your own
title and NEVER supply a governance/sudo password (R32). The deployed CLI still
exposes a `--password` flag — that is a USER/UI residual; AMAMA does not pass it.
For a sudo-gated / cross-host request, surface the operation to the MAESTRO to
action via the UI.

## Contents

- [List Pending Requests](#list-pending-requests)
- [Get a Specific Request](#get-a-specific-request)
- [Approve a Request (MANAGER only)](#approve-a-request-manager-only)
- [Reject a Request (MANAGER only)](#reject-a-request-manager-only)
- [Submit a Transfer Request](#submit-a-transfer-request)
- [Transfer Request Handling (M5)](#transfer-request-handling-m5)

## List Pending Requests

```
aimaestro-governance.sh requests --status pending
```

To keep the poll cheap, redirect the listing to a scratch file
(`aimaestro-governance.sh requests --status pending > /tmp/amama-pending.json`) and surface
only the count + request ids; fetch a full record with `request <id>` only when acting on one.

See the `team-governance` skill for full API details.

## Get a Specific Request

```
aimaestro-governance.sh request <id>
```

See the `team-governance` skill for full API details.

## Approve a Request (password-gated — MAESTRO actions it)

```
aimaestro-governance.sh approve <id> --password <P> [--approver <MANAGER-UUID>]
```

`--password` is REQUIRED by the CLI and is USER authority — it never passes through a
model (R32). The MANAGER records its verdict and surfaces the request to the MAESTRO to
action via the UI or a logged-in CLI session. For **TRDD** approvals (the MANAGER's own
R28 path) use `aimaestro-trdd.sh approve <trdd-id> --approver W --rationale R` instead —
AID-authorized, no password, mints the portfolio token `aimaestro-trdd.sh verify` checks.

**Response on success**: Status transitions to `local-approved` or `dual-approved` (if remote already approved).

See the `team-governance` skill for full API details.

## Reject a Request (password-gated — MAESTRO actions it)

```
aimaestro-governance.sh reject <id> --password <P> [--rejector <MANAGER-UUID>] [--reason <rejection-reason>]
```

Password-gated like approve (R32). TRDD refusals use `aimaestro-trdd.sh refuse <trdd-id> --reason R` — AID-authorized, `--reason` required.

**Response on success**: Status transitions to `rejected`. The operation is permanently blocked.

See the `team-governance` skill for full API details.

## Submit a Transfer Request

```
aimaestro-governance.sh transfer create --agent <agent-uuid> --from-team <source-team-uuid> --to-team <destination-team-uuid> [--note <transfer-justification>]
```

**Response**: Creates a GovernanceRequest of type `transfer-agent` with status `pending`. Returns the request ID.

**Who can approve transfers**:
- MANAGER — via `aimaestro-governance.sh transfer resolve <transferId> --action approve|reject [--reject-reason TEXT]`
- COS of the destination team — same `transfer resolve` route, authorized by its portfolio mandate token (R28/R30)

List pending transfers first: `aimaestro-governance.sh transfer list [--team ID] [--agent ID] [--status S]`.

See the `team-governance` skill for full API details.

## Transfer Request Handling (M5)

Transfer requests have special routing rules because they involve two teams.

### Transfer Workflow

1. **Request submitted** via `aimaestro-governance.sh transfer create …`
2. A GovernanceRequest of type `transfer-agent` is created with status `pending`
3. **Notifications sent** to:
   - MANAGER (AMAMA) for governance approval
   - COS of the destination team for domain approval
4. **Either** MANAGER or destination COS can approve:
   - If MANAGER approves: request moves to `local-approved`, awaiting remote (destination COS) confirmation, OR directly to `dual-approved` if COS already approved
   - If destination COS approves: request moves to `remote-approved`, awaiting MANAGER confirmation, OR directly to `dual-approved` if MANAGER already approved
5. **On dual-approved**: The transfer is executed automatically
6. **On rejected**: by either party, the transfer is cancelled

### Transfer Conflict Resolution

- If the source team COS objects, they can escalate to MANAGER
- If MANAGER and destination COS disagree, MANAGER's decision takes precedence
- Transfers that remain pending for more than 24 hours are auto-rejected
