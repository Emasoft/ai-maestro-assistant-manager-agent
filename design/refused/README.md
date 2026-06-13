# `design/refused/` — declined proposals (terminal)

This zone holds **proposals that were NEVER approved** — declined at the
proposal gate. They are kept here (never deleted) as the audit record of
what was asked for and why it was refused.

A file lands here via the refusal protocol (see
`~/.claude/rules/trdd-approval-tiers.md`):

1. frontmatter `column: proposal` → `column: refused`, bump `updated:`;
2. append to the proposal's `## Approval log`:
   `- <ISO> — REFUSED by <approver> (tier <N>). <one-line reason>.`;
3. `git mv design/proposals/TRDD-….md design/refused/TRDD-….md`.

`refused` is terminal — re-attempting the idea means authoring a **new**
proposal in `design/proposals/` (which may cite the refused one).

**`design/refused/` is for never-approved proposals only.** Once-approved
TRDDs that later finish, are withdrawn, or are replaced go to
`design/archived/` instead.
