---
name: amama-autonomous-fallback
description: Use when an approval request arrives from a peer agent (CHIEF-OF-STAFF, AUTONOMOUS, MAINTAINER) and the user is unavailable. Trigger after consulting amama-presence-tracker. Reads the reversibility matrix and returns a verdict (approve-autonomously / defer / escalate-to-user). Loaded by ai-maestro-assistant-manager-agent-main-agent.
version: 1.0.0
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: false
---

# Autonomous-Fallback Skill

## Overview

Decides what to do with an inbound approval request when the user is `monitoring`, `away`, or `dnd`. Consults the [reversibility matrix](references/reversibility-matrix.md) — the single source of truth for which operations are auto-approve-eligible — then applies the per-state authority table from [amama-presence-tracker/references/state-thresholds.md](../amama-presence-tracker/references/state-thresholds.md).

Phase 1 of TRDD-bfcedff0. Hard-floor list (always-escalate ops) inherited from `amama-amcos-coordination/references/delegation-rules.md:112-126`. Defense-in-depth string-match guard hard-blocks production/security paths until phase 1.5 adds HMAC.

## Prerequisites

- AMAMA persona loaded.
- [amama-presence-tracker](../amama-presence-tracker/SKILL.md) callable (returns the current state).
- `references/reversibility-matrix.md` present and parseable.
- The hard-floor list at `skills/amama-amcos-coordination/references/delegation-rules.md:112-126` accessible.

## Instructions

Apply this procedure for every approval request that arrives via AMP from a peer agent (CHIEF-OF-STAFF, AUTONOMOUS, MAINTAINER). Never apply it to messages from the user.

1. **Hard-floor gate (immutable, ALWAYS-ESCALATE).** If the requested operation matches any of the seven hard-floor categories — production deployments, security-sensitive changes, data deletion, external communications, budget commitments, breaking changes to public APIs, access changes — return `(escalate-to-user, "hard-floor")` and STOP. The hard-floor does not consult the matrix.

2. **Defense-in-depth string-match guard (phase 1 only — replaced by HMAC in phase 1.5).** If any field of the approval request (operation key, target path, branch name, attributes) matches the regex `(production|prod|main|secrets|credentials|iam|auth)` (case-insensitive), return `(escalate-to-user, "phase-1-string-match-guard")`. This is intentionally over-broad — it will be replaced when phase 1.5 ships HMAC verification.

3. **Schema / identity gate.** If `source_role` is not in `{COS, AUTONOMOUS, MAINTAINER}`, OR if the operation key is not present in the matrix, return `(defer, "unclassified-or-unknown-source")`. Phase 1 logs the deferred entry with empty Compensating-Action.

4. **Presence gate.** Call [amama-presence-tracker](../amama-presence-tracker/SKILL.md) `get_state()`. If state is `active`, `unknown`, or `unknown-after-compaction`, return `(escalate-to-user, "presence-not-permitting-fallback")`. Status quo applies — every risky approval still goes to the user.

5. **Per-role authority overrides.**
   - `source_role == AUTONOMOUS`:
     - If `attributes.first_push_to_main` is true → return `(escalate-to-user, "AUTONOMOUS-first-push-to-main → W")`.
     - If `attributes.breaking_change` is true → return `(escalate-to-user, "AUTONOMOUS-breaking-change → W")`.
     - For COMPENSABLE rows (matrix class C), downgrade to `defer` (require ratification on user return) — even though state would otherwise auto-approve a C in `away`.
   - `source_role == MAINTAINER`:
     - The eligible matrix subset is `{add-label-issue-or-pr, comment-issue-or-pr, open-draft-pr, convert-draft-pr-to-ready, delete-merged-worktree}` (rows 13-16, 23). All other rows → `(escalate-to-user, "MAINTAINER-out-of-scope")`.
   - `source_role == COS`: the full matrix applies as written.

6. **R6 v3 routing constraint (2026-05-05).** If the operation's TARGET agent is a team-internal title (ORCHESTRATOR, ARCHITECT, INTEGRATOR, MEMBER, or any custom team-layer title), the matrix verdict still applies, BUT the operation must be EXECUTED by sending the instruction to the team's CHIEF-OF-STAFF — never directly to the team member. AMAMA composes the AMP message addressed to the COS (whitelist enforced at composition time: `recipient ∈ {HUMAN, peer MANAGERs, CHIEF-OF-STAFF, AUTONOMOUS, MAINTAINER}`). The COS then performs the operation inside the team. This constraint applies regardless of state and regardless of source-role.

7. **Matrix lookup (snapshot rule).** Read the full matrix file ONCE at this step and cache the parse in-memory for the rest of the decision. If the user edits the matrix concurrently, the in-flight decision uses the snapshot. The next decision uses the new content. Resolve `classification ∈ {R, C, W}` from the matrix row matching the operation key.

8. **Apply state-authority table** (from `state-thresholds.md`):
   - `monitoring` → R: `approve-autonomously`. C: `defer`. W: `defer`.
   - `away`       → R: `approve-autonomously`. C: `approve-autonomously`. W: `defer`.
   - `dnd`        → R: `approve-autonomously`. C: `defer`. W: `defer`.

9. **Audit log (single source of truth — append-only).** Every verdict — approve, defer, escalate — appends ONE entry to `docs_dev/approvals/autonomous-decisions-pending-ratification.md`. Each entry is structured as:

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

10. **Return the verdict tuple** to the caller in the persona decision tree:
    `(verdict, classification, justification, compensating_action_ref?)`

## Phase-1 expected behavior

Because phase 1's `amama-presence-tracker` always returns `unknown` (the PRESENCE sister plugin has not shipped yet), step 4 ALWAYS escalates to the user. Therefore phase 1's `decide()` is **invisible in production** — it never auto-approves anything. The matrix and the policy logic are wired and audit-loggable, but no operation is taken without user review until phase 3 ships.

This is intentional. It lets the user inspect the matrix and the audit log against real approval requests for at least one week before phase 1.5 / phase 3 enable any active push.

## What this skill does NOT do

- Does NOT execute the operation itself. After `approve-autonomously`, the persona invokes the existing operation routine (e.g. running tests, opening a PR) with the COS as recipient when the target is team-internal.
- Does NOT modify the matrix or thresholds.
- Does NOT verify HMAC. Phase 1.5 adds the cue-HMAC check.
- Does NOT parse cue lines from any source. Phase 1 has no cue parser.
- Does NOT auto-approve any hard-floor operation, regardless of state, ever.

## Related

- [amama-presence-tracker](../amama-presence-tracker/SKILL.md) — must be called first to establish state.
- [amama-amcos-coordination](../amama-amcos-coordination/SKILL.md) — the existing COS coordination workflows; supplies the hard-floor list and the AMP message templates.
- [amama-approval-workflows](../amama-approval-workflows/SKILL.md) — GovernanceRequest workflows for approvals that ARE escalated to user.
- [reversibility-matrix](references/reversibility-matrix.md) — the 25-row classification table.
- TRDD-bfcedff0: `design/tasks/TRDD-bfcedff0-21c8-439f-a3e5-b2dcc3b8ad19-amama-phase-1-presence-matrix.md`
