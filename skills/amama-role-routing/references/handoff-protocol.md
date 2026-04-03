# Handoff Protocol

## Table of Contents
- [Steps](#steps)
- [File Naming Convention](#file-naming-convention)
- [Storage Location](#storage-location)
- [Checklist](#checklist)

## Steps

### Step 1: Identify Intent
```
Parse user message -> Identify primary intent -> Match to routing rule
```

### Step 2: Validate Handoff (CRITICAL)

Before creating and sending any handoff, complete this validation checklist:

#### Handoff Validation Checklist

Before sending handoff to AMCOS or specialist agents:

- [ ] **All required fields present** - Verify handoff contains: from, to, type, UUID, task description
- [ ] **UUID is unique** - Check against existing handoffs in `docs_dev/handoffs/` to prevent collisions
  ```bash
  # Verify UUID uniqueness
  ! grep -r "UUID: <new-uuid>" docs_dev/handoffs/ && echo "UUID is unique"
  ```
- [ ] **Target agent exists and is alive** - Send health ping before handoff using the `agent-messaging` skill
- [ ] **File is valid markdown** - No syntax errors, proper structure
- [ ] **File is readable by target agent** - Verify file permissions and path accessibility
- [ ] **No [TBD] placeholders** - All placeholder text must be replaced with actual values
  ```bash
  # Check for placeholder text
  ! grep -E "\[TBD\]|\[TODO\]|\[PLACEHOLDER\]|<fill-in>" handoff-file.md && echo "No placeholders found"
  ```
- [ ] **Task description is actionable** - Contains clear success criteria
- [ ] **Dependencies documented** - Any blocked-by or blocks relationships noted

#### Validation Failure Handling

| Failure | Resolution |
|---------|------------|
| Missing required field | Add missing field before proceeding |
| UUID collision | Generate new UUID |
| Target agent unavailable | Queue handoff, notify user, retry in 5 minutes |
| Invalid markdown | Fix syntax errors |
| Contains placeholders | Replace all [TBD] with actual values |
| Unclear task | Request clarification from user |

**NEVER send an invalid handoff.** An invalid handoff wastes agent resources and delays work.

### Step 3: Create Handoff Document
```
Generate UUID -> Create handoff-{uuid}-amama-to-{agent}.md -> Save to docs_dev/handoffs/
```

### Step 4: Send via AI Maestro
```
Compose message -> Set appropriate priority -> Send to agent session
```

### Step 5: Track Handoff
```
Log handoff in state -> Set status to "pending" -> Monitor for acknowledgment
```

### Step 6: Report to User
```
Confirm routing -> Provide tracking info -> Set expectation for response
```

## File Naming Convention

```
handoff-{uuid}-{from}-to-{to}.md

Examples:
- handoff-a1b2c3d4-amama-to-amcos.md   # AM delegates to AMCOS
- handoff-e5f6g7h8-amcos-to-amama.md   # AMCOS reports to AM
- handoff-i9j0k1l2-amcos-to-amaa.md    # AMCOS assigns to Architect agent
- handoff-m3n4o5p6-amaa-to-amcos.md    # Architect agent reports to AMCOS
- handoff-q7r8s9t0-amcos-to-amoa.md    # AMCOS assigns to Orchestrator agent
```

## Storage Location

All handoff files are stored in: `docs_dev/handoffs/`

## Checklist

Copy this checklist and track your progress:

- [ ] Parse user message to identify primary intent
- [ ] Match intent to routing rule using decision matrix
- [ ] Determine if handling directly or routing to specialist agent
- [ ] If routing: Generate UUID for handoff
- [ ] If routing: Create handoff document with all required fields
- [ ] If routing: Save handoff to `docs_dev/handoffs/`
- [ ] If routing: Send AI Maestro message to target agent session
- [ ] If routing: Track handoff status (set to "pending")
- [ ] Report routing decision to user
- [ ] Monitor for acknowledgment from target agent
- [ ] Update handoff status when acknowledged
