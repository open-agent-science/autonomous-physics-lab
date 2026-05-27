#!/usr/bin/env python3
"""Render the scientific-memory review-tier index."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.registry.scientific_memory_index import (  # noqa: E402
    render_scientific_memory_index,
    write_scientific_memory_index,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render or update docs/scientific-memory-review-tiers.md."
    )
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument(
        "--output",
        default="docs/scientific-memory-review-tiers.md",
        help="Output Markdown path when --write is used.",
    )
    parser.add_argument("--write", action="store_true", help="Write the index file.")
    args = parser.parse_args(argv)

    if args.write:
        path = write_scientific_memory_index(args.root, args.output)
        print(f"Wrote {path}")
    else:
        print(render_scientific_memory_index(args.root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
