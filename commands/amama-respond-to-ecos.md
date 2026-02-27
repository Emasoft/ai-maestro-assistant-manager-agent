---
name: eama-respond-to-ecos
description: "Respond to pending ECOS approval requests with approve, reject, or needs-revision decision"
argument-hint: "--request-id <id> --decision <approved|rejected|needs-revision> [--comment <text>]"
allowed-tools: ["Read", "Write"]
---

# Respond to ECOS Command

Respond to pending Chief of Staff (ECOS) approval requests with a decision.

## Usage

```
/eama-respond-to-ecos --request-id <request_id> --decision <decision> [--comment <text>]
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--request-id` | Yes | The ECOS request ID to respond to (format: `ecos-req-{uuid}`) |
| `--decision` | Yes | Decision: `approved`, `rejected`, or `needs-revision` |
| `--comment` | No | Optional explanation or conditions for the decision |

## Decision Values

| Decision | Effect | When to Use |
|----------|--------|-------------|
| `approved` | ECOS proceeds with the operation | Operation is safe and aligned with goals |
| `rejected` | ECOS cancels the operation | Operation is inappropriate or risky |
| `needs-revision` | ECOS must modify and resubmit | Operation concept is okay but details need adjustment |

## What This Command Does

1. **Validates Request ID**
   - Checks that the request ID exists in pending requests
   - Retrieves the original request details

2. **Validates Decision**
   - Ensures decision is one of the valid options
   - For `needs-revision`, requires comment explaining what to change

3. **Sends Response via AI Maestro**
   - Formats response message according to ECOS protocol
   - Sends to ECOS via AI Maestro messaging

4. **Updates State Tracking**
   - Records decision with timestamp
   - Logs for audit trail

5. **Outputs Confirmation**
   - Shows what was sent
   - Confirms delivery status

## Examples

### Approve an Operation

```
/eama-respond-to-ecos --request-id ecos-req-a1b2c3d4 --decision approved --comment "Proceed with staging deployment"
```

Output:
```
Response sent to ECOS

Request ID: ecos-req-a1b2c3d4
Decision: APPROVED
Comment: Proceed with staging deployment
Sent at: 2025-02-02T14:32:00Z

ECOS will now proceed with the operation.
```

### Reject an Operation

```
/eama-respond-to-ecos --request-id ecos-req-x9y8z7 --decision rejected --comment "Too risky before weekend - defer to Monday"
```

Output:
```
Response sent to ECOS

Request ID: ecos-req-x9y8z7
Decision: REJECTED
Comment: Too risky before weekend - defer to Monday
Sent at: 2025-02-02T14:35:00Z

ECOS will cancel the operation.
```

### Request Revision

```
/eama-respond-to-ecos --request-id ecos-req-m4n5o6 --decision needs-revision --comment "Reduce scope to only feature/* branches, exclude main"
```

Output:
```
Response sent to ECOS

Request ID: ecos-req-m4n5o6
Decision: NEEDS REVISION
Comment: Reduce scope to only feature/* branches, exclude main
Sent at: 2025-02-02T14:40:00Z

ECOS will revise the request and resubmit.
```

## Listing Pending Requests

Before responding, you may want to see pending requests.

Check your inbox using the `agent-messaging` skill. Filter for messages from ECOS-prefixed senders to find approval requests.

**Verify**: confirm you have reviewed all unread ECOS messages before proceeding.

## Message Format Sent

The command sends an approval response to ECOS using the `agent-messaging` skill:

- **Recipient**: `ecos-<project-name>`
- **Subject**: "EAMA Approval Response: <request_id>"
- **Priority**: `high`
- **Content**: Include the following fields:
  - `type`: `approval-response`
  - `request_id`: The request ID being responded to
  - `decision`: The decision value (`approved`, `rejected`, or `needs-revision`)
  - `comment`: The optional comment text
  - `conditions`: List of conditions (empty list if none)
  - `responded_at`: ISO-8601 timestamp of the response

**Verify**: confirm message delivery via the `agent-messaging` skill's sent messages feature.

## Error Conditions

| Error | Cause | Solution |
|-------|-------|----------|
| `Request ID not found` | Invalid or already-responded request ID | Check pending requests list |
| `Invalid decision value` | Decision not one of allowed values | Use: approved, rejected, needs-revision |
| `needs-revision requires comment` | Missing comment for revision request | Add --comment explaining what to change |
| `AI Maestro unavailable` | Messaging system not running | Start AI Maestro service |
| `ECOS not registered` | ECOS agent not in AI Maestro registry | Register ECOS agent |

## Prerequisites

1. **AI Maestro must be running**
   Verify AI Maestro health using the `agent-messaging` skill's health check feature.

2. **ECOS must be registered**
   Use the `ai-maestro-agents-management` skill to list agents and confirm an ECOS agent is registered and active.

3. **Pending request must exist**
   Check your inbox using the `agent-messaging` skill and filter for unread ECOS messages.

## Related Commands

- `/eama-orchestration-status` - View pending ECOS requests in status report
- `/eama-configure-ecos-delegation` - Configure autonomous operation rules
- `/eama-approve-plan` - Approve plans (separate from ECOS approval flow)

## Related Skills

- **eama-ecos-coordination**
- **eama-approval-workflows**
