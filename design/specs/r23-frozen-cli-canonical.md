---
spec: r23-frozen-cli-clause
status: normative
authority: Emasoft/ai-maestro (hub)
source-issue: https://github.com/Emasoft/ai-maestro/issues/107
source-comment: https://github.com/Emasoft/ai-maestro/issues/107#issuecomment-5190121266
source-comment-date: 2026-08-05T09:35:49Z
fetched: 2026-08-05
consumed-by: skills/amama-*/SKILL.md
conformance-test: tests/test_r23_conformance.py
---

# R23 — the canonical frozen-CLI clause

This file is the **single source** for the R23 transport prohibition that every
`SKILL.md` in this plugin carries verbatim. It is a **test fixture, not a runtime
artifact**: no skill loads it, no script reads it at runtime. Only
`tests/test_r23_conformance.py` reads it, to prove each skill's copy still matches.

## Why every skill duplicates this text instead of linking to it

The hub ruled duplication on ai-maestro#107, and rejected a pointer, for a reason that
is specific rather than stylistic: **skills load on demand and in isolation.** Every
skill in this plugin is `context: fork`. A skill loaded alone cannot resolve
"see the canonical R23 wording" — the agent consulting that skill at decision time
would hold a reference and not the rule. That is the same defect as keeping the rule
only in the persona, moved up one level.

So the rule is copied, and **the conformance test is what makes copying safe**. Without
the test a copy is just drift waiting to happen; with it, drift fails a gate. The test
is the load-bearing half of this arrangement, not an optional extra.

## The canonical text (copy verbatim, including the `>` markers)

> **Never call the ai-maestro server API directly.** No skill, agent, command, hook, MCP config, bundled script, or setting may issue a request to `/api/…`, nor instruct an agent to (R23.1). Every server interaction goes through the frozen CLI layer installed with ai-maestro — `~/.local/bin/aimaestro-*.sh`, `amp-*.sh`, `aid-*.sh` (R23.2).
>
> Two independent reasons, and either alone invites a workaround:
> 1. **The CLI runs the pipeline, governance and audit gates that a raw route bypasses.** A direct call is *unaudited even when it works* — it succeeds and leaves no trace in the ledgers the fleet is governed by.
> 2. **Server routes are renameable; the CLI interface is frozen** (R23.4). Route-coupled code breaks silently on a server release, and the breakage surfaces as an agent that has quietly stopped working.
>
> There is **no element-level exception — not even for the core `ai-maestro-plugin`** (R23.5). The boundary is the script layer, not any particular plugin.

## What this replaced, and why the old wording was a live defect

Until 2026-08-05 the skills carried a one-line clause naming only two CLIs
(`aimaestro-agent.sh` / `aimaestro-teams.sh`) as "the only sanctioned interface", and
`amama-status-reporting` carried a truncated form of even that, missing the word
"frozen", the CLI names, and the hooks-and-scripts sentence.

That was **narrower than the rule**, and narrow in the direction that causes harm: an
agent needing `amp-kanban-get` would not find it among "the only sanctioned interface"
and could conclude either that `amp-*` is forbidden or that no CLI covers its need —
and the second conclusion leads straight to the raw route the rule exists to prevent.
The repo already contradicted itself on this: the persona names `aimaestro-governance.sh`
and `amp-*`, and TRDD-DE33HN3J records `amp-kanban-*.sh` as deployed and frozen.

## Known limitation — this mirror can drift from the hub silently

The canonical source is a GitHub issue comment, not a versioned file in the hub repo.
The conformance test proves **repo-internal** consistency: that all ten skills match
*this* file. It cannot detect the hub amending R23 upstream. Re-check
`source-comment` and refresh `fetched:` at each publish; if the hub later publishes R23
as a versioned file, repoint `source-comment` at it and prefer that.
