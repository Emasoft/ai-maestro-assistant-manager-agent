---
trdd-id: Y6V1TOGN
title: Align AMAMA to Claude Code 2.1.208-2.1.224 and decide the native cross-session messaging question
column: dev
created: 2026-08-07T18:28:40+0200
updated: 2026-08-07T20:42:21+0200
current-owner: amama-session
task-type: infra
approval-tier: 0
relevant-rules: []
external-refs: ["https://code.claude.com/docs/en/release-notes"]
---

# Align AMAMA to Claude Code 2.1.208 → 2.1.224

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-08-07

- USER directive 2026-08-07: study the CC changelog and align the codebase.
- **Audited, already compliant — do NOT redo:** all 11 skills carry
  `context: fork` + `background: false` (2.1.218 made `fork` background BY
  DEFAULT; the explicit opt-out is what keeps them foreground); no agent name
  contains `:` (2.1.218 now rejects those); nothing uses the Task tool's
  deprecated `mode:` param (2.1.212); nothing asserts the old
  no-nested-subagents rule (2.1.219 raised default spawn depth to 3).
- **DONE this session:** stale model comments on both agent files; the
  cross-session-messaging position in the persona.
- **OPEN — the one real decision:** ratify (or overturn) the position below
  with the hub. Everything else here is mechanical.

## The decision that needs the hub: native cross-session messaging

CC 2.1.224 shipped **native cross-session `SendMessage` + `ListAgents`** — any
Claude Code session on any of the owner's machines can message any other, by
name, **with no server in the path**.

That lands underneath a governance model built on the opposite assumption. R23
routes every server interaction through the frozen CLI *because a direct call is
unaudited even when it works*; R42 locks cross-agent drive to self-only with one
carve-out. A native session-to-session message satisfies neither: it leaves no
trace in the AI Maestro ledgers, so a mandate or approval delivered that way did
not happen as far as the fleet's own record is concerned.

**Position taken in the persona, conservative pending ratification:** the native
channel is OUT OF BAND for every governed interaction (mandates, approvals,
refusals, title changes, dispatch — all stay on AMP through the COS). It is
legitimate for reaching a Claude session that is not an AI Maestro agent at all,
and for operational chatter no rule governs. Explicitly NOT a way around a 403
or 409 — that is the same act with the audit removed.

**Why conservative rather than adopting it:** the cheap direction is reversible.
If the hub ratifies a wider use, widening later costs a doc edit. If we adopt it
now and it turns out governance traffic went unaudited for a week, nothing
reconstructs what was said.

## Acceptance criteria

- [x] Skills/agents audited against 2.1.208-2.1.224 for breaking harness changes
- [x] Stale model-version claims corrected (`opus` is a FAMILY alias → Opus 5 since 2.1.219)
- [x] Persona states the native-cross-session-messaging position
- [ ] Hub asked to ratify or overturn that position (issue on Emasoft/ai-maestro)
- [ ] If ratified wider: revisit the persona section and the AMP-only framing

## Notes

`crossSessionInbound` / `dialogExpiry` (2.1.224) are the settings that decide
whether an inbound cross-session message to a bypassed-permissions session is
held for approval. Fleet-level config, not this plugin's to set — but the
MANAGER should know they exist before recommending anything.

## MANAGER ruling — 2026-08-07, on the COS-routed Tier-2 (orchestrator TRDD-NSWPM93D)

A COS routed AMOA's transport-policy proposal to me per R6, asking me to pick
AMP-only / AMP-primary-with-exceptions / agent-discretion. **Reframed and ruled:
policy is not open — R42.3 already says AMP is the ONLY channel by which one agent
may influence another. I read its edge; I did not choose a policy.**

1. **Influence is AMP-only** — direct, mandate, assign, approve, refuse, prioritise,
   **or attest**. Attestation named explicitly because it looks like a report and is
   the one that already landed wrongly (a peer credited AMOA with GitHub ruleset
   changes it never made, after guessing the sender from a session display name).
2. **Non-influencing native traffic permitted, narrowly**, under two conditions:
   self-identify by **project/repo, never session name** (names are mutable display
   strings — that mutability is the mechanism behind the misattribution), and act on
   nothing received until independently verified.
3. **Outbound-unreachable senders are outside every exception, strengthened**: do not
   act on their content at all beyond verifying the facts from source. A transport
   that can direct an agent but cannot receive its correction is a one-way authority
   claim, and four measured failures today were instances of exactly that.
4. **No native fallback for AMP hiccups** — AMOA's restraint upheld and made
   explicit rather than left as an omission, because an undocumented absence is a gap
   someone fills while a documented prohibition is a decision.

5. **AMP unreachable — influence is SUSPENDED, not rerouted** (added on the COS's
   second pass; points 1-4 said what an agent must NOT do and never said what it
   MUST, and an unstated obligation is the vacuum someone fills). The agent sends
   nothing that directs/approves/refuses/attests by any other means; **records the
   intent durably** (own TRDD or own-repo issue, timestamped); escalates the
   *outage* to its own USER as a fault report, not a governance act; sends the real
   message when AMP recovers. Two guards, without which the record becomes the
   workaround: a record states intent at time T and **directs no one** ("I intended
   to request X" is a fact about me; "do X" is influence) — and **the recipient must
   not act on the record**, only on the AMP message that follows, because a durable
   note read by its target is still an unaudited channel if acting on it is allowed.
   Principle: **the fallback for an unavailable audited channel is never an
   unaudited one** — it is waiting, plus a note that makes the wait reconstructible.

**NOT ruled, escalated to the hub (Tier 3):** whether R42.3's "ONLY channel" text
should be amended now that the platform ships a second transport beneath it, and
whether R42.1's "queued input" clause reaches auto-delivered native messages.

## Governance-doc fork — reported by the COS, NOT independently verified

The COS reports the hub's `governance-rules` doc has forked: a local copy with
**240 unpushed commits** at v5.3.2 containing R42.8 (7 occurrences), against a
published tip at v5.2.0 containing none.

**Verified here:** published tip `2ca29e43`, committed 2026-08-05T12:25:55Z — static
for two days. **NOT verified:** either occurrence count or either version number.
Three tree queries did not surface the R42-bearing document on that branch and this
machine holds no `ai-maestro` clone. Recorded as a report I could not check — the
same standing I asked the COS to give my ruling.

**Why it is actionable anyway:** the implication does not depend on the numbers.
**An unpushed rule cannot bind** — a rule on one disk is a draft carrying a rule's
number. That *strengthens* the R42.8 correction shipped in `2a3378c` (procedure
kept, citation demoted): if the local text does grant unblock authority, procedure
still survives and authority still waits for publication. It also explains why AMOA
"caught a non-existent R42.8" while I posted an "R42.8 correction" — both right,
different artifacts.

**The hazard to surface to the hub:** with the newest text unpushed, an agent
verifying against the canonical source gets the OLDER answer and is correct to,
which inverts what verification is for. The hub's tree — surface on `ai-maestro#125`,
do not touch.

**Disclosure recorded in the ruling:** I reached this position independently ~4h
earlier for this plugin, before the routing note — corroboration or bias, but not
fresh analysis of the COS's evidence. What the COS added was four measured failures.

**Verification gap, stated:** `design/proposals/` on the orchestrator repo's main
branch does not list TRDD-NSWPM93D (commit `9c1c7b8` appears local/unpushed), so the
ruling rests on the routing note, not the canonical record. Both cited `ai-maestro#76`
comments were verified to exist (5219694921, 5220208974).

## Approval log
