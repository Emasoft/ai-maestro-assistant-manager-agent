---
trdd-id: U17K7AX6
title: Agent-state probe skill for MANAGER and CHIEF-OF-STAFF
column: backburner
created: 2026-08-06T12:44:39+0200
updated: 2026-08-06T12:44:39+0200
current-owner: amama-session
task-type: feature
approval-tier: 0
external-refs: [hub-directive-2026-08-06]
---

# Agent-state probe skill for MANAGER and CHIEF-OF-STAFF

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-08-06

- **INTAKE ONLY.** Filed from a USER directive given to the ai-maestro HUB Claude on
  2026-08-06 (relayed to this session the same day). The hub owns the cross-repo design;
  implementation direction for THIS plugin arrives via hub propagation (issue / AMP).
- **NEXT ACTION:** wait for the hub's coordination. Do NOT start construction — new
  construction needs a USER/hub GO (`ATOM-QZK7-LW8Z`).
- Recorded here so the board reflects the expected incoming work instead of it living
  only in one session's head.

## What the USER asked for (verbatim intent, condensed)

The assistant-manager (MANAGER title) plugin must be instructed on how to use the
ai-maestro-plugin skills to **detect and unblock any situation where an agent stops
responding to messages**. Ideally a specific function/skill to probe an agent's state —
`idle | blocked | permission-prompt | api-error | …` — plus all other data about it,
including the **last error message**, available to both MANAGER and CHIEF-OF-STAFF.

## Data sources to harvest (named by the USER)

1. **ai-maestro-janitor HTML global report** — already tracks per-agent state + last
   error. Hub is to ask the janitor how it collects this and whether it can share those
   fields with the ai-maestro server.
2. **agentlenspro CLI** — per-agent diagnostics/context info.
3. **ai-maestro-plugin statusline hook** — the hook parses the statusline event input
   JSON (rich per-session info) and sends it to the ai-maestro server.

Deliverable shape: one simple skill for MANAGER + COS that unifies all three sources
into a single per-agent state view (state enum + metadata + last error message).

## Acceptance criteria (draft — to be finalized when the hub's spec arrives)

- [ ] Skill callable by MANAGER and COS sessions; returns state enum + last error per agent.
- [ ] All three named sources harvested (janitor report fields, agentlenspro, statusline hook data on the server).
- [ ] Documented unblock playbook per state (idle vs blocked vs permission prompt vs api error).

## Approval log
