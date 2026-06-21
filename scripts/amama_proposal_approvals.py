#!/usr/bin/env python3
"""
AMAMA Proposal Approvals

Batch-review the TRDD proposals in ``design/proposals/`` and act on them
with the fast user/MANAGER syntax described in
``~/.claude/rules/trdd-approval-tiers.md`` Part A (Batch approval syntax).

Two subcommands:

    list
        Print every pending proposal (``column: proposal``) in
        ``design/proposals/`` as a numbered, one-line-each table sorted by
        ``created:``, and write a manifest that pins each NUMBER to a stable
        ``trdd-id`` for the current listing. The approver then refers to
        proposals by number.

    open
        List the OPEN TRDDs — everything in ``design/tasks/`` (an OPEN TRDD is
        exactly one living there; ``failed``/``blocked`` are OPEN, terminal
        ones are in ``design/archived/``) — plus pending/archived zone counts.

    decide --approved "4,6,22" --refused "7,8"
        Resolve the numbers against the most recent manifest (by stable
        ``trdd-id``, never array position) and act:

        * ``--approved`` only  -> approve exactly those; the rest stay PENDING.
        * ``--refused`` only   -> refuse exactly those AND approve every other
                                   proposal in the listing (bulk complement).
        * both given           -> explicit dual lists; the rest stay PENDING
                                   (an explicit ``--approved`` disables the
                                   refuse-mode complement-approve).

    archive --state {completed|cancelled|superseded} --id <short-or-full-id> …
        Move any TRDD (proposal OR planned task) to ``design/archived/`` in a
        terminal-DONE state. ``cancel`` is the alias for ``--state cancelled``.
        ``failed`` is NOT an archive state — a failed TRDD is retryable and
        stays OPEN in ``design/tasks/``.

Approve  = set ``column: planned``, append an ``## Approval log`` line, bump
           ``updated:``, ``git mv`` the file into ``design/tasks/``.
Refuse   = set ``column: refused``, append the log line, bump ``updated:``,
           ``git mv`` the file into ``design/refused/`` (never deleted —
           RULE 0 audit trail). Only NEVER-approved proposals are refused.
Archive  = set ``column: <completed|cancelled|superseded>``, append the log
           line, bump ``updated:``, ``git mv`` into ``design/archived/``.

Frontmatter is mutated with SURGICAL line edits (not a YAML round-trip) so the
TRDD grep-invariants — one field per line, flow-style lists, field order — are
preserved verbatim. Stdlib only.

Usage:
    python3 amama_proposal_approvals.py list [--json] [--root DIR]
    python3 amama_proposal_approvals.py decide --approved "4,6,2" [--json]
    python3 amama_proposal_approvals.py decide --refused "7,8" [--dry-run]
    python3 amama_proposal_approvals.py decide --approved "1,2" --refused "9"
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from amama_atomic_write import atomic_write

# Frontmatter is the block between the first two `---` fences at file start.
_FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
_APPROVAL_HEADER_RE = re.compile(r"(?m)^## Approval log[ \t]*$")
_NEXT_H2_RE = re.compile(r"(?m)^## ")

PENDING_COLUMN = "proposal"
APPROVED_COLUMN = "planned"
REFUSED_COLUMN = "refused"

# Terminal-DONE states that live in design/archived/ (NEVER `failed` —
# failed is retryable and stays OPEN in design/tasks/).
ARCHIVE_STATES = ("completed", "cancelled", "superseded")

MANIFEST_COMPONENT = "proposal-approvals"
MANIFEST_NAME = "latest-index.json"


# --------------------------------------------------------------------------- #
# Time helpers (local time + GMT offset, per the repo-wide timestamp rule)
# --------------------------------------------------------------------------- #
def iso_now() -> str:
    """ISO 8601 local datetime with compact ``+HHMM`` offset (TRDD `updated:`)."""
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def ts_now() -> str:
    """Filesystem-safe local timestamp with offset (report filenames)."""
    return datetime.now().astimezone().strftime("%Y%m%d_%H%M%S%z")


# --------------------------------------------------------------------------- #
# Path resolution
# --------------------------------------------------------------------------- #
def project_root(explicit: str | None) -> Path:
    """Resolve the project root: --root, else CLAUDE_PROJECT_DIR, else git top, else cwd."""
    if explicit:
        return Path(explicit).resolve()
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env).resolve()
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return Path(out.stdout.strip()).resolve()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd().resolve()


def proposals_dir(root: Path) -> Path:
    return root / "design" / "proposals"


def tasks_dir(root: Path) -> Path:
    return root / "design" / "tasks"


def refused_dir(root: Path) -> Path:
    # Top-level design/refused/ — proposals that were NEVER approved.
    return root / "design" / "refused"


def archived_dir(root: Path) -> Path:
    # design/archived/ — ONLY once-approved TRDDs (completed/cancelled/superseded).
    return root / "design" / "archived"


def manifest_dir(root: Path) -> Path:
    return root / "reports" / MANIFEST_COMPONENT


# --------------------------------------------------------------------------- #
# Frontmatter parsing + surgical mutation
# --------------------------------------------------------------------------- #
def parse_frontmatter(text: str) -> dict[str, str]:
    """Return top-level scalar fields from the `---` block (one field per line)."""
    m = _FM_RE.match(text)
    if not m:
        return {}
    fields: dict[str, str] = {}
    for line in m.group(1).split("\n"):
        fm = re.match(r"^([A-Za-z0-9_-]+):\s?(.*)$", line)
        if fm:
            fields[fm.group(1)] = fm.group(2).strip()
    return fields


def set_frontmatter_field(text: str, field: str, value: str) -> str:
    """Replace (or add) a scalar field INSIDE the frontmatter block only."""
    m = _FM_RE.match(text)
    if not m:
        raise ValueError("file has no YAML frontmatter block")
    out_lines: list[str] = []
    found = False
    for line in m.group(1).split("\n"):
        if re.match(rf"^{re.escape(field)}:(\s|$)", line):
            out_lines.append(f"{field}: {value}")
            found = True
        else:
            out_lines.append(line)
    if not found:
        out_lines.append(f"{field}: {value}")
    new_fm = "\n".join(out_lines)
    return text[: m.start(1)] + new_fm + text[m.end(1):]


def append_approval_log(text: str, bullet: str) -> str:
    """Append a bullet to the body's `## Approval log` section (create if absent)."""
    m = _APPROVAL_HEADER_RE.search(text)
    if not m:
        sep = "" if text.endswith("\n") else "\n"
        return f"{text}{sep}\n## Approval log\n\n{bullet}\n"
    section_start = m.end()
    nxt = _NEXT_H2_RE.search(text, section_start)
    end = nxt.start() if nxt else len(text)
    block = text[section_start:end].rstrip("\n")
    new_block = f"{block}\n{bullet}\n"
    return text[:section_start] + new_block + text[end:]


