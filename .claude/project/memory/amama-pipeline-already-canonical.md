---
name: amama-pipeline-already-canonical
description: "should I upgrade AMAMA's CI/publish pipeline to the CPV canon / RC-PIPELINE-DRIFT WARNINGs on publish --dry-run / is cpv-upgrade-plugin --force-templates safe here / is the pipeline missing SBOM / provenance / SHA-pinning / SHA256SUMS / what is task #22 for AMAMA"
ocd: 2026-07-17
lmd: 2026-08-18
publish-globally: false
metadata:
  node_type: memory
  type: reference
  tier: component
---

# AMAMA's pipeline is ALREADY at full canonical hardening — do NOT force-migrate

Verified 2026-07-17 (reading the actual `.github/workflows/*.yml` lines, not a grep). [^1]

- **ci.yml**: every `uses:` SHA-pinned ✓ + actionlint ✓ + commitlint ✓ + macOS matrix ✓ + per-job `timeout-minutes` ✓.
- **release.yml**: SHA-pinned ✓ + **SBOM** (`anchore/sbom-action`, SPDX) ✓ + **build-provenance** (`actions/attest-build-provenance`, OIDC `id-token: write`) ✓ + **per-asset SHA256SUMS** ✓ — all landed under **issue #121**.
- **notify-marketplace.yml**: SHA-pinned ✓.

So the whole "genuine new canon" a CPV RC-PIPELINE-DRIFT WARNING advertises (SBOM / provenance / SHA256SUMS / SHA-pins / actionlint / commitlint / macOS matrix / timeouts) is **already present**. Board task **#22's pipeline-*hardening* premise is a NO-OP for AMAMA** (#22's live scope is the separate dependency-**resolver-tag** blocking flip, gated on CPV's `cpv.pipeline` durability answer — a different concern).

**The RC-PIPELINE-DRIFT WARNINGs that remain are NOT hardening gaps:**
- `publish.py` + `ci.yml`: **BY DESIGN** for the `remote-validation` pipeline profile — CPV's own finding says *do NOT run `--force-templates`*, it would re-vendor the validators the plugin deliberately removed. The profile is a SELECTOR, not a suppressor (TRDD-02e1672b).
- `release.yml` / `notify-marketplace.yml` / `.markdownlint.json`: cosmetic template-shape drift (e.g. the intentional `MD025 front_matter_title` rule).

**Bottom line:** these WARNINGs are advisory and non-blocking; the strict gate passes at **NIT=0** without touching them (see [[strict-publish-gate-nit-was-a-prose-plus]]). Forcing a template migration would DOWNGRADE the by-design architecture for zero security gain. Leave the pipeline as-is.

## Notes and lessons learned

[^1]: [id:ATOM-GREP-E-LITERAL-BRACE-PIPE, status:valid, keywords:"grep found zero hits but the thing is present, my own grep lied about SHA pinning, verify before fixing pipeline drift, ERE interval and alternation escaping", ocd:2026-07-17, lmd:2026-07-17]
  DO NOT trust a `grep -E` count when the pattern uses `\{40\}` or `a\|b`, BECAUSE in
  ERE the backslash makes `{40}` and `|` LITERAL — so `uses:.*@[0-9a-f]\{40\}` and
  `sbom\|SBOM` both matched nothing and falsely reported "0 SHA-pins, 0 SBOM", nearly
  triggering a needless (and downgrading) pipeline migration. DO write `{40}` and `|`
  with NO backslash under `-E` (or `\{40\}`/`\|` only under BRE), and READ the actual
  lines to confirm a "0 hits" before acting on it. Same class as the gh-404-to-stdout
  and tee-truncation traps: verify the tool, not just its output.
