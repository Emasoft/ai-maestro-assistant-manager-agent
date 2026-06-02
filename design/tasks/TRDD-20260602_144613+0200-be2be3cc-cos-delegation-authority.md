---
trdd-id: be2be3cc-3947-454f-8c93-7d368363f53c
title: COS delegation authority — which decisions COS handles vs escalates to MANAGER
column: dev
created: 2026-06-02T14:46:13+0200
updated: 2026-06-02T14:46:13+0200
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
  + reversibility-matrix + hard-floor): escalate-to-USER if present,
  decide-autonomously if absent, golden rules ALWAYS to USER.

**Presence is MANAGER-tier, not COS-tier.** The COS filters the same
way regardless of user presence; presence only changes the MANAGER's
downstream behavior (already built via amama-presence-tracker reading
the AI Maestro server /api/users/me/presence). Optional robustness: a
janitor-written presence breadcrumb fallback when the server is down.

**Deliverables:** (1) references/cos-delegation-authority.md; (2)
amcos-prrd-trdd-kanban skill COS-filter section; (3) COS persona filter
rules; (4) amama-presence-tracker janitor-breadcrumb fallback note.

**NEXT ACTION:** write references/cos-delegation-authority.md.

## Problem

The user created the COS to prevent the MANAGER being overloaded by
every team agent's requests/approvals/problem-reports. Governance R6
forces team agents to write only to the COS. But no rule distinguishes
what the COS can decide itself from what it must escalate — so the COS
passes everything through unfiltered, nullifying its purpose.

## Design

Full tier tables in references/cos-delegation-authority.md (bundled in
the prrd-trdd-kanban universal skill).
