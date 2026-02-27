---
name: amama-role-routing
description: Use when routing user requests to appropriate specialist agents based on their skills/specialization. Routing is a plugin-level concern; AI Maestro governance roles are limited to manager, chief-of-staff, and member.
version: 2.0.0
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-main
user-invocable: false
triggers:
  - User submits a new request or task
  - Assistant Manager needs to delegate work
  - Handoff between specialist agents is required
---

# Role Routing Skill

## Overview

This skill provides the Assistant Manager (AMAMA) with decision logic for routing user requests to the appropriate specialist agent based on that agent's **skills and specialization** (a plugin-level concern).

### Governance Roles vs. Agent Specializations

AI Maestro defines exactly **3 governance roles**:

| Governance Role | Purpose |
|-----------------|---------|
| `manager` | Team manager with full administrative authority |
| `chief-of-staff` | Agent lifecycle, permissions, failure recovery |
| `member` | All other agents — the default role |

**Architect**, **Orchestrator**, and **Integrator** are NOT governance roles. They are **plugin-level specializations** expressed through agent skills, metadata, and tags. When creating or registering agents, always set `role: 'member'` for all non-COS agents. The specialization (architect, orchestrator, integrator) is conveyed via the agent's `skills` array and `tags` metadata, not the `role` field.

```jsonc
// CORRECT — specialization via skills/tags, governance role is 'member'
{
  "name": "amaa-architect",
  "role": "member",
  "skills": ["architecture", "design", "requirements-analysis"],
  "tags": ["specialization:architect"]
}

// WRONG — do NOT use specialization names as governance roles
{
  "name": "amaa-architect",
  "role": "architect"  // ← INVALID: not a governance role
}
```

## Prerequisites

- AI Maestro messaging system must be running
- All specialist agents (EAA, EOA, EIA) must be registered with `role: 'member'`
- `docs_dev/handoffs/` directory must exist and be writable
- UUID generation capability required

## Instructions

1. Parse user message to identify primary intent
2. Match intent to routing rule using the decision matrix
3. If handling directly (status, approval, clarification), respond immediately
4. If routing to a specialist agent, create handoff document with UUID
5. Save handoff to `docs_dev/handoffs/`
6. Send via AI Maestro to target agent session
7. Track handoff status and monitor for acknowledgment
8. Report routing decision to user

Specialist agents routed to:
- **EAA** — Agent with architect specialization (governance role: `member`)
- **EOA** — Agent with orchestrator specialization (governance role: `member`)
- **EIA** — Agent with integrator specialization (governance role: `member`)

## Output

| Routing Decision | Action Taken | Handoff File | Message Sent |
|------------------|--------------|--------------|--------------|
| Route to AMCOS | Create handoff document | `handoff-{uuid}-amama-to-amcos.md` | AI Maestro message to Chief of Staff |
| Route to EAA | Create handoff document | `handoff-{uuid}-amama-to-eaa.md` | AI Maestro message to Architect agent |
| Route to EOA | Create handoff document | `handoff-{uuid}-amama-to-eoa.md` | AI Maestro message to Orchestrator agent |
| Route to EIA | Create handoff document | `handoff-{uuid}-amama-to-eia.md` | AI Maestro message to Integrator agent |
| Handle Directly | Respond to user | None | None |
| Ambiguous Intent | Request clarification | None | None |

## Plugin Prefix Reference

| Specialization | Prefix | Plugin Name | Governance Role |
|----------------|--------|-------------|-----------------|
| Assistant Manager | `amama-` | AI Maestro Assistant Manager Agent | `manager` |
| Chief of Staff | `amcos-` | AI Maestro Chief of Staff | `chief-of-staff` |
| Architect | `amaa-` | AI Maestro Architect Agent | `member` |
| Orchestrator | `amoa-` | AI Maestro Orchestrator Agent | `member` |
| Integrator | `amia-` | AI Maestro Integrator Agent | `member` |

## Routing Decision Matrix

Routing is based on **agent specialization/skills**, not governance role. The governance role for all specialist agents is `member`.

| User Intent Pattern | Route To | Agent Specialization | Handoff Type |
|---------------------|----------|----------------------|--------------|
| "design", "plan", "architect", "spec", "requirements" | EAA | architect | task_assignment |
| "build", "implement", "create", "develop", "code" | EOA | orchestrator | task_assignment |
| "review", "test", "merge", "release", "deploy", "quality" | EIA | integrator | task_assignment |
| "spawn agent", "terminate agent", "restart session", "agent health" | AMCOS | chief-of-staff (governance) | agent_lifecycle |
| "status", "progress", "update" | Handle directly | — | none |
| "approve", "reject", "confirm" | Handle directly | — | approval_response |

