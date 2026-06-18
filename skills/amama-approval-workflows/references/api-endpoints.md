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

See the `team-governance` skill for full API details.

## Get a Specific Request

```
aimaestro-governance.sh request <id>
```

See the `team-governance` skill for full API details.

## Approve a Request (MANAGER only)

```
aimaestro-governance.sh approve <id> [--approver <MANAGER-UUID>]
```

AID-authorized (R28) — no password. A cross-host approval is sudo-gated (USER/UI,
R32): surface it to the MAESTRO rather than supplying a password yourself.

**Response on success**: Status transitions to `local-approved` or `dual-approved` (if remote already approved).

See the `team-governance` skill for full API details.

## Reject a Request (MANAGER only)

```
aimaestro-governance.sh reject <id> [--rejector <MANAGER-UUID>] [--reason <rejection-reason>]
```

AID-authorized (R28) — no password.

**Response on success**: Status transitions to `rejected`. The operation is permanently blocked.

See the `team-governance` skill for full API details.

## Submit a Transfer Request

```
aimaestro-governance.sh transfer --agent <agent-uuid> --from-team <source-team-uuid> --to-team <destination-team-uuid> [--note <transfer-justification>]
```

**Response**: Creates a GovernanceRequest of type `transfer-agent` with status `pending`. Returns the request ID.

**Who can approve transfers**:
- MANAGER — AID-authorized (R28), via `aimaestro-governance.sh approve`
- COS of the destination team — via its portfolio mandate token (R28/R30)

See the `team-governance` skill for full API details.

## Transfer Request Handling (M5)

Transfer requests have special routing rules because they involve two teams.

### Transfer Workflow

1. **Request submitted** via `aimaestro-governance.sh transfer …`
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
