# AI Maestro Assistant Manager Agent (AMAMA)

## Purpose
Claude Code plugin for the AI Maestro ecosystem. AMAMA is the user's right hand — sole interlocutor between user and AI agent teams. Governance role: `manager`. Creates teams, assigns COS (Chief-of-Staff) roles, approves/rejects operations, routes work to specialist agents.

## Tech Stack
- **Language**: Markdown (agent/skill/command definitions), Python (scripts, hooks, validation)
- **Platform**: Claude Code plugin (`.claude-plugin/plugin.json` manifest)
- **Dependencies**: AI Maestro >= 0.26.0, Python 3.8+, Claude Code 2.1.69+
- **External skills**: `team-governance`, `agent-messaging`, `ai-maestro-agents-management`

## Structure
- `agents/` — Agent definitions (.md with YAML frontmatter)
- `skills/` — 8 skill directories, each with SKILL.md + references/
- `commands/` — 4 slash commands (.md)
- `hooks/` — hooks.json defining 3 hooks
- `scripts/` — Python scripts (amama_*, validate_*, cpv_*)
- `shared/` — Templates and thresholds
- `docs/` — Published documentation
- `.claude-plugin/plugin.json` — Plugin manifest (current v2.6.0)
- `.github/workflows/` — CI/CD

## Key Abbreviations
- AMAMA = AI Maestro Assistant Manager Agent (manager)
- AMCOS = AI Maestro Chief-of-Staff (chief-of-staff)
- AMAA = AI Maestro Architect Agent (member)
- AMOA = AI Maestro Orchestrator Agent (member)
- AMIA = AI Maestro Integrator Agent (member)
