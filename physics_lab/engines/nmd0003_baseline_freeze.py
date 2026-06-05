"""NMD-0003 broad-surface nuclear baseline freeze helper (TASK-0531)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import numpy as np
import yaml

from physics_lab.engines.nuclear_mass_baselines import (
    MAGIC_NUMBERS,
    SemiEmpiricalCoefficients,
    evaluate_baseline,
    fit_semi_empirical_coefficients,
)
from physics_lab.engines.nuclear_masses import NuclearMassEntry, load_nuclear_mass_dataset

COEFFICIENT_KEYS = ("volume", "surface", "coulomb", "asymmetry", "pairing")


def run_nmd0003_baseline_freeze(config_path: Path) -> dict[str, Any]:
    """Run the deterministic TASK-0531 NMD-0003 baseline comparison."""
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    dataset_path = Path(config["dataset"]["snapshot_ref"])
    split_manifest_path = Path(config["dataset"]["split_manifest_ref"])
    inherited_result_path = Path(config["baseline"]["inherited_coefficients_ref"])
    validation_fraction = float(config["splits"].get("validation_holdout_fraction", 0.3))

    dataset = load_nuclear_mass_dataset(dataset_path)
    entries = sorted(dataset.entries, key=lambda entry: (entry.A, entry.Z, entry.N, entry.nuclide_id))
    split_manifest = yaml.safe_load(split_manifest_path.read_text(encoding="utf-8")) or {}
    _assert_split_manifest_matches_dataset(split_manifest, entries, dataset_path)

    split_index = max(1, int(round((1.0 - validation_fraction) * len(entries))))
    split_index = min(split_index, len(entries) - 1)
    train_entries = entries[:split_index]
    validation_entries = entries[split_index:]

    inherited_coefficients = _load_frozen_coefficients(inherited_result_path)
    nmd0003_coefficients = fit_semi_empirical_coefficients(train_entries)
    baselines = (
        (
            "inherited_result0015_nmd0002_frozen",
            inherited_coefficients,
            "Frozen RESULT-0015 / NMD-0002 coefficients reused without refit.",
        ),
        (
            "nmd0003_train_fitted_frozen",
            nmd0003_coefficients,
            "Least-squares coefficients fit only on the predeclared NMD-0003 train split.",
        ),
    )

    baseline_summaries = {}
    for baseline_id, coefficients, note in baselines:
        full_rows = evaluate_baseline(
            entries=entries,
            model_id=baseline_id,
            coefficients=coefficients,
        )
        train_rows = evaluate_baseline(
            entries=train_entries,
            model_id=baseline_id,
            coefficients=coefficients,
        )
        validation_rows = evaluate_baseline(
            entries=validation_entries,
            model_id=baseline_id,
            coefficients=coefficients,
        )
        baseline_summaries[baseline_id] = {
            "description": note,
            "coefficients": coefficients.to_dict(),
            "complexity_score": len(COEFFICIENT_KEYS),
            "fit_policy": (
                "frozen_external" if baseline_id.startswith("inherited") else "fit_train_split_only"
            ),
            "metrics": {
                "train": _residual_summary(train_rows),
                "validation_holdout": _residual_summary(validation_rows),
                "full_nmd0003_training_surface": _residual_summary(full_rows),
            },
            "subset_metrics": _subset_metrics(full_rows),
            "top_abs_residual_rows": _top_abs_residuals(full_rows, limit=10),
        }

    comparison = _comparison_summary(
        inherited=baseline_summaries["inherited_result0015_nmd0002_frozen"],
        nmd0003=baseline_summaries["nmd0003_train_fitted_frozen"],
    )
    return {
        "task_id": "TASK-0531",
        "benchmark_id": "nmd0003-broad-surface-baseline-freeze",
        "input_references": {
            "dataset": str(dataset_path),
            "split_manifest": str(split_manifest_path),
            "inherited_baseline_result": str(inherited_result_path),
        },
        "dataset_summary": {
            "dataset_id": dataset.dataset_id,
            "row_count": len(entries),
            "train_count": len(train_entries),
            "validation_holdout_count": len(validation_entries),
            "split_policy": config["splits"]["policy"],
            "post_ame2020_holdout_excluded": True,
        },
        "stop_conditions": list(config.get("stop_conditions", [])),
        "baseline_summaries": baseline_summaries,
        "comparison": comparison,
        "task0517_interpretation_update": _task0517_interpretation_update(comparison),
        "verdict": "INCONCLUSIVE",
        "limitations": [
            "NMD-0003 train/validation split is retrospective within AME2020 measured rows, not a post-AME2020 reveal.",
            "The broad-surface baseline is a fitted liquid-drop-style baseline, not a new residual-feature family.",
            "The post-AME2020 primary holdout remains excluded and unscored.",
            "Sandbox benchmark evidence only; no PRED, CLAIM, KNOW, or discovery wording is promoted.",
        ],
    }


def _assert_split_manifest_matches_dataset(
    split_manifest: dict[str, Any],
    entries: list[NuclearMassEntry],
    dataset_path: Path,
) -> None:
    manifest_dataset_path = Path(str(split_manifest.get("source_dataset"))).as_posix()
    config_dataset_path = dataset_path.as_posix()
    if manifest_dataset_path != config_dataset_path:
        raise ValueError("NMD-0003 split manifest source_dataset does not match config dataset.")
    training_split = split_manifest.get("training_split", {})
    training_ids = set(str(item) for item in training_split.get("nuclide_ids", []))
    dataset_ids = {entry.nuclide_id for entry in entries}
    if training_ids != dataset_ids:
        raise ValueError("NMD-0003 split manifest ids do not match dataset entries.")
    if int(training_split.get("row_count", -1)) != len(entries):
        raise ValueError("NMD-0003 split manifest row_count does not match dataset entries.")


def _load_frozen_coefficients(path: Path) -> SemiEmpiricalCoefficients:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for score in payload.get("scores", []):
        if score.get("model_id") != "model_fitted_semi_empirical":
            continue
        coefficients = score.get("coefficients", {})
        missing = [key for key in COEFFICIENT_KEYS if key not in coefficients]
        if missing:
            raise ValueError(f"Frozen baseline coefficients missing keys: {', '.join(missing)}")
        return SemiEmpiricalCoefficients(
            volume=float(coefficients["volume"]),
            surface=float(coefficients["surface"]),
            coulomb=float(coefficients["coulomb"]),
            asymmetry=float(coefficients["asymmetry"]),
            pairing=float(coefficients["pairing"]),
        )
    raise ValueError(f"model_fitted_semi_empirical coefficients not found in {path}")


def _residual_summary(rows: Iterable[Any]) -> dict[str, float | int | None]:
    row_list = list(rows)
    if not row_list:
        return {
            "count": 0,
            "mae_mev": None,
            "rmse_mev": None,
            "median_abs_residual_mev": None,
            "p90_abs_residual_mev": None,
            "max_abs_residual_mev": None,
        }
    residuals = np.asarray([row.residual_mev for row in row_list], dtype=float)
    abs_residuals = np.abs(residuals)
    normalized = [
        abs(row.normalized_residual)
        for row in row_list
        if row.normalized_residual is not None
    ]
    return {
        "count": len(row_list),
        "mae_mev": round(float(np.mean(abs_residuals)), 6),
        "rmse_mev": round(float(np.sqrt(np.mean(np.square(residuals)))), 6),
        "median_abs_residual_mev": round(float(np.median(abs_residuals)), 6),
        "p90_abs_residual_mev": round(float(np.percentile(abs_residuals, 90)), 6),
        "max_abs_residual_mev": round(float(np.max(abs_residuals)), 6),
        "mean_abs_normalized_residual": (
            None if not normalized else round(float(np.mean(normalized)), 6)
        ),
    }


def _subset_metrics(rows: list[Any]) -> dict[str, dict[str, Any]]:
    return {
        "a_range": _grouped_summary(rows, _a_bin),
        "z_range": _grouped_summary(rows, _z_bin),
        "n_range": _grouped_summary(rows, _n_bin),
        "magic_distance": _grouped_summary(rows, _magic_distance_bin),
        "odd_even_class": _grouped_summary(rows, lambda row: row.pairing_class),
        "neutron_richness": _grouped_summary(
            rows,
            lambda row: "neutron_rich" if row.neutron_rich else "not_neutron_rich",
        ),
    }


def _grouped_summary(rows: list[Any], key_fn: Any) -> dict[str, Any]:
    grouped: dict[str, list[Any]] = {}
    for row in rows:
        grouped.setdefault(str(key_fn(row)), []).append(row)
    return {key: _residual_summary(value) for key, value in sorted(grouped.items())}


def _a_bin(row: Any) -> str:
    if row.A <= 40:
        return "A<=40"
    if row.A <= 100:
        return "41<=A<=100"
    if row.A <= 180:
        return "101<=A<=180"
    return "A>180"


def _z_bin(row: Any) -> str:
    if row.Z <= 20:
        return "Z<=20"
    if row.Z <= 50:
        return "21<=Z<=50"
    if row.Z <= 82:
        return "51<=Z<=82"
    return "Z>82"


def _n_bin(row: Any) -> str:
    if row.N <= 28:
        return "N<=28"
    if row.N <= 82:
        return "29<=N<=82"
    if row.N <= 126:
        return "83<=N<=126"
    return "N>126"


def _magic_distance_bin(row: Any) -> str:
    distance = min(_nearest_magic_distance(row.Z), _nearest_magic_distance(row.N))
    if distance == 0:
        return "magic"
    if distance <= 2:
        return "near_magic_1_2"
    if distance <= 8:
        return "mid_distance_3_8"
    return "far_distance_gt8"


def _nearest_magic_distance(value: int) -> int:
    return min(abs(value - magic) for magic in MAGIC_NUMBERS)


def _top_abs_residuals(rows: list[Any], *, limit: int) -> list[dict[str, Any]]:
    return [
        {
            "nuclide_id": row.nuclide_id,
            "Z": row.Z,
            "N": row.N,
            "A": row.A,
            "pairing_class": row.pairing_class,
            "residual_mev": round(float(row.residual_mev), 6),
            "abs_residual_mev": round(float(abs(row.residual_mev)), 6),
            "near_magic": row.near_magic,
            "neutron_rich": row.neutron_rich,
        }
        for row in sorted(rows, key=lambda r: abs(r.residual_mev), reverse=True)[:limit]
    ]


def _comparison_summary(*, inherited: dict[str, Any], nmd0003: dict[str, Any]) -> dict[str, Any]:
    comparison: dict[str, Any] = {}
    for split_name in ("train", "validation_holdout", "full_nmd0003_training_surface"):
        inherited_metrics = inherited["metrics"][split_name]
        fitted_metrics = nmd0003["metrics"][split_name]
        comparison[split_name] = _improvement_metrics(
            inherited_metrics=inherited_metrics,
            fitted_metrics=fitted_metrics,
        )
    return comparison


def _improvement_metrics(
    *,
    inherited_metrics: dict[str, Any],
    fitted_metrics: dict[str, Any],
) -> dict[str, float]:
    inherited_mae = float(inherited_metrics["mae_mev"])
    fitted_mae = float(fitted_metrics["mae_mev"])
    inherited_rmse = float(inherited_metrics["rmse_mev"])
    fitted_rmse = float(fitted_metrics["rmse_mev"])
    return {
        "mae_improvement_mev": round(inherited_mae - fitted_mae, 6),
        "mae_relative_improvement": round((inherited_mae - fitted_mae) / inherited_mae, 6),
        "rmse_improvement_mev": round(inherited_rmse - fitted_rmse, 6),
        "rmse_relative_improvement": round((inherited_rmse - fitted_rmse) / inherited_rmse, 6),
    }


def _task0517_interpretation_update(comparison: dict[str, Any]) -> str:
    validation = comparison["validation_holdout"]
    full_surface = comparison["full_nmd0003_training_surface"]
    if validation["mae_relative_improvement"] > 0.0:
        return (
            "The broad-surface fitted baseline improves the deterministic validation split "
            "versus inherited NMD-0002 coefficients. TASK-0517 should remain interpreted as "
            "control-dominated factory memory under a mismatched inherited baseline, not as "
            "evidence against all future NMD-0003 residual-family testing."
        )
    return (
        "The train-fitted NMD-0003 baseline improves train/full-surface MAE but worsens the "
        "predeclared validation holdout versus inherited NMD-0002 coefficients. TASK-0517 "
        "therefore remains control-dominated memory, and a future factory sprint should not "
        "assume that a broad-surface least-squares baseline alone removes baseline mismatch."
        f" Full-surface MAE relative improvement: {full_surface['mae_relative_improvement']}; "
        f"validation MAE relative improvement: {validation['mae_relative_improvement']}."
    )
