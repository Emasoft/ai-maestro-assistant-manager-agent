# Emasoft Assistant Manager Agent (eama-)

**Version**: 1.0.0

## Overview

The Emasoft Assistant Manager Agent (EAMA) is the **user's right hand** - the sole interlocutor with the user. It receives user requests, clarifies requirements, routes work to appropriate roles (Architect, Orchestrator, Integrator), and presents results back to the user.

## Communication Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                          USER                                    │
│   (provides requirements, approves, reports issues)              │
└─────────────────────┬───────────────────────────────────────────┘
                      │ ONLY direct communication channel
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│      EMASOFT-ASSISTANT-MANAGER-AGENT (eama-)                     │
│   - Receives user requests, clarifies requirements               │
│   - Requests user approvals (push, merge, publish, security)     │
│   - Reports status to user                                       │
│   - Coordinates with ECOS for agent lifecycle                    │
│   - Routes handoffs between roles                                │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│      EMASOFT-CHIEF-OF-STAFF (ecos-)                              │
│   - Agent lifecycle management (create, terminate, restart)      │
│   - Session management and health monitoring                     │
│   - Permission management for sensitive operations               │
│   - Failure recovery and escalation                              │
└──────┬─────────────────────┬─────────────────────┬──────────────┘
       │                     │                     │
       ▼                     ▼                     ▼
   ARCHITECT           ORCHESTRATOR           INTEGRATOR
     (EAA)                (EOA)                  (EIA)
```

## Core Responsibilities

1. **User Communication**: Only role that communicates directly with user
2. **Request Routing**: Directs requests to appropriate specialist role
3. **Approval Workflows**: Manages approval requests for push, merge, publish, security
4. **Status Reporting**: Presents status reports from other roles
5. **Handoff Coordination**: Routes handoffs between architect, orchestrator, integrator

## Components

### Agents

| Agent | Description |
|-------|-------------|
| `eama-assistant-manager-main-agent.md` | Main assistant manager agent |
| `eama-report-generator.md` | Generates status reports for user |

### Commands

| Command | Description |
|---------|-------------|
| `eama-planning-status` | Show planning phase status |
| `eama-orchestration-status` | Show orchestration phase status |
| `eama-approve-plan` | Approve plan for orchestration |
| `eama-respond-to-ecos` | Respond to pending ECOS approval requests |

### Skills

| Skill | Description | When to Use |
|-------|-------------|-------------|
| `eama-user-communication` | User interaction patterns | When communicating with the user |
| `eama-status-reporting` | Status report generation | When user requests status updates |
| `eama-approval-workflows` | Approval request patterns | When sensitive operations require user approval |
| `eama-role-routing` | Route requests to correct role | When delegating work to EAA, EOA, or EIA |
| `eama-ecos-coordination` | Coordinate with ECOS for approvals and agent lifecycle | When ECOS requests approval or reports agent status |
| `eama-github-routing` | Route GitHub operations to appropriate specialists | When handling GitHub issues, PRs, projects, or releases |
| `eama-label-taxonomy` | GitHub label taxonomy and management | When creating or organizing GitHub labels |
| `eama-session-memory` | Session memory management and handoff tracking | When persisting session state or tracking handoffs |

### Hooks

| Hook | Event | Description |
|------|-------|-------------|
| `eama-memory-load` | SessionStart | Load session memory at startup |
| `eama-memory-save` | SessionEnd | Save session memory on exit |

## Communication Methods

1. **Handoff .md files** with UUIDs - for detailed specifications
2. **AI Maestro messages** - for short exchanges (status updates, questions)
3. **GitHub Issues** - as permanent record and discovery mechanism

## Installation (Production)

Install from the Emasoft marketplace. Use `--scope local` to install only for the current project directory, or `--scope global` for all projects.

```bash
# Add Emasoft marketplace (first time only)
claude plugin marketplace add emasoft-plugins --url https://github.com/Emasoft/emasoft-plugins

# Install plugin (--scope local = this project only, recommended)
claude plugin install emasoft-assistant-manager-agent@emasoft-plugins --scope local

# RESTART Claude Code after installing (required!)
```

Once installed, start a session with the main agent:

```bash
claude --agent eama-assistant-manager-main-agent
```

## Development Only (--plugin-dir)

`--plugin-dir` loads a plugin directly from a local directory without marketplace installation. Use only during plugin development.

```bash
claude --plugin-dir ./OUTPUT_SKILLS/emasoft-assistant-manager-agent
```

## Validation

```bash
cd OUTPUT_SKILLS/emasoft-assistant-manager-agent
uv run python scripts/validate_plugin.py . --verbose
```
