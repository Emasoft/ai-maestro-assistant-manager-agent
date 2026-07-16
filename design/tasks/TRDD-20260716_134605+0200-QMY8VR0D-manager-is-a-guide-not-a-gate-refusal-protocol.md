---
trdd-id: QMY8VR0D
title: A manager is a guide not a gate — refusal protocol in persona, tool, memory, and fleet
column: dev
created: 2026-07-16T13:46:05+0200
updated: 2026-07-16T13:46:05+0200
current-owner: amama-manager
task-type: feature
scope: project
release-via: publish
mandated-by: user
approved: true
approval-judge: user
approval-datetime: 2026-07-16T13:46:05+0200
min-approval-requirement: user
relevant-rules: [1]
implementation-commits: [8d4de6f, 1fe5d68]
---

# A manager is a guide, not a gate — the refusal protocol

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-07-16

- **Mandate (USER, 2026-07-16, two messages):** (1) a manager does not simply permit or
  refuse — every refusal names the defect, states the bar, invites re-proposal, pushes
  toward alternatives, and iterates until the need is met or truly unmeetable; write it
  into the MANAGER main-agent prompt. (2) **The MESSAGE is the channel** — agent↔manager,
  COS↔manager, agent↔orchestrator dialogue with follow-ups and replies IS the management;
  the mechanical approval via tools is only a bureaucratic requirement. (3) Share the
  principle globally via wikimem + open issues on the ORCHESTRATOR and COS repos linking it.
- **DONE — everything buildable is landed:**
  - Persona: "YOU ARE A GUIDE, NOT A GATE" section, messages-first, four elements,
    iteration-as-conversation, the incident, the proposer-side corollary; the old
    "You are the gate" line removed (`8d4de6f`, `1fe5d68`).
  - Tool: `decide --refused` requires `--refusal-reason`; error teaches the four elements;
    content-free default deleted; mixed-batch reason-leak bug fixed; 34/34, both new tests
    falsified. Tool check explicitly does NOT discharge the message duty.
  - Wikimem (USER scope, global): `…/plugins/data/ai-maestro-janitor-ai-maestro-plugins/
    memory/manager-is-a-guide-not-a-gate.md` — already user-scoped, no symlink needed.
  - Issues: hub **ai-maestro#71** (fleet REFUSAL PROTOCOL for the governance rules +
    proposer-side corollary; amended with the messages-first correction),
    **ai-maestro-orchestrator-agent#30** (persona ask, member↔orchestrator channel),
    **ai-maestro-chief-of-staff#28** (dual duty: own Tier-1 refusals AND relaying MANAGER
    decisions with reasoning intact, replies carried back up).
- **NEXT ACTION:** drive #71 / ORCH#30 / COS#28 to adoption (their Claudes must be running
  to answer). Fold the ratified rule text into the #66-settled-parts propagation wave.
- **The incident (evidence):** plugin-Claude proposed commands → hub denied most on
  security grounds (CORRECTLY) → proposer began deleting dependent skills → USER caught it
  by chance, explained the defect → hardened, re-proposed, approved. A correct refusal and
  a destructive one are indistinguishable in the refuser's log — the duty attaches to
  every refusal.

## Notes

`relevant-rules: [1]` — PRRD G1.1 governs the three issue posts. Born-approved: a USER
mandate is approved the moment it is written (mandated-by: user).
