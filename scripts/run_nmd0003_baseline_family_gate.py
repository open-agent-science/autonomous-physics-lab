#!/usr/bin/env python3
"""Run TASK-0535 NMD-0003 baseline-family gate metrics."""

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
    from physics_lab.engines.nmd0003_baseline_family_gate import (
        run_nmd0003_baseline_family_gate,
    )

    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics = run_nmd0003_baseline_family_gate(Path(args.config))
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    print(f"NMD-0003 baseline-family gate complete: {output_dir / 'metrics.json'}")
    print(f"Verdict: {metrics['verdict']}")
    print(f"Dominant factor: {metrics['split_sensitivity_diagnostic']['dominant_factor']}")
    print(f"Recommendation: {metrics['recommendation']['decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
