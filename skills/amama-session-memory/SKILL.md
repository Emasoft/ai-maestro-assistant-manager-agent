---
name: amama-session-memory
description: User preference and communication style persistence via AI Maestro memory system. Use when restoring user context, tracking decisions, or managing availability states. Trigger with session start.
version: 2.0.0
license: MIT
compatibility: Requires AI Maestro installed.
metadata:
  author: Emasoft
context: fork
agent: amama-main
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

AI Maestro's CozoDB stores structured memory records with semantic indexing. Each memory entry is a typed relation:

| Relation | Schema | Purpose |
|----------|--------|---------|
| `user_preferences` | `(key: String, value: String, source: String, timestamp: DateTime)` | Communication style, format, verbosity |
| `decisions` | `(id: Uuid, context: String, decision: String, reason: String, related_issues: [String], timestamp: DateTime)` | Approval history |
| `pending_items` | `(id: Uuid, type: String, description: String, priority: String, created: DateTime, deadline: DateTime?)` | Items awaiting user action |
| `availability_state` | `(state: String, since: DateTime, notes: String)` | Current user availability |
| `session_handoffs` | `(session_id: String, summary: String, resume_instructions: String, timestamp: DateTime)` | Session continuity data |

**Why CozoDB**: Supports Datalog queries for complex relationship traversal, built-in vector search for semantic memory retrieval, and transactional writes for consistency.

### Tier 2: Subconscious Memory Indexing

AI Maestro's subconscious memory system automatically indexes conversation history into a semantic search index. AMAMA leverages this for:

- **Implicit preference detection**: Searching past conversations for patterns like repeated format choices, tone corrections, or decision styles without AMAMA having explicitly recorded them.
- **Decision context retrieval**: When a decision was made in a conversation but not formally logged, semantic search over history can recover the context.
- **Cross-agent memory**: Preferences expressed to other agents (EIA, EAA, EOA) are indexed and accessible to AMAMA.

**Query interface**:
```bash
# Semantic search over conversation history
curl -s "$AIMAESTRO_API/api/memory/search" \
  -H "Content-Type: application/json" \
  -d '{"agent": "'$SESSION_NAME'", "query": "user preference for response format", "limit": 5}'
```

### Tier 3: Long-Term Memory Consolidation

AI Maestro periodically consolidates short-term memory entries into long-term summaries. AMAMA benefits from:

- **Preference stabilization**: Temporary preferences that persist across multiple sessions get promoted to stable preferences with higher confidence scores.
- **Decision pattern recognition**: Consolidated view of decision history reveals patterns (e.g., "user consistently favors simplicity over feature richness").
- **Stale item cleanup**: Pending items that remain unresolved beyond a configurable threshold are flagged for review or archival.

Consolidation runs automatically via AI Maestro's background scheduler. AMAMA can trigger manual consolidation:
```bash
curl -X POST "$AIMAESTRO_API/api/memory/consolidate" \
  -H "Content-Type: application/json" \
  -d '{"agent": "'$SESSION_NAME'", "scope": "user_preferences"}'
```

### Tier 4 (Fallback): File-Based Handoff Documents

**Location**: `thoughts/shared/handoffs/amama/`

When AI Maestro's CozoDB is unavailable (service down, first-time setup, or recovery), AMAMA falls back to file-based storage:

```
thoughts/shared/handoffs/amama/
  current.md              # Current session state
  user-preferences.md     # Accumulated user preferences
  decision-log.md         # Historical decisions
  pending-items.md        # Items awaiting user action
```

**Fallback detection**: On session start, AMAMA checks CozoDB connectivity. If unavailable, it logs a warning and uses file-based storage. When CozoDB becomes available again, file-based state is synced back into CozoDB.

### Secondary: GitHub Issue Comments

**Location**: Comments on open issues with `amama-context` label.

**Use Case**: When working on a specific issue, AMAMA records user decisions and preferences as issue comments to preserve context within the GitHub thread.

**Format in Issue Comments**:
```markdown
<!-- AMAMA-CONTEXT
user_preference: prefers detailed error messages
decision: approved retry logic with exponential backoff
pending: awaiting input on max retry count
availability_state: active
-->
```

## What AMAMA Session Memory Stores

AMAMA session memory is structured around the user relationship, not technical task state.

### 1. User Preferences and Communication Style

Data that helps AMAMA communicate in ways the user prefers:

| Preference Type | Example Data | Why Stored |
|-----------------|--------------|------------|
| Verbosity level | "prefers concise responses" | Avoid over-explaining |
| Technical depth | "wants implementation details" | Match expertise level |
| Format preference | "likes bullet points over prose" | Match reading style |
| Language quirks | "uses 'ship it' to mean 'approve'" | Understand user jargon |
| Communication channel | "prefers GitHub comments over chat" | Route responses correctly |

