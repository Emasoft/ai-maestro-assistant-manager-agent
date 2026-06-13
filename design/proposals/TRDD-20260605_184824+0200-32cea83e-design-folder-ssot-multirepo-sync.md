---
trdd-id: 32cea83e-a180-44d7-8e71-e46ff1b380de
title: design/ as SSOT — permanent sync + perfect mirror across all repos of a project
column: proposal
created: 2026-06-05T18:48:24+0200
updated: 2026-06-10T04:48:45+0200
current-owner: amama
assignee: amama
priority: 2
severity: HIGH
effort: XL
labels: [governance, design-sync, multi-repo, architecture]
task-type: infra
approval-tier: 3
parent-trdd: TRDD-8793afa6
relevant-rules: []
release-via: none
impacts: [ci-pipeline, config-schema]
review-requirements: [human-review]
runtime-targets: [macos, linux]
external-refs: []
---

# TRDD-32cea83e — design/ as SSOT + perfect multi-repo mirror + permanent sync

## ⏵ STATE — READ THIS FIRST (authoritative)

- **What:** make every project's `design/` folder a **single source of
  truth on GitHub**, kept **permanently synced** after every change, and
  **mirrored byte-identically across ALL GitHub repos of the project**
  (a project may have N repos — frontend, backend, docs, … — each cloned
  independently, each needing the full `design/` context).
- **Status:** PROPOSAL awaiting USER decision (Tier 3 — architectural,
  cross-project, governance, touches CI + a possible ruleset exception).
- **Foundation already built (MANAGER plugin, this session):** the
  proposal-approvals tool (`scripts/amama_proposal_approvals.py` +
  `amama-proposal-approvals` skill), the 4-zone folder model
  (`design/proposals|tasks|refused|archived`), the OPEN-TRDD definition,
  the canonical lifecycle ASCII diagram, and `project-id` + canonical
  TRDD citation — all in `~/.claude/rules/trdd-approval-tiers.md`.
- **NEXT ACTION:** USER picks (1) the write-sync lane and (2) the mirror
  mechanism from `## Decisions needed`. Then MANAGER builds the
  MANAGER-local reference pieces and files per-plugin issues for the
  cross-project rollout.

## Problem

`design/` (PRRD, TRDDs across proposals/tasks/refused/archived) is
git-tracked. The GitHub copy must be the SSOT. But:

1. **Multi-repo projects.** One logical project = N GitHub repos. Every
   repo must carry an **identical** `design/` so any clone has the full
   picture. Repo URL is therefore NOT a project key — `project-id` is.
2. **Drift risk.** Agents clone, edit `design/` (create a TRDD, the
   orchestrator assigns via kanban, COS/MANAGER approve/refuse/archive,
   the integrator merges a PR) and may forget to push — the SSOT and the
   other repos go stale.
3. **No cross-repo atomicity.** You cannot atomically commit+push to N
   GitHub repos. "Perfect mirror at all times" is therefore an
   *eventual-consistency* goal: single-writer + near-real-time fan-out +
   reconciliation, with a small bounded lag — NOT a distributed
   transaction. (Stated honestly; do not claim true simultaneity.)

## The model

### Project registry (keyed by `project-id`)

Recorded in the PRRD frontmatter and/or the AI Maestro server:

```yaml
project-id: <stable-uuid-or-slug>     # repo-independent
repos:                                # all member repos
  - { url: github.com/Emasoft/foo-frontend, design-primary: true }
  - { url: github.com/Emasoft/foo-backend }
  - { url: github.com/Emasoft/foo-docs }
```

Exactly ONE member repo is the **design-primary** = the write target +
SSOT. The others are **mirrors** (read-only for `design/`: agents never
edit a mirror's `design/` directly — they write via the primary lane).

### Single-writer rule (prevents split-brain)

ALL `design/` writes target the **design-primary**. Because there is
exactly one write target, mirrors can never diverge by independent
edits — they only ever receive the primary's tree. This is what makes a
"perfect mirror" achievable without N-way merge.

### Write-sync lane (primary ← agent change) — DECISION 1

How a `design/`-only change reaches the primary's `main` (which is
PR-gated by the baseline ruleset):

- **1A — admin/owner direct-push** for `design/`-only diffs. MANAGER/COS
  (and the solo USER) are admin → instant. Simplest; team agents still
  need 1B.
- **1B — `design/`-only fast-merge lane** *(recommended)*: agent pushes a
  `design/`-only branch; a CI check asserts the diff touches only
  `design/**` and auto-merges to `main`. Respects PR-gating, zero human
  latency.
- **1C — sync daemon (single writer)**: one privileged process
  serializes pull→apply→push; needs a path-scoped ruleset exception
  (Tier-2 baseline deviation).

### Mirror fan-out (primary → all mirrors) — DECISION 2

How the primary's `design/` is replicated to every mirror:

