#!/usr/bin/env python3
"""No GitHub @handles inside fenced blocks — the hole the prose guards leave open.

The workspace mention guard deliberately SKIPS fenced content, and that exemption
is correct for prose: GitHub does not linkify inside a code span, so `@name` in a
fence is inert *on the page it sits on*.

It is not inert in a TEMPLATE. A fenced `gh issue comment --body "..."` block, a
heredoc, or a pasteable byline is content that gets copied OUT of its fence and
posted — at which point the handle pages a real account. The fence tells you
nothing about whether the handle survives, because the fence does not travel with
the text. This has bitten the fleet twice: a PRRD byline shipped a real org handle
inside a code span for months, and a salvaged self-id template paged the owner from
every issue body created from it (orchestrator, 2026-08-08).

So this test inverts the prose guard's assumption and scans exactly what that guard
skips. Mirrors the hub's `tests/governance/no-handles-in-postable-bodies.test.ts`
(commit e171a8bc), added at the USER's request for a safeguard against citations.

Templates carry NO `@` at all. If a real handle is genuinely needed at runtime,
build it from a variable so the literal shipped text is harmless.

Run: python3 tests/test_no_handles_in_fenced_bodies.py      (exit 0 = all pass)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SKIP = (".git/", "node_modules", "_dev/", "reports/", ".venv")
_SUFFIXES = (".md", ".py", ".sh")

# A handle is `@` + a letter-led word, NOT preceded by a word char or a backtick.
# The lookbehind is what keeps `user@example.com` and `actions/checkout@v4` out --
# an address does not page its domain, and a version pin is not a mention. Both are
# asserted below rather than assumed, because a matcher that quietly stops matching
# turns this whole file into a green light over an unscanned tree.
_HANDLE = re.compile(r"(?<![\w`])@([A-Za-z][\w-]*)")
_FENCE = "```"


def _files() -> list[Path]:
    out = []
    for suf in _SUFFIXES:
        for p in _ROOT.rglob(f"*{suf}"):
            if not any(s in str(p) for s in _SKIP):
                out.append(p)
    return out


def _fenced_hits() -> tuple[list[str], int]:
    """Return (hits, number_of_fenced_lines_examined)."""
    hits, fenced_lines = [], 0
    for p in _files():
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        in_fence = False
        for lineno, line in enumerate(text.splitlines(), 1):
            if line.strip().startswith(_FENCE):
                in_fence = not in_fence
                continue
            if not in_fence:
                continue
            fenced_lines += 1
            for m in _HANDLE.finditer(line):
                rel = p.relative_to(_ROOT)
                hits.append(f"{rel}:{lineno}  @{m.group(1)}")
    return hits, fenced_lines


def test_matcher_catches_handles_and_skips_non_handles():
    """The handle matcher fires on real mentions and not on emails or version pins."""
    must_catch = [
        'gh issue comment --body "ping @janitor"',
        "Posted by @Emasoft via the shared gh auth",
    ]
    must_skip = ["user@example.com", "actions/checkout@v4", "`@lru_cache`"]
    for s in must_catch:
        assert _HANDLE.search(s), f"matcher failed to catch a real handle in: {s!r}"
    for s in must_skip:
        assert not _HANDLE.search(s), f"matcher wrongly flagged: {s!r}"


def test_scan_actually_enters_fences():
    """Fenced content exists and is examined — else a clean result means nothing."""
    _, fenced_lines = _fenced_hits()
    assert fenced_lines > 100, (
        f"only {fenced_lines} fenced lines examined across the repo — the fence "
        "tracker is broken, and a zero-hit result would be a green light over an "
        "unscanned tree rather than evidence of cleanliness"
    )


def test_no_handles_inside_fenced_blocks():
    """No @handle appears inside any fenced block — templates get copied OUT of the fence."""
    hits, _ = _fenced_hits()
    assert not hits, (
        "GitHub @handles found inside fenced blocks:\n  "
        + "\n  ".join(hits[:20])
        + "\n\nA fence does NOT travel with the text. Anything in a postable body, "
        "heredoc or byline gets copied out and pages a real account. Remove the "
        "handle, or build it from a variable so the shipped literal is harmless."
    )


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _harness import run_standalone  # noqa: E402

    sys.exit(run_standalone(globals()))
