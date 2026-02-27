# Approval Workflow Examples

## Example 1: Approving a Team Membership Request

```bash
# 1. Poll for pending requests
curl -s "$AIMAESTRO_API/api/v1/governance/requests?status=pending"

# Response includes:
# {
#   "id": "gov-abc123",
#   "type": "add-to-team",
#   "status": "pending",
#   "payload": {
#     "agentId": "agent-007",
#     "teamId": "team-alpha",
#     "role": "developer",
#     "reason": "Needed for sprint 42 capacity"
#   }
# }

# 2. Present to MANAGER (user)
## Governance Request: Add Agent to Team
**Request ID**: gov-abc123
**Type**: add-to-team
**Agent**: agent-007 (CodeBot)
**Team**: team-alpha (Alpha Squad)
**Role**: developer
**Reason**: Needed for sprint 42 capacity

# 3. MANAGER approves
curl -X POST "$AIMAESTRO_API/api/v1/governance/requests/gov-abc123/approve" \
  -H "Content-Type: application/json" \
  -d '{"password": "***", "approvedBy": "MANAGER", "notes": "Approved for sprint 42"}'

# Response: {"id": "gov-abc123", "status": "local-approved", ...}
```

## Example 2: Handling a Transfer Request

```bash
# 1. Transfer request arrives
curl -s "$AIMAESTRO_API/api/v1/governance/requests/gov-def456"

# {
#   "id": "gov-def456",
#   "type": "transfer-agent",
#   "status": "remote-approved",  <-- destination COS already approved
#   "payload": {
#     "agentId": "agent-042",
#     "fromTeamId": "team-beta",
#     "toTeamId": "team-gamma",
#     "note": "Agent expertise better suited for gamma's mission"
#   }
# }

# 2. Present to MANAGER -- note that destination COS already approved
## Governance Request: Transfer Agent
**Request ID**: gov-def456
**Status**: remote-approved (destination COS approved)
**Agent**: agent-042 (DataProcessor)
**From**: team-beta -> **To**: team-gamma
**Note**: Agent expertise better suited for gamma's mission

# 3. MANAGER approves -> transitions to dual-approved -> executed
curl -X POST "$AIMAESTRO_API/api/v1/governance/requests/gov-def456/approve" \
  -H "Content-Type: application/json" \
  -d '{"password": "***", "approvedBy": "MANAGER"}'

# Response: {"id": "gov-def456", "status": "dual-approved", ...}
# System auto-executes the transfer -> status becomes "executed"
```

## Example 3: Rejecting a Dangerous Request

```bash
# 1. Delete-agent request arrives
# {
#   "id": "gov-ghi789",
#   "type": "delete-agent",
#   "status": "pending",
#   "payload": {
#     "agentId": "agent-001",
#     "reason": "Agent no longer needed"
#   }
# }

# 2. MANAGER rejects
curl -X POST "$AIMAESTRO_API/api/v1/governance/requests/gov-ghi789/reject" \
  -H "Content-Type: application/json" \
  -d '{"password": "***", "rejectedBy": "MANAGER", "reason": "Agent-001 is still critical for monitoring"}'

# Response: {"id": "gov-ghi789", "status": "rejected", ...}
```
