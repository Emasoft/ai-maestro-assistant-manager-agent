---
trdd-id: KBXCQ6GG
title: Claude Code 2.1.206 to 2.1.221 changelog alignment audit for AMAMA
column: complete
created: 2026-08-04T12:10:55+0200
updated: 2026-08-04T12:10:55+0200
current-owner: amama
assignee: amama
priority: 2
severity: MEDIUM
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
implementation-commits: [c4d2554]
external-refs: ["https://code.claude.com/docs/en/hooks.md"]
audit-trigger: user-report
audit-target: ai-maestro-assistant-manager-agent (the AMAMA plugin surface)
audit-conclusion: one-defect-found-and-fixed
---

# TRDD-KBXCQ6GG — Claude Code 2.1.206→2.1.221 changelog alignment

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-08-04T12:10

**✅ COMPLETE.** One real defect found and fixed (`c4d2554`); every other candidate in the
window verified inapplicable by reading the repo, not by inference. Successor to
[[TRDD-3HSUEP3Y]], which audited the 2.1.170→2.1.191 window and concluded benign.

**NEXT ACTION:** none. Do not re-audit this window.

## The one defect — a dormant bug that 2.1.218 woke up

`scripts/amama_stop_check.py` emitted `permissionDecision` and `permissionDecisionReason`
inside `hookSpecificOutput` for a **Stop** event. Those fields are **PreToolUse-exclusive**;
Stop accepts only `hookEventName` and `additionalContext` there, and blocks solely through the
top-level `decision`/`reason` pair — which the hook already set correctly.

Why it mattered *now* rather than whenever it was written:

> 2.1.218 — "Fixed hooks with exit code 2 not blocking as documented when the hook's stdout
> JSON fails schema validation"

A schema-invalid exit-2 payload used to fail validation and **silently not block**. After that
fix it blocks as documented. So whether this hook performed its entire stated purpose —
blocking exit on incomplete coordination work — depended on which side of that release the CLI
was on, with no symptom on either side. That is the generalizable shape: **a payload defect
that is inert only because a bug elsewhere is swallowing it is not a benign defect, it is a
scheduled one.**

Fixed in `c4d2554`: invalid fields dropped; the report path moved from an undocumented
top-level `report` key into `additionalContext` (the documented Stop channel); `details` pushed
into the report FILE only, where extra keys cost nothing.

**Verified against the shipped schema, not from memory** (`hooks.md` fetched and quoted):
blocking path exits 2 and emits zero invalid fields at either level while still writing the
full report; the no-issues path stays a silent exit 0; the `agent_id` subagent short-circuit is
unchanged; ruff clean.

## Everything else in the window — checked, inapplicable

| change | verdict |
|---|---|
| 2.1.207 `${user_config.*}` rejected in shell-form hook commands | N/A — no `user_config` anywhere; hooks use `${CLAUDE_PLUGIN_ROOT}`, which is unaffected |
| 2.1.207 `pluginConfigs` no longer read from project settings | N/A — never used |
| 2.1.212 Task-tool `mode` deprecated | N/A — never passed |
| 2.1.218 agent names may not contain `:` | N/A — the one agent name is clean |
| 2.1.210 `Write(path)`/`Glob(path)`/`NotebookEdit(path)` rules warn | N/A — no such permission rules |
| 2.1.218 `context: fork` skills default to background | **Already correct** — all 10 skills carry the `background: false` opt-out |
| 2.1.218 SessionStart reports `source: "fork"` | N/A — the SessionStart hook does not branch on `source` at all |
| 2.1.217/219 subagent nesting + concurrency caps | N/A — no cap env vars set, no programmatic fan-out in shipped surfaces |
| 2.1.219 Opus 5 default / model ids | N/A — the only `claude-opus-4-7` strings are inside a frozen TRDD record (§12), which must not be edited |

## Notes and lessons learned

**A near-miss worth recording.** The `context: fork` row was initially flagged as affecting all
ten skills — read from a grep that stopped at `context: fork` without reading the next
frontmatter line, where `background: false` already sat. The correction cost nothing because it
happened before any edit, but the same haste one line later would have "fixed" ten correct
files. Grep locates a candidate; it does not establish the finding.
