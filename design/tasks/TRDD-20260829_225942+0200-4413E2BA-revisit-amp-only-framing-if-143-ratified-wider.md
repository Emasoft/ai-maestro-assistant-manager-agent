---
trdd-id: 4413E2BA
title: Revisit the persona AMP-only framing if ai-maestro 143 ratifies a wider native cross-session channel
column: backburner
created: 2026-08-29T22:59:42+0200
updated: 2026-08-29T22:59:42+0200
current-owner: amama-session
task-type: docs
min-approval-requirement: none
blocked-by: []
parent-trdd: Y6V1TOGN
external-refs: ["github.com/Emasoft/ai-maestro/issues/143"]
review-after: 2026-11-01
---

# Revisit the AMP-only framing if #143 ratifies a wider native channel

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-08-29

**This card is a CARVE-OUT, not new work.** It is criterion 5 of `TRDD-Y6V1TOGN`,
which was closed complete on 2026-08-29 against its four unconditional criteria.
Criterion 5 was **carved out, not met** — it is conditional on a ruling that does
not exist yet, so leaving it inside Y6V1TOGN kept that card asserting
`human_review` while nobody was reviewing it.

- **The condition:** `Emasoft/ai-maestro#143` is ratified in a way that WIDENS
  the sanctioned use of Claude Code's native cross-session `SendMessage` /
  `ListAgents` beyond the conservative position AMAMA's persona currently states.
- **If and only if that happens:** revisit the persona's cross-session-messaging
  section and its AMP-only framing, and widen it to match the ruling.
- **If #143 is ratified as posed** (correct R42.3's factual clause, authority ban
  unchanged) — or refused — this card is **cancelled**, not completed. Nothing to
  do: the persona already states the conservative position, which that outcome
  leaves correct.
- **NEXT ACTION:** none. Do not poll #143 and do not pre-write the revision — the
  wording depends on the ruling text. `review-after: 2026-11-01` parks it from
  drift; it is a snooze, not a mute, so if #143 is ruled sooner, open this
  immediately.

## Status of #143 as of 2026-08-29

OPEN, USER-tier, awaiting a ruling. Last updated 2026-08-25, 4 comments — and
**none of the four is the human USER deciding.** All four were posted through the
shared owner `gh` identity by agent sessions proposing and adopting each other's
wording; the last one restates the ask as still open. No expected date is
recorded anywhere. Verified with the hub session on 2026-08-29, which measured
the same thing independently.

## The position this card would revisit

Stated in AMAMA's persona, conservative pending ratification: the native
cross-session channel is **out of band for every governed interaction** —
mandates, approvals, refusals, title changes, dispatch all stay on AMP through
the COS. It is legitimate for reaching a Claude session that is not an AI Maestro
agent at all, and for operational chatter no rule governs. It is explicitly NOT a
way around a 403 or 409 — that is the same act with the audit removed.

**Why it was taken conservatively:** the cheap direction is reversible. Widening
later costs a doc edit. Adopting it early and discovering governance traffic went
unaudited for a week leaves nothing that reconstructs what was said.

## Acceptance criteria

- [ ] #143 reaches a USER ruling (any outcome).
- [ ] If ratified WIDER: the persona's cross-session-messaging section and the
      AMP-only framing are updated to match the ruling text, and this card closes
      `complete`.
- [ ] If ratified as posed, or refused: this card closes `cancelled` with the
      ruling cited — the persona needs no edit.

## Approval log
