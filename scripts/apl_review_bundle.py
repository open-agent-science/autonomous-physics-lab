#!/usr/bin/env python3
"""Generate a portable PR review bundle."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.registry.review_bundle import generate_review_bundle  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", nargs="?", default="main")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    output = generate_review_bundle(Path(args.root), base=args.base)
    print(f"Review bundle written to: {output.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
