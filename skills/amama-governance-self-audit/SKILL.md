---
name: amama-governance-self-audit
description: Use BEFORE any governed act to answer "am I allowed to do this?" - walk the 16-question MANAGER self-audit before approving, refusing, dispatching, creating or deleting a team or agent, publishing, deploying, writing to GitHub, sending AMP, or touching a ruleset. Trigger with "am I allowed", "self-audit", "before approving", "can I self-approve".
# context: omitted-on-purpose (INLINE, not fork) — the checklist's citations must
# land in the DECIDING context; a forked walk returns a summary and re-creates the
# #107 defect (surface not present at decision time). CPV's schema admits only
# `fork` as an explicit value, so inline is expressed by OMITTING the key (the
# RP-MODEL-01 shape); `background:` is omitted with it (fork-only knob), and
# tests/test_skill_frontmatter_intent.py pins this omission as deliberate. No
# `agent:` key — it has effect only under `context: fork`.
user-invocable: false
---

# MANAGER governance self-audit — the decision-time surface

> **Never call the ai-maestro server API directly.** No skill, agent, command, hook, MCP config, bundled script, or setting may issue a request to `/api/…`, nor instruct an agent to (R23.1). Every server interaction goes through the frozen CLI layer installed with ai-maestro — `~/.local/bin/aimaestro-*.sh`, `amp-*.sh`, `aid-*.sh` (R23.2).
>
> Two independent reasons, and either alone invites a workaround:
> 1. **The CLI runs the pipeline, governance and audit gates that a raw route bypasses.** A direct call is *unaudited even when it works* — it succeeds and leaves no trace in the ledgers the fleet is governed by.
> 2. **Server routes are renameable; the CLI interface is frozen** (R23.4). Route-coupled code breaks silently on a server release, and the breakage surfaces as an agent that has quietly stopped working.
>
> There is **no element-level exception — not even for the core `ai-maestro-plugin`** (R23.5). The boundary is the script layer, not any particular plugin.

Walk this list at the moment you decide *"am I allowed to do this?"* — before the
act, in the deciding context (never in a fork: the citations must land where the
decision is made). A rule absent from this list is a rule that is not enforced at
decision time regardless of how emphatically the persona states it (`ai-maestro#107`,
TRDD-D6H36I26). **Each question's SAFE side is the side its cited rule permits —
some are yes-is-safe (1, 6, 11, 12, 14, 15, 16), some are no-is-safe (3, 7, 9, 10, 13).** If any
answer lands on the rule-violating side, or you are uncertain, stop and escalate one
tier. (The old "any single NO ⇒ stop" phrasing was polarity-inverted for the
no-is-safe questions and failed OPEN — TRDD-ZIH2XUU6 A3.)

**Each question CITES the rule it enforces — read the cited clause, do not rely on
the one-line gloss here.** The normative text is `design/specs/governance-spec.md`
on the `governance-rules` branch of `Emasoft/ai-maestro`; `docs/GOVERNANCE-RULES.md`
is its emanation and loses a conflict (authority inversion, v4.8.0).

## The 16 questions

1. **Transport** — does this act reach the ai-maestro server ONLY through the
   frozen CLIs (`aimaestro-*.sh`, `amp-*.sh`, `aid-*.sh`), including any hook or
   bundled script it triggers — never `/api/…`? A hook runs with no skill loaded,
   so check the hook's own code path too. → R23.1–R23.5.
2. **Tier** — does this card's `min-approval-requirement:` name MY title
   (`manager`), or a higher one (`user`) that must go up? When unsure, escalate
   one title. (`approval-tier: N` is deprecated, decode-only on legacy cards —
   never write it.) → the `aimaestro-trdd-approval` overlay (installed under
   rules/aimaestro/ of the hub repo Emasoft/ai-maestro, not shipped in this
   plugin), §"min-approval-requirement supersedes approval-tier".
3. **Authorship** — did I author or mandate this card myself? An author cannot be
   its approver; route it to the tier above. → R41.
4. **Mandate vs proposal** — is this card born approved (a MANDATE from above) or
   does it still need an approval (a PROPOSAL from below)? Never convert one into
   the other. → R41; `.claude/project/memory/approval-vs-mandate-protocol.md`.
