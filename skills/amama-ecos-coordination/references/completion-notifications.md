# Completion Notifications from ECOS

## Use-Case TOC

- When ECOS sends completion notifications -> Section 1
- How to process completion notifications -> Section 2
- When to notify the user about completions -> Section 3

## Table of Contents

1. When ECOS Sends Completion Notifications
2. Processing Completion Notifications
3. User Notification Rules

---

## 1. When ECOS Sends Completion Notifications

ECOS notifies EAMA when:

1. An approved operation completes (success or failure)
2. An autonomous operation completes (based on notification_level)
3. A delegated task chain completes
4. An error occurs that requires escalation

### Notification Triggers by Mode

| Mode | Trigger | Expected |
|------|---------|----------|
| Approval mode | Every completed operation | Always |
| Autonomous mode | Based on `notification_level` setting | Varies |

---

## 2. Processing Completion Notifications

When EAMA receives a completion notification:

### Step 1: Parse the notification
- Extract `request_id`, `result`, and `autonomous_mode`

### Step 2: Handle based on result

**If `result` is `failed`:**
1. Evaluate severity of the failure
2. Decide if user notification is needed
3. Consider revoking autonomous mode if pattern of failures

**If `result` is `success`:**
1. Update state tracking
2. Optionally notify user based on importance

**If `result` is `partial`:**
1. Review what completed and what didn't
2. Decide if additional action needed
3. May need to request clarification from ECOS

### Step 3: Handle autonomous mode operations

If `autonomous_mode` was true:
1. Verify operation was within granted scope
2. Log for audit trail
3. Check if scope limits were approached

---

## 3. User Notification Rules

| Completion Type | Notify User |
|-----------------|-------------|
| Critical operation success | Always |
| Critical operation failure | Always |
| Routine operation success | Based on user preference |
| Routine operation failure | Always |
| Autonomous operation success | Aggregate in status report |
| Autonomous operation failure | Immediately |

### User Preference Defaults

```yaml
user_notification_preferences:
  critical_success: always
  critical_failure: always
  routine_success: daily_summary
  routine_failure: immediately
  autonomous_success: weekly_summary
  autonomous_failure: immediately
```

### Aggregation for Status Reports

When `notification_level` is not `all`, EAMA aggregates autonomous operation completions:

```yaml
status_report:
  period: "2025-02-02 12:00 - 18:00"
  autonomous_operations:
    total: 15
    successful: 14
    failed: 1
    operations:
      - type: implementation
        count: 8
      - type: testing
        count: 5
      - type: documentation
        count: 2
  failures:
    - request_id: "autonomous-xyz123"
      type: "testing"
      reason: "Integration test timeout"
```
