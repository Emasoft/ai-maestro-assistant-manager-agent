# Creating ECOS Procedure


## Contents

- [Overview](#overview)
- [Key Principles](#key-principles)
- [Session Naming Convention](#session-naming-convention)
- [Agent Creation Template](#agent-creation-template)
- [Required Parameters Explained](#required-parameters-explained)
- [Critical Notes](#critical-notes)
  - [Directory Structure](#directory-structure)
  - [Plugin Path](#plugin-path)
  - [Create vs Wake](#create-vs-wake)
  - [Pre-requisite](#pre-requisite)
- [Step-by-Step Procedure](#step-by-step-procedure)
  - [Step 1: Choose Session Name](#step-1-choose-session-name)
  - [Step 2: Prepare Agent Directory](#step-2-prepare-agent-directory)
  - [Step 3: Copy Plugin](#step-3-copy-plugin)
  - [Step 4: Execute Agent Creation](#step-4-execute-agent-creation)
  - [Step 5: Wait for Initialization](#step-5-wait-for-initialization)
  - [Step 6: Health Check Ping](#step-6-health-check-ping)
  - [Step 7: Verify Response](#step-7-verify-response)
  - [Step 9: Register ECOS](#step-9-register-ecos)
- [Session: ecos-chief-of-staff-one](#session-ecos-chief-of-staff-one)
  - [Step 10: Report to User](#step-10-report-to-user)
- [Success Criteria](#success-criteria)
- [Troubleshooting](#troubleshooting)
  - [Creation Fails with Exit Code 1](#creation-fails-with-exit-code-1)
  - [No Response to Health Ping](#no-response-to-health-ping)
  - [Plugin Not Found Error](#plugin-not-found-error)
- [Related Documents](#related-documents)

## Overview

EAMA (Assistant Manager) is the ONLY agent authorized to create ECOS (Chief of Staff) instances. This document describes the step-by-step procedure for spawning a new ECOS agent.

## Key Principles

1. **EAMA chooses the session name** - To avoid collisions and maintain naming consistency
2. **Session name = AI Maestro registry name** - The session name becomes the agent's identifier in AI Maestro
3. **Plugin must be pre-copied** - Plugin files must exist in the target directory BEFORE spawning
4. **Main agent injection** - The `--agent` flag ensures ECOS receives its role-specific system prompt

## Session Naming Convention

Use this format for ECOS session names:

```
<role-prefix>-<descriptive>[-number]
```

**Examples:**
- `ecos-chief-of-staff-one` - Primary ECOS instance
- `ecos-project-alpha` - ECOS for specific project "alpha"
- `ecos-inventory-system` - ECOS for inventory-system project

**Subordinate agents** spawned by ECOS follow their own naming:
- `eoa-svgbbox-orchestrator` (Orchestrator for svgbbox project)
- `eia-inventory-review` (Integrator for inventory review)

## Agent Creation Template

Use the `ai-maestro-agents-management` skill to create the ECOS agent with the following parameters:

- **Agent name**: `ecos-chief-of-staff-one` (EAMA picks a unique name; this becomes the AI Maestro registry name)
- **Working directory**: `~/agents/ecos-chief-of-staff-one/`
- **Task**: "Coordinate agents across all projects"
- **Plugin**: load `emasoft-chief-of-staff` using the skill's plugin management features
- **Main agent**: `ecos-chief-of-staff-main-agent`

**Verify**: confirm the agent appears in the agent list with correct status.

## Required Parameters Explained

| Parameter | Purpose | Example Value |
|-----------|---------|---------------|
| Agent name | AI Maestro registry identifier | `ecos-chief-of-staff-one` |
| Working directory | Working directory (flat structure) | `~/agents/ecos-chief-of-staff-one/` |
| Task | Task description (for context) | `"Coordinate agents across all projects"` |
| Plugin | Plugin to load for the agent | `emasoft-chief-of-staff` |
| Main agent | Main agent prompt file | `ecos-chief-of-staff-main-agent` |

## Critical Notes

### Directory Structure

- Use **FLAT agent folder structure**: `~/agents/<session-name>/`
- NOT nested: `~/agents/project/session-name/`

### Plugin Path

- Use **LOCAL agent folder path**: `~/agents/<session-name>/.claude/plugins/`
- NOT development path: `./OUTPUT_SKILLS/emasoft-chief-of-staff/`

### Create vs Wake

- **NEW creation**: Standard creation (no continue/wake option)
- **Wake hibernated agent**: Use the wake feature of the `ai-maestro-agents-management` skill

### Pre-requisite

**Plugin files MUST be copied to target directory BEFORE creating the agent.**

Prepare the agent's plugin directory:
```bash
# Copy plugin to agent's local directory
mkdir -p ~/agents/$SESSION_NAME/.claude/plugins/
cp -r /path/to/emasoft-chief-of-staff ~/agents/$SESSION_NAME/.claude/plugins/
```

## Step-by-Step Procedure

### Step 1: Choose Session Name

Pick a unique session name following the naming convention:

```bash
SESSION_NAME="ecos-chief-of-staff-one"
```

### Step 2: Prepare Agent Directory

Create the agent's working directory:

```bash
mkdir -p ~/agents/$SESSION_NAME
```

### Step 3: Copy Plugin

Copy the ECOS plugin to the agent's local plugins directory:

```bash
mkdir -p ~/agents/$SESSION_NAME/.claude/plugins/
cp -r /path/to/emasoft-chief-of-staff ~/agents/$SESSION_NAME/.claude/plugins/
```

### Step 4: Execute Agent Creation

Use the `ai-maestro-agents-management` skill to create the agent with the parameters prepared in Steps 1-3.

**Verify**: the creation command succeeds (exit code 0).

### Step 5: Wait for Initialization

Wait 5 seconds for ECOS to initialize.

### Step 6: Health Check Ping

Send a health check message using the `agent-messaging` skill:
- **Recipient**: The ECOS session name chosen in Step 1
- **Subject**: "Health Check"
- **Content**: ping type, message "Verify ECOS alive", expect_reply true, timeout 10
- **Type**: `ping`
- **Priority**: `normal`

### Step 7: Verify Response

Check your inbox using the `agent-messaging` skill for a `pong` response from ECOS within 30 seconds.

Expected response content:
```json
{
  "type": "pong",
  "status": "alive",
  "uptime": "5",
  "active_specialists": []
}
```

### Step 9: Register ECOS

Record the new ECOS instance in the active sessions log:

File: `docs_dev/sessions/active-ecos-sessions.md`

```markdown
## Session: ecos-chief-of-staff-one
- **Spawned**: 2026-02-05 16:30:22
- **Plugins**: emasoft-chief-of-staff
- **Working Dir**: ~/agents/ecos-chief-of-staff-one
- **Last Health Check**: 2026-02-05 16:30:30 (ALIVE)
- **Active Specialists**: (none yet)
- **Current Tasks**: Awaiting work requests
```

### Step 10: Report to User

Notify the user that ECOS is ready:

```
✅ ECOS ready!

Session: ecos-chief-of-staff-one
Status: Active and responding
Working Dir: ~/agents/ecos-chief-of-staff-one

ECOS is now available to coordinate specialist agents (EOA, EAA, EIA).
```

## Success Criteria

A successful ECOS spawn meets ALL of the following criteria:

- [ ] Agent creation via `ai-maestro-agents-management` skill succeeded (exit code 0)
- [ ] ECOS session registered in AI Maestro (visible in agent list)
- [ ] ECOS main agent loaded with correct role constraints
- [ ] ECOS plugins loaded correctly
- [ ] ECOS working directory set correctly
- [ ] ECOS health check ping successful (pong received)
- [ ] ECOS added to active sessions log in `docs_dev/sessions/active-ecos-sessions.md`

## Troubleshooting

### Creation Fails with Exit Code 1

**Cause**: AI Maestro service may be down or session name collision

**Solution**:
1. Check AI Maestro health using the `agent-messaging` skill's health check feature
2. Use the `ai-maestro-agents-management` skill to list agents and check for name collisions
3. If collision, use different session name with suffix: `ecos-chief-of-staff-two`

### No Response to Health Ping

**Cause**: ECOS may not have finished initializing

**Solution**:
1. Wait additional 10 seconds
2. Retry health ping
3. Check tmux session manually: `tmux attach -t $SESSION_NAME`

### Plugin Not Found Error

**Cause**: Plugin not copied to local directory before spawn

**Solution**:
1. Verify plugin exists: `ls ~/agents/$SESSION_NAME/.claude/plugins/emasoft-chief-of-staff/`
2. Copy plugin if missing
3. Re-run spawn command

## Related Documents

- [ECOS Communication Protocol](./ecos-communication-protocol.md)
- [ECOS Approval Workflow](./ecos-approval-workflow.md)
- [Active ECOS Sessions Management](./managing-active-sessions.md)
