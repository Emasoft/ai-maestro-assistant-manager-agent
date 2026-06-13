---
trdd-id: 30ebf367-54a3-4b06-b133-8e28b3a0a07c
title: Multi-agent conflict prevention — domain ownership + concurrency rails for design/ and code
column: proposal
created: 2026-06-05T23:36:01+0200
updated: 2026-06-05T23:36:01+0200
current-owner: amama
assignee: amama
priority: 1
severity: HIGH
effort: XL
labels: [governance, concurrency, architecture, security, ownership]
task-type: infra
approval-tier: 3
parent-trdd: TRDD-32cea83e
relevant-rules: []
release-via: none
impacts: [config-schema, ci-pipeline, public-api]
review-requirements: [human-review]
runtime-targets: [macos, linux]
external-refs:
  - reports/design-concurrency/20260605_233152+0200-role-github-ownership.md
  - reports/design-concurrency/20260605_233231+0200-concurrency-primitives.md
---

# TRDD-30ebf367 — Multi-agent conflict prevention: domain ownership + concurrency rails

## ⏵ STATE — READ THIS FIRST (authoritative)

- **What:** prevent two agents from making **conflicting (opposite) edits to
  the same file** — in `design/` AND in code — when their PRs merge. The
  orchestrator guarantees the MAIN tasks it assigns are orthogonal, but it
  **cannot** orthogonalize the **derived tasks** (NPT/EHT) each agent spawns,
  so derived-task PRs can collide. USER-delegated deep analysis.
- **Status:** PROPOSAL awaiting USER decision (Tier 3 — architecture, security,
  cross-project, all role plugins + server).
