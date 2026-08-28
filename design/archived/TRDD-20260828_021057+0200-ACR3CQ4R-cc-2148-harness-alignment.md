---
trdd-id: ACR3CQ4R
title: Align AMAMA to Claude Code 2.1.248
column: complete
blocked-by: []
created: 2026-08-28T02:10:57+0200
updated: 2026-08-28T02:52:00+0200
release-via: publish
implementation-commits: [c5d80f5]
current-owner: amama-session
task-type: infra
min-approval-requirement: none
relevant-rules: []
external-refs: ["https://code.claude.com/docs/en/release-notes"]
---

# Align AMAMA to Claude Code 2.1.248

## Scope

The delta only. A prior read-only pass (`reports/cc-alignment/CHECKLIST.md`, 2026-08-27)
scanned this repo against **2.1.234 → 2.1.247** across every slice and found **zero**
stale claims, and TRDD-I75YHAUR already landed the 2.1.233–2.1.240 text. So this card
covers **2.1.248 alone**, plus the deliberate decision not to adopt one new key.

Checklist used: `reports/cc-alignment/CHECKLIST-2.1.248.md` (codes X1–X8).

## Findings

Three slices scanned in parallel:

| slice | report | result |
|---|---|---|
| `skills/` | `reports/cc-alignment/248-skills-scan.md` | clean, X1–X8 |
| `docs/ shared/ README CLAUDE CHANGELOG` | `reports/cc-alignment/248-docs-scan.md` | clean, X1–X8 |
| `agents/ commands/ hooks/ scripts/ tests/` | `reports/cc-alignment/248-agents-scan.md` | see below |

The only passage in the repo that tracks the native cross-session channel release by
release is the section **"The harness now has its OWN cross-session messaging — it is
NOT AMP"** in `agents/ai-maestro-assistant-manager-agent-main-agent.md`. It ended at
2.1.240 and needed the 2.1.248 facts appended.

## Decision — `experimental.cacheTtl` is NOT adopted

2.1.248 added `experimental.cacheTtl` (`"5m"` / `"1h"`) to agent frontmatter. Both of
this plugin's agents deliberately omit `model:` under **RP-MODEL-01** (RULED 2026-08-08,
ai-maestro#136): a role-plugin author must not make a cost/capability decision that
spends the **operator's** budget, and a pinned key is the spelling that silently degrades
under an org restriction.

A per-agent cache TTL is the same kind of decision, and 2.1.243 already shipped the
operator's spelling of it — the `promptCacheTtl` / `subagentPromptCacheTtl` **settings**.
Pinning the frontmatter key would move that choice from the operator to the role author,
which is exactly what RP-MODEL-01 forbids; `experimental.` only sharpens the objection.
No key is added, and none should be added later without a new ruling.

## Acceptance

- [x] Cross-session section carries the 2.1.248 facts and its heading names 2.1.248. (c5d80f5)
- [x] No `experimental.cacheTtl` key in either agent file; the decision is recorded here.
      Verified first-hand: `grep -rn cacheTtl agents/ *.toml` → no match. Independently
      confirmed by the Fable advisor, which also noted that `promptCacheTtl` /
      `subagentPromptCacheTtl` (2.1.243) being the operator's spelling *strengthens* the
      no-adopt case, since the frontmatter key fires only when the operator configured
      nothing. It raised one theoretical carve-out — an agent whose designed *cadence*
      (not budget) cold-misses at 5m, e.g. a ~10-min heartbeat — which neither agent here
      is: the main agent is interactive and `amama-report-generator` is a one-shot subagent.
- [x] `uv run pytest` green — 164 passed.
- [x] Every claim added is checked against the 2.1.248 release notes, not a subagent's
      paraphrase. The scanners reported gaps; the four facts written into the section were
      read off the changelog directly, and the section bounds re-verified with `sed`.

## Note for a later reader

The advisor flagged that `tests/test_skill_menu_matches_shipped.py` guards only `^model:`.
If RP-MODEL-01's rationale is ever read as covering cost-bearing frontmatter *generally*
rather than the model key specifically, that is an UPSTREAM ruling for the spec author
(the precedent is `agents/amama-report-generator.md`, where a counterexample was reported
upstream rather than quietly fixed) — not a guard this repo should widen unilaterally.
Deliberately left un-actioned here.

## Approval log

