# Handoff Document Format

## Contents

- [CozoDB Handoff Record](#cozodb-handoff-record)
- [Fallback Handoff Document Structure](#fallback-handoff-document-structure)
- [Session Metadata](#session-metadata)
- [User State](#user-state)
- [Active Context](#active-context)
- [Pending Items Requiring User Attention](#pending-items-requiring-user-attention)
- [Recent Decisions](#recent-decisions)
- [Communication Notes](#communication-notes)
- [Resume Instructions](#resume-instructions)
- [Handoff Best Practices](#handoff-best-practices)

When AMAMA session ends or context compacts, a handoff record ensures continuity. The primary handoff is stored in CozoDB; a file-based copy is written as fallback.

## CozoDB Handoff Record

> **Note**: Memory is file-based. Handoff records are stored as markdown files in `thoughts/shared/handoffs/amama/`.
> See the `session-memory` skill for full details on file-based memory storage.

## Fallback Handoff Document Structure

**File**: `thoughts/shared/handoffs/amama/current.md`

```markdown
# AMAMA Session Handoff

## Session Metadata
- Session ID: amama-20250130-001
- Last Updated: 2025-01-30
- Previous Session: amama-20250129-003
- Storage Backend: CozoDB (synced) | File-only (fallback)

## User State
- Availability: monitoring
- Last Interaction: responded to architecture question
- Engagement Level: high (multiple detailed responses)

## Active Context
- Current Project: authentication-module
- Active Issue: #45 (user auth implementation)
- Active Role Handoff: Architect designing OAuth flow

## Pending Items Requiring User Attention
1. Database schema choice - deferred, re-raise when design phase starts
2. OAuth provider selection - awaiting user research
3. PR #47 review - submitted, no response yet

## Recent Decisions
- 2025-01-30: Approved PostgreSQL for user data (CozoDB decision ID: abc-123)
- 2025-01-29: Approved microservices pattern (CozoDB decision ID: def-456)

## Communication Notes
- User prefers concise responses
- Technical detail level: high
- Prefers bullet points over paragraphs
- Uses "LGTM" for lightweight approvals

## Resume Instructions
When resuming:
1. Connect to CozoDB and query latest state
2. If CozoDB unavailable, use this file as fallback
3. Check pending_items for items that may need attention
4. Reference recent decisions before proposing alternatives
5. Maintain concise communication style
6. Check if user availability has changed
```

## Handoff Best Practices

1. **Be Specific**: Include issue numbers, file paths, CozoDB record IDs
2. **Be Current**: Write to CozoDB before every potential compaction
3. **Be Minimal**: Only essential context, not full history
4. **Be Actionable**: Include "Resume Instructions" section
5. **Be Linked**: Reference CozoDB relations for details
6. **Be Redundant**: Always write fallback files alongside CozoDB
