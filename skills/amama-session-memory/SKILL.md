---
name: amama-session-memory
description: Use when restoring user context, tracking decisions, or managing availability states. Trigger with session start or preference changes.
version: 2.3.3
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: false
---

# AMAMA Session Memory Skill

## Overview

Maintains user relationship continuity across sessions. Uses CozoDB (primary) with file-based fallback for preferences, decisions, pending items, and availability states.

## Prerequisites

1. AI Maestro with CozoDB at `~/.aimaestro/agents/<agent-id>/`
2. Subconscious memory indexing service running
3. File access for `thoughts/shared/handoffs/amama/`

## Instructions

1. Check CozoDB availability and initialize storage
2. Load context from CozoDB or handoff files
3. Run semantic search for implicit preferences
4. Detect preference expressions and patterns
5. Record decisions (approvals, rejections, deferrals)
6. Track pending items awaiting user attention
7. Monitor availability state changes
8. Write handoffs before session end
9. Trigger consolidation for stable preferences

Copy this checklist and track your progress:

- [ ] Check CozoDB / initialize storage
- [ ] Load context
- [ ] Detect preferences and patterns
- [ ] Record decisions
- [ ] Track pending items
- [ ] Write handoffs at session end

## Output

| Output | When |
|--------|------|
| Session restored | Session start |
| Preference recorded | Preference detected |
| Decision logged | User decides |
| Availability ack | State change |
| Handoff record | Session end |
| Pending reminder | Resume |
| Sync status | CozoDB recovery |

## Error Handling

| Error | Resolution |
|-------|------------|
| CozoDB unavailable | File-based fallback |
| CozoDB write fail | Retry once, then fallback |
| Fallback dir missing | Create directory |
| File corrupted | Regenerate from CozoDB |
| Semantic timeout | Structured data only |
| Conflicting prefs | Most recent wins |
| CozoDB/file diverge | CozoDB authoritative |

## Examples

**Session start:** Loads preferences, pending items, decisions from CozoDB or fallback.

**Preference detection:** User says "be more brief" -- writes to CozoDB + fallback.

**Input/Output:** Store `{"relation":"user_preferences","data":{"key":"response_length","value":"concise"}}` => Output: `Noted: keeping responses concise.`

See [references/examples.md](references/examples.md) for detailed examples:
  - Example 1: Session Start with AI Maestro Memory
  - Example 2: Session Start with Fallback
  - Example 3: Detecting and Recording Preference
  - Example 4: Recording Decision with Context
  - Example 5: Availability State Change
  - Example 6: Semantic Search for Implicit Preferences

## Resources

- **Related skills** - amama-approval-workflows, amama-user-communication
- **Memory API** - `$AIMAESTRO_API/api/memory/`

### Reference Documents

- [memory-architecture.md](references/memory-architecture.md) - Storage tiers and schemas
  - Tiered Storage Architecture
  - Tier 1: AI Maestro CozoDB Agent Database
  - Tier 2: Subconscious Memory Indexing
  - Tier 3: Long-Term Memory Consolidation
  - Tier 4: File-Based Handoff Documents (Fallback)
  - Secondary: GitHub Issue Comments
  - Data Types Stored
- [memory-triggers.md](references/memory-triggers.md) - Trigger conditions and API
  - Memory Retrieval Triggers
  - Memory Update Triggers
- handoff-format.md (references/handoff-format.md) - Handoff templates
- [examples.md](references/examples.md) - Operation examples
  - Example 1: Session Start with AI Maestro Memory
  - Example 2: Session Start with Fallback
  - Example 3: Detecting and Recording Preference
  - Example 4: Recording Decision with Context
  - Example 5: Availability State Change
  - Example 6: Semantic Search for Implicit Preferences
- record-keeping-formats.md (references/record-keeping-formats.md) - Record formats

---

**Version**: 2.3.3 | **Updated**: 2026-03-08
