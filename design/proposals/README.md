# design/proposals/ — TRDDs awaiting approval

This folder holds TRDDs with **`column: proposal`** — tasks that have
been **authored** but **not yet authorized to execute**. They are
requests, not commitments.

The canonical procedure lives in
`~/.claude/rules/trdd-approval-tiers.md` Part A (Creation procedure,
Promotion protocol, Refusal protocol, Batch approval syntax). This
README is the local quick-reference.

## What lives here

- `TRDD-*.md` with `column: proposal` — pending a decision.
- `refused/` — refused proposals, archived (per RULE 0, **never
  deleted**) with `column: refused`. Not part of the pending index.
- `README.md` — this file.

Everything directly in this folder (excluding `refused/`) is, by
invariant, *pending approval*. The moment a proposal is decided it
`git mv`s OUT — approved → `design/tasks/`, refused → `refused/` — so
this folder stays an accurate live index of "awaiting a decision".

**The design/ zones (all moves, never deletes — RULE 0):**

| Zone | `column:` values | Meaning |
|---|---|---|
| `design/proposals/` | `proposal` | pending a decision |
| `design/tasks/` | `planned`…`dev`/`testing`/`blocked`/**`failed`** | **OPEN work** (an OPEN TRDD = one living here) |
| `design/refused/` | `refused` | proposal rejected |
| `design/archived/` | `completed` · `cancelled` · `superseded` | terminal-DONE (finished / withdrawn / replaced) |

**`failed` stays OPEN** in `design/tasks/` — it is retryable, never
archived. Giving up on a failed TRDD is an explicit *cancel*
(`failed` → `cancelled` → `design/archived/`).

## Frontmatter a proposal must carry

Standard v2 TRDD frontmatter, plus:

- `column: proposal`
- **`approval-tier: N`** — the tier (0/1/2/3) this proposal needs, per
  Part B of the rule. Tier-0 work is **never** staged here — it is
  authored directly in `design/tasks/` as `column: planned` (DERIVED
  TASKS / NPT / EHT / in-own-scope work). Proposals are Tier 1/2/3.

## Deciding proposals — the fast path

Use the **`amama-proposal-approvals`** skill (MANAGER plugin):

1. **List:** "list proposals" → a numbered, one-line-each table
   (number · 8-char id · tier · title), with a manifest pinning each
   number to a stable `trdd-id`.
2. **Decide** by replying with either form:
   - `approved: 4,6,22,14,2` — approve exactly those; **every unlisted
     proposal stays PENDING** (omission never refuses).
   - `refused: 48,7,8,5` — refuse exactly those **and approve every
     other** proposal in the listing (bulk path for when approvals
     outnumber refusals).
   - Both lines together — explicit dual lists; the rest stay PENDING.

On approval the skill sets `column: planned`, logs the decision in the
TRDD's `## Approval log`, and `git mv`s it into `design/tasks/`. On
refusal it sets `column: refused`, logs the reason, and `git mv`s it
into `refused/`.

## Who may approve

Per the proposal's `approval-tier:` (Part B of the rule):

| Tier | Approver |
|---|---|
| 1 | CHIEF-OF-STAFF (routes via COS) |
| 2 | MANAGER |
| 3 | USER |

(Tier 0 = agent-independent — not staged here at all.) When operating
solo, the human USER is the manager and may approve any tier.
