---
name: eama-session-memory
description: User preference and communication style persistence. Use when restoring user context, tracking decisions, or managing availability states. Trigger with session start.
version: 1.0.0
license: MIT
compatibility: Requires file system access to handoff documents and GitHub issue comments for persistence. Requires AI Maestro installed.
metadata:
  author: Emasoft
context: fork
agent: eama-main
user-invocable: false
triggers:
  - when session starts and user context must be restored
  - when user expresses preferences or communication style
  - when approval decisions are made
  - when user availability state changes
  - when session ends and handoff document must be created
---

# EAMA Session Memory Skill

## Overview

Session memory for the Emasoft Assistant Manager Agent (EAMA) serves a unique purpose: maintaining continuity in the user relationship across sessions. Unlike orchestration memory that tracks tasks and patterns, EAMA session memory focuses on user-centric data that enables the assistant to communicate effectively with the user regardless of context compaction or session interruptions.

**Purpose**: Enable EAMA to remember the user across sessions, maintaining relationship continuity and avoiding repetitive clarification requests.

**Scope**: User preferences, communication style, approval history, pending items, and availability states.

## Prerequisites

1. File system access to create and maintain handoff documents directory (`thoughts/shared/handoffs/eama/`)
2. GitHub API access for issue comment persistence (optional but recommended)
3. Understanding of EAMA role as user-facing communication agent
4. Familiarity with context compaction and session continuity concepts

## What EAMA Session Memory Stores

EAMA session memory is structured around the user relationship, not technical task state.

### 1. User Preferences and Communication Style

Data that helps EAMA communicate in ways the user prefers:

| Preference Type | Example Data | Why Stored |
|-----------------|--------------|------------|
| Verbosity level | "prefers concise responses" | Avoid over-explaining |
| Technical depth | "wants implementation details" | Match expertise level |
| Format preference | "likes bullet points over prose" | Match reading style |
| Language quirks | "uses 'ship it' to mean 'approve'" | Understand user jargon |
| Communication channel | "prefers GitHub comments over chat" | Route responses correctly |

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

| State | Description | EAMA Behavior |
|-------|-------------|---------------|
| `active` | User is actively engaged | Full interaction, ask questions freely |
| `monitoring` | User is available but not actively working | Batch non-urgent items, summarize |
| `away` | User is temporarily unavailable | Queue items, avoid interruptions |
| `do-not-disturb` | User explicitly requested no interruptions | Only critical escalations |
| `unknown` | Availability not established | Assume monitoring, ask if needed |

## Memory Storage Locations

EAMA stores session memory in two persistent locations.

### Primary: Handoff Documents

**Location**: `thoughts/shared/handoffs/eama/`

**Structure**:
```
thoughts/shared/handoffs/eama/
  current.md              # Current session state
  user-preferences.md     # Accumulated user preferences
  decision-log.md         # Historical decisions
  pending-items.md        # Items awaiting user action
```

**Why Handoff Documents**: They survive context compaction, are human-readable, and can be shared across EAMA sessions.

### Secondary: GitHub Issue Comments

**Location**: Comments on open issues with `eama-context` label.

**Use Case**: When working on a specific issue, EAMA records user decisions and preferences as issue comments to preserve context within the GitHub thread.

**Format in Issue Comments**:
```markdown
<!-- EAMA-CONTEXT
user_preference: prefers detailed error messages
decision: approved retry logic with exponential backoff
pending: awaiting input on max retry count
availability_state: active
-->
```

## Memory Retrieval Triggers

EAMA retrieves session memory based on state changes, not time intervals.

### Trigger 1: Session Start

**Condition**: EAMA agent initializes or resumes after compaction.

**Actions**:
1. Read `thoughts/shared/handoffs/eama/current.md`
2. Load user preferences from `user-preferences.md`
3. Check `pending-items.md` for items needing attention
4. Restore user availability state
5. Report loaded context to user if preferences indicate

**Example**:
```markdown
## Session Restored

I've loaded your previous context:
- You prefer concise responses
- Pending: database schema choice (deferred)
- Last state: monitoring

Would you like to continue where we left off?
```

### Trigger 2: Role Routing Request

**Condition**: User sends a request that EAMA must route to another role.

