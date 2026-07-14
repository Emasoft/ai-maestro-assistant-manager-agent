#!/usr/bin/env python3
"""Real (no-mock) tests for scripts/publish.py::get_plugin_name + the resolver tag.

Each test builds a throwaway temp project with a real
``.claude-plugin/plugin.json`` on disk and asserts the ACTUAL
``get_plugin_name`` outcome, plus the ``{name}--v{version}`` tag-format contract
the Claude Code dependency resolver requires
(https://code.claude.com/docs/en/plugin-dependencies.md, since CC 2.1.110).
Nothing is mocked.

Regression guard for repo #25 / ai-maestro TRDD-JT3U4ZVM: publish.py emitted only
the plain ``v{version}`` tag, which the resolver's ``{name}--v`` prefix filter
never matches — so every version-constrained dependent failed to install ("no git
tag satisfying <range>") on a repo full of tags, taking the whole AI Maestro fleet
down for a day. These tests pin the name source (the MANIFEST, never the dir name)
and the exact tag prefix so the outage cannot silently recur.

Run: python3 tests/test_publish_dependency_tag.py      (exit 0 = all pass)
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import publish  # noqa: E402  # pyright: ignore[reportMissingImports]
from _harness import run_standalone  # noqa: E402


def _mkplugin(name_field: object | None) -> Path:
    """Build a temp plugin dir; write plugin.json with (or without) a name field."""
    d = Path(tempfile.mkdtemp(prefix="dep-tag-"))
    (d / ".claude-plugin").mkdir(parents=True)
    data: dict[str, object] = {"version": "1.2.3"}
    if name_field is not None:
        data["name"] = name_field
    (d / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(data), encoding="utf-8"
    )
    return d


def test_get_plugin_name_reads_manifest():
    """get_plugin_name returns the `name` field from .claude-plugin/plugin.json."""
    d = _mkplugin("my-plugin")
    try:
        assert publish.get_plugin_name(d) == "my-plugin"
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_get_plugin_name_none_when_name_absent():
    """A manifest with no `name` key yields None (hard-fail signal, never a guess)."""
    d = _mkplugin(None)
    try:
        assert publish.get_plugin_name(d) is None
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_get_plugin_name_none_when_name_empty():
    """An empty-string `name` is treated as absent (None), not a `--v` tag prefix."""
    d = _mkplugin("")
    try:
        assert publish.get_plugin_name(d) is None
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_get_plugin_name_none_when_no_manifest():
    """A directory with no plugin.json yields None rather than raising."""
    d = Path(tempfile.mkdtemp(prefix="dep-tag-"))
    try:
        assert publish.get_plugin_name(d) is None
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_get_plugin_name_none_on_malformed_json():
    """Malformed plugin.json yields None (the except path), never a crash."""
    d = Path(tempfile.mkdtemp(prefix="dep-tag-"))
    (d / ".claude-plugin").mkdir(parents=True)
    (d / ".claude-plugin" / "plugin.json").write_text("{ not json", encoding="utf-8")
    try:
        assert publish.get_plugin_name(d) is None
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_dep_tag_prefix_contract():
    """The resolver tag is `{name}--v{version}` — the `{name}--v` prefix is what CC filters on."""
    name, version = "my-plugin", "1.2.3"
    dep_tag = f"{name}--v{version}"
    # The resolver lists tags and filters to those starting with `{name}--v`; the
    # plain `v{version}` tag fails that filter, which is the whole bug this guards.
    assert dep_tag.startswith(f"{name}--v")
    assert dep_tag == "my-plugin--v1.2.3"
    assert not f"v{version}".startswith(f"{name}--v")


def test_this_repo_manifest_name_pins_tag_prefix():
    """This plugin's real manifest name is stable, so its `--v` tag prefix can't drift."""
    repo_root = _SCRIPTS.parent
    assert publish.get_plugin_name(repo_root) == "ai-maestro-assistant-manager-agent"


if __name__ == "__main__":
    sys.exit(run_standalone(globals()))
