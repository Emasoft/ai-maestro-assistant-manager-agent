# Creating AMCOS Instance (AMAMA Exclusive Responsibility)

## Use-Case TOC

- When to create a new AMCOS instance -> Section 1.3
- How to spawn AMCOS with proper constraints -> Section 1.2
- Why only AMAMA can create AMCOS -> Section 1.1
- What to do after creating AMCOS -> Section 1.4

## Table of Contents

1. Why AMAMA Creates AMCOS
2. How to Create AMCOS
3. When to Create AMCOS
4. Post-Creation Steps

---

## 1. Why AMAMA Creates AMCOS

AMAMA is the ONLY agent authorized to create AMCOS. This ensures:

1. **Single point of authority** - Only the user's representative can instantiate the operational coordinator
2. **Role constraint enforcement** - AMCOS is created with proper constraints via `--agent` flag
3. **Audit trail** - All AMCOS instances are traceable to AMAMA approval

---

## 2. How to Create AMCOS

When a new AMCOS instance is needed (first time setup or after termination), AMAMA spawns it using the `ai-maestro-agents-management` skill:

- **Agent name**: `amcos-chief-of-staff-one` (chosen by AMAMA to avoid collisions)
- **Working directory**: `~/agents/amcos-chief-of-staff-one/`
- **Task**: "Coordinate agents across all projects. You are the Chief of Staff."
- **Plugin**: load `ai-maestro-chief-of-staff` using the skill's plugin management features
- **Main agent**: `amcos-chief-of-staff-main-agent` (REQUIRED - see below)

**Verify**: confirm the agent appears in the agent list with correct status.

**Session Name = AI Maestro Registry Name**

The session name becomes the agent's identity in AI Maestro:
- AMAMA (Manager) chooses the session name for AMCOS (e.g., `amcos-chief-of-staff-one`)
- AMCOS then chooses session names for subordinate agents (e.g., `amoa-svgbbox-orchestrator`)
- Session names must be unique across all running agents

**Naming Convention:**
- Format: `<role-prefix>-<descriptive-name>[-number]`
- Examples: `amcos-chief-of-staff-one`, `amoa-project-alpha-orchestrator`, `amia-main-integrator`

**Notes:**
- Working directory uses FLAT agent folder structure: `~/agents/<session-name>/`
- Plugin path points to LOCAL agent folder, NOT the development OUTPUT_SKILLS folder
- For NEW spawn, do not use the continue/wake option (only used when WAKING a hibernated agent)
- The plugin must be copied to the local agent folder before spawning

### Critical: The Main Agent Entry Point

Specifying the main agent entry point `amcos-chief-of-staff-main-agent` is **REQUIRED**. It:

1. **Injects the AMCOS main agent prompt** into the Claude Code system prompt
2. **Enforces role constraints** - AMCOS cannot violate its boundaries
3. **Links to documentation** - AMCOS automatically reads ROLE_BOUNDARIES.md

**Without this entry point, AMCOS would be an unconstrained Claude Code instance!**

---

## 3. When to Create AMCOS

| Scenario | Action |
|----------|--------|
| **First time** | Create when user starts using the AI Maestro agent ecosystem |
| **After termination** | Create if previous AMCOS was terminated due to failure |
| **Never duplicate** | Only ONE AMCOS should exist at any time |

---

## 4. Post-Creation Steps

After creating AMCOS:

1. Verify AMCOS is running using the `ai-maestro-agents-management` skill to list active agents
2. Send an initialization message using the `agent-messaging` skill
3. Confirm AMCOS acknowledges its role constraints
4. Register AMCOS in the organization agent registry

### Verification

Use the `ai-maestro-agents-management` skill to list agents and confirm AMCOS appears with active status.

### Initialization Message

Send an initialization check message to AMCOS using the `agent-messaging` skill:
- **Recipient**: The AMCOS session name (e.g., `amcos-chief-of-staff-one`)
- **Subject**: "AMAMA Initialization Check"
- **Content**: initialization-check type, with expected_role "chief-of-staff"
- **Type**: `initialization-check`
- **Priority**: `high`

**Verify**: AMCOS should respond confirming its role constraints are loaded.
