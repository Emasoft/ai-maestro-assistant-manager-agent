---
trdd-id: QX6VFAXS
title: Harness-readiness alignment audit — pillar-tool adoption, stale CLI syntax, review-column routing
column: dev
created: 2026-08-19T00:07:37+0200
updated: 2026-08-19T00:07:37+0200
current-owner: amama-session
task-type: audit
min-approval-requirement: none
relevant-rules: [23, 28]
---

# Harness-readiness alignment audit (USER goal 2026-08-19)

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-08-19

- Audit pass 1 DONE: decoupling checker clean on shipped tree; frontmatter/hooks/plugin.json valid.
- D1 stale `governance.sh transfer` syntax in amama-approval-workflows/references/api-endpoints.md — IN PROGRESS.
- D2 zero trddgrep/prrdgrep/specgrep adoption — pending (pattern: core plugin ama-trdd-find).
- D3 dependency `ai-maestro-plugin ^2.6.0` stale vs core 3.1.25 — awaiting hub confirm of ^3.1.0.
- Q1 review-column ownership (USER: maintainer; Part B2: integrator) — RULING PENDING at hub (msg 9b4cb094).
- Q2 governance approve/reject hard-require --password vs skills' "AID-authorized, no password" — RULING PENDING at hub.
- NEXT ACTION: apply D1 edit; then D2 skill edits; hold D3/Q1/Q2 on hub reply.

## Findings

| id | severity | where | defect |
|---|---|---|---|
| D1 | MAJOR | amama-approval-workflows/references/api-endpoints.md:70 | `transfer --agent …` — actual CLI is `transfer create/list/resolve` |
| D2 | MAJOR | all skills + main agent | no trddgrep/prrdgrep/specgrep usage (3-pillars tools) |
| D3 | MINOR | .claude-plugin/plugin.json | dependency `ai-maestro-plugin ^2.6.0` vs installed 3.1.25 |
| Q1 | RULING | routing tables (amama-github-routing, amama-role-routing) | review-column owner: maintainer (USER) vs integrator (Part B2) |
| Q2 | BLOCKER | amama-approval-workflows, main agent | documented `governance.sh approve` call fails at runtime (--password required) |

## Acceptance

- [ ] D1 fixed and consistent across skill + references
- [ ] D2: pillar tools referenced wherever board/PRRD/spec queries occur, with fallback per core pattern
- [ ] D3 bumped after hub confirm
- [ ] Q1/Q2 resolved per hub ruling and routing/docs updated
- [ ] plugin validates + tests green; version bumped via publish pipeline
