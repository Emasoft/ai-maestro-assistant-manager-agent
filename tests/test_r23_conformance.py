#!/usr/bin/env python3
"""Conformance tests for the R23 frozen-CLI clause carried by every SKILL.md.

The hub ruled on ai-maestro#107 that every role-plugin must carry the R23
prohibition as FULL TEXT in each ``SKILL.md`` — a pointer was explicitly
rejected, because skills load on demand and in isolation, so a skill loaded
alone cannot resolve a reference. Duplication is therefore the ruled pattern,
and THIS TEST is what makes duplicating safe: without it a copy is drift
waiting to happen.

Comparison is byte-exact on purpose. A whitespace-normalising comparator can
pass a copy that lost its blockquote markers or its bold emphasis, and a buggy
normaliser can pass a TRUNCATED copy — which is the exact defect being fixed
here (``amama-status-reporting`` shipped a truncated clause naming no CLIs at
all). Byte-exact's only failure mode is a false positive on innocuous reflow,
which is cheap and is itself a signal that someone edited a frozen block.

Run: python3 tests/test_r23_conformance.py      (exit 0 = all pass)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_CANONICAL = _ROOT / "design" / "specs" / "r23-frozen-cli-canonical.md"
_SKILLS = _ROOT / "skills"
_COMMANDS = _ROOT / "commands"

# A command whose `allowed-tools` pins Bash to one script — Bash(python3 …x.py:*) —
# is confined STRUCTURALLY and cannot issue a raw route; a bare Bash entry can.
# What separates them is the character AFTER the word: `(` means script-confined,
# anything else means unrestricted. Matching only the double-quoted flow spelling
# (`"Bash"`) read every other valid YAML form — `[Bash]`, `'Bash'`, a block
# sequence item — as confined, so a command holding unrestricted Bash would be
# exempted from carrying the clause AND the test would still pass, making the
# coverage gap invisible. Quote-agnostic, with boundaries on both sides.
_UNRESTRICTED_BASH = re.compile(
    r"""allowed-tools:[^\n]*(?<![\w(])(?P<q>["']?)Bash(?P=q)(?![\w(])"""
)

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _harness import run_standalone  # noqa: E402

# The pre-2026-08-05 wording. It named only two CLIs as "the only sanctioned
# interface", which is NARROWER than the rule and narrow in the harmful
# direction: an agent needing `amp-kanban-get` finds it absent from the
# sanctioned set and may conclude the raw route is its only option. Asserted
# ABSENT so a stale-branch merge cannot resurrect it silently.
_SUPERSEDED_FRAGMENT = "the frozen CLIs (`aimaestro-agent.sh` / `aimaestro-teams.sh`) are the only sanctioned interface"


def _canonical_block() -> str:
    """Extract the canonical quoted block from the spec file.

    The block is the contiguous run of lines starting at the '> **Never call'
    line. Returned verbatim, blockquote markers included, because that is the
    form each SKILL.md must contain.
    """
    lines = _CANONICAL.read_text(encoding="utf-8").split("\n")
    start = next(i for i, ln in enumerate(lines) if ln.startswith("> **Never call"))
    end = start
    while end < len(lines) and lines[end].startswith(">"):
        end += 1
    return "\n".join(lines[start:end])


def _skill_files() -> list[Path]:
    return sorted(_SKILLS.glob("*/SKILL.md"))


def test_canonical_source_is_present_and_substantial():
    """The canonical spec file exists and yields a multi-paragraph clause (guards a vacuous pass)."""
    assert _CANONICAL.is_file(), f"canonical source missing: {_CANONICAL}"
    block = _canonical_block()
    # A rule asserted only over a corpus can pass vacuously on an empty needle:
    # if _canonical_block() ever returned "", every `in` check below would pass.
    assert len(block) > 500, "canonical block implausibly short — extraction is broken"
    for marker in ("(R23.1)", "(R23.2)", "(R23.4)", "(R23.5)"):
        assert marker in block, f"canonical block lost sub-clause {marker}"
    for cli in ("aimaestro-*.sh", "amp-*.sh", "aid-*.sh"):
        assert cli in block, f"canonical block lost CLI family {cli}"


def test_every_skill_carries_the_canonical_clause_verbatim():
    """Every skills/*/SKILL.md contains the canonical R23 block byte-for-byte."""
    skills = _skill_files()
    # Non-vacuity: an empty glob would make the loop below trivially pass.
    assert len(skills) >= 10, f"expected >=10 skills, found {len(skills)} — glob is wrong"
    block = _canonical_block()
    missing = [p.parent.name for p in skills if block not in p.read_text(encoding="utf-8")]
    assert not missing, f"SKILL.md missing the canonical R23 clause: {missing}"


def test_superseded_two_cli_wording_is_gone():
    """The narrower pre-#107 two-CLI wording appears in no skill (guards merge resurrection)."""
    offenders = [p.parent.name for p in _skill_files() if _SUPERSEDED_FRAGMENT in p.read_text(encoding="utf-8")]
    assert not offenders, f"superseded two-CLI R23 wording still present in: {offenders}"


def test_server_capable_commands_carry_the_clause():
    """Commands holding unrestricted Bash carry the clause; script-confined ones are exempt."""
    commands = sorted(_COMMANDS.glob("*.md"))
    # Non-vacuity: an empty glob would make both halves below pass trivially.
    assert commands, f"no commands found under {_COMMANDS} — glob is wrong"
    block = _canonical_block()
    unrestricted = [p for p in commands if _UNRESTRICTED_BASH.search(p.read_text(encoding="utf-8"))]
    # The rule binds commands as well as skills (R23.1 names them), but demanding
    # the block in a surface that cannot reach the server is how a rule becomes
    # furniture — pasted everywhere, read nowhere (ai-maestro#107). So coverage is
    # required exactly where the capability exists.
    assert unrestricted, "expected >=1 command with unrestricted Bash — detector may have rotted"
    missing = [p.name for p in unrestricted if block not in p.read_text(encoding="utf-8")]
    assert not missing, f"commands with unrestricted Bash lack the canonical R23 clause: {missing}"


def test_hooks_that_reach_the_server_state_the_prohibition():
    """Every hook whose description names a frozen CLI also cites R23 (a hook loads no skill)."""
    hooks = _ROOT / "hooks" / "hooks.json"
    assert hooks.is_file(), f"hooks.json missing: {hooks}"
    text = hooks.read_text(encoding="utf-8")
    # A hook runs with NO skill loaded, so "no skill instructed it" is structurally
    # true there rather than an oversight — the prohibition has to live on the hook.
    descriptions = re.findall(r'"_description":\s*"((?:[^"\\]|\\.)*)"', text)
    server_capable = [d for d in descriptions if re.search(r"\bamp-\w+|aimaestro-[\w.]+\.sh|aid-\w+", d)]
    # Non-vacuity, the guard its three sibling tests carry and this one lacked:
    # a `for` over an empty findall passes silently, so a renamed key, a
    # restructured hooks.json, or a reworded description would turn this test
    # green permanently while checking nothing.
    assert descriptions, "no _description values found in hooks.json — the regex has rotted"
    assert server_capable, "no hook description names a frozen CLI — detector may have rotted"
    for desc in server_capable:
        assert "R23" in desc, f"hook description names a frozen CLI but omits R23: {desc[:70]}…"


if __name__ == "__main__":
    sys.exit(run_standalone(globals()))
