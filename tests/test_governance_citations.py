#!/usr/bin/env python3
"""Pin every governance rule this plugin CITES to the ratified rule set.

This test exists because of a specific, expensive failure on 2026-08-07/08.

This plugin shipped a release citing `R42.8` as settled governance, taken from a
downstream summary rather than the rule catalog. It was then *demoted* to
"pending amendment" on a correct measurement (R42.8 genuinely appeared on no
readable ref) and a wrong inference (the USER grant predated its publication by
three days). Both the over-claim and the retraction shipped to users. Nothing in
this repo could have caught either, because nothing checked citations at all.

So the test asserts the one thing a script CAN check: every `Rnn` this plugin
cites is a rule that actually exists in the ratified catalog. It cannot check
that a citation is *apt* — only a reader can — but it makes an invented,
renumbered, or hallucinated rule number fail loudly instead of shipping.

The snapshot below is the rule set of `docs/GOVERNANCE-RULES.md` on the
`governance-rules` branch of `Emasoft/ai-maestro`, which the hub confirmed on
2026-08-08 is the authoritative ref (`main` carries a stale v4.0.2 that asserts,
falsely, that the catalog ends at R20 — do not measure against it).

WHEN THIS TEST FAILS after an upstream renumber: re-fetch the catalog, confirm
the new range by reading it, and update SNAPSHOT together with SNAPSHOT_VERSION
in the same commit. Updating one without the other is how the snapshot silently
stops meaning anything.

Run: python3 tests/test_governance_citations.py      (exit 0 = all pass)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent

# docs/GOVERNANCE-RULES.md @ governance-rules, version 5.3.3, tip e46764f6,
# verified first-hand 2026-08-08. R1..R52 with no gaps.
SNAPSHOT_VERSION = "5.3.3"
SNAPSHOT = {f"R{n}" for n in range(1, 53)}

# Rules whose subject matter IS the MANAGER's own job. A citation-free persona
# is how R49 sat encoded-but-uncited: the behaviour was right, but no reader
# could trace it to an authority, and no scan could tell "absent" from "present
# under a different name". Each of these must be cited BY NUMBER somewhere.
_MANAGER_CORE = {
    "R6",   # communication graph — COS is the sole entry into a team
    "R23",  # frozen-CLI decoupling
    "R41",  # APPROVAL vs MANDATE
    "R42",  # no agent may drive another agent
    "R45",  # teams are same-host; groups may span hosts (scale-critical)
    "R49",  # the refusal protocol — an approver is a guide, not a gate
}

# Rules that govern how the ai-maestro SERVER and UI must be BUILT, not how the
# MANAGER must behave. Their absence from this plugin is a decision, not a gap.
# Recorded so a coverage scan reads the decision instead of re-deriving it every
# time -- and so that adding a rule here is a deliberate, reviewable act.
_PLATFORM_ONLY = {
    "R7",   # UI robustness
    "R8",   # data integrity
    "R21",  # what an all-in-one function is
    "R47",  # VPN-unique user names / remote registration
    "R50",  # one operation, one AIO function
    "R51",  # all-or-nothing: an AIO function is a transaction
}

_SEARCH_DIRS = ("agents", "skills", "docs", "tests")
_SUFFIXES = {".md", ".py", ".json"}
# A citation is `Rnn` or `Rnn.n` on a word boundary. The trailing (?![0-9])
# stops `R4` from matching inside `R42` — without it every short id appears
# cited by any longer one, and the test passes vacuously.
_CITE = re.compile(r"\bR([0-9]{1,2})(?:\.[0-9]+)?(?![0-9])")


def _corpus() -> list[tuple[Path, str]]:
    out = []
    for d in _SEARCH_DIRS:
        base = _ROOT / d
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix in _SUFFIXES:
                out.append((p, p.read_text(encoding="utf-8", errors="replace")))
    return out


def _cited() -> dict[str, set[str]]:
    """Map rule id -> set of repo-relative files citing it."""
    found: dict[str, set[str]] = {}
    for path, text in _corpus():
        for m in _CITE.finditer(text):
            found.setdefault(f"R{m.group(1)}", set()).add(
                str(path.relative_to(_ROOT))
            )
    return found


def test_corpus_is_not_empty():
    """The scanned corpus contains files — otherwise every check below passes vacuously."""
    files = _corpus()
    assert len(files) >= 20, (
        f"only {len(files)} files scanned across {_SEARCH_DIRS} — the glob is "
        "wrong, and every other assertion in this file would pass on an empty set"
    )


def test_every_cited_rule_exists_in_the_ratified_catalog():
    """No file cites an Rnn absent from the ratified catalog (invented or renumbered)."""
    cited = _cited()
    # Non-vacuity: we know R42 is cited; if the regex stops matching, say so
    # loudly rather than reporting a clean run over nothing.
    assert "R42" in cited, (
        "R42 is not detected as cited anywhere — the citation regex has rotted; "
        "this test would otherwise pass without checking anything"
    )
    unknown = {r: sorted(f)[:3] for r, f in cited.items() if r not in SNAPSHOT}
    assert not unknown, (
        f"citations to rules absent from catalog v{SNAPSHOT_VERSION}: {unknown}. "
        "Either the rule was renumbered upstream (re-fetch and update SNAPSHOT + "
        "SNAPSHOT_VERSION together) or the citation is invented — which is the "
        "exact defect that shipped in v2.15.0."
    )


def test_manager_core_rules_are_cited_by_number():
    """Rules governing the MANAGER's own job are cited by number, not just paraphrased."""
    cited = _cited()
    missing = sorted(_MANAGER_CORE - set(cited), key=lambda r: int(r[1:]))
    assert not missing, (
        f"MANAGER-core rules never cited by number: {missing}. Encoding the "
        "behaviour is not enough — an uncited rule cannot be traced to its "
        "authority by a reader, or distinguished from an absent one by a scan. "
        "R49 sat encoded-but-uncited for exactly this reason."
    )


