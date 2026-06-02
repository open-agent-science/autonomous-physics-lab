#!/usr/bin/env python3
"""Run the TASK-0518 NMD-0002 uncertainty perturbation control."""

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
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--trials", type=int, default=200)
    parser.add_argument("--seed", type=int, default=518)
    return parser


def main() -> int:
    from physics_lab.factories.nuclear_uncertainty import run_uncertainty_perturbation_control

    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics = run_uncertainty_perturbation_control(
        dataset_path=Path("data/nuclear_masses/nmd-0002-curated-measured-slice.yaml"),
        factory_summary_path=Path("agent_runs/AGENT-RUN-0052/factory_summary.yaml"),
        baseline_result_path=Path("results/EXP-0012/RUN-0001/result.yaml"),
        trials=args.trials,
        seed=args.seed,
    )
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(f"NMD-0002 uncertainty perturbation control complete: {output_dir / 'metrics.json'}")
    print(f"Verdict: {metrics['verdict']}")
    for mode_id, summary in metrics["mode_summaries"].items():
        print(f"{mode_id}: top1_counts={summary['top1_counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
