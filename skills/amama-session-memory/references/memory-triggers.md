# Memory Triggers Reference

Detailed trigger/action patterns for AMAMA session memory retrieval and updates.

## Contents

- [Memory Retrieval Triggers](#memory-retrieval-triggers)
- [Memory Update Triggers](#memory-update-triggers)

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
- Cross-agent note: AMAA recorded you prefer modular designs

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
      "decision": "Selected PostgreSQL",
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
**Decision**: Selected PostgreSQL
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