# --------------------------------------------------------------------------- #
# Proposal model + listing
# --------------------------------------------------------------------------- #
@dataclass
class Proposal:
    """One TRDD file with the metadata the listing/decision/status needs."""

    n: int
    trdd_id: str
    short: str
    file: str          # path relative to root, POSIX style
    title: str
    tier: str
    column: str
    created: str
    blocked_by: str = ""   # raw flow-style list value, e.g. "[TRDD-9a8aba94]"
    assignee: str = ""


def read_proposal(path: Path, root: Path) -> Proposal | None:
    """Parse a proposal file; return None if it has no usable frontmatter."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    fm = parse_frontmatter(text)
    if not fm:
        return None
    trdd_id = fm.get("trdd-id", "")
    return Proposal(
        n=0,
        trdd_id=trdd_id,
        short=trdd_id[:8] if trdd_id else "????????",
        file=path.relative_to(root).as_posix(),
        title=fm.get("title", "(untitled)"),
        tier=fm.get("approval-tier", "—"),
        column=fm.get("column", ""),
        created=fm.get("created", ""),
        blocked_by=fm.get("blocked-by", ""),
        assignee=fm.get("assignee", ""),
    )


def list_pending(root: Path) -> list[Proposal]:
    """All `column: proposal` files directly in design/proposals/, numbered by created:."""
    pdir = proposals_dir(root)
    if not pdir.is_dir():
        return []
    found: list[Proposal] = []
    for path in sorted(pdir.glob("*.md")):  # non-recursive: skips refused/
        if path.name.lower() == "readme.md":
            continue
        prop = read_proposal(path, root)
        if prop is None or prop.column != PENDING_COLUMN:
            continue
        found.append(prop)
    found.sort(key=lambda p: (p.created, p.file))
    for i, prop in enumerate(found, start=1):
        prop.n = i
    return found


def list_open(root: Path) -> list[Proposal]:
    """All OPEN TRDDs = everything in design/tasks/ (any column; the zone invariant).

    `failed` and `blocked` are OPEN (retryable / waiting), not terminal — terminal
    TRDDs live in design/archived/ and never appear here.
    """
    tdir = tasks_dir(root)
    if not tdir.is_dir():
        return []
    found: list[Proposal] = []
    for path in sorted(tdir.glob("*.md")):  # non-recursive
        if path.name.lower() == "readme.md":
            continue
        prop = read_proposal(path, root)
        if prop is None:
            continue
        found.append(prop)
    found.sort(key=lambda p: (p.column, p.created, p.file))
    for i, prop in enumerate(found, start=1):
        prop.n = i
    return found


def list_unparsed(root: Path, folder: Path) -> list[str]:
    """.md files with no parseable v2 frontmatter (legacy / broken).

    These are SURFACED, never silently dropped — an open TRDD the tool cannot
    parse (e.g. a pre-frontmatter legacy TRDD) must still be visible to the
    MANAGER so the "all open TRDDs" claim stays honest. They need v2-frontmatter
    migration (see ~/.claude/rules/trdd-design-tasks.md "Migration from v1").
    """
    if not folder.is_dir():
        return []
    out: list[str] = []
    for path in sorted(folder.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        try:
            if not parse_frontmatter(path.read_text(encoding="utf-8")):
                out.append(path.relative_to(root).as_posix())
        except OSError:
            out.append(path.relative_to(root).as_posix())
    return out


# --------------------------------------------------------------------------- #
# Manifest (number -> stable trdd-id)
# --------------------------------------------------------------------------- #
def write_manifest(root: Path, items: list[Proposal]) -> Path:
    """Persist the current listing so `decide` can resolve numbers later."""
    mdir = manifest_dir(root)
    mdir.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated": iso_now(),
        "root": str(root),
        "items": [asdict(p) for p in items],
    }
    target = mdir / MANIFEST_NAME
    atomic_write(target, json.dumps(payload, indent=2))
    return target


def read_manifest(root: Path) -> dict:
    """Load the most recent listing manifest, or raise if none exists."""
    target = manifest_dir(root) / MANIFEST_NAME
    if not target.is_file():
        raise FileNotFoundError(
            "no proposal listing manifest — run `list` first so numbers resolve"
        )
    return json.loads(target.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# Number parsing ("4,6,22" and "1-5" ranges)
# --------------------------------------------------------------------------- #
def parse_numbers(spec: str | None) -> list[int]:
    """Parse a comma list with optional N-M ranges into a sorted unique int list."""
    if not spec:
        return []
    nums: set[int] = set()
    for tok in spec.replace(" ", "").split(","):
        if not tok:
            continue
        rng = re.fullmatch(r"(\d+)-(\d+)", tok)
        if rng:
            lo, hi = int(rng.group(1)), int(rng.group(2))
            if lo > hi:
                lo, hi = hi, lo
            nums.update(range(lo, hi + 1))
        elif tok.isdigit():
            nums.add(int(tok))
        else:
            raise ValueError(f"bad number token: {tok!r}")
    return sorted(nums)


# --------------------------------------------------------------------------- #
# File move (git mv when tracked, filesystem rename otherwise)
# --------------------------------------------------------------------------- #
def _is_tracked(root: Path, path: Path) -> bool:
    r = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--error-unmatch", str(path)],
        capture_output=True, text=True,
    )
    return r.returncode == 0


def move_file(root: Path, src: Path, dest: Path) -> str:
    """Move src->dest; prefer `git mv` (stages the rename), fall back to fs rename."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        raise FileExistsError(f"destination already exists: {dest}")
    if _is_tracked(root, src):
        r = subprocess.run(
            ["git", "-C", str(root), "mv", str(src), str(dest)],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            return "git"
    src.rename(dest)
    return "fs"


# --------------------------------------------------------------------------- #
# Apply a single decision
# --------------------------------------------------------------------------- #
def apply_move(
    root: Path, src: Path, *, target_col: str, dest_dir: Path, verb: str,
    approver: str, tier: str, reason: str,
) -> dict:
    """Mutate frontmatter (column + updated) + append the log line, then move the file."""
    dest = dest_dir / src.name
    original = src.read_text(encoding="utf-8")
    text = set_frontmatter_field(original, "column", target_col)
    text = set_frontmatter_field(text, "updated", iso_now())
    bullet = f"- {iso_now()} — {verb} by {approver} (tier {tier}). {reason}"
    text = append_approval_log(text, bullet)
    # Mutate the source atomically, then move. If the move fails, RESTORE the
    # pre-mutation content so a failed decision never strands a mutated file in
    # the source zone (e.g. a `planned`-column file still in design/proposals/) —
    # F7. The rollback's own error is suppressed so the ORIGINAL move failure is
    # what propagates (fail-fast), not a secondary rollback error.
    atomic_write(src, text)
    try:
        kind = move_file(root, src, dest)
    except BaseException:
        with contextlib.suppress(OSError):
            atomic_write(src, original)
        raise
    return {
        "verb": verb.lower(),
        "from": src.relative_to(root).as_posix(),
        "to": dest.relative_to(root).as_posix(),
        "move": kind,
    }


# --------------------------------------------------------------------------- #
# decide orchestration
# --------------------------------------------------------------------------- #
def build_plan(manifest: dict, approved: list[int], refused: list[int]) -> dict:
    """Resolve the approve/refuse number sets per the batch-approval semantics."""
    items_by_n = {int(it["n"]): it for it in manifest["items"]}
    known = set(items_by_n)

    approve_set = set(approved)
    refuse_set = set(refused)

    overlap = approve_set & refuse_set
    if overlap:
        raise ValueError(f"numbers appear in BOTH approved and refused: {sorted(overlap)}")

    unknown = sorted((approve_set | refuse_set) - known)

    complement_used = False
    if refuse_set and not approve_set:
        # refused-only: approve every OTHER listed proposal (bulk complement)
        approve_set = known - refuse_set
        complement_used = True

    return {
        "items_by_n": items_by_n,
        "approve": sorted(approve_set & known),
        "refuse": sorted(refuse_set & known),
        "unknown": unknown,
        "complement_used": complement_used,
    }


def decide(
    root: Path, approved: list[int], refused: list[int],
    approver: str, reason_approve: str, reason_refuse: str, dry_run: bool,
) -> dict:
    """Execute (or preview) the resolved plan against the current pending set."""
    manifest = read_manifest(root)
    plan = build_plan(manifest, approved, refused)
    items_by_n = plan["items_by_n"]

    # Current pending files keyed by stable trdd-id (robust to filename).
    pending = {p.trdd_id: p for p in list_pending(root)}

    results: list[dict] = []
    skipped: list[dict] = []

    def act(n: int, approve: bool) -> None:
        it = items_by_n[n]
        prop = pending.get(it["trdd_id"])
        if prop is None:
            skipped.append({
                "n": n, "short": it.get("short", "?"),
                "title": it.get("title", ""),
                "why": "already decided or no longer pending",
            })
            return
        src = root / prop.file
        if dry_run:
            verb = "approve" if approve else "refuse"
            dest = (tasks_dir(root) if approve else refused_dir(root)) / src.name
            results.append({
                "verb": verb, "n": n, "short": prop.short, "title": prop.title,
                "from": prop.file, "to": dest.relative_to(root).as_posix(),
                "move": "(dry-run)",
            })
            return
        if approve:
            rec = apply_move(
                root, src, target_col=APPROVED_COLUMN, dest_dir=tasks_dir(root),
                verb="APPROVED", approver=approver, tier=prop.tier, reason=reason_approve,
            )
        else:
            rec = apply_move(
                root, src, target_col=REFUSED_COLUMN, dest_dir=refused_dir(root),
                verb="REFUSED", approver=approver, tier=prop.tier, reason=reason_refuse,
            )
        rec.update({"n": n, "short": prop.short, "title": prop.title})
        results.append(rec)

    for n in plan["approve"]:
        act(n, approve=True)
    for n in plan["refuse"]:
        act(n, approve=False)

    return {
        "approved": [r for r in results if r["verb"] == "approve" or r["verb"] == "approved"],
        "refused": [r for r in results if r["verb"] == "refuse" or r["verb"] == "refused"],
        "skipped": skipped,
        "unknown": plan["unknown"],
        "complement_used": plan["complement_used"],
        "dry_run": dry_run,
    }


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
def render_table(items: list[Proposal]) -> str:
    """Succinct numbered listing the user scans at a glance."""
    if not items:
        return "No pending proposals in design/proposals/."
    title_w = max(len(p.title) for p in items)
    title_w = min(title_w, 72)
    head = f"{'#':>3}  {'id':<8}  {'tier':<4}  title"
    rule = f"{'─' * 3}  {'─' * 8}  {'─' * 4}  {'─' * min(title_w, 72)}"
    rows = [head, rule]
    for p in items:
        title = p.title if len(p.title) <= title_w else p.title[: title_w - 1] + "…"
        rows.append(f"{p.n:>3}  {p.short:<8}  {p.tier:<4}  {title}")
    rows.append("")
    rows.append(f"{len(items)} pending. Reply: `approved: N,N` or `refused: N,N`.")
    return "\n".join(rows)


def write_decision_report(root: Path, outcome: dict) -> Path:
    """Archive the decision outcome under the gitignored reports/ tree."""
    mdir = manifest_dir(root)
    mdir.mkdir(parents=True, exist_ok=True)
    report = mdir / f"{ts_now()}-decision.md"
    lines = [f"# Proposal decision — {iso_now()}", ""]
    if outcome["dry_run"]:
        lines.append("**DRY RUN — nothing was changed.**\n")
    if outcome["complement_used"]:
        lines.append("_Refused-only mode: every other listed proposal was approved by complement._\n")
    for label, key in (("Approved", "approved"), ("Refused", "refused")):
        recs = outcome[key]
        lines.append(f"## {label} ({len(recs)})")
        if not recs:
            lines.append("_none_")
        for r in recs:
            lines.append(f"- #{r['n']} `{r['short']}` — {r['title']}  →  `{r['to']}` ({r['move']})")
        lines.append("")
    if outcome["skipped"]:
        lines.append(f"## Skipped ({len(outcome['skipped'])})")
        for s in outcome["skipped"]:
            lines.append(f"- #{s['n']} `{s['short']}` — {s['title']}  ({s['why']})")
        lines.append("")
    if outcome["unknown"]:
        lines.append(f"## Unknown numbers (not in manifest): {outcome['unknown']}")
        lines.append("")
    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def render_outcome(outcome: dict) -> str:
    """Human after-action summary for the terminal."""
    out: list[str] = []
    if outcome["dry_run"]:
        out.append("DRY RUN — no files changed.")
    if outcome["complement_used"]:
        out.append("Refused-only: all other listed proposals approved by complement.")
    out.append(f"Approved: {len(outcome['approved'])}   Refused: {len(outcome['refused'])}"
               f"   Skipped: {len(outcome['skipped'])}")
    for r in outcome["approved"]:
        out.append(f"  ✓ #{r['n']} {r['short']} → {r['to']}")
    for r in outcome["refused"]:
        out.append(f"  ✗ #{r['n']} {r['short']} → {r['to']}")
    for s in outcome["skipped"]:
        out.append(f"  – #{s['n']} {s['short']} skipped ({s['why']})")
    if outcome["unknown"]:
        out.append(f"  ! unknown numbers (not in listing): {outcome['unknown']}")
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def render_open(items: list[Proposal], pending: int, archived: int,
                unparsed: list[str] | None = None) -> str:
    """The OPEN-work picture for one project (the exact open-TRDD list + zone counts)."""
    unparsed = unparsed or []
    blocked = [p for p in items if p.column == "blocked"]
    failed = [p for p in items if p.column == "failed"]
    total_open = len(items) + len(unparsed)
    head = (f"OPEN TRDDs (design/tasks/): {total_open}  "
            f"(🔴 blocked: {len(blocked)}  ⚠ failed: {len(failed)}"
            + (f"  ❓ unparsed: {len(unparsed)}" if unparsed else "") + ")  "
            f"|  pending proposals: {pending}  |  archived: {archived}")
    if not items and not unparsed:
        return head + "\n  (no open TRDDs)"
    rows = [head, ""]
    if items:
        col_w = max(len(p.column) for p in items)
        for p in items:
            flag = "  ⚠ retry" if p.column == "failed" else ("  🔴" if p.column == "blocked" else "")
            rows.append(f"  {p.short}  {p.column:<{col_w}}  {p.title}{flag}")
    if blocked:
        rows.append("")
        rows.append(f"🔴 BLOCKED ({len(blocked)}) — blockers:")
        for p in blocked:
            blockers = p.blocked_by or "(blocked-by not recorded)"
            rows.append(f"  {p.short}  {p.title}  ← {blockers}")
    if unparsed:
        rows.append("")
        rows.append(f"❓ UNPARSED / legacy ({len(unparsed)}) — OPEN but no v2 frontmatter; migrate:")
        for f in unparsed:
            rows.append(f"  {f}")
    return "\n".join(rows)


def cmd_list(args: argparse.Namespace) -> int:
    root = project_root(args.root)
    items = list_pending(root)
    write_manifest(root, items)
    if args.json:
        print(json.dumps({"root": str(root), "items": [asdict(p) for p in items]}, indent=2))
    else:
        print(render_table(items))
    return 0


def cmd_open(args: argparse.Namespace) -> int:
    """List the OPEN TRDDs (design/tasks/) plus pending/archived zone counts."""
    root = project_root(args.root)
    items = list_open(root)
    unparsed = list_unparsed(root, tasks_dir(root))
    pending = len(list_pending(root))
    adir = archived_dir(root)
    archived = len(list(adir.glob("*.md"))) if adir.is_dir() else 0
    if args.json:
        print(json.dumps({
            "root": str(root),
            "open": [asdict(p) for p in items],
            "open_unparsed": unparsed,
            "pending_proposals": pending,
            "archived": archived,
        }, indent=2))
    else:
        print(render_open(items, pending, archived, unparsed))
    return 0


def find_in(folder: Path, ident: str) -> Path | None:
    """Locate a TRDD by full trdd-id or 8-char short id within one folder (non-recursive)."""
    if not folder.is_dir():
        return None
    for path in sorted(folder.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        try:
            fm = parse_frontmatter(path.read_text(encoding="utf-8"))
        except OSError:
            continue  # unreadable (perms/race/broken symlink) can't be the target — skip, don't crash the search (F6)
        tid = fm.get("trdd-id", "")
        if tid and (tid == ident or tid[:8] == ident):
            return path
    return None


def cmd_archive(args: argparse.Namespace) -> int:
    """Archive once-approved TRDD(s) from design/tasks/ → design/archived/ (terminal-DONE)."""
    root = project_root(args.root)
    state = (getattr(args, "state", None) or "cancelled").lower()
    if state not in ARCHIVE_STATES:
        print(f"ERROR: --state must be one of {ARCHIVE_STATES} (NOT 'failed' — "
              f"failed stays OPEN in design/tasks/ and is retried)", file=sys.stderr)
        return 2
    results: list[dict] = []
    missing: list[str] = []
    redirect: list[str] = []   # pending proposals — must be refused, not archived
    for ident in args.id:
        path = find_in(tasks_dir(root), ident)   # ONLY approved tasks reach archived/
        if path is None:
            if find_in(proposals_dir(root), ident) is not None:
                redirect.append(ident)   # it's still a proposal → refuse it instead
            else:
                missing.append(ident)
            continue
        try:
            fm = parse_frontmatter(path.read_text(encoding="utf-8"))
        except OSError:
            # Found by find_in but unreadable now (race / perms) — surface as
            # unprocessed instead of crashing mid-batch (which would leave earlier
            # moves already applied). F6.
            missing.append(ident)
            continue
        tier = fm.get("approval-tier", "—")
        if args.dry_run:
            dest = archived_dir(root) / path.name
            results.append({
                "verb": state, "short": fm.get("trdd-id", "")[:8],
                "title": fm.get("title", ""),
                "from": path.relative_to(root).as_posix(),
                "to": dest.relative_to(root).as_posix(), "move": "(dry-run)",
            })
            continue
        rec = apply_move(
            root, path, target_col=state, dest_dir=archived_dir(root),
            verb=state.upper(), approver=args.approver, tier=tier,
            reason=args.reason or f"{state.capitalize()} via amama-proposal-approvals skill.",
        )
        rec.update({"short": fm.get("trdd-id", "")[:8], "title": fm.get("title", "")})
        results.append(rec)
    if args.json:
        print(json.dumps({"archived": results, "state": state,
                          "redirect_to_refuse": redirect, "missing": missing}, indent=2))
    else:
        for r in results:
            print(f"  ⊗ {r['short']} → {r['to']}  [{state}]  ({r['title']})")
        for ident in redirect:
            print(f"  ↩ {ident} is a pending PROPOSAL (never approved) — refuse it "
                  f"(→ design/refused/), don't archive it.")
        for ident in missing:
            print(f"  ! not found in design/tasks/: {ident}")
        if not args.dry_run and results:
            print("\nReview `git status`, then commit the moves when ready.")
    return 0 if not (missing or redirect) else 1


def cmd_decide(args: argparse.Namespace) -> int:
    root = project_root(args.root)
    if not args.approved and not args.refused:
        print("ERROR: pass --approved and/or --refused", file=sys.stderr)
        return 2
    approved = parse_numbers(args.approved)
    refused = parse_numbers(args.refused)
    try:
        outcome = decide(
            root, approved, refused,
            approver=args.approver,
            reason_approve=args.reason or "Batch approval via amama-proposal-approvals skill.",
            reason_refuse=args.reason or "Batch refusal via amama-proposal-approvals skill.",
            dry_run=args.dry_run,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    report = None
    if not args.dry_run:
        report = write_decision_report(root, outcome)
    if args.json:
        payload = dict(outcome)
        if report:
            payload["report"] = str(report)
        print(json.dumps(payload, indent=2))
    else:
        print(render_outcome(outcome))
        if report:
            print(f"\nReport: {report}")
        if not args.dry_run and (outcome["approved"] or outcome["refused"]):
            print("\nReview `git status`, then commit the moves when ready.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Batch-review design/proposals/ TRDDs.")
    parser.add_argument("--root", help="Project root (default: CLAUDE_PROJECT_DIR / git top / cwd)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List pending proposals + write the manifest")
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_open = sub.add_parser("open", help="List OPEN TRDDs (design/tasks/) + zone counts")
    p_open.add_argument("--json", action="store_true")
    p_open.set_defaults(func=cmd_open)

    p_dec = sub.add_parser("decide", help="Approve/refuse proposals by number")
    p_dec.add_argument("--approved", help='Numbers to approve, e.g. "4,6,22" or "1-5"')
    p_dec.add_argument("--refused", help='Numbers to refuse (refused-only approves the rest)')
    p_dec.add_argument("--approver", default=os.environ.get("AMAMA_APPROVER", "USER"),
                       help="Who is deciding (default: USER)")
    p_dec.add_argument("--reason", help="Custom one-line rationale for the log")
    p_dec.add_argument("--dry-run", action="store_true", help="Show the plan, change nothing")
    p_dec.add_argument("--json", action="store_true")
    p_dec.set_defaults(func=cmd_decide)

    def _add_archive_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--id", nargs="+", required=True,
                       help="TRDD id(s): full trdd-id or 8-char short id (proposal or task)")
        p.add_argument("--approver", default=os.environ.get("AMAMA_APPROVER", "USER"))
        p.add_argument("--reason", help="Custom one-line reason for the log")
        p.add_argument("--dry-run", action="store_true", help="Show the plan, change nothing")
        p.add_argument("--json", action="store_true")

    p_arch = sub.add_parser("archive", help="Archive TRDD(s) → design/archived/ (terminal-DONE)")
    p_arch.add_argument("--state", choices=ARCHIVE_STATES, default="cancelled",
                        help="terminal state (default: cancelled). NEVER 'failed' (retryable, stays OPEN)")
    _add_archive_args(p_arch)
    p_arch.set_defaults(func=cmd_archive)

    # `cancel` is the convenience alias for `archive --state cancelled`.
    p_can = sub.add_parser("cancel", help="Alias for `archive --state cancelled`")
    _add_archive_args(p_can)
    p_can.set_defaults(func=cmd_archive, state="cancelled")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
