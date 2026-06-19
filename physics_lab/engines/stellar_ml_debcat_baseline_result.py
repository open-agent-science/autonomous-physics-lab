"""Engine for the Stellar M-L DEBCat benchmark RESULT-0022 (Gate B replayable).

Deterministically recomputes every number RESULT-0022 reports from the committed
CC-BY-4.0 DEBCat normalized rows and their frozen system-level holdout lanes:
the textbook single/piecewise/fitted exponents and the per-mass-band null on the
main-sequence slice, seeded system-level split-sensitivity, deterministic
luminosity-shuffle controls, the by-stage confound diagnostic, and the per-model
relative-error scores. Pure and deterministic; reads only committed data. This is
the regenerate-and-compare source the Gate B validator re-runs via ``physics-lab run``.
"""

from __future__ import annotations

import random
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ROWS = REPO_ROOT / "data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml"

PRIMARY_MASS_RANGE = (0.5, 2.0)  # half-open [lo, hi)
PRIMARY_STAGE = "main_sequence_compatible"
SPLIT_SEEDS = (11, 23, 37, 53, 71)
SPLIT_TRAIN_FRACTION = 0.7
TEXTBOOK_ALPHA = 3.5
PIECEWISE_ALPHA = 4.0
STAGE_ORDER = ("main_sequence_compatible", "subgiant", "evolved", "unknown")


def _admitted_primary_rows() -> list[dict[str, Any]]:
    doc = yaml.safe_load(ROWS.read_text(encoding="utf-8"))
    rows = doc["rows"]
    lo, hi = PRIMARY_MASS_RANGE
    return [r for r in rows if r.get("admissibility") == "admitted" and lo <= float(r["mass_solar"]) < hi]


def _mae(rows: list[dict[str, Any]], predict: Callable[[dict[str, Any]], float]) -> float:
    return statistics.fmean(abs(float(r["log_luminosity_solar"]) - predict(r)) for r in rows)


def _alpha_mae(rows: list[dict[str, Any]], alpha: float) -> float:
    return _mae(rows, lambda r: alpha * float(r["log_mass_solar"]))


def _fit_alpha(train: list[dict[str, Any]]) -> float:
    sxx = sum(float(r["log_mass_solar"]) ** 2 for r in train)
    sxy = sum(float(r["log_mass_solar"]) * float(r["log_luminosity_solar"]) for r in train)
    return sxy / sxx


def _massband_null_predictor(train: list[dict[str, Any]]) -> Callable[[dict[str, Any]], float]:
    band: dict[str, list[float]] = defaultdict(list)
    for r in train:
        band[r["mass_band"]].append(float(r["log_luminosity_solar"]))
    band_median = {k: statistics.median(v) for k, v in band.items()}
    global_median = statistics.median([float(r["log_luminosity_solar"]) for r in train])
    return lambda r: band_median.get(r["mass_band"], global_median)


def _rel_errors(rows: list[dict[str, Any]], log_predict: Callable[[dict[str, Any]], float]) -> tuple[float, float]:
    errors = []
    for r in rows:
        predicted_l = 10 ** log_predict(r)
        actual_l = float(r["luminosity_solar"])
        errors.append(abs(predicted_l - actual_l) / actual_l)
    return round(statistics.fmean(errors), 6), round(max(errors), 6)