- **Core decision:** the primary rail is **single-writer-per-DOMAIN** (the
  USER's instinct, confirmed best): partition every mutable surface into
  domains with exactly one owner; a derived task that needs to touch a domain
  it does NOT own must **delegate to the owner or take a claim**, never edit it
  directly. Safety nets (lease/claim, optimistic versioning, merge-queue+path-
  overlap, atomic writes) catch the residual.
- **Evidence base (read before acting):**
  - `reports/design-concurrency/20260605_233152+0200-role-github-ownership.md`
    — role × GitHub-op map; resolves the orchestrator-vs-integrator ruleset
    question (MAINTAINER already owns ruleset config; INTEGRATOR's "branch
    protection" is a merge-gate vocabulary collision).
  - `reports/design-concurrency/20260605_233231+0200-concurrency-primitives.md`
    — existing primitives (in-proc mutex, mkdir cross-proc lock, governance
    state machine, IBCT scopes, worktree isolation, SSOT single-writer) and
    the 7 enforcement gaps (G1–G7).
- **NEXT ACTION:** USER picks from `## Decisions needed`. Then MANAGER builds
  the ownership-map + atomic-write fix (cheap core) and files the per-plugin +
  server issues (cross-project) for the rails.
- **Relation to `TRDD-32cea83e`:** the SSOT single-writer for `design/` is the
  *design-side instance* of this proposal's general ownership principle; this
  TRDD generalizes it to **code** + **resource domains** and adds the
  enforcement the SSOT rule currently lacks (gaps G6/G7).

## Problem & conflict taxonomy

| Class | Conflict | Today |
|---|---|---|
| **C1** | two agents edit the **same TRDD** file | per-file TRDDs + append-only log help; same-body prose can still conflict (G6) |
| **C2** | two agents edit **different TRDDs** | safe by construction (per-file) — no action |
| **C3** | two edits to the **same PRRD rule** | RBAC by role only; two managers race freely (G4); non-atomic write (G5) |
| **C4** | two PRs touch the **same code file** oppositely | worktree isolates until merge; then no merge-queue / overlap detection (G3/G7) |
| **C5** | two agents touch a **shared DOMAIN** (rulesets, CI, deps, schema) — maybe different files, semantically coupled | no per-domain owner; agents write "just-for-a-while" TRDDs → chaos (the USER's ruleset example) |

C5 is the dangerous one and the one the orchestrator cannot prevent — it is
the target of the primary rail.

## What already exists (don't reinvent — see the 2 reports)

- **Single-process** named mutex + **atomic-rename** writes (server TS
  registries). **Cross-process** mkdir-lock — but only on 2 files.
- **Governance** approve/reject/execute + TTL state machine (HTTP + lock +
  identity) — a ready shape to clone for a claim/lease registry.
- **IBCT per-operation scopes** + full auth/identity layer.
- **Worktree code isolation** (`isolation: worktree`) — conflicts surface only
  at merge.
- **SSOT single-writer-per-design-primary** (TRDD-32cea83e) — the design-side
  partition, decided.
- **Gaps (all ENFORCEMENT):** G1 no cross-agent lease; G2 no optimistic
  versioning; G3 no merge-queue/overlap; G4 advisory-only TRDD ownership; G5
  non-atomic Python design-tooling writes; G6 SSOT single-writer is rule not
  mechanism; G7 no code-side ownership/path-claim.

## Options evaluated (security + synchronization)

| Option | Prevents | Security | Sync | Verdict |
|---|---|---|---|---|
| **A. Domain ownership partition** (single-writer-per-domain) | C1,C3,C4,C5 by construction | **Best** — blast-radius limited; sensitive domains (rulesets/CI/creds) bound to trusted roles | Best — non-overlapping domains need no coordination | **PRIMARY** |
| **B. Claim/lease registry** (clone governance-registry + mkdir-lock + TTL) | C1,C3,C4 dynamically when A can't pre-assign | Good — must be auth'd (IBCT/identity) so claims can't be spoofed | Good — serializes same-resource edits cross-agent | **Net 1** |
| **C. Optimistic versioning** (expected-hash / compare-and-swap) | lost updates A/B miss | Neutral | Cheap, catches residual races | **Net 2** |
| **D. Merge queue + path-overlap detection** (INTEGRATOR) | C4/C7 at merge | Positive — flags unexpected edits to sensitive paths | Serializes merges; proactive overlap vs GitHub's reactive "up-to-date" | **Net 3** |
| **E. Atomic Python writes** (tmp+rename in `prrd_lib`) | C3/C5 local torn-write (G5) | Neutral | Closes pre-git torn-write window | **Foundation fix (do regardless)** |
| **F. Worktree isolation** | confines edits pre-merge | Positive | Already present | **Reuse** |
| **G. Append-only / per-file formats** | C1/C2 | Neutral | Already the design-side choice; extend | **Reuse/extend** |

No single option covers all classes → **defense-in-depth**, with **A as the
primary rail** and B–E as nets. (Per the no-over-engineering directive: A + E +
the delegation rule + a minimal B are the high-value core; C and D are phase-2.)

## Recommended solution

### R1 — The domain ownership map (PRIMARY rail)

A per-project **ownership map** (declared in the PRRD / `design/`, SSOT,
mirrored per TRDD-32cea83e) assigning every mutable surface to **exactly one
owner**. Two kinds of domain:

- **Path domains** (CODEOWNERS-style globs): `src/auth/** → agent-X`,
  `.github/** → MAINTAINER`, `design/** → design-primary writer`, etc.
- **Resource domains** (not file-shaped): GitHub ruleset config, releases/tags,
  dependency/lockfiles, DB schema/migrations, CI workflows, kanban columns.

**The derived-task rule (the crux that kills C5):** when an agent's derived
task needs to touch a domain it does **not** own, it MUST NOT edit it. It
either (a) authors a TRDD **assigned to the owner** (delegation), or (b) takes
a **claim** (R3) if the domain is claim-based. "Touch a ruleset just for a
while" becomes structurally impossible — that domain belongs to MAINTAINER.

### R2 — Role ownership resolutions (from the evidence)

- **GitHub repo CONFIG (rulesets, branch-protection config, CI hardening,
  supply-chain) → the repo's MAINTAINER.** It is the only role owning the
  Rulesets API SHOW/APPLY lifecycle + drift detection. Applying the ratified
  baseline as-is is Tier-0; any **deviation** is Tier-2 → MANAGER (unchanged).
- **Fix the vocabulary collision:** rename INTEGRATOR's "Branch Protection"
  responsibility to **"merge-gate enforcement"** (it enforces gates AT merge;
  it does NOT manage ruleset config). INTEGRATOR defers config to the repo's
  MAINTAINER.
- **PR merge + release = single-owner-per-repo:** classify each repo in the
  project registry as **team-project** (INTEGRATOR merges + cuts releases) OR
  **maintained** (MAINTAINER merges + publishes) — **never both**. Removes the
  INTEGRATOR-vs-MAINTAINER merge/release collisions.
- **Kanban columns partitioned:** ORCHESTRATOR owns **assignment/priority**
  columns (`assign:*`); INTEGRATOR owns **merge-driven** transitions
  (in-review → merged → done). Different columns → no write conflict. (Make
  INTEGRATOR's persona explicitly accept the merge-driven transitions — today
  only the ORCH persona asserts it.)
- **design/ SSOT → single design-primary writer** (TRDD-32cea83e).

### R3 — Claim/lease registry (Net 1; closes G1/G4/G6)

A generalized **claim/lease** service: clone the governance-request-registry
shape + the proven `user-presence.ts` mkdir cross-process lock + a
`/api/claims/[resource]/acquire|release` endpoint (auth'd via the existing
identity/IBCT layer). Before editing a claim-based resource (a specific TRDD,
PRRD rule, or an un-owned shared file), an agent acquires a TTL'd claim;
others see it and defer. Stale-takeover + monotonic guard already proven. Makes
the advisory `current-owner:`/`assignee:` **enforced**.

### R4 — Optimistic versioning (Net 2; closes G2)

design/ + PRRD + TRDD writes carry an **expected content-hash / rev**; the
write-lane (or server) rejects a stale write (compare-and-swap) → loser
rebases. Cheap; catches lost updates leases miss.

### R5 — Merge queue + path-overlap detection (Net 3; closes G3/G7)

The merge owner (INTEGRATOR/MAINTAINER per repo) runs a **merge queue**:
serialize merges; before merging PR-B, diff its path-set against in-flight +
recently-merged PRs; on overlap, require rebase-onto-fresh-main + re-test.
Proactive overlap detection on top of GitHub's reactive strict-status-checks.

### R6 — Atomic Python writes (Foundation; closes G5; trivial)

Make `prrd_lib.write_prrd` + the TRDD/kanban tooling use **tmp+rename**
(reuse `document-registry.ts:59-67` pattern) and take the R3 claim. Closes the
local torn-write window before git. Do this regardless of the rest.

### Defense-in-depth ordering

1. **Ownership map (R1/R2)** prevents most conflicts up front.
2. **Worktree isolation (F)** confines edits until merge.
3. **Claim leases (R3)** serialize within a domain / for un-owned files.
4. **Optimistic versioning (R4)** catches lost updates.
5. **Merge queue + overlap (R5)** catches code conflicts at merge.
6. **Janitor reconcile + the approval watchdog (TRDD-32cea83e / rule Part D)**
   backstop drift + mis-ownership.

## Phasing

- **Phase 1 (cheap, high-value):** R1 ownership-map schema + the R2 role
  resolutions (persona edits via per-plugin issues) + R6 atomic writes + the
  derived-task delegation rule in the canonical rule.
- **Phase 2 (the nets):** R3 claim/lease registry (server + shared plugin),
  R4 optimistic versioning.
- **Phase 3:** R5 merge queue + path-overlap in the INTEGRATOR.

## Security & synchronization summary

- **Security:** ownership partition + claims + IBCT auth limit blast radius and
  bind sensitive domains (rulesets/CI/creds) to trusted, gated roles; merge-
  overlap detection flags unexpected edits to sensitive paths. Claims/leases
  MUST be authenticated (reuse amp-auth/aid-token) so they can't be spoofed.
- **Synchronization:** non-overlapping domains need zero coordination;
  residual overlaps are serialized by claims, caught by versioning, and
  resolved at merge by the queue — composing with the already-present
  worktree isolation + SSOT single-writer.

## Verification status — facts vs assumptions (USER directive 2026-06-05: decide on facts + tests, never assume)

### ✓ VERIFIED (read the actual code / ran real tests)

- **Role ownership map** — the 8 personas were read directly; claims cite
  `file:line` (report 1). The orch-vs-integrator resolution is fact-based.
- **mkdir cross-process lock exists and is correct** — re-read
  `ai-maestro/lib/user-presence.ts:47-79,120-133`: atomic `mkdir`, 30s
  stale-takeover, 10s timeout, monotonic guard, tmp+rename. **CONSTRAINT
  surfaced by verification:** it is cross-*process* on **one filesystem**
  only — it does **NOT** work cross-*machine*. Agents can be on different
  hosts (one MANAGER/host), so the lease registry MUST be **server-mediated**
  for cross-host; the mkdir-lock alone is insufficient. (This corrects the
  "rec server" from a preference into a requirement.)
- **G5 confirmed real** — `prrd-trdd/prrd_lib.py:362` is a bare
  `p.write_text(render_prrd(doc))` — no tmp+rename, no lock. Concurrent/crash
  torn-write is a genuine defect. Fix = the proven tmp+rename pattern.
- **proposal-approvals tool** — 15/15 real tests pass (this repo).

### ✗ ASSUMED — must be tested BEFORE the decision is committed

| Hypothesis | Test that would verify it |
|---|---|
| **1B** — a `design/`-only PR can auto-merge into a `baseline-*`-protected `main` | Create a throwaway sandbox repo, apply the ratified rulesets, open a `design/`-only PR, wire the diff-only-`design/**` CI gate + auto-merge, OBSERVE whether it merges without a human approval and whether the ruleset blocks it |
| **2A** — GitHub Action fan-out mirrors `design/` across repos, loop-safe, seconds | 3 sandbox repos + the Action; push a `design/` change to primary; OBSERVE replication, timing, and that mirror commits do NOT re-trigger fan-out |
| **Cross-host lease** | prototype the `/api/claims` endpoint (server) + 2 clients incl. a simulated second host; assert mutual exclusion + TTL takeover |
| **Merge-queue path-overlap** detection actually catches C4 | unit-test an overlap detector on synthetic PR file-sets; integration-test two same-file green PRs |
| **Optimistic versioning** compare-and-swap rejects stale writes | prototype + concurrent-writer test |
| report-2 items marked **? INFERRED** (agent-heartbeat = liveness, not lease) | read `lib/agent-status.ts` before relying on it |

**I will NOT present 1B/2A as recommendations-of-fact until the sandbox test
above is run.** They are the current best hypotheses; the test decides.

## Decisions needed (USER)

1. **Adopt single-writer-per-domain as the primary rail?** (rec **yes**)
2. **Confirm R2 role resolutions:** MAINTAINER owns ruleset config; INTEGRATOR
   = merge-gate (rename, defer config); merge/release single-owner-per-repo;
   kanban column partition. (rec **yes**)
3. **Phasing:** build Phase 1 now (ownership-map + role resolutions + atomic
   writes + delegation rule), defer the lease registry + merge queue to
   Phase 2/3? (rec **yes**)
4. **Claim/lease home:** AI Maestro **server** (clone governance-registry) vs a
   file-based mkdir-lock in the shared plugin. (rec **server** — reuses the
   auth'd governance shape; file-lock fallback for offline.)

## Approval log

- 2026-06-05T23:36:01+0200 — Authored by amama as a Tier-3 PROPOSAL from the
  USER-delegated deep analysis (2026-06-05). Evidence: the two
  reports/design-concurrency/ surveys. Awaiting USER decisions.