- **2A — GitHub Action fan-out** *(recommended)*: on push to the
  primary's `main` touching `design/**`, an Action force-syncs the exact
  `design/` tree into every mirror repo's `main` (token with write
  access to mirrors; commit tagged `[design-mirror]`; mirrors do NOT
  re-fan-out → no loops). GitHub-native, no daemon, converges in
  seconds.
- **2B — `design/` as a git submodule** pointing to ONE shared design
  repo. Content is literally one repo → always byte-identical (strongest
  guarantee). Cost: submodule operational overhead (`--recursive`
  clones, `submodule update`), and a per-repo pointer-bump commit on
  every change.
- **2C — daemon mirror push**: the same single writer that lands on the
  primary also pushes the tree to each mirror in the same serialized
  pass.

### Reconciliation backstop (all options)

The **ai-maestro-janitor** periodically diffs each mirror's `design/`
tree-hash against the primary's; on drift (missed Action, failed push,
race) it re-syncs. This is what upgrades "eventual" to "reliably
eventually perfect". Also catches the "agent forgot to push" case:
local-only `design/` commits older than N minutes are surfaced/pushed.

### Read freshness (pull-before-act)

Before any agent reads `design/` to decide (orchestrator picks next
TRDD; COS/MANAGER review proposals; an agent checks its assignments), it
pulls its repo's `design/` (a mirror, kept current). A staleness guard
(`design/` tree-hash vs `origin`) fails-fast if behind.

### Triggers (where sync fires)

| Trigger | Role | Action |
|---|---|---|
| create TRDD (proposal/planned) | any agent | write via lane → primary; fan-out |
| kanban assign (assignee/column) | ORCHESTRATOR | write via lane → primary; fan-out |
| approve / refuse / archive / cancel | MANAGER / COS | write via lane → primary; fan-out |
| PR merged | INTEGRATOR | merge to primary IS a write; fan-out; broadcast pull |
| before reading design/ to decide | any agent | pull + staleness guard |
| periodic | janitor | reconcile mirrors ↔ primary; push local-only commits |

### Conflict model

Per-file TRDDs + flow-style frontmatter → edits to *different* TRDDs
never conflict. The single-writer primary serializes writes; the
fast-merge lane / daemon rebases a `design/` change onto fresh `main`
and retries (per the github-timeouts retry pattern). Same-file races
resolve SSOT-wins + re-apply (column field + append-only Approval log
make this mechanical).

## Deliverables (once decisions made)

**Shared-plugin rule (USER, 2026-06-05):** `ai-maestro-plugin` (from the
ai-maestro-plugins marketplace) is local-scope-installed in EVERY agent —
no agent exists without it. So **every script useful to all agents lives
in `ai-maestro-plugin/scripts/prrd-trdd/`** (alongside the existing
`findtrdd.py`, `get-prrd.py`, `prrd-edit.py`, `findprrd.py`, `kanban.py`),
**each with a `--help` screen AND a skill** explaining its use. The
MANAGER plugin keeps only MANAGER-role-specific thin skills that invoke
the shared scripts.

**Cross-project method (USER, 2026-06-05):** per the
don't-edit-other-projects' repos rule, every `ai-maestro-plugin` change
is requested by **filing a detailed GitHub ISSUE** on the
`ai-maestro-plugin` repo (Method 1 — preferred), **never** a direct edit
of the local clone and **never** a drive-by PR. The issue MUST be fully
self-contained — the receiving developer shares none of our context — so
it embeds: the exact script specs (querytrdd / decidetrdd / design_sync /
findtrdd `--project`), the `--help` requirement, the per-script skill
specs, AND the MANDATORY skill-authoring requirements below (tamper
verification + long timeout). The MANAGER prototype
(`amama_proposal_approvals.py` + its tests) is linked from the issue as
the working reference implementation.

1. Canonical spec `~/.claude/rules/design-folder-sync.md` (auto-loads
   ecosystem-wide).
2. **Relocate the prototyped proposal-approvals tooling** (built this
   session in the MANAGER plugin as `amama_proposal_approvals.py`) into
   shared, un-branded `ai-maestro-plugin/scripts/prrd-trdd/` scripts —
   each with `--help` + a skill:
   - `querytrdd.py` — READ side: list pending proposals (+manifest),
     list OPEN TRDDs (incl. blocked/failed/unparsed), `--project` scope.
   - `decidetrdd.py` — WRITE side: approve / refuse / archive / cancel
     (approver-only; the skill documents the tier authority).
   - `design_sync.py` — pull / push-via-lane / status / reconcile / mirror.
   The MANAGER plugin's `amama-proposal-approvals` skill becomes a thin
   pointer to the shared scripts; the prototype script + test move to
   `scripts_dev/` (RULE 0 — moved, not deleted) once the shared version
   lands.
3. The mirror-fan-out GitHub Action (template) + the `design/`-only
   fast-merge CI check (template) — shipped in `ai-maestro-plugin` and
   applied per design-primary repo.
4. `project-id` + `repos[]` + `design-primary` fields in the PRRD schema
   (`prrd-design-rules.md`) and the AI Maestro registry.
