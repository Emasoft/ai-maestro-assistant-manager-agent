# AI Maestro Assistant Manager Agent (amama-)

**Version**: 1.1.6

## Overview

The AI Maestro Assistant Manager Agent (AMAMA) is the **user's right hand** - the sole interlocutor with the user. It receives user requests, clarifies requirements, routes work to appropriate specialist agents, and presents results back to the user.

Requires **AI Maestro >= 0.26.0** for inter-agent messaging, governance APIs, and team management.

## Communication Hierarchy

```
USER <-> AMAMA (manager) <-> AMCOS (chief-of-staff) <-> Specialist Agents (member)
                                                    <-> EAA  (architect skills)
                                                    <-> EOA  (orchestrator skills)
                                                    <-> EIA  (integrator skills)
```

**Governance Roles** (AI Maestro defines exactly 3):

| Role | Agent | Purpose |
|------|-------|---------|
| `manager` | AMAMA | Team manager, sole user contact, full admin authority |
| `chief-of-staff` | AMCOS | Agent lifecycle, permissions, failure recovery |
| `member` | EAA, EOA, EIA | All specialist agents (specialization via skills/tags) |

## Core Responsibilities

1. **User Communication**: Only agent that communicates directly with user
2. **Request Routing**: Directs requests to appropriate specialist agent via AMCOS
3. **Approval Workflows**: Manages GovernanceRequest API (push, merge, publish, security)
4. **Status Reporting**: Queries AI Maestro APIs, presents reports to user
5. **Team Management**: Creates teams via `POST /api/teams`, assigns COS role
6. **Governance Password**: Manages bcrypt-hashed password in `~/.aimaestro/governance.json`

## Components

### Agents

| Agent | Description |
|-------|-------------|
| `amama-assistant-manager-main-agent.md` | Main assistant manager agent |
| `amama-report-generator.md` | Generates status reports for user |

### Commands

| Command | Description |
|---------|-------------|
| `amama-planning-status` | Show planning phase status |
| `amama-orchestration-status` | Show orchestration phase status |
| `amama-approve-plan` | Approve plan for orchestration |
| `amama-respond-to-amcos` | Respond to pending AMCOS approval requests |

### Skills

| Skill | Description | When to Use |
|-------|-------------|-------------|
| `amama-user-communication` | User interaction patterns | When communicating with the user |
| `amama-status-reporting` | Status report generation (AI Maestro APIs) | When user requests status updates |
| `amama-approval-workflows` | GovernanceRequest approval workflows | When sensitive operations require user approval |
| `amama-role-routing` | Route requests to correct specialist agent | When delegating work to specialist agents |
| `amama-amcos-coordination` | Coordinate with AMCOS for approvals and agent lifecycle | When AMCOS requests approval or reports agent status |
| `amama-github-routing` | Route GitHub operations with team boundary awareness | When handling GitHub issues, PRs, projects, or releases |
| `amama-label-taxonomy` | GitHub label taxonomy and management | When creating or organizing GitHub labels |
| `amama-session-memory` | CozoDB-backed session memory and handoff tracking | When persisting session state or tracking handoffs |

### Hooks

| Hook | Event | Description |
|------|-------|-------------|
| `amama-memory-load` | SessionStart | Load session memory at startup |
| `amama-memory-save` | SessionEnd | Save session memory on exit |

## Communication Methods

1. **Handoff .md files** with UUIDs - for detailed specifications
2. **AI Maestro AMP messages** - for short exchanges (status updates, questions)
3. **GitHub Issues** - as permanent record and discovery mechanism

## Installation

This plugin ships with AI Maestro. It is installed automatically when AI Maestro provisions an Assistant Manager agent.

```bash
# Start a session with the main agent
claude --agent amama-assistant-manager-main-agent
```

### Development Only (--plugin-dir)

`--plugin-dir` loads a plugin directly from a local directory without installation. Use only during plugin development.

```bash
claude --plugin-dir /path/to/ai-maestro-assistant-manager-agent
```

## Validation

```bash
cd /path/to/ai-maestro-assistant-manager-agent
uv run python scripts/amama_validate_plugin.py . --verbose
```
