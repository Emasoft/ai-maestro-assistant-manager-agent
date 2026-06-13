---
name: amama-memory-write
description: Capture a durable, reusable fact as a markdown memory note so a future session recalls it from the SYMPTOM. Use after a confirmed user preference, an approval/governance decision worth remembering, a project constraint not derivable from code, or any "we should remember this" moment — or when the user says "remember this", "save a memory", "note that for next time", "from now on always X". Writes a schema-valid note (name/description/metadata + body) with the description indexed by question/symptom vocabulary, and appends the MEMORY.md index line. The AMAMA mirror of the AI-Maestro memory-write protocol (see the memory-protocol rule).
version: 2.9.1
compatibility: Requires AI Maestro installed. memgrep optional (degrades to grep).
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: true
---

# AMAMA Memory Write Skill

## Overview

Capture one durable fact as a memory note so a future session — which will have
the SYMPTOM, not the answer — can recall it. The load-bearing decision is the
`description`: it MUST carry the words the problem will present with (the user's
words, the question, the symptom), because recall ranks on `description`
(+ `title` + `tags`). Put the symptom in `description`; put the answer in the body.

For AMAMA the most valuable notes are **confirmed user preferences** (type
`feedback`) and **prior approval/governance decisions** (type `project` or
`feedback`). Only capture what is NON-OBVIOUS and reusable. Do NOT capture what
the repo already records (code structure, git history, CLAUDE.md, the PRRD) or
what only matters to the current conversation.

## Instructions

1. Resolve the memory dir (same as recall) and ensure it exists:

   ```bash
   MEMDIR="$HOME/.claude/projects/$(pwd | sed 's#/#-#g')/memory"
   [ -d "$MEMDIR" ] || MEMDIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)/memory"
   mkdir -p "$MEMDIR"
   ```

2. Choose `type` ∈ `user | feedback | project | reference` and a kebab slug
   prefixed with the type (e.g. `feedback_squash_merge_default`).

3. Check for an existing note that already covers this (update it rather than
   duplicate): use the `amama-memory-recall` skill with the symptom first, which
   runs the same gated recall — memgrep if present, grep otherwise:

   ```bash
   if command -v memgrep >/dev/null 2>&1; then
     memgrep recall "<symptom>" "$MEMDIR"        # found → update that note, don't duplicate
   else
     grep -rliE "<symptom>" "$MEMDIR" 2>/dev/null # fallback: degrade, never break
   fi
   ```

4. Write `"$MEMDIR/<type>_<slug>.md"` **with the Write tool (NOT echo)**, schema:

   ```yaml
   ---
   name: <type>_<slug>
   description: "<the SYMPTOM in the user's words — the words a future session will search with, NOT the answer's jargon>"
   metadata:
     node_type: memory
     type: <user|feedback|project|reference>
   ---
   <the one fact. For feedback/project, follow with **Why:** and **How to apply:**
   lines. Link related notes with [[their-name]].>
   ```

5. Append a one-line pointer to `"$MEMDIR/MEMORY.md"` (create if missing) **with
   the Write/Edit tool**: a markdown list item that links the note's **Title** to
   its `<type>_<slug>.md` filename (from step 4) and ends with ` — ` plus a
   one-line hook — i.e. the standard "dash, bracketed Title, parenthesised
   filename, em-dash, hook" bullet shape.

6. Sanity-check: would a future AMAMA session, having only the SYMPTOM, find this
   note by searching `description`? If the description reads like the *answer*,
   rewrite it to read like the *question*.

## Correcting a memory — the 2-step non-destructive protocol

When a new discovery CONTRADICTS an existing memory, change the memory
non-destructively, in two steps (mirrors the Bug-Autopsy directive + RULE 0):

1. **Clean the fact in place.** Replace the wrong statement in the body with the
   correct one — the body is the current truth, no "we used to think X" clutter.
2. **Demote the error to a lesson — the WHY is the point.** Record the error that
   caused the false memory as a **numbered footnote** in a `## Notes and lessons
   learned` section at the BOTTOM, and link the corrected fact to it with a
   standard-markdown footnote `[^N]`. The load-bearing content is *why* the
   previous statement was wrong — the root cause, so the next session does not
   repeat it.

## Output

One note file + one MEMORY.md index line. Report the note path and the one-line
description; do NOT echo the whole note back into the conversation.

## Examples

```text
User: from now on, always escalate production deploys to me — never auto-approve
  → type: feedback
    description: "prod deploy approval — should I auto-approve or escalate to the user"
    body: "Always escalate production deploys to the user; never auto-approve."
          **Why:** user wants final say on irreversible prod changes.
          **How to apply:** on a COS prod-deploy approval request, escalate-to-user.

User: remember automating my own paid Claude accounts is fine, don't over-flag ToS
  → type: feedback; description carries "is it ok to automate / rotate my own Claude accounts".
```

A corrected note (2-step protocol — fact clean in the body, error demoted to a
dated `[^2]` lesson with the WHY):

```markdown
---
name: feedback_merge_strategy_default
description: "which merge strategy did the user pick for the team / squash or merge"
metadata:
  node_type: memory
  type: feedback
---
The user wants **squash-merge** as the default for all teams.[^2]

## Notes and lessons learned
[^2]: [ocd:2026-06-09 lmd:2026-06-09] earlier this said "merge-commit" — wrong.
  The error: I read the strategy off a stale PR template instead of the user's
  stated preference. Lesson: a user preference comes from the user's words, not
  a repo default.
```

## Scope

ONLY authors/updates memory notes + the MEMORY.md index. Does NOT recall (use
`amama-memory-recall`). One fact per note. Symptom-indexed `description` is
mandatory — it is what makes the note recallable.

## Resources

- `rules/memory-protocol.md` — the AMAMA protocol (the law, the schema, the
  lessons-learned conventions, the dual-test method).
- `skills/amama-memory-recall/SKILL.md` — the RECALL side (find a note before you
  duplicate or correct it).
- `~/.claude/rules/markdown-memory-recall.md` — the canonical AI-Maestro protocol.
- The harness `# Memory` directive — the authoring source-of-truth this skill
  follows.
