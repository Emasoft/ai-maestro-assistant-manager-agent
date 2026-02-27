# Delegation Rules for Autonomous Operation

## Use-Case TOC

- When to grant autonomous mode to ECOS -> Section 2
- How to configure delegation rules -> Section 2
- When to revoke autonomous mode -> Section 3
- What operations always require approval -> Section 4

## Table of Contents

1. What is Autonomous Mode
2. Granting Autonomous Mode
3. Revoking Autonomous Mode
4. Operations That ALWAYS Require EAMA Approval

---

## 1. What is Autonomous Mode

Autonomous mode allows ECOS to proceed with certain operation types without requesting approval for each one. EAMA grants autonomous mode based on:

- Operation type
- Risk level
- Time boundaries
- Scope boundaries

### Delegation Configuration

EAMA can configure delegation rules stored in state file:

```yaml
ecos_delegation:
  autonomous_mode: true|false
  granted_at: "ISO-8601"
  expires_at: "ISO-8601|never"
  operation_types:
    routine-operation: true
    minor-decision: true
    critical-operation: false
    policy-exception: false
  scope_limits:
    max_files_per_operation: 50
    allowed_branches: ["feature/*", "fix/*"]
    forbidden_paths: ["**/secrets/**", "**/prod/**"]
  notification_level: "all|important|critical-only"
```

---

## 2. Granting Autonomous Mode

EAMA grants autonomy via command or AI Maestro message.

Send an autonomy grant using the `agent-messaging` skill:
- **Recipient**: `ecos-<project-name>`
- **Subject**: "EAMA Autonomous Mode Grant"
- **Priority**: `high`
- **Content**: Include the following fields:
  - `type`: `autonomy-grant`
  - `operation_types`: List of operation types ECOS can perform autonomously (e.g., `routine-operation`, `minor-decision`)
  - `expires_at`: ISO-8601 timestamp when autonomous mode ends (e.g., `2025-02-02T18:00:00Z`)
  - `scope_limits`: A nested structure containing:
    - `max_files_per_operation`: Maximum files per operation (e.g., 50)
    - `allowed_branches`: List of branch patterns (e.g., `feature/*`)
  - `notification_level`: Reporting frequency (`all`, `important`, or `critical-only`)

**Verify**: confirm message delivery via the `agent-messaging` skill's sent messages feature.

### Grant Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `operation_types` | Types of operations ECOS can do autonomously | `["routine-operation", "minor-decision"]` |
| `expires_at` | When autonomous mode ends | ISO-8601 timestamp or `"never"` |
| `scope_limits` | Boundaries for autonomous operations | See configuration above |
| `notification_level` | How often ECOS reports to EAMA | `"all"`, `"important"`, `"critical-only"` |

---

## 3. Revoking Autonomous Mode

EAMA revokes autonomy when:

1. User explicitly requests revocation
2. Time boundary expires
3. ECOS exceeds scope limits
4. Security concern detected
5. User unavailable for extended period

### Revocation Message

Send an autonomy revocation using the `agent-messaging` skill:
- **Recipient**: `ecos-<project-name>`
- **Subject**: "EAMA Autonomous Mode Revoked"
- **Priority**: `urgent`
- **Content**: Include the following fields:
  - `type`: `autonomy-revoke`
  - `reason`: One of `User request`, `Scope exceeded`, `Security concern`, or `Timeout`
  - `effective_immediately`: `true` (revocation always takes effect immediately)
  - `revoked_at`: ISO-8601 timestamp of revocation

**Verify**: confirm message delivery via the `agent-messaging` skill's sent messages feature.

### Revocation Reasons

| Reason | Description |
|--------|-------------|
| `User request` | User explicitly asked to revoke |
| `Scope exceeded` | ECOS attempted unauthorized operation |
| `Security concern` | Suspicious activity detected |
| `Timeout` | Autonomy period expired |

---

## 4. Operations That ALWAYS Require EAMA Approval

No matter what delegation is granted, these operations ALWAYS require EAMA approval:

| Operation | Reason |
|-----------|--------|
| **Production deployments** | Any deployment to production environment |
| **Security-sensitive changes** | Authentication, authorization, encryption |
| **Data deletion** | Removing user data or database records |
| **External communications** | Publishing releases, sending notifications |
| **Budget commitments** | Any cost-incurring actions |
| **Breaking changes** | API changes that break backward compatibility |
| **Access changes** | Modifying permissions or credentials |

These restrictions cannot be overridden by delegation configuration. ECOS must always request approval for these operation types regardless of autonomous mode status.