## Detailed Routing Rules

### Route to EAA (Architect specialization, `role: member`) when:

1. **New project/feature design needed**
   - User says: "Design a...", "Plan how to...", "Create architecture for..."
   - Action: Create handoff with requirements, route to EAA agent session

2. **Requirements analysis required**
   - User says: "What do we need for...", "Analyze requirements for..."
   - Action: Create handoff with context, route to EAA agent session

3. **Technical specification needed**
   - User says: "Spec out...", "Document how...", "Define the API for..."
   - Action: Create handoff, route to EAA agent session

4. **Module planning required**
   - User says: "Break down...", "Modularize...", "Plan implementation of..."
   - Action: Create handoff, route to EAA agent session

### Route to EOA (Orchestrator specialization, `role: member`) when:

1. **Implementation ready to start**
   - Condition: Approved design/plan exists
   - Action: Create handoff with design docs, route to EOA agent session

2. **Task coordination needed**
   - User says: "Build...", "Implement...", "Start development..."
   - Action: Create handoff with requirements, route to EOA agent session

3. **Multi-agent work coordination**
   - Condition: Work requires multiple parallel agents
   - Action: Create handoff with task breakdown, route to EOA agent session

4. **Progress monitoring required**
   - Condition: Orchestration in progress, need intervention
   - Action: Forward message to EOA agent session

### Route to EIA (Integrator specialization, `role: member`) when:

1. **Work ready for integration**
   - Condition: Orchestrator agent signals completion
   - Action: Create handoff with completion report, route to EIA agent session

2. **Code review requested**
   - User says: "Review...", "Check the PR...", "Evaluate changes..."
   - Action: Create handoff with PR details, route to EIA agent session

3. **Quality gates needed**
   - User says: "Test...", "Validate...", "Run quality checks..."
   - Action: Create handoff, route to EIA agent session

4. **Release preparation**
   - User says: "Prepare release...", "Merge...", "Deploy..."
   - Action: Create handoff, route to EIA agent session

### Route to AMCOS (Chief of Staff — governance role: `chief-of-staff`) when:

1. **Agent lifecycle operations needed**
   - User says: "Spawn a new agent", "Create agent for...", "Start new session"
   - Action: Create handoff with agent requirements, route to AMCOS
   - **IMPORTANT**: When AMCOS creates new agents, it MUST set `role: 'member'` for all specialist agents. Specialization is expressed via `skills` and `tags`, never via the `role` field.

2. **Agent termination required**
   - User says: "Terminate agent", "Stop session", "Kill agent"
   - Action: Create handoff with agent ID, route to AMCOS

3. **Session management needed**
   - User says: "Restart agent", "Check agent health", "Agent status"
   - Action: Create handoff with session details, route to AMCOS

4. **Permission management required**
   - Condition: Sensitive operation requires elevated permissions
   - Action: Create handoff with permission request, route to AMCOS

5. **Failure recovery needed**
   - Condition: Agent failure detected, escalation required
   - Action: Create handoff with failure details, route to AMCOS

6. **Approval requests from AMCOS**
   - Condition: AMCOS requests user approval for agent operations
   - Action: Present approval request to user, forward decision to AMCOS

### Handle Directly (no routing):

1. **Status requests**
   - User says: "What's the status?", "How's progress?"
   - Action: Query relevant agents, compile report, present to user

2. **Approval decisions**
   - User says: "Yes, approve", "No, reject", "Proceed with..."
   - Action: Record decision, forward to requesting agent

3. **Clarification requests**
   - User says: "Explain...", "What does X mean?"
   - Action: Answer directly or query relevant agent

4. **Configuration/settings**
   - User says: "Set...", "Configure...", "Enable..."
   - Action: Handle directly

## Communication Hierarchy

```
USER <-> AMAMA (Assistant Manager) <-> AMCOS (Chief of Staff) <-> EAA (Architect skill agent)
                                                            <-> EOA (Orchestrator skill agent)
                                                            <-> EIA (Integrator skill agent)
```

**Governance roles in this hierarchy:**
- AMAMA: `manager`
- AMCOS: `chief-of-staff`
- EAA, EOA, EIA: `member` (with specialization expressed via skills/tags)

**CRITICAL**:
- AMAMA is the ONLY agent that communicates directly with the USER
- AMCOS manages agent lifecycle and sits between AMAMA and specialist agents
- EAA, EOA, and EIA do NOT communicate directly with each other or with AMAMA
- All specialist agent operations flow through AMCOS
- All specialist agents use governance `role: 'member'` — their specialization is metadata, not a governance concept

## Handoff Protocol

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

