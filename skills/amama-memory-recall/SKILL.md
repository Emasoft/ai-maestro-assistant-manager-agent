---
name: amama-memory-recall
description: Recall durable project memories from a SYMPTOM before deciding, approving, recommending, or re-deriving a prior decision. Searches the project's markdown memory notes with memgrep (degrading to plain grep when memgrep is absent), ranking notes by how well your symptom query hits each note's description/title/tags, and returns the top notes to read. Use when you think "have we hit this before?" or "did the user already tell me their preference?", or the user says "recall memories about X", "did we already decide this", "search the memory notes", "what did we learn about Y". Read-only. The AMAMA mirror of the AI-Maestro memory-recall protocol (see the memory-protocol rule).
compatibility: Requires AI Maestro installed. memgrep optional (degrades to grep).
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: true
---

# AMAMA Memory Recall Skill

## Overview

Recall is the FIRST step before making an approval decision, recommending a team
or COS candidate, re-deriving a prior decision, or acting on a recurring request
— "have we hit this before? did the user already state a preference?". It
searches the project's curated markdown memory notes (the harness per-project
`memory/` dir) and returns the notes whose `description`/`title`/`tags` best
match your SYMPTOM. The answer is in the matched note's body.

For AMAMA the highest-value recalls are **confirmed user preferences** and
**prior approval/governance decisions**. This is distinct from
conversation/transcript search: it recalls *curated, symptom-indexed notes*, not
raw chat history.

## The one law

Query with the SYMPTOM — the user's words, the question, the problem — NOT the
answer's jargon. A note is findable from the symptom because its author put
symptom vocabulary in `description`. (Query "squash" and you find the
merge-strategy note only once you already know the answer; query "which merge
strategy did the user pick" and you find it from the question.)

## Instructions

1. Resolve the project memory dir (the harness per-project notes dir, with a
   project-local fallback):

   ```bash
   MEMDIR="$HOME/.claude/projects/$(pwd | sed 's#/#-#g')/memory"
   [ -d "$MEMDIR" ] || MEMDIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)/memory"
   ```

2. Build a SYMPTOM query from the user's words / the question / the problem
   (never the answer's jargon), then recall — memgrep if present, plain grep
   otherwise:

   ```bash
   SYMPTOM="the symptom in the user's / the error's words"
   if command -v memgrep >/dev/null 2>&1; then
     memgrep recall "$SYMPTOM" "$MEMDIR"        # notes ranked best-first: path — description
   else
     grep -rliE "$SYMPTOM" "$MEMDIR" 2>/dev/null # fallback: degrade, never break
   fi
   ```

   `memgrep` is NOT bundled in this plugin — it lives in **ai-maestro-janitor**.
   If absent and you have that repo checked out, install once:
   `cargo install --path <ai-maestro-janitor>/tools/memgrep`. Until then the grep
   fallback works on note frontmatter + bodies. Do NOT expect memgrep under this
   plugin's own root — it is not shipped here; install it from ai-maestro-janitor.

3. Read the top 1-3 notes the recall returns; the fact you need is in their
   bodies. If recall returns nothing, the memory does not exist yet — make the
   decision, then capture it with the `amama-memory-write` skill.

## Output

A short ranked list of `path — description` lines (memgrep) or matching paths
(grep fallback), best first. Read the top few; do NOT dump full note bodies into
the conversation — open the one you need.

## Examples

<example>
User: which merge strategy should this team use again?
→ recall "which merge strategy did the user pick for this team" → surfaces the
  feedback note whose body says "always squash-merge"; apply it without re-asking.
</example>

<example>
User: the COS is requesting a prod deploy approval
→ recall "prod deploy approval user preference escalate" → surfaces the feedback
  note "always escalate production deploys to the user" → escalate per the note.
</example>

```text
User: have we already decided how to handle cross-host governance requests?
User: did the user tell me their timezone / when they're usually available?
User: check the memory notes about what we approved for the inventory team
```

## Scope

ONLY searches + surfaces existing memory notes (read-only). Does NOT write notes
(use `amama-memory-write`). Does NOT search chat transcripts. Degrades to plain
grep when memgrep is absent; never blocks on a missing binary.

## Resources

- `rules/memory-protocol.md` — the AMAMA recall protocol (the one law, the note
  schema, the dual-test method).
- `skills/amama-memory-write/SKILL.md` — the WRITE side (authoring a note).
- `~/.claude/rules/markdown-memory-recall.md` — the canonical AI-Maestro protocol
  this skill mirrors.
- memgrep lives in `ai-maestro-janitor/tools/memgrep` (its own `SKILL.md` is the
  tool reference) — install via `cargo install --path <janitor>/tools/memgrep`.
