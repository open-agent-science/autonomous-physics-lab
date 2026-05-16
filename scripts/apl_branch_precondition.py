#!/usr/bin/env python3
"""Branch + working-tree precondition check for APL agent sessions.

Agents should run this script before any ``git add`` / ``git commit`` /
``git push`` to catch two common failure modes early:

1. **Wrong branch.** A parallel session may have switched HEAD without
   the agent noticing (see the TASK-0227 / TASK-0251 incident). The
   check exits non-zero when HEAD does not match the expected branch.

2. **Surprise working-tree changes.** Modified or untracked files that
   the agent did not produce are usually the symptom of cross-session
   contamination. The check filters known harness state via
   ``HARNESS_IGNORE_PATHS`` and an optional ``--allow-untracked`` glob
   list, then exits non-zero when anything else is dirty.

Usage:

    python3 scripts/apl_branch_precondition.py \\
        --expected-branch agent/roman/claude/task-0263-foo \\
        --allow-untracked "docs/notes/draft-*.md"

Exit codes:

    0 — all checks pass
    1 — branch mismatch or unexpected working-tree changes
    2 — invalid arguments

The script is opt-in and additive. It does not modify the working tree.
"""

from __future__ import annotations

import argparse
import fnmatch
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.registry.review_git import (  # noqa: E402
    HARNESS_IGNORE_PATHS,
    current_branch,
    working_tree_changed_files,
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="APL agent branch + working-tree precondition check.",
    )
    parser.add_argument(
        "--expected-branch",
        required=True,
        help="The branch the agent expects to be on (e.g. agent/<id>/<agent>/task-XXXX-slug).",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root (default: current directory).",
    )
    parser.add_argument(
        "--allow-untracked",
        action="append",
        default=[],
        metavar="PATTERN",
        help=(
            "Glob pattern (fnmatch-style) for additional untracked paths the agent "
            "expects to see. Can be passed multiple times."
        ),
    )
    parser.add_argument(
        "--allow-modified",
        action="append",
        default=[],
        metavar="PATTERN",
        help=(
            "Glob pattern (fnmatch-style) for additional modified paths the agent "
            "expects. Can be passed multiple times."
        ),
    )
    return parser.parse_args(argv)


def _filter_paths(paths: tuple[str, ...], patterns: list[str]) -> tuple[str, ...]:
    """Drop paths matching any of the fnmatch-style patterns."""
    if not patterns:
        return paths
    return tuple(
        path
        for path in paths
        if not any(fnmatch.fnmatch(path, pattern) for pattern in patterns)
    )


def run(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    actual_branch = current_branch(root)
    failures: list[str] = []

    if actual_branch != args.expected_branch:
        failures.append(
            f"Branch mismatch: expected {args.expected_branch!r}, on {actual_branch!r}."
        )

    # working_tree_changed_files already filters HARNESS_IGNORE_PATHS by default.
    dirty_paths = working_tree_changed_files(root, ignore_paths=HARNESS_IGNORE_PATHS)
    # Apply additional caller-supplied allowlists.
    allow_patterns = list(args.allow_untracked) + list(args.allow_modified)
    surprise_paths = _filter_paths(dirty_paths, allow_patterns)
    if surprise_paths:
        joined = ", ".join(surprise_paths)
        failures.append(
            f"Working tree has unexpected changes: {joined}. "
            "Stash, commit, or pass --allow-untracked / --allow-modified for each expected path."
        )

    if failures:
        print("Branch precondition FAILED:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"Branch precondition OK: on {actual_branch}, no surprise files.")
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parse_args(argv)
    except SystemExit as exc:
        # argparse exits with code 2 on parse errors; preserve that.
        return int(exc.code) if exc.code is not None else 2
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