5. `findtrdd --project <project-id>` — extend the existing shared
   `ai-maestro-plugin/scripts/prrd-trdd/findtrdd.py` (cross-project →
   ai-maestro-plugin issue).
6. Per-plugin issues (orchestrator/COS/architect/integrator/programmer/
   autonomous/maintainer) wiring pull-before-act + write-via-lane at
   each role's triggers, + the lifecycle diagram in every main-agent +
   README.
7. janitor reconciliation detector (cross-project → janitor issue).
8. **TRDD approval watchdog** (rule Part D) — a lazy, idle-time auditor
   (janitor cadence / MANAGER idle sweep, NEVER per-creation) that computes
   each TRDD's objective tier-floor from its content + proposed diff,
   compares it to the declared `approval-tier:`, and auto-corrects clear
   under-classification (raise tier + move `design/tasks/`→`design/proposals/`
   to un-authorize) or queues ambiguous cases for the MANAGER. The
   floor-computation logic ships in shared `ai-maestro-plugin/scripts/prrd-trdd/`
   (e.g. a `trdd_classify.py` + a `decidetrdd.py audit` mode); the periodic
   driver is a janitor detector. Cross-project → ai-maestro-plugin + janitor
   issues. This is what makes self-classification (fast) safe against
   under-classification gaming.
9. **Emergency enforcement mode** (rule Part D6) — MANAGER-declared
   temporary rules (`design/requirements/emergency-rules.yaml` + server
   registry) that RAISE the required approval for a matched category
   (security threat / CVE / deprecated API) immediately + proactively,
   `no-self-approve`, until lifted. Two-stage token discipline: a
   **zero-LLM script pre-filter** (path-glob / keyword / dep `match`
   predicates) narrows the corpus to the few suspects; the LLM confirm
   runs only on those. Carries `expires:` (auto-lift) + MANAGER idle-sweep
   reminder so a forgotten emergency can't drain tokens. Ships with the
   watchdog (deliverable 8) in shared `ai-maestro-plugin` + janitor.

### Skill-authoring requirements (shared scripts) — USER, 2026-06-05

Every skill that documents a shared `ai-maestro-plugin` script MUST
instruct the agent to:

1. **Verify the script against malicious injection BEFORE running it.**
   Shared scripts run in every agent and (for `decidetrdd` / `design_sync`)
   push to GitHub with credentials — a tampered copy is a token-leak and
   repo-corruption risk for every repo's `design/`. The skill instructs the agent to:
   - run ONLY the canonical copy under
     `$CLAUDE_PLUGIN_ROOT/scripts/prrd-trdd/` (never an untrusted copy in
     the working tree or a path passed by another agent);
   - verify the file's integrity — SHA-256 against the pinned manifest the
     plugin ships — and **refuse + alert** on mismatch;
   - quickly scan the script for injection / exfiltration patterns
     (unexpected network egress, `eval`/`exec` of dynamic strings, base64
     blobs, credential/env reads) before executing it.
2. **Use a much longer Bash timeout** (≥ 20 min / 1,200,000 ms) — the
   sync / mirror / reconcile and multi-repo git operations are slow and
   retry on transient GitHub failures (per the github-timeouts rule).

Both are MANDATORY in every shared-script skill (querytrdd, decidetrdd,
design_sync, findtrdd, …). (Implies a shipped integrity manifest — e.g.
`ai-maestro-plugin/scripts/prrd-trdd/SHA256SUMS` — as part of deliverable 2.)

## Verification status (USER directive: facts + tests, never assume)

The write-lane (1A/1B/1C) and mirror (2A/2B/2C) choices here are **unverified
hypotheses** — GitHub's real behavior (can a `design/`-only PR auto-merge into
a `baseline-*`-protected `main`? does the Action fan-out replicate loop-safely?)
MUST be confirmed by a **sandbox test** before the decision is committed. The
full facts-vs-assumptions table + the per-hypothesis test plan lives in
`TRDD-30ebf367` ("Verification status"). VERIFIED so far: the mkdir
cross-process lock is real but **same-host only** (cross-host lease ⇒ server),
and the Python design-tooling write is non-atomic (a real bug to fix).

## Decisions needed (USER)

- **DECISION 1 (write lane):** 1A admin-direct / **1B fast-merge
  (recommended)** / 1C daemon.
- **DECISION 2 (mirror):** **2A Action fan-out (recommended)** / 2B
  submodule / 2C daemon.
- **Project-id source of truth:** PRRD frontmatter, AI Maestro server,
  or both (registry in server, mirrored to PRRD)?
- **Atomicity expectation:** confirm "eventual (seconds) + reconciliation
  backstop" is acceptable (true N-repo atomicity is impossible).

## Approval log

- 2026-06-05T18:48:24+0200 — Authored as a PROPOSAL (Tier 3) by amama,
  capturing the design/ SSOT + multi-repo mirror + permanent-sync design
  from the USER's 2026-06-05 design conversation. Awaiting USER decisions.
