#!/usr/bin/env python3
"""Thin `--check` wrapper for the MD-0002 formation-energy benchmark (RESULT-0021).

Superseded as the canonical replay command by
``physics-lab run examples/materials_md0002_formation_energy_benchmark.yaml``
(the engine workflow that regenerates the full result.yaml for Gate B). This
wrapper is retained for the lightweight ``--check`` reproduction affordance: it
delegates to the same deterministic engine and asserts the committed RESULT-0021
holdout metrics. Reads only committed data; no fetch, no claim.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.engines.materials_md0002_formation_energy_result import (  # noqa: E402
    compute_result_metrics,
)

EXPECTED_CATION_PAIR_HOLDOUT_MAE = 0.200606
EXPECTED_NULL_HOLDOUT_MAE = 0.506092
TOL = 1e-6


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify against committed result metrics.")
    args = parser.parse_args()
    m = compute_result_metrics()
    print(
        f"train={m['train_count']} holdout={m['holdout_count']} "
        f"cation_pair_holdout_mae={m['cation_pair_holdout_mae']:.6f} "
        f"null_holdout_mae={m['null_holdout_mae']:.6f} "
        f"improvement_abs={m['improvement_abs']:.6f}"
    )
    if args.check:
        ok = (
            abs(m["cation_pair_holdout_mae"] - EXPECTED_CATION_PAIR_HOLDOUT_MAE) <= TOL
            and abs(m["null_holdout_mae"] - EXPECTED_NULL_HOLDOUT_MAE) <= TOL
        )
        print("GATE_A_REPLAY:", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
