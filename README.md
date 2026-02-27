# AI Maestro Assistant Manager Agent (AMAMA)

**Version**: 2.0.0 (bump from 1.1.6 -- the entire plugin was migrated to v2 architecture)

## Overview

The AI Maestro Assistant Manager Agent (AMAMA) is the **user's right hand** -- the sole interlocutor with the user. It receives user requests, clarifies requirements, routes work to appropriate specialist agents via the Chief-of-Staff (AMCOS), and presents results back to the user.

Requires **AI Maestro >= 0.26.0** for inter-agent messaging, governance APIs, and team management.

## Communication Hierarchy

```
USER <-> AMAMA (manager) <-> AMCOS (chief-of-staff) <-> Specialist Agents (member)
                                                    <-> AMAA  (architect skills)
                                                    <-> AMOA  (orchestrator skills)
                                                    <-> AMIA  (integrator skills)
```

**Key principle**: AMAMA **never** communicates directly with specialist agents. All specialist routing goes through AMCOS.

## Governance Model (v2)

AI Maestro defines exactly 3 governance roles:

| Role | Agent | Purpose |
|------|-------|---------|
| `manager` | AMAMA | Team manager, sole user contact, full admin authority |
| `chief-of-staff` | AMCOS | Agent lifecycle, permissions, failure recovery |
| `member` | AMAA, AMOA, AMIA | All specialist agents (specialization via skills/tags, NOT the role field) |

**COS Assignment Model**: AMAMA does NOT spawn new AMCOS instances. Instead, AMAMA assigns the `chief-of-staff` governance role to an already-running registered agent via `PATCH /api/teams/{id}/chief-of-staff`.

## Two-Track Approval System

| Track | Scope | Mechanism | Skill |
|-------|-------|-----------|-------|
| **Governance approvals** | Team membership, COS assignment, agent lifecycle, transfers | GovernanceRequest API | `amama-approval-workflows` |
| **Operational approvals** | Deployments, merges, test runs, routine AMCOS operations | Message-based flow (`approval_request` / `approval_decision`) | `amama-amcos-coordination` |

## Plugin Components

### Agents

| Agent | File | Description |
|-------|------|-------------|
| Assistant Manager | `agents/amama-assistant-manager-main-agent.md` | Main AMAMA agent -- user communication, routing, approvals, team management |
| Report Generator | `agents/amama-report-generator.md` | Generates formatted status reports for user |

### Commands

| Command | File | Description |
|---------|------|-------------|
| `/amama-planning-status` | `commands/amama-planning-status.md` | Show planning phase status |
| `/amama-orchestration-status` | `commands/amama-orchestration-status.md` | Show orchestration phase status |
| `/amama-approve-plan` | `commands/amama-approve-plan.md` | Approve plan for orchestration |
| `/amama-respond-to-amcos` | `commands/amama-respond-to-amcos.md` | Respond to AMCOS approval requests (approve/deny/defer) |

### Skills

| Skill | Description | Triggers |
|-------|-------------|----------|
| `amama-user-communication` | User interaction patterns, response templates, escalation | When communicating with or presenting info to the user |
| `amama-status-reporting` | Status report generation via AI Maestro APIs | When user requests status updates |
| `amama-approval-workflows` | GovernanceRequest API approval workflows | When governance operations (team, agent, COS) need authorization |
| `amama-role-routing` | Route requests to correct specialist agent via AMCOS | When delegating work based on user intent |
| `amama-amcos-coordination` | AMCOS coordination: approvals, health checks, delegation | When AMCOS requests approval, reports status, or needs work delegated |
| `amama-github-routing` | Route GitHub operations with team boundary awareness | When handling GitHub issues, PRs, projects, releases |
| `amama-label-taxonomy` | GitHub label taxonomy and management | When creating or organizing GitHub labels |
| `amama-session-memory` | CozoDB-backed session memory and handoff tracking | When persisting session state or tracking handoffs |

### Hooks

| Hook ID | Event | Script | Description |
|---------|-------|--------|-------------|
| `amama-memory-load` | `SessionStart` | `scripts/amama_session_start.py` | Load session memory at startup |
| `amama-memory-save` | `SessionEnd` | `scripts/amama_session_end.py` | Save session memory on exit |
| `amama-stop-check` | `Stop` | `scripts/amama_stop_check.py` | Block exit until coordination work is complete |

### Shared Resources

| File | Description |
|------|-------------|
| `shared/handoff_template.md` | Standard handoff document format with YAML front-matter |
| `shared/message_templates.md` | Generic message templates for inter-agent communication |
| `shared/thresholds.py` | Governance thresholds, valid roles, valid specializations |

## Message Protocol

### Standard Message Types

| Type | Direction | Purpose |
|------|-----------|---------|
| `work_request` | AMAMA -> AMCOS | Route user work to specialist via AMCOS |
| `approval_request` | AMCOS -> AMAMA | Request approval for an operation |
| `approval_decision` | AMAMA -> AMCOS | Respond with `approve`, `deny`, or `defer` |
| `status_query` | AMAMA -> AMCOS | Request status update |
| `status_report` | AMCOS -> AMAMA | Status response |
| `ping` / `pong` | bidirectional | Health check (30s timeout) |
| `cos-role-assignment` | AMAMA -> agent | Assign COS role to agent |
| `cos-role-accepted` | agent -> AMAMA | Agent accepts COS role |
| `autonomy_grant` / `autonomy_revoke` | AMAMA -> AMCOS | Grant/revoke autonomous operation |
| `operation_complete` | AMCOS -> AMAMA | Notify task completion |
| `user_decision` | AMAMA -> AMCOS | Forward user decision |

