#!/usr/bin/env python3
"""Deterministic entrypoint for the bounded Research Factory layer (TASK-0506).

Reads a factory config, selects the campaign adapter by ``adapter_id``, runs the
shared core, and writes a schema-valid ``factory_summary`` to the output dir.
The runner is campaign-agnostic: adding a new campaign means registering an
adapter, not editing this script.

Usage:
  python3 scripts/run_research_factory.py --config <config.yaml> --output-dir <dir>

It never creates RESULT, PRED, CLAIM, or KNOW artifacts.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="Path to a factory config YAML.")
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to write factory_summary.yaml (created if missing).",
    )
    return parser


def main() -> int:
    from physics_lab.factories import (
        FactorySpec,
        get_adapter,
        run_factory,
        write_factory_summary,
    )

    args = build_parser().parse_args()
    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) or {}
    spec = FactorySpec.from_config(config)
    adapter = get_adapter(spec.adapter_id)
    summary = run_factory(spec, adapter)
    out_path = write_factory_summary(summary, args.output_dir)

    counts = summary["candidate_counts"]
    print(f"Research factory '{spec.factory_id}' ({spec.adapter_id}) complete.")
    print(
        "Candidates: "
        f"generated={counts['generated']} executed={counts['executed']} "
        f"shortlisted={counts['shortlisted']} rejected_by_control={counts['rejected_by_control']}"
    )
    print(f"Route verdicts: {summary['route_verdict_summary']}")
    print(f"factory_summary written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
