# Creating ECOS Instance (EAMA Exclusive Responsibility)

## Use-Case TOC

- When to create a new ECOS instance -> Section 1.3
- How to spawn ECOS with proper constraints -> Section 1.2
- Why only EAMA can create ECOS -> Section 1.1
- What to do after creating ECOS -> Section 1.4

## Table of Contents

1. Why EAMA Creates ECOS
2. How to Create ECOS
3. When to Create ECOS
4. Post-Creation Steps

---

## 1. Why EAMA Creates ECOS

EAMA is the ONLY agent authorized to create ECOS. This ensures:

1. **Single point of authority** - Only the user's representative can instantiate the operational coordinator
2. **Role constraint enforcement** - ECOS is created with proper constraints via `--agent` flag
3. **Audit trail** - All ECOS instances are traceable to EAMA approval

---

## 2. How to Create ECOS

When a new ECOS instance is needed (first time setup or after termination), EAMA spawns it using the `ai-maestro-agents-management` skill:

- **Agent name**: `ecos-chief-of-staff-one` (chosen by EAMA to avoid collisions)
- **Working directory**: `~/agents/ecos-chief-of-staff-one/`
- **Task**: "Coordinate agents across all projects. You are the Chief of Staff."
- **Plugin**: load `emasoft-chief-of-staff` using the skill's plugin management features
- **Main agent**: `ecos-chief-of-staff-main-agent` (REQUIRED - see below)

**Verify**: confirm the agent appears in the agent list with correct status.

**Session Name = AI Maestro Registry Name**

The session name becomes the agent's identity in AI Maestro:
- EAMA (Manager) chooses the session name for ECOS (e.g., `ecos-chief-of-staff-one`)
- ECOS then chooses session names for subordinate agents (e.g., `eoa-svgbbox-orchestrator`)
- Session names must be unique across all running agents

**Naming Convention:**
- Format: `<role-prefix>-<descriptive-name>[-number]`
- Examples: `ecos-chief-of-staff-one`, `eoa-project-alpha-orchestrator`, `eia-main-integrator`

**Notes:**
- Working directory uses FLAT agent folder structure: `~/agents/<session-name>/`
- Plugin path points to LOCAL agent folder, NOT the development OUTPUT_SKILLS folder
- For NEW spawn, do not use the continue/wake option (only used when WAKING a hibernated agent)
- The plugin must be copied to the local agent folder before spawning

### Critical: The Main Agent Entry Point

Specifying the main agent entry point `ecos-chief-of-staff-main-agent` is **REQUIRED**. It:

1. **Injects the ECOS main agent prompt** into the Claude Code system prompt
2. **Enforces role constraints** - ECOS cannot violate its boundaries
3. **Links to documentation** - ECOS automatically reads ROLE_BOUNDARIES.md

**Without this entry point, ECOS would be an unconstrained Claude Code instance!**

---

## 3. When to Create ECOS

| Scenario | Action |
|----------|--------|
| **First time** | Create when user starts using the Emasoft agent ecosystem |
| **After termination** | Create if previous ECOS was terminated due to failure |
| **Never duplicate** | Only ONE ECOS should exist at any time |

---

## 4. Post-Creation Steps

After creating ECOS:

1. Verify ECOS is running using the `ai-maestro-agents-management` skill to list active agents
2. Send an initialization message using the `agent-messaging` skill
3. Confirm ECOS acknowledges its role constraints
4. Register ECOS in the organization agent registry

### Verification

Use the `ai-maestro-agents-management` skill to list agents and confirm ECOS appears with active status.

### Initialization Message

Send an initialization check message to ECOS using the `agent-messaging` skill:
- **Recipient**: The ECOS session name (e.g., `ecos-chief-of-staff-one`)
- **Subject**: "EAMA Initialization Check"
- **Content**: initialization-check type, with expected_role "chief-of-staff"
- **Type**: `initialization-check`
- **Priority**: `high`

**Verify**: ECOS should respond confirming its role constraints are loaded.
