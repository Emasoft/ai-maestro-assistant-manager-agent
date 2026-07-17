---
trdd-id: QMY8VR0D
title: A manager is a guide not a gate — refusal protocol in persona, tool, memory, and fleet
column: dev
created: 2026-07-16T13:46:05+0200
updated: 2026-07-17T12:20:33+0200
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
- **✅ ADOPTION COMPLETE (2026-07-17) — supersedes the 07-16 status below. ONLY USER RATIFICATION REMAINS.**
  - **hub#71 R49 — CODIFIED + PUSHED + VERIFIED.** Landed on the remote with the governance-rules
    push (`dcbfabca`, `GOVERNANCE-RULES.md` v4.5.0). I read all six sub-clauses on `?ref=governance-rules`
    and they are faithful to the USER mandate: R49.1 (defect+bar+invitation; a bare "no" is itself a
    defect), **R49.2 — MY proactive-alternatives refinement LANDED verbatim** ("the approver pushes
    toward an alternative route"; "a verdict correct on the merits but ending with the need abandoned
    is a *failed* refusal"), R49.3 (from-DRAFT corollary — CORE's pin), **R49.4 (the MESSAGE is the
    channel; the tool is the paperwork — the USER's messages-first mandate verbatim; GitHub-issue-as-
    channel where no AMP thread exists)**, R49.5 (iterate; **binds MANAGER at Tier 2** — no author
    exemption), R49.6 (defect recorded where the proposer will act on it).
  - **ORCH#30 — SHIPPED + VERIFIED** in v1.9.5 (tag live on remote 16:22Z). Persona section +
    `amoa_reassign_module.py --reason` guardrail. Its reciprocal improvements (the guardrail + the
    "RECORDED, NOT DELIVERED" degradation) were folded back into AMAMA (`28d1bd7`).
  - **COS#28 — LANDED** (`5daeca4`, 16 guards, 211 tests green; committed local, bundles with #42).
    Approver half + **relay half** (refusals relay with defect/bar/invitation intact; counter-arguments
    flow back UP — "both directions, or the gateway is a wall"). **COS added a duty on the MANAGER and
    I APPROVED it: a decision reaching COS without the four elements gets BOUNCED BACK to me** rather
    than relayed bare or with invented reasoning — R49.5 binds me, and a protocol whose enforcement
    stops at its author is decoration. COS also **REFUSED my guardrail ask** by reading its code and
    disproving its own claim (`amcos_approval_manager.py:1121` already has `respond --comment
    required=True`; it never had AMAMA's content-free-default hole) and cited my own canonical lesson
    `[^3]` back at me (route the rule to the surface where the behavior happens; tools enforce only the
    mechanical residue). **Accepted** — its cross-surface guard (a test pinning `--comment
    required=True`) is better than what I asked for.
  - **FLEET LESSON (COS, worth carrying):** grep UNDER-REPORTS on a reasonless-"no" audit — the arg is
    often not named `reason` (COS's is `--comment`). Read the surface; don't pattern-match it.
  - **REMAINING: USER ratification of R49 only.** Do NOT fabricate it. If ratification alters the text,
    tell COS to re-align before publish (it is unpublished, so that is safe).
- **ADOPTION STATUS (2026-07-16) — historical, superseded by the block above:**
  - **hub ai-maestro#71 — CODIFIED as R49 + MANAGER-REVIEWED (biggest step).** The hub landed
    the refusal protocol as governance rule **R49** (R49.1–R49.6: guide-not-gate + concrete
    defect/bar/invitation; R49.3 from-DRAFT corollary; R49.4/R49.6 GitHub-issue-as-channel +
    record-vs-channel split; R49.5 iterate; framed as the refusal-half of R41). Both CORE pins +
    the USER messages-first addendum are in verbatim. Committed on worktree
    `worktree-agent-a4768518dc36ee151` (off governance-rules), **NOT pushed** — honest
    review-first process. I VERIFIED it is correctly absent from `?ref=governance-rules`
    (0 hits, tip still 71df9353) — consistent, not a discrepancy. **MANAGER review posted
    (hub#71 issuecomment-4994056329): endorsed as faithful + one refinement offered (make the
    approver's proactive-alternatives duty explicit, not just implicit in "refuse the impl not
    the need") + flagged that R49's push rides the SAME wall as the five 404 shas.** CORE
    confirmed the proposer-side clauses read correctly.
  - **AWAITING: USER ratification** (R49 is a USER-set IRON rule; CORE + I agree the chain is
    MANAGER-review → USER-ratify). Surface to USER with the review attached; do NOT fabricate.
  - **AWAITING: the push** — even once ratified, R49 cannot reach the fleet-read branch until
    the push-blocker (`claude-plugins-validation#169`) clears. R49 is now one more item gated
    on the hub's `git push origin governance-rules` stderr.
  - **ORCH#30 — ADOPTED** (acknowledged; RECORDED-NOT-DELIVERED degradation called "the right
    shape"). **COS#28 — pending** (COS Claude awake, not yet reached it).
- **NEXT ACTION:** (1) surface R49 to the USER for ratification with the hub#71 review; (2) once
  R49 lands on the remote, fold its citation into the AMAMA persona (cite R49 as canonical like
  the DEP overlay does, rather than restate); (3) drive COS#28 to adoption. Fold the ratified
  rule text into the #66-settled-parts propagation wave.
- **The incident (evidence):** plugin-Claude proposed commands → hub denied most on
  security grounds (CORRECTLY) → proposer began deleting dependent skills → USER caught it
  by chance, explained the defect → hardened, re-proposed, approved. A correct refusal and
  a destructive one are indistinguishable in the refuser's log — the duty attaches to
  every refusal.

## Notes

`relevant-rules: [1]` — PRRD G1.1 governs the three issue posts. Born-approved: a USER
mandate is approved the moment it is written (mandated-by: user).
