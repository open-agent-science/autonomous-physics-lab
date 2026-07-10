#!/usr/bin/env python3
"""Print a recursive docs/reviews inventory without writing generated output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.registry.reviews_policy import (  # noqa: E402
    build_reviews_inventory,
    render_reviews_inventory,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root. Defaults to cwd.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    args = parser.parse_args()

    inventory = build_reviews_inventory(Path(args.root).resolve())
    if args.json:
        print(
            json.dumps(
                {
                    "total_files": inventory.total_files,
                    "counts_by_group": inventory.counts_by_group,
                    "entries": [
                        {"path": entry.path, "group": entry.group}
                        for entry in inventory.entries
                    ],
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(render_reviews_inventory(inventory), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
