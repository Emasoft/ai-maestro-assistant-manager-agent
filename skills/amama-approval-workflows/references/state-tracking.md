# Approval State Tracking Reference

## Table of Contents
- [State File Schema](#state-file-schema)
- [Proactive Monitoring](#proactive-monitoring)

All GovernanceRequests are tracked both server-side (the frozen `aimaestro-governance.sh` CLI authorizes via AID + portfolio token, R28 — no password) and in the local state file for redundancy.

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

operational_approvals:
  - id: "approval-{uuid}"
    type: "push" | "merge" | "publish" | "security" | "design"
    requested_by: "<team-title, via COS>"
    requested_at: "ISO-8601"
    status: "pending" | "approved" | "rejected"
    user_decision: null | "approve" | "reject" | "request_changes"
    decided_at: null | "ISO-8601"
    conditions: []
    notes: ""
```

## Proactive Monitoring

- Poll every 60 seconds during active sessions, but keep the poll cheap — redirect the full
  listing to a scratch file (`aimaestro-governance.sh requests --status pending > /tmp/amama-pending.json`)
  and surface only a count + the request ids (`<N> pending, ids:[…]`), never the raw payloads.
  Fetch a full record (`aimaestro-governance.sh request <id>`) only when about to act on one.
- Present pending requests to user with context and recommended action
- Auto-escalate requests older than 10 minutes to urgent priority
