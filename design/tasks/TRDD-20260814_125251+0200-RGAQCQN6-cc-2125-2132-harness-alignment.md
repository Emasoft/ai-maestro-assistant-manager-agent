---
trdd-id: RGAQCQN6
title: Align AMAMA to Claude Code 2.1.225-2.1.232
column: dev
created: 2026-08-14T12:52:51+0200
updated: 2026-08-14T12:52:51+0200
current-owner: amama-session
task-type: infra
approval-tier: 0
relevant-rules: []
external-refs: ["https://code.claude.com/docs/en/release-notes"]
---

# Align AMAMA to Claude Code 2.1.225 → 2.1.232

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-08-14

- USER directive 2026-08-14: study the CC changelog (2.1.221-2.1.232 pasted in
  full) and align the codebase.
- **Predecessor:** `TRDD-Y6V1TOGN` aligned this repo to **2.1.208-2.1.224** and
  stays open on its own hub-ratification box (`ai-maestro#143`). This card is
  deliberately SEPARATE, not an extension of it — one atomic task per TRDD, and
  stuffing a new sweep into a card whose only open item is an external ask would
  muddy both.
- **Audited, already compliant — do NOT redo (each verified first-hand, not
  inferred):** no reference anywhere to `ultraplan` (removed 2.1.222) or
  `ultrareview` (aliased to `/code-review` 2.1.223); no subagent-cap or
  spawn-depth claim (200-cap removed 2.1.224); no shipped doc asserts
  read-before-write, so the Write-tool relaxation (2.1.228) breaks nothing; no
  live assumption that spawned agents run in the FOREGROUND, so the 2.1.232
  background-by-default change for non-teammate agent spawns breaks nothing.
- **`context: fork` + `background: false` on all 11 skills is still correct.**
  2.1.232's background-by-default applies to *agent spawns*, NOT to skill
  `context: fork`; the 2.1.218 opt-out those skills carry remains load-bearing.
  `tests/test_skill_frontmatter_intent.py` already pins that intent.
- **NEXT ACTION: none — the persona edit below is DONE.** What remains is the
  hub ask, which is blocked on the USER exactly as `Y6V1TOGN`'s is.

## The delta that actually mattered

Only ONE section of the codebase was stale: the persona's
`### The harness now has its OWN cross-session messaging` block, written and
titled to 2.1.224. Four platform changes since bear on it.

**None of them touch the load-bearing argument** — a native session-to-session
message still leaves no trace in the AI Maestro ledgers, so a governance act
delivered that way still did not happen as far as the fleet's record goes.
Three of the four *tighten* the conservative position rather than loosening it.

### 1. Session-name uniqueness (2.1.232) does NOT relax the name rule

The `Y6V1TOGN` ruling forbids self-identifying by session name because **names
are mutable display strings**, and that mutability is the mechanism behind the
AMOA misattribution. 2.1.232 makes interactive session names unique *per
machine*. Uniqueness is not immutability, and three holes survive:

1. a name is still renameable mid-flight;
2. uniqueness covers **live sessions on one machine**, so a dead session's name
   recycles — "orchestrator" today need not be "orchestrator" yesterday, which
   is precisely the misattribution shape;
3. the auto-variant (`name-word-word`) is a **new** hazard: a session can be
   running under a name it did not choose, so even self-identification by name
   can misfire on your own name.

Writing "names are unique now" would invite the reading "names are safe now".
They are not.

### 2. `ListAgents` offline/cloud labels (2.1.229) — a MAY, not a MUST

Ruling point 3 (outbound-unreachable senders) was previously discoverable only
by a failed send; `offline` makes it partly visible beforehand. This is
**application of the existing rule, not a new one.** Deliberately NOT written as
a mandatory pre-check: that invites the inverse failure of reading `online` as
proof of reachability, when it is a point-in-time label that can flip before a
correction ever arrives. "Act on nothing until independently verified" already
dominates any pre-check.

### 3. Friction removed (2.1.232) — argues for MORE caution

Bare-name delivery drops the ref-confirmation step, and `@`-mention adds a
one-keystroke path to another session. Neither was designed as a safety guard,
but the confirmation step was incidentally acting as one. Cheaper misdirection
is a reason to keep the position conservative, not to relax it.

### 4. Start-by-name to remote machines (2.1.225) — reinforcement

SendMessage can now *initiate* to Remote Control sessions on other machines,
where before it could only reply. This widens the unaudited channel's reach to
exactly the population most likely to be outbound-unreachable — the case ruling
point 3 already treats most strictly.

## Acceptance criteria

- [x] Repo audited against 2.1.225-2.1.232 for breaking harness changes
- [x] Verified the retired features (`ultraplan`, `ultrareview`, subagent cap)
      are genuinely unreferenced rather than assumed so
- [x] Verified `background: false` is still the correct opt-out post-2.1.232
- [x] Persona section retitled to a range and the four deltas folded in, each
      stated WITH its non-implication
- [ ] Delta folded into the PENDING hub ask (`ai-maestro#143`) rather than
      opened as a second issue — blocked on the USER, same as `Y6V1TOGN`

## Gotcha that will bite the next editor

The persona region around lines 294-318 uses **load-bearing line breaks**. The
`skillaudit` rule `A2A_CROSS_AGENT_INJECT` matches **per line**, and those
paragraphs name every token class it looks for. Re-flowing them onto single
lines re-arms the rule and blocks the publish gate at `--strict`. The in-file
comment at lines 296-300 says so; lines 315-318 are split mid-sentence for the
same reason and were left untouched by this edit. Earliest failure signal: the
publish gate reddens.

## Approval log
