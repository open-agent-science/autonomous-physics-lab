#!/usr/bin/env python3
"""Compatibility wrapper for packaging RESULT-0027.

The canonical Gate-B-safe route is:

    physics-lab run examples/exoplanet_null_baseline_result.yaml
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.workflows.exoplanet_null_baseline_result import (  # noqa: E402
    DEFAULT_OUTPUT,
    SOURCE_COMMIT,
    write_package,
)


def main() -> int:
    """Run the legacy packager command."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--git-commit")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if not args.write:
        parser.error("--write is required")
    output = args.output_dir if args.output_dir.is_absolute() else REPO_ROOT / args.output_dir
    write_package(output, commit=args.git_commit or SOURCE_COMMIT)
    print(f"Wrote RESULT-0027 package to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
