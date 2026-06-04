#!/usr/bin/env python3
"""Run TASK-0550 Materials MD-0001 baseline benchmark metrics."""

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
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-dir", required=True)
    return parser


def main() -> int:
    from physics_lab.engines.materials_md0001_baseline import (
        run_materials_md0001_baseline,
    )

    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics = run_materials_md0001_baseline(Path(args.config))
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Materials MD-0001 baseline benchmark complete: {output_dir / 'metrics.json'}")
    print(f"Verdict: {metrics['verdict']}")
    for axis_id, axis in metrics["axis_outputs"].items():
        best = axis["best_holdout_baseline"]
        print(f"{axis_id}: best holdout baseline={best['baseline_id']} MAE={best['mae']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