**Actions**:
1. Check decision-log.md for relevant prior decisions
2. Check pending-items.md for related pending items
3. Include context in handoff to target role
4. Record routing decision

### Trigger 3: GitHub Issue Context

**Condition**: User references a GitHub issue number.

**Actions**:
1. Query issue for EAMA-CONTEXT comments
2. Extract user preferences and decisions
3. Merge with session preferences (issue-specific takes precedence)
4. Apply context to current interaction

### Trigger 4: Approval Request

**Condition**: EAMA needs to request user approval.

**Actions**:
1. Check decision-log.md for similar past decisions
2. Check if item was previously deferred
3. Adapt request based on user communication style
4. Record approval or rejection when received

## Memory Update Triggers

EAMA updates session memory based on user actions, not time intervals.

### Trigger 1: User Expresses Preference

**Condition**: User indicates communication or decision preference.

**Detection Signals**:
- "I prefer..." statements
- Corrections to EAMA behavior ("don't ask me every time")
- Repeated patterns in responses (always choosing same option)

**Actions**:
1. Extract preference
2. Update user-preferences.md
3. Apply immediately to current session
4. Confirm understanding if preference is major

**Example Update**:
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
1. Record decision in decision-log.md with context
2. If deferred, add to pending-items.md
3. If rejection, record reason for future reference
4. Update any related pending items

**Example Decision Log Entry**:
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
1. Update availability state in current.md
2. Adjust EAMA behavior accordingly
3. Queue or release pending items based on state

### Trigger 4: Pending Item Resolution

**Condition**: Pending item is addressed (answered, decided, or cancelled).

**Actions**:
1. Remove from pending-items.md
2. If decision made, add to decision-log.md
3. Update related items if dependencies exist
4. Notify user of resolution if requested

### Trigger 5: Session End or Compaction Warning

**Condition**: Session is ending or context approaching limit.

**Actions**:
1. Write all in-memory state to handoff documents
2. Ensure pending-items.md is current
3. Create handoff summary in current.md
4. Validate all files are written successfully

## Handoff Document Creation

When EAMA session ends or context compacts, a handoff document ensures continuity.

### Handoff Document Structure

**File**: `thoughts/shared/handoffs/eama/current.md`

```markdown
# EAMA Session Handoff

## Session Metadata
- Session ID: eama-20250130-001
- Last Updated: 2025-01-30
- Previous Session: eama-20250129-003

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
- 2025-01-30: Approved PostgreSQL for user data (see decision-log.md)
- 2025-01-29: Approved microservices pattern (see decision-log.md)

## Communication Notes
- User prefers concise responses
- Technical detail level: high
- Prefers bullet points over paragraphs
- Uses "LGTM" for lightweight approvals

## Resume Instructions
When resuming:
1. Check pending-items.md for items that may need attention
2. Reference recent decisions before proposing alternatives
3. Maintain concise communication style
4. Check if user availability has changed
```

### Handoff Document Best Practices

1. **Be Specific**: Include issue numbers, file paths, decision IDs
2. **Be Current**: Update before every potential compaction
3. **Be Minimal**: Only essential context, not full history
4. **Be Actionable**: Include "Resume Instructions" section
5. **Be Linked**: Reference other files for details

## Instructions

Follow these steps to maintain session memory:

1. **Initialize memory structure** - Create handoff directory structure on first use
2. **Load context on session start** - Read handoff documents and restore user preferences
3. **Detect user preferences** - Listen for preference expressions and communication patterns
4. **Record decisions** - Log all user approvals, rejections, and deferrals
5. **Track pending items** - Maintain list of items awaiting user attention
6. **Monitor availability state** - Detect and respond to user availability changes
7. **Update handoff documents** - Write memory to disk before session end or compaction
8. **Validate continuity** - Ensure next session can resume seamlessly

**Checklist for session memory management**:

Copy this checklist and track your progress:

- [ ] Create `thoughts/shared/handoffs/eama/` directory structure
- [ ] Initialize `current.md` with session metadata
- [ ] Initialize `user-preferences.md` with empty sections
- [ ] Initialize `decision-log.md` with header
- [ ] Initialize `pending-items.md` with empty sections
- [ ] Implement session start retrieval trigger
- [ ] Implement preference detection and recording
- [ ] Implement decision logging
- [ ] Implement availability state tracking
- [ ] Implement pending item management
- [ ] Implement handoff document creation
- [ ] Test session continuity across compaction
- [ ] Test GitHub issue context integration

