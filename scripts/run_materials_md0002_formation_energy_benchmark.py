#!/usr/bin/env python3
"""Run TASK-0703 MD-0002 formation-energy baseline benchmark."""

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
        "--config",
        default="examples/benchmarks/materials_md0002_formation_energy.yaml",
    )
    parser.add_argument("--output-dir", required=True)
    return parser


def main() -> int:
    from physics_lab.engines.materials_md0002_baseline import (
        run_materials_md0002_formation_energy_benchmark,
    )

    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics = run_materials_md0002_formation_energy_benchmark(Path(args.config))
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Metrics: {output_dir / 'metrics.json'}")
    print(f"Verdict: {metrics['verdict']}")
    print(
        "Best composition baseline: "
        f"{metrics['best_composition_baseline']['baseline_id']} "
        f"MAE={metrics['best_composition_baseline']['mae']}"
    )
    print(f"Failed gates: {', '.join(metrics['promotion_assessment']['failed_gates']) or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