If any validation check fails:

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
- handoff-a1b2c3d4-amama-to-eaa.md    # AM assigns to Architect agent
- handoff-e5f6g7h8-amaa-to-amama.md    # Architect agent reports to AM
- handoff-i9j0k1l2-amama-to-eoa.md    # AM assigns to Orchestrator agent
- handoff-m3n4o5p6-amoa-to-amama.md    # Orchestrator agent reports to AM
- handoff-q7r8s9t0-amama-to-eia.md    # AM assigns to Integrator agent
```

## Storage Location

All handoff files are stored in: `docs_dev/handoffs/`

## GitHub Operations Routing

> For GitHub operations routing, see the **amama-github-routing** skill.

## Design Document Routing

### Handle Locally (AMAMA):

| Operation | Tool | Details |
|-----------|------|---------|
| Search designs by UUID | `amama_design_search.py --uuid` | Returns matching design docs |
| Search designs by keyword | `amama_design_search.py --keyword` | Full-text search in design/* |
| Search designs by status | `amama_design_search.py --status` | Filter by draft/approved/deprecated |
| List all designs | `amama_design_search.py --list` | Catalog of all design documents |

### Route to EAA (Architect agent) for:

| Operation | User Intent Pattern | Handoff Content |
|-----------|---------------------|-----------------|
| Create new design | "design", "create spec", "architect solution" | Requirements, constraints |
| Update design | "modify design", "update spec", "revise architecture" | Design UUID, changes |
| Review design | "review design", "validate architecture" | Design UUID, review criteria |

### Search Before Route Decision Tree

```
User mentions design/spec/architecture
          │
          ▼
    ┌─────────────────┐
    │ Does user give  │
    │ UUID or path?   │
    └────────┬────────┘
             │
     ┌───────┴───────┐
     │ YES           │ NO
     ▼               ▼
┌────────────┐  ┌─────────────────┐
│ Search by  │  │ Search by       │
│ UUID/path  │  │ keyword/context │
└─────┬──────┘  └────────┬────────┘
      │                  │
      ▼                  ▼
┌───────────────────────────────────┐
│   Design found?                   │
└────────────────┬──────────────────┘
         ┌───────┴───────┐
         │ YES           │ NO
         ▼               ▼
┌────────────────┐  ┌─────────────────┐
│ Include design │  │ Route to EAA to │
│ context in     │  │ create new      │
│ routing        │  │ design          │
└────────────────┘  └─────────────────┘
```

## Module Orchestration Routing

### Route to EOA (Orchestrator agent) for:

| Operation | User Intent Pattern | Handoff Content |
|-----------|---------------------|-----------------|
| Start module implementation | "implement module", "build component" | Module UUID from design |
| Coordinate parallel work | "parallelize", "split tasks" | Task breakdown, dependencies |
| Resume orchestration | "continue building", "resume work" | Orchestration state, progress |
| Replan modules | "reorganize tasks", "reprioritize" | Current state, new priorities |

### Orchestration Handoff Checklist

When routing to EOA, handoff MUST include:

1. **Design Reference**: UUID of approved design
2. **Module List**: Modules to implement (from design)
3. **Priority Order**: Which modules first
4. **Dependencies**: Inter-module dependencies
5. **Constraints**: Time, resources, technical limits
6. **Success Criteria**: What defines "done"

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

## Examples

### Example 1: Routing a Design Request to EAA

```
# User says: "Design a user authentication system"

# AMAMA identifies intent: "design" -> Route to EAA (architect specialization, role: member)

# Creates handoff
## Handoff: handoff-a1b2c3d4-amama-to-eaa.md

**From**: AMAMA (Assistant Manager)
**To**: EAA (Architect agent, role: member)
**Type**: task_assignment

### Request
Design a user authentication system

### Requirements
- Support OAuth2 and password-based auth
- Include role-based access control
- Must integrate with existing user database

### Expected Deliverable
- Design document in design/auth-system/DESIGN.md
- Module breakdown with dependencies
```

### Example 2: Handling Status Request Directly

```
# User says: "What's the status of the project?"

# AMAMA identifies intent: "status" -> Handle directly

# AMAMA queries all agents, compiles report, presents to user
# No handoff created - direct response
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Ambiguous intent | Multiple possible routes | Ask user for clarification |
| Target agent unavailable | Session not running | Queue handoff, notify user, retry |
| Handoff directory missing | Not initialized | Create `docs_dev/handoffs/` automatically |
| UUID collision | Extremely rare | Generate new UUID and retry |

## Resources

- Handoff Template in the shared folder
- Message Templates in the shared folder
- GitHub Routing SKILL (amama-github-routing)
- Proactive Handoff Protocol in amama-session-memory skill references
