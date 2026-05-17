#!/usr/bin/env python3
"""Write a deterministic nuclear prediction registry coverage summary."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


def _add_repo_root_to_path(root: Path) -> None:
    sys.path.insert(0, str(root.resolve()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root. Defaults to the current directory.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/nuclear_masses/nuclear_prediction_registry_coverage.yaml"),
        help="Output YAML path.",
    )
    args = parser.parse_args()

    _add_repo_root_to_path(args.root)
    from physics_lab.registry.nuclear_prediction_coverage import write_coverage_summary

    coverage = write_coverage_summary(args.root, args.out)
    print(
        "Wrote coverage summary for "
        f"{coverage['audit_scope']['entry_count']} entries to {args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
