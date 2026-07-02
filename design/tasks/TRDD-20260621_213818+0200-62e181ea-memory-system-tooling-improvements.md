---
trdd-id: 62e181ea-20b1-4614-ad9f-0893117b4857
title: Memory-system tooling improvements — is-due CLI, marker due-gating, gate↔model tier, frontmatter placement
column: planned
created: 2026-06-21T21:38:18+0200
updated: 2026-07-02T06:15:00+0200
current-owner: amama
assignee: amama
priority: 3
severity: MEDIUM
effort: M
task-type: infra
approval-tier: 2
relevant-rules: []
release-via: none
review-requirements: [human-review]
impacts: []
external-refs: ["github.com/Emasoft/ai-maestro-janitor"]
---

# TRDD-62e181ea — Memory-system tooling improvements (proposals)

## ⏵ STATE — READ THIS FIRST — 2026-07-02

**✅ APPROVED + FILED 2026-07-02** (MANAGER, tier-2): P1-P4 routed as **ai-maestro-janitor#68**. Verify-before-file flagged P2/P4 may be superseded by CLOSED janitor #50/#56/#33 (maintainer to disregard if resolved); P1/P3 genuinely new; cross-reffed #45/#46/#47. AMAMA coordination complete → janitor executes; MANAGER verify-acks on release.

_(historical proposal STATE — 2026-06-21)_

Improvement PROPOSALS for the janitor wikimem system, distilled from lessons hit
THIS session (the MAESTRO asked, 2026-06-21: "create TRDDs with all the proposals
for improvements ... based on your experience and lessons learned"). All are
CROSS-PROJECT — the janitor owns the memory tooling — so on approval each becomes a
Method-1 issue on `ai-maestro-janitor`. NONE re-files the already-open janitor
memory issues (see "Already filed"); they cross-ref.

## P1 — `is-due` / `mark-ran` CLI verbs (the "is-due idea")

**Lesson/experience:** a `[janitor-memory-*]` heartbeat marker is a round-robin
nudge, not a due-guarantee ([[janitor-memory-marker-is-due-gated]]). The skills say
"check `memory_settings.is_due(...)` first, `mark_ran(...)` after," but the only
surface is the Python lib — and `memory_settings_cli.py` exposes ONLY `get`/`set`.
This session, on a `[janitor-memory-repair]` marker, I could not check is-due
cheaply: a direct lib import failed (`LIB_IMPORT_FAILED` — the package layout isn't
import-friendly from an agent shell), so I fell back to a content scan that itself
produced a FALSE POSITIVE (see P4).

**Proposal:** add two verbs to `memory_settings_cli.py`:
- `is-due <pass> <scope>` → prints `due`/`not-due`, exit 0 = due.
- `mark-ran <pass> <scope>` → records the cadence stamp.

Then every memory pass self-gates + records via a stable, frozen CLI — not a
fragile lib import. **Owner:** janitor.

## P2 — Scheduler emits a memory marker ONLY when that pass is actually due

**Lesson/experience:** same root as P1 — the heartbeat round-robins the 5 memory
markers, so a marker can fire for a pass whose specific cadence has NOT elapsed; the
agent then loads the skill + scans only to bail (wasted turn).

**Proposal:** in `dispatch.py`, cross-check `is_due(pass, scope)` (via P1's verb)
BEFORE emitting a `[janitor-memory-*]` marker; emit nothing if nothing is due. Turns
the marker from "maybe due" into "is due," eliminating the wasted-turn class.
**Owner:** janitor. Depends on P1.

## P3 — Reconcile the `verify_repair` gate with the wikimem model on `tier`

**Lesson/experience:** the model says "no `tier` ⇒ component (valid); existing flat
notes stay valid." But the repair gate's `_REQUIRED_FM_KEYS` REQUIRES `tier`, so
repairing a valid tier-less page FAILS (`verify FAILED ... missing required key(s):
tier` — proven by a pilot txn this session). 22/28 of my LOCAL pages are validly
tier-less, so the gate would reject a minimal repair of any of them.

**Proposal:** make them consistent — EITHER (a) the gate treats absent `tier` as
`component` (matching the model), OR (b) the repair skill's default path auto-adds
`tier: component` when it backfills, so a tier-less page CAN be minimally repaired.
Today neither holds (the skill backfills ocd/lmd, but the gate also demands tier).
**Owner:** janitor.

## P4 — Standardize + document frontmatter key placement (top-level vs `metadata:`)

**Lesson/experience:** a naive `grep '^ocd:'` reported 9 pages "missing ocd/lmd" — a
FALSE POSITIVE: the harness `# Memory` directive wrote them NESTED under `metadata:`,
and `parse_frontmatter()` hoists metadata sub-keys to top level, so the gate sees
them but a top-level grep doesn't. The authoring directive, memgrep, and the gate
don't visibly agree on WHERE `ocd`/`lmd`/`tier` live.

**Proposal:** document the canonical placement (recommend `ocd`/`lmd`/`tier` as
TOP-LEVEL keys, matching the `janitor-memory-write` examples + how memgrep documents
them) and make the harness `# Memory` authoring directive emit that shape — so
scans/tooling are consistent and false-positive-proof. **Owner:** janitor (+ the
harness `# Memory` directive). Sibling: [[verify-before-fixing-non-bugs]] (the scan
was a measurement artifact, like the tee/SIGPIPE + pgrep-self-match traps).

## Already filed (cross-ref — do NOT re-file) — [[memory-system-ux-issues-filed]]

- **janitor#45** — auto-recall off by default.
- **janitor#46** — `metadata.type` ignored by recall ranking.
- **janitor#47** — no `memgrep lint` for malformed pages (P3/P4 would feed it).

## Routing

On MAESTRO review, file P1-P4 as one or more issues on `ai-maestro-janitor`
(Method-1; cross-ref #45/#46/#47). Natural order: P1 → P2 → (P3, P4).

## Notes and lessons learned

(none yet)
