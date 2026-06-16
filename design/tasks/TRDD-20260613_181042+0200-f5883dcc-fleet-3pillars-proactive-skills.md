---
trdd-id: f5883dcc-3ee0-4335-85cb-c2aa12fe9b9e
title: Fleet 3-pillars as proactive ama-* skills in the core plugin + governance-aware wiring + fool-proof rule injection
column: planned
created: 2026-06-13T18:10:42+0200
updated: 2026-06-16T02:49:24+0200
current-owner: amama
assignee: amama
priority: 1
severity: HIGH
effort: XL
task-type: infra
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: none
review-requirements: [human-review]
impacts: [public-api, install-script, config-schema]
external-refs: ["github.com/Emasoft/ai-maestro-plugin"]
---

# TRDD-f5883dcc — 3-pillars as proactive `ama-*` skills (core plugin) + governance-aware wiring

## ⏵ STATE — READ THIS FIRST ON RESUME — 2026-06-16

**✅ PHASE A SHIPPED (core ai-maestro-plugin v2.7.9, 2026-06-16).** The granular `ama-*` skills landed
exactly as specified below: `ama-prrd-{get,find,edit,propose}`, `ama-trdd-{write,find,update,transition}`,
`ama-kanban-render`, `ama-proposal-approvals` — REPLACING the monolithic `prrd-trdd-kanban`; governance-
enforcing + role-permission-sliced; decoupling-safe (local PRRD.md / design/tasks / kanban.py files — zero
`/api/`). `team-kanban`/`team-governance` retained (server-backed → ride amp-kanban-*/governance CLIs, R22).
MANAGER verify-acked on #8 (issuecomment-4713826803). **Correction logged:** a transient MANAGER re-scope
comment on #8 (prior session) wrongly said "extend the monolith, don't add ama-*" — retracted; THIS TRDD's
granular approach was right all along (granularizing ≠ redundant; it's the USER's "many granular skills").
**NEXT: Phase B** — governance-rule auto-install via the core SessionStart hook + fleet wiring each role
plugin's agents (main+sub) to the `ama-*` skills with their permission slice. Architect epic-create = a
SERVER task → team-kanban/amp-kanban path (not the local ama-trdd-write).

---
_(historical STATE — 2026-06-13)_

## ⏵ STATE (historical) — 2026-06-13

**USER directive (2026-06-13).** The 3 pillars (TRDD/PRRD/kanban) are being built as SKILLS
(many — one per operation), and agents must use them **PROACTIVELY** — but **role-appropriately**,
because the governance structure is everything: many roles have **read-only** kanban access,
every role follows **approval-tier** rules per TRDD, and PRRD changes are **proposal-gated**.
"This is the pillar of the whole ai-maestro system of development." Make it **fool-proof.**

### The architecture (DECIDED with the USER)
1. **Skills live in the CORE plugin `ai-maestro-plugin`** — NOT in AMAMA (the manager). The core
   plugin is installed in EVERY agent, so every role can find the skills. AMAMA's per-plugin
   `amama-prrd-trdd-kanban` + `amama-proposal-approvals` are REDUNDANT → removed (like the memory
   per-plugin skills). Same for any other role's per-plugin 3-pillars skills.
2. **Naming = `ama-*`** (AMA = **A**i **M**aestro **A**gent — the shared core). Collision-free vs
   the role prefixes (`amama-`/`amaa-`/`amoa-`/`amia-`/`amcos-`). Granular, one skill per operation:
   - `ama-trdd-write` · `ama-trdd-find` · `ama-trdd-update` · `ama-trdd-transition` (column moves)
   - `ama-prrd-get` · `ama-prrd-find` · `ama-prrd-edit` (silver, gated) · `ama-prrd-propose` (proposal queue)
   - `ama-kanban-render` (read) · `ama-kanban-*` (write ops, gated)
   - `ama-proposal-approvals` (the batch approve/refuse/archive — MANAGER/COS gated)
   (These wrap the EXISTING base-plugin scripts: get-prrd.py, prrd-edit.py, findtrdd.py, kanban.py,
   prrd_lib.py, bootstrap_design.py, amama_proposal_approvals.py — already in `scripts/prrd-trdd/`.)
