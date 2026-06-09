# Markdown memory — recall protocol (AMAMA)

This rule is the AMAMA-parameterized mirror of the canonical AI-Maestro
protocol `~/.claude/rules/markdown-memory-recall.md`. It is the **recall**
half of the memory system: how the **ASSISTANT-MANAGER (AMAMA)** agent
RECALLS durable project memories, the **discipline** that makes recall work,
and the **tool** (`memgrep`) that powers it. The harness `# Memory` directive
(injected each session) is the **write** half; this rule is the read half.

Together they are "the memory system": authoring (directive + the
`amama-memory-write` skill) + recall (this rule + the `amama-memory-recall`
skill) + the search tool (memgrep) + the note corpus.

## The one law that makes memory work: index by the QUESTION, not the answer

A memory is found from the SYMPTOM, not the solution. When you write a note,
its `description:` (and `title`/`tags`) MUST carry the words a future session
will have when the problem RECURS — the user's words, the error text, the
symptom, the *question* — NOT the jargon of the fix.

- WRONG `description`: "user prefers squash-merge on the inventory team".
  (Findable only if you already know the answer is "squash".)
- RIGHT `description`: "which merge strategy did the user pick / how should I
  set merge-strategy for this team" + the squash-merge fact in the BODY.

Two-hop recall: a symptom query lands you on the note; the note's BODY gives the
answer. The `description` is the load-bearing surface — `memgrep recall` ranks
on `description + title + tags` ONLY (the `metadata.type` taxonomy does NOT
affect ranking). Put symptom vocabulary in `description`; put the answer in the
body.

## Recall BEFORE acting (the protocol)

Before making an approval decision, recommending a team or COS candidate,
re-deriving a prior decision, or acting on a recurring request, RECALL first —
"have we hit this before? did the user already tell me their preference?".
Cheap, and it is the whole point of having a memory. For AMAMA, the highest-value
recalls are **confirmed user preferences** and **prior approval/governance
decisions** — facts the user stated once and expects you to remember.

```bash
# memdir is the harness per-project memory dir (slug = project path, dashed):
MEMDIR="$HOME/.claude/projects/$(pwd | sed 's#/#-#g')/memory"
# Fallback to a project-local memory/ dir when the harness dir is absent:
[ -d "$MEMDIR" ] || MEMDIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)/memory"
SYMPTOM="the user's words / the question / the symptom"   # NOT the answer's jargon

if command -v memgrep >/dev/null 2>&1; then
  memgrep recall "$SYMPTOM" "$MEMDIR"      # notes ranked best-first as: path — description
else
  grep -rliE "$SYMPTOM" "$MEMDIR"          # fallback: plain grep, degrade-not-break
fi
```

Read the top 1-3 notes the recall returns; the answer is in their bodies. If
recall returns nothing, the memory does not exist yet — make the decision, then
write a note (via the `amama-memory-write` skill / the harness `# Memory`
directive) so the next session recalls it from the symptom.

## The note schema (recall-relevant fields)

The harness `# Memory` directive is the authoring source-of-truth. On disk, a
note is one markdown file `$MEMDIR/<type>_<slug>.md`:

```yaml
---
name: <type>_<slug>                # == filename stem
description: "<symptom surface — the load-bearing recall field>"
metadata:
  node_type: memory
  type: user | feedback | project | reference
---
<body: the one fact. For feedback/project, follow with **Why:** and
**How to apply:** lines. Link related notes with [[their-name]].>
```

- `type: user` — a fact about the user (identity, contact, timezone).
- `type: feedback` — a confirmed user preference / correction (add **Why:** /
  **How to apply:**). The AMAMA workhorse: "always squash-merge", "escalate all
  prod deploys", "don't over-flag ToS on my own accounts".
- `type: project` — a project constraint not derivable from code (add **Why:** /
  **How to apply:**).
- `type: reference` — a hard-won technical fact / gotcha (API quirk, a command
  that works, a trap that wasted time).

`MEMORY.md` (in `$MEMDIR`) is the human index — one line per note,
`- [Title](file.md) — one-line hook.` — loaded each session. `memgrep index`
can generate a richer `memory-index.md`; that is an OPTIONAL generated artifact,
`MEMORY.md` remains the canonical loaded index. Recall does not need either
index — it scans the notes directly.

## memgrep — the recall engine (cross-repo, optional)

`memgrep` is `rg` for markdown (gitignore-aware tree walk, per-line regex,
markdown-structural filters, boolean `--where`, and the memory subcommands
`recall`/`index`/`links`/`fact`). It ranks notes by how well a SYMPTOM query
hits each note's `description + title + tags`.

- **memgrep is NOT bundled in this plugin.** It lives in the **ai-maestro-janitor**
  repo (`ai-maestro-janitor/tools/memgrep`). This plugin's skills MUST gate on
  `command -v memgrep` and fall back to `grep`, so recall **degrades, never
  breaks**. Do NOT point installers at this plugin's own root — memgrep is not
  shipped under it; install it from ai-maestro-janitor (below).
- **Install (once, if you have the janitor repo checked out):**
  `cargo install --path <ai-maestro-janitor>/tools/memgrep` (puts the binary on
  `~/.cargo/bin`). Until then, the plain-`grep` fallback works on note
  frontmatter + bodies.
- **recall:** `memgrep recall "SYMPTOM" <memdir>` — symptom-ranked notes,
  precision-first (surface matches suppress body-only matches unless nothing
  matched the surface), printed `path — description`, best first.

## The dual-test method (evaluating / improving recall)

When designing or testing memory recall, run BOTH tests and judge BOTH
dimensions (your search strategy AND the system's retrieval) in each:

- **Test A — cold-recall:** simulate a session with NO prior recollection; build
  the query ONLY from the symptom/user's words, never the answer's jargon. Tests
  "is the right note findable from the symptom?".
- **Test B — write-then-recall:** author a note, then retrieve it. Tests the
  round-trip.

**Contamination warning:** after you WRITE a note you are biased toward its
wording — your own cold-recall is no longer cold. Do cold-recall from a clean
framing, or have the symptom come from the user verbatim.

## Why this rule exists

A fresh AMAMA session is blind to the note corpus even when the answer (a user
preference, a prior decision) was written down last week — unless a standing
rule makes "recall before acting" and "index by symptom" a discipline. This rule
is that discipline, parameterized for the MANAGER role, with a tool command that
degrades to grep when the binary is not present.
