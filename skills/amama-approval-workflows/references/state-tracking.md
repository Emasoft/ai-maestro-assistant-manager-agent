# Approval State Tracking Reference

## Table of Contents
- [State File Schema](#state-file-schema)
- [Proactive Monitoring](#proactive-monitoring)

All GovernanceRequests are tracked both in the API and in the local state file for redundancy.

## State File Schema

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

## Proactive Monitoring

- Poll `GET /api/v1/governance/requests?status=pending` every 60 seconds during active sessions
- Present pending requests to user with context and recommended action
- Auto-escalate requests older than 10 minutes to urgent priority
