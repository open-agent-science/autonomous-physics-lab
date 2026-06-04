#!/usr/bin/env python3
"""Task-to-campaign lane index query helper (TASK-0460/TASK-0509).

Maps active canonical tasks to campaign lanes using existing task metadata and
the campaign ids in campaign_profiles/_catalog.yaml, so agents and the Scientific
Campaign Director can see lane ownership and parallel-safety without reading
every task file.

Usage:
  python3 scripts/apl_task_campaign_index.py                 # print YAML
  python3 scripts/apl_task_campaign_index.py --format markdown

Descriptive only: it never changes task status, campaign metadata, or committed
generated files.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--format", choices=("yaml", "markdown"), default="yaml", help="Output format."
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
    print(render_markdown(index) if args.format == "markdown" else render_yaml(index), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
