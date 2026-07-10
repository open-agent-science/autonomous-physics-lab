#!/usr/bin/env python3
"""Reject newly added flat-root docs/reviews files in a git diff."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.registry.reviews_policy import new_root_review_files  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root. Defaults to cwd.")
    parser.add_argument("--base", required=True, help="Base commit/ref for the diff.")
    parser.add_argument("--head", required=True, help="Head commit/ref for the diff.")
    args = parser.parse_args()

    violations = new_root_review_files(Path(args.root).resolve(), args.base, args.head)
    if not violations:
        print("docs/reviews shard policy: PASS")
        return 0

    print("docs/reviews shard policy: FAIL")
    print("New review files must be placed under docs/reviews/<domain>/, not the flat root.")
    print("Existing flat-root review files are grandfathered; this guard is diff-based.")
    for path in violations:
        print(f"- {path}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
