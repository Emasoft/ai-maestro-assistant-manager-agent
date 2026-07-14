# Escalation Rules Reference

## Table of Contents
- [Auto-Reject Conditions](#auto-reject-conditions)
- [Auto-Approve Conditions (NEVER by default)](#auto-approve-conditions-never-by-default)
- [Escalation Triggers](#escalation-triggers)
- [User Notification](#user-notification)
- [Workflow Checklist](#workflow-checklist)

## Auto-Reject Conditions

- GovernanceRequest older than 24 hours without response
- Requesting agent session terminated
- Blocking security vulnerability detected
- `$AID_AUTH` invalid / missing — the request cannot be authorized; stop and surface (never fall back to unauthenticated calls)

## Auto-Approve Conditions (NEVER by default)

- No auto-approve without explicit user configuration
- All governance requests require MANAGER decision

## Escalation Triggers

- Security-related GovernanceRequest (delete-agent, configure-agent with security changes)
- GovernanceRequest with "urgent" priority flag
- Cross-host / sudo-gated request — surface to the MAESTRO to action via the UI (R32)
- Transfer request contested by source team COS

## User Notification

When a GovernanceRequest is created:

1. Display the request prominently with its type and payload summary
2. If user is idle, send periodic reminders
3. Block the requested operation until MANAGER decides
4. Log all requests and decisions to both the API and local state

## Workflow Checklist

- [ ] Verify `$AID_AUTH` present (server runs the 3-check authz, R28)
- [ ] Poll for pending GovernanceRequests via `aimaestro-governance.sh requests` (redirect to a scratch file; surface only count + ids)
- [ ] Parse request type
- [ ] Present GovernanceRequest to MANAGER using appropriate template
- [ ] Wait for MANAGER decision
- [ ] Call `aimaestro-governance.sh approve`/`reject` (AID-authorized; sudo-gated → surface to MAESTRO, R32)
- [ ] Verify state transition completed
- [ ] Update local approval state tracking file
- [ ] Notify requesting agent of the outcome
- [ ] Log the request and decision to approval-log.md
- [ ] Handle errors, rate limits, and timeouts
