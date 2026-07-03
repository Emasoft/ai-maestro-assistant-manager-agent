---
trdd-id: BB3ATT83
title: Token-efficiency audit + fix of the AMAMA plugin (context-inflation / cache waste)
column: dev
created: 2026-07-03T03:38:27+0200
updated: 2026-07-03T03:38:27+0200
current-owner: amama
assignee: amama
priority: 3
severity: MEDIUM
effort: M
task-type: refactor
release-via: publish
relevant-rules: []
test-requirements: [unit, lint]
impacts: []
---

# TRDD-BB3ATT83 — Token-efficiency audit + fix of the AMAMA plugin

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-07-03

**Origin:** USER ran `/code-review xhigh --fix` targeting "whole codebase — all causes
of token wasting / cache inefficiency / context inflation; bash commands that skip
lean-ctx/distill/tldr; each such line/skill = an error." Whole-codebase audit (NOT a diff).

**DONE (durable):**
- Reviewed the runtime-instruction + executable surface: 15 scripts, 2 agents, 4 commands,
  hooks, 3 shared, 69 skill files.
- **25 findings** identified + verified (finders cited exact file:line; distinguished
  bounded-vs-unbounded output; marked env-specific vs tool-agnostic). Reports:
  - `reports/token-review/scripts.md` (5), `hooks-agents-cmds.md` (4),
    `skills-A.md` (4), `skills-B.md` (4), `skills-C.md` (8).
- **Consolidated fix plan:** `reports/token-review/FIX-SPEC.md` — 4 disjoint lanes
  (P = Python/careful+tests; M1 = github-routing+agents; M2 = approval+amcos;
  M3 = session-memory+status+comms). Rubric: `reports/token-review/RUBRIC.md`.
- Every fix is **TOOL-AGNOSTIC** (compact-print, `--json`/`--jq` narrowing,
  discard-stdout, redirect-to-file, delegate-to-script, scoped-read) → the
  shipped-plugin portability tension is MOOT; do NOT hardcode ctx_*/distill/tldr.

**NOT DONE — 0 fixes applied.** The 4 fixer agents were spawned but ALL died instantly
on the **5-hour session cap** ("session limit · resets 5:20am Europe/Rome"), 0-6 tool
uses each. Working tree verified **CLEAN** (`git status --porcelain` empty) — no
half-applied edits.

**NEXT ACTION (after the session-cap reset, ~5:20am Rome 2026-07-03):**
1. Re-spawn the 4 fixer lanes from `reports/token-review/FIX-SPEC.md` (P=opus+run tests,
   M1/M2/M3=sonnet; disjoint files, working-tree only, NO git). One at a time, 3s apart.
2. Wire K9 skill-pointer AFTER Lane P reports its append-script decision (the pointer at
   `skills/amama-session-memory/references/record-keeping-formats.md:287` — M3 was told
   NOT to touch it).
3. Validate: plugin Python test suite + `CLAUDE_PRIVATE_USERNAMES="$(whoami)" CPV
   remote_validation.py plugin .` (--strict). Fix regressions.
4. Report fixed/skipped to USER. Do **NOT** commit/push/publish (USER did not ask).

**Highest-value fixes:** S1 `publish.py run()` dumps full stdout of every test/lint/
validator even on success → quiet-on-success (biggest surface). K9 session-memory
Write-tool append re-emits the WHOLE log each append (O(n²)) → delegate to an atomic
append script.

**Known skips (note to USER, don't force):** H4 `commands/amama-respond-to-amcos.md`
needs a NEW delegated script (behavioral redesign) — own follow-up TRDD. K9 depends on
Lane P deciding whether a ≤20-line atomic-append script is warranted.

**Durable artifacts to read before acting:** `reports/token-review/FIX-SPEC.md` (the plan),
the 5 `reports/token-review/*.md` finding files (the evidence).

## Background

AMAMA is a shipped Claude Code plugin. "Token waste" = anything that puts more tokens into
the orchestrator context (re-read every turn) than necessary: verbose script/hook stdout,
skill instructions that dump whole files / raw CLI output, agent prompts pasting content vs
paths or missing reporting-rules, cache-unfriendly ordering. The audit found the biggest
surfaces are (a) `publish.py run()` printing all wrapped-command output on success, and
(b) session-memory logs appended via the Write tool (whole-log re-emit). All fixes are
tool-agnostic so they don't break users lacking lean-ctx/distill/tldr.