**CozoDB write**:
```bash
curl -X POST "$AIMAESTRO_API/api/memory/store" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "'$SESSION_NAME'",
    "relation": "user_preferences",
    "data": {"key": "verbosity", "value": "concise", "source": "explicit", "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}
  }'
```

### 2. Previous Decisions and Approvals

Historical record of user decisions to avoid re-asking:

| Decision Type | Example Data | Why Stored |
|---------------|--------------|------------|
| Architecture approvals | "approved microservices pattern for auth" | Avoid re-proposing |
| Tool selections | "chose PostgreSQL over MySQL" | Remember constraints |
| Style decisions | "prefers function-based over class-based" | Maintain consistency |
| Scope decisions | "deferred OAuth until Phase 2" | Track deferrals |
| Rejection reasons | "rejected Redis caching due to cost" | Avoid repeating proposals |

### 3. Pending Items Requiring User Attention

Items waiting for user input or action:

| Pending Type | Example Data | Why Stored |
|--------------|--------------|------------|
| Unanswered questions | "waiting for database schema preference" | Resume asking |
| Deferred decisions | "OAuth scope question deferred to later" | Re-raise appropriately |
| Review requests | "PR #45 awaiting user review" | Track open items |
| Approval requests | "deploy to staging pending approval" | Remind when appropriate |
| Blockers needing user | "external API key needed from user" | Track dependencies |

### 4. User Availability States

State-based availability tracking (not time-based):

| State | Description | AMAMA Behavior |
|-------|-------------|---------------|
| `active` | User is actively engaged | Full interaction, ask questions freely |
| `monitoring` | User is available but not actively working | Batch non-urgent items, summarize |
| `away` | User is temporarily unavailable | Queue items, avoid interruptions |
| `do-not-disturb` | User explicitly requested no interruptions | Only critical escalations |
| `unknown` | Availability not established | Assume monitoring, ask if needed |

## Memory Retrieval Triggers

AMAMA retrieves session memory based on state changes, not time intervals.

### Trigger 1: Session Start

**Condition**: AMAMA agent initializes or resumes after compaction.

**Actions**:
1. Check CozoDB connectivity at `~/.aimaestro/agents/<agent-id>/`
2. If CozoDB available:
   a. Query `session_handoffs` for latest handoff record
   b. Query `user_preferences` for all active preferences
   c. Query `pending_items` for unresolved items
   d. Query `availability_state` for current state
   e. Run semantic search for any recent preference changes from other agents
3. If CozoDB unavailable (fallback):
   a. Read `thoughts/shared/handoffs/amama/current.md`
   b. Load user preferences from `user-preferences.md`
   c. Check `pending-items.md` for items needing attention
   d. Restore user availability state
4. Report loaded context to user if preferences indicate

**Example**:
```markdown
## Session Restored

I've loaded your previous context (via AI Maestro memory):
- You prefer concise responses
- Pending: database schema choice (deferred)
- Last state: monitoring
- Cross-agent note: EAA recorded you prefer modular designs

Would you like to continue where we left off?
```

### Trigger 2: Role Routing Request

**Condition**: User sends a request that AMAMA must route to another role.

**Actions**:
1. Query CozoDB `decisions` relation for relevant prior decisions
2. Query CozoDB `pending_items` for related pending items
3. Run semantic search for related conversation context
4. Include context in handoff to target role
5. Record routing decision

### Trigger 3: GitHub Issue Context

**Condition**: User references a GitHub issue number.

**Actions**:
1. Query CozoDB for decisions linked to the issue number
2. Query issue for AMAMA-CONTEXT comments
3. Run semantic search for conversations mentioning the issue
4. Merge all sources (CozoDB takes precedence, then semantic, then GitHub comments)
5. Apply context to current interaction

### Trigger 4: Approval Request

**Condition**: AMAMA needs to request user approval.

**Actions**:
1. Query CozoDB `decisions` for similar past decisions
2. Run semantic search for related past conversations
3. Check if item was previously deferred in `pending_items`
4. Adapt request based on user communication style from `user_preferences`
5. Record approval or rejection when received

## Memory Update Triggers

AMAMA updates session memory based on user actions, not time intervals.

### Trigger 1: User Expresses Preference

**Condition**: User indicates communication or decision preference.

**Detection Signals**:
- "I prefer..." statements
- Corrections to AMAMA behavior ("don't ask me every time")
- Repeated patterns in responses (always choosing same option)

