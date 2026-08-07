---
trdd-id: G290DKHM
title: AMAMA script correctness review — fix CRITICAL mass-approve + HIGH id-collision + HIGH sidecar-orphan bugs
column: complete
created: 2026-06-25T06:24:48+0200
updated: 2026-06-25T07:01:23+0200
current-owner: amama
assignee: amama
priority: 1
severity: CRITICAL
effort: M
task-type: bugfix
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: publish
delivery: direct-push
target-branch: main
test-requirements: [unit, lint, typecheck]
review-requirements: [human-review]
impacts: []
external-refs: []
---

# TRDD-G290DKHM — AMAMA script correctness review (GOLDEN-RULE deep read)

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-06-25T06:24

**✅ CAMPAIGN COMPLETE — 14 AMAMA-specific scripts reviewed; 11 real bugs fixed across 8 scripts;
6 scripts CLEAN. Full suite 109 passed (98 prior + 11 new regression tests), ruff + mypy clean.**
See "CAMPAIGN TOTAL" near the end for the full per-batch breakdown + commit list. Batches: 1
(proposal_approvals + download), 2 (design_search + init_design), 3 (hooks), 4 (status reporters),
5 (foundational utils). All commits on `main`, UNPUSHED — ride the next publish.py pending USER
approval. The 11 fixes are pure correctness (no logic redesign); deferred design-flags are recorded,
none are observed bugs.
Trigger: USER challenge "why are you not working??" → `/go-on-yourself` in-control improvement.
A fresh-eyes correctness review of AMAMA's two most complex AMAMA-specific scripts (delegated to
two parallel Opus reviewers, GOLDEN-RULE whole-file read; findings verified by me against the
actual diffs before landing). NOT cosmetic — all three are real correctness/governance/data-integrity
bugs that the existing test suite did not catch.

### Fixed (each: real bug, fail-before/pass-after regression test, WHY comment at the change site)
1. **CRITICAL — `amama_proposal_approvals.py::build_plan` mass-approve via phantom complement.**
   In `refused:`-only batch mode, a stale/typo'd number whose id resolves to nothing
   (`decide --refused 99`) made `refuse_set & known` empty, so the complement `known - refuse_set`
   became the ENTIRE listing → every pending proposal silently APPROVED + moved to `design/tasks/`
   at rc=0. Fix: fail-fast — if not one refused number resolves, raise (rc=1, nothing moves). A mix
   of valid+unknown still proceeds (user named ≥1 real target). Test:
   `test_refused_only_all_unknown_does_not_mass_approve`.
2. **HIGH — `amama_proposal_approvals.py::find_in` short-id collision mis-route.** The 8-char short
   id is only a "casual" reference and CAN collide; `find_in` returned the first sorted match, so
   `cancel/archive --id <short>` could silently archive the WRONG TRDD. Fix: exact full-id wins;
   unique short resolves; >1 short raises `AmbiguousId` → `cmd_archive` surfaces it per-ident
   (rc=1, the rest of the batch still proceeds). Test:
   `test_ambiguous_short_id_does_not_misroute_archive`.
3. **HIGH — `amama_download.py` metadata sidecar orphaned on inner-`.md` filename.** Write side
   used `filename.replace('.md','')` (strips EVERY `.md`); read side uses `md_file.stem` (final
   suffix only). For a filename with `.md` mid-string (e.g. `--doc-type spec.md`) they disagreed →
   metadata orphaned → `lookup` silently returned `{}` AND `verify_storage` SKIPPED the SHA256
   integrity check (it lives in the `else` of the missing-metadata guard), so a tampered file passed
   verification undetected. Fix: write side uses `Path(filename).stem` (single source of truth with
   the read side). Test: `test_metadata_sidecar_name_matches_read_side_when_filename_has_inner_md`.

### Flagged items — RESOLVED / deferred
- **[HIGH] ✅ FIXED (commit 9d3523c)** — `lookup_documents` couldn't find docs in no-task-id
  categories (`specs`, `sync`): it matched a folder literally named `{task_id}`, but those categories
  store the id only in the metadata JSON.
- **[MEDIUM] ✅ FIXED (commit 9d3523c)** — `lookup_documents` missed `--subcategory` subfolders
  (non-recursive `glob("*.md")` vs `verify`'s `rglob`).
  → Both fixed by ONE coherent strategy: recursive `rglob("*.md")` per category + include a doc iff
  its metadata sidecar's `task_id` matches (subsumes both gaps, stays correct for task-id-path
  categories, agrees with `verify_storage`). 4 fail-before/pass-after tests.
- **[LOW] DEFERRED** — empty task folder left behind on download failure (cosmetic litter).
- **[NIT] DEFERRED** — `init_storage` `.gitignore` "already present?" coarse substring match.
  → Both deferred deliberately: negligible real-world impact; fixing now would be churn against
  `/go-on-yourself` "write only what is strictly necessary." Recorded here so they are not lost.

### Verification
`uv run --with pytest pytest tests/ -q` → **105 passed** (98 prior + 7 new regression tests).
`ruff check scripts/ tests/` → all passed. `mypy scripts/` → no issues (15 files). Reviewer reports:
`reports/amama-code-review/20260625_06*-{proposal-approvals,amama-download,download-lookup-fix}.md`
(gitignored).

