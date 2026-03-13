# Approval Workflow Examples

## Contents

- [Example 1: Approving a Team Membership Request](#example-1-approving-a-team-membership-request)
- [Example 2: Handling a Transfer Request](#example-2-handling-a-transfer-request)
- [Example 3: Rejecting a Dangerous Request](#example-3-rejecting-a-dangerous-request)

## Example 1: Approving a Team Membership Request

```
# 1. Poll for pending requests
GET $AIMAESTRO_API/api/v1/governance/requests?status=pending

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
POST $AIMAESTRO_API/api/v1/governance/requests/gov-abc123/approve
Body: {"password": "***", "approvedBy": "MANAGER", "notes": "Approved for sprint 42"}

# Response: {"id": "gov-abc123", "status": "local-approved", ...}
```

See the `team-governance` skill for full API details.

## Example 2: Handling a Transfer Request

```
# 1. Transfer request arrives
GET $AIMAESTRO_API/api/v1/governance/requests/gov-def456

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
POST $AIMAESTRO_API/api/v1/governance/requests/gov-def456/approve
Body: {"password": "***", "approvedBy": "MANAGER"}

# Response: {"id": "gov-def456", "status": "dual-approved", ...}
# System auto-executes the transfer -> status becomes "executed"
```

See the `team-governance` skill for full API details.

## Example 3: Rejecting a Dangerous Request

```
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
POST $AIMAESTRO_API/api/v1/governance/requests/gov-ghi789/reject
Body: {"password": "***", "rejectedBy": "MANAGER", "reason": "Agent-001 is still critical for monitoring"}

# Response: {"id": "gov-ghi789", "status": "rejected", ...}
```

See the `team-governance` skill for full API details.
