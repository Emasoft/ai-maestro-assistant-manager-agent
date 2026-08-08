#!/usr/bin/env python3
"""Pin the two role-plugin spec clauses that drift silently between releases.

Both come from `design/specs/role-plugins-spec.md` v1.1.0 on the `governance-rules`
branch of `Emasoft/ai-maestro` (tip `eaf609ad`), verified first-hand 2026-08-08.

RP-SKILL-MENU-01 — the main agent MUST carry a compact skill menu, one line per
shipped skill. The spec's own rationale is that an agent which cannot SEE its
skill inventory does not reach for it: descriptions alone under-trigger for
role-specific procedures. It also says **a stale menu is worse than none**, which
is the part a test can enforce — a menu that lists a skill the plugin no longer
ships asserts an inventory that does not exist, and a reader cannot tell.

RP-MODEL-01 — role-plugin agents OMIT `model:`. Model choice belongs to whoever
launches the session; a pin spends the operator's budget, is the only spelling
that silently degrades under an org model-restriction, and conflicts with CPV's
CA-04 cache-warmth default. Both the main agent and subagents are covered.

Run: python3 tests/test_skill_menu_matches_shipped.py      (exit 0 = all pass)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SKILLS = _ROOT / "skills"
_AGENTS = _ROOT / "agents"
_MAIN = _AGENTS / "ai-maestro-assistant-manager-agent-main-agent.md"

# Menu rows are `| `name` | when to reach for it |`. Matching the backticked name
# in the first cell keeps prose mentions of a skill elsewhere in the persona from
# counting as menu entries -- the spec asks for a MENU, not for coverage.
_MENU_ROW = re.compile(r"^\|\s*`(amama-[a-z0-9-]+)`\s*\|", re.MULTILINE)

# `model:` at the start of a line, outside a comment. A commented-out mention is
# how this repo records WHY the key is absent, so it must not count as a pin.
_MODEL_KEY = re.compile(r"^model:\s*\S+", re.MULTILINE)


def _shipped() -> set[str]:
    return {p.parent.name for p in _SKILLS.glob("*/SKILL.md")}


def _menu() -> set[str]:
    return set(_MENU_ROW.findall(_MAIN.read_text(encoding="utf-8")))


def test_shipped_skills_are_discoverable():
    """The plugin ships skills and the main agent file exists — else everything below is vacuous."""
    shipped = _shipped()
    assert len(shipped) >= 10, (
        f"found only {len(shipped)} shipped skills — the glob is wrong, and both "
        "checks below would pass over an empty set"
    )
    assert _MAIN.is_file(), f"main agent not found at {_MAIN}"


def test_skill_menu_matches_shipped_exactly():
    """The persona's skill menu lists exactly the shipped skills — no missing, no stale (RP-SKILL-MENU-01)."""
    shipped, menu = _shipped(), _menu()
    # Non-vacuity: a rewritten table shape would silently yield an empty menu,
    # and `set() - shipped` is empty, so "no stale entries" would pass on nothing.
    assert menu, (
        "no menu rows parsed from the persona — the table shape changed and this "
        "test would otherwise report a clean menu while none exists"
    )
    missing = sorted(shipped - menu)
    stale = sorted(menu - shipped)
    assert not missing and not stale, (
        f"skill menu out of sync — missing from menu: {missing}; listed but not "
        f"shipped: {stale}. RP-SKILL-MENU-01 requires the menu be updated in the "
        "SAME change that adds, renames or removes a skill; a stale menu is worse "
        "than none because it asserts an inventory that does not exist."
    )


def test_no_agent_pins_a_model():
    """No agent file carries a `model:` key — main or subagent (RP-MODEL-01, RULED 2026-08-08)."""
    agents = sorted(_AGENTS.glob("*.md"))
    assert agents, f"no agent files found under {_AGENTS} — glob is wrong"
    pinned = {p.name: _MODEL_KEY.findall(p.read_text(encoding="utf-8")) for p in agents}
    offenders = {k: v for k, v in pinned.items() if v}
    assert not offenders, (
        f"agents pinning a model: {offenders}. RP-MODEL-01 ruled that role-plugin "
        "agents omit `model:` — omission expresses `inherit` without a second "
        "spelling. Carrying a key past the release that adopts the ruling is a "
        "conformance failure. Record the WHY in a comment, not in a key."
    )


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _harness import run_standalone  # noqa: E402

    sys.exit(run_standalone(globals()))
