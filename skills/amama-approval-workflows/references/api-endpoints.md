# GovernanceRequest API Endpoints Reference

## Contents

- [List Pending Requests](#list-pending-requests)
- [Get a Specific Request](#get-a-specific-request)
- [Approve a Request (MANAGER only)](#approve-a-request-manager-only)
- [Reject a Request (MANAGER only)](#reject-a-request-manager-only)
- [Submit a Transfer Request](#submit-a-transfer-request)
- [Transfer Request Handling (M5)](#transfer-request-handling-m5)

## List Pending Requests

```
GET $AIMAESTRO_API/api/v1/governance/requests?status=pending
```

See the `team-governance` skill for full API details.

## Get a Specific Request

```
GET $AIMAESTRO_API/api/v1/governance/requests/{id}
```

See the `team-governance` skill for full API details.

## Approve a Request (MANAGER only)

```
POST $AIMAESTRO_API/api/v1/governance/requests/{id}/approve
Body: {
  "password": "<governance-password>",
  "approvedBy": "MANAGER",
  "conditions": [],
  "notes": "<optional-notes>"
}
```

**Response on success**: Status transitions to `local-approved` or `dual-approved` (if remote already approved).

See the `team-governance` skill for full API details.

## Reject a Request (MANAGER only)

```
POST $AIMAESTRO_API/api/v1/governance/requests/{id}/reject
Body: {
  "password": "<governance-password>",
  "rejectedBy": "MANAGER",
  "reason": "<rejection-reason>"
}
```

**Response on success**: Status transitions to `rejected`. The operation is permanently blocked.

See the `team-governance` skill for full API details.

## Submit a Transfer Request

```
POST $AIMAESTRO_API/api/v1/governance/transfers
Body: {
  "agentId": "<agent-uuid>",
  "fromTeamId": "<source-team-uuid>",
  "toTeamId": "<destination-team-uuid>",
  "note": "<transfer-justification>"
}
```

**Response**: Creates a GovernanceRequest of type `transfer-agent` with status `pending`. Returns the request ID.

**Who can approve transfers**:
- MANAGER (via governance password)
- COS of the destination team (via their authority token)

See the `team-governance` skill for full API details.

## Transfer Request Handling (M5)

Transfer requests have special routing rules because they involve two teams.

### Transfer Workflow

1. **Request submitted** via `POST /api/v1/governance/transfers`
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
