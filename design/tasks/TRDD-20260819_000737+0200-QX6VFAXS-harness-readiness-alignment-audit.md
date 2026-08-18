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

- DONE: D1 (transfer create/list/resolve, commit 06c...), Q2 reroute (trdd.sh approve|refuse; governance approve/reject = MAESTRO password-gated; transfer resolve for transfers), D3 dep bump ^3.1.0, D2 pillar tools (main agent + kanban monitoring + status reporting), Q1 context-dependent review routing (team→AMIA via COS; no-team→MAINTAINER), corpus hygiene (trddgrep fix; 4 complete cards checklisted+archived; 4A48FFEA body-state claim defanged). Tests 158/158 green. validate errors 25→16.
- PENDING hub reply (msg 333e4cdd): Q3 external-blocker grammar for blocked-by (6 GRAPH-UNKNOWN-BLOCKER) + policy on 10 legacy archived TERMINAL-WITHOUT-CHECKLIST.
- PENDING: version bump + publish via canonical pipeline once remaining errors resolved; repo is AHEAD of origin (push not yet authorized this session).
- NEXT ACTION: on hub Q3 reply, fix the 6 blocked-by fields per the sanctioned grammar, then re-run trddgrep validate.

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
