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
    GENERATED_SURFACES,
    render_scientific_memory_index,
    write_scientific_memory_surfaces,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Render or update the scientific-memory public surfaces: the"
            " review-tier index and the historical pre-tier ledger."
        )
    )
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument(
        "--write", action="store_true", help="Write every generated surface."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if any committed surface differs from a fresh render.",
    )
    args = parser.parse_args(argv)

    if args.check:
        stale = []
        for relative_path, render in GENERATED_SURFACES.items():
            expected = render(args.root)
            target = Path(args.root) / relative_path
            committed = target.read_text(encoding="utf-8") if target.exists() else ""
            if committed == expected:
                print(f"scientific-memory surface: IN SYNC ({relative_path})")
            else:
                print(f"scientific-memory surface: STALE ({relative_path})")
                stale.append(relative_path)
        if stale:
            print("Regenerate with: python3 scripts/apl_scientific_memory_index.py --write")
            return 1
        return 0
    if args.write:
        for path in write_scientific_memory_surfaces(args.root):
            print(f"Wrote {path}")
    else:
        print(render_scientific_memory_index(args.root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
