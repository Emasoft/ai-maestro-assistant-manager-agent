# Reversibility matrix

## Table of Contents

- [Classification legend](#classification-legend)
- [The 25 rows](#the-25-rows)
- [Per-role authority overrides (applied in SKILL.md step 5)](#per-role-authority-overrides-applied-in-skillmd-step-5)
- [R6 v3 routing constraint reminder](#r6-v3-routing-constraint-reminder)
- [Update protocol](#update-protocol)
- [Cross-reference with the hard-floor list](#cross-reference-with-the-hard-floor-list)
- [Crisis cross-reference](#crisis-cross-reference)

Single source of truth for autonomous-fallback eligibility. Every approval request that is NOT in the hard-floor list (see amama-amcos-coordination/references/delegation-rules.md:112-126) is classified by this matrix.

## Classification legend

- **R (REVERSIBLE)** — undo is a single command, byte-identical state restored. Eligible for autonomous fallback in `monitoring`, `away`, and `dnd`.
- **C (COMPENSABLE)** — undo is a sequence with side effects (e.g. force-push that visibly rewinds main). Eligible in `away` only. Never in `dnd`. **AUTONOMOUS source downgrades C → defer.**
- **W (ONE-WAY-DOOR)** — undo is impossible or carries unbounded risk. NEVER auto-approved regardless of state. Always defer to user ratification on return.

## The 25 rows

| # | Operation key | Class | Roles eligible | Compensating action | Notes |
|---|---|---|---|---|---|
| 1 | `run-unit-tests` | R | COS, AUTONOMOUS, MAINTAINER | n/a (read-only) | F2 caveat: triggers cloud minutes when CI hooks are wired in — re-classify if surprise occurs |
| 2 | `run-integration-tests` | R | COS, AUTONOMOUS, MAINTAINER | n/a (read-only) | F2 caveat: as above |
| 3 | `generate-status-report` | R | COS, AUTONOMOUS, MAINTAINER | n/a (read-only) | |
| 4 | `run-linter` | R | COS, AUTONOMOUS, MAINTAINER | n/a (read-only) | |
| 5 | `run-type-checker` | R | COS, AUTONOMOUS, MAINTAINER | n/a (read-only) | |
| 6 | `read-files` | R | COS, AUTONOMOUS, MAINTAINER | n/a (read-only) | |
| 7 | `send-amp-message-to-cos` | R | COS, AUTONOMOUS, MAINTAINER | Re-send corrective AMP message | AMP cannot delete; supersede only. R6 v3 reminder: messages bound for team members route HERE. |
| 8 | `wake-hibernated-agent` | R | COS, AUTONOMOUS, MAINTAINER | `POST /api/agents/{id}/hibernate` | If target is team-internal, AMAMA asks the team's COS to wake — see §6 of SKILL.md (R6 v3 routing constraint) |
| 9 | `hibernate-agent-no-task` | R | COS, AUTONOMOUS, MAINTAINER | `POST /api/agents/{id}/wake` | Same R6 v3 routing rule for team-internal targets |
| 10 | `hibernate-agent-with-task` | C | COS, AUTONOMOUS | wake + replay last in-flight prompt; possible duplicate work | AUTONOMOUS source downgrades to defer |
| 11 | `commit-feature-branch` | R | COS, AUTONOMOUS, MAINTAINER | `git revert <sha>` | Creates a revert commit; preserves history |
| 12 | `push-feature-branch` | C | COS, AUTONOMOUS, MAINTAINER | `git push --force-with-lease` to rewind + notify any reviewer who pulled | |
| 13 | `open-draft-pr` | R | COS, AUTONOMOUS, MAINTAINER | `gh pr close <num>` | |
| 14 | `convert-draft-pr-to-ready` | R | COS, AUTONOMOUS, MAINTAINER | `gh pr ready --undo <num>` | |
| 15 | `add-label-issue-or-pr` | R | COS, AUTONOMOUS, MAINTAINER | `gh issue edit <num> --remove-label <label>` | |
| 16 | `comment-issue-or-pr` | C | COS, AUTONOMOUS, MAINTAINER | `gh api repos/.../issues/comments/<id> -X DELETE` | |
| 17 | `merge-pr-squash` | C | COS, AUTONOMOUS | `git revert -m 1 <merge-sha>` + force-push (visible in history) | AUTONOMOUS: defer if `attributes.first_push_to_main` (force-W via per-role override). |
| 18 | `merge-pr-fast-forward` | C | COS, AUTONOMOUS | `git push --force-with-lease` to rewind main (requires explicit user notice) | Fork to W if `attributes.breaking_change` is true |
| 19 | `deploy-to-staging` | C | COS | Re-run previous staging deploy from prior git tag | AUTONOMOUS not eligible — solo agent has no staging gate |
| 20 | `deploy-to-production` | W | (none) | (W — defer) | Hard-floor row 1 also covers this |
| 21 | `db-migration-forward` | C | COS | run the `down` migration if available; otherwise W | |
| 22 | `db-migration-destructive-down` | W | (none) | (W — defer) | Data loss is unrecoverable |
| 23 | `delete-merged-worktree` | R | COS, AUTONOMOUS, MAINTAINER | `git worktree add <path> <branch>` | |
| 24 | `delete-unmerged-worktree` | W | (none) | (W — defer) | Work lost unless branch preserved |
| 25 | `safe-delete-file` | R | COS, AUTONOMOUS, MAINTAINER | `cp -R .trashcan/<ts>/. ./` per janitor's restore recipe | Uses `/janitor-safe-delete` — recoverable from `.trashcan/` |

## Per-role authority overrides (applied in SKILL.md step 5)

- **AUTONOMOUS** source:
  - Downgrade C → defer (require ratification on return). The autonomous agent has no team architect/integrator to second-guess decisions, so the matrix is one notch stricter.
  - `attributes.first_push_to_main = true` → force-escalate (W override) for any merge operation.
  - `attributes.breaking_change = true` → force-escalate (W override).
- **MAINTAINER** source:
  - Eligible matrix rows restricted to `{13, 14, 15, 16, 23}` (issue-triage scope only).
  - All other rows → `(escalate-to-user, "MAINTAINER-out-of-scope")`.
- **COS** source:
  - Full matrix applies as written. No additional overrides.

## R6 v3 routing constraint reminder

When the operation's TARGET agent is a team-internal title (ORCH/ARCH/INT/MEMBER), the verdict from this matrix still applies — but the AMP message that EXECUTES the operation must be addressed to the team's CHIEF-OF-STAFF, never to the team member directly. AMAMA composes the message to the COS asking the COS to perform the operation inside the team. See SKILL.md §6 for full text. The recipient whitelist is enforced at composition time: `{HUMAN, peer MANAGERs, CHIEF-OF-STAFF, AUTONOMOUS, MAINTAINER}`.

## Update protocol

- **New operation.** Add a row. Default classification is W (defer) until the operation has been audited and re-classified.
- **Reclassification (e.g. F2 surprise — a row turns out to have hidden side effects).** Edit the row. Commit message MUST contain the token `matrix-amend` so the change is greppable in git history.
- **The matrix file is read once per decision** (snapshot rule, SKILL.md step 7). Concurrent edits do NOT affect the in-flight decision. The next decision uses the new content.

## Cross-reference with the hard-floor list

The seven hard-floor categories from `amama-amcos-coordination/references/delegation-rules.md:112-126` (production deploys, security, data deletion, external comms, budget, breaking changes, access changes) ALWAYS escalate, regardless of state and regardless of matrix classification. The matrix's row-level classification is consulted only AFTER the hard-floor gate passes.

| Hard-floor category | Mapped matrix rows | Notes |
|---|---|---|
| Production deployments | 20 (W) | Belt-and-suspenders. |
| Security-sensitive changes | (none) | Phase 1 string-match guard catches `secrets`, `credentials`, `iam`, `auth` paths until phase 1.5 adds HMAC. |
| Data deletion | 22, 24 (W) | Both already W. |
| External communications | 16 (C) | Comments may be ratified-or-rolled-back; release publication is a separate row to add when needed. |
| Budget commitments | (none) | Add row when a concrete operation arises. |
| Breaking changes | 18 (forks to W if `breaking_change` attribute is true) | Per-row attribute fork. |
| Access changes | (none) | Currently always escalated by hard-floor; matrix row would default W if added. |

## Crisis cross-reference

| Crisis ID | Matrix mechanism that closes it |
|---|---|
| F1 (new op not in matrix) | Step 3 of SKILL.md returns `(defer, "unclassified")` — strict-by-default |
| F3 (partial-execution failure) | Phase 1 records partial state in audit log; phase 1.5 adds tx-id |
| F5 (matrix edited concurrently) | Snapshot rule — matrix read ONCE per decision |
| F6 (ambiguous classification) | Per-row attribute forks (e.g. row 18 + `breaking_change` flag) |
| K3 (AUTONOMOUS first-push-to-main) | Per-role override: AUTONOMOUS + `first_push_to_main` → force W |
| L2 (social-engineering merge issue) | Per-role override: MAINTAINER restricted to issue-triage subset; merges not eligible |
