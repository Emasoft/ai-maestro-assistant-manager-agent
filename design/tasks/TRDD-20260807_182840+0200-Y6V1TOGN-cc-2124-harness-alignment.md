---
trdd-id: Y6V1TOGN
title: Align AMAMA to Claude Code 2.1.208-2.1.224 and decide the native cross-session messaging question
column: human_review
blocked-by: []
created: 2026-08-07T18:28:40+0200
updated: 2026-08-19T00:55:00+0200
current-owner: amama-session
task-type: infra
approval-tier: 0
relevant-rules: []
external-refs: ["github.com/Emasoft/ai-maestro/issues/143", "https://code.claude.com/docs/en/release-notes"]
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

## Governance-doc fork — MEASURED FIRST-HAND (supersedes the earlier unverified note)

`docs/GOVERNANCE-RULES.md`, read directly off each ref via the contents API:

| ref | version | `R42` count | `R42.8` |
|---|---|---|---|
| **`main`** (default branch) | **4.0.2** | **0** | 0 |
| `governance-rules` (tip `2ca29e43`, 2026-08-05) | 5.2.0 | 14 | 0 |
| COS's local, 240 unpushed — NOT checkable here | 5.3.2 | 20 | 7 |

**The headline is not R42.8 — it is that `main` has NO R42 at all.** An agent that
does the obviously-correct thing and reads the default branch finds no AMP-only
rule whatsoever. Note also that **even the published SSOT branch has zero R42.8**,
so the `2a3378c` demotion was right against BOTH readable refs.

### Bindingness — the earlier formulation was too crude

"An unpushed rule cannot bind" does not cover the state R42 is actually in:
published to a non-default branch. The refined rule:

> **What makes a rule bind is not that it was pushed. It is that its authority is
> discoverable from where a conscientious agent would look.**

1. **One disk, unpushed** → draft. Cannot bind. (R42.8; `ai-maestro#125` open.)
2. **Pushed to an undesignated branch** → cannot bind; nobody knows to look.
3. **Pushed to a DESIGNATED SSOT** → binds, if the designation is discoverable.
4. **On the default branch** → binds.

R42.3 is state 3. "Canonical" is a **designation**, not a property the default
branch owns by being default: `main` is a git convention, SSOT is a governance
decision.

**CORRECTION (COS, verified here): the state-3 proviso is UNMET.** I claimed the
designation was discoverable because I carry it in THIS repo's standing traps —
but that is a note in my own tree, discoverable to me, not to the fleet. I answered
a question about a SHARED property using my own local state as the sample. Fourth
instance of today's error class.

Measured on `CLAUDE.md@main` (1855 lines, every match printed, no `head`):
- `:579` — "`docs/GOVERNANCE-RULES.md` — **Full** governance rules (… the full
  **R1-R20** set)"
- `:1714` — "Team governance rules **R1-R20** (semver v3.7.0+)"
- `:1716` — the ONLY mention of the branch, framing `governance-rules` as a fork
  `main` syncs FROM, addressed to *plugins fetching raw markdown*.

So the default branch does not present a document with a gap where R42 should be —
**it labels it "Full" and states a range that ends at R20.** An agent that reads
`main`, finds no R42 and concludes it does not exist is not being careless; it is
being **correctly informed by a wrong index**.

### Consequence for enforcement — MANAGER's lane, and it is now urgent

R42.3 **binds the agents who know it**, and **cannot fairly be enforced against an
agent that checked the canonical location and was told the document was complete.**
That is the difference between a rule and a trap. Any sanction, refusal or
correction grounded in R42 against such an agent is unsound while `:579`/`:1714`
stand. Today's ruling is unaffected — it binds ME, and I know the rule — but the
fleet currently holds a rule it cannot uniformly enforce, which makes the one-line
fix urgent rather than cosmetic.

**The defect to fix (surface, do not touch — hub's tree):** state 3 requires the
designation to be discoverable, and `main`'s 4.0.2 gives no pointer — it reads as a
complete governance document that simply has no AMP rule. **A stale canonical
location is worse than an empty one**: an empty one 404s and prompts a search, a
stale one answers confidently. Ask is NOT to re-litigate R42 — it is **one header
line on `main`'s copy** ("partial; canonical text at ref `governance-rules`") or a
merge.

### My own negative finding was the unreliable one

The earlier "three tree queries did not surface the document" was FALSE and
self-inflicted. Re-run against a captured tree (3068 entries, doc at line 1332):
all three filters MATCHED it — at positions 89, 22 and 74 — and my own `head -20`
/ `head -20` / `head` discarded it every time, one by **two lines**. I then
reported a fact about my pipe as a fact about the repository. Lesson recorded as
`ATOM-EWPM-VQ25` on the debugging-methodology page: **a self-chosen `head` never
looks truncated — it looks like the answer**; an absence claim needs `wc -l` plus a
positive control before it leaves the session.

**Disclosure recorded in the ruling:** I reached this position independently ~4h
earlier for this plugin, before the routing note — corroboration or bias, but not
fresh analysis of the COS's evidence. What the COS added was four measured failures.

**Verification gap, stated:** `design/proposals/` on the orchestrator repo's main
branch does not list TRDD-NSWPM93D (commit `9c1c7b8` appears local/unpushed), so the
ruling rests on the routing note, not the canonical record. Both cited `ai-maestro#76`
comments were verified to exist (5219694921, 5220208974).

## Approval log

## Wait state (2026-08-19, TRDD-QX6VFAXS hygiene)

Awaiting a USER-tier hub decision: ai-maestro#143 — R42.3's "ONLY channel" clause is USER-tier; only the USER may correct it. Per hub Q3 ruling a USER-decision wait is `human_review` (blocked-by holds TRDD ids only). Resume in `dev` on the ruling.
