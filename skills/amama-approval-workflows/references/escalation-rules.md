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
- Governance password rate-limit exceeded (requests queued until cooldown ends)

## Auto-Approve Conditions (NEVER by default)

- No auto-approve without explicit user configuration
- All governance requests require MANAGER decision

## Escalation Triggers

- Security-related GovernanceRequest (delete-agent, configure-agent with security changes)
- GovernanceRequest with "urgent" priority flag
- Multiple failed governance password attempts (potential breach)
- Transfer request contested by source team COS

## User Notification

When a GovernanceRequest is created:

1. Display the request prominently with its type and payload summary
2. If user is idle, send periodic reminders
3. Block the requested operation until MANAGER decides
4. Log all requests and decisions to both the API and local state

## Workflow Checklist

- [ ] Verify governance password is set
- [ ] Poll for pending GovernanceRequests via API
- [ ] Parse request type
- [ ] Present GovernanceRequest to MANAGER using appropriate template
- [ ] Wait for MANAGER decision
- [ ] Call approve or reject API endpoint with governance password
- [ ] Verify state transition completed
- [ ] Update local approval state tracking file
- [ ] Notify requesting agent of the outcome
- [ ] Log the request and decision to approval-log.md
- [ ] Handle errors, rate limits, and timeouts
