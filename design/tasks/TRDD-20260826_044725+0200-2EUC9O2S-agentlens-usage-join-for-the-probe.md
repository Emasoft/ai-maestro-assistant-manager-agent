---
trdd-id: 2EUC9O2S
title: Agentlens usage join for the agent-state probe
column: backburner
created: 2026-08-26T04:47:25+0200
updated: 2026-08-26T04:47:25+0200
current-owner: amama-session
task-type: feature
min-approval-requirement: none
blocked-by: []
external-refs: ["ai-maestro:TRDD-LT5N2JA4", "github.com/Emasoft/ai-maestro-assistant-manager-agent/issues/35"]
---

# Agentlens usage join for the agent-state probe

Carved out of `TRDD-U17K7AX6` by the hub's ruling of 2026-08-26 (option b), so that
card could close against a revised 2-of-3 scope without silently retiring the third
source the USER named.

## Why this is parked, not unbuilt

The probe's `usage` key is a **typed `null` on purpose**. The agentlens sessions view
keys on **Claude Code session id**; the probe keys on **agent id**; there is no proven
mapping between them. A guessed join does not degrade gracefully — it **misattributes
cost to the wrong agent**, which is worse than a visible null, because a null is
legible as missing and a wrong number is not. The absence is documented in the hub
service's own docstring and is a *measured* gap, not an oversight.

## The one thing that unblocks this

A **proven** session-id ↔ agent-id join key — one that can be demonstrated, not
inferred: either agentlens records the agent id, or ai-maestro records the Claude Code
session id, on a field both sides can be read from. Until such a key exists and is
verified on live data, this card stays parked. Do not open it to "try a heuristic".

## Acceptance criteria

- [ ] A join key exists on live data and is verified in both directions (no orphans in a
      sample, no two agents claiming one session).
- [ ] `probe`'s `usage` returns real per-agent figures, and `sources.usage` reports `ok`.
- [ ] A wrong/absent join still yields `null` + `unavailable: <why>` — never a guess.

## Approval log
