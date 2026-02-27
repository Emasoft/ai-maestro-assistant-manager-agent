# GovernanceRequest API Endpoints Reference

## List Pending Requests

```bash
curl -s "$AIMAESTRO_API/api/v1/governance/requests?status=pending" \
  -H "Content-Type: application/json"
```

## Get a Specific Request

```bash
curl -s "$AIMAESTRO_API/api/v1/governance/requests/{id}" \
  -H "Content-Type: application/json"
```

## Approve a Request (MANAGER only)

```bash
curl -X POST "$AIMAESTRO_API/api/v1/governance/requests/{id}/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "<governance-password>",
    "approvedBy": "MANAGER",
    "conditions": [],
    "notes": "<optional-notes>"
  }'
```

**Response on success**: Status transitions to `local-approved` or `dual-approved` (if remote already approved).

## Reject a Request (MANAGER only)

```bash
curl -X POST "$AIMAESTRO_API/api/v1/governance/requests/{id}/reject" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "<governance-password>",
    "rejectedBy": "MANAGER",
    "reason": "<rejection-reason>"
  }'
```

**Response on success**: Status transitions to `rejected`. The operation is permanently blocked.

## Submit a Transfer Request

```bash
curl -X POST "$AIMAESTRO_API/api/governance/transfers" \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "<agent-uuid>",
    "fromTeamId": "<source-team-uuid>",
    "toTeamId": "<destination-team-uuid>",
    "note": "<transfer-justification>"
  }'
```

**Response**: Creates a GovernanceRequest of type `transfer-agent` with status `pending`. Returns the request ID.

**Who can approve transfers**:
- MANAGER (via governance password)
- COS of the destination team (via their authority token)

## Transfer Request Handling (M5)

Transfer requests have special routing rules because they involve two teams.

### Transfer Workflow

1. **Request submitted** via `POST /api/governance/transfers`
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
