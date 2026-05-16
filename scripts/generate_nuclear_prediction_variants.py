#!/usr/bin/env python3
"""Generate deterministic Nuclear Mass Surface prediction-variant slates."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import yaml

DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEFAULT_REPO_ROOT))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "config",
        type=Path,
        help="Path to a nuclear prediction variant factory YAML config.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=DEFAULT_REPO_ROOT,
        help="Repository root. Defaults to the checkout containing this script.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Explicit scratch directory for draft PRED YAML files.",
    )
    parser.add_argument(
        "--write-drafts",
        action="store_true",
        help="Write draft PRED YAML files into --output-dir or config output.draft_prediction_dir.",
    )
    parser.add_argument(
        "--summary-out",
        type=Path,
        help="Optional path for the generated candidate slate summary YAML.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    from physics_lab.engines.nuclear_prediction_variants import generate_variant_slate_from_config

    args = build_parser().parse_args(argv)
    summary = generate_variant_slate_from_config(
        args.config,
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        write_drafts=True if args.write_drafts else None,
    )
    rendered = yaml.safe_dump(summary, sort_keys=False, allow_unicode=False)

    if args.summary_out is not None:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
