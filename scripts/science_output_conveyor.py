#!/usr/bin/env python3
"""Build an advisory science-output conveyor health report."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.registry.science_output_conveyor import (  # noqa: E402
    build_science_output_conveyor_report,
    render_science_output_conveyor_markdown,
    science_output_conveyor_json,
)


def build_parser() -> argparse.ArgumentParser:
    """Create the conveyor report parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of Markdown.",
    )
    parser.add_argument(
        "--recent-limit",
        type=int,
        default=8,
        help="Maximum number of recent items per section.",
    )
    parser.add_argument(
        "--root",
        default=str(REPO_ROOT),
        help="Repository root. Defaults to the checkout containing this script.",
    )
    return parser


def main() -> int:
    """Run the science-output conveyor report."""
    args = build_parser().parse_args()
    report = build_science_output_conveyor_report(
        Path(args.root),
        recent_limit=args.recent_limit,
    )
    if args.json:
        print(science_output_conveyor_json(report))
    else:
        print(render_science_output_conveyor_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
