---
trdd-id: d369cf76-4192-4137-b4d1-86cd8b345b99
title: Fleet-wide — wire every plugin's agents (main AND sub) to proactively use the memory system
column: planned
created: 2026-06-13T17:36:10+0200
updated: 2026-06-14T02:20:43+0200
current-owner: amama
assignee: amama
priority: 2
severity: HIGH
effort: L
task-type: infra
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: none
test-requirements: []
review-requirements: [human-review]
impacts: [public-api]
external-refs: ["github.com/Emasoft/ai-maestro-janitor/issues/18"]
---

# TRDD-d369cf76 — Fleet proactive-memory wiring (main + sub agents)

## ⏵ STATE — READ THIS FIRST ON RESUME — 2026-06-13

**🟢 FINAL SPEC RECEIVED (janitor, via assistant-manager#15 — supersedes the per-plugin
`<plugin>-memory-*` model in the body below).** Memory skills are **GLOBAL, from the
user-level janitor plugin** — names **CONFIRMED UNCHANGED**: `janitor-memory-recall` /
`janitor-memory-write` / `janitor-memory-update` (no rename). Role plugins **USE the global
skills; they do NOT ship their own**. The locked config:
- **3-scope storage:** LOCAL `~/.claude/projects/<slug>/memory/` (harness, unchanged) ·
  **PROJECT `<repo>/.claude/project/memory/`** (tracked+pushed; needs gitignore exception:
  `.claude/**` ignored then `!.claude/project/memory/**`) · USER `${CLAUDE_PLUGIN_DATA}/memory/`.
- **Rollout mechanism = the NEW `/janitor-memory-bootstrap` skill** — each plugin's own main
  agent runs it once (creates `.claude/project/memory/` + gitignore exception, seeds the
  arch-hub page + MEMORY.md, points the agent at the recall rule + skills + proactive contract).
