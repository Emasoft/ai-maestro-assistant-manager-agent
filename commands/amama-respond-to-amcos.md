---
name: amama-respond-to-amcos
description: "Respond to pending AMCOS approval requests with approve, deny, or defer decision"
argument-hint: "--request-id <id> --decision <approve|deny|defer> [--comment <text>]"
allowed-tools: ["Read", "Write", "Bash"]
---

# Respond to AMCOS Command

Respond to pending Chief of Staff (AMCOS) approval requests with a decision.

> **Never call the ai-maestro server API directly.** No skill, agent, command, hook, MCP config, bundled script, or setting may issue a request to `/api/…`, nor instruct an agent to (R23.1). Every server interaction goes through the frozen CLI layer installed with ai-maestro — `~/.local/bin/aimaestro-*.sh`, `amp-*.sh`, `aid-*.sh` (R23.2).
>
> Two independent reasons, and either alone invites a workaround:
> 1. **The CLI runs the pipeline, governance and audit gates that a raw route bypasses.** A direct call is *unaudited even when it works* — it succeeds and leaves no trace in the ledgers the fleet is governed by.
> 2. **Server routes are renameable; the CLI interface is frozen** (R23.4). Route-coupled code breaks silently on a server release, and the breakage surfaces as an agent that has quietly stopped working.
>
> There is **no element-level exception — not even for the core `ai-maestro-plugin`** (R23.5). The boundary is the script layer, not any particular plugin.

This command carries the clause and its three siblings do not, on purpose. They pin `allowed-tools` to a single script (`Bash(python3 …amama_<x>.py:*)`), which confines them structurally — a stronger guarantee than prose. This one holds **unrestricted `Bash`** on an inter-agent approval flow, so it is the one surface here that both *could* issue a raw route and has a plausible reason to reach for one. Pasting the block into the confined three would make the rule furniture: present everywhere, read nowhere.

## Usage

```
/amama-respond-to-amcos --request-id <request_id> --decision <decision> [--comment <text>]
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--request-id` | Yes | The AMCOS request ID to respond to (format: `amcos-req-{uuid}`) |
| `--decision` | Yes | Decision: `approve`, `deny`, or `defer` |
| `--comment` | No | Optional explanation or conditions for the decision |

## Decision Values

| Decision | Effect | When to Use |
|----------|--------|-------------|
| `approve` | AMCOS proceeds with the operation | Operation is safe and aligned with goals |
| `deny` | AMCOS cancels the operation | Operation is inappropriate or risky |
| `defer` | AMCOS must provide more info or modify and resubmit | Operation concept is okay but details need adjustment |

## What This Command Does

1. **Validates Request ID**
   - Checks that the request ID exists in pending requests
   - Retrieves the original request details

2. **Validates Decision**
   - Ensures decision is one of the valid options
   - For `defer`, requires comment explaining what to change

3. **Sends Response via AI Maestro**
   - Formats response message according to AMCOS protocol
   - Sends to AMCOS via AI Maestro messaging

4. **Updates State Tracking**
   - Records decision with timestamp
   - Logs for audit trail

5. **Outputs Confirmation**
   - Shows what was sent
   - Confirms delivery status

## Examples

### Approve an Operation

```
/amama-respond-to-amcos --request-id amcos-req-a1b2c3d4 --decision approve --comment "Proceed with staging deployment"
```

Output:
```
Response sent to AMCOS

Request ID: amcos-req-a1b2c3d4
Decision: APPROVE
Comment: Proceed with staging deployment
Sent at: 2025-02-02T14:32:00Z

AMCOS will now proceed with the operation.
```

### Reject an Operation

```
/amama-respond-to-amcos --request-id amcos-req-x9y8z7 --decision deny --comment "Too risky before weekend - defer to Monday"
```

Output:
```
Response sent to AMCOS

Request ID: amcos-req-x9y8z7
Decision: DENY
Comment: Too risky before weekend - defer to Monday
Sent at: 2025-02-02T14:35:00Z

AMCOS will cancel the operation and log the denial.
```

### Defer for Revision

```
/amama-respond-to-amcos --request-id amcos-req-m4n5o6 --decision defer --comment "Reduce scope to only feature/* branches, exclude main"
```

Output:
```
Response sent to AMCOS

Request ID: amcos-req-m4n5o6
Decision: NEEDS REVISION
Comment: Reduce scope to only feature/* branches, exclude main
Sent at: 2025-02-02T14:40:00Z

AMCOS will revise the request and resubmit.
```

## Listing Pending Requests

Before responding, you may want to see pending requests.

Check your inbox via the `amp-inbox` CLI. Filter for messages from AMCOS-prefixed senders to find approval requests.

**Verify**: confirm you have reviewed all unread AMCOS messages before proceeding.

## Message Format Sent

The command sends an approval response to AMCOS via the `amp-send` CLI (`--type approval --priority high`):

- **Recipient**: `amcos-<project-name>`
- **Subject**: "AMAMA Approval Response: <request_id>"
- **Priority**: `high`
- **Content**: Include the following fields:
  - `type`: `approval_decision`
  - `request_id`: The request ID being responded to
  - `decision`: The decision value (`approve`, `deny`, or `defer`)
  - `comment`: The optional comment text
  - `conditions`: List of conditions (empty list if none)
  - `responded_at`: ISO-8601 timestamp of the response

**Verify**: confirm the `amp-send` command exited 0 (delivery accepted by AI Maestro).

## Error Conditions

| Error | Cause | Solution |
|-------|-------|----------|
| `Request ID not found` | Invalid or already-responded request ID | Check pending requests list |
| `Invalid decision value` | Decision not one of allowed values | Use: approve, deny, defer |
| `defer requires comment` | Missing comment for defer decision | Add --comment explaining what to change |
| `AI Maestro unavailable` | Messaging system not running | Start AI Maestro service |
| `AMCOS not registered` | AMCOS agent not in AI Maestro registry | Register AMCOS agent |

## Prerequisites

1. **AI Maestro must be running**
   Verify AI Maestro health via the `amp-status` CLI.

2. **AMCOS must be registered**
   Use the `ai-maestro-agents-management` skill to list agents and confirm an AMCOS agent is registered and active.

3. **Pending request must exist**
   Check your inbox via the `amp-inbox` CLI and filter for unread AMCOS messages.

## Related Commands

- `/amama-orchestration-status` - View pending AMCOS requests in status report
- `/amama-approve-plan` - Approve plans (separate from AMCOS approval flow)

## Related Skills

- **amama-amcos-coordination**
- **amama-approval-workflows**
