---
name: amama-session-memory
description: User preference and communication style persistence via AI Maestro memory system. Use when restoring user context, tracking decisions, or managing availability states. Trigger with session start.
version: 2.3.0
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: false
triggers:
  - when session starts and user context must be restored
  - when user expresses preferences or communication style
  - when approval decisions are made
  - when user availability state changes
  - when session ends and handoff document must be created
---

# AMAMA Session Memory Skill

## Overview

Session memory for the AI Maestro Assistant Manager Agent (AMAMA) serves a unique purpose: maintaining continuity in the user relationship across sessions. AMAMA session memory integrates with AI Maestro's centralized memory system (CozoDB agent database, subconscious indexing, and long-term consolidation) as the primary storage backend, with a file-based fallback for resilience. This enables semantic search over conversation history, automatic memory consolidation, and cross-agent memory sharing.

**Purpose**: Enable AMAMA to remember the user across sessions, maintaining relationship continuity and avoiding repetitive clarification requests.

**Scope**: User preferences, communication style, approval history, pending items, and availability states.

## Prerequisites

1. AI Maestro installed with CozoDB agent database at `~/.aimaestro/agents/<agent-id>/`
2. Subconscious memory indexing service running (conversation history to semantic search)
3. File system access for fallback handoff documents directory (`thoughts/shared/handoffs/amama/`)
4. GitHub API access for issue comment persistence (optional but recommended)
5. Understanding of AMAMA role as user-facing communication agent
6. Familiarity with context compaction and session continuity concepts

## Memory Architecture

AMAMA session memory uses a tiered storage architecture with AI Maestro as the primary backend and file-based handoffs as fallback.

### Tier 1 (Primary): AI Maestro CozoDB Agent Database

**Location**: `~/.aimaestro/agents/<agent-id>/memory.cozo`

CozoDB stores structured memory records with semantic indexing. Each memory entry is a typed relation:

| Relation | Schema | Purpose |
|----------|--------|---------|
| `user_preferences` | `(key, value, source, timestamp)` | Communication style, format, verbosity |
| `decisions` | `(id, context, decision, reason, related_issues, timestamp)` | Approval history |
| `pending_items` | `(id, type, description, priority, created, deadline?)` | Items awaiting user action |
| `availability_state` | `(state, since, notes)` | Current user availability |
| `session_handoffs` | `(session_id, summary, resume_instructions, timestamp)` | Session continuity data |

**Why CozoDB**: Datalog queries for relationship traversal, built-in vector search for semantic retrieval, transactional writes for consistency.

### Tier 2: Subconscious Memory Indexing

AI Maestro's subconscious memory system indexes conversation history into a semantic search index. AMAMA leverages this for implicit preference detection, decision context retrieval, and cross-agent memory (preferences expressed to AMIA/AMAA/AMOA).

### Tier 3: Long-Term Memory Consolidation

AI Maestro periodically consolidates short-term memory into long-term summaries: preference stabilization, decision pattern recognition, and stale item cleanup.

### Tier 4 (Fallback): File-Based Handoff Documents

**Location**: `thoughts/shared/handoffs/amama/`

When CozoDB is unavailable, AMAMA falls back to file-based storage:

```
thoughts/shared/handoffs/amama/
  current.md              # Current session state
  user-preferences.md     # Accumulated user preferences
  decision-log.md         # Historical decisions
  pending-items.md        # Items awaiting user action
```

On session start, AMAMA checks CozoDB connectivity. If unavailable, it uses file-based storage and syncs back when CozoDB returns.

### Secondary: GitHub Issue Comments

Records user decisions and preferences as hidden HTML comments (`<!-- AMAMA-CONTEXT ... -->`) on issues with the `amama-context` label.

## What AMAMA Session Memory Stores

AMAMA session memory is structured around the user relationship, not technical task state.

### 1. User Preferences and Communication Style

| Preference Type | Example Data | Why Stored |
|-----------------|--------------|------------|
| Verbosity level | "prefers concise responses" | Avoid over-explaining |
| Technical depth | "wants implementation details" | Match expertise level |
| Format preference | "likes bullet points over prose" | Match reading style |
| Language quirks | "uses 'ship it' to mean 'approve'" | Understand user jargon |
| Communication channel | "prefers GitHub comments over chat" | Route responses correctly |

### 2. Previous Decisions and Approvals

