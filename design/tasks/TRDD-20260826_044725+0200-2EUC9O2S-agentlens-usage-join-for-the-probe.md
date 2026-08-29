---
trdd-id: 2EUC9O2S
title: Agentlens usage join for the agent-state probe
column: backburner
created: 2026-08-26T04:47:25+0200
updated: 2026-08-29T22:56:00+0200
current-owner: amama-session
task-type: feature
min-approval-requirement: none
blocked-by: []
external-refs: ["ai-maestro:TRDD-LT5N2JA4", "github.com/Emasoft/ai-maestro-assistant-manager-agent/issues/35"]
---

# Agentlens usage join for the agent-state probe

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-08-29

**The park is now MEASURED, not asserted.** A live-data probe on 2026-08-29
falsified the only candidate join key. Do NOT re-investigate — the answer is
recorded and reproducible.

- **Neither side records the other's id.** ai-maestro `types/agent.ts:143
  AgentSession` = index/status/workingDirectory/createdAt/lastActive — no Claude
  Code session id. agentlens session records = sessionId/workspace/accountId/
  model/title — no agent id.
- **The only overlap is a path** (`workingDirectory` ↔ `workspace`), and it
  fails BOTH acceptance directions on live data:
  - uniqueness: one workdir (`…/Code/SKILL_FACTORY`) is claimed by TWO agents;
  - coverage: 2 of 31 agentlens workspaces match an agent workdir; 93.5%
    orphaned; **2.4%** of 19,367 session records attributable; 10 of 12 real
    agent workdirs have zero coverage. Both matches are test agents.
- **Therefore `usage: null` + `sources.usage: unavailable` is CORRECT** and
  stays. A workspace join would misattribute cost — the exact failure below.
- **NEXT ACTION:** none in this repo. This card can only be unblocked by an
  UPSTREAM change in another project (ai-maestro records the CC session id, or
  agentlens records the agent id). Per the cross-project rule this repo files an
  issue and never edits them. Hub consulted 2026-08-29; awaiting its answer on
  whether such a key already exists before filing.
- **Evidence (read first, do not redo the probe):**
  `reports/amama-join-key-probe/20260829_225600+0200-2EUC9O2S-join-key-falsified.md`
- **SUPERSEDED — do NOT carry forward:** the framing that this is parked pending
  *investigation*. Investigation is finished. It is parked pending an upstream
  schema change.

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
