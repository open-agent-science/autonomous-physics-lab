#!/usr/bin/env python3
"""Rank a nuclear prediction variant slate from a factory summary YAML.

Reads a slate summary produced by generate_nuclear_prediction_variants.py
--summary-out and emits a markdown selection report covering candidate count,
target-batch coverage, model-family coverage, duplicate prediction ids,
near-duplicate value vectors, and largest delta_from_baseline_mev rows.

No scientific success scores are assigned and no comparison against future or
holdout measurements is made.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEFAULT_REPO_ROOT))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "summary",
        type=Path,
        help="Path to a factory slate summary YAML (from --summary-out).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Optional path for the generated markdown ranking report.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    from physics_lab.engines.nuclear_prediction_variant_review import rank_slate_from_file

    args = build_parser().parse_args(argv)

    report = rank_slate_from_file(args.summary)
    markdown = report.to_markdown()

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(markdown, encoding="utf-8")
        print(f"Ranking report written to: {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(markdown)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
