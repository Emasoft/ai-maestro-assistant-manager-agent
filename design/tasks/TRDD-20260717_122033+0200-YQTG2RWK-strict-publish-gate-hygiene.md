---
trdd-id: YQTG2RWK
title: AMAMA strict-publish-gate hygiene — clear the NIT blocker + flagged warnings
column: dev
created: 2026-07-17T12:20:33+0200
updated: 2026-07-17T12:20:33+0200
current-owner: amama
assignee: amama
priority: 2
severity: LOW
effort: S
task-type: infra
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: none
delivery: direct-push
target-branch: main
test-requirements: [publish.py --patch --dry-run passes strict gate]
review-requirements: []
impacts: []
external-refs: []
---

# TRDD-YQTG2RWK — AMAMA strict-publish-gate hygiene

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-07-17

**Trigger:** `/go-on-yourself` (USER, 2026-07-17). Assessed AMAMA on real ground:
tests 140/140 GREEN, but `publish.py --patch --dry-run` FAILS strict (exit 4) on
**NIT=1** plus 18 advisory WARNINGs. This TRDD clears the blocker + the low-risk
hygiene; the two judgment items are deferred (documented below), not swept.

**SCOPE (this turn) — 3 verified low-risk fixes:**
1. **NIT blocker** (the only `--strict` blocker): markdownlint MD004/ul-style in
   `design/tasks/TRDD-*QMY8VR0D*.md` L78. The `+` is a **prose conjunction** on a
   hard-wrapped line (`Both CORE pins` / `+ the USER …`), which MD004 misreads as a
   `+`-marker list item (issue #113). FIX = move the `+` to the end of the prior
   line — pure reflow, zero meaning change. File is `column: dev` (editable).
2. **3 scripts shebang-but-not-executable** → `chmod +x amama_state_paths.py
   amama_append_log.py amama_atomic_write.py`.
3. **README** hygiene: add `text` language tag to the 2 untagged fences (ASCII arch
   diagram + dir tree) and add a `## Usage` section (validator wants `## Usage`/
   `## Examples`/`## How to Use`; README only had `### Commands`/`### Skills`).

**DEFERRED — verified NOT to sweep (integrate/verify, don't delete):**
- **report-generator.md 4 unknown frontmatter fields** (`type`,`trigger_conditions`,
  `auto_skills`,`memory_requirements`): grep shows ZERO readers → inert to the CLI,
  BUT may be fleet-schema intent. Non-blocking (WARNING). Verify against the server
  schema / sibling role plugins before removing. Not this turn.
- **RC-PIPELINE-DRIFT (5 files)**: publish.py + ci.yml drift is **BY DESIGN** for the
  `remote-validation` profile — CPV's own finding says do NOT `--force-templates`.
  release.yml/notify-marketplace.yml/.markdownlint.json carry GENUINE new canon
  (SBOM, build-provenance, per-asset SHA256SUMS, actionlint/commitlint, macOS matrix)
  worth SELECTIVE adoption — that is board **#22** (MANAGER-directed pipeline upgrade),
  its own TRDD, higher blast-radius (`.github/`). Not swept here.

**NEXT ACTION:** apply the 3 fixes → re-run `--dry-run` (expect NIT=0, 3 fewer
WARNINGs) → CHANGELOG → commit. Publish stays USER-gated (21 commits already ahead).

**ACCEPTANCE:** `uv run python scripts/publish.py --patch --dry-run` reaches the
strict gate with NIT=0 (the `remote-validation` by-design WARNINGs may remain — they
are advisory selectors, not blockers).

## Notes and lessons learned

(none yet)
