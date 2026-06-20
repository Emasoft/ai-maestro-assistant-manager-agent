# AMAMA tests

Tests for the ai-maestro-assistant-manager-agent (MANAGER) plugin.

Run the whole suite (what CI runs):

```bash
uv run --extra dev pytest tests/ -q
```

Every test file is **also** runnable standalone — it prints a unicode-bordered
result table (test · status · description) and exits 0 iff all pass:

```bash
uv run --extra dev python tests/test_amama_design_search.py
```

## Covered

All tests are **real, no-mock**: each builds throwaway tmp dirs / git repos, runs
the ACTUAL script functions or CLI, and asserts the real filesystem / stdout /
exit-code outcome. Template: `test_proposal_approvals.py`.

| Test file | Script under test | Focus |
|---|---|---|
| `test_proposal_approvals.py` | `amama_proposal_approvals.py` | proposal→approval lifecycle; `approved:`/`refused:` parsing; promote/refuse/archive |
| `test_amama_session_start.py` | `amama_session_start.py` | SessionStart hook: normal / subagent short-circuit / malformed stdin |
| `test_amama_user_prompt_submit.py` | `amama_user_prompt_submit.py` | UserPromptSubmit hook behavior |
| `test_amama_stop_check.py` | `amama_stop_check.py` | Stop hook: allow vs block on pending work / unread messages / open issues |
| `test_amama_notify_agent.py` | `amama_notify_agent.py` | frontmatter parse, session lookup, AMP-message argv + error paths |
| `test_amama_design_search.py` | `amama_design_search.py` | the 8 extract/parse/find functions over real markdown |
| `test_amama_init_design_folders.py` | `amama_init_design_folders.py` | folder scaffolding, seed files, idempotency |
| `test_amama_orchestration_status.py` | `amama_orchestration_status.py` | orchestration-status CLI |
| `test_amama_planning_status.py` | `amama_planning_status.py` | planning-status CLI |
| `test_amama_approve_plan.py` | `amama_approve_plan.py` | approve-plan command state changes |
| `test_amama_report_writer.py` | `amama_report_writer.py` | report file writing (path / timestamp / content) |
| `test_amama_download.py` | `amama_download.py` | URL/path/error logic + a real download via a local `127.0.0.1` `http.server` fixture (no internet, no mocks, server closed in `finally`) |

`scripts/publish.py` is exercised end-to-end by the publish pipeline, the strict
pre-push hook, and the CI gates — it is intentionally not unit-tested here (see
`design/tasks/TRDD-…a96d744d…` §Deferred).

## Memory

The memory system is **no longer per-plugin**. AMAMA uses the **global,
user-level janitor memory system** — `/janitor-memory-recall`,
`/janitor-memory-write`, `/janitor-memory-update` (from the `ai-maestro-janitor`
plugin); those skills are tested upstream in the janitor, not here. AMAMA's
memory contract (the proactive-use rules + the 3 scopes) lives in the repo
`CLAUDE.md` and the global rule `~/.claude/rules/markdown-memory-recall.md`.
