# Session Memory Examples

Detailed examples of AMAMA session memory operations.

## Contents

- [Example 1: Session Start with AI Maestro Memory](#example-1-session-start-with-ai-maestro-memory)
- [Example 2: Session Start with Fallback](#example-2-session-start-with-fallback)
- [Example 3: Detecting and Recording Preference](#example-3-detecting-and-recording-preference)
- [Example 4: Recording Decision with Context](#example-4-recording-decision-with-context)
- [Example 5: Availability State Change](#example-5-availability-state-change)
- [Example 6: Semantic Search for Implicit Preferences](#example-6-semantic-search-for-implicit-preferences)

## Example 1: Session Start with AI Maestro Memory

**Scenario**: AMAMA starts and CozoDB is available with previous session data.

```markdown
## Session Restored (via AI Maestro Memory)

I've loaded your context from AI Maestro's agent database:

**Your Preferences** (from CozoDB):
- Concise responses preferred (stable - 5 sessions)
- High technical detail (stable - 3 sessions)

**Cross-Agent Insights** (from subconscious memory):
- AMAA noted you prefer modular architecture patterns
- AMOA recorded you like task breakdowns in checklists

**Pending Items**:
- Database schema choice (deferred)
- PR #47 awaiting your review

**Recent Decisions**:
- PostgreSQL approved for user data (ID: abc-123)

Would you like to address the pending items, or continue with something else?
```

## Example 2: Session Start with Fallback

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

## Example 3: Detecting and Recording Preference

**User Input**: "Can you be more brief? I don't need all the explanation."

**AMAMA Actions**:
1. Detect preference expression
2. Write to file-based fallback `user-preferences.md`:
   ```markdown
   ### Communication Style
   - Response length: brief/concise (expressed 2025-01-30)
   ```
3. Respond briefly:
   ```markdown
   Got it - keeping responses brief from now on.
   ```

## Example 4: Recording Decision with Context

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

## Example 5: Availability State Change

**User Input**: "I need to step away for a while. Don't wait for me on the PR reviews."

**AMAMA Actions**:
1. Update file-based fallback `current.md` with availability state
2. Adjust behavior:
   - Queue non-critical items
   - Proceed with autonomous work where possible
3. Acknowledge:
   ```markdown
   Understood - I'll continue with autonomous work and queue items for your return.
   ```

## Example 6: Semantic Search for Implicit Preferences

**Scenario**: User never explicitly stated a preference, but AMAMA needs to know.

AMAMA queries the file-based subconscious memory for conversation snippets where the user reacted to different formats. Based on engagement patterns, AMAMA infers that the user consistently prefers tabular formats for status reports.
