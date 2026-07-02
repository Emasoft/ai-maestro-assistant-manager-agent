---
trdd-id: 4a48ffea-7c49-4cde-8831-b2997ff8bf7a
title: Fleet coordination + verification improvements — cache staleness, idle-agent wake, coverage audit, marker friction
column: planned
created: 2026-06-21T21:38:18+0200
updated: 2026-07-02T06:15:00+0200
current-owner: amama
assignee: amama
priority: 3
severity: MEDIUM
effort: M
task-type: infra
approval-tier: 2
relevant-rules: []
release-via: none
review-requirements: [human-review]
impacts: []
external-refs: ["github.com/Emasoft/ai-maestro-janitor", "github.com/Emasoft/ai-maestro", "github.com/Emasoft/claude-plugins-validation"]
---

# TRDD-4a48ffea — Fleet coordination + verification improvements (proposals)

## ⏵ STATE — READ THIS FIRST — 2026-07-02

**✅ APPROVED + FILED 2026-07-02** (MANAGER, tier-2): P5→**ai-maestro-janitor#69**, P6→**ai-maestro#51**, P7→**claude-plugins-validation#155**, P8→**ai-maestro-janitor#70**; P9 stays a documented harness constraint (no repo owns it). AMAMA coordination complete → owner repos execute; MANAGER verify-acks on their releases.

_(historical proposal STATE — 2026-06-21)_

Cross-project improvement PROPOSALS distilled from recurring fleet-work pain this
session and prior (MAESTRO request 2026-06-21). On approval each routes to its owner
repo as a Method-1 issue.

## P5 — Cache-vs-live staleness check + "verify-against-live" before any audit

**Lesson/experience (recurring; cost real time this session):** installed plugin
CACHES lag live — core `2.7.6` cached vs `2.7.12` live; AMAMA `2.9.1` cached vs
`2.12.8` live. A 5-plugin governance audit run against the caches systematically
OVER-reported: most "HIGH/CRITICAL" findings were already fixed in live (the
staleness trap — [[verify-before-fixing-non-bugs]],
[[verify-cli-verb-source-vs-deployed]],
[[held-on-false-blocker-verify-deployed-surface]]).

**Proposal:**
- a small helper `plugin-freshness` that compares each cached plugin version to its
  live `plugin.json` (via gh) and prints a staleness table;
- bake into the audit skills: confirm the target is CURRENT main (gh HEAD / live
  version) BEFORE acting on any cache-based finding.

**Owner:** janitor (freshness helper) + the audit skills.

## P6 — Active idle-agent wake mechanism

**Lesson/experience:** GitHub issues are PASSIVE — an idle plugin session doesn't
poll, so a filed directive/work-order isn't delivered until the human owner bridges
the session ([[fleet-agent-didnt-receive-instruction]]). This stalled the R26-R40
and approval-tier waves on the owner manually waking each plugin.

**Proposal:** an active wake path — the ai-maestro server pushes a "you have
assigned work" signal, or the janitor heartbeat checks the agent's assigned
TRDDs/issues and nudges — so cross-plugin coordination doesn't depend on the human
relaying. **Owner:** ai-maestro server (+ janitor heartbeat); relates to the #46
AMP-identity / presence work.

## P7 — CPV canonical-pipeline test-coverage audit

**Lesson/experience:** a green CI "Test" job ≠ real coverage — AMAMA had 13 scripts
but 1 test (11 untested, hidden behind green; [[green-ci-hides-test-coverage-gaps]],
closed for AMAMA by TRDD-a96d744d → 67 tests). Every fleet plugin likely has the
same hidden gap.

**Proposal:** the CPV canonical-pipeline acceptance (the #44 fleet wave) adds a
coverage-audit gate — count testable components (scripts/skills/hooks/commands) vs
test files, flag untested, warn/fail below a threshold. **Owner:** CPV
(claude-plugins-validation); folds into the #44 acceptance.

## P8 — `[janitor-reload]` marker asks for an action the agent can't perform

**Lesson/experience:** the `[janitor-reload]` heartbeat marker tells the agent to
run `/reload-plugins`, but that built-in is rejected by the Skill tool — the agent
can't self-run it and must ask the user ([[janitor-reload-not-agent-runnable]]),
wasting the turn's intent.

**Proposal:** the janitor should detect that `/reload-plugins` isn't agent-runnable
and instead surface a user-facing "please run /reload-plugins" line (or find an
agent-runnable reload path) — rather than emit a marker the agent cannot honor.
**Owner:** janitor.

## P9 — Workflow rate-limit-as-string handling (known HARNESS limitation — documented, not fileable)

**Lesson/experience:** the Workflow `agent()` does NOT throw on a server rate-limit —
it RETURNS the limit text as the result string, so a try/catch misses it; a fan-out
launched into a hot throttle thrashes (≈951k tokens for ZERO output —
[[no-multiagent-workflow-during-rate-limit]]).

**Status:** this is Claude-Code/Workflow HARNESS behavior (Anthropic), NOT an
AI-Maestro repo — so it is NOT Method-1-fileable on our repos. Captured here as a
standing OPERATING CONSTRAINT: detect the RL-string in `agent()` returns + back off;
never fan out into a throttle; probe recovery with one serial agent first. (The
audit/scan skills already hand-roll this; this lesson is the durable artifact.)

## Routing

On MAESTRO review: P5 → janitor + audit skills; P6 → ai-maestro server (relates to #46);
P7 → CPV #44 acceptance; P8 → janitor; P9 stays a documented constraint (no
repo to file against).

## Notes and lessons learned

(none yet)