def compute_result_metrics() -> dict[str, Any]:
    """Recompute every number RESULT-0022 reports, deterministically, from committed data."""
    primary = _admitted_primary_rows()
    ms = [r for r in primary if r.get("evolutionary_stage_flag") == PRIMARY_STAGE]
    train = [r for r in ms if r["lane"] == "train"]
    holdout = [r for r in ms if r["lane"] == "holdout"]
    validation = [r for r in ms if r["lane"] == "validation"]

    fitted_alpha = _fit_alpha(train)
    null_pred = _massband_null_predictor(train)
    global_train_median = statistics.median([float(r["log_luminosity_solar"]) for r in train])
    distinct_mass_bands = len({r["mass_band"] for r in train})

    alpha_3p5_mae = round(_alpha_mae(holdout, TEXTBOOK_ALPHA), 6)
    alpha_4p0_mae = round(_alpha_mae(holdout, PIECEWISE_ALPHA), 6)
    fitted_mae = round(_alpha_mae(holdout, fitted_alpha), 6)
    null_mae = round(_mae(holdout, null_pred), 6)
    margin = round(null_mae - alpha_3p5_mae, 6)

    # seeded system-level split sensitivity (null - formula margin per seed)
    systems = sorted({r["system_id"] for r in ms})
    split_per_seed = []
    for seed in SPLIT_SEEDS:
        shuffled = list(systems)
        random.Random(seed).shuffle(shuffled)
        n_train = round(SPLIT_TRAIN_FRACTION * len(shuffled))
        train_sys = set(shuffled[:n_train])
        s_train = [r for r in ms if r["system_id"] in train_sys]
        s_hold = [r for r in ms if r["system_id"] not in train_sys]
        seed_margin = _mae(s_hold, _massband_null_predictor(s_train)) - _alpha_mae(s_hold, TEXTBOOK_ALPHA)
        split_per_seed.append(round(seed_margin, 6))

    # deterministic luminosity-shuffle control on the frozen holdout lane
    shuffle_per_seed = []
    for seed in SPLIT_SEEDS:
        lums = [float(r["log_luminosity_solar"]) for r in ms]
        random.Random(seed).shuffle(lums)
        permuted = [dict(r, log_luminosity_solar=lum) for r, lum in zip(ms, lums)]
        p_train = [r for r in permuted if r["lane"] == "train"]
        p_hold = [r for r in permuted if r["lane"] == "holdout"]
        shuffle_margin = _mae(p_hold, _massband_null_predictor(p_train)) - _alpha_mae(p_hold, TEXTBOOK_ALPHA)
        shuffle_per_seed.append(round(shuffle_margin, 6))

    # by-stage holdout formula (alpha=3.5) MAE — diagnostic over the primary range
    by_stage: dict[str, float] = {}
    for stage in STAGE_ORDER:
        stage_holdout = [
            r for r in primary if r.get("evolutionary_stage_flag", "unknown") == stage and r["lane"] == "holdout"
        ]
        if stage_holdout:
            by_stage[stage] = round(_alpha_mae(stage_holdout, TEXTBOOK_ALPHA), 6)

    def fitted_log(r: dict[str, Any]) -> float:
        return fitted_alpha * float(r["log_mass_solar"])

    def piece_log(r: dict[str, Any]) -> float:
        return PIECEWISE_ALPHA * float(r["log_mass_solar"])

    def single_log(r: dict[str, Any]) -> float:
        return TEXTBOOK_ALPHA * float(r["log_mass_solar"])

    scores = {}
    for key, fn in (("fitted", fitted_log), ("piecewise", piece_log), ("single", single_log), ("null", null_pred)):
        tr = _rel_errors(train, fn)
        te = _rel_errors(holdout, fn)
        scores[key] = {
            "train_mean_relative_error": tr[0],
            "train_max_relative_error": tr[1],
            "test_mean_relative_error": te[0],
            "test_max_relative_error": te[1],
        }

    single_minus_fitted = round(alpha_3p5_mae - fitted_mae, 6)
    single_minus_piecewise = round(alpha_3p5_mae - alpha_4p0_mae, 6)
    return {
        "main_sequence_components": len(ms),
        "train_count": len(train),
        "validation_count": len(validation),
        "holdout_count": len(holdout),
        "alpha_3p5_holdout_mae": alpha_3p5_mae,
        "alpha_4p0_holdout_mae": alpha_4p0_mae,
        "fitted_alpha": round(fitted_alpha, 6),
        "fitted_holdout_mae": fitted_mae,
        "null_holdout_mae": null_mae,
        "margin_dex": margin,
        "single_minus_fitted_dex": single_minus_fitted,
        "single_minus_piecewise_dex": single_minus_piecewise,
        "split_seeds_evaluated": len(SPLIT_SEEDS),
        "split_positive_seed_count": sum(1 for x in split_per_seed if x > 0),
        "split_margin_min_dex": round(min(split_per_seed), 6),
        "split_margin_max_dex": round(max(split_per_seed), 6),
        "shuffle_real_margin_dex": margin,
        "shuffle_margin_max_dex": round(max(shuffle_per_seed), 6),
        "shuffle_real_exceeds_all": all(margin > x for x in shuffle_per_seed),
        "by_stage_holdout_mae_dex": by_stage,
        "fitted_alpha_coeff": round(fitted_alpha, 6),
        "global_train_median_log_l": round(global_train_median, 6),
        "distinct_train_mass_bands": distinct_mass_bands,
        "scores": scores,
    }


__all__ = ["compute_result_metrics"]
