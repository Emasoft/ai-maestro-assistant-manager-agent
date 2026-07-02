---
trdd-id: FR9K2XQ7
title: Fleet role-agent governance + 3-pillars readiness audit — 7 issues filed
column: dev
created: 2026-07-02T05:59:19+0200
updated: 2026-07-02T05:59:19+0200
current-owner: amama
assignee: amama
priority: 1
severity: HIGH
effort: L
task-type: infra
parent-trdd: f5883dcc-3ee0-4335-85cb-c2aa12fe9b9e
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: none
review-requirements: []
labels: [fleet, governance, 3-pillars, readiness]
external-refs: ["github.com/Emasoft/ai-maestro-chief-of-staff/issues/24", "github.com/Emasoft/ai-maestro-orchestrator-agent/issues/25", "github.com/Emasoft/ai-maestro-architect-agent/issues/24", "github.com/Emasoft/ai-maestro-integrator-agent/issues/21", "github.com/Emasoft/ai-maestro-programmer-agent/issues/25", "github.com/Emasoft/ai-maestro-autonomous-agent/issues/12", "github.com/Emasoft/ai-maestro-maintainer-agent/issues/18"]
---

# TRDD-FR9K2XQ7 — Fleet role-agent governance + 3-pillars readiness audit

## ⏵ STATE — READ THIS FIRST ON RESUME — 2026-07-02

**✅ AUDIT + ISSUES FILED 2026-07-02** (USER directive: "scan other plugins … open issues on their github repo with precise instructions"). Audited all 7 non-AMAMA role-agent plugins (read-only, one Opus agent per plugin) against a governance + 3-pillars readiness rubric, then filed a precise, self-contained issue on each repo (serial gh writes, G1.1 sanity-gated, dedup-checked, zero repo-file edits). **Every plugin is NOT-READY.**

| Plugin | Verdict (C/H/M) | Issue |
|---|---|---|
| chief-of-staff | 0/3/5 | #24 (new) |
| orchestrator | 1/2/3 | #25 (new) |
| architect | 0/3/1 | #24 (new) |
| integrator | 3/2/2 | #21 (new) |
| programmer | 0/1/3 | #25 (new) |
| autonomous | 0/1/1 | #12 (comment) |
| maintainer | 0/2/1 | #18 (comment) |

**UNIFORM DRIFT (the fleet-wide gap — per-plugin detail is in each issue + report):**
1. All operate the 3 pillars via LOCAL skills (`amia-*`/`amoa-*`/…) instead of the core `ama-*` granular skills — the redundancy the standard forbids ([[f5883dcc]] A1/A4).
2. The G1.1 self-id line is ABSENT from GitHub-writing templates fleet-wide (impersonation risk under the shared @Emasoft identity).
3. Sub-agents lack their own proactive-3-pillars block (sub-agents inherit nothing).
4. Approval-tier self-classification lives only in main agents, not the executing sub-agents.
(AMAMA = the exemplar, already wired → excluded from the audit set.)

**NEXT ACTION:** monitor the 7 issues; each plugin's Claude executes on wake; MANAGER verify-ack on each plugin's release (the durable gate). This is Phase B fleet-wiring of f5883dcc plus the role-plugin-audit half of #24.

**Durable artifacts:** per-plugin audit reports at `reports/fleet-readiness/20260702_*.md` (gitignored). Filed by the serial filing agent 2026-07-02.

## Rubric (what "ready" means)
- **A. 3-pillars wiring** — main + every sub-agent use the core `ama-*` skills with the role's permission slice; no redundant local pillar skills.
- **B. Governance** — current `GOVERNANCE-RULES.md` cited; G1.1 in every gh-writing template; approval-tiers integrated (proposal→planned, folders); `governance-scenarios.md` present.
- **C. R23 decoupling** not regressed (no server `/api/*` or `~/.aimaestro/` I/O; `gh`/GitHub-API fine).
- **D. R24** proactive memory-recall wired in main + sub.

## Relationships
- **parent** f5883dcc — 3-pillars Phase B (fleet wiring); this executes it via per-repo issues.
- **related** #24 (9a16554d role-plugin audit), #14 (governance propagation).
- **prior art** per-repo-decoupling-issues (R23 already ~complete fleet-wide; NOT re-filed here).

## Why
A team of role-agents not aligned with the pillars/governance would mis-classify approval tiers, bypass proposal gates, run redundant drifting skills, and post to GitHub with no self-id (impersonation under the shared identity). The audit turns that diffuse risk into a concrete, per-repo, fixable gap list.