| Decision Type | Example Data | Why Stored |
|---------------|--------------|------------|
| Architecture approvals | "approved microservices pattern for auth" | Avoid re-proposing |
| Tool selections | "chose PostgreSQL over MySQL" | Remember constraints |
| Style decisions | "prefers function-based over class-based" | Maintain consistency |
| Scope decisions | "deferred OAuth until Phase 2" | Track deferrals |
| Rejection reasons | "rejected Redis caching due to cost" | Avoid repeating proposals |

### 3. Pending Items Requiring User Attention

| Pending Type | Example Data | Why Stored |
|--------------|--------------|------------|
| Unanswered questions | "waiting for database schema preference" | Resume asking |
| Deferred decisions | "OAuth scope question deferred to later" | Re-raise appropriately |
| Review requests | "PR #45 awaiting user review" | Track open items |
| Approval requests | "deploy to staging pending approval" | Remind when appropriate |
| Blockers needing user | "external API key needed from user" | Track dependencies |

### 4. User Availability States

| State | Description | AMAMA Behavior |
|-------|-------------|---------------|
| `active` | User is actively engaged | Full interaction, ask questions freely |
| `monitoring` | User is available but not actively working | Batch non-urgent items, summarize |
| `away` | User is temporarily unavailable | Queue items, avoid interruptions |
| `do-not-disturb` | User explicitly requested no interruptions | Only critical escalations |
| `unknown` | Availability not established | Assume monitoring, ask if needed |

## Memory Triggers

Memory retrieval and updates are driven by state changes, not time intervals. There are 4 retrieval triggers (session start, role routing, GitHub issue context, approval request) and 5 update triggers (preference expression, decision made, availability change, pending item resolution, session end/compaction).

For detailed trigger conditions, detection signals, actions, and CozoDB/fallback API examples, see [references/memory-triggers.md](references/memory-triggers.md).
  - Memory Retrieval Triggers
  - Memory Update Triggers

## Handoff Document Creation

When a session ends or context compacts, a handoff record ensures continuity. The primary handoff is stored in CozoDB `session_handoffs` relation; a file-based copy is written to `thoughts/shared/handoffs/amama/current.md` as fallback. Both are always written together.

**Best practices**: Be specific (include issue numbers, CozoDB IDs), be current (write before compaction), be minimal (essential context only), be actionable (include resume instructions), be redundant (always write both CozoDB and fallback).

For the full handoff document template, CozoDB write format, and fallback file structure, see [references/handoff-format.md](references/handoff-format.md).
  - Handoff Document Format
  - CozoDB Handoff Record
  - Fallback Handoff Document Structure
  - Handoff Best Practices

## Instructions

Follow these steps to maintain session memory:

1. **Check AI Maestro CozoDB availability** - Verify `~/.aimaestro/agents/<agent-id>/` exists and is accessible
2. **Initialize memory structure** - Create CozoDB relations if first use; create fallback handoff directory
3. **Load context on session start** - Query CozoDB (primary) or read handoff documents (fallback)
4. **Run semantic search** - Query subconscious memory for implicit preferences from conversation history
5. **Detect user preferences** - Listen for preference expressions and communication patterns
6. **Record decisions** - Log all user approvals, rejections, and deferrals to CozoDB and fallback
7. **Track pending items** - Maintain list of items awaiting user attention in CozoDB and fallback
8. **Monitor availability state** - Detect and respond to user availability changes
9. **Update handoff records** - Write to CozoDB and fallback files before session end or compaction
10. **Trigger memory consolidation** - Request long-term consolidation for stable preferences
11. **Sync fallback on recovery** - When CozoDB returns after outage, sync file-based state back
12. **Validate continuity** - Ensure next session can resume seamlessly from either storage tier

**Checklist for session memory management** — Copy this checklist and track your progress:

