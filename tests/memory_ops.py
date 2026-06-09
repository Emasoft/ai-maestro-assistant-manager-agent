"""Reference implementation of the AMAMA markdown-memory operations.

This module implements EXACTLY the operations documented in the
`amama-memory-recall` and `amama-memory-write` skills and the
`rules/memory-protocol.md` rule, so the test suite exercises the real
documented behaviour (not a parallel mock):

- `recall_grep_fallback`  -> the `grep -rliE "$SYMPTOM" "$MEMDIR"` fallback the
  recall skill runs when `command -v memgrep` is empty.
- `write_note`            -> the schema-valid note the write skill authors.
- `append_index_line`     -> the `MEMORY.md` index line the write skill appends.
- `parse_note`            -> read back a note's frontmatter + body for assertions.

Stdlib + pyyaml only (pyyaml is already a declared plugin dependency).
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import yaml

VALID_TYPES = ("user", "feedback", "project", "reference")

# Matches the YAML frontmatter block delimited by `---` lines at the top of a note.
_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.DOTALL)


def recall_grep_fallback(symptom: str, memdir: Path) -> list[Path]:
    """Recall via the documented grep fallback (memgrep-absent path).

    Mirrors the skill's fallback verbatim: `grep -rliE "$SYMPTOM" "$MEMDIR"`.
    `-r` recurse, `-l` list filenames only, `-i` case-insensitive, `-E` ERE.
    Returns the matching note paths (sorted for determinism). A non-match is a
    grep exit code of 1, which we translate to an empty list (not an error) so
    recall degrades, never breaks.
    """
    if not memdir.is_dir():
        return []
    proc = subprocess.run(
        ["grep", "-rliE", symptom, str(memdir)],
        capture_output=True,
        text=True,
        check=False,
    )
    # grep exit codes: 0 = match, 1 = no match, >=2 = real error.
    if proc.returncode >= 2:
        raise RuntimeError(f"grep failed ({proc.returncode}): {proc.stderr.strip()}")
    return sorted(Path(line) for line in proc.stdout.splitlines() if line.strip())


def memgrep_available(path_env: str | None = None) -> bool:
    """The skill's gate: `command -v memgrep`.

    `path_env` overrides $PATH for the lookup (used by the fallback test to
    simulate memgrep being absent). Uses `command -v` via the shell exactly as
    documented, not Python's shutil.which, so the test exercises the real gate.
    """
    env = {"PATH": path_env} if path_env is not None else None
    # Invoke /bin/sh by ABSOLUTE path: when `env` overrides PATH (the
    # memgrep-absent test passes an empty/minimal PATH), subprocess must still
    # be able to locate the shell itself — only `command -v memgrep`'s lookup
    # should be governed by the overridden PATH, not the shell's resolution.
    proc = subprocess.run(
        ["/bin/sh", "-c", "command -v memgrep"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    return proc.returncode == 0


def write_note(
    memdir: Path,
    note_type: str,
    slug: str,
    description: str,
    body: str,
) -> Path:
    """Author a schema-valid note `$MEMDIR/<type>_<slug>.md` (write-skill step 4).

    Builds the frontmatter (name/description/metadata.{node_type,type}) + body
    exactly as the skill documents. Returns the written path. Raises on an
    invalid `note_type` (fail-fast — the schema only permits four types).
    """
    if note_type not in VALID_TYPES:
        raise ValueError(f"invalid note type {note_type!r}; must be one of {VALID_TYPES}")
    memdir.mkdir(parents=True, exist_ok=True)
    name = f"{note_type}_{slug}"
    note_path = memdir / f"{name}.md"
    # Build frontmatter with yaml.safe_dump so quoting/escaping is always valid;
    # sort_keys=False keeps the documented field order (name, description, metadata).
    frontmatter = yaml.safe_dump(
        {
            "name": name,
            "description": description,
            "metadata": {"node_type": "memory", "type": note_type},
        },
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    ).rstrip("\n")
    note_path.write_text(f"---\n{frontmatter}\n---\n{body.rstrip(chr(10))}\n", encoding="utf-8")
    return note_path


def append_index_line(memdir: Path, title: str, note_filename: str, hook: str) -> Path:
    """Append the MEMORY.md index line (write-skill step 5), creating it if absent.

    Format: `- [<Title>](<file.md>) — <one-line hook>.`
    """
    memdir.mkdir(parents=True, exist_ok=True)
    index = memdir / "MEMORY.md"
    line = f"- [{title}]({note_filename}) — {hook}\n"
    with index.open("a", encoding="utf-8") as fh:
        fh.write(line)
    return index


def parse_note(note_path: Path) -> tuple[dict, str]:
    """Read a note back: return (frontmatter_dict, body_str). Raises if malformed."""
    text = note_path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"{note_path} has no valid YAML frontmatter block")
    frontmatter = yaml.safe_load(match.group(1))
    body = match.group(2)
    return frontmatter, body


def is_schema_valid(frontmatter: object) -> bool:
    """True iff the frontmatter matches the documented note schema.

    Accepts ``object`` (not ``dict``) because a malformed note's
    ``yaml.safe_load`` can return a non-dict (str/None/list) — the isinstance
    guard below is the real, reachable validation of that case.
    """
    if not isinstance(frontmatter, dict):
        return False
    if not isinstance(frontmatter.get("name"), str) or not frontmatter["name"]:
        return False
    if not isinstance(frontmatter.get("description"), str) or not frontmatter["description"]:
        return False
    meta = frontmatter.get("metadata")
    if not isinstance(meta, dict):
        return False
    if meta.get("node_type") != "memory":
        return False
    if meta.get("type") not in VALID_TYPES:
        return False
    return True