## Output

| Output Type | Format | When Generated |
|-------------|--------|----------------|
| Session restored message | Markdown summary of loaded context | At session start |
| Preference recorded confirmation | "Noted: brief responses preferred" | When preference detected |
| Decision logged confirmation | "Recorded: PostgreSQL approved" | When user makes decision |
| Availability state change | "Understood - I'll queue items" | When user indicates away/DND |
| Handoff document | Structured markdown file | At session end or compaction |
| Pending items reminder | List of items needing attention | When resuming or user asks |

## Task Checklist

Copy this checklist to track implementation:

- [ ] Create `thoughts/shared/handoffs/eama/` directory structure
- [ ] Initialize `current.md` with session metadata
- [ ] Initialize `user-preferences.md` with empty sections
- [ ] Initialize `decision-log.md` with header
- [ ] Initialize `pending-items.md` with empty sections
- [ ] Implement session start retrieval trigger
- [ ] Implement preference detection and recording
- [ ] Implement decision logging
- [ ] Implement availability state tracking
- [ ] Implement pending item management
- [ ] Implement handoff document creation
- [ ] Test session continuity across compaction
- [ ] Test GitHub issue context integration

## Examples

### Example 1: Session Start with Restored Context

**Scenario**: EAMA starts and finds previous session data.

```markdown
## Session Restored

I've loaded your context from our previous session:

**Your Preferences**:
- Concise responses preferred
- High technical detail

**Pending Items**:
- Database schema choice (deferred)
- PR #47 awaiting your review

**Recent Decisions**:
- PostgreSQL approved for user data

Would you like to address the pending items, or continue with something else?
```

### Example 2: Detecting and Recording Preference

**User Input**: "Can you be more brief? I don't need all the explanation."

**EAMA Actions**:
1. Detect preference expression
2. Update user-preferences.md:
   ```markdown
   ### Communication Style
   - Response length: brief/concise (expressed 2025-01-30)
   ```
3. Respond briefly:
   ```markdown
   Got it - keeping responses brief from now on.
   ```

### Example 3: Recording Decision with Context

**User Input**: "Let's go with PostgreSQL. We need the JSON support."

**EAMA Actions**:
1. Record in decision-log.md:
   ```markdown
   ## Decision: Database Selection - 2025-01-30

   **Decision**: APPROVED PostgreSQL
   **Reason**: "We need the JSON support"
   **Context**: User data storage for authentication module
   **Related Issues**: #45
   ```
2. Remove from pending-items.md if it was pending
3. Acknowledge:
   ```markdown
   Noted: PostgreSQL selected for user data (JSON support).
   ```

### Example 4: Availability State Change

**User Input**: "I need to step away for a while. Don't wait for me on the PR reviews."

**EAMA Actions**:
1. Update current.md:
   ```markdown
   ## User State
   - Availability: away
   - Last Interaction: indicated stepping away
   ```
2. Adjust behavior:
   - Queue non-critical items
   - Proceed with autonomous work where possible
3. Acknowledge:
   ```markdown
   Understood - I'll continue with autonomous work and queue items for your return.
   ```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Handoff directory not found | First session or deleted | Create directory structure |
| Handoff file corrupted | Write failure or manual edit | Use backup or reinitialize |
| Conflicting preferences | User changed mind | Most recent preference wins |
| Stale pending items | Items no longer relevant | Prompt user to confirm or remove |
| GitHub context unavailable | API failure or private repo | Rely on handoff documents only |
| Memory files too large | Too much history | Archive old decisions, keep recent |

## Resources

- **AGENT_OPERATIONS.md** - Core agent operational patterns
- **eama-approval-workflows** - Approval decision patterns
- **eama-user-communication** - Communication patterns
- **eama-role-routing** - Role handoff patterns
- **eama-status-reporting** - Status report generation

### Reference Documents

- [references/record-keeping-formats.md](references/record-keeping-formats.md) - Session record-keeping formats

---

**Version**: 1.0.0
**Last Updated**: 2025-02-04
**Target Audience**: Emasoft Assistant Manager Agent
**Difficulty Level**: Intermediate
