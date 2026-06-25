---
trdd-id: 3HSUEP3Y
title: Claude Code 2.1.170 to 2.1.191 plugin-ecosystem compatibility audit for AMAMA
column: complete
created: 2026-06-25T19:31:10+0200
updated: 2026-06-25T19:31:10+0200
current-owner: amama
assignee: amama
priority: 2
severity: LOW
effort: S
task-type: audit
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: none
delivery: direct-push
target-branch: main
test-requirements: []
audit-requirements: []
review-requirements: [human-review]
impacts: []
external-refs: ["https://code.claude.com/docs/en/changelog.md"]
audit-trigger: user-report
audit-target: ai-maestro-assistant-manager-agent (the AMAMA plugin surface)
audit-conclusion: benign
---

# TRDD-3HSUEP3Y — Claude Code 2.1.170→2.1.191 plugin-ecosystem compatibility audit

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-06-25T19:31

**✅ AUDIT COMPLETE — NO AMAMA CODE/MANIFEST CHANGE REQUIRED.** AMAMA (v2.12.11)
is verified compatible with every plugin-ecosystem change in the Claude Code
changelog window v2.1.170 → v2.1.191. Conclusion is FACT-VERIFIED (each candidate
read against the actual repo files, not inferred). The single observation worth a
USER decision — the two `model: opus` agent pins — is SAFE under the changelog
(alias, not a deprecated version-id) and is already captured by the pending
cache-optimization work item (CA-04). No churn introduced, per `/go-on-yourself`
"write only what is strictly necessary."

**NEXT ACTION (coordination, MANAGER lane):** post a fleet-wide heads-up
summarizing the window's plugin-ecosystem impact + a per-plugin audit checklist so
each peer plugin's Claude audits its own surface (serves "fleet ready"). Then
surface to USER: (a) AMAMA verified compat to CC 2.1.191; (b) the model-pin
decision point; (c) offer to drive the same audit fleet-wide.

**Load-bearing facts:**
- Trigger: USER instruction (2026-06-25) — "read all the updates in the changelog
  since v2.1.170 onward to v2.1.191 and update the plugin accordingly."
- Source of truth: `https://code.claude.com/docs/en/changelog.md` (fetched this
  session). Versions with NO entry in the window: 2.1.171, 2.1.177, 2.1.180,
  2.1.182, 2.1.184, 2.1.188, 2.1.189; 2.1.190 = "bug fixes" only.

## What was checked, and the verified verdict per candidate

Each candidate is a changelog entry that COULD touch a plugin. Verdict columns are
VERIFIED (file read), not inferred.

| # | Changelog change (version) | AMAMA exposure (verified) | Verdict |
|---|---|---|---|
| 1 | Hooks with comma-separated matchers silently never firing — FIXED (2.1.191) | `hooks/hooks.json` has only SessionStart / UserPromptSubmit / Stop groups — **no tool matchers at all** | N/A |
| 2 | Hook `if` path-conditions `Edit(src/**)`/`Read(.env)` now match (2.1.176) | **no `if` conditions** anywhere in hooks.json | N/A |
| 3 | `TeamCreate`/`TeamDelete` tools removed; Agent `team_name` ignored (2.1.178) | **zero references** to the CC team tools; the `team_name` grep hits are AI Maestro's OWN governance/AMCOS domain templates (server concept), unrelated to the Agent tool | N/A |
| 4 | Agent frontmatter `model:` deprecation warning (2.1.183) | 2 agents pin `model: opus` (main-agent, report-generator). `opus` is an **alias** → always resolves to current Opus 4.8; the warning targets deprecated/auto-updated **version-ids** (e.g. `claude-opus-4-7`), not aliases | Safe |
| 5 | Permission wildcard fixes `WebFetch(domain:*.x)` / mid-pattern `Read(a-*/b)` (2.1.172/176) | **no settings.json / settings.local.json** in the plugin | N/A |
| 6 | MCP retries / `claude mcp login` / idle-timeout (2.1.186/187/191) | **no `.mcp.json`** — AMAMA ships zero MCP servers | N/A |
| 7 | Skill frontmatter keys accept kebab/snake/camelCase (2.1.186) | 10 skills, valid frontmatter; optional keys (`default-enabled`/`display-name`/`fallback`/`metadata`) unused | N/A (relaxation, never breaking) |
| 8 | Nested `.claude/skills` load + precedence (2.1.178) | AMAMA is a distributed plugin (ships `skills/` at root, not nested `.claude/`) | N/A |
| 9 | `respondToBashCommands` default behavior change (2.1.186) | AMAMA hooks read stdin JSON; ship no `!`-bash-output dependence | N/A |
| 10 | Manifest / marketplace schema | no field added/removed/required in the window; `plugin.json` (v2.12.11, dep `ai-maestro-plugin ^2.6.0`) is well-formed | N/A |

