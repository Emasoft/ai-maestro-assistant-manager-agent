# Governance Password Management Reference

## Table of Contents
- [Initial Setup](#initial-setup)
- [Security Rules](#security-rules)

The governance password authenticates MANAGER approval/rejection actions. It is required before any GovernanceRequest can be approved or rejected.

## Initial Setup

Set the governance password on first use:

```
POST $AIMAESTRO_API/api/v1/governance/password
Body: {"password": "<governance-password>"}
```

- The password is bcrypt-hashed and stored server-side by AI Maestro
- To change the password, provide `currentPassword` and `password` in the request body

See the `team-governance` skill for full API details.

## Security Rules

- NEVER store the governance password in plaintext in any file, log, or message
- NEVER include the governance password in AI Maestro messages between agents
- The password is provided by the user at runtime or read from a secure environment variable
- **Rate limiting**: 5 failed attempts trigger a 60-second cooldown (`429 Too Many Requests`)

