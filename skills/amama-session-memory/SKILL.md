---
name: amama-session-memory
description: User preference and communication style persistence via AI Maestro memory system. Use when restoring user context, tracking decisions, or managing availability states. Trigger with session start.
version: 2.3.2
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: false
triggers:
  - session start/end (context restore, handoff creation)
  - user preference or availability state change
  - approval decision made
---

# AMAMA Session Memory Skill

## Overview

Maintains user relationship continuity across AMAMA sessions. Uses CozoDB agent database (primary) with file-based fallback. Stores preferences, communication style, approval history, pending items, and availability states.

4-tier architecture: CozoDB, subconscious semantic indexing, long-term consolidation, file-based handoffs. See [references/memory-architecture.md](references/memory-architecture.md) for details.

## Prerequisites

1. AI Maestro installed with CozoDB agent database at `~/.aimaestro/agents/<agent-id>/`
2. Subconscious memory indexing service running
3. File system access for fallback directory (`thoughts/shared/handoffs/amama/`)
4. GitHub API access (optional, for issue comment persistence)

## Instructions

1. **Check CozoDB availability** at `~/.aimaestro/agents/<agent-id>/`
2. **Initialize storage** - Create CozoDB relations if first use; create fallback directory
3. **Load context on session start** - Query CozoDB (primary) or read handoff files (fallback)
4. **Run semantic search** - Query subconscious memory for implicit preferences
5. **Detect preferences** - Listen for preference expressions and communication patterns
6. **Record decisions** - Log approvals, rejections, deferrals to CozoDB + fallback
7. **Track pending items** - Maintain items awaiting user attention
8. **Monitor availability** - Detect and respond to user availability changes
9. **Write handoffs before session end** - CozoDB `session_handoffs` + fallback file
10. **Trigger consolidation** - Request long-term consolidation for stable preferences
11. **Sync on recovery** - When CozoDB returns after outage, sync file state back

Memory retrieval and updates are event-driven (not time-based). See [references/memory-triggers.md](references/memory-triggers.md) for trigger conditions and API examples.

For handoff document format and best practices, see [references/handoff-format.md](references/handoff-format.md).

## Output

| Output Type | When Generated |
|-------------|----------------|
| Session restored message | Session start (indicates storage tier used) |
| Preference recorded confirmation | Preference detected |
| Decision logged confirmation | User makes decision (includes CozoDB ID) |
| Availability state change ack | User indicates away/DND |
| Handoff record | Session end or compaction |
| Pending items reminder | Resume or user request |
| Fallback sync status | Recovery from CozoDB outage |

## Error Handling

| Error | Resolution |
|-------|------------|
| CozoDB unavailable | Switch to file-based fallback, log warning |
| CozoDB write failure | Retry once, then fall back to files |
| Fallback dir missing | Create directory structure |
| Fallback file corrupted | Regenerate from CozoDB (authoritative source) |
| Semantic search timeout | Proceed with CozoDB structured data only |
| Conflicting preferences | Most recent wins; consolidation resolves conflicts |
| CozoDB/file divergence | CozoDB is authoritative; sync files to match |
| Cross-agent conflict | Most recent timestamp wins; flag for user confirmation |

## Examples

**Session start (CozoDB available):**
```
Session Restored (via AI Maestro Memory):
- Preferences: concise responses, high technical detail
- Pending: database schema choice, PR #47 review
- Recent: PostgreSQL approved (ID: abc-123)
```

**Preference detection:**
User says "Can you be more brief?" -- Write to CozoDB `user_preferences` + fallback file, confirm: "Got it - keeping responses brief."

See [references/examples.md](references/examples.md) for six detailed operation examples.

## Resources

- **AGENT_OPERATIONS.md** - Core agent patterns
- **amama-approval-workflows / amama-user-communication** - Related skills
- **CozoDB docs** - `~/.aimaestro/docs/memory-system.md`
- **Memory API** - `$AIMAESTRO_API/api/memory/`

### Reference Documents

- [references/memory-architecture.md](references/memory-architecture.md) - Storage tiers, CozoDB schemas, data types
- [references/memory-triggers.md](references/memory-triggers.md) - Trigger conditions and API examples
- [references/handoff-format.md](references/handoff-format.md) - Handoff templates and CozoDB write format
- [references/examples.md](references/examples.md) - Six detailed operation examples
- [references/record-keeping-formats.md](references/record-keeping-formats.md) - Record-keeping formats

---

**Version**: 2.3.2 | **Updated**: 2026-03-07
