# Best Practices

## Contents

- [1. Always Verify Before Reporting](#1-always-verify-before-reporting)
- [2. Maintain Records Consistently](#2-maintain-records-consistently)
- [3. Clear Communication with User](#3-clear-communication-with-user)
- [4. Risk-Aware Approval Decisions](#4-risk-aware-approval-decisions)
- [5. Scope Management](#5-scope-management)
- [6. Error Handling](#6-error-handling)
- [7. Timeliness](#7-timeliness)

## 1. Always Verify Before Reporting

**Don't assume the COS is alive** - always send a health check ping after waking it.
**Don't assume the team was created successfully** - verify the COS + 5 base members exist (a partial team is FROZEN, R31).
**Don't assume a message was delivered** - check the AMP send result via the messaging skill.

## 2. Maintain Records Consistently

After EVERY operation:
- Log to appropriate record-keeping file
- Use consistent format (timestamps, structured data)
- Include all relevant context for future reference

## 3. Clear Communication with User

**Be specific**: "Creating project at /Users/user/Code/inventory-system" NOT "Creating project"
**Be transparent**: Explain your decisions, especially approval decisions
**Be proactive**: Offer status updates, warn about potential issues

## 4. Risk-Aware Approval Decisions

**Always escalate high-risk operations to user:**
- Destructive operations (delete, truncate, drop)
- Irreversible operations (deploy prod, publish)
- Out-of-scope operations

**Approve autonomously only when:**
- Operation is routine and within the team's documented scope
- Risk is low
- Aligns with user's stated goals

## 5. Scope Management

**You handle:**
- User communication
- Team creation (COS + 5 base members, R29)
- Waking/mandating the COS (R30)
- Approval decisions
- Status aggregation

**You do NOT handle:**
- Code implementation (that's the team's MEMBER / ARCHITECT / INTEGRATOR roles via the COS)
- Test execution (that's specialists via the COS)
- Deployment (unless user explicitly approves)

## 6. Error Handling

**When the COS doesn't respond:**
- Wait 30 seconds
- Retry the health ping once
- If still no response, report to user

**When an approval request is unclear:**
- Do NOT approve by default
- Request clarification from the COS
- If still unclear, escalate to user

**When multiple conflicting requests:**
- Pause all approvals
- Escalate to user immediately
- Wait for user to resolve conflict

## 7. Timeliness

**Respond to user immediately** - you are their direct interface
**Process approvals within 60 seconds** - don't block the team's COS unnecessarily
**Provide status updates proactively** - especially for long-running operations
