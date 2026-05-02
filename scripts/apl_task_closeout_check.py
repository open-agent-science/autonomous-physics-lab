#!/usr/bin/env python3
"""Lightweight maintainer helper for task closeout readiness."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for the closeout helper."""
    parser = argparse.ArgumentParser(
        description="Print a deterministic task closeout snapshot without editing files."
    )
    parser.add_argument("--task", required=True, help="Task id, for example TASK-0033")
    parser.add_argument(
        "--suggest",
        action="store_true",
        help="Print suggested file updates without applying them.",
    )
    return parser


def main() -> int:
    """Run the closeout helper."""
    from physics_lab.registry.task_closeout import (
        build_closeout_report,
        render_closeout_report,
    )

    parser = build_parser()
    args = parser.parse_args()
    report = build_closeout_report(REPO_ROOT, args.task)
    print(render_closeout_report(report, suggest=args.suggest, root=REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
