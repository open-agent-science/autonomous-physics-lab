#!/usr/bin/env python3
"""Deterministic maintainer helper for post-merge task closeout."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for task closeout."""
    parser = argparse.ArgumentParser(
        description="Check or apply maintainer task closeout after merge."
    )
    parser.add_argument("--task", required=True, help="Task id, for example TASK-0034.")
    parser.add_argument("--pr", required=True, type=int, help="Merged pull request number.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply task closeout changes on main after checks pass.",
    )
    parser.add_argument(
        "--sync-board",
        action="store_true",
        help="Also regenerate tasks/ACTIVE.md during apply mode. Leave unset for lower-conflict YAML-only closeout.",
    )
    return parser


def main() -> int:
    """Run the task closeout helper."""
    from physics_lab.registry.maintainer_review import (
        build_closeout_report,
        render_closeout_report,
    )

    parser = build_parser()
    args = parser.parse_args()
    report = build_closeout_report(
        REPO_ROOT,
        task_id=args.task,
        pull_request=args.pr,
        apply=args.apply,
        sync_board=args.sync_board,
    )
    print(render_closeout_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
