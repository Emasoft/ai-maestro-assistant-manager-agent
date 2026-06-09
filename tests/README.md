# AMAMA memory-system tests

Tests for the markdown memory system (GitHub issue #11): the
`amama-memory-recall` / `amama-memory-write` skills and the
`rules/memory-protocol.md` rule.

## What is covered

`test_memory_system.py` exercises the **real documented behaviour** (via
`memory_ops.py`, a reference implementation of exactly what the skills
document — not a parallel mock):

- **recall** — the `grep -rliE "$SYMPTOM" "$MEMDIR"` fallback returns ranked
  matching notes; a non-match degrades to an empty list (never an exception);
  an absent memory dir is empty, not an error.
- **write** — `write_note` produces a schema-valid note
  (`name` / `description` / `metadata.{node_type,type}` + body), and
  `append_index_line` adds the `- [Title](file.md) — hook.` line to `MEMORY.md`.
- **schema validation** — `is_schema_valid` rejects malformed frontmatter
  (non-dict, missing fields, wrong `node_type`/`type`).
- **degrade-never-break** — with memgrep off `PATH`, the `command -v memgrep`
  gate reports absent and the grep fallback still recalls the note.
- **cross-repo constraint** — neither skill nor the rule claims memgrep ships
  under this plugin's own root (memgrep is provided by ai-maestro-janitor).

## Run

```bash
cd tests
uv run --with pyyaml --with pytest python -m pytest test_memory_system.py -q
```

Exit code is 0 on all-pass, non-zero on any failure (standard pytest), so the
plugin's pre-publish test gate can invoke it directly.

Dependencies: `pyyaml` (already a plugin dependency) + `pytest`; both are
provided on the fly by `uv run --with`.
