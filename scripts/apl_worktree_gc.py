#!/usr/bin/env python3
"""Garbage-collect disposable PR-review worktrees under ``.worktrees/_reviews``.

Maintainer review checks out each reviewed PR head in a throwaway detached git
worktree under ``<root>/.worktrees/_reviews/``. Those pile up after many reviews
or crashed runs and can exhaust local disk. This command removes only the safe
ones: detached review worktrees older than the age threshold. It never touches a
normal task worktree or a review worktree that has a branch checked out, so it is
safe to run while other agents work on the same machine.

Examples:
    python3 scripts/apl_worktree_gc.py --dry-run
    python3 scripts/apl_worktree_gc.py --older-than-hours 24
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for review-worktree GC."""
    from physics_lab.registry.review_worktree_gc import DEFAULT_GC_AGE_HOURS

    parser = argparse.ArgumentParser(
        description=(
            "Remove abandoned detached PR-review worktrees under "
            ".worktrees/_reviews. Conservative by default: only detached review "
            "worktrees older than the threshold are removed."
        )
    )
    parser.add_argument(
        "--older-than-hours",
        type=float,
        default=DEFAULT_GC_AGE_HOURS,
        help=(
            "Only remove review worktrees at least this many hours old "
            f"(default: {DEFAULT_GC_AGE_HOURS}). Protects recent worktrees that "
            "may belong to a parallel agent."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be removed without deleting anything.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root to clean (default: this checkout).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the review-worktree GC command."""
    from physics_lab.registry.review_worktree_gc import (
        gc_review_worktrees,
        render_gc_report,
    )

    parser = build_parser()
    args = parser.parse_args(argv)
    report = gc_review_worktrees(
        Path(args.root),
        older_than_hours=args.older_than_hours,
        dry_run=args.dry_run,
    )
    print(render_gc_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
