---
name: amama-autonomous-fallback
description: Use when an approval request arrives from a peer agent and the user is unavailable. Trigger with inbound AMP approvals from COS, AUTONOMOUS, or MAINTAINER. Returns approve-autonomously / defer / escalate-to-user.
version: 1.0.0
context: fork
agent: amama-assistant-manager-main-agent
---

# Autonomous-Fallback Skill

## Overview

Decides what to do with an inbound approval request when the user is `monitoring`, `away`, or `dnd`. Consults the 25-row reversibility matrix and the per-state authority table, applies the per-role authority overrides, and enforces the R6 v3 routing constraint (team-bound messages route via COS only). Phase 1 of TRDD-bfcedff0. The hard-floor list (always-escalate ops) is inherited from amama-amcos-coordination.

## Prerequisites

- AMAMA persona loaded.
- amama-presence-tracker callable (returns the current state).
- references/reversibility-matrix.md present and parseable.
- The hard-floor list at amama-amcos-coordination/references/delegation-rules.md:112-126 accessible.

## Instructions

Apply for every approval request from a peer agent (never to user messages). Full step-by-step procedure is in references/decision-flow.md (see Resources). Summary:

1. Hard-floor gate. If matched, escalate-to-user.
2. Phase-1 string-match guard (replaced by HMAC in phase 1.5).
3. Schema/identity gate. Unknown role or unclassified op → defer.
4. Presence gate. Call amama-presence-tracker; non-`away`/`monitoring`/`dnd` states escalate.
5. Per-role authority — AUTONOMOUS downgrades C→defer; MAINTAINER restricted to issue-triage subset; COS full matrix.
6. R6 v3 routing — team-internal targets always go via COS, never directly.
7. Matrix lookup (snapshot rule) — read once per decision.
8. State-authority table — `monitoring` R-only auto; `away` R+C auto; `dnd` R-only auto; W always defer.
9. Audit log — append one entry to docs_dev/approvals/autonomous-decisions-pending-ratification.md.
10. Return `(verdict, classification, justification, compensating_action_ref?)`.

Phase-1 behavior: amama-presence-tracker returns `unknown` until phase 3 ships, so step 4 always escalates. Policy is wired but dormant.

## Output

| Verdict | When emitted | Side effect |
|---------|--------------|-------------|
| `approve-autonomously` | Matrix says R or C, state permits | Operation executed (via COS for team-internal targets); audit-log entry appended |
| `defer` | Matrix says W, OR unclassified, OR per-role override downgraded | Reply to source with `pending-ratification`; audit-log entry; user reviews on return |
| `escalate-to-user` | Hard-floor / phase-1-string-match / state ∉ {monitoring,away,dnd} / per-role W-override | Standard escalation flow |

## Error Handling

| Error | Action |
|-------|--------|
| references/reversibility-matrix.md missing | Return `(escalate-to-user, "matrix-absent")` — strict-by-default |
| Operation key not in matrix | Return `(defer, "unclassified")` |
| `source_role` not in {COS, AUTONOMOUS, MAINTAINER} | Return `(defer, "unknown-source")` |
| `decisions-pending-ratification.md` unwritable | stderr warning, escalate-to-user instead of approving |
| amama-presence-tracker unreachable | Return `(escalate-to-user, "presence-unreachable")` |

## Examples

**T2 — unclassified op while away:**
```
state = away
request = (source=COS, op="deploy-to-quantum-cloud")
verdict = (defer, "unclassified")
audit log: APPROVAL-2026-05-05-001 | Source=COS | Op=deploy-to-quantum-cloud | Verdict=defer
```

**T10 — AUTO first-push-to-main (per-role override forces W):**
```
state = active   ; not even a fallback path
request = (source=AUTONOMOUS, op="merge-pr-squash", attrs={first_push_to_main: true})
verdict = (escalate-to-user, "AUTONOMOUS-first-push-to-main → W")
```

**Routine R-class while away:**
```
state = away
request = (source=COS, op="run-unit-tests", target=team-architect)
verdict = (approve-autonomously, R, "matrix-row-1")
side effect: AMP message composed to the team's COS asking COS to run-unit-tests inside the team (R6 v3 routing)
```

## Resources

- [references/decision-flow.md](references/decision-flow.md) — Full 10-step decision flow
  - Step 1 — Hard-floor gate, Step 2 — Phase-1 string-match guard, Step 3 — Schema/identity gate, Step 4 — Presence gate, Step 5 — Per-role authority overrides, Step 6 — R6 v3 routing constraint, Step 7 — Matrix lookup (snapshot rule), Step 8 — State-authority table, Step 9 — Audit log, Step 10 — Return verdict tuple

- [references/reversibility-matrix.md](references/reversibility-matrix.md) — The 25-row classification table
  - Classification legend, The 25 rows, Per-role authority overrides (applied in SKILL.md step 5), R6 v3 routing constraint reminder, Update protocol, Cross-reference with the hard-floor list, Crisis cross-reference

- TRDD-bfcedff0 (design/tasks/) — Phase-1 spec, ratification gate, change log
