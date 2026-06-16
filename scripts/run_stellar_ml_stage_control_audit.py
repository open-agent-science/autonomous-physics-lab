#!/usr/bin/env python3
"""Stellar M-L stage-control and split-sensitivity audit (TASK-0759).

Reads the locally regenerated, gitignored DEBCat component rows (Route 2; the
raw debs.dat and full rows are never committed) and runs a controlled audit of
the textbook single-alpha mass-luminosity formula L/L_sun = (M/M_sun)^3.5 over
the 0.5-2.0 M_sun primary range:

1. main-sequence-restricted primary scoring (the predeclared confound control),
   with evolved / subgiant / unknown stages reported only as diagnostics;
2. deterministic luminosity-shuffle controls (the M-L margin must collapse when
   the mass-luminosity pairing is broken);
3. seeded, system-level (no-leakage) split-sensitivity to test margin stability.

All policy parameters are predeclared below before any metric is inspected
(no-peek). The script scores existing committed evidence: no fit, no new fetch,
no RESULT/PRED/CLAIM artifact.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
ROWS_PATH = REPO_ROOT / "data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml"

# --- Predeclared policy (frozen before inspecting metrics; no-peek) -----------
PRIMARY_ALPHA = 3.5
PRIMARY_L0 = 1.0
PRIMARY_MASS_RANGE = (0.5, 2.0)
PRIMARY_STAGE = "main_sequence_compatible"
DIAGNOSTIC_STAGES = ("main_sequence_compatible", "subgiant", "evolved", "unknown")
SPLIT_SEEDS = (11, 23, 37, 53, 71)
SPLIT_TRAIN_FRACTION = 0.70


def _predict(log_mass: float) -> float:
    return math.log10(PRIMARY_L0) + PRIMARY_ALPHA * log_mass


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _mae(rows: list[dict[str, Any]]) -> float | None:
    return _mean([abs(r["residual"]) for r in rows])


def _null_mae(rows: list[dict[str, Any]], train_rows: list[dict[str, Any]]) -> float | None:
    """Per-mass-band train-median null, global-train-median fallback."""
    bands: dict[str, list[float]] = {}
    for r in train_rows:
        bands.setdefault(str(r["mass_band"]), []).append(r["log_lum"])
    median_by_band = {b: statistics.median(v) for b, v in bands.items() if v}
    global_median = (
        statistics.median([r["log_lum"] for r in train_rows]) if train_rows else None
    )
    if global_median is None:
        return None
    abs_err = [
        abs(r["log_lum"] - median_by_band.get(str(r["mass_band"]), global_median))
        for r in rows
    ]
    return _mean(abs_err)


def _load_primary_rows() -> list[dict[str, Any]]:
    doc = yaml.safe_load(ROWS_PATH.read_text(encoding="utf-8"))
    rows = doc["rows"] if isinstance(doc, dict) and "rows" in doc else doc
    out: list[dict[str, Any]] = []
    for row in rows:
        if row.get("admissibility") != "admitted":
            continue
        mass = float(row["mass_solar"])
        if not (PRIMARY_MASS_RANGE[0] <= mass < PRIMARY_MASS_RANGE[1]):
            continue
        log_mass = float(row["log_mass_solar"])
        log_lum = float(row["log_luminosity_solar"])
        out.append({
            "row_id": row["row_id"],
            "system_id": row["system_id"],
            "lane": row.get("lane"),
            "mass_band": row.get("mass_band", "unknown"),
            "stage": row.get("evolutionary_stage_flag", "unknown"),
            "log_mass": log_mass,
            "log_lum": log_lum,
            "residual": log_lum - _predict(log_mass),
        })
    return out


def _frozen_lane_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    train = [r for r in rows if r["lane"] == "train"]
    out: dict[str, Any] = {"train_count": len(train)}
    for lane in ("validation", "holdout"):
        lane_rows = [r for r in rows if r["lane"] == lane]
        f = _mae(lane_rows)
        n = _null_mae(lane_rows, train)
        out[lane] = {
            "count": len(lane_rows),
            "formula_mae_dex": round(f, 6) if f is not None else None,
            "null_mae_dex": round(n, 6) if n is not None else None,
            "formula_minus_null_dex": round(f - n, 6) if f is not None and n is not None else None,
            "formula_beats_null": (f < n) if f is not None and n is not None else None,
        }
    return out


def _seeded_split_sensitivity(rows: list[dict[str, Any]]) -> dict[str, Any]:
    systems = sorted({r["system_id"] for r in rows})
    per_seed = []
    for seed in SPLIT_SEEDS:
        shuffled = list(systems)
        random.Random(seed).shuffle(shuffled)
        n_train = round(SPLIT_TRAIN_FRACTION * len(shuffled))
        train_sys = set(shuffled[:n_train])
        train = [r for r in rows if r["system_id"] in train_sys]
        holdo = [r for r in rows if r["system_id"] not in train_sys]
        f = _mae(holdout := holdo)
        n = _null_mae(holdout, train)
        per_seed.append(round(n - f, 6) if f is not None and n is not None else None)
    positive = [m for m in per_seed if m is not None and m > 0]
    return {
        "seeds": list(SPLIT_SEEDS),
        "null_minus_formula_holdout_dex_per_seed": per_seed,
        "positive_seed_count": len(positive),
        "stable_positive": len(positive) == len(SPLIT_SEEDS),
    }


def _shuffle_control(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Break the mass-luminosity pairing; the formula margin must collapse."""
    train = [r for r in rows if r["lane"] == "train"]
    holdout = [r for r in rows if r["lane"] == "holdout"]
    real_margin = None
    f = _mae(holdout)
    n = _null_mae(holdout, train)
    if f is not None and n is not None:
        real_margin = n - f
    shuffled_margins = []
    for seed in SPLIT_SEEDS:
        lums = [r["log_lum"] for r in rows]
        random.Random(seed).shuffle(lums)
        permuted = [
            {**r, "log_lum": lum, "residual": lum - _predict(r["log_mass"])}
            for r, lum in zip(rows, lums)
        ]
        ptrain = [r for r in permuted if r["lane"] == "train"]
        phold = [r for r in permuted if r["lane"] == "holdout"]
        pf = _mae(phold)
        pn = _null_mae(phold, ptrain)
        if pf is not None and pn is not None:
            shuffled_margins.append(round(pn - pf, 6))
    return {
        "real_holdout_null_minus_formula_dex": round(real_margin, 6) if real_margin is not None else None,
        "shuffled_holdout_null_minus_formula_dex_per_seed": shuffled_margins,
        "shuffled_mean": round(_mean(shuffled_margins), 6) if shuffled_margins else None,
        "real_margin_exceeds_all_shuffled": (
            real_margin is not None
            and all(real_margin > m for m in shuffled_margins)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "agent_runs/AGENT-RUN-0073/metrics.json")
    args = parser.parse_args()

    rows = _load_primary_rows()
    ms_rows = [r for r in rows if r["stage"] == PRIMARY_STAGE]

    metrics = {
        "task_id": "TASK-0759",
        "agent_run_id": "AGENT-RUN-0073",
        "audit": "stellar_ml_stage_control_and_split_sensitivity",
        "source": "DEBCat Route 2 (local-only debs.dat; checksum-pinned; not committed)",
        "formula": "log L = 3.5 * log M (L0=1)",
        "predeclared_policy": {
            "primary_mass_range_solar": list(PRIMARY_MASS_RANGE),
            "primary_stage": PRIMARY_STAGE,
            "split_seeds": list(SPLIT_SEEDS),
            "split_train_fraction": SPLIT_TRAIN_FRACTION,
            "null": "per-mass-band train-median log_luminosity (global-median fallback)",
        },
        "primary_range_counts": {
            "all_stages": len(rows),
            "main_sequence_compatible": len(ms_rows),
        },
        "mixed_stage_frozen_lane": _frozen_lane_metrics(rows),
        "main_sequence_frozen_lane": _frozen_lane_metrics(ms_rows),
        "by_stage_holdout_formula_mae_dex": {
            stage: round(v, 6) if (v := _mae([r for r in rows if r["stage"] == stage and r["lane"] == "holdout"])) is not None else None
            for stage in DIAGNOSTIC_STAGES
        },
        "main_sequence_split_sensitivity": _seeded_split_sensitivity(ms_rows),
        "main_sequence_shuffle_control": _shuffle_control(ms_rows),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
