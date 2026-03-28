# Memory Architecture Reference

Detailed architecture of the AMAMA session memory tiered storage system and data types.

## Contents

- [Tiered Storage Architecture](#tiered-storage-architecture)
- [Tier 1: AI Maestro CozoDB Agent Database](#tier-1-ai-maestro-cozodb-agent-database)
- [Tier 2: Subconscious Memory Indexing](#tier-2-subconscious-memory-indexing)
- [Tier 3: Long-Term Memory Consolidation](#tier-3-long-term-memory-consolidation)
- [Tier 4: File-Based Handoff Documents (Fallback)](#tier-4-file-based-handoff-documents-fallback)
- [Secondary: GitHub Issue Comments](#secondary-github-issue-comments)
- [Data Types Stored](#data-types-stored)

## Tiered Storage Architecture

AMAMA session memory uses a tiered storage architecture with AI Maestro as the primary backend and file-based handoffs as fallback.

### Tier 1: AI Maestro CozoDB Agent Database

**Location**: `$AGENT_DIR/db/memory.cozo`

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

### Tier 4: File-Based Handoff Documents (Fallback)

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

---

## Data Types Stored

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