- **Proactive contract** (now in the skills + `markdown-memory-recall` rule): recall-before-acting
  · write/update-after-solving · maintain-project-wikimem · scope-routing. **MY DELTA:** also
  propagate the contract into SUB-AGENT prompts (sub-agents inherit nothing — USER's must-have).
- **REMOVE the fleet's redundant per-plugin skills** — AMAMA strips `amama-memory-recall`/`-write`
  + reconciles `rules/memory-protocol.md` (confirming removal with janitor on #15).
- **EXECUTE ON JANITOR PUBLISH** — the janitor's skills/bootstrap are committed but UNPUSHED
  (pending USER review). Align now (design locked); run `/janitor-memory-bootstrap` + the rework
  once it ships. No `column:` collision — memory lives under `.claude/project/memory/`, the
  3-pillars under `design/` (orthogonal).
- **🔴 SECOND BLOCKER — CPV #120 (discovered 2026-06-14).** `validate_gitignore` raises an
  UNSATISFIABLE `[MINOR] missing coverage for .claude/` for any plugin that tracks content under
  `.claude/` (exactly the PROJECT-memory pattern `.claude/project/memory/**`): its check is
  `git check-ignore -q -- .claude`, which only passes if the whole `.claude` dir is ignored — but
  git cannot re-include a path whose parent dir is excluded, so `.claude/**` + `!.claude/project/memory/**`
  can never satisfy it. MINOR = exit 3 → blocks the exit-0-only publish gate. So EVERY fleet
  memory-rework publish (AMAMA's included) is blocked until CPV #120 is fixed. Filed + owned by the
  **janitor's Claude** (it owns the memory model) — do NOT duplicate; track it. The memory rollout
  is now gated on BOTH the janitor's memory publish AND CPV #120's fix.

**AMAMA IS IN SCOPE (USER emphasized — it's the MANAGER, the most important role).** AMAMA's
own agents MUST be updated as the exemplar, not just the fleet's:
- `agents/…-main-agent.md` — currently references the per-plugin `amama-memory-recall/write`
  (lines 37-38, 48-54). REWIRE to the global `janitor-memory-*` + ADD the PROPAGATE-to-sub-agents
  clause.
- `agents/amama-report-generator.md` (sub-agent) — ADD the proactive-memory block (recall + propagate).
- REMOVE the `amama-memory-recall`/`-write` skills + reconcile `rules/memory-protocol.md`
  (keep as a thin pointer to the global rule, or drop) — per #31's answer.
- Execute bundled with the memory-path follow-up release (one coherent AMAMA memory-rework publish).

**USER directive (2026-06-13).** Adopting the memory *skills* is NOT enough — every role
plugin's agent `.md` files must be **wired to PROACTIVELY invoke** the memory system
(recall-before-acting + write-after-learning), and **critically that wiring must apply to
SUB-AGENTS too**, not only the main agent. "This is one important task you have in preparing
the fleet." Coordinate with each plugin to update their agent `.md` files.

**SEQUENCING.** The janitor is finalizing the new memory skill + a PROJECT-memory path change
(incoming "in the next few hours"). The new memory skill "will certainly contain the
instructions" (the HOW). So: WAIT for the janitor's memory skill to land, then coordinate the
wiring referencing the final skill — and bundle AMAMA's own wiring with the memory-path
follow-up release (avoid double-publishing AMAMA).

**AMAMA's own state (scoped 2026-06-13):**
- `agents/…-main-agent.md` — ✅ ALREADY wired (lines 48-54: "Recall before acting" + capture via amama-memory-write).
- `agents/amama-report-generator.md` (SUB-AGENT) — ❓ needs review/wiring (the user's "even sub-agents" gap). Add at least recall-where-relevant + the propagation principle.

## The requirement (what every plugin must add to its agent `.md` files)

Every `agents/*.md` (main AND each sub-agent) gets a proactive-memory block. Canonical text
(adapt `<plugin>-memory-*` to the plugin's skill names):

```
## Memory — proactive (applies to YOU and every sub-agent you spawn)
- RECALL before acting: before debugging a recurring problem, making/repeating a decision,
  recommending, or acting on a recurring alert, invoke `<plugin>-memory-recall` with the
  SYMPTOM (the user's words / the error text) — "have we hit this before?". Cheap; do it first.
- WRITE after learning: when something durable + non-obvious is confirmed (a preference, a
  gotcha + its why, a decision), invoke `<plugin>-memory-write` — `description:` indexed by
  the SYMPTOM (the question), NOT the answer's jargon.
- PROPAGATE: when you spawn a sub-agent, include this same memory directive in its prompt so
  it recalls + writes too. Memory discipline is inherited, not assumed.
```

## Plan
1. **Wait** for the janitor's new memory skill + PROJECT-path change to land (TRDD tracks it via task #9). Reference its final instructions.
2. **AMAMA (lead by example):** wire `amama-report-generator.md` (sub-agent) with the recall + propagation block; confirm the main agent's block matches the canonical text + adds the PROPAGATE clause. Bundle into the memory-path follow-up release.
3. **Fleet coordination:** message every role plugin (orchestrator, integrator, programmer, architect, autonomous, chief-of-staff, maintainer, integrator, code-auditor, amvcp, + base) to add the proactive-memory block to ALL their `agents/*.md` (main + sub). Verify-and-ack each against its live tree.
4. **Verify:** for each plugin, grep its `agents/*.md` for the recall/write/propagate directive; a plugin is done only when EVERY agent file (not just the main) carries it.

## Why
Skills that are never invoked are dead weight. The fleet adopted memory-recall/write skills,
but without an explicit agent-level "recall before acting / write after learning / propagate
to sub-agents" instruction, agents won't use them — and sub-agents (which inherit nothing by
default) definitely won't. This wiring is what makes the memory system actually function
across the fleet. It is a restart-readiness item.

## Acceptance criteria
- Every role plugin's `agents/*.md` (main + every sub-agent) carries the proactive-memory block.
- Sub-agent SPAWN sites instruct propagation of the memory directive.
- AMAMA exemplifies it (main + amama-report-generator).
- Verified against each plugin's live tree + acked.