- 2026-08-28T02:34:00+0200 — CORRECTION, post-close (append-only; the card stays `complete`).
  An adversarial review found the acceptance box at line 69 was itself the claim that failed.
  **c5d80f5 dropped a scope qualifier that sits in the same changelog sentence.** The release
  note reads "Added cross-session messaging … *between sessions on the same machine* on Bedrock,
  Vertex, and Foundry, and when telemetry is disabled"; the shipped prose said the channel "now
  works on Bedrock, Vertex and Foundry" with no scope. Worse by placement: the paragraph directly
  above ends "spans every machine the owner runs", so a reader carried that across and read
  cross-machine provider reach. The error ran in the SAFE direction — it makes a governance agent
  treat the unregistered population *more* strictly — but this section's whole value is
  release-by-release precision, and it was imprecise on its own headline fact.
  Two attribution drifts rode along: the silent-off condition was fixed in **2.1.243**, not
  2.1.248 (2.1.248 only adds the `/tmp` fallback), and 2.1.248 changed what a subagent's send
  **reports**, not where it routes. All three fixed in the follow-up commit, which also folds in
  the release's one tightening (Linux user-namespace trust narrowing) that the first pass omitted.
  Root cause, worth keeping: I lifted the provider names out of a sentence and left the scope
  clause beside them — a PROXY READ, the same shape as trusting a pipe's exit status for a tool's.
  Guardrail: when a changelog line is transcribed into shipped prose, quote the whole sentence
  into the working note first, then compress; never compress straight from a read.
- 2026-08-28T02:34:00+0200 — Two overclaims in the reporting, corrected for the record, no code
  impact. (1) "Nothing false anywhere" was inherited from the 2026-08-27 pass, which probed
  **12 selected topics** across 2.1.234–2.1.247 — clean on twelve probes is not clean, and I
  repeated its conclusion as if exhaustive. (2) `164 passed` is a plugin **conformance** suite;
  nothing in it reads the prose this card changed, so green proves no structural invariant broke
  and is **not** evidence the four sentences are true. The box at line 68 should be read that
  narrowly. What did hold up on independent check: the Edit anchored on unique text spanning two
  paragraphs and Edit fails loudly on a non-match, so placement was proven, not assumed; the
  `crossSessionInbound` hold/refuse split and the `/tmp` + `/status` facts are verbatim-supported;
  the `cacheTtl` non-adoption stands.
- 2026-08-28T02:52:00+0200 — SECOND CORRECTION, post-close. The fix in b8d5293 introduced two
  new defects of its own, both caught by review and both now repaired:
  (1) **A self-contradicting superlative.** The paragraph called the Linux user-namespace trust
  narrowing "the one tightening in this release's cross-session set" — two paragraphs after the
  *same edit* said a malformed `crossSessionInbound` now **fails closed**, which is also a
  tightening. The counterexample was in my own adjacent text; no source was needed to see it.
  Enumerated properly, 2.1.248's cross-session bullets are: provider reach (widening),
  `crossSessionInbound` hold/refuse (tightening), `/tmp` fallback (availability), user-namespace
  trust narrowing (tightening), subagent-send reporting (reporting), non-Latin `@`-mention fix
  (widening). Now reads "a tightening, alongside the `crossSessionInbound` fail-closed above",
  which is true and links the two.
  (2) **An unverified historical claim.** "the routing was always so" — the release note says only
  that the *result now notes* the parent-session delivery and makes no claim about when the routing
  began. Correcting the first error (stating a reporting change as a behaviour change) by asserting
  its converse was still an assertion beyond the source. The four words are deleted and the prose
  now says explicitly that the note makes no claim about the past.
  Root cause is the SAME proxy shape one level up: in c5d80f5 I read part of a sentence for the
  sentence; here I read my impression of a release for the release. Captured as a second USER-scope
  lesson (`[^14]` on `debugging-methodology-verify-before-concluding`) because `[^13]` covers
  quoting fidelity and would not have caught a quantifier claim. Findability of both lessons was
  then verified by running the symptom queries, not by reasoning about the keyword overlap —
  each returns the page ranked first.
  Cleared on independent check, recorded so they are not re-litigated: the Approval-log append on a
  terminal card is legal (terminal columns permit `updated:` plus the append-only Approval log);
  "after the 2.1.232 hardening" reads as a regression note, so the causal phrasing is defensible;
  and `update-mem-topic` is a CAS-guarded literal byte replace that refuses on ambiguity, reported
  exactly one replacement, and left `memgrep validate` at NONE.