Broader staleness sweep (all returned EMPTY — verified, not inferred):
- No version-pinned/deprecated model-id strings (`claude-opus-4-7`, `claude-3-*`,
  etc.) anywhere in `*.md`/`*.json`/`*.toml`/`*.py` (only the `model: opus`
  aliases in (4)).
- No stale CC-mechanics claims (`TeamCreate`/`TeamDelete`, "cannot spawn nested",
  "5 levels", "one level deep").
- No references to any setting added/changed in the window
  (`respondToBashCommands`, `footerLinksRegexes`, `availableModels`,
  `enforceAvailableModels`, `sandbox.credentials`, `teammateMode`,
  `attribution.sessionUrl`, `forceRemoteSettingsRefresh`).

## The one observation (USER decision — NOT changelog-forced)

`agents/ai-maestro-assistant-manager-agent-main-agent.md` and
`agents/amama-report-generator.md` carry `model: opus`.
- **Changelog stance:** SAFE — `opus` is an alias; no deprecation warning, resolves
  correctly under the tightened `availableModels` enforcement (2.1.172/175/176).
- **CPV CA-04 stance:** pinning a model on an agent breaks prompt-cache warmth vs
  inheriting the session model. This is a *cache* concern, NOT a changelog one, and
  is already captured by the pending cache-optimization item (the "12 CA warnings"
  pass). Cross-reference, do not duplicate here.
- **Governance stance:** the pins encode "Opus-only for delicate work" — a
  deliberate guarantee for the governance-critical MANAGER + report agents.
- **Decision deferred to USER:** keep the pins (governance guarantee) vs omit them
  (cache warmth, session-inherits-Opus anyway). Not changed under this audit
  because it is not changelog-driven and changing it unilaterally would override a
  deliberate "Opus-only" choice.

## Why no change is the correct outcome (not a dodge)

Every plugin-ecosystem change in the window either (a) targets a component AMAMA
does not ship (settings.json, .mcp.json, statusline, output-styles, workflows,
nested .claude/, tool-matcher hooks), (b) is a relaxation that cannot break a
valid plugin (skill-frontmatter case flexibility, malformed-YAML tolerance), or
(c) is a global-UX / harness behavior change with no plugin-authored surface
(`respondToBashCommands`, `/plugin` UI, MEMORY.md reminder). The two real AMAMA
touchpoints (hooks, agents) were read directly and are compatible. Manufacturing
edits to "look busy" would violate `/go-on-yourself` ("write only what is strictly
necessary") and the recheck discipline (90% of edits introduce new errors).

## Fleet implication (MANAGER coordination — separate action)

The window's *structurally* significant ecosystem changes (agent-teams redesign
removing `TeamCreate`/`TeamDelete`; nested `.claude/` precedence; `Tool(param:value)`
permission syntax; tightened `availableModels` enforcement; the comma-matcher hook
fix) WILL matter for fleet plugins that DO ship settings.json, .mcp.json,
tool-matcher hooks, or version-pinned agent models. As MANAGER I will post a
fleet-wide heads-up + per-plugin audit checklist (coordination only; per the
cross-project rule I do not edit peer repos directly) so each plugin's Claude runs
the same audit on its own surface.

## Verification

- Changelog fetched + every entry 2.1.170→2.1.191 extracted verbatim (two
  WebFetch passes to cover the full window).
- `hooks/hooks.json`, `agents/*.md` frontmatter, `.claude-plugin/plugin.json` read
  directly; `settings.json`/`.mcp.json`/statusline/output-styles/workflows confirmed
  absent; staleness greps over the whole tree returned empty.
- AMAMA test suite + gates unaffected (no source touched). Repo at v2.12.11, `main`
  with the prior 18 unpushed commits; this TRDD is the 19th-area artifact, rides
  the next publish.py pending USER approval.
