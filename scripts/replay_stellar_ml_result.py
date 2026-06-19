#!/usr/bin/env python3
"""Thin `--check` wrapper for the Stellar M-L DEBCat benchmark (RESULT-0022).

Superseded as the canonical replay command by
``physics-lab run examples/stellar_ml_debcat_baseline_benchmark.yaml`` (the engine
workflow that regenerates the full result.yaml for Gate B). This wrapper is
retained for the lightweight ``--check`` reproduction affordance: it delegates to
the same deterministic engine and asserts the committed RESULT-0022 holdout
metrics. Reads only committed data; no fetch, no claim.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.engines.stellar_ml_debcat_baseline_result import (  # noqa: E402
    compute_result_metrics,
)

EXPECTED_ALPHA_3P5_HOLDOUT_MAE = 0.184954
EXPECTED_NULL_HOLDOUT_MAE = 0.331817
EXPECTED_FITTED_HOLDOUT_MAE = 0.119925
TOL = 1e-6


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify against committed result metrics.")
    args = parser.parse_args()
    m = compute_result_metrics()
    print(
        f"main_sequence={m['main_sequence_components']} train={m['train_count']} holdout={m['holdout_count']} "
        f"alpha3.5_mae={m['alpha_3p5_holdout_mae']:.6f} fitted_alpha={m['fitted_alpha']:.6f} "
        f"fitted_mae={m['fitted_holdout_mae']:.6f} null_mae={m['null_holdout_mae']:.6f}"
    )
    if args.check:
        ok = (
            abs(m["alpha_3p5_holdout_mae"] - EXPECTED_ALPHA_3P5_HOLDOUT_MAE) <= TOL
            and abs(m["null_holdout_mae"] - EXPECTED_NULL_HOLDOUT_MAE) <= TOL
            and abs(m["fitted_holdout_mae"] - EXPECTED_FITTED_HOLDOUT_MAE) <= TOL
            and (m["alpha_3p5_holdout_mae"] - m["fitted_holdout_mae"]) > 0.04
        )
        print("SINGLE_ALPHA_3P5_INADEQUATE:", (m["alpha_3p5_holdout_mae"] - m["fitted_holdout_mae"]) > 0.04)
        print("GATE_A_REPLAY:", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
