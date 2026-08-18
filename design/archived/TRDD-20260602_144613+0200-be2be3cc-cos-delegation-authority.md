---
trdd-id: BE2BE3CC
title: COS delegation authority — which decisions COS handles vs escalates to MANAGER
column: complete
created: 2026-06-02T14:46:13+0200
updated: 2026-06-02T14:50:19+0200
current-owner: assistant-manager
assignee: assistant-manager
priority: 2
severity: HIGH
task-type: docs
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: [6]
release-via: none
target-branch: main
test-requirements: []
runtime-targets: [macos, linux]
impacts: []
attempts: 0
test-failures: 0
last-test-result: not-run
implementation-commits: []
ci-runs: []
external-refs: []
---

# COS delegation authority

## ⏵ STATE — READ THIS FIRST ON RESUME — 2026-06-02T14:46:13+0200

**Goal:** Make the CHIEF-OF-STAFF a real gatekeeper instead of an
unfiltered relay. Currently every team-agent request the COS receives
is passed straight upstream to the MANAGER — defeating the reason the
COS exists (to absorb load).

**Design (locked):** Two-tier filter at the team boundary:
- COS-AUTONOMOUS — COS decides within the team, no upstream.
- COS-ESCALATE — COS forwards to MANAGER, who applies the EXISTING
  presence-aware flow (amama-presence-tracker + amama-autonomous-fallback
  plus reversibility-matrix + hard-floor): escalate-to-USER if present,
  decide-autonomously if absent, golden rules ALWAYS to USER.

**Presence is MANAGER-tier, not COS-tier.** The COS filters the same
way regardless of user presence; presence only changes the MANAGER's
downstream behavior (already built via amama-presence-tracker reading
the AI Maestro server /api/users/me/presence). Optional robustness: a
janitor-written presence breadcrumb fallback when the server is down.

**Deliverables:** (1) references/cos-delegation-authority.md; (2)
amcos-prrd-trdd-kanban skill COS-filter section; (3) COS persona filter
rules; (4) amama-presence-tracker janitor-breadcrumb fallback note.

**STATUS: COMPLETE.** Shipped: references/cos-delegation-authority.md, amcos-prrd-trdd-kanban skill + COS persona (two-tier filter), amama-presence-tracker janitor-breadcrumb fallback. Janitor breadcrumb write requested at janitor#15 (its call). All commits local-only pending push.

## Problem

The user created the COS to prevent the MANAGER being overloaded by
every team agent's requests/approvals/problem-reports. Governance R6
forces team agents to write only to the COS. But no rule distinguishes
what the COS can decide itself from what it must escalate — so the COS
passes everything through unfiltered, nullifying its purpose.

## Design

Full tier tables in references/cos-delegation-authority.md (bundled in
the prrd-trdd-kanban universal skill).

## Approval log

- 2026-08-16T16:46:00+0200 — AUDITED, stays `complete`. Verified against the COS repo's
  tree, not this card's prose. Three of four deliverables are real:
  `agents/ai-maestro-chief-of-staff-main-agent.md:208,220,236` and
  `skills/amcos-prrd-trdd-kanban/SKILL.md:15,46` carry the COS-AUTONOMOUS/COS-ESCALATE
  two-tier filter, and `skills/amama-presence-tracker/SKILL.md:38` (this repo) carries the
  janitor-breadcrumb fallback.
  **CORRECTION — one line above is FALSE:** the STATE block's `STATUS: COMPLETE` claims it
  shipped `references/cos-delegation-authority.md`. No such file exists in either repo
  (`find . -iname "cos-delegation-authority*"` → only this TRDD). The tier tables were
  folded into `skills/amcos-prrd-trdd-kanban/SKILL.md` instead of a separate reference
  file. The work shipped; the artifact name in the prose did not. Do not go looking for
  that file, and do not read its absence as unfinished work.
  Also stale: "All commits local-only pending push" — the deliverables are in the COS repo's
  tracked tree.
