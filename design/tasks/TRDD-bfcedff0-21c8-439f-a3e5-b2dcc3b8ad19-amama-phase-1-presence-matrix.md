# TRDD-bfcedff0 — AMAMA Phase 1: Presence-read + Reversibility Matrix (with v3 hardening #1)

**TRDD ID:** `bfcedff0-21c8-439f-a3e5-b2dcc3b8ad19`
**Filename:** `design/tasks/TRDD-bfcedff0-21c8-439f-a3e5-b2dcc3b8ad19-amama-phase-1-presence-matrix.md`
**Tracked in:** this repo (`design/tasks/` is git-tracked)
**Status:** Not started
**Owner:** Emasoft
**Created:** 2026-05-05
**Plugin:** `ai-maestro-assistant-manager-agent` (AMAMA)
**Target version:** v2.8.0 (next minor — closes audit Gap A partial + Gap B partial)
**Estimated effort:** ≤ 1 day
**Reversibility:** full (4 new files + 1 diff revertible by single `git revert`)

---

## 1. User request (verbatim)

The motivating request, paraphrased from the conversation that produced this TRDD:

> "Examine the current skills and workflows of the assistant manager main agent and evaluate its ability to handle multiple autonomous agents and teams, and reporting to the user every problem or important decision if the user is available, otherwise to take decisions in his stead."

Subsequent direction:

> "Examine the janitor to see if it can be used to improve the MANAGER workflow, or if there are better ways to solve the problems you found. A mixed solution would be even better."

> "Take your time and think of all the edge cases that can put each of the proposed plans into a crisis and see what plan solve the crisis better."

> "go on, continue" (authorization to draft this TRDD)

The audit (`reports/assistant-manager-audit/20260504_023156+0200-orchestration-capability-audit.md`) found three gaps. The crisis-stress-test (`reports/assistant-manager-audit/20260504_153853+0200-crisis-stress-test-plan-v3.md`) selected **Plan v3 = v2-multi-plugin + four targeted hardening additions** as the answer. This TRDD is **phase 1** of that plan — the smallest viable cut — bundled with **v3 hardening #1** (sticky-unknown after compaction + versioned schema).

---

## 2. Why phase 1 first, alone, and what it deliberately does NOT deliver

Phase 1 is **invisible in production until phase 3 ships**. The reversibility matrix is consulted only when `availability_state.state ≠ active`. Only the PRESENCE sister plugin (phase 3, separate TRDD) writes the host-global file `~/.aimaestro/host-state/last-user-input.ts` that drives state transitions. Until that plugin is installed, AMAMA reads file-absent → `unknown`, refuses all autonomous-fallback decisions, and falls through to its existing "always escalate" behavior. Therefore:

- Phase 1 cannot regress production behaviour.
- Phase 1 establishes the **policy artifacts** (matrix, thresholds, decision logic) so phases 1.5+ can rely on them.
- Phase 1 lets the user **inspect the matrix in production for at least one week** — tuning rows, finding misclassifications — before any cron-driven push begins.

What phase 1 does NOT deliver:

