#!/usr/bin/env python3
"""Deterministic replay/verification of the Stellar M-L DEBCat controlled audit.

Recomputes, from the committed DEBCat normalized component rows and their frozen
system-level holdout lanes (CC BY 4.0; TASK-0763), the controlled baseline-adequacy
and stage-control evidence packaged in RESULT-0022:

- frozen main-sequence-compatible lane (mass 0.5-2.0 Msun): holdout MAE for the
  textbook single exponent alpha=3.5, the textbook piecewise mid-mass alpha=4.0, a
  train-fitted exponent (fixed intercept, fit on the train lane only), and a
  per-mass-band train-median null (global-median fallback);
- seeded, system-level (no-leakage) split-sensitivity of the null-minus-formula
  margin;
- deterministic luminosity-shuffle controls on the frozen holdout lane.

Reads only committed data; no fetch, no claim, no universal-law assertion. Exits
non-zero if the recomputed numbers do not match the committed result within tol.
This re-states the TASK-0762 lesson: fixed M^3.5 beats the null but is not the
adequate sole baseline on this scoped slice; fitted/piecewise exponents are better.
"""

from __future__ import annotations

import argparse
import random
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
ROWS = REPO_ROOT / "data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml"

# Predeclared policy (AGENT-RUN-0073 / AGENT-RUN-0074).
PRIMARY_MASS_RANGE = (0.5, 2.0)
PRIMARY_STAGE = "main_sequence_compatible"
SPLIT_SEEDS = (11, 23, 37, 53, 71)
SPLIT_TRAIN_FRACTION = 0.7
TEXTBOOK_ALPHA = 3.5
PIECEWISE_ALPHA = 4.0

# Committed result metrics (RESULT-0022), holdout MAE in dex on the frozen lane.
EXPECTED = {
    "alpha_3p5_holdout_mae": 0.184954,
    "alpha_4p0_holdout_mae": 0.137608,
    "fitted_alpha": 4.526004,
    "fitted_holdout_mae": 0.119925,
    "null_holdout_mae": 0.331817,
    "split_sensitivity_per_seed": [0.180271, 0.15486, 0.127142, 0.102269, 0.133989],
    "shuffle_real_margin": 0.146863,
    "shuffle_per_seed": [-0.141034, -0.146732, -0.14912, -0.09802, -0.092278],
}
TOL = 1e-6


def _primary_rows() -> list[dict[str, Any]]:
    doc = yaml.safe_load(ROWS.read_text(encoding="utf-8"))
    lo, hi = PRIMARY_MASS_RANGE
    return [
        r
        for r in doc["rows"]
        if r.get("admissibility") == "admitted"
        and r.get("evolutionary_stage_flag") == PRIMARY_STAGE
        and lo <= r["mass_solar"] <= hi
    ]


def _mae(rows: list[dict[str, Any]], predict: Callable[[dict[str, Any]], float]) -> float:
    return statistics.fmean(abs(r["log_luminosity_solar"] - predict(r)) for r in rows)


def _alpha_mae(rows: list[dict[str, Any]], alpha: float) -> float:
    return _mae(rows, lambda r: alpha * r["log_mass_solar"])


def _fit_alpha(train: list[dict[str, Any]]) -> float:
    # fixed-intercept least squares: logL = alpha * logM
    sxx = sum(r["log_mass_solar"] ** 2 for r in train)
    sxy = sum(r["log_mass_solar"] * r["log_luminosity_solar"] for r in train)
    return sxy / sxx


def _null_mae(holdout: list[dict[str, Any]], train: list[dict[str, Any]]) -> float:
    band: dict[str, list[float]] = defaultdict(list)
    for r in train:
        band[r["mass_band"]].append(r["log_luminosity_solar"])
    band_median = {k: statistics.median(v) for k, v in band.items()}
    global_median = statistics.median([r["log_luminosity_solar"] for r in train])
    return _mae(holdout, lambda r: band_median.get(r["mass_band"], global_median))


