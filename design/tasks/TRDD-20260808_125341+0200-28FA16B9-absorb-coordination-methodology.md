---
trdd-id: 28FA16B9
title: Absorb the multi-agent coordination methodology sections 3 5 8 and 10
column: complete
created: 2026-08-08T12:53:41+0200
updated: 2026-08-08T12:53:41+0200
current-owner: amama-session
task-type: docs
approval-tier: 0
relevant-rules: []
external-refs: ["https://github.com/Emasoft/ai-maestro/blob/governance-rules/design/methodology/multi-agent-coordination-methodology.md"]
---

# Absorb the coordination methodology (MANAGER sections)

Tier 0: applying a USER-commissioned upstream methodology to this plugin's own
persona. No deviation, no other team's tree touched.

## Source, verified first-hand

`design/methodology/multi-agent-coordination-methodology.md` on `governance-rules`,
commit **`cfd568b8`** — fetched and read (178 lines, 12 sections), not taken from
the routing note.

## Absorbed

- **§3 work-order shape** — spec card in the orderer's repo + the peer's OWN Tier-0
  card + a closure record (tag + tip sha + pasted timestamps). Plus the fold-in rule:
  add to an open order rather than issuing a second.
- **§5 refusal** — already binding here as R49 in full, so cross-referenced rather
  than duplicated. Duplicating it would have created two texts that can drift.
- **§8 channel hierarchy** — SendMessage live, GitHub issues durable/fallback, card
  canonical. Recorded as a DUTY: polling issues is part of the coordination loop.
  The load-bearing line is why it is a duty at all — *a request sitting unread in a
  working channel is indistinguishable, to the sender, from a refusal.*
- **§10 guards and authority** — a guard you cannot satisfy is a hostage; guard the
  class, not today's instance; and authority is re-evaluated per item, never
  inherited from the conversation, so relayed authority is refused even
  mid-collaboration.

## Note on §8, since it names this session

The USER's course-correction quoted in §8 ("not all communications are made via
sendMessage — check the issues") was given to THIS session. Acting on it drained 16
open issues to 1 and surfaced three items that existed only on issues, including a
fleet-wide persona defect (ai-maestro#131) and a ratified launch plan. The clause is
therefore not adopted on authority — it is adopted on a measured result.

## Acceptance criteria

- [x] §3, §8, §10 absorbed into the persona; §5 cross-referenced to R49
- [x] Existing conformance tests still green
- [x] Folded into the release already queued rather than cutting a dedicated one
- [x] Closed upstream with tag + tip sha + timestamps