| Deferred | Lands in | Reason |
|---|---|---|
| Active push from cron / heartbeat | Phase 3 (PRESENCE plugin) | Phase 3 is its own plugin and its own TRDD |
| Cue HMAC + replay protection (v3 hardening #4) | Phase 1.5 | HMAC ships before phase 3 emits any cue; gates phase 3 |
| `mkdir`-mutex + dispatch ordering (v3 hardenings #2, #3) | Phase 1.5 | Same gating |
| Slash commands (`/amama-set-availability`, `/amama-ratify-pending`, `/amama-revert-decision`, `/amama-autonomy-tier`, `/amama-fleet-status`) | Phase 2 | Commands consume phase 1's logic; no value alone until logic is exercised |
| Ratification ritual + per-item commit | Phase 2 | Same |
| Multi-team fleet view + AMAMA-DET sister plugin | Phase 4 | Independent feature, separate plugin |
| Out-of-band notifier (Slack/oh-my-hi/Discord) | Phase 6 | Opt-in, depends on user-installed channel |
| MAINTAINER GHA push-trigger | Phase 7 (latency optimization, NOT wake mechanism) | MAIN polls every 5min already |
| `availability_transitions`, `autonomous_decisions`, `team_health` CozoDB tables | Phase 2 | File-based fallbacks suffice for phase 1's read-only logic |
| Compensating-action transaction-id chain (closes residual D3) | Phase 1.5 | Minor follow-up |

---

## 3. Files (5 — exact paths and roles)

### 3.1 NEW — `skills/amama-presence-tracker/SKILL.md`

**Purpose.** Provide a single read-side interface to compute the user's current availability state. Read from the host-global file (when present) and the AMAMA CozoDB `availability_state` relation. Validate schema version. Apply v3 hardening #1: sticky-unknown after compaction.

**Loaded by.** Add this skill to the `skills:` frontmatter list of `agents/ai-maestro-assistant-manager-agent-main-agent.md` (see §3.5).

**Triggers.** Any decision-tree branch in the persona where the agent must classify routine-vs-escalation (today: `If approval needed → escalate to user`; tomorrow: `If approval needed → consult presence-tracker → consult autonomous-fallback`).

**Input file paths (read).**
- `~/.aimaestro/host-state/last-user-input.ts` — host-global epoch (written by PRESENCE plugin in phase 3; absent in phase 1)
- `<project>/.claude/amama/availability-overrides.md` — user explicit overrides with TTL (written by `/amama-set-availability` in phase 2; absent in phase 1)
- AMAMA's CozoDB `availability_state(state, since, notes)` — fallback when files unavailable
- A new in-process flag `compaction_observed_this_session` — set true on the first SessionStart that follows a compaction event

**Output (per call).** A single tuple: `(state: enum{active,monitoring,away,dnd,unknown,unknown-after-compaction}, since: epoch, source: enum{file,db,override,absent,corrupt-schema,absent-and-no-db})`.

**Algorithm (pseudocode).**

```
def get_state():
    if compaction_observed_this_session and not _confirmed_after_compaction:
        return ("unknown-after-compaction", now, "compaction-guard")

    override = read_override_if_unexpired()
    if override is not None:
        return (override.state, override.since, "override")

    last_input = read_host_global_last_input()  # phase 1: returns NULL when file absent
    if last_input is None:
        # Phase 1 default: graceful degradation, no false positives.
        return ("unknown", now, "absent-and-no-presence-plugin")

    if not _has_valid_schema(last_input.raw):
        return ("unknown", now, "corrupt-schema")

    age_seconds = max(0, now - last_input.epoch)  # v3 hardening: clamp ≥ 0 (B8 NTP backward jump)

    if age_seconds < 30*60:        return ("active",     last_input.epoch, "auto-clock")
    if age_seconds < 4*3600:       return ("monitoring", last_input.epoch, "auto-clock")
    if age_seconds < 24*3600:      return ("away",       last_input.epoch, "auto-clock")
    return ("dnd-implied", last_input.epoch, "auto-clock")
```

**v3 hardening #1 — versioned schema.** The `last-user-input.ts` file format is:

```
# AIMAESTRO-PRESENCE v=1
<epoch_seconds>
```

Parser MUST refuse anything missing the magic header or with `v != 1`. On refusal, return `("unknown", now, "corrupt-schema")`. The PRESENCE plugin will write this format when it ships in phase 3.

**SessionStart guard (sticky-unknown after compaction).** AMAMA's `scripts/amama_session_start.py` (modified in §3.5) sets the flag `compaction_observed_this_session = True` whenever it detects a freshly compacted session (heuristic: in-memory state empty + recent SessionStart marker on disk). Until the next confirmed presence read (which can only come from a phase-3 detector), `get_state()` returns `unknown-after-compaction`. This closes crisis D4 (compaction destroys cue read result).

**Side effects.** Read-only. Writes only to CozoDB `availability_transitions` (NEW append-only audit log) when a state change is observed across calls. CozoDB write is best-effort — if the DB is locked, log a one-line warning and skip. (Phase 2 will add the formal `availability_transitions` schema; phase 1 logs to a markdown fallback `docs_dev/sessions/availability-log.md` when DB unavailable.)

### 3.2 NEW — `skills/amama-presence-tracker/references/state-thresholds.md`

**Purpose.** Externalize the threshold table so phase 2's `/amama-set-availability` can read the same numbers (single source of truth).

**Content.** A markdown table with one row per state, the auto-clock condition, the user-explicit-override syntax, and AMAMA's authority while in that state. Direct copy of v2 §4.3.

| State | Auto-trigger | Explicit override | AMAMA authority |
|---|---|---|---|
| `active` | `now - last_user_input < 30min` | `/amama-set-availability active [duration]` | Status quo. Escalate everything risky. Hard-floor still applies. |
| `monitoring` | `30min ≤ ... < 4h` | `/amama-set-availability monitoring [duration]` | Batch low-priority items. Escalate medium+. Auto-approve **REVERSIBLE only**. |
| `away` | `4h ≤ ... < 24h` | `/amama-set-availability away [duration]` | Auto-approve **REVERSIBLE + COMPENSABLE**. Defer ONE-WAY-DOOR. Out-of-band ping for CRITICAL (phase 6). |
| `dnd` | `... ≥ 24h` | `/amama-set-availability dnd [duration]` | Auto-approve **REVERSIBLE only**. Defer C and W. Out-of-band ping for SEV-0 only (phase 6). |
| `unknown` | `last_user_input` missing or schema-invalid; no override | `/amama-set-availability unknown` (rarely needed) | **Refuse all autonomous action.** Escalate every approval to user. |
| `unknown-after-compaction` | First call after detected compaction restart | n/a | Same as `unknown`. Stays until first phase-3 PRESENCE confirmation. |

**Critical guardrail (v2 §4.3).** Explicit-override TTL wins over auto-clock. `/amama-set-availability dnd 8h` then a single user prompt at hour 2 keeps state at `dnd` until the 8h window expires. The user message is processed, but the state machine does NOT snap back to `active`. Closes crisis B5.

### 3.3 NEW — `skills/amama-autonomous-fallback/SKILL.md`

**Purpose.** Policy logic. Given an incoming approval request from a peer agent, return a verdict: `approve-autonomously` / `defer` / `escalate-to-user`.

**Inputs.**
- The reversibility matrix (`references/reversibility-matrix.md`)
- The current availability state (from `amama-presence-tracker`)
- The approval-request fields: `source_role` (COS/AUTONOMOUS/MAINTAINER), `operation` (matrix-row key), `attributes` (e.g. `branch=main`, `breaking_change=true`)
- AMAMA's existing 7-op hard-floor list (per `delegation-rules.md:112-126`)

**Output (per call).** A verdict tuple: `(verdict, classification, justification, compensating_action_ref?)`.

**Decision tree.**

```
1. SAFETY GATE — hard-floor check.
   If operation in HARD_FLOOR_LIST → escalate-to-user. Reason: "always-require-user". Stop.

2. SCHEMA / IDENTITY GATE.
   If source_role unknown or operation unknown → defer. Reason: "unclassified-or-unknown-source".

3. STATE GATE.
   If state == unknown OR unknown-after-compaction → escalate-to-user.

4. PER-ROLE AUTHORITY GATE (v2 §4.5).
   If source_role == AUTONOMOUS:
       If attributes.first_push_to_main → ONE-WAY-DOOR override.
       If attributes.breaking_change   → ONE-WAY-DOOR override.
       Even C-class operations require ratification (downgrade by one notch).
   If source_role == MAINTAINER:
       Restrict to the issue-triage subset of matrix rows (13-16, 23 for now).

5. MATRIX LOOKUP.
   Read classification from matrix row (REVERSIBLE / COMPENSABLE / ONE-WAY-DOOR).
   Apply state-authority table from `state-thresholds.md`:
     active      → escalate-to-user (status quo)
     monitoring  → R: approve-autonomously; C: defer; W: defer
     away        → R: approve; C: approve; W: defer
     dnd         → R: approve; C: defer; W: defer

6. LOG.
   Every decision (auto-approve OR defer-as-fallback OR escalate) appends one entry to
   `docs_dev/approvals/autonomous-decisions-pending-ratification.md` with:
     - `Approval-ID: APPROVAL-YYYY-MM-DD-NNN`
     - `Decided-At: <timestamp+offset>`
     - `Source-Role: <COS|AUTONOMOUS|MAINTAINER>`
     - `Operation: <matrix-row-key>`
     - `Classification: <R|C|W>`
     - `State-At-Decision: <state>`
     - `Verdict: <approve|defer|escalate>`
     - `Justification: <one-line>`
     - `Compensating-Action: <ready-to-paste command>` (if approve)
     - `Ratified-At: -` (filled in phase 2 by ratification ritual)
   Phase 2 also writes the same record to a CozoDB `autonomous_decisions` table.

7. RETURN verdict.
```

**Snapshot rule (closes crisis F5).** The matrix file is read **once per decision** at the top of step 5 and cached in-memory for the rest of the decision. If the user edits the matrix concurrently, the in-flight decision uses the snapshot, the next decision uses the new content.

**R6 v3 routing constraint (2026-05-05).** Whenever the requested operation's TARGET agent is a team-internal title (ORCH, ARCH, INT, MEMBER, or any custom team-layer title), the matrix verdict applies BUT the operation must be EXECUTED by routing the instruction to the team's CHIEF-OF-STAFF — never directly. Concretely: a verdict of `approve-autonomously` for a team-internal target means "AMAMA composes an AMP message to the team's COS asking the COS to perform the operation, and logs that delegated execution under the same Approval-ID". AMAMA must NEVER send AMP messages to team-internal targets directly under R6 v3. The only exception is HUMAN, which retains universal access. This constraint applies regardless of state (active/monitoring/away/dnd) and regardless of source-role.

**Hard floor (immutable list).** Per `skills/amama-amcos-coordination/references/delegation-rules.md:112-126`:

1. Production deployments
2. Security-sensitive changes (auth, secrets, IAM)
3. Data deletion (any irreversible storage write)
4. External communications on behalf of user (release notes, public posts)
5. Budget commitments
6. Breaking changes to public APIs
7. Access changes (permissions, repo visibility, branch protection)

These ALWAYS escalate regardless of state. The matrix's row-level classification is consulted only AFTER the hard-floor gate passes.

### 3.4 NEW — `skills/amama-autonomous-fallback/references/reversibility-matrix.md`

The single source of truth for autonomous-fallback eligibility. Format: each row carries `key | classification | applies_to_roles | compensating_action | notes`.

| # | Operation key | Class | Roles eligible | Compensating action | Notes |
|---|---|---|---|---|---|
| 1 | `run-unit-tests` | R | COS, AUTONOMOUS, MAINTAINER | n/a (read-only) | F2 caveat: triggers cloud minutes if CI hooks |
| 2 | `run-integration-tests` | R | COS, AUTONOMOUS, MAINTAINER | n/a (read-only) | F2 caveat: as above |
| 3 | `generate-status-report` | R | COS, AUTONOMOUS, MAINTAINER | n/a (read-only) | |
| 4 | `run-linter` | R | COS, AUTONOMOUS, MAINTAINER | n/a (read-only) | |
| 5 | `run-type-checker` | R | COS, AUTONOMOUS, MAINTAINER | n/a (read-only) | |
| 6 | `read-files` | R | COS, AUTONOMOUS, MAINTAINER | n/a (read-only) | |
| 7 | `send-amp-message-to-cos` | R | COS, AUTONOMOUS, MAINTAINER | Re-send corrective AMP message | AMP can supersede but not delete |
| 8 | `wake-hibernated-agent` | R | COS, AUTONOMOUS, MAINTAINER | `POST /api/agents/{id}/hibernate` | |
| 9 | `hibernate-agent-no-task` | R | COS, AUTONOMOUS, MAINTAINER | `POST /api/agents/{id}/wake` | |
| 10 | `hibernate-agent-with-task` | C | COS, AUTONOMOUS | wake + replay last in-flight prompt; possible duplicate work | |
| 11 | `commit-feature-branch` | R | COS, AUTONOMOUS, MAINTAINER | `git revert <sha>` | Creates a revert commit; preserves history |
| 12 | `push-feature-branch` | C | COS, AUTONOMOUS, MAINTAINER | `git push --force-with-lease` to rewind + notify any reviewer who pulled | |
| 13 | `open-draft-pr` | R | COS, AUTONOMOUS, MAINTAINER | `gh pr close <num>` | |
| 14 | `convert-draft-pr-to-ready` | R | COS, AUTONOMOUS, MAINTAINER | `gh pr ready --undo <num>` | |
| 15 | `add-label-issue-or-pr` | R | COS, AUTONOMOUS, MAINTAINER | `gh issue edit <num> --remove-label <label>` | |
| 16 | `comment-issue-or-pr` | C | COS, AUTONOMOUS, MAINTAINER | `gh api repos/.../issues/comments/<id> -X DELETE` | |
| 17 | `merge-pr-squash` | C | COS, AUTONOMOUS | `git revert -m 1 <merge-sha>` + force-push (visible in history) | AUTONOMOUS: defer if `attributes.first_push_to_main` |
| 18 | `merge-pr-fast-forward` | C | COS, AUTONOMOUS | `git push --force-with-lease` to rewind main (requires explicit user notice) | Fork to W if `BREAKING CHANGE` token in commit body |
| 19 | `deploy-to-staging` | C | COS | Re-run previous staging deploy from prior git tag | |
| 20 | `deploy-to-production` | W | (none) | (W — defer) | Hard-floor row 1 also covers this |
| 21 | `db-migration-forward` | C | COS | run the `down` migration if available; otherwise W | |
| 22 | `db-migration-destructive-down` | W | (none) | (W — defer) | Data loss is unrecoverable |
| 23 | `delete-merged-worktree` | R | COS, AUTONOMOUS, MAINTAINER | `git worktree add <path> <branch>` | |
| 24 | `delete-unmerged-worktree` | W | (none) | (W — defer) | Work lost unless branch preserved |
| 25 | `safe-delete-file` | R | COS, AUTONOMOUS, MAINTAINER | `cp -R .trashcan/<ts>/. ./` per janitor's restore recipe | Uses `/janitor-safe-delete` |

**Classification legend.**
- **R (REVERSIBLE)** — undo is a single command, byte-identical state restored. Eligible in `monitoring/away/dnd`.
- **C (COMPENSABLE)** — undo is a sequence with side effects. Eligible in `away` only. Never in `dnd`.
- **W (ONE-WAY-DOOR)** — undo impossible or unbounded risk. NEVER auto-approved. Always defer.

**Per-role authority overrides (applied in §3.3 step 4).**

- `AUTONOMOUS`:
  - Downgrade C → defer (require ratification on return).
  - `attributes.first_push_to_main = true` → escalate (W override).
  - `attributes.breaking_change = true` → escalate (W override).
- `MAINTAINER`:
  - Eligible rows restricted to `{13, 14, 15, 16, 23}` (issue-triage scope).
  - Other rows → escalate.
- `COS`:
  - Full matrix as above.

**Update protocol.**
- New operations: add a row, classify default to W, schedule a follow-up to refine.
- Re-classifications (e.g. F2 surprise): bump phase to P0, edit row, commit message must contain `matrix-amend` token.

### 3.5 MODIFY — `agents/ai-maestro-assistant-manager-agent-main-agent.md`

**Three edits.**

**Edit 1.** Add the two new skills to the `skills:` YAML frontmatter list.

**Edit 2.** Add a new sub-section under "When to Use Judgment" (currently `:285-301`) titled **"When state ≠ active (autonomous-fallback)"**. Content (verbatim spec):

> When an approval request arrives from a peer agent (CHIEF-OF-STAFF, AUTONOMOUS, or MAINTAINER):
>
> 1. Consult `amama-presence-tracker.get_state()`. If state is `active` or `unknown` or `unknown-after-compaction`, escalate to user as today (no behaviour change).
> 2. Otherwise (state ∈ `{monitoring, away, dnd}`), consult `amama-autonomous-fallback.decide(request)`.
> 3. Apply the verdict:
>    - `approve-autonomously` → execute the operation, append to `docs_dev/approvals/autonomous-decisions-pending-ratification.md`, send approval AMP to source-role with `Approved-By: AMAMA (autonomous-fallback)` field.
>    - `defer` → reply to source with `pending-ratification` status, queue for user-return ritual (phase 2 implements the ritual; phase 1 logs only).
>    - `escalate-to-user` → escalate as today.
> 4. Hard-floor list ALWAYS escalates regardless of state.

**Edit 3.** In `scripts/amama_session_start.py`, add a SessionStart-time check that sets `compaction_observed_this_session = True` whenever the session is detected as freshly compacted (heuristic: empty in-memory marker file + recent SessionStart timestamp). The check writes a one-line audit entry to `docs_dev/sessions/compaction-events-log.md`. The flag is read by `amama-presence-tracker` (§3.1).

**Test for non-regression.** When `~/.aimaestro/host-state/last-user-input.ts` is absent (production reality in phase 1), every existing AMAMA decision path reaches the SAME outcome it reached before phase 1 — the new `When state ≠ active` branch is gated behind a `state ∈ {monitoring, away, dnd}` condition that cannot be true without the file.

---

## 4. Test scenarios (subset of crisis-stress-test §6.3)

Six scenarios. Each is a fixture-driven unit/integration test runnable from `pytest` or a manual scenario file. Names match crisis IDs from the stress-test report.

### T1 — B2: corrupted `last-user-input.ts`

**Fixture.** Write `~/.aimaestro/host-state/last-user-input.ts` with content `not_a_number\nlol\n`. Compaction flag = false. No override file.

**Action.** Call `amama-presence-tracker.get_state()`.

**Expected.** Returns `("unknown", now, "corrupt-schema")`. Audit log records `notes='corrupt-schema'`. NO autonomous-fallback path is entered for any subsequent approval request in the same call.

### T2 — F1: matrix lookup with unclassified op

**Fixture.** State = `away`. Approval request: `(source=COS, operation='deploy-to-quantum-cloud')` (not in matrix).

**Action.** `amama-autonomous-fallback.decide(req)`.

**Expected.** Verdict = `defer`. Reason = `"unclassified-or-unknown-source"`. Audit log shows the entry with empty Compensating-Action.

### T5 — B5: dnd-override + 1 prompt mid-window

**Fixture.** Override file written with `state=dnd, ttl_seconds=8*3600, since=<now>`. Two hours later, `last-user-input.ts` updated with new epoch.

**Action.** `amama-presence-tracker.get_state()` after the new prompt.

**Expected.** Returns `("dnd", since, "override")` (not `active`). Override TTL not yet expired. After 8h: returns whichever idle-clock state matches the actual last_user_input age.

### T7 — J3: merge-conflict in ratification file

**Fixture.** `docs_dev/approvals/autonomous-decisions-pending-ratification.md` contains `<<<<<<< HEAD ... ======= ... >>>>>>> main` markers.

**Action.** AMAMA tries to append a new autonomous-decision row.

**Expected.** Detection by SessionStart guard (or by the append routine). AMAMA refuses to append, emits one user-facing line: `"Pending-ratification file has unresolved git merge markers. Please resolve at <path> before any autonomous decisions can be logged."` All subsequent approval requests escalate-to-user until resolved.

### T9 — B8: NTP backward jump

**Fixture.** Write `last-user-input.ts` with `epoch = now`. Then set system clock 30s back. Call `get_state()`.

**Expected.** `age_seconds = max(0, now-30 - now) = 0`. State = `active`. NO underflow exception or wrong-state classification. Audit log shows `notes='clock-skew-clamped'` if the `max(0, ...)` clamp was actually applied.

### T10 — K3: AUTO first-push-to-main

**Fixture.** State = `active`. Approval request: `(source=AUTONOMOUS, operation='merge-pr-squash', attributes={first_push_to_main: true})`.

**Action.** `decide(req)`.

**Expected.** Verdict = `escalate-to-user`. Reason = `"AUTONOMOUS + first-push-to-main → W override"`. The matrix row 17 says C, but the per-role override in §3.4 elevates to W. Audit log shows the chain (`row-17-class=C; per-role-override=W; final=escalate`).

---

## 5. Test plan

- **Unit tests (5 files).** `tests/unit/test_amama_presence_tracker.py`, `test_amama_autonomous_fallback.py`, `test_reversibility_matrix.py`, `test_state_thresholds.py`, `test_session_start_compaction_guard.py`.
- **Integration test.** `tests/integration/test_phase1_end_to_end.py` — simulates four states via fixture files, walks one approval per state, verifies log entries.
- **Matrix lookup coverage.** 25 rows × 3 source roles × 5 states = 375 combinations. Spot-check 30 critical pairs (every row × every role-state intersection that crosses an authority boundary).
- **No new infrastructure.** No cron, no hook (other than the SessionStart edit), no detector, no HMAC, no CozoDB schema migration. Phase 1 should pass `pytest -q` in under 30s on the existing CI.
- **CPV strict.** Plugin must pass `cpv-validate-plugin` (the existing publish gate). No regressions in lint, encoding, marketplace, or skill validation.

---

## 6. Reversibility / bail-out

- Revert this entire phase = `git revert <commit-sha>` of the single phase-1 commit.
- 4 new files under `skills/`, 1 diff in `agents/...-main-agent.md`. No infrastructure to tear down.
- During production: the user can type `/amama-autonomy-tier strict` (delivered in phase 2) to disable matrix-driven auto-fallback at runtime. In phase 1, before the slash command exists, the bail-out is to `rm references/reversibility-matrix.md` — the autonomous-fallback skill's matrix-snapshot step (§3.3 step 5) handles file-absent → defer-everything → user-escalate.
- Per CLAUDE.md RULE 0, every file added in this phase MUST be committed before any subsequent edit lands. The phase-1 commit IS the ratchet.

---

## 7. Security considerations

- **Cue injection (H2).** Phase 1 emits no cues and parses no cues. Crisis H2 lands in phase 1.5 when the cue HMAC is added. **In phase 1, AMAMA must NOT begin to parse `[amama-…]` lines from any source** — the persona text edit in §3.5 must explicitly say "no cue parsing in phase 1; only in-process function calls".
- **Matrix tampering (H1).** The matrix file is committed and reviewed in PR. Tampering requires a PR. A subsequent phase will add a SHA-pinned matrix-hash check to detect post-merge edits.
- **Fabricated approval requests (H5).** Phase 1's `decide()` accepts approval requests by AMP; the source-role is taken from the AMP message. AMP messages are not yet HMAC-signed. **Phase 1's persona text MUST NOT auto-approve any operation that touches `production`, `main`, `prod`, `secrets`, `credentials`, `iam`, `auth` paths** even if the matrix says they're R or C. This is a defense-in-depth string-match guard at the top of `decide()`. Phase 1.5 replaces it with HMAC verification.
- **Schema validation.** v3 hardening #1 (§3.1) ensures malformed `last-user-input.ts` cannot inflate the user's apparent idleness — the parser refuses on missing magic header.
- **Compaction guard.** Sticky-unknown after compaction (§3.1) prevents a freshly compacted session from acting on a stale CozoDB state-snapshot.
- **R6 v3 routing constraint (2026-05-05).** When the requested operation's target is a team-internal agent (ORCH/ARCH/INT/MEMBER), AMAMA must NEVER send the AMP message directly. Even under `approve-autonomously` the message is composed and addressed to the team's CHIEF-OF-STAFF, with the actual operation embedded as a request the COS will execute inside the team. This prevents the "team gets a directive the COS doesn't know about" failure mode the user observed empirically. AMAMA's `decide()` MUST refuse to compose any AMP message whose recipient is a team-internal title — the recipient list is whitelisted to {HUMAN, peer MANAGERs, CHIEF-OF-STAFF, AUTONOMOUS, MAINTAINER}. The persona enforces this at composition time; the API enforces it (or will enforce it once the server graph is updated to v3) at delivery time.

---

## 8. Definition of Done

- [ ] All 4 new files created at the paths in §3.
- [ ] Main-agent .md edited per §3.5 (3 edits — frontmatter, decision branch, SessionStart guard).
- [ ] All 6 test scenarios in §4 pass.
- [ ] Unit + integration test files in §5 written and passing.
- [ ] `cpv-validate-plugin` passes with zero CRITICAL/MAJOR/MINOR findings.
- [ ] Plugin version bumped to v2.8.0 per the existing publish.py protocol.
- [ ] CHANGELOG.md entry under `### Added`.
- [ ] PR opened against `main`. PR body cites this TRDD by UUID.
- [ ] PR review done. Phase-1 commit on `main`.
- [ ] One week of observation before phase 1.5 starts (per ratification gate in §10).
- [ ] TRDD `Status:` line updated as work progresses (Not started → In progress → Done).

---

## 9. Open questions

| # | Question | Suggested answer |
|---|---|---|
| Q1 | Should phase 1 also add the `availability_transitions` CozoDB table, or is the markdown fallback enough? | Markdown only in phase 1. The table arrives in phase 2 alongside the formal ratification ritual. |
| Q2 | Should the SessionStart guard fire on EVERY restart or only on detected compaction? | Only on detected compaction. Plain restarts are safe — CozoDB persists. (Heuristic: empty in-memory marker file + recent SessionStart wall-clock.) |
| Q3 | What happens if AMAMA reads the matrix but then the file is `git pull`'d in mid-decision? | Snapshot rule (§3.3 step 5): the in-flight decision uses the version captured at decision-start. Next decision uses the new content. |
| Q4 | Should the per-role authority overrides be in the matrix file or in the autonomous-fallback skill text? | In the skill text (§3.3 step 4). The matrix file lists rows; the skill text encodes the role policy. Single matrix file, multi-role consumers. |
| Q5 | What's the right `availability-overrides.md` schema for phase 2's `/amama-set-availability`? | Out of scope for phase 1 (read-side only treats absent file as "no override"). Schema decision goes in the phase-2 TRDD. |
| Q6 | Does phase 1 need a slash command? | No. The skill is invoked via in-process call from the main-agent decision tree. Slash commands land in phase 2. |

---

## 10. Ratification gate (RULE 0 compliance)

This TRDD is the minimum viable cut. **Phase 1 ships, then operates for at least 1 week with real matrix data, before phase 1.5 (HMAC + mutex + dispatch ordering) is opened.** The user is the ratifier:

1. Phase-1 commit lands → 1 week of operation → owner (Emasoft) reviews `docs_dev/approvals/autonomous-decisions-pending-ratification.md`.
2. If matrix rows are wrong, owner amends them in a `matrix-amend` commit.
3. After ratification of the week's data, owner opens the phase-1.5 TRDD.
4. Phases 3 / 4 / 5 / 6 / 7 each have their own TRDDs and their own ratification gates.

Do not start phase 1.5 until:
- ≥1 week elapsed since phase-1 commit
- 0 matrix rows downgraded due to "I thought this was reversible" surprises
- ≥3 actual approval requests routed through `decide()` and observed in the log

---

## 11. References

- Audit: `reports/assistant-manager-audit/20260504_023156+0200-orchestration-capability-audit.md`
- Plan v1 (option η): `reports/assistant-manager-audit/20260504_151750+0200-janitor-amama-synthesis-plan.md`
- Plan v2 (multi-plugin): `reports/assistant-manager-audit/20260504_152845+0200-janitor-amama-synthesis-plan-v2-multi-plugin.md`
- Plan v3 (crisis stress-test, chosen): `reports/assistant-manager-audit/20260504_153853+0200-crisis-stress-test-plan-v3.md`
- AMAMA persona: `agents/ai-maestro-assistant-manager-agent-main-agent.md`
- Hard-floor list: `skills/amama-amcos-coordination/references/delegation-rules.md:112-126`
- 4-state availability model: `skills/amama-session-memory/references/memory-architecture.md:99-107`
- Janitor base: https://github.com/Emasoft/ai-maestro-janitor (v0.3.15)
- Role plugins (untouched by phase 1):
  - `ai-maestro-chief-of-staff` v2.12.8
  - `ai-maestro-autonomous-agent` v1.0.8
  - `ai-maestro-maintainer-agent` v1.0.9

---

## 12. Change log

| Date | Author | Change |
|---|---|---|
| 2026-05-05 | AMAMA-orchestrator (Claude) on owner's instruction "go on, continue" | Initial draft |
| 2026-05-05 | AMAMA-orchestrator (Claude) on owner's R6 v3 update | Add R6 v3 routing constraint to §3.3 (autonomous-fallback) and §7 (security): operations targeting team-internal agents must route via COS even when matrix says auto-approve. AMP recipients whitelisted to {HUMAN, peer MANAGERs, COS, AUTONOMOUS, MAINTAINER}. |

End of TRDD.
