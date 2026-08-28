---
trdd-id: ACR3CQ4R
title: Align AMAMA to Claude Code 2.1.248
column: dev
blocked-by: []
created: 2026-08-28T02:10:57+0200
updated: 2026-08-28T02:10:57+0200
release-via: publish
implementation-commits: []
current-owner: amama-session
task-type: infra
min-approval-requirement: none
relevant-rules: []
external-refs: ["https://code.claude.com/docs/en/release-notes"]
---

# Align AMAMA to Claude Code 2.1.248

## Scope

The delta only. A prior read-only pass (`reports/cc-alignment/CHECKLIST.md`, 2026-08-27)
scanned this repo against **2.1.234 → 2.1.247** across every slice and found **zero**
stale claims, and TRDD-I75YHAUR already landed the 2.1.233–2.1.240 text. So this card
covers **2.1.248 alone**, plus the deliberate decision not to adopt one new key.

Checklist used: `reports/cc-alignment/CHECKLIST-2.1.248.md` (codes X1–X8).

## Findings

Three slices scanned in parallel:

| slice | report | result |
|---|---|---|
| `skills/` | `reports/cc-alignment/248-skills-scan.md` | clean, X1–X8 |
| `docs/ shared/ README CLAUDE CHANGELOG` | `reports/cc-alignment/248-docs-scan.md` | clean, X1–X8 |
| `agents/ commands/ hooks/ scripts/ tests/` | `reports/cc-alignment/248-agents-scan.md` | see below |

The only passage in the repo that tracks the native cross-session channel release by
release is the section **"The harness now has its OWN cross-session messaging — it is
NOT AMP"** in `agents/ai-maestro-assistant-manager-agent-main-agent.md`. It ended at
2.1.240 and needed the 2.1.248 facts appended.

## Decision — `experimental.cacheTtl` is NOT adopted

2.1.248 added `experimental.cacheTtl` (`"5m"` / `"1h"`) to agent frontmatter. Both of
this plugin's agents deliberately omit `model:` under **RP-MODEL-01** (RULED 2026-08-08,
ai-maestro#136): a role-plugin author must not make a cost/capability decision that
spends the **operator's** budget, and a pinned key is the spelling that silently degrades
under an org restriction.

A per-agent cache TTL is the same kind of decision, and 2.1.243 already shipped the
operator's spelling of it — the `promptCacheTtl` / `subagentPromptCacheTtl` **settings**.
Pinning the frontmatter key would move that choice from the operator to the role author,
which is exactly what RP-MODEL-01 forbids; `experimental.` only sharpens the objection.
No key is added, and none should be added later without a new ruling.

## Acceptance

- [ ] Cross-session section carries the 2.1.248 facts and its heading names 2.1.248.
- [ ] No `experimental.cacheTtl` key in either agent file; the decision is recorded here.
- [ ] `uv run pytest` green.
- [ ] Every claim added is checked against the 2.1.248 release notes, not a subagent's paraphrase.
