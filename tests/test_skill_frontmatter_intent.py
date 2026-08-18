#!/usr/bin/env python3
"""Pin the skill-frontmatter choices that a HARNESS DEFAULT could silently flip.

Every skill here is `context: fork` + `background: false`. The second field is
not decoration and it is not the default: Claude Code 2.1.218 changed
`context: fork` skills to run in the BACKGROUND by default, with `background:
false` as the per-skill opt-out. So the explicit value is the only thing keeping
these skills foreground, and a future release that changes the default again
would move them without touching this repo, without failing anything, and
without appearing in any diff.

That is the failure mode worth a test: a silent behavioural change owned by
software we do not control. A backgrounded MANAGER skill does not error — it
answers into a different surface than the user is reading, which is the kind of
break that gets noticed days later and blamed on the wrong thing.

The test therefore asserts the INTENT, not the current default. If the fleet
later decides some skills SHOULD background, the fix is to change the expected
value here deliberately — which is exactly the review this pins.

Run: python3 tests/test_skill_frontmatter_intent.py      (exit 0 = all pass)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SKILLS = _ROOT / "skills"

# Frontmatter is read with a line regex rather than a YAML parser on purpose:
# the parser would normalise `false`/`no`/`off` (all accepted since 2.1.218)
# into one boolean and hide which spelling shipped. Here the literal text is
# part of what is being pinned.
_FIELD = r"^{field}:\s*(?P<v>\S+)\s*$"


def _skill_files() -> list[Path]:
    return sorted(_SKILLS.glob("*/SKILL.md"))


def _frontmatter(path: Path) -> str:
    """Return the frontmatter block, or "" when the file has none."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---", 4)
    return text[4:end] if end != -1 else ""


def _field(fm: str, field: str) -> str | None:
    m = re.search(_FIELD.format(field=field), fm, re.MULTILINE)
    return m.group("v") if m else None


# Every key here is one the HARNESS would otherwise choose for us. That is the
# whole selection rule: an undeclared key is not "left at a sensible default",
# it is a decision made by software we do not control, whose change produces no
# diff, no error and no failing test in this repo.
_MUST_DECLARE = ("context", "background", "user-invocable")

# CPV's schema admits exactly ONE explicit `context` value — `fork`. A skill that
# must load INLINE (its content has to land in the deciding context, e.g. the
# governance self-audit checklist) therefore CANNOT declare the key: any non-fork
# spelling is a CPV CRITICAL and blocks publish. For those skills the intent is
# pinned the same way RP-MODEL-01 pins `model:` — the key is OMITTED and a
# mandatory frontmatter comment records the omission as deliberate. `background:`
# is a fork-only knob, so it is omitted together with `context`;
# `user-invocable` stays mandatory for every skill.
_INLINE_OMISSION = re.compile(r"^#\s*context:\s*omitted-on-purpose\b.*\bINLINE\b", re.MULTILINE)


def test_every_skill_declares_the_harness_owned_keys_explicitly():
    """Each skills/*/SKILL.md sets context, background AND user-invocable — or documents the inline omission."""
    skills = _skill_files()
    # Non-vacuity: an empty glob would make the loop below trivially pass.
    assert len(skills) >= 10, f"expected >=10 skills, found {len(skills)} — glob is wrong"
    missing = {}
    for p in skills:
        fm = _frontmatter(p)
        absent = [k for k in _MUST_DECLARE if _field(fm, k) is None]
        if absent == ["context", "background"] and _INLINE_OMISSION.search(fm):
            # Deliberate inline skill: both fork-shaped keys omitted, WHY on record.
            continue
        if absent:
            missing[p.parent.name] = absent
    assert not missing, (
        f"SKILL.md relying on a harness default: {missing} — 2.1.218 flipped the "
        "`fork` default to background, which is the proof that these defaults "
        "move; only an explicit value survives the next such change"
    )


def test_fork_skills_are_pinned_foreground():
    """Every `context: fork` skill pins `background: false` — the 2.1.218 opt-out that keeps it foreground."""
    skills = _skill_files()
    forked = [p for p in skills if _field(_frontmatter(p), "context") == "fork"]
    # Non-vacuity again: if the frontmatter shape changes so nothing parses as
    # `fork`, this test must fail loudly rather than pass over an empty list.
    assert forked, "no `context: fork` skill found — the frontmatter reader has rotted"
    wrong = [
        p.parent.name
        for p in forked
        if (_field(_frontmatter(p), "background") or "").lower() not in {"false", "no", "off", "0"}
    ]
    assert not wrong, (
        f"`context: fork` skills not pinned foreground: {wrong}. If backgrounding "
        "one is intended, change the expectation here deliberately — that review "
        "is the point of this test"
    )


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _harness import run_standalone  # noqa: E402

    sys.exit(run_standalone(globals()))