**Actions**:
1. Extract preference
2. Write to CozoDB `user_preferences` relation (or fallback to `user-preferences.md`)
3. Index the conversation snippet via subconscious memory for future semantic search
4. Apply immediately to current session
5. Confirm understanding if preference is major

**Example CozoDB Write**:
```bash
curl -X POST "$AIMAESTRO_API/api/memory/store" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "'$SESSION_NAME'",
    "relation": "user_preferences",
    "data": {"key": "response_length", "value": "concise", "source": "explicit-2025-01-30", "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}
  }'
```

**Fallback file update** (`user-preferences.md`):
```markdown
## User Preferences - Updated

### Communication Style
- Response length: concise (expressed 2025-01-30)
- Technical depth: implementation-level (inferred from responses)
- Format: bullet points preferred (expressed 2025-01-28)
```

### Trigger 2: User Makes Decision

**Condition**: User approves, rejects, or defers something.

**Actions**:
1. Record decision in CozoDB `decisions` relation (or fallback to `decision-log.md`)
2. If deferred, add to CozoDB `pending_items` (or fallback to `pending-items.md`)
3. If rejection, record reason for future reference
4. Update any related pending items
5. Index via subconscious memory for semantic retrieval

**Example CozoDB Write**:
```bash
curl -X POST "$AIMAESTRO_API/api/memory/store" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "'$SESSION_NAME'",
    "relation": "decisions",
    "data": {
      "id": "'$(uuidgen)'",
      "context": "Architect proposed PostgreSQL vs MySQL for user data",
      "decision": "APPROVED PostgreSQL",
      "reason": "We need JSON support and better concurrent writes",
      "related_issues": ["#45", "#47"],
      "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
    }
  }'
```

**Fallback Decision Log Entry** (`decision-log.md`):
```markdown
## Decision: Database Selection - 2025-01-30

**Context**: Architect proposed PostgreSQL vs MySQL for user data
**Decision**: APPROVED PostgreSQL
**Reason**: "We need JSON support and better concurrent writes"
**Constraints Added**: Must use pgvector for embeddings
**Related Issues**: #45, #47
```

### Trigger 3: User Availability Changes

**Condition**: User indicates availability state change.

**Detection Signals**:
- Explicit statements ("I'll be away for a bit")
- Response patterns (no responses for extended period indicates away)
- Return statements ("I'm back")
- DND requests ("don't interrupt me unless critical")

**Actions**:
1. Update CozoDB `availability_state` relation (or fallback to `current.md`)
2. Adjust AMAMA behavior accordingly
3. Queue or release pending items based on state

### Trigger 4: Pending Item Resolution

**Condition**: Pending item is addressed (answered, decided, or cancelled).

**Actions**:
1. Remove from CozoDB `pending_items` (or fallback `pending-items.md`)
2. If decision made, add to CozoDB `decisions` (or fallback `decision-log.md`)
3. Update related items if dependencies exist
4. Notify user of resolution if requested

### Trigger 5: Session End or Compaction Warning

**Condition**: Session is ending or context approaching limit.

**Actions**:
1. Write all in-memory state to CozoDB `session_handoffs` relation
2. Ensure `pending_items` is current in CozoDB
3. Trigger subconscious memory indexing for the current session
4. Also write fallback handoff documents for resilience:
   a. Write `thoughts/shared/handoffs/amama/current.md`
   b. Sync `pending-items.md` from CozoDB state
5. Validate all writes succeeded

## Handoff Document Creation

When AMAMA session ends or context compacts, a handoff record ensures continuity. The primary handoff is stored in CozoDB; a file-based copy is written as fallback.

### CozoDB Handoff Record

```bash
curl -X POST "$AIMAESTRO_API/api/memory/store" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "'$SESSION_NAME'",
    "relation": "session_handoffs",
    "data": {
      "session_id": "amama-20250130-001",
      "summary": "User active on auth-module. PostgreSQL approved. 3 pending items.",
      "resume_instructions": "Check pending DB schema choice. Maintain concise style. User prefers LGTM for approvals.",
      "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
    }
  }'
```

### Fallback Handoff Document Structure

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

### Handoff Best Practices

1. **Be Specific**: Include issue numbers, file paths, CozoDB record IDs
2. **Be Current**: Write to CozoDB before every potential compaction
3. **Be Minimal**: Only essential context, not full history
4. **Be Actionable**: Include "Resume Instructions" section
5. **Be Linked**: Reference CozoDB relations for details
6. **Be Redundant**: Always write fallback files alongside CozoDB

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

**Checklist for session memory management**:

Copy this checklist and track your progress:

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
- [ ] Test cross-agent memory (preferences from EIA/EAA/EOA)
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

## Task Checklist

Copy this checklist to track implementation:

- [ ] Verify CozoDB agent database at `~/.aimaestro/agents/<agent-id>/`
- [ ] Initialize CozoDB relations
- [ ] Create fallback `thoughts/shared/handoffs/amama/` directory structure
- [ ] Initialize fallback files with empty sections
- [ ] Implement CozoDB-first retrieval with file fallback
- [ ] Implement subconscious memory semantic search
- [ ] Implement preference detection and dual-write
- [ ] Implement decision logging (CozoDB + fallback)
- [ ] Implement availability state tracking
- [ ] Implement pending item management
- [ ] Implement handoff creation (CozoDB + fallback)
- [ ] Implement long-term consolidation trigger
- [ ] Implement fallback-to-CozoDB sync
- [ ] Test session continuity across compaction
- [ ] Test CozoDB failure and fallback path
- [ ] Test semantic search and cross-agent memory
- [ ] Test GitHub issue context integration

## Examples

### Example 1: Session Start with AI Maestro Memory

**Scenario**: AMAMA starts and CozoDB is available with previous session data.

```markdown
## Session Restored (via AI Maestro Memory)

I've loaded your context from AI Maestro's agent database:

**Your Preferences** (from CozoDB):
- Concise responses preferred (stable - 5 sessions)
- High technical detail (stable - 3 sessions)

**Cross-Agent Insights** (from subconscious memory):
- EAA noted you prefer modular architecture patterns
- EOA recorded you like task breakdowns in checklists

**Pending Items**:
- Database schema choice (deferred)
- PR #47 awaiting your review

**Recent Decisions**:
- PostgreSQL approved for user data (ID: abc-123)

Would you like to address the pending items, or continue with something else?
```

### Example 2: Session Start with Fallback

**Scenario**: AMAMA starts but CozoDB is unavailable.

```markdown
## Session Restored (file fallback - CozoDB unavailable)

I've loaded your context from handoff documents:

**Your Preferences**:
- Concise responses preferred
- High technical detail

**Pending Items**:
- Database schema choice (deferred)
- PR #47 awaiting your review

Note: AI Maestro memory is currently unavailable. Using file-based fallback.
I'll sync back to CozoDB when it becomes available.
```

### Example 3: Detecting and Recording Preference

**User Input**: "Can you be more brief? I don't need all the explanation."

**AMAMA Actions**:
1. Detect preference expression
2. Write to CozoDB:
   ```bash
   curl -X POST "$AIMAESTRO_API/api/memory/store" \
     -d '{"agent": "amama-main", "relation": "user_preferences", "data": {"key": "response_length", "value": "concise", "source": "explicit"}}'
   ```
3. Write fallback to `user-preferences.md`:
   ```markdown
   ### Communication Style
   - Response length: brief/concise (expressed 2025-01-30)
   ```
4. Respond briefly:
   ```markdown
   Got it - keeping responses brief from now on.
   ```

### Example 4: Recording Decision with Context

**User Input**: "Let's go with PostgreSQL. We need the JSON support."

**AMAMA Actions**:
1. Record in CozoDB `decisions` relation with full context
2. Write fallback to `decision-log.md`
3. Remove from CozoDB `pending_items` if it was pending
4. Index via subconscious memory
5. Acknowledge:
   ```markdown
   Noted: PostgreSQL selected for user data (JSON support). Decision ID: abc-123.
   ```

### Example 5: Availability State Change

**User Input**: "I need to step away for a while. Don't wait for me on the PR reviews."

**AMAMA Actions**:
1. Update CozoDB `availability_state`:
   ```bash
   curl -X POST "$AIMAESTRO_API/api/memory/store" \
     -d '{"agent": "amama-main", "relation": "availability_state", "data": {"state": "away", "since": "2025-01-30T15:00:00Z", "notes": "Stepping away, do not wait on PR reviews"}}'
   ```
2. Update fallback `current.md`
3. Adjust behavior:
   - Queue non-critical items
   - Proceed with autonomous work where possible
4. Acknowledge:
   ```markdown
   Understood - I'll continue with autonomous work and queue items for your return.
   ```

### Example 6: Semantic Search for Implicit Preferences

**Scenario**: User never explicitly stated a preference, but AMAMA needs to know.

```bash
# Query subconscious memory for format preferences
curl -s "$AIMAESTRO_API/api/memory/search" \
  -d '{"agent": "amama-main", "query": "user preferred output format for status reports", "limit": 3}'

# Returns conversation snippets where user reacted to different formats
# AMAMA infers: user consistently engaged more with tabular formats
```

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

---

**Version**: 2.0.0
**Last Updated**: 2026-02-27
**Target Audience**: AI Maestro Assistant Manager Agent
**Difficulty Level**: Intermediate
