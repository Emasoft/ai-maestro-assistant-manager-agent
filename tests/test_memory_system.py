"""Tests for the AMAMA markdown memory system (issue #11).

Covers the three acceptance scenarios:
  (a) recall returns ranked/matching notes against a fixture memory dir;
  (b) write produces a schema-valid note + a MEMORY.md index line;
  (c) the grep fallback path works when memgrep is absent (PATH excludes memgrep).

Also asserts the shipped SKILL.md / rule files exist with valid frontmatter and
respect the cross-repo constraint (no `$CLAUDE_PLUGIN_ROOT/tools/memgrep`).

Stdlib + pytest + pyyaml only. Run: `uv run pytest tests/ -v`.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from memory_ops import (
    VALID_TYPES,
    append_index_line,
    is_schema_valid,
    memgrep_available,
    parse_note,
    recall_grep_fallback,
    write_note,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
RULE_FILE = REPO_ROOT / "rules" / "memory-protocol.md"
RECALL_SKILL = REPO_ROOT / "skills" / "amama-memory-recall" / "SKILL.md"
WRITE_SKILL = REPO_ROOT / "skills" / "amama-memory-write" / "SKILL.md"


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture
def fixture_memdir(tmp_path: Path) -> Path:
    """A small fixture memory dir with notes whose descriptions are SYMPTOM-indexed."""
    memdir = tmp_path / "memory"
    memdir.mkdir()
    # Note 1: a confirmed user preference about merge strategy (the symptom is the
    # QUESTION "which merge strategy", not the answer "squash").
    write_note(
        memdir,
        "feedback",
        "merge_strategy_default",
        "which merge strategy did the user pick for the team / squash or merge",
        "The user wants **squash-merge** as the default for all teams.\n"
        "**Why:** keeps history linear.\n"
        "**How to apply:** set merge-strategy: squash on every new team.",
    )
    # Note 2: a prior governance decision about prod-deploy approvals.
    write_note(
        memdir,
        "feedback",
        "prod_deploy_escalation",
        "prod deploy approval — should I auto-approve or escalate to the user",
        "Always escalate production deploys to the user; never auto-approve.\n"
        "**Why:** user wants final say on irreversible prod changes.\n"
        "**How to apply:** on a COS prod-deploy request, escalate-to-user.",
    )
    # Note 3: an unrelated reference note (should NOT match the above symptoms).
    write_note(
        memdir,
        "reference",
        "aimaestro_api_auth",
        "API call returned 403 / how do I authenticate to the AI Maestro server",
        "Authenticate with the AID session secret: `-H 'Authorization: Bearer $AID_AUTH'`.",
    )
    return memdir


# --------------------------------------------------------------------------- #
# (a) Recall against a fixture memory dir
# --------------------------------------------------------------------------- #
def test_recall_finds_note_from_symptom(fixture_memdir: Path) -> None:
    """recall: a symptom query returns the matching note (the QUESTION, not the answer)."""
    hits = recall_grep_fallback("merge strategy", fixture_memdir)
    names = {p.name for p in hits}
    assert "feedback_merge_strategy_default.md" in names
    # The unrelated API-auth note must NOT match the merge-strategy symptom.
    assert "reference_aimaestro_api_auth.md" not in names


def test_recall_indexed_by_question_not_answer(fixture_memdir: Path) -> None:
    """The one law: a note is findable from the SYMPTOM/question wording."""
    # Querying the QUESTION the future session will have finds the note...
    hits = recall_grep_fallback("should I auto-approve or escalate", fixture_memdir)
    assert any(p.name == "feedback_prod_deploy_escalation.md" for p in hits)


def test_recall_no_match_returns_empty_not_error(fixture_memdir: Path) -> None:
    """A non-match degrades to an empty list (grep exit 1), never an exception."""
    hits = recall_grep_fallback("something that appears in no note whatsoever zzqq", fixture_memdir)
    assert hits == []


def test_recall_missing_memdir_is_empty(tmp_path: Path) -> None:
    """Recall over an absent memory dir returns empty (degrade, never break)."""
    assert recall_grep_fallback("anything", tmp_path / "does-not-exist") == []


# --------------------------------------------------------------------------- #
# (b) Write produces a schema-valid note + a MEMORY.md index line
# --------------------------------------------------------------------------- #
def test_write_produces_schema_valid_note(tmp_path: Path) -> None:
    """write_note authors a file whose frontmatter matches the documented schema."""
    memdir = tmp_path / "memory"
    note = write_note(
        memdir,
        "feedback",
        "timezone_pref",
        "did the user tell me their timezone / when are they usually available",
        "User is in Europe/Rome; usually available 09:00-18:00 CET.",
    )
    assert note.exists()
    assert note.name == "feedback_timezone_pref.md"
    frontmatter, body = parse_note(note)
    assert is_schema_valid(frontmatter)
    assert frontmatter["name"] == "feedback_timezone_pref"
    assert frontmatter["metadata"] == {"node_type": "memory", "type": "feedback"}
    # The description carries the SYMPTOM/question vocabulary, and the answer is in the body.
    assert "timezone" in frontmatter["description"]
    assert "Europe/Rome" in body


def test_write_appends_memory_index_line(tmp_path: Path) -> None:
    """append_index_line writes the documented `- [Title](file.md) — hook.` line."""
    memdir = tmp_path / "memory"
    write_note(memdir, "user", "owner_email", "what is the user's email", "owner@example.com")
    index = append_index_line(
        memdir, "Owner email", "user_owner_email.md", "the user's contact email."
    )
    assert index.name == "MEMORY.md"
    content = index.read_text(encoding="utf-8")
    assert "- [Owner email](user_owner_email.md) — the user's contact email." in content


def test_write_index_line_round_trips_to_recall(tmp_path: Path) -> None:
    """A written note is recallable from its symptom (Test B — write-then-recall)."""
    memdir = tmp_path / "memory"
    write_note(
        memdir,
        "project",
        "single_manager_per_host",
        "can there be more than one manager / how many managers per host",
        "Exactly ONE manager (AMAMA) per host.\n**Why:** governance singleton.\n"
        "**How to apply:** never recommend a second manager.",
    )
    hits = recall_grep_fallback("how many managers per host", memdir)
    assert any(p.name == "project_single_manager_per_host.md" for p in hits)


def test_write_rejects_invalid_type(tmp_path: Path) -> None:
    """Fail-fast: an out-of-schema note type is refused, not silently coerced."""
    with pytest.raises(ValueError):
        write_note(tmp_path / "memory", "bogus", "x", "desc", "body")


@pytest.mark.parametrize("note_type", VALID_TYPES)
def test_write_accepts_all_valid_types(tmp_path: Path, note_type: str) -> None:
    """All four documented note types produce a schema-valid note."""
    note = write_note(tmp_path / "memory", note_type, "slug", f"symptom for {note_type}", "the fact")
    frontmatter, _ = parse_note(note)
    assert is_schema_valid(frontmatter)
    assert frontmatter["metadata"]["type"] == note_type


# --------------------------------------------------------------------------- #
# (c) The grep fallback path works when memgrep is absent
# --------------------------------------------------------------------------- #
def test_memgrep_gate_reports_absent_with_empty_path(fixture_memdir: Path) -> None:
    """`command -v memgrep` returns absent when PATH cannot reach the binary.

    Simulates the no-memgrep environment by pointing PATH at an empty dir, then
    confirms the documented gate (`command -v memgrep`) reports it absent AND
    that the grep fallback still recalls the note. This is the exact branch the
    skill takes when memgrep is not installed.
    """
    empty_bin = fixture_memdir.parent / "empty-bin"
    empty_bin.mkdir()
    assert memgrep_available(path_env=str(empty_bin)) is False
    # With memgrep absent, recall MUST still work via grep.
    hits = recall_grep_fallback("prod deploy approval", fixture_memdir)
    assert any(p.name == "feedback_prod_deploy_escalation.md" for p in hits)


def test_grep_fallback_runs_under_path_without_memgrep(fixture_memdir: Path) -> None:
    """End-to-end: run the documented fallback shell pipeline with memgrep off PATH.

    Mirrors the skill recipe literally: with `command -v memgrep` failing, run
    `grep -rliE "$SYMPTOM" "$MEMDIR"`. We invoke it via /bin/sh with a PATH that
    still contains grep (a real system dir) but no memgrep, proving the fallback
    is self-contained.
    """
    import shutil
    import subprocess

    grep_path = shutil.which("grep")
    assert grep_path, "grep must be available to run the documented fallback"
    grep_dir = str(Path(grep_path).parent)
    # PATH carries grep's dir (so the fallback's `grep` resolves) but no memgrep.
    # `sh` itself is invoked by ABSOLUTE path /bin/sh, so the overridden PATH only
    # governs the `command -v memgrep` lookup, not the shell's own resolution
    # (a bare "sh" would FileNotFound under a PATH that lacks the shell's dir).
    env = {**os.environ, "PATH": grep_dir, "MEMDIR": str(fixture_memdir), "SYMPTOM": "squash or merge"}
    script = (
        'if command -v memgrep >/dev/null 2>&1; then echo "MEMGREP"; '
        'else grep -rliE "$SYMPTOM" "$MEMDIR"; fi'
    )
    proc = subprocess.run(["/bin/sh", "-c", script], capture_output=True, text=True, check=True, env=env)
    assert "MEMGREP" not in proc.stdout  # proves the fallback branch ran
    assert "feedback_merge_strategy_default.md" in proc.stdout


# --------------------------------------------------------------------------- #
# Shipped artifact checks (rule + skills exist, valid frontmatter, constraints)
# --------------------------------------------------------------------------- #
def _read_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path} must start with YAML frontmatter"
    _, fm, _ = text.split("---\n", 2)
    return yaml.safe_load(fm)


def test_rule_file_present() -> None:
    """The recall protocol rule is shipped."""
    assert RULE_FILE.is_file()
    assert "index by the QUESTION, not the answer" in RULE_FILE.read_text(encoding="utf-8")


@pytest.mark.parametrize("skill", [RECALL_SKILL, WRITE_SKILL])
def test_skill_frontmatter_valid(skill: Path) -> None:
    """Each skill ships with parseable frontmatter carrying the AMAMA convention fields."""
    assert skill.is_file()
    fm = _read_frontmatter(skill)
    for key in ("name", "description", "version", "compatibility", "context", "agent", "user-invocable"):
        assert key in fm, f"{skill} frontmatter missing {key}"
    assert fm["name"].startswith("amama-memory-")


@pytest.mark.parametrize("path", [RULE_FILE, RECALL_SKILL, WRITE_SKILL])
def test_no_bundled_memgrep_reference(path: Path) -> None:
    """Cross-repo constraint: never claim memgrep ships in THIS plugin's tools/."""
    text = path.read_text(encoding="utf-8")
    assert "$CLAUDE_PLUGIN_ROOT/tools/memgrep" not in text


@pytest.mark.parametrize("skill", [RECALL_SKILL, WRITE_SKILL])
def test_skill_documents_grep_fallback(skill: Path) -> None:
    """Both skills document the memgrep gate + the grep fallback (degrade, never break)."""
    text = skill.read_text(encoding="utf-8")
    assert "command -v memgrep" in text
    assert "grep -rliE" in text
