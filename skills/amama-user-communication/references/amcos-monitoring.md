# Proactive AMCOS Monitoring

## Table of Contents
- [Monitoring Schedule](#monitoring-schedule)
- [Health Check Procedure](#health-check-procedure)
- [AI Maestro Inbox Check](#ai-maestro-inbox-check)
- [Responsiveness Ping (15 Minute Timeout)](#responsiveness-ping-15-minute-timeout)
- [Actions When AMCOS Unresponsive](#actions-when-amcos-unresponsive)
- [See Also](#see-also)

AMAMA must proactively monitor AMCOS health and responsiveness to prevent communication failures and ensure timely approval processing.

---

## Monitoring Schedule

| Check Type | Frequency | Trigger |
|------------|-----------|---------|
| AMCOS Health Check | Every 10 minutes | During active work sessions |
| AI Maestro Inbox | Every 2 minutes | For pending approval requests |
| AMCOS Responsiveness Ping | When 15 minutes without response | After sending any message to AMCOS |

## Health Check Procedure

Send a periodic AMCOS health check every 10 minutes during active work using the `agent-messaging` skill:
- **Recipient**: `amcos-<project>-coordinator`
- **Subject**: "Periodic Health Check"
- **Content**: ping type, message "Routine health check", expect_reply true, timeout 60
- **Type**: `ping`
- **Priority**: `low`

**Verify**: check inbox for a `pong` response within the timeout period.

## AI Maestro Inbox Check

Check your inbox every 2 minutes for approval requests using the `agent-messaging` skill. Filter for messages with content type `approval_request`.

## Responsiveness Ping (15 Minute Timeout)

If no response from AMCOS after 15 minutes since last message sent, send an urgent ping using the `agent-messaging` skill:
- **Recipient**: `amcos-<project>-coordinator`
- **Subject**: "URGENT: Response Required"
- **Content**: ping type, message "No response received for 15 minutes. Please acknowledge.", expect_reply true, timeout 30
- **Type**: `ping`
- **Priority**: `urgent`

## Actions When AMCOS Unresponsive

If AMCOS fails to respond after the urgent ping (30 second timeout):

1. **Verify AMCOS Session Exists**
   Use the `ai-maestro-agents-management` skill to list agents and check if the AMCOS session is still active.

2. **Check AI Maestro Health**
   Use the `agent-messaging` skill's health check feature to verify AI Maestro is running.

3. **Notify User**
   ```
   AMCOS (amcos-<project>-coordinator) is unresponsive.
   Last successful contact: <timestamp>
   Attempted recovery: <steps taken>

   Options:
   - [Restart AMCOS] - Attempt to reassign the chief-of-staff role to another agent
   - [Continue Without] - Proceed with reduced coordination
   - [Investigate] - Check logs for error details
   ```

4. **Attempt Recovery**
   - If AI Maestro is down: Alert user to restart AI Maestro
   - If AMCOS session crashed: Reassign the chief-of-staff role using standard reassignment procedure
   - If network issue: Wait 5 minutes and retry

5. **Log Incident**
   Record the unresponsive incident in `docs_dev/sessions/amcos-health-log.md`

---

## See Also

- [blocker-notification-templates.md](blocker-notification-templates.md) - Blocker notification formats
