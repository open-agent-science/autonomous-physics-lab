#!/usr/bin/env python3
"""Run TASK-0600 Materials MD-0001 formation-energy null-control audit."""

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
    parser.add_argument("--permutations", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=0)
    return parser


def main() -> int:
    from physics_lab.engines.materials_md0001_formation_energy_null_control import (
        run_formation_energy_null_control_audit,
    )

    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics = run_formation_energy_null_control_audit(
        Path(args.config),
        permutations=args.permutations,
        seed=args.seed,
    )
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Materials MD-0001 formation-energy null-control complete: {output_dir / 'metrics.json'}")
    print(f"Verdict: {metrics['verdict']}")
    real = metrics["real_baselines_holdout_mae"]
    print(
        "formation_energy_per_atom: "
        f"global_mean={real['global_mean_null']} "
        f"cation_group_mean={real['cation_group_mean']} "
        f"skill={real['cation_group_skill_vs_global_null']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
