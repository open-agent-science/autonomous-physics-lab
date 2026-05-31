#!/usr/bin/env python3
"""Task-to-campaign lane index generator (TASK-0460).

Maps active canonical tasks to campaign lanes using existing task metadata and
the campaign ids in campaigns/catalog.yaml, so agents and the Scientific
Campaign Director can see lane ownership and parallel-safety without reading
every task file.

Usage:
  python3 scripts/apl_task_campaign_index.py                 # print YAML
  python3 scripts/apl_task_campaign_index.py --format markdown
  python3 scripts/apl_task_campaign_index.py --write         # write campaigns/task-index.yaml
  python3 scripts/apl_task_campaign_index.py --check         # exit 1 if committed file is stale

Descriptive only: it never changes task status or campaign metadata.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_OUTPUT = "campaigns/task-index.yaml"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--format", choices=("yaml", "markdown"), default="yaml", help="Output format."
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help=f"Write the YAML index to {DEFAULT_OUTPUT} instead of stdout.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if the committed index differs from a fresh build.",
    )
    return parser


def main() -> int:
    from physics_lab.registry.task_campaign_index import (
        build_index,
        render_markdown,
        render_yaml,
    )

    args = build_parser().parse_args()
    root = Path(args.root)
    index = build_index(root)
    yaml_text = render_yaml(index)
    output_path = root / DEFAULT_OUTPUT

    if args.check:
        if not output_path.exists():
            print(f"Missing {DEFAULT_OUTPUT}; run --write.", file=sys.stderr)
            return 1
        current = output_path.read_text(encoding="utf-8")
        if current != yaml_text:
            print(f"{DEFAULT_OUTPUT} is stale; run --write.", file=sys.stderr)
            return 1
        print(f"{DEFAULT_OUTPUT} is up to date.")
        return 0

    if args.write:
        output_path.write_text(yaml_text, encoding="utf-8")
        print(f"Wrote {DEFAULT_OUTPUT} ({index['summary']['active_tasks']} active tasks).")
        return 0

    print(render_markdown(index) if args.format == "markdown" else yaml_text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