- [ ] Verify CozoDB agent database at `~/.aimaestro/agents/<agent-id>/`
- [ ] Initialize CozoDB relations (user_preferences, decisions, pending_items, availability_state, session_handoffs)
- [ ] Create fallback `thoughts/shared/handoffs/amama/` directory structure
- [ ] Initialize fallback files (current.md, user-preferences.md, decision-log.md, pending-items.md)
- [ ] Implement CozoDB-first session start retrieval with file fallback
- [ ] Implement subconscious memory semantic search on session start
- [ ] Implement preference detection and dual-write (CozoDB + fallback)
- [ ] Implement decision logging with CozoDB + fallback
- [ ] Implement availability state tracking
- [ ] Implement pending item management
- [ ] Implement handoff document creation (CozoDB + fallback)
- [ ] Implement long-term memory consolidation trigger
- [ ] Implement fallback-to-CozoDB sync on recovery
- [ ] Test session continuity across compaction
- [ ] Test CozoDB failure and fallback path
- [ ] Test semantic search retrieval of implicit preferences
- [ ] Test cross-agent memory (preferences from AMIA/AMAA/AMOA)
- [ ] Test GitHub issue context integration

## Output

| Output Type | Format | When Generated |
|-------------|--------|----------------|
| Session restored message | Markdown summary of loaded context (indicates storage tier) | At session start |
| Preference recorded confirmation | "Noted: brief responses preferred" | When preference detected |
| Decision logged confirmation | "Recorded: PostgreSQL approved (CozoDB ID: abc-123)" | When user makes decision |
| Availability state change | "Understood - I'll queue items" | When user indicates away/DND |
| Handoff record | CozoDB session_handoffs entry + fallback markdown file | At session end or compaction |
| Pending items reminder | List of items needing attention | When resuming or user asks |
| Memory consolidation report | Summary of stabilized preferences | After long-term consolidation |
| Fallback sync status | "CozoDB restored - synced N file-based records" | After recovery from outage |

## Examples

Six detailed examples covering all major operations are provided in the reference document: session start with CozoDB, session start with fallback, preference detection, decision recording, availability state changes, and semantic search for implicit preferences.

See [references/examples.md](references/examples.md) for the full examples.
  - Example 1: Session Start with AI Maestro Memory
  - Example 2: Session Start with Fallback
  - Example 3: Detecting and Recording Preference

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| CozoDB unavailable | Service down or first-time setup | Switch to file-based fallback, log warning |
| CozoDB write failure | Disk full or corruption | Retry once, then fall back to file-based |
| Fallback directory not found | First session or deleted | Create directory structure |
| Fallback file corrupted | Write failure or manual edit | Use CozoDB as source of truth, regenerate files |
| Semantic search timeout | Subconscious indexing lagging | Proceed without semantic results, use CozoDB structured data |
| Conflicting preferences | User changed mind | Most recent preference wins; consolidation resolves conflicts |
| CozoDB/file state divergence | Outage caused split-brain | CozoDB is authoritative; sync file state to match CozoDB |
| Stale pending items | Items no longer relevant | Long-term consolidation flags these; prompt user to confirm or remove |
| GitHub context unavailable | API failure or private repo | Rely on CozoDB and fallback documents only |
| Memory too large | Too much history | Long-term consolidation archives old entries, keeps summaries |
| Cross-agent memory conflict | Different agents recorded contradictory preferences | Most recent timestamp wins; flag for user confirmation |

## Resources

- **AGENT_OPERATIONS.md** - Core agent operational patterns
- **amama-approval-workflows** - Approval decision patterns
- **amama-user-communication** - Communication patterns
- **amama-role-routing** - Role handoff patterns
- **amama-status-reporting** - Status report generation
- **AI Maestro CozoDB documentation** - `~/.aimaestro/docs/memory-system.md`
- **Subconscious memory API** - `$AIMAESTRO_API/api/memory/` endpoints

### Reference Documents

- [references/record-keeping-formats.md](references/record-keeping-formats.md) - Session record-keeping formats
  - Contents
  - Overview
  - Project Registry
  - Approval Log
- [references/memory-triggers.md](references/memory-triggers.md) - Detailed retrieval and update trigger patterns with API examples
  - Memory Retrieval Triggers
  - Memory Update Triggers
- [references/handoff-format.md](references/handoff-format.md) - Handoff document templates and CozoDB write format
  - Handoff Document Format
  - CozoDB Handoff Record
  - Fallback Handoff Document Structure
  - Handoff Best Practices
- [references/examples.md](references/examples.md) - Six detailed session memory operation examples
  - Example 1: Session Start with AI Maestro Memory
  - Example 2: Session Start with Fallback
  - Example 3: Detecting and Recording Preference

---

**Version**: 2.2.0
**Last Updated**: 2026-02-27
**Target Audience**: AI Maestro Assistant Manager Agent
**Difficulty Level**: Intermediate
