# COS Coordination Error Handling

<!-- TOC -->
- [Common Errors](#common-errors)
- [Error Scenarios](#error-scenarios)
- [Escalation to User](#escalation-to-user)
- [Audit Trail](#audit-trail)
<!-- /TOC -->

## Common Errors

| Error | Symptom | Solution |
|-------|---------|----------|
| Agent not in registry | `404` on COS assignment | Register agent first via `POST /api/agents/register` |
| COS-assigned agent not found | No response to messages | Verify agent session exists, check AI Maestro registry |
| Message send failure | AI Maestro API error | Check AI Maestro service status |
| Invalid approval format | COS-assigned agent rejects response | Review message format in [message-formats.md](message-formats.md) |
| Autonomy grant failed | COS-assigned agent doesn't acknowledge grant | Verify agent has latest plugin version |
| Duplicate request ID | Request ID collision | Use unique UUID for each request |
| Team not found | `404` on team operations | Create team first via `POST /api/teams` |
| COS already assigned | Team already has a COS | Unassign current COS before assigning new one |

## Error Scenarios

| Error | Cause | AMAMA Action |
|-------|-------|-------------|
| COS-assigned agent unresponsive | Agent session crashed or network issue | Alert user, attempt restart |
| Request timeout | AMAMA took too long to respond | Auto-escalate to user |
| Invalid request format | Malformed message from COS-assigned agent | Return error, request retry |
| Scope exceeded | COS-assigned agent attempted unauthorized operation | Revoke autonomy, alert user |
| Conflicting requests | Multiple requests for same resource | Queue and resolve sequentially |
| Cross-host assignment failure | GovernanceRequest rejected | Check governance policies, retry or escalate |

## Escalation to User

AMAMA escalates to user when:

1. Cannot make autonomous decision
2. Request involves user-defined critical operations
3. COS-assigned agent reports critical failure
4. Security concern detected
5. Request timeout approaching

## Audit Trail

All COS interactions are logged:

```yaml
cos_audit_log:
  - timestamp: "ISO-8601"
    event_type: "assign-cos|unassign-cos|request|response|grant|revoke|complete"
    request_id: "cos-req-{uuid}"
    team_id: "team-{uuid}"
    agent_id: "agent-{uuid}"
    details: "Event description"
    user_involved: true|false
```
