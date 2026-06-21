#!/usr/bin/env python3
"""Shared standalone-runner scaffolding for the AMAMA test suite.

Every ``tests/test_*.py`` module is BOTH a pytest module (collected by its
``test_*`` functions) AND a self-contained standalone script
(``python3 tests/test_x.py`` -> exit 0, prints a unicode result table). The
table renderer and the standalone runner were previously copied verbatim into
each test file; that byte-identical duplication tripped the CI Mega-Linter
jscpd copy-paste gate (>5%). This module holds the single canonical copy so
each test file just calls it -- genuine DRY, no behavior change.

A test file uses it as:

    from _harness import run_standalone   # tests/ is on sys.path under pytest

    if __name__ == "__main__":
        sys.exit(run_standalone(globals()))

``run_standalone`` is passed the CALLER's ``globals()`` so it can discover that
module's own ``test_*`` functions (the original per-file ``main()`` relied on
the same module-global lookup).

Slow tests (those that spin a real HTTP server, etc.) are marked in the result
table with a trailing snail. Pass their names via ``slow`` and they get the
``slow_marker`` appended to the description of their PASS row -- matching the
per-file runners that originally carried a ``_SLOW`` set.
"""

from __future__ import annotations

from collections.abc import Collection, Mapping
from typing import Any


def _table(rows: list[tuple[str, str, str]]) -> str:
    """Render rows as a unicode-bordered Test/Status/Description result table."""
    name_w = max(len(r[0]) for r in rows)
    desc_w = max(len(r[2]) for r in rows)
    top = f"┏━{'━' * name_w}━┳━━━━━━━━┳━{'━' * desc_w}━┓"
    head = f"┃ {'Test':<{name_w}} ┃ Status ┃ {'Description':<{desc_w}} ┃"
    sep = f"┡━{'━' * name_w}━╇━━━━━━━━╇━{'━' * desc_w}━┩"
    bot = f"└─{'─' * name_w}─┴────────┴─{'─' * desc_w}─┘"
    out = [top, head, sep]
    for name, status, desc in rows:
        out.append(f"│ {name:<{name_w}} │ {status:<6} │ {desc:<{desc_w}} │")
    out.append(bot)
    return "\n".join(out)


def run_standalone(
    module_globals: Mapping[str, Any],
    *,
    slow: Collection[str] = (),
    slow_marker: str = " 🐌",
) -> int:
    """Run every ``test_*`` callable in ``module_globals``, print the result table.

    Collects the caller module's ``test_*`` functions (sorted by name), runs each
    catching ``AssertionError`` (FAIL) and any other exception (ERROR), prints the
    unicode table + an ``N/M passed`` line, and returns 1 if any test failed/errored
    else 0 -- the exit code a standalone ``python3 tests/test_x.py`` invocation needs.

    A test whose name is in ``slow`` gets ``slow_marker`` appended to its PASS-row
    description (the 🐌 slow-test convention).
    """
    tests = [v for k, v in sorted(module_globals.items()) if k.startswith("test_") and callable(v)]
    slow_names = frozenset(slow)
    rows: list[tuple[str, str, str]] = []
    failed = 0
    for fn in tests:
        desc = (fn.__doc__ or "").strip().split("\n")[0]
        marker = slow_marker if fn.__name__ in slow_names else ""
        try:
            fn()
            rows.append((fn.__name__, "PASS", f"{desc}{marker}"))
        except AssertionError as exc:
            failed += 1
            rows.append((fn.__name__, "FAIL", f"{desc}  [{exc}]"))
        except Exception as exc:  # noqa: BLE001
            failed += 1
            rows.append((fn.__name__, "ERROR", f"{desc}  [{type(exc).__name__}: {exc}]"))
    print(_table(rows))
    print(f"\n{len(tests) - failed}/{len(tests)} passed.")
    return 1 if failed else 0