def replay() -> dict[str, Any]:
    rows = _primary_rows()
    train = [r for r in rows if r["lane"] == "train"]
    holdout = [r for r in rows if r["lane"] == "holdout"]

    fitted_alpha = _fit_alpha(train)

    # seeded system-level split sensitivity (null - formula margin per seed)
    systems = sorted({r["system_id"] for r in rows})
    split_sensitivity = []
    for seed in SPLIT_SEEDS:
        shuffled = list(systems)
        random.Random(seed).shuffle(shuffled)
        n_train = round(SPLIT_TRAIN_FRACTION * len(shuffled))
        train_sys = set(shuffled[:n_train])
        s_train = [r for r in rows if r["system_id"] in train_sys]
        s_hold = [r for r in rows if r["system_id"] not in train_sys]
        margin = _null_mae(s_hold, s_train) - _alpha_mae(s_hold, TEXTBOOK_ALPHA)
        split_sensitivity.append(round(margin, 6))

    # deterministic luminosity-shuffle control on the frozen holdout lane
    real_margin = _null_mae(holdout, train) - _alpha_mae(holdout, TEXTBOOK_ALPHA)
    shuffle_margins = []
    for seed in SPLIT_SEEDS:
        lums = [r["log_luminosity_solar"] for r in rows]
        random.Random(seed).shuffle(lums)
        permuted = [dict(r, log_luminosity_solar=lum) for r, lum in zip(rows, lums)]
        p_train = [r for r in permuted if r["lane"] == "train"]
        p_hold = [r for r in permuted if r["lane"] == "holdout"]
        margin = _null_mae(p_hold, p_train) - _alpha_mae(p_hold, TEXTBOOK_ALPHA)
        shuffle_margins.append(round(margin, 6))

    return {
        "main_sequence_count": len(rows),
        "train_count": len(train),
        "holdout_count": len(holdout),
        "alpha_3p5_holdout_mae": round(_alpha_mae(holdout, TEXTBOOK_ALPHA), 6),
        "alpha_4p0_holdout_mae": round(_alpha_mae(holdout, PIECEWISE_ALPHA), 6),
        "fitted_alpha": round(fitted_alpha, 6),
        "fitted_holdout_mae": round(_alpha_mae(holdout, fitted_alpha), 6),
        "null_holdout_mae": round(_null_mae(holdout, train), 6),
        "split_sensitivity_per_seed": split_sensitivity,
        "shuffle_real_margin": round(real_margin, 6),
        "shuffle_per_seed": shuffle_margins,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify against committed result metrics.")
    args = parser.parse_args()
    m = replay()
    print(
        f"main_sequence={m['main_sequence_count']} train={m['train_count']} holdout={m['holdout_count']}\n"
        f"alpha3.5_mae={m['alpha_3p5_holdout_mae']:.6f} "
        f"alpha4.0_mae={m['alpha_4p0_holdout_mae']:.6f} "
        f"fitted_alpha={m['fitted_alpha']:.6f} fitted_mae={m['fitted_holdout_mae']:.6f} "
        f"null_mae={m['null_holdout_mae']:.6f}\n"
        f"split_sensitivity={m['split_sensitivity_per_seed']}\n"
        f"shuffle_real={m['shuffle_real_margin']:.6f} shuffle_per_seed={m['shuffle_per_seed']}"
    )
    if args.check:
        ok = (
            abs(m["alpha_3p5_holdout_mae"] - EXPECTED["alpha_3p5_holdout_mae"]) <= TOL
            and abs(m["alpha_4p0_holdout_mae"] - EXPECTED["alpha_4p0_holdout_mae"]) <= TOL
            and abs(m["fitted_alpha"] - EXPECTED["fitted_alpha"]) <= TOL
            and abs(m["fitted_holdout_mae"] - EXPECTED["fitted_holdout_mae"]) <= TOL
            and abs(m["null_holdout_mae"] - EXPECTED["null_holdout_mae"]) <= TOL
            and all(
                abs(a - b) <= TOL
                for a, b in zip(m["split_sensitivity_per_seed"], EXPECTED["split_sensitivity_per_seed"])
            )
            and all(x > 0 for x in m["split_sensitivity_per_seed"])
            and abs(m["shuffle_real_margin"] - EXPECTED["shuffle_real_margin"]) <= TOL
            and all(
                abs(a - b) <= TOL for a, b in zip(m["shuffle_per_seed"], EXPECTED["shuffle_per_seed"])
            )
            and all(m["shuffle_real_margin"] > x for x in m["shuffle_per_seed"])
        )
        # the headline lesson: fitted/piecewise materially better than fixed 3.5
        single_inadequate = (
            m["alpha_3p5_holdout_mae"] - m["fitted_holdout_mae"]
        ) > 0.04  # split-noise reference
        print("SINGLE_ALPHA_3P5_INADEQUATE:", single_inadequate)
        print("GATE_A_REPLAY:", "PASS" if (ok and single_inadequate) else "FAIL")
        return 0 if (ok and single_inadequate) else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