### Request ID Format

All AMCOS requests use the format: `amcos-req-<uuid>` (e.g., `amcos-req-a1b2c3d4`).

## Communication Methods

1. **Handoff .md files** with UUIDs -- for detailed specifications and deliverables
2. **AI Maestro AMP messages** -- for short exchanges (status, approvals, health checks)
3. **GitHub Issues** -- as permanent record and discovery mechanism

## Plugin Abbreviations

| Abbreviation | Full Name | Governance Role |
|-------------|-----------|-----------------|
| AMAMA | AI Maestro Assistant Manager Agent | `manager` |
| AMCOS | AI Maestro Chief-of-Staff | `chief-of-staff` |
| AMAA | AI Maestro Architect Agent | `member` (architect specialization) |
| AMOA | AI Maestro Orchestrator Agent | `member` (orchestrator specialization) |
| AMIA | AI Maestro Integrator Agent | `member` (integrator specialization) |

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
uv run python scripts/validate_plugin.py . --verbose
```

## Scripts

All scripts are in the `scripts/` directory and use the `amama_` prefix:

| Script | Purpose |
|--------|---------|
| `amama_session_start.py` | SessionStart hook -- load memory |
| `amama_session_end.py` | SessionEnd hook -- save memory |
| `amama_stop_check.py` | Stop hook -- verify coordination complete |
| `amama_memory_manager.py` | CozoDB memory management |
| `amama_memory_operations.py` | Memory CRUD operations |
| `amama_notify_agent.py` | Send notifications to agents |
| `amama_approve_plan.py` | Plan approval logic |
| `amama_planning_status.py` | Planning status logic |
| `amama_orchestration_status.py` | Orchestration status logic |
| `amama_design_search.py` | Search design documents |
| `amama_download.py` | Download resources |
| `amama_init_design_folders.py` | Initialize design folder structure |
| `smart_exec.py` | Smart command execution |
| `bump_version.py` | Version bumping |
| `pre-push-hook.py` | Pre-push validation |
| `validate_plugin.py` | Main plugin validation entry point |
| `validate_agent.py` | Agent definition validation |
| `validate_command.py` | Command definition validation |
| `validate_documentation.py` | Documentation validation |
| `validate_encoding.py` | File encoding validation |
| `validate_enterprise.py` | Enterprise feature validation |
| `validate_hook.py` | Hook definition validation |
| `validate_lsp.py` | LSP integration validation |
| `validate_marketplace_pipeline.py` | Marketplace pipeline validation |
| `validate_marketplace.py` | Marketplace metadata validation |
| `validate_mcp.py` | MCP integration validation |
| `validate_scoring.py` | Plugin scoring validation |
| `validate_security.py` | Security validation |
| `validate_skill_comprehensive.py` | Comprehensive skill validation |
| `validate_skill.py` | Basic skill validation |
| `validate_xref.py` | Cross-reference validation |
| `validation_common.py` | Shared validation utilities |

## Project Structure

```
ai-maestro-assistant-manager-agent/
├── .claude-plugin/
│   └── plugin.json                    # Plugin manifest
├── agents/
│   ├── amama-assistant-manager-main-agent.md  # Main agent definition
│   └── amama-report-generator.md              # Report generator agent
├── commands/
│   ├── amama-approve-plan.md          # Approve plan command
│   ├── amama-orchestration-status.md  # Orchestration status command
│   ├── amama-planning-status.md       # Planning status command
│   └── amama-respond-to-amcos.md      # Respond to AMCOS command
├── hooks/
│   └── hooks.json                     # Hook definitions
├── scripts/
│   ├── amama_*.py                     # AMAMA functional scripts
│   ├── validate_*.py                  # Plugin validation suite
│   ├── validation_common.py           # Shared validation utilities
│   ├── smart_exec.py                  # Smart command execution
│   ├── bump_version.py                # Version bumping
│   └── pre-push-hook.py              # Pre-push validation
├── shared/
│   ├── handoff_template.md            # Handoff document format
│   ├── message_templates.md           # Generic message templates
│   └── thresholds.py                  # Governance thresholds
├── skills/
│   ├── amama-amcos-coordination/      # AMCOS coordination skill + 12 reference docs
│   ├── amama-approval-workflows/      # Governance approval workflows + 2 references
│   ├── amama-github-routing/          # GitHub operations routing + 1 reference
│   ├── amama-label-taxonomy/          # GitHub label management
│   ├── amama-role-routing/            # Request routing to specialists
│   ├── amama-session-memory/          # CozoDB session memory + 1 reference
│   ├── amama-status-reporting/        # Status report generation
│   └── amama-user-communication/      # User interaction patterns + 2 references
├── docs/                              # Published documentation
├── git-hooks/                         # Git hook scripts
├── LICENSE                            # MIT License
└── README.md
```

## License

MIT
