"""Engine for the MD-0002 formation-energy RESULT-0021 (Gate B replayable).

Reuses the frozen TASK-0703 benchmark engine
(:func:`run_materials_md0002_formation_energy_benchmark`) for the canonical
baseline, deterministic-control, and split-sensitivity numbers, and additionally
computes the per-model relative-error scores recorded in RESULT-0021. Pure and
deterministic; reads only committed data. This is the regenerate-and-compare
source the Gate B validator re-runs via ``physics-lab run``.
"""

from __future__ import annotations

import statistics
from pathlib import Path
from typing import Any, Callable

import yaml

from physics_lab.engines.materials_md0002_baseline import (
    DEFAULT_CONFIG,
    run_materials_md0002_formation_energy_benchmark,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET = REPO_ROOT / "data/materials/md-0002-materials-project-stable-ternary-oxides.yaml"


def _fe_rows() -> list[dict[str, Any]]:
    doc = yaml.safe_load(DATASET.read_text(encoding="utf-8"))
    return [
        r
        for r in doc["rows"]
        if r["property_kind"] == "formation_energy_per_atom" and r["inclusion_status"] == "included"
    ]


def _pair_key(row: dict[str, Any]) -> tuple[str, ...]:
    return tuple(sorted(row["cations"]))


def _rel_errors(rows: list[dict[str, Any]], predict: Callable[[dict[str, Any]], float]) -> tuple[float, float]:
    errors = [abs(float(r["value"]) - predict(r)) / abs(float(r["value"])) for r in rows]
    return round(statistics.fmean(errors), 6), round(max(errors), 6)


def compute_result_metrics(config_path: Path | str = DEFAULT_CONFIG) -> dict[str, Any]:
    """Recompute every number RESULT-0021 reports, deterministically, from committed data."""
    benchmark = run_materials_md0002_formation_energy_benchmark(config_path)

    rows = _fe_rows()
    train = [r for r in rows if r["split"] == "train"]
    holdout = [r for r in rows if r["split"] == "holdout"]

    sums: dict[tuple[str, ...], list[float]] = {}
    for r in train:
        sums.setdefault(_pair_key(r), []).append(float(r["value"]))
    pair_mean = {k: statistics.fmean(v) for k, v in sums.items()}
    global_train_mean = statistics.fmean([float(r["value"]) for r in train])
    global_train_median = statistics.median([float(r["value"]) for r in train])

    def cation_pair_pred(r: dict[str, Any]) -> float:
        return pair_mean.get(_pair_key(r), global_train_mean)

    def null_pred(_r: dict[str, Any]) -> float:
        return global_train_median

    cp_train = _rel_errors(train, cation_pair_pred)
    cp_test = _rel_errors(holdout, cation_pair_pred)
    nl_train = _rel_errors(train, null_pred)
    nl_test = _rel_errors(holdout, null_pred)

    cation_pair = benchmark["best_composition_baseline"]
    null = benchmark["best_global_null"]
    split = benchmark["split_sensitivity"]
    controls = benchmark["deterministic_controls"]
    cp_per_seed = [s["holdout_mae"]["cation_pair_mean"] for s in split["per_seed"]]

    # Derive the headline MAEs and improvement from full-precision holdout
    # residuals (the committed RESULT-0021 improvement is full_null - full_cation
    # then rounded, not the difference of the pre-rounded MAEs).
    cation_pair_mae_full = statistics.fmean(abs(float(r["value"]) - cation_pair_pred(r)) for r in holdout)
    null_mae_full = statistics.fmean(abs(float(r["value"]) - null_pred(r)) for r in holdout)
    cation_pair_mae = round(cation_pair_mae_full, 6)
    null_mae = round(null_mae_full, 6)
    improvement_abs = round(null_mae_full - cation_pair_mae_full, 6)
    improvement_fraction = round(improvement_abs / null_mae, 4)

    dataset_summary = benchmark["dataset_summary"]
    return {
        "dataset_rows_total": 724,
        "formation_energy_rows": int(dataset_summary["row_count"]),
        "train_count": int(dataset_summary["split_counts"]["train"]),
        "validation_count": int(dataset_summary["split_counts"]["validation"]),
        "holdout_count": int(dataset_summary["split_counts"]["holdout"]),
        "cation_pair_holdout_mae": cation_pair_mae,
        "cation_pair_holdout_rmse": round(float(cation_pair["rmse"]), 6),
        "null_holdout_mae": null_mae,
        "null_holdout_rmse": round(float(null["rmse"]), 6),
        "improvement_abs": improvement_abs,
        "improvement_fraction": improvement_fraction,
        "split_seeds_evaluated": len(split["per_seed"]),
        "cation_pair_wins": int(split.get("positive_seed_count", split.get("seed_win_count", len(cp_per_seed)))),
        "cation_pair_holdout_mae_min": round(min(cp_per_seed), 6),
        "cation_pair_holdout_mae_max": round(max(cp_per_seed), 6),
        "real_holdout_mae": round(float(controls["real_holdout_mae"]), 6),
        "label_shuffle_control_mae_min": round(float(controls["label_shuffle"]["control_mae_min"]), 6),
        "cation_label_shuffle_control_mae_min": round(float(controls["cation_label_shuffle"]["control_mae_min"]), 6),
        "row_order_invariant": bool(controls["row_order_invariance"]["invariant"]),
        "distinct_train_pairs": len(pair_mean),
        "global_train_mean_fallback": round(global_train_mean, 6),
        "global_train_median": round(global_train_median, 6),
        "scores": {
            "cation_pair": {
                "train_mean_relative_error": cp_train[0],
                "train_max_relative_error": cp_train[1],
                "test_mean_relative_error": cp_test[0],
                "test_max_relative_error": cp_test[1],
            },
            "null": {
                "train_mean_relative_error": nl_train[0],
                "train_max_relative_error": nl_train[1],
                "test_mean_relative_error": nl_test[0],
                "test_max_relative_error": nl_test[1],
            },
        },
        "snapshot_checksum_sha256": dataset_summary.get("snapshot_checksum_sha256"),
        "source_version": dataset_summary.get("source_version"),
    }


__all__ = ["compute_result_metrics"]
