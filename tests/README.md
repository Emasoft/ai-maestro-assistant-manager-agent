# AMAMA tests

Tests for the ai-maestro-assistant-manager-agent (MANAGER) plugin. Run with:

```bash
uv run --with pytest pytest tests/ -x -q
```

## Covered

- `test_proposal_approvals.py` — the proposal→approval lifecycle
  (`scripts/amama_proposal_approvals.py`): listing proposals, the
  `approved:` / `refused:` decision parsing, and the
  promote / refuse / archive transitions.

## Memory

The memory system is **no longer per-plugin**. AMAMA uses the **global,
user-level janitor memory system** — `/janitor-memory-recall`,
`/janitor-memory-write`, `/janitor-memory-update` (from the `ai-maestro-janitor`
plugin); those skills are tested upstream in the janitor, not here. AMAMA's
memory contract (the proactive-use rules + the 3 scopes) lives in the repo
`CLAUDE.md` and the global rule `~/.claude/rules/markdown-memory-recall.md`.
