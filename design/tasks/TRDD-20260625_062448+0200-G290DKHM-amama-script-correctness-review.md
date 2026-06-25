---
trdd-id: G290DKHM
title: AMAMA script correctness review — fix CRITICAL mass-approve + HIGH id-collision + HIGH sidecar-orphan bugs
column: complete
created: 2026-06-25T06:24:48+0200
updated: 2026-06-25T06:42:32+0200
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

**✅ EXECUTED + VERIFIED — 7 real bugs fixed across 4 scripts, full suite green (106 passed),
ruff + mypy clean.** Batch 1 (the 5 below): 9de61a6 (approvals), 484fdc1 + 9d3523c (download),
f54010c + a3fe248 (this TRDD). Batch 2 (2 more, see "Batch 2" section): bbec046 (design-search),
5df63a5 (init-design). All on `main`, unpushed — ride the next publish.py pending USER approval.
Review reports (gitignored): `reports/amama-code-review/20260625_06*.md` (5 files).
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

## Why this is in-control + safe
Pure correctness fixes to AMAMA's OWN scripts (no external dependency, no peer/USER gate). Each is a
real bug the suite missed, fixed fail-fast with a proven regression test and a WHY comment. Directly
serves `/go-on-yourself` ("identify shortcomings, base on facts, improve on real ground"). Reversible
(committed, not pushed — rides the next publish.py with the doc-sweep commits, pending USER approval).
