#!/usr/bin/env python3
"""Run TASK-0596 NMD-0003 uncertainty-weighted baseline diagnostic."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        default="data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml",
    )
    parser.add_argument(
        "--gate",
        default="data/nuclear_masses/nmd-0003-stratified-baseline-gate.yaml",
    )
    parser.add_argument("--output-dir", required=True)
    return parser


def main() -> int:
    from physics_lab.engines.nmd0003_uncertainty_weighted_diagnostic import (
        run_nmd0003_uncertainty_weighted_baseline_diagnostic,
    )

    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics = run_nmd0003_uncertainty_weighted_baseline_diagnostic(
        dataset_path=Path(args.dataset), gate_path=Path(args.gate)
    )
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    decision = metrics["readiness_decision"]
    print(
        "NMD-0003 uncertainty-weighted baseline diagnostic complete: "
        f"{output_dir / 'metrics.json'}"
    )
    print(f"Verdict: {metrics['verdict']}")
    print(
        "Weighting changes candidate-readiness interpretation: "
        f"{decision['weighting_changes_candidate_readiness_interpretation']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
