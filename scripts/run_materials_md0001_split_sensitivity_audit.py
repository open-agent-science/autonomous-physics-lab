#!/usr/bin/env python3
"""Run TASK-0601 Materials MD-0001 split-sensitivity audit."""

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
        "--committed-metrics",
        default="agent_runs/AGENT-RUN-0057/metrics.json",
    )
    parser.add_argument("--output-dir", required=True)
    return parser


def main() -> int:
    from physics_lab.engines.materials_md0001_split_sensitivity import (
        run_materials_md0001_split_sensitivity_audit,
    )

    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics = run_materials_md0001_split_sensitivity_audit(
        committed_metrics_path=Path(args.committed_metrics)
    )
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    print(
        "MD-0001 split-sensitivity audit complete: "
        f"{output_dir / 'metrics.json'}"
    )
    print(f"Verdict: {metrics['verdict']}")
    for axis, verdict in metrics["overall_split_robustness"].items():
        print(f"  {axis}: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
