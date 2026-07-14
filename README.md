# AI Maestro Assistant Manager Agent (AMAMA)

**Version**: 2.12.12

Part of the [AI Maestro](https://github.com/Emasoft/ai-maestro) ecosystem. See also: [AI Maestro Plugins Marketplace](https://github.com/Emasoft/ai-maestro-plugins).

## Overview

The AI Maestro Assistant Manager Agent (AMAMA) is the **user's right hand** -- the sole interlocutor with the user. It receives user requests, clarifies requirements, routes work to appropriate specialist agents via the Chief-of-Staff (AMCOS), and presents results back to the user.

Requires **[AI Maestro](https://github.com/Emasoft/ai-maestro) >= 0.26.0** for inter-agent messaging, governance APIs, and team management.

## Communication Hierarchy

```
USER <-> AMAMA (manager) <-> AMCOS (chief-of-staff) <-> Specialist Agents (member)
                                                    <-> AMAA  (architect skills)
                                                    <-> AMOA  (orchestrator skills)
                                                    <-> AMIA  (integrator skills)
```

**Key principle**: AMAMA **never** communicates directly with specialist agents. All specialist routing goes through AMCOS.

## Governance Model (v2)

AI Maestro defines exactly 3 governance titles:

| Role | Agent | Purpose |
|------|-------|---------|
| `manager` | AMAMA | Team manager, sole user contact, full admin authority |
| `chief-of-staff` | AMCOS | Agent lifecycle, permissions, failure recovery |
| `member` | AMAA, AMOA, AMIA | All specialist agents (specialization via skills/tags, NOT the role field) |

**COS Assignment Model (R29)**: AMAMA (MANAGER) creates AND deletes teams on its own with NO user approval, and the team's COS is created as part of team creation -- when AMAMA runs `aimaestro-teams.sh create`, the AI Maestro server **auto-creates** the `chief-of-staff` for that team. AMAMA then wakes the COS and grants its mandate (R30). The whole COS lifecycle is AID-authorized (R28); AMAMA never uses a sudo/governance password and there is no dashboard step (R32).

## Two-Track Approval System

| Track | Scope | Mechanism | Skill |
|-------|-------|-----------|-------|
| **Governance approvals** | Team membership, COS assignment, agent lifecycle, transfers | GovernanceRequest API | `amama-approval-workflows` |
| **Operational approvals** | Deployments, merges, test runs, routine AMCOS operations | Message-based flow (`approval_request` / `approval_decision`) | `amama-amcos-coordination` |

## TRDD lifecycle — at a glance

The project's `design/` folder on GitHub is the **sole source of truth** for
all TRDDs (proposals, open work, and terminal records). Every clone pulls
before acting and pushes after each change.

```text
        ┌───────────────────────────────────────────────────────────────┐
        │  design/  ⇅  GitHub repo  =  SOLE SOURCE OF TRUTH              │
        │  every clone PULLS before acting and PUSHES after each change   │
        └───────────────────────────────────────────────────────────────┘

  idea / request
       │
       │  Tier 0 (own scope · NPT/EHT) ── author directly as `planned` ──┐
       │                                                                 │
       ▼   needs approval                                                ▼
 ┌───────────────────┐   approve                                ┌────────────────────────┐
 │ design/proposals/ │   (T1 COS · T2 MANAGER · T3 USER)         │  design/tasks/         │
 │  column: proposal │ ───────────────────────────────────────▶ │  = OPEN WORK           │
 │   (PENDING)       │                                          │                        │
 └───────────────────┘                                          │  planned→todo→dispatch │
       │                                                        │  →dev→testing→ai_review│
       │ refuse  (NEVER approved)                               │  →human_review         │
       ▼                                                        │  →complete→publish|deploy
 ┌───────────────────┐                                          │                        │
 │ design/refused/   │                                          │  • blocked  (lists its │
 │  column: refused  │                                          │    blocked-by:)        │
 └───────────────────┘                                          │  • failed → RETRY      │
                                                                │    (stays OPEN, never  │
                                                                │     archived)          │
                                                                └───────────┬────────────┘
                                                                            │ terminal-DONE
                                                                            │ (was approved)
                                                                            ▼
                                                          ┌──────────────────────────────┐
                                                          │  design/archived/            │
                                                          │  completed · cancelled ·     │
                                                          │  superseded                  │
                                                          └──────────────────────────────┘

  OPEN TRDD  = any file in design/tasks/  (INCLUDING `blocked` and `failed`).
  refused/   = proposals NEVER approved.   archived/ = ONCE-approved, now terminal.
  `failed` is OPEN and retryable — fix the cause (often via other TRDDs), retry;
  it is NEVER moved to archived. Giving up on a failed TRDD = cancel → archived.
```

Full rules: the base `~/.claude/rules/trdd-design-tasks.md` plus the seeded DEP
overlay `.claude/rules/aimaestro-trdd-approval.md`. Decide proposals fast with
the core `ama-proposal-approvals` skill (`approved: 4,6` / `refused: 7,8`).

## Plugin Components

### Agents

| Agent | File | Description |
|-------|------|-------------|
| Assistant Manager | `agents/ai-maestro-assistant-manager-agent-main-agent.md` | Main AMAMA agent -- user communication, routing, approvals, team management |
| Report Generator | `agents/amama-report-generator.md` | Generates formatted status reports for user |

### Commands

| Command | File | Description |
|---------|------|-------------|
| `/amama-planning-status` | `commands/amama-planning-status.md` | Show planning phase status |
| `/amama-orchestration-status` | `commands/amama-orchestration-status.md` | Show orchestration phase status |
| `/amama-approve-plan` | `commands/amama-approve-plan.md` | Approve plan for orchestration |
| `/amama-respond-to-amcos` | `commands/amama-respond-to-amcos.md` | Respond to AMCOS approval requests (approve/deny/defer) |

### Skills

| Skill | Refs | Description |
|-------|------|-------------|
| `amama-user-communication` | 6 | Communicating with users: clarification, options, approval, reporting |
| `amama-status-reporting` | 4 | Generating status reports via AI Maestro APIs (sessions, health, teams, tasks) |
| `amama-approval-workflows` | 11 | Governance approvals via GovernanceRequest API (team, agent lifecycle, COS) |
| `amama-role-routing` | 4 | Routing user requests to specialist agents based on intent |
| `amama-amcos-coordination` | 16 | COS coordination: approvals, delegation, health checks, completions |
| `amama-github-routing` | 7 | Routing GitHub operations (issues, PRs, projects, releases) via team labels |
| `amama-label-taxonomy` | 2 | GitHub label taxonomy management and triage |
| `amama-session-memory` | 5 | CozoDB-backed session memory, preferences, handoff tracking |
| `amama-autonomous-fallback` | 2 | Approve-autonomously / defer / escalate when a peer approval arrives and the user is unavailable |
| `amama-presence-tracker` | 1 | Compute the user's availability state (active/monitoring/away/dnd) for autonomous-fallback gating |

### Hooks

| Hook ID | Event | Script | Description |
|---------|-------|--------|-------------|
| `amama-memory-load` | `SessionStart` | `scripts/amama_session_start.py` | SessionStart wiring (memory recall is now on-demand via the global `/janitor-memory-recall` skill) |
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
claude --agent ai-maestro-assistant-manager-agent-main-agent
```

### Development Only (--plugin-dir)

`--plugin-dir` loads a plugin directly from a local directory without installation. Use only during plugin development.

```bash
claude --plugin-dir /path/to/ai-maestro-assistant-manager-agent
```

## Validation

Validation runs against the canonical CPV pipeline fetched from GitHub —
no validator scripts are vendored into this repo:

```bash
cd /path/to/ai-maestro-assistant-manager-agent
uvx --from git+https://github.com/Emasoft/claude-plugins-validation \
    --with pyyaml cpv-remote-validate plugin . --strict --verbose
```

## Token Optimization

All AMAMA scripts write verbose output to timestamped report files in the gitignored `reports/<component>/` (never the git-tracked `design/` tree) and print only 2-3 line summaries to stdout. Sub-agents must follow the same pattern — see the main agent's "Sub-Agent Output Rules" section.

## Scripts

All runtime scripts are in the `scripts/` directory. The plugin's own
functional scripts use the `amama_` prefix; `publish.py` is the canonical
release pipeline. Validation and linting are NOT vendored — they run
remotely against CPV from GitHub (see [Validation](#validation) above).

| Script | Purpose |
|--------|---------|
| `amama_session_start.py` | SessionStart hook -- wiring (memory recall is on-demand via the global `/janitor-memory-recall` skill) |
| `amama_stop_check.py` | Stop hook -- verify coordination complete |
| `amama_user_prompt_submit.py` | UserPromptSubmit hook -- record user-input presence |
| `amama_report_writer.py` | Shared report writer for token-efficient output |
| `amama_notify_agent.py` | Send notifications to agents |
| `amama_approve_plan.py` | Plan approval logic |
| `amama_planning_status.py` | Planning status logic |
| `amama_orchestration_status.py` | Orchestration status logic |
| `amama_design_search.py` | Search design documents |
| `amama_download.py` | Download resources |
| `amama_init_design_folders.py` | Initialize design folder structure |
| `publish.py` | Canonical plugin release pipeline (bump, lint, validate, test, tag, push) |

## Project Structure

```
ai-maestro-assistant-manager-agent/
├── .claude-plugin/
│   └── plugin.json                    # Plugin manifest
├── agents/
│   ├── ai-maestro-assistant-manager-agent-main-agent.md  # Main agent definition
│   └── amama-report-generator.md              # Report generator agent
├── commands/
│   ├── amama-approve-plan.md          # Approve plan command
│   ├── amama-orchestration-status.md  # Orchestration status command
│   ├── amama-planning-status.md       # Planning status command
│   └── amama-respond-to-amcos.md      # Respond to AMCOS command
├── hooks/
│   └── hooks.json                     # Hook definitions
├── scripts/
│   ├── amama_*.py                     # AMAMA functional scripts (hooks + logic)
│   └── publish.py                     # Canonical release pipeline (remote CPV validate/lint)
├── shared/
│   ├── handoff_template.md            # Handoff document format
│   ├── message_templates.md           # Generic message templates
│   └── thresholds.py                  # Governance thresholds
├── skills/
│   ├── amama-amcos-coordination/      # AMCOS coordination skill + 16 reference docs
│   ├── amama-approval-workflows/      # Governance approval workflows + 11 reference docs
│   ├── amama-autonomous-fallback/     # Approve/defer/escalate when user unavailable + 2 reference docs
│   ├── amama-github-routing/          # GitHub operations routing + 7 reference docs
│   ├── amama-label-taxonomy/          # GitHub label management + 2 reference docs
│   ├── amama-presence-tracker/        # User availability state for autonomous-fallback + 1 reference doc
│   ├── amama-role-routing/            # Request routing to specialists + 4 reference docs
│   ├── amama-session-memory/          # CozoDB session memory + 5 reference docs
│   ├── amama-status-reporting/        # Status report generation + 4 reference docs
│   └── amama-user-communication/      # User interaction patterns + 6 reference docs
├── docs/                              # Published documentation
├── git-hooks/                         # Git hook scripts
├── LICENSE                            # MIT License
└── README.md
```

## Recommended External Tools

AMAMA agents should use these tools (when available) to conserve orchestrator context tokens:

| Tool | Plugin / CLI | Purpose |
|------|-------------|---------|
| LLM Externalizer | `llm-externalizer` plugin (MCP) | Offload analysis/scanning to cheaper external LLMs |
| Serena MCP | `serena-mcp` (MCP) | Symbol-aware code navigation and search |
| TLDR | `tldr` CLI | Token-efficient code structure analysis |

See the main agent's "Token-Efficient External Tools" section for usage details.

## Compatibility

| Dependency | Minimum Version |
|------------|----------------|
| Claude Code | 2.1.69+ |
| AI Maestro | 0.26.0+ |
| Python | 3.8+ |

## License

MIT
