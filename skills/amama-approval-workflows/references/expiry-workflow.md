# Approval Expiry Workflow Reference

## Contents

- [Expiry Check Schedule](#expiry-check-schedule)
- [Expiry Workflow Steps](#expiry-workflow-steps)
- [Expiry Configuration](#expiry-configuration)

GovernanceRequests that remain pending for too long are automatically rejected to prevent stale requests from blocking workflows.

## Expiry Check Schedule

Check GovernanceRequest timestamps every hour to identify expired requests. Redirect the
pending listing to a scratch file, then filter client-side on `requested_at` and surface
only the count + the ids that ARE expired — not the full listing:

```
aimaestro-governance.sh requests --status pending > /tmp/amama-pending.json
# from the file, keep only entries whose requested_at is >24h old; report "<N> expired, ids:[…]"
```

The 24h age cutoff is applied **client-side**: the CLI has no server-side `olderThan`
filter, so list with `requests --status pending` and filter the result by `requested_at`.

See the `team-governance` skill for full CLI details.

## Expiry Workflow Steps

**Step 1: Identify Expired Requests**

Every hour, query for GovernanceRequests where:
- `status` is `pending`, `remote-approved`, or `local-approved`
- `requested_at` is more than 24 hours ago

**Step 2: Auto-Reject Expired Requests**

For each expired GovernanceRequest:

1. **Reject via CLI** (AID-authorized, R28 — no password)
   ```
   aimaestro-governance.sh reject <id> --reason "EXPIRED: Request pending for more than 24 hours without dual-approval"
   ```

2. **Update local state file**
   ```yaml
   governance_requests:
     - id: "gov-{uuid}"
       status: "rejected"
       manager_decision: "auto-rejected"
       decided_at: "<current-ISO-8601>"
       notes: "EXPIRED: Auto-rejected after 24 hours without response"
   ```

3. **Notify requesting agent** via AI Maestro messaging:
   - **Subject**: "GovernanceRequest Expired: {id}"
   - **Content**: type `governance_decision`, request_id, decision `rejected`, reason `EXPIRED`
   - **Priority**: `normal`

4. **Log to approval-log.md**
   ```markdown
   ## GOV-<ID> - EXPIRED

   - **Request ID**: <REQUEST-ID>
   - **Type**: <governance-request-type>
   - **From**: <requesting-agent>
   - **Requested**: <requested_at>
   - **Expired**: <current-timestamp>
   - **Decision**: REJECTED (EXPIRED)
   - **Reason**: Auto-rejected after 24 hours without dual-approval
   ```

**Step 3: Notify MANAGER of Expirations (Optional)**

If user preference is set to receive expiry notifications:
```
GovernanceRequests Expired

The following governance requests were auto-rejected after 24 hours:

- GOV-<ID-1>: <type> - <summary> (from <agent>)
- GOV-<ID-2>: <type> - <summary> (from <agent>)

These requests have been returned to the requesting agents. They can resubmit if still needed.
```

## Expiry Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `expiry_threshold_hours` | 24 | Hours before auto-reject |
| `expiry_check_interval_minutes` | 60 | How often to check for expired |
| `notify_user_on_expiry` | false | Send summary to MANAGER on expiry |
| `allow_resubmission` | true | Requesting agent can resubmit after expiry |
