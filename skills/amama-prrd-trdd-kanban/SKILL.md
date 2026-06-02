---
name: amama-prrd-trdd-kanban
description: "MANAGER's role in the PRRD / TRDD / Kanban workflow. Use when AMAMA authors proto-TRDDs from user input, promotes from backburner to todo, mutates silver PRRD rules, reviews proposals routed via COS, or relays golden-rule decisions to/from the USER."
allowed-tools: "Bash(python3:*), Bash(get-prrd.py:*), Bash(prrd-edit.py:*), Bash(findprrd.py:*), Bash(findtrdd.py:*), Bash(kanban.py:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

## Overview

This is the MANAGER (AMAMA) role-layer of the PRRD / TRDD / Kanban
model. AMAMA owns the `backburner` and `todo` columns, mutates silver
PRRD rules, and is the RECIPIENT of approval requests from team agents.
For shared mechanics (scripts, frontmatter schema, citation grammar,
column-transition matrix), see the universal `prrd-trdd-kanban` skill
in ai-maestro-plugin.

## Prerequisites

- The universal `prrd-trdd-kanban` skill (ai-maestro-plugin) installed.
- `design/requirements/PRRD.md` and `design/tasks/` present in the repo.
- `$AID_AUTH` set for MANAGER ops (silver PRRD edits, column moves).
- Self-id as Emasoft for any git/commit step (name/email per global rules).

## Instructions

1. **Author proto-TRDDs in backburner.** On a new user request, create
   `design/tasks/TRDD-$TS-${UID:0:8}-<slug>.md` with `UID=$(python3 -c
   "import uuid; print(uuid.uuid4())")` and `TS=$(date +%Y%m%d_%H%M%S%z)`.
   Fill mandatory frontmatter: `trdd-id`, `title`, `column: backburner`,
   `created:`, `updated:`, `current-owner: amama`, `task-type:`, and
   `relevant-rules:` if the user named constraints. Body = paraphrased
   request. Commit it. (Transition #1: new → backburner.)
2. **Promote backburner → todo.** Pick the next proto-TRDD (highest
   priority or oldest), confirm intent, set `column: todo`, bump
   `updated:`, then AMP-send COS: "TRDD-<id> promoted to todo". After
   this, ORCHESTRATOR owns it. (Transition #2.)
3. **Receive approval requests via COS.** AMAMA does NOT request its own
   approval — team agents route their requests to AMAMA through COS.
4. **Apply the approval gate.** AMAMA's own mutations (backburner→todo,
   silver PRRD edits) are inherently MANAGER-authorized — no separate
   approval. For requests from agents, decide accept / reject /
   forward-to-user and AMP-reply the verdict (per R15.6 a direct AMP
   reply is allowed). See `exempt-operations.md` in the universal skill
   for which transitions need AMAMA's sign-off.
5. **Mutate silver PRRD rules; relay golden to USER.** Add / revise /
   delete silver rules directly via `prrd-edit.py`. For any GOLDEN-rule
   change, promote/demote, AMAMA refuses to act alone — relay to USER,
   then apply the decision via `prrd-edit.py --user <op>` only after the
   user authorises in writing. Relay USER outcomes back to the team
   (transitions #11 human_review→complete/dev, #30 →failed).

## Output

- TRDD edits: authored proto-TRDDs (backburner) and frontmatter bumps.
- Column moves: `backburner → todo`, plus USER-relayed #11 / #30 moves.
- AMP approval verdicts: accept/reject/forward replies to requesting COS.
- Silver PRRD rule mutations; USER-authorized golden-rule applications.

## Error Handling

- **Caller is not MANAGER** → refuse; AMAMA-only operations.
- **Request touches a GOLDEN rule** → do NOT mutate; relay to USER and
  wait for written authorization before `prrd-edit.py --user`.
- **Backburner overflow** (>10 idle proto-TRDDs) → queue a triage report
  to the USER rather than silently growing the queue.
- **Unsure whether a change is silver or golden, or who owns a column**
  → escalate to USER; never guess a destructive mutation.

## Examples

```text
# Promote backburner → todo, notify the team's COS
Subject: TRDD-1f2a promoted to todo
To: cos-payments
Type: status_update
Body: TRDD-1f2a "Add refund flow" is now in todo. ORCH should claim it.
      Priority: high. Rules: S3.2, S7.1.
```

```text
# Silver PRRD proposal accepted (verdict back to requester)
Subject: Re: Proposal P-88
To: cos-payments
Type: approval_decision
Body: Accepted. PRRD updated via prrd-edit.py: S4.2 — "<new text>".
```

## Resources

For all shared mechanics see the universal `prrd-trdd-kanban` skill in
ai-maestro-plugin — it bundles the PRRD design rules, the TRDD design-task
spec, the full column-transition matrix, the TRDD frontmatter schema, and
the `exempt-operations.md` approval reference. The AMAMA persona lives in
this plugin's `agents/` directory. Sibling role-layers exist for the other
roles (ORCH, ARCH, INT, MEM, COS, AUTO, MAINT) as `am*-prrd-trdd-kanban`
skills — consult them for delegation awareness.