### Gotcha re-encountered (and the lesson held)
The `while ls design/tasks/TRDD-*-$ID-*.md` collision idiom hung 8 min AGAIN (nullglob → `ls`
lists cwd → exit 0 → infinite loop) — the exact SVEILW09 gotcha. Re-confirmed: use
`while [ -n "$(find design/tasks -name "TRDD-*-$ID-*.md")" ]` for the create-time collision check.

## Batch 2 — next-largest scripts (design_search 444 LOC, init_design_folders 386 LOC)
Two more parallel Opus GOLDEN-RULE reviews; fixes verified against the diffs + full suite.
- **FIXED (LOW) `amama_design_search.py::extract_title_from_content`** (commit bbec046) — filename
  fallback used `filename.replace('.md','')` (strips EVERY `.md`) → corrupted the fallback title for a
  scanned file with an internal `.md` in its stem. Now `removesuffix('.md')`. Same class as the
  download sidecar bug. Test strengthened with the internal-`.md` case.
- **FIXED (MEDIUM) `amama_init_design_folders.py` `--platforms` dedup** (commit 5df63a5) — argparse
  `nargs='+'` repeats + out-of-first-position `shared` flowed verbatim into `index.yaml`
  (`['shared','web','web']`). Now `list(dict.fromkeys(['shared', *platforms]))` (order-preserving,
  shared-first); carries an explicit `results: dict[str, Any]` (a derived mypy regression the agent
  caught + fixed pre-ship). Regression test added.
- **Flagged (triaged, DEFERRED — recorded so not lost):** design_search FL1/FL2 (substring
  `uuid:`/`status:` key matching) are *theoretical* on AMAMA's v2 schema (it uses `trdd-id:`/
  `parent-trdd:`, not `uuid:`/`parent-uuid:`) → low priority; FL3 status-fall-through, FL4-FL8
  cosmetic/heuristic. init Finding 2 (`--force` clobbers index `documents`/`stats` — by-design per
  the flag's help; a backup/merge contract is a product call), Finding 3 (the structured-error model
  vs strict fail-fast — a whole-model decision), Finding 4 (dead `write_json_file` — NIT cleanup).
  None are observed correctness bugs; deferred per "write only what is strictly necessary."

## Batches 3-5 — hooks, status reporters, foundational utils (CAMPAIGN COMPLETE)
Extended the GOLDEN-RULE review to the rest of AMAMA's scripts.
- **Batch 3 (runtime-critical hooks)** commit 93e4d3c — `amama_stop_check` HIGH: valid-but-non-object
  JSON stdin (`5`/`[]`/`"x"`) crashed the Stop hook with an AttributeError traceback at the session
  boundary → coerce non-dict payload to `{}`. `amama_session_start` HIGH: `sys.stdin.read()` OSError
  (broken pipe/EIO) was uncaught → guard `(JSONDecodeError, OSError)` for parity with the sibling
  `amama_user_prompt_submit` (reviewed CLEAN). Hooks must be fail-SAFE at the boundary.
- **Batch 4 (status reporters)** commit 35bbfb0 — `amama_planning_status` + `amama_notify_agent`:
  both used `data.get(key, default)`, which only substitutes on an ABSENT key; a present-but-null
  YAML value (`modules:`) flowed `None` downstream and crashed (`len(None)`, `None[:54]`,
  `None.get(...)`, iterate-None). Coerced with `or`. `amama_approve_plan` + `amama_orchestration_status`
  reviewed CLEAN (C2 honesty-cleanup confirmed complete, no dangling refs).
- **Batch 5 (foundational utils)** — `amama_state_paths` + `amama_report_writer` reviewed CLEAN
  (no antipattern; C1 path-helper mismatch confirmed fixed). 2 design-flags DEFERRED: report_writer
  uses `project_root()` (worktree-vs-main-root — deliberate, fine for AMAMA's main-checkout usage),
  and same-second report filename clobber (acceptable for write-once throwaway reports).
  `amama_atomic_write` cleared incidentally by multiple reviewers ("sound"). `publish.py` excluded
  (canonical/CPV-owned — its AMAMA-specific addition `_sync_readme_version` is already tested).

### CAMPAIGN TOTAL
**14 AMAMA-specific scripts reviewed; 11 real bugs fixed across 8 scripts; 6 scripts CLEAN.**
A recurring antipattern surfaced 3× (`str.replace('.md','')` extension-strip → `Path().stem`/
`removesuffix`) and a 2nd recurring class (present-but-null YAML key crashing `.get(k,default)`
consumers, fixed via `or`). Full suite **109 passed** (98 prior + 11 new regression tests), ruff +
mypy clean throughout. 11 commits on `main` (unpushed): 9de61a6, 484fdc1, 9d3523c, bbec046, 5df63a5,
93e4d3c, 35bbfb0 + the TRDD-doc commits f54010c/a3fe248/5b6917a + (this one). All 6 review reports
in `reports/amama-code-review/` (gitignored). Deferred flags recorded above + in Batch 2 — none are
observed correctness bugs.

## Why this is in-control + safe
Pure correctness fixes to AMAMA's OWN scripts (no external dependency, no peer/USER gate). Each is a
real bug the suite missed, fixed fail-fast with a proven regression test and a WHY comment. Directly
serves `/go-on-yourself` ("identify shortcomings, base on facts, improve on real ground"). Reversible
(committed, not pushed — rides the next publish.py with the doc-sweep commits, pending USER approval).
