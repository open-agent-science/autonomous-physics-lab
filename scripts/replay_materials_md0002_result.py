#!/usr/bin/env python3
"""Deterministic replay/verification of the MD-0002 formation-energy benchmark.

Recomputes, from the committed MD-0002 dataset and its frozen per-row holdout
split, the two predeclared baselines packaged in RESULT-0021:

- exact cation-pair mean (group by unordered non-oxygen cation pair; train mean
  per pair, global train mean fallback for unseen pairs);
- global-median null (train-lane global median).

Reads only committed data; no fetch, no fit-to-holdout, no claim. Exits non-zero
if the recomputed holdout MAEs do not match the committed result within tol.
"""

from __future__ import annotations

import argparse
import statistics
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DATASET = REPO_ROOT / "data/materials/md-0002-materials-project-stable-ternary-oxides.yaml"

# Committed result metrics (AGENT-RUN-0072 / RESULT-0021), formation energy.
EXPECTED_CATION_PAIR_HOLDOUT_MAE = 0.200606
EXPECTED_NULL_HOLDOUT_MAE = 0.506092
TOL = 1e-6


def _fe_rows() -> list[dict[str, Any]]:
    doc = yaml.safe_load(DATASET.read_text(encoding="utf-8"))
    return [
        r for r in doc["rows"]
        if r["property_kind"] == "formation_energy_per_atom" and r["inclusion_status"] == "included"
    ]


def _pair_key(row: dict[str, Any]) -> tuple[str, ...]:
    return tuple(sorted(row["cations"]))


def replay() -> dict[str, float]:
    rows = _fe_rows()
    train = [r for r in rows if r["split"] == "train"]
    holdout = [r for r in rows if r["split"] == "holdout"]

    # cation-pair mean baseline (fit on train only)
    sums: dict[tuple[str, ...], list[float]] = {}
    for r in train:
        sums.setdefault(_pair_key(r), []).append(float(r["value"]))
    pair_mean = {k: statistics.fmean(v) for k, v in sums.items()}
    global_train_mean = statistics.fmean([float(r["value"]) for r in train])
    cation_pair_mae = statistics.fmean(
        abs(float(r["value"]) - pair_mean.get(_pair_key(r), global_train_mean)) for r in holdout
    )

    # global-median null (train median)
    global_train_median = statistics.median([float(r["value"]) for r in train])
    null_mae = statistics.fmean(abs(float(r["value"]) - global_train_median) for r in holdout)

    return {
        "train_count": len(train),
        "holdout_count": len(holdout),
        "cation_pair_holdout_mae": cation_pair_mae,
        "null_holdout_mae": null_mae,
        "improvement_abs": null_mae - cation_pair_mae,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify against committed result metrics.")
    args = parser.parse_args()
    m = replay()
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
