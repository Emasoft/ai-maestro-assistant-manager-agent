---
trdd-id: U17K7AX6
title: Agent-state probe skill for MANAGER and CHIEF-OF-STAFF
column: testing
blocked-by: []
created: 2026-08-06T12:44:39+0200
updated: 2026-08-26T00:00:00+0200
current-owner: amama-session
task-type: feature
approval-tier: 0
external-refs: ["ai-maestro:TRDD-LT5N2JA4", hub-directive-2026-08-06, "github.com/Emasoft/ai-maestro-assistant-manager-agent/issues/35", "github.com/Emasoft/ai-maestro/issues/130"]
---

# Agent-state probe skill for MANAGER and CHIEF-OF-STAFF

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-08-26 (3rd)

- **BLOCKER CLEARED.** The hub reports `ai-maestro:TRDD-LT5N2JA4` COMPLETE + deployed
  (13c3e710, closed 69921da3). Column back to `testing`, `blocked-by` emptied.
- **VERIFIED FIRST-HAND on this host** (not from the hub's message): `probe` is a real
  verb in the DEPLOYED `~/.local/bin/aimaestro-agent.sh` (control-tested — a bogus verb
  returns `Unknown command`, `probe` reaches the API), `cmd_probe` in
  `~/.local/bin/agent-commands.sh:281` calls `GET /api/agents/<id>/probe`, and that route
  answers **401 auth_required** unauthenticated (not 404), so it exists and is gated.
- **NOT VERIFIABLE FROM HERE — the card's own NEXT ACTION is still open.** This host has
  **no AID** (`aid-auth.sh` yields no usable bearer; the CLI reports "No authentication
  method available"), so the probe PAYLOAD cannot be read from this session. Whether it
  carries `lastError` (classified) + `blockedSince` is therefore UNCONFIRMED — do not
  wire the skill to fields nobody has seen.
- **ACCEPTANCE CRITERION 2 IS NOW CONTESTED, not met.** The hub states the agentlenspro
  feed (`usage`) is **deliberately ABSENT** — no proven join key, and it must not be
  synthesized. That is one of the three USER-named sources. Closing the card on the other
  two would retire an unmet criterion silently, which is exactly what the 2nd STATE block
  refused to do. Needs a USER/hub ruling: accept 2-of-3 as the final shape, or keep the
  agentlenspro join as its own follow-up card.
- **NEXT ACTION:** hub asked (both questions above). On answer: if the fields exist, wire
  `skills/amama-agent-unblock/SKILL.md` to the single `probe` call replacing the
  multi-call shape (its line 163 already names this supersession), then close.

## ⏵ STATE — superseded, 2026-08-06 (2nd)

- **SPEC LANDED, SKILL BUILT.** The hub's spec arrived the same day as
  [issue #35](https://github.com/Emasoft/ai-maestro-assistant-manager-agent/issues/35);
  the USER said go. Built `skills/amama-agent-unblock/SKILL.md` carrying the §4
  procedure + the §5 blocked-only rule, wired into the persona (frontmatter skills
  list + the "No agent-command power" section's ONE exception) and the README.
- **VERIFIED FIRST-HAND, not from the issue text:** `aimaestro-session.sh block-state`
  exists in the deployed `~/.local/bin` copy (control-tested against a bogus verb, which
  returns `unknown command`), and its own `help` carries the R42/R42.8 limits table +
  the 0/419 rationale. R23 conformance 5/5 with the new skill included.
- **SUPERSEDED — do NOT carry forward:** the first STATE block's "wait for the hub,
  do not start construction". The GO arrived.
- **SHIPPED in v2.15.0**, CI+Release+Notify all green. #35 items ① and ② closed;
  item ③ (probe-shape feedback) answered on #35 and escalated to the hub repo.
  Item ② was a **no-op, verified**: `read-prompt` appeared nowhere in this repo.
- **NOW `blocked`, not `testing`** — and the distinction is the point: the SKILL half is
  delivered, but this card's acceptance criterion "all three named sources harvested"
  (janitor global-report fields, agentlenspro, statusline-hook data) is the hub's
  aggregated probe `TRDD-LT5N2JA4`, which does not exist yet. Calling the card complete
  because the visible half shipped would retire an unmet criterion silently.
- **NEXT ACTION:** none of mine — wait for the hub's probe. When it lands, verify it
  carries `lastError` (classified) + `blockedSince`, then finish and close.

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

## Blocker note (2026-08-19, TRDD-QX6VFAXS hygiene)

`blocked-by: LT5N2JA4` is a CROSS-PROJECT blocker — hub TRDD `ai-maestro:TRDD-LT5N2JA4` (the aggregated probe carrying lastError + the janitor/agentlenspro feeds). Scoped citation parsing shipped hub-side (TRDD-PTFPGSLV, c242d4ca): trddgrep now accepts this spelling and lints WARN GRAPH-CROSS-PROJECT-BLOCKER instead of ERROR.