def test_every_ratified_rule_is_either_cited_or_explicitly_out_of_scope():
    """Every rule in the catalog is cited here or classified platform-only — no silent gaps."""
    cited = set(_cited())
    unaccounted = sorted(
        SNAPSHOT - cited - _PLATFORM_ONLY, key=lambda r: int(r[1:])
    )
    assert not unaccounted, (
        f"rules neither cited nor classified: {unaccounted}. Every ratified rule "
        "must be a decision: cite it where it binds the MANAGER, or add it to "
        "_PLATFORM_ONLY with the reason. This is what makes an upstream rule "
        "addition fail loudly here instead of sitting unnoticed as a coverage gap."
    )


    # NOTE: an earlier version of this file asserted that no _PLATFORM_ONLY rule
    # is cited anywhere. That invariant was FALSE and the test caught it on its
    # first run: the persona names those rules precisely in order to exclude
    # them, and naming a rule to say it does not apply is the honest act, not a
    # contradiction. The real invariant is the one below -- prose and code must
    # agree on the SAME set, so neither can drift into a private opinion.


_EXCLUSION_MARKER = "Rules that deliberately do NOT bind this plugin"
_PERSONA = _ROOT / "agents" / "ai-maestro-assistant-manager-agent-main-agent.md"


def test_platform_only_set_matches_the_documented_exclusion():
    """_PLATFORM_ONLY equals the rule set the persona's exclusion paragraph names."""
    text = _PERSONA.read_text(encoding="utf-8")
    start = text.find(_EXCLUSION_MARKER)
    assert start != -1, (
        f"{_PERSONA.name} no longer contains the exclusion paragraph "
        f"({_EXCLUSION_MARKER!r}). A reader who cannot find the reasoning will "
        "re-derive the 'gap' and re-litigate it — which is the cost this "
        "paragraph exists to prevent."
    )
    # The paragraph is one blockquote; stop at the blank line that ends it.
    end = text.find("\n\n", start)
    para = text[start : end if end != -1 else len(text)]
    documented = {f"R{m.group(1)}" for m in _CITE.finditer(para)}
    assert documented == _PLATFORM_ONLY, (
        f"persona documents {sorted(documented, key=lambda r: int(r[1:]))} as "
        f"out-of-scope but _PLATFORM_ONLY holds "
        f"{sorted(_PLATFORM_ONLY, key=lambda r: int(r[1:]))}. Update both "
        "together: the test set decides what the coverage check tolerates, and "
        "the paragraph is the only place a human learns WHY."
    )


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _harness import run_standalone  # noqa: E402

    sys.exit(run_standalone(globals()))
