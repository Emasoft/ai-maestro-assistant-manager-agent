#!/usr/bin/env python3
"""Real (no-mock) tests for scripts/amama_init_design_folders.py.

``amama_init_design_folders.py`` scaffolds the AMAMA design/ tree: the main
folders (requirements/handoffs/config + the TRDD lifecycle folders
proposals/tasks/refused/archived), per-platform requirements + config
sub-trees, the markdown templates, and an ``index.yaml`` manifest. It also
guards against re-init (exit 1 unless ``--force``).

Every test runs against a fresh throwaway dir under the system temp dir and
asserts the REAL filesystem outcome — directories created, file contents,
parsed YAML, exit codes. The CLI is driven as Claude Code would drive it: a
real ``subprocess`` with ``--root`` pinned to the temp dir (JSON/args in, exit
code out). The pure functions are also called in-process against a real Path.
Nothing is mocked.

Run: python3 tests/test_amama_init_design_folders.py      (exit 0 = all pass)
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import amama_init_design_folders as idf  # noqa: E402  # pyright: ignore[reportMissingImports]
from _harness import run_standalone  # noqa: E402

_SCRIPT = _SCRIPTS / "amama_init_design_folders.py"


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
def _tmp() -> Path:
    """A fresh throwaway working directory (caller is responsible for cleanup)."""
    return Path(tempfile.mkdtemp(prefix="idf-test-"))


def _run_cli(root: Path, *argv: str) -> subprocess.CompletedProcess[str]:
    """Invoke the script exactly as a real caller would: subprocess + --root."""
    return subprocess.run(
        [sys.executable, str(_SCRIPT), "--root", str(root), *argv],
        capture_output=True,
        text=True,
        check=False,
    )


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def test_creates_all_main_and_platform_folders():
    """A fresh init creates every main folder + the per-platform requirements/config sub-trees."""
    tmp = _tmp()
    try:
        root = tmp / "design"
        proc = _run_cli(root)
        assert proc.returncode == 0, f"exit {proc.returncode}; stderr={proc.stderr!r}"
        # All seven main folders exist (incl. the TRDD lifecycle quartet).
        for name in ("requirements", "handoffs", "config", "proposals", "tasks", "refused", "archived"):
            assert (root / name).is_dir(), f"missing main folder {name}"
        # 'shared' is the default platform → its requirements + config sub-trees exist.
        for sub in ("templates", "specs", "rdd"):
            assert (root / "requirements" / "shared" / sub).is_dir(), f"missing requirements/shared/{sub}"
        assert (root / "config" / "shared").is_dir()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_seed_template_files_written_with_real_content():
    """Init writes the three markdown templates with their real (non-empty, placeholder) content."""
    tmp = _tmp()
    try:
        root = tmp / "design"
        assert _run_cli(root).returncode == 0
        spec = root / "requirements" / "shared" / "templates" / "MODULE_SPEC_TEMPLATE.md"
        rdd = root / "requirements" / "shared" / "templates" / "RDD_TEMPLATE.md"
        handoff = root / "handoffs" / "templates" / "HANDOFF_TEMPLATE.md"
        for f in (spec, rdd, handoff):
            assert f.is_file(), f"missing template {f.name}"
        # Real content, not stubs — assert distinctive markers from each template.
        assert "Module Specification Template" in spec.read_text(encoding="utf-8")
        assert "{{MODULE_ID}}" in spec.read_text(encoding="utf-8")
        assert "Requirements-Driven Design Document" in rdd.read_text(encoding="utf-8")
        assert "Agent Handoff Document" in handoff.read_text(encoding="utf-8")
        assert "{{HANDOFF_ID}}" in handoff.read_text(encoding="utf-8")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_index_yaml_written_and_parseable():
    """Init writes a valid index.yaml recording version, root, the platform list, and zeroed stats."""
    tmp = _tmp()
    try:
        root = tmp / "design"
        assert _run_cli(root, "--platforms", "web", "ios").returncode == 0
        index_file = root / "index.yaml"
        assert index_file.is_file(), "index.yaml not created"
        data = yaml.safe_load(index_file.read_text(encoding="utf-8"))
        assert data["version"] == "1.0.0"
        assert data["root"] == str(root)
        # 'shared' is force-prepended; the requested platforms follow.
        assert data["platforms"] == ["shared", "web", "ios"]
        assert data["stats"]["total_documents"] == 0
        assert set(data["stats"]["by_platform"]) == {"shared", "web", "ios"}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_reinit_without_force_is_safe_noop_exit1():
    """Re-running on an already-initialized root is a SAFE no-op: exit 1, no error, files untouched."""
    tmp = _tmp()
    try:
        root = tmp / "design"
        assert _run_cli(root).returncode == 0
        # Mark a template so we can prove the second run does not overwrite it.
        spec = root / "requirements" / "shared" / "templates" / "MODULE_SPEC_TEMPLATE.md"
        sentinel = spec.read_text(encoding="utf-8") + "\n<!-- user edit sentinel -->\n"
        spec.write_text(sentinel, encoding="utf-8")
        index_before = (root / "index.yaml").read_text(encoding="utf-8")

        second = _run_cli(root)
        assert second.returncode == 1, "re-init without --force must exit 1 (guard)"
        assert "already initialized" in second.stdout
        # Idempotency: nothing destroyed — user edit + original index survive intact.
        assert spec.read_text(encoding="utf-8") == sentinel, "second run clobbered an existing template"
        assert (root / "index.yaml").read_text(encoding="utf-8") == index_before, "second run rewrote index.yaml"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_force_reinit_succeeds_and_idempotent_function_layer():
    """--force re-init exits 0; and re-running the folder/template builders twice adds nothing new."""
    tmp = _tmp()
    try:
        root = tmp / "design"
        assert _run_cli(root).returncode == 0
        forced = _run_cli(root, "--force")
        assert forced.returncode == 0, f"--force should re-init cleanly; stderr={forced.stderr!r}"

        # Function-level idempotency: a second create_template_files call returns [] (all exist),
        # while create_folder_structure stays mkdir(exist_ok=True)-safe and re-lists the same dirs.
        platforms = ["shared"]
        first_templates = idf.create_template_files(root, platforms)
        assert first_templates == [], "templates already on disk, yet builder reported new writes"
        folders_again = idf.create_folder_structure(root, platforms)
        assert all(p.is_dir() for p in folders_again), "re-run folder builder left a path missing"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_json_mode_reports_created_then_error_on_reinit():
    """--json emits a machine-readable result: success=true on first init, success=false on guarded re-init."""
    tmp = _tmp()
    try:
        root = tmp / "design"
        first = _run_cli(root, "--json")
        assert first.returncode == 0
        payload = json.loads(first.stdout)
        assert payload["success"] is True
        assert payload["index_created"] is True
        assert len(payload["folders_created"]) > 0
        assert len(payload["templates_created"]) == 3  # spec + rdd (shared) + handoff
        assert payload["errors"] == []
        # Guarded re-init under --json: structured failure, not a crash.
        second = _run_cli(root, "--json")
        assert second.returncode == 1
        payload2 = json.loads(second.stdout)
        assert payload2["success"] is False
        assert any("already initialized" in e for e in payload2["errors"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(run_standalone(globals()))