3. **The skills ENFORCE governance** — each `ama-*` skill checks the caller's role + the operation's
   permission/approval-tier and refuses or routes accordingly (e.g. `ama-prrd-edit` refuses non-MANAGER
   on a silver rule → tells them to `ama-prrd-propose`; `ama-kanban` write ops refuse read-only roles;
   `ama-trdd-transition` enforces the column-transition matrix per `manager-approval-defaults.md`).
   The skill is the choke-point; the agent can't bypass governance by invoking it.
4. **Governance RULES injected fool-proof into EVERY agent** — the four canonical rules
   (`trdd-design-tasks.md`, `trdd-approval-tiers.md`, `prrd-design-rules.md`,
   `manager-approval-defaults.md`) are **bundled in the core plugin** and **auto-installed to
   `~/.claude/rules/`** at session start by the core plugin's SessionStart hook (or MCP) — the
   SAME PROVEN mechanism the janitor uses for `markdown-memory-recall.md` and llm-externalizer uses
   for its rule. Plugins CAN install rule files this way (verified). Use `~/.claude/rules/`
   (user-global, loaded every session) — NOT a project `.claude/rules/` (uncertain auto-load).
   Idempotent + overwrite-on-version-change so every agent, every machine, always has the current rules.
5. **Per-role proactive wiring** — each role plugin's agents (main AND sub) get a proactive-3-pillars
   block tuned to THAT role's permissions: recall the kanban/TRDDs before acting; author/transition
   via the `ama-*` skills they're allowed; self-classify approval tier; propose PRRD changes via the
   gated path. The role's permission slice is injected via the auto-installed rules + the agent .md.
   PROPAGATE into sub-agent prompts (sub-agents inherit nothing).

### Governance-permission matrix (the "role-appropriate" core — from the four rules)
| Op | MANAGER | ORCH | ARCH | INT | COS | MEMBER | AUTON | MAINT |
|---|---|---|---|---|---|---|---|---|
| read kanban/TRDD/PRRD | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| author proto-TRDD | ✅ | ✅ | ✅ | ✅ | ✅ | via COS | ✅ | ✅ |
| TRDD column transition | ✅ | dispatch | design | release | relay | signal-only | ✅ | ✅ |
| edit SILVER PRRD | ✅ | propose | propose | propose | relay | propose-via-COS | propose | propose |
| edit GOLDEN PRRD | ❌ USER-only | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| approve TRDD (tier) | T2/T3 | T1 | T0 | T0 | T1 | T0 | →USER | →MGR |

## Plan (parallels the memory rollout — same shape: core skills + auto-installed rules + proactive wiring)
1. **Design sign-off** (this TRDD) + propose the architecture to the **base plugin** (it hosts the
   `ama-*` skills + the rule-auto-install hook). Coordinate the granular-skill split + the hook.
2. **Base plugin builds:** the `ama-*` skills (governance-enforcing wrappers over the existing scripts)
   + bundles the four rules + the SessionStart-hook auto-install to `~/.claude/rules/`. Publishes.
3. **AMAMA (exemplar):** remove `amama-prrd-trdd-kanban` + `amama-proposal-approvals`; wire the main
   agent + `amama-report-generator` sub-agent to the `ama-*` skills with the MANAGER permission slice
   (full write + approval authority). Bundle into AMAMA's governance-rework release.
4. **Fleet:** direct each role plugin to wire its agents (main + sub) to the `ama-*` skills with ITS
   role slice + remove its per-plugin 3-pillars skills. Verify-and-ack per live tree.
5. **Verify fool-proof:** confirm a fresh agent on a clean machine gets the rules auto-installed +
   the `ama-*` skills available + the role-correct proactive directives. No agent can mutate
   governance it isn't permitted to (the skills refuse).

## Why
The 3-pillars are the development backbone. If the operation skills live per-plugin, they drift +
not every role has them; if the governance rules aren't in every agent's context, agents
self-classify approval tiers / propose PRRD changes wrong. Centralizing the skills in the core
plugin (installed everywhere) + auto-installing the rules (proven mechanism) + governance-enforcing
skills + role-tuned proactive wiring = every agent uses the pillars correctly, by construction.

## Acceptance criteria
- `ama-*` skills in the core plugin; per-plugin 3-pillars skills removed fleet-wide.
- The four governance rules bundled in core + auto-installed to `~/.claude/rules/` every session (idempotent).
- Each role plugin's agents (main + sub) carry the role-correct proactive-3-pillars block.
- The skills ENFORCE the permission matrix (refuse/route) — governance can't be bypassed.
- AMAMA exemplifies it. Verified on a clean-machine agent.
