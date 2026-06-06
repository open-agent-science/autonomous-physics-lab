#!/usr/bin/env python3
"""Run TASK-0612 Nuclear F2 independent replay and control ledger."""

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
        default="agent_runs/AGENT-RUN-0060/metrics.json",
    )
    parser.add_argument("--output-dir", required=True)
    return parser


def main() -> int:
    from physics_lab.engines.nuclear_f2_independent_replay import (
        run_nuclear_f2_independent_replay,
    )

    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics = run_nuclear_f2_independent_replay(
        committed_metrics_path=Path(args.committed_metrics)
    )
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    print(f"F2 independent replay complete: {output_dir / 'metrics.json'}")
    print(f"Replay verdict: {metrics['replay_verdict']}")
    if metrics["replay_verdict"] == "REPLAY_MATCH":
        print(f"F2 scoring verdict: {metrics['control_ledger']['f2_scoring_verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
