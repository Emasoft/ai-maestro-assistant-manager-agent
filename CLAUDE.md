# ai-maestro-assistant-manager-agent (AMAMA) — project instructions

AMAMA is the **MANAGER** role plugin of the AI Maestro fleet: the sole user interface and governance authority (3-pillars task system, approval tiers, fleet coordination).

## Memory — use the GLOBAL janitor-hosted system (proactively)

AMAMA uses the **global, user-level janitor memory system** — NOT a per-plugin one. The skills are `/janitor-memory-recall` · `/janitor-memory-write` · `/janitor-memory-update`; the protocol + recall law live in `~/.claude/rules/markdown-memory-recall.md`. Three scopes: **LOCAL** `~/.claude/projects/<slug>/memory/` (harness), **PROJECT** `<repo>/.claude/project/memory/` (git-tracked, this repo — bootstrapped), **USER** the janitor's fixed data dir.

### The proactive-use contract (applies to the main agent AND every sub-agent it spawns)
- **RECALL BEFORE ACTING** — before an approval decision, a recurring design decision, recommending a candidate, or acting on a recurring alert, run `/janitor-memory-recall` first, indexed by the **symptom** (the user's words / the question), across all 3 scopes. Unprompted.
- **WRITE / UPDATE AFTER LEARNING** — after a non-trivial decision or solved problem, capture it via `/janitor-memory-write` / `/janitor-memory-update` (clean-the-fact-in-place + demote-the-error-to-a-`[^N]`-lesson). Unprompted.
- **PROPAGATE** — when you spawn a sub-agent, include this same recall/write directive in its prompt. Memory discipline is inherited, not assumed.
- **SCOPE ROUTING** — machine-private → LOCAL; project-shared (no secrets) → PROJECT; cross-project → USER; UNSURE → LOCAL.

### MANAGER-role recall emphasis (what's highest-value for AMAMA)
For the MANAGER, the highest-value recalls are **confirmed user preferences** and **prior approval/governance decisions** — facts the user stated once and expects you to remember. AMAMA's workhorse note `type` is **`feedback`** (a confirmed preference + its **Why** / **How to apply**): e.g. merge-strategy choices, "escalate all prod deploys", "don't over-flag ToS on the owner's own accounts". Index by the QUESTION/symptom, never the answer's jargon.

### Janitor-dependency coupling (a ratified invariant)
The memory system depends on the **user-level `ai-maestro-janitor` plugin** — the ONLY plugin installed at USER scope (guardian of the whole install: global memory, cron/resume, auth/cookie refresh, marketplace upkeep, security scanning). **janitor-always-present** is a USER-ratified architecture decision; it is what makes "rely on the global janitor memory system" safe by construction. AMAMA ships no per-plugin memory skills — it relies on the janitor's global ones.
