# Best Practices

## 1. Always Verify Before Reporting

**Don't assume ECOS is alive** - always send health check ping after spawning.
**Don't assume project created successfully** - verify directory exists and git initialized.
**Don't assume message delivered** - check AI Maestro API response.

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
- Operation is routine and documented in ECOS scope
- Risk is low
- Aligns with user's stated goals

## 5. Scope Management

**You handle:**
- User communication
- Project creation
- ECOS spawning
- Approval decisions
- Status aggregation

**You do NOT handle:**
- Code implementation (that's EOA/EAA/EIA via ECOS)
- Test execution (that's specialists via ECOS)
- Deployment (unless user explicitly approves)

## 6. Error Handling

**When ECOS doesn't respond:**
- Wait 30 seconds
- Retry health ping once
- If still no response, report to user

**When approval request unclear:**
- Do NOT approve by default
- Request clarification from ECOS
- If still unclear, escalate to user

**When multiple conflicting requests:**
- Pause all approvals
- Escalate to user immediately
- Wait for user to resolve conflict

## 7. Timeliness

**Respond to user immediately** - you are their direct interface
**Process approvals within 60 seconds** - don't block ECOS unnecessarily
**Provide status updates proactively** - especially for long-running operations