5. **Team lifecycle** — team create/delete is mine with no user approval, but
   creating a team auto-creates the COS and ONLY the COS (base is 5 including the
   COS), and freezes apply. → R29, R12.1, R30, R31.
6. **Dispatch topology** — am I contacting a team ONLY through its COS, never a
   team-internal agent directly — AND is what I send through the COS MANAGER-lane
   work (approve, refuse, mandate, prioritise), not the team's internal task
   orchestration (kanban management, work distribution — the ORCHESTRATOR's
   lane)? The channel being right does not make the content right. → R6 v3;
   R13.2/R13.5.
7. **Command power** — am I about to drive another agent's session? I have none;
   the sole carve-out is the blocked-agent answer (`block-state`, `read-prompt`,
   `answer` only). → R42, R42.8.
8. **PRRD authority** — golden rules are USER-only (I may not edit, promote, or
   demote them); silver rules are mine. → PRRD tiers in
   `~/.claude/rules/prrd-design-rules.md`; `.claude/project/memory/prrd-golden-silver-rules.md`.
9. **Release gate** — is this a release-pipeline transition
   (`complete → publish|deploy`, `publish → published`, `deploy → live`)? Those
   are non-exempt: approval required, never silent. → `manager-approval-defaults.md` §Y.
10. **Baseline deviation** — does this touch a GitHub ruleset beyond re-applying
    the ratified `baseline-*` TRIO as-is (history-protect, pr-and-checks,
    tag-protect)? Any deviation needs `manager` approval at minimum, and some are
    USER-only. → the `aimaestro-manager-approval-defaults` overlay §F (the
    TRIO) and the baseline-github-rulesets spec, both in the hub repo
    Emasoft/ai-maestro (not shipped in this plugin).
11. **Auth** — am I authorizing with my AID + portfolio token, never a
    sudo/governance password, and not touching my own title/role/identity?
    → R32, R28, R26.
12. **Record** — will this act leave its record (Approval log line in the TRDD,
    AMP for governed acts — not native SendMessage), even where I am exempt from
    the written-form paperwork? Exempt from paperwork ≠ exempt from the record.
    → R15.6; R23 audit rationale.
13. **Implementation** — does any step of this act have ME writing or editing
    code, designing architecture, or doing a team's internal task orchestration —
    including "just this once because it is small or urgent" (the persona's ONE
    ABSOLUTE BOUNDARY names that form explicitly)? Route the work to a team
    through its COS instead. → R13.2.
14. **GitHub authorship** — if this act writes to GitHub (issue, comment, PR,
    review, release note), does the body BEGIN with the one-line
    self-identification of which agent/role/plugin authored it, written with no
    at-sign anywhere in the line (all agents share one human-owner GitHub
    identity, and a bare handle pages a real account)? → R22.1–R22.3.
15. **AMP payload** — if this act sends an AMP message with an attachment, does
    the message carry ONLY the GitHub issue/comment URL of the attachment,
    never the file content itself? → R15.4.
16. **Creation constraints** — if this act creates a team or an agent
    (AUTONOMOUS, MAINTAINER, or via team creation), does every created agent
    get its mandatory role-plugin, and exactly ONE role each?
    → R9.13, R11.12, R12.3.

## Refusing

A refusal is itself a governed act: it must name the precise defect, the bar for
acceptance, and invite re-submission — and must not refuse the underlying NEED
when only the filing is defective. → R49.

## Keeping this list honest

This checklist is the enforcement surface, so a governed power missing from it is
unenforced (#107). When a new MANAGER power or rule lands, add its question in the
SAME change — and cite the rule, never restate it: a restated rule is a copy that
drifts silently when the original is bumped (S8.1→S8.2 lesson, `ai-maestro#109`).

**The same obligation fires on a PROHIBITION — new or newly-discovered.** A
checklist built by enumerating powers systematically misses prohibitions: a
standing prohibition predates the checklist, so no "new power" event ever
surfaces it — which is exactly how R13.2, the persona's single most absolute
constraint, went missing while twelve narrower rules were caught
(TRDD-ZIH2XUU6). When a prohibition is discovered absent, its question arrives
in the same change that records the discovery.
