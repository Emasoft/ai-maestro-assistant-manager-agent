---
trdd-id: QX6VFAXS
title: Harness-readiness alignment audit — pillar-tool adoption, stale CLI syntax, review-column routing
column: complete
created: 2026-08-19T00:07:37+0200
updated: 2026-08-19T01:25:00+0200
current-owner: amama-session
task-type: audit
min-approval-requirement: none
relevant-rules: [23, 28]
---

# Harness-readiness alignment audit (USER goal 2026-08-19)

## ⏵ STATE — CLOSED 2026-08-19

All findings fixed or ruled; v2.18.0 released via publish.py (all gates green, pushed, GitHub release). Residuals are hub-side: TRDD-PTFPGSLV (trddgrep scoped-blocker parsing + grandfather boundary). Nothing to resume.

## Findings

| id | severity | where | defect |
|---|---|---|---|
| D1 | MAJOR | amama-approval-workflows/references/api-endpoints.md:70 | `transfer --agent …` — actual CLI is `transfer create/list/resolve` |
| D2 | MAJOR | all skills + main agent | no trddgrep/prrdgrep/specgrep usage (3-pillars tools) |
| D3 | MINOR | .claude-plugin/plugin.json | dependency `ai-maestro-plugin ^2.6.0` vs installed 3.1.25 |
| Q1 | RULING | routing tables (amama-github-routing, amama-role-routing) | review-column owner: maintainer (USER) vs integrator (Part B2) |
| Q2 | BLOCKER | amama-approval-workflows, main agent | documented `governance.sh approve` call fails at runtime (--password required) |

## Acceptance

- [x] D1 fixed and consistent across skill + references (transfer create/list/resolve)
- [x] D2: pillar tools referenced at board/PRRD/spec query sites, with fallback per core pattern
- [x] D3 bumped to ^3.1.0 after hub confirm
- [x] Q1/Q2/Q3 resolved per hub rulings; routing/docs/corpus updated (validate 25 -> 11, all sanctioned residuals pending hub TRDD-PTFPGSLV)
- [x] plugin validates (CPV strict clean) + tests 158/158 green; v2.18.0 released via publish.py

Closed complete on 2026-08-19.
