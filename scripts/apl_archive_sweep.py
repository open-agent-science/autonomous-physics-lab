#!/usr/bin/env python3
"""Archive terminal canonical task files into id-range buckets (reusable sweep).

The reusable, idempotent mechanism for the periodic task-archive sweep (see
docs/task-archive-migration-plan.md). Run it on a threshold (too many terminal
tasks sitting flat under tasks/) or on a monthly cadence -- NOT per task close.

Because the repository references tasks by id, not by path
(docs/task-reference-convention.md), this is a pure ``git mv``: it moves files
and does not rewrite any references.

What it does:
  * finds terminal tasks (DONE / SUPERSEDED / REJECTED) still flat directly
    under tasks/ (never touches already-archived, active, proposals, or
    microtasks);
  * moves each into its id-range bucket tasks/archive/<lo>-<hi>/ via ``git mv``
    (bucket = id // 500, a pure function of the immutable id);
  * warns (does not block) about any lingering literal ``tasks/<name>`` path
    references to moved files, so convention drift is visible.

Always preview with --dry-run first.

Examples::

    python3 scripts/apl_archive_sweep.py --dry-run
    python3 scripts/apl_archive_sweep.py --limit 50
    python3 scripts/apl_archive_sweep.py
"""
from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml

TERMINAL_STATUSES = ("DONE", "SUPERSEDED", "REJECTED")
BUCKET_SIZE = 500
ARCHIVE_DIRNAME = "archive"
CANONICAL_RE = re.compile(r"^TASK-(\d{4,})-")
# These legitimately discuss task paths; never warn about them.
REF_SCAN_EXCLUDE = {
    "docs/task-archive-migration-plan.md",
    "docs/task-reference-convention.md",
}
# tasks/ cross-references (related_objects) are opaque, tolerated metadata and
# are not existence-checked, so they are not flagged here.
REF_SCAN_EXCLUDE_PREFIXES = ("docs/task-views/", "tasks/")
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".txt"}


@dataclass(frozen=True)
class Move:
    task_id: str
    old_rel: str
    new_rel: str


def bucket_name(task_id: str) -> str:
    number = int(task_id.split("-")[1])
    lo = (number // BUCKET_SIZE) * BUCKET_SIZE
    return f"{lo:04d}-{lo + BUCKET_SIZE - 1:04d}"


def _status(path: Path) -> str | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    if isinstance(data, dict) and data.get("status") is not None:
        return str(data["status"])
    return None


def plan_moves(root: Path, statuses: tuple[str, ...], limit: int | None) -> list[Move]:
    tasks_dir = root / "tasks"
    moves: list[Move] = []
    for path in sorted(tasks_dir.glob("TASK-[0-9][0-9][0-9][0-9]-*.yaml")):
        match = CANONICAL_RE.match(path.name)
        if not match or _status(path) not in statuses:
            continue
        task_id = f"TASK-{match.group(1)}"
        new_rel = f"tasks/{ARCHIVE_DIRNAME}/{bucket_name(task_id)}/{path.name}"
        moves.append(Move(task_id, f"tasks/{path.name}", new_rel))
        if limit is not None and len(moves) >= limit:
            break
    return moves


def apply_moves(root: Path, moves: list[Move]) -> None:
    for move in moves:
        (root / move.new_rel).parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "-C", str(root), "mv", move.old_rel, move.new_rel], check=True)


def lingering_path_references(root: Path, moves: list[Move]) -> list[str]:
    """Warn-only: literal tasks/<name> references to moved files still present."""
    moved_paths = {m.old_rel for m in moves}
    tracked = subprocess.run(
        ["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True
    ).stdout.splitlines()
    hits: list[str] = []
    for rel in tracked:
        if rel in REF_SCAN_EXCLUDE or any(rel.startswith(p) for p in REF_SCAN_EXCLUDE_PREFIXES):
            continue
        if Path(rel).suffix not in TEXT_SUFFIXES:
            continue
        try:
            text = (root / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for old_rel in moved_paths:
            if old_rel in text:
                hits.append(f"{rel}: {old_rel}")
    return sorted(set(hits))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    parser.add_argument("--dry-run", action="store_true", help="preview without moving")
    parser.add_argument("--limit", type=int, default=None, help="cap the number of tasks moved this run")
    parser.add_argument(
        "--status", nargs="+", default=list(TERMINAL_STATUSES),
        help=f"terminal statuses to archive (default: {' '.join(TERMINAL_STATUSES)})",
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    moves = plan_moves(root, tuple(args.status), args.limit)
    if not moves:
        print("No flat terminal tasks to archive. Nothing to do.")
        return 0

    by_bucket: dict[str, int] = {}
    for move in moves:
        bucket = Path(move.new_rel).parent.name
        by_bucket[bucket] = by_bucket.get(bucket, 0) + 1

    label = "DRY-RUN: would archive" if args.dry_run else "Archiving"
    print(f"{label} {len(moves)} terminal task(s) into {len(by_bucket)} bucket(s):")
    for bucket in sorted(by_bucket):
        print(f"  tasks/archive/{bucket}/  <- {by_bucket[bucket]} file(s)")

    if not args.dry_run:
        apply_moves(root, moves)

    warnings = lingering_path_references(root, moves)
    if warnings:
        print(f"\nWARNING: {len(warnings)} lingering literal task-path reference(s) to moved files "
              "(reference tasks by id; see docs/task-reference-convention.md):")
        for hit in warnings:
            print(f"  {hit}")

    if args.dry_run:
        print("\n(Dry run — no files changed.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
