# Style and Conventions

## Naming
- Plugin prefixes: `am-` for AI Maestro plugins (AMAMA, AMCOS, AMOA, AMIA, AMAA). NEVER `e-` or `emasoft-` prefixes (those are separate Emasoft plugins).
- Skill directories: `amama-{function}` (e.g., `amama-user-communication`)
- Scripts: `amama_{function}.py` prefix
- Session names: `domain-subdomain-name` format (e.g., `amama-myproject-manager`)

## SKILL.md Rules
- Must stay under 4000 chars (MINOR) / 5000 chars (MAJOR)
- Required sections: Overview, Prerequisites, Instructions, Output, Error Handling, Examples, Resources
- Detailed content goes in `references/` subdirectory
- All `[text](references/foo.md)` links must have TOC embedded — titles appear within 50 lines after link
- NEVER convert markdown links to backtick/plain text

## Governance
- 3 roles only: `manager`, `chief-of-staff`, `member`
- Specializations via skills/metadata, NOT the role field
- 5-status kanban: `backlog | pending | in_progress | review | completed`
- COS assignment model: AMAMA assigns role to existing agent (never "spawns" AMCOS)

## Plugin Abstraction Principle (PAP)
- No embedded curl commands — reference external skills instead
- No hardcoded localhost URLs
- Use `$AIMAESTRO_API` environment variable for API base
