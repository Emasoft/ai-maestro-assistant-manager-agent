---
name: amama-prrd-trdd-kanban
description: "MANAGER's role in the PRRD / TRDD / Kanban workflow. Use when AMAMA authors proto-TRDDs from user input, promotes from backburner to todo, mutates silver PRRD rules, reviews proposals routed via COS, or relays golden-rule decisions to/from the USER."
allowed-tools: "Bash(python3:*), Bash(get-prrd.py:*), Bash(prrd-edit.py:*), Bash(findprrd.py:*), Bash(findtrdd.py:*), Bash(kanban.py:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

## Overview

This is the MANAGER's role-specific layer of the PRRD / TRDD / Kanban
model. For the universal mechanics (scripts, frontmatter schema,
citation grammar, column transition matrix), see the `prrd-trdd-kanban`
skill in `ai-maestro-plugin`.

## Approval discipline — AMAMA IS the MANAGER

AMAMA does NOT request its own approval. Instead, AMAMA is the
RECIPIENT of approval requests from team agents (routed via COS). See
the **prrd-trdd-kanban** universal skill's `exempt-operations.md`
reference (bundled in ai-maestro-plugin)
for the canonical list of which transitions require AMAMA's approval
and the AMP reply format (per R15.6, AMAMA may reply with direct AMP).
AMAMA's mutations (e.g. backburner→todo promotion, PRRD silver edits)
are inherently MANAGER-authorized — no separate approval is needed.
For GOLDEN PRRD rule changes, AMAMA relays to USER and applies the
user's decision via `prrd-edit.py --user`.

## Columns AMAMA owns

| Column | Ownership detail |
|---|---|
| `backburner` | AMAMA authors proto-TRDDs from user input. The TRDD frontmatter is minimal — `column: backburner`, `task-type:`, `title:`, `current-owner: amama`. Body is the user's request (paraphrased). |
| `todo` | AMAMA promotes the next proto-TRDD from backburner to todo when ready. After promotion, ORCHESTRATOR becomes responsible. |

AMAMA also touches `coordination fields` (`column:`, `assignee:`,
`priority:`) on any TRDD when needed — these are coordination overrides
that bypass `current-owner:` (per the schema).

## PRRD authority

| Operation | AMAMA can do? | Notes |
|---|---|---|
| Mutate silver rules (add / revise / delete) | YES | Direct via `prrd-edit.py` |
| Promote silver → golden | NO | USER-only. AMAMA relays the proposal to the user, then runs `prrd-edit.py --user promote N` IF the user authorises in writing. |
| Demote golden → silver | NO | USER-only. Same relay pattern. |
| Mutate golden rules | NO | USER-only. AMAMA refuses if a team agent proposes changing a golden rule; relays to user. |
| Review proposals from team agents | YES | Routed via COS. Decide accept / reject / forward-to-user. Update the proposal file's status. |

## Transitions AMAMA triggers

Per column-transitions.md row numbers:

- **#1** — `(new) → backburner` when user gives a new task request.
  Author the TRDD with proper UUID, timestamp, mandatory fields.
- **#2** — `backburner → todo` when MANAGER decides this is next-up.
  Bump `updated:`. AMP-send to COS: "TRDD-<id> promoted to todo".
- **#11** — `human_review → complete` / `→ dev` based on USER decision
  relayed via AMAMA.
- **#30** — `<any non-terminal> → failed` when USER decides to abandon.

For all other transitions, AMAMA does NOT directly mutate the TRDD —
the column owner does. AMAMA may be informed via AMP for visibility.

## Per-column checklists

### Authoring a proto-TRDD (column = backburner)

- [ ] Generate UUID:
      `UID=$(python3 -c "import uuid; print(uuid.uuid4())")`
- [ ] Capture timestamp `TS=$(date +%Y%m%d_%H%M%S%z)` and ISO datetime
- [ ] Create `design/tasks/TRDD-$TS-${UID:0:8}-<slug>.md`
- [ ] Fill mandatory frontmatter: `trdd-id`, `title`, `column:
      backburner`, `created:`, `updated:`, `current-owner: amama`,
      `task-type:` (best guess)
- [ ] Cite PRRD rules in `relevant-rules:` if the user mentioned constraints
- [ ] Body: paraphrase the user's request, mark unresolved questions
- [ ] Stage + commit: `git add design/tasks/<file>; git commit -m
      "docs: add TRDD-${UID:0:8} — <description>"`
- [ ] Add a TaskCreate entry with the short reference

### Promoting backburner → todo

- [ ] Pick the next proto-TRDD: highest-priority OR oldest
- [ ] Read its full body and frontmatter; confirm the user's intent
- [ ] Edit `column: todo`, bump `updated:`
- [ ] AMP-send to COS: "TRDD-<id> promoted to todo; please claim via ORCH"
- [ ] Note in `docs_dev/teams/team-registry.md` if delegating to a specific team

### Reviewing a PRRD proposal (received via COS)

- [ ] `findtrdd.py --grep <proposal-uid>` to find the proposal file
- [ ] Read the proposal body — rationale + proposed text
- [ ] Check whether the change is golden or silver
- [ ] If silver: decide accept (run `prrd-edit.py revise/add/delete`)
      OR reject (mark `status: rejected`, write rationale in body)
- [ ] If golden: relay to USER. Use the AMAMA-USER channel. Wait for
      response. Either run `prrd-edit.py --user <op>` (if approved) or
      mark the proposal rejected.
- [ ] AMP-reply to the proposing COS with the decision

### Relaying a USER decision back to a team

- [ ] If the user accepted a proposal: run the mutation, AMP-reply to
      COS with the accepted text
- [ ] If the user rejected: AMP-reply with the rationale (so the team
      learns)
- [ ] If the user requested changes to the proposal text: send back to
      proposing agent (via COS) so they can revise

## AMP message templates

```text
# Backburner → Todo promotion
Subject: TRDD-<id> promoted to todo
To: cos-<team>
Type: status_update
Body:
  TRDD-<id> "<title>" is now in todo. ORCH should claim it and
  delegate design to ARCHITECT. Priority: <pri>. Relevant rules:
  <rule-numbers>. Body: design/tasks/TRDD-<id>...md
```

```text
# Reviewing a proposal — accept (silver)
Subject: Re: Proposal <pid>
To: cos-<team>
Type: approval_decision
Body:
  Proposal <pid> accepted. PRRD updated: PRRD S<N>.<v> — "<new text>".
```

## Drift signals AMAMA handles

- `kanban.py --check-drift` may surface drift in any column.
- AMAMA's special concern is **backburner overflow** (>10 proto-TRDDs
  sitting unprompted). At that point, AMAMA queues a status report to
  the user: "10+ proto-TRDDs in backburner — recommend a quick triage".

## Resources

- Universal skill: `prrd-trdd-kanban` in `ai-maestro-plugin`
  (references/prrd-design-rules.md, references/trdd-design-tasks.md,
  references/column-transitions.md, references/trdd-frontmatter-schema.md)
- AMAMA persona: `agents/ai-maestro-assistant-manager-agent-main-agent.md`
- Other role layers (for delegation awareness): `amoa-prrd-trdd-kanban`
  (ORCH), `amaa-prrd-trdd-kanban` (ARCH), `amia-prrd-trdd-kanban` (INT),
  `ampa-prrd-trdd-kanban` (MEM), `amcos-prrd-trdd-kanban` (COS),
  `ai-maestro-autonomous-prrd-trdd-kanban` (AUTO),
  `maintainer-prrd-trdd-kanban` (MAINT)
