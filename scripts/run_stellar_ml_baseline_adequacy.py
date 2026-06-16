#!/usr/bin/env python3
"""Stellar M-L baseline-adequacy audit (TASK-0762).

Last control before Gate A: on the same frozen, main-sequence-restricted DEBCat
rows used by TASK-0759, compare the textbook single-alpha relation
`L/L_sun = (M/M_sun)^3.5` against:

- the textbook piecewise mid-mass exponent `alpha = 4.0` (the classic
  0.43-2 M_sun branch), and
- a train-fitted exponent (least squares, intercept fixed at L0=1 to match the
  textbook convention; fit on the train lane only, never the holdout).

This decides whether the single-alpha 3.5 baseline is adequate (within split
noise of the best exponent) or whether a piecewise/fitted baseline is materially
better and required before Gate A. Predeclared (no-peek); reads the locally
regenerated, gitignored DEBCat rows (Route 2; raw debs.dat not committed). No
RESULT/PRED/CLAIM.
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
ROWS_PATH = REPO_ROOT / "data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml"

PRIMARY_MASS_RANGE = (0.5, 2.0)
PRIMARY_STAGE = "main_sequence_compatible"
# Predeclared fixed-intercept (L0=1) exponents; "train_fitted" is computed on train only.
TEXTBOOK_SINGLE_ALPHA = 3.5
TEXTBOOK_PIECEWISE_MID_ALPHA = 4.0
# Split-noise reference from TASK-0759 (across-seed margin spread, dex).
SPLIT_NOISE_DEX = 0.04


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _load_ms_rows() -> list[dict[str, Any]]:
    doc = yaml.safe_load(ROWS_PATH.read_text(encoding="utf-8"))
    rows = doc["rows"] if isinstance(doc, dict) and "rows" in doc else doc
    out: list[dict[str, Any]] = []
    for row in rows:
        if row.get("admissibility") != "admitted":
            continue
        mass = float(row["mass_solar"])
        if not (PRIMARY_MASS_RANGE[0] <= mass < PRIMARY_MASS_RANGE[1]):
            continue
        if row.get("evolutionary_stage_flag") != PRIMARY_STAGE:
            continue
        out.append({
            "lane": row.get("lane"),
            "mass_band": row.get("mass_band", "unknown"),
            "log_mass": float(row["log_mass_solar"]),
            "log_lum": float(row["log_luminosity_solar"]),
        })
    return out


def _fit_alpha_fixed_intercept(train: list[dict[str, Any]]) -> float:
    num = sum(r["log_mass"] * r["log_lum"] for r in train)
    den = sum(r["log_mass"] ** 2 for r in train)
    return num / den if den else float("nan")


def _holdout_mae(rows: list[dict[str, Any]], alpha: float) -> float | None:
    return _mean([abs(r["log_lum"] - alpha * r["log_mass"]) for r in rows])


def _null_holdout_mae(holdout: list[dict[str, Any]], train: list[dict[str, Any]]) -> float | None:
    bands: dict[str, list[float]] = {}
    for r in train:
        bands.setdefault(str(r["mass_band"]), []).append(r["log_lum"])
    median_by_band = {b: statistics.median(v) for b, v in bands.items() if v}
    gmed = statistics.median([r["log_lum"] for r in train]) if train else None
    if gmed is None:
        return None
    return _mean([abs(r["log_lum"] - median_by_band.get(str(r["mass_band"]), gmed)) for r in holdout])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "agent_runs/AGENT-RUN-0074/metrics.json")
    args = parser.parse_args()

    rows = _load_ms_rows()
    train = [r for r in rows if r["lane"] == "train"]
    holdout = [r for r in rows if r["lane"] == "holdout"]
    fitted_alpha = _fit_alpha_fixed_intercept(train)

    alphas = {
        "textbook_single_3p5": TEXTBOOK_SINGLE_ALPHA,
        "textbook_piecewise_mid_4p0": TEXTBOOK_PIECEWISE_MID_ALPHA,
        "train_fitted": fitted_alpha,
    }
    null_mae = _null_holdout_mae(holdout, train)
    per_alpha = {
        name: {
            "alpha": round(alpha, 4),
            "holdout_mae_dex": round(_holdout_mae(holdout, alpha), 6),
            "holdout_minus_textbook_single_dex": None,  # filled below
        }
        for name, alpha in alphas.items()
    }
    base = per_alpha["textbook_single_3p5"]["holdout_mae_dex"]
    best_name = min(per_alpha, key=lambda k: per_alpha[k]["holdout_mae_dex"])
    for name in per_alpha:
        per_alpha[name]["holdout_minus_textbook_single_dex"] = round(
            per_alpha[name]["holdout_mae_dex"] - base, 6
        )
    single_gap = base - per_alpha[best_name]["holdout_mae_dex"]

    metrics = {
        "task_id": "TASK-0762",
        "agent_run_id": "AGENT-RUN-0074",
        "audit": "stellar_ml_baseline_adequacy",
        "source": "DEBCat Route 2 (local-only debs.dat; checksum-pinned; not committed)",
        "predeclared_policy": {
            "primary_mass_range_solar": list(PRIMARY_MASS_RANGE),
            "primary_stage": PRIMARY_STAGE,
            "fixed_intercept_L0": 1.0,
            "alphas": "textbook 3.5, piecewise-mid 4.0, train-fitted (fit on train lane only)",
            "split_noise_reference_dex": SPLIT_NOISE_DEX,
        },
        "counts": {"main_sequence_train": len(train), "main_sequence_holdout": len(holdout)},
        "train_fitted_alpha": round(fitted_alpha, 4),
        "null_holdout_mae_dex": round(null_mae, 6) if null_mae is not None else None,
        "per_alpha_holdout": per_alpha,
        "best_alpha": best_name,
        "single_alpha_gap_to_best_dex": round(single_gap, 6),
        "single_alpha_adequate": single_gap <= SPLIT_NOISE_DEX,
        "verdict": (
            "SINGLE_ALPHA_ADEQUATE"
            if single_gap <= SPLIT_NOISE_DEX
            else "PIECEWISE_OR_FITTED_BASELINE_MATERIALLY_BETTER"
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
