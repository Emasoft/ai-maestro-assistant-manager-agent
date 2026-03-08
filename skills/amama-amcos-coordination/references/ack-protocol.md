# Message Acknowledgment Protocol

## Table of Contents
- [ACK Timeout Requirements](#ack-timeout-requirements)
- [ACK Message Format](#ack-message-format)
- [Handling Missing ACK](#handling-missing-ack)
- [ACK Verification Checklist](#ack-verification-checklist)

All messages sent to a COS-assigned agent require acknowledgment (ACK) to ensure reliable communication. Different message types have different ACK timeout requirements.

## ACK Timeout Requirements

| Message Type | ACK Timeout | Retry Behavior | Escalation |
|--------------|-------------|----------------|------------|
| Approval decisions | 30 seconds | Retry once after timeout | Escalate to user if no ACK after retry |
| Work requests | 60 seconds | Retry once after timeout | Escalate to user if no ACK after retry |
| Health check pings | 30 seconds | No retry | Log as unresponsive |
| Status queries | 30 seconds | Retry once after timeout | Report timeout to user |
| Autonomy grant/revoke | 30 seconds | Retry once after timeout | Escalate to user if no ACK after retry |

## ACK Message Format

The COS-assigned agent must respond with an ACK message within the timeout period. The ACK message arrives via the `agent-messaging` skill with the following structure:

- **Sender**: The COS-assigned agent's session name
- **Subject**: "ACK: <original-subject>"
- **Priority**: `normal`
- **Content fields**:
  - `type`: `ack`
  - `original_message_id`: The message ID of the original message being acknowledged
  - `status`: One of `received` (message received), `processing` (actively working on it), or `completed` (action done)
  - `timestamp`: ISO-8601 timestamp of the acknowledgment

## Handling Missing ACK

**Step 1: Wait for Timeout**
- Start timer when message is sent
- Check inbox for ACK message at timeout

**Step 2: Retry Once**

Resend the original message with a retry flag using the `agent-messaging` skill:
- **Recipient**: The COS-assigned agent's session name
- **Subject**: "RETRY: <original-subject>"
- **Content**: Same as original message, plus `retry_of` (original message ID) and `retry_count` (1)
- **Priority**: `high`

**Verify**: confirm message delivery via the skill's sent messages feature.

**Step 3: Escalate if Still No ACK**
If no ACK after retry:

1. **Log the failure** in `docs_dev/sessions/ack-failures.md`
2. **Alert the user**:
   ```
   COS-Assigned Agent Communication Failure

   Agent: <agent-session-name>
   Team: <team-name>
   Message: <subject>
   Sent: <timestamp>
   Retry: <retry-timestamp>
   Status: No acknowledgment received

   The COS-assigned agent may be unresponsive. Options:
   - [Check Agent Health] - Send health ping
   - [Retry Again] - Send message again
   - [Reassign COS] - Unassign COS role and assign to different agent
   ```
3. **Do not assume message was processed** - treat as failed delivery

## ACK Verification Checklist

- [ ] Message sent with unique message ID
- [ ] Timer started at send time
- [ ] ACK received within timeout period
- [ ] ACK references correct original message ID
- [ ] ACK status recorded in communication log
