# Decision flow — full 10-step procedure

## Table of Contents

- [Step 1 — Hard-floor gate](#step-1--hard-floor-gate)
- [Step 2 — Phase-1 string-match guard](#step-2--phase-1-string-match-guard)
- [Step 3 — Schema/identity gate](#step-3--schemaidentity-gate)
- [Step 4 — Presence gate](#step-4--presence-gate)
- [Step 5 — Per-role authority overrides](#step-5--per-role-authority-overrides)
- [Step 6 — R6 v3 routing constraint](#step-6--r6-v3-routing-constraint)
- [Step 7 — Matrix lookup (snapshot rule)](#step-7--matrix-lookup-snapshot-rule)
- [Step 8 — State-authority table](#step-8--state-authority-table)
- [Step 9 — Audit log](#step-9--audit-log)
- [Step 10 — Return verdict tuple](#step-10--return-verdict-tuple)

The full 10-step decision flow that amama-autonomous-fallback applies to every inbound approval request.

## Step 1 — Hard-floor gate

If the requested operation matches any of the seven hard-floor categories — production deployments, security-sensitive changes, data deletion, external communications, budget commitments, breaking changes to public APIs, access changes — return `(escalate-to-user, "hard-floor")` and STOP. The hard-floor does NOT consult the matrix. The 7 categories are inherited from amama-amcos-coordination/references/delegation-rules.md:112-126.

## Step 2 — Phase-1 string-match guard

Phase 1 only — replaced by HMAC verification in phase 1.5. If any field of the approval request (operation key, target path, branch name, attributes) matches the regex `(production|prod|main|secrets|credentials|iam|auth)` (case-insensitive), return `(escalate-to-user, "phase-1-string-match-guard")`. Intentionally over-broad — accepts false positives in exchange for safety until HMAC ships.

## Step 3 — Schema/identity gate

If `source_role` is not in `{COS, AUTONOMOUS, MAINTAINER}` OR if the operation key is not present in the matrix, return `(defer, "unclassified-or-unknown-source")`. Phase 1 logs the deferred entry with empty Compensating-Action.

## Step 4 — Presence gate

Call amama-presence-tracker `get_state()`. If state is `active`, `unknown`, or `unknown-after-compaction`, return `(escalate-to-user, "presence-not-permitting-fallback")`. Status quo applies — every risky approval still goes to user. **Phase 1 default**: state is always `unknown` until phase 3 ships, so this gate fires for every request — by design.

## Step 5 — Per-role authority overrides

- `source_role == AUTONOMOUS`:
  - `attributes.first_push_to_main = true` → `(escalate-to-user, "AUTONOMOUS-first-push-to-main → W")`
  - `attributes.breaking_change = true` → `(escalate-to-user, "AUTONOMOUS-breaking-change → W")`
  - For COMPENSABLE rows (matrix class C), downgrade to `defer` — even if state would otherwise auto-approve a C in `away`. Reason: solo agent has no team peer to second-guess.
- `source_role == MAINTAINER`:
  - Eligible matrix subset is `{add-label-issue-or-pr, comment-issue-or-pr, open-draft-pr, convert-draft-pr-to-ready, delete-merged-worktree}` (rows 13-16, 23). All other rows → `(escalate-to-user, "MAINTAINER-out-of-scope")`.
- `source_role == COS`: full matrix applies as written.

## Step 6 — R6 v3 routing constraint

(2026-05-05.) If the operation's TARGET agent is a team-internal title (ORCHESTRATOR, ARCHITECT, INTEGRATOR, MEMBER, or any custom team-layer title), the matrix verdict still applies, BUT the operation must be EXECUTED by sending the instruction to the team's CHIEF-OF-STAFF — never directly to the team member. Compose the AMP message addressed to the COS (whitelist enforced at composition time: `recipient ∈ {HUMAN, peer MANAGERs, CHIEF-OF-STAFF, AUTONOMOUS, MAINTAINER}`). The COS then performs the operation inside the team. Applies regardless of state and regardless of source-role.

Empirical motivation (recorded in TRDD-bfcedff0 §1, R6 v3 update): when MANAGER messages a team-internal agent directly, the COS or the team's ORCHESTRATOR are not informed, or have already issued contradictory instructions, producing chaos. The COS is the SOLE entry point into a team.

## Step 7 — Matrix lookup (snapshot rule)

Read references/reversibility-matrix.md ONCE at this step and cache the parse for the rest of the decision. If the user edits the matrix concurrently, the in-flight decision uses the snapshot. The next decision uses the new content. Resolve `classification ∈ {R, C, W}` from the matrix row matching the operation key. Closes crisis F5 (concurrent edit during decision).

## Step 8 — State-authority table

Apply the per-state authority (per amama-presence-tracker references/state-thresholds.md):

| State | R | C | W |
|-------|---|---|---|
| monitoring | approve-autonomously | defer | defer |
| away | approve-autonomously | approve-autonomously | defer |
| dnd | approve-autonomously | defer | defer |

Note: AUTONOMOUS source's per-role override (step 5) downgrades C → defer in `away` too.

## Step 9 — Audit log

Every verdict — approve, defer, escalate — appends ONE entry to `docs_dev/approvals/autonomous-decisions-pending-ratification.md`. Each entry uses this structure (append-only, immutable per existing AMAMA record-keeping rules):

```
## APPROVAL-YYYY-MM-DD-NNN
- Decided-At: <local-time-with-offset>
- Source-Role: <COS|AUTONOMOUS|MAINTAINER>
- Operation: <matrix-row-key>
- Target-Agent: <full-session-name>
- Target-Layer: <team-internal|peer|self>
- Classification: <R|C|W|hard-floor|unclassified>
- State-At-Decision: <state>
- Verdict: <approve-autonomously|defer|escalate-to-user>
- Justification: <one-line reason>
- Compensating-Action: <ready-to-paste shell command, or "n/a" or "deferred">
- Ratified-At: -
- Ratification-Verdict: -
```

The `Ratified-At:` and `Ratification-Verdict:` fields are filled in by phase 2's ratification ritual when the user returns. Phase 1 only writes the rows; the ritual command lands later.

## Step 10 — Return verdict tuple

Return `(verdict, classification, justification, compensating_action_ref?)` to the caller in the persona decision tree. The caller — in the persona's "When state ≠ active" decision-tree branch — applies the verdict per the routine documented in the main-agent .md.

## Phase-1 invisibility property

Steps 1-3 fire for every request. Step 4 (presence gate) ALWAYS escalates in phase 1 because amama-presence-tracker returns `unknown` until phase 3 ships. Therefore steps 5-10 don't execute in production until phase 3 — they're wired but dormant.
