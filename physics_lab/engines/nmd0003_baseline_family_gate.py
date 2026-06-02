"""NMD-0003 baseline-family gate helper (TASK-0535).

This module compares physically standard nuclear-mass baseline *families* on the
committed NMD-0003 AME2020 measured training surface. It does not introduce any
residual-feature hypothesis family, shell-axis term, local-curvature term,
high-error cluster label, or post-hoc correction term. The only degrees of
freedom are the five liquid-drop coefficients and predeclared fitting policies
(ordinary least squares, weighted least squares, ridge regularization, and a
region-stratified coefficient diagnostic), evaluated under two predeclared
deterministic splits to separate domain mismatch from baseline-family weakness.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable

import numpy as np
import yaml

from physics_lab.engines.nuclear_mass_baselines import (
    MAGIC_NUMBERS,
    SemiEmpiricalCoefficients,
    evaluate_baseline,
    fit_semi_empirical_coefficients,
    fit_semi_empirical_coefficients_ridge,
    fit_semi_empirical_coefficients_weighted,
)
from physics_lab.engines.nuclear_masses import NuclearMassEntry, load_nuclear_mass_dataset

COEFFICIENT_KEYS = ("volume", "surface", "coulomb", "asymmetry", "pairing")

# Predeclared region partition for the region-stratified coefficient diagnostic
# and for the A-range residual slice. Bounds are inclusive on the lower edge.
A_REGION_BOUNDS = ("A<=40", "41<=A<=100", "101<=A<=180", "A>180")
REGION_MIN_TRAIN_ROWS = 30


def run_nmd0003_baseline_family_gate(config_path: Path) -> dict[str, Any]:
    """Run the deterministic TASK-0535 NMD-0003 baseline-family comparison."""
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    dataset_path = Path(config["dataset"]["snapshot_ref"])
    split_manifest_path = Path(config["dataset"]["split_manifest_ref"])
    inherited_result_path = Path(config["baseline"]["inherited_coefficients_ref"])
    validation_fraction = float(config["splits"].get("validation_holdout_fraction", 0.3))
    ridge_alpha = float(config["families"]["ridge"]["alpha"])
    wls_policy = str(config["families"]["weighted_least_squares"]["weight_policy"])

    dataset = load_nuclear_mass_dataset(dataset_path)
    entries = sorted(
        dataset.entries, key=lambda entry: (entry.A, entry.Z, entry.N, entry.nuclide_id)
    )
    split_manifest = yaml.safe_load(split_manifest_path.read_text(encoding="utf-8")) or {}
    _assert_split_manifest_matches_dataset(split_manifest, entries, dataset_path)

    inherited_coefficients = _load_frozen_coefficients(inherited_result_path)

    declared_splits = {
        "sorted_aZN_70_30": (
            "Inherited TASK-0516/TASK-0531 split: sort by (A, Z, N) and assign the "
            "first 70% to train and the trailing 30% to the validation holdout. "
            "Because A is the primary sort key, the validation holdout is the "
            "heavy-mass tail, making it an extrapolation holdout."
        ),
        "stratified_interleaved_70_30": (
            "Deterministic stratified split over the same sorted order: assign a row "
            "to the validation holdout when its sorted index modulo 10 is >= 7. This "
            "keeps every mass region represented in both train and validation, so it "
            "is an interpolation holdout."
        ),
    }

    splits_output: dict[str, Any] = {}
    for split_id in ("sorted_aZN_70_30", "stratified_interleaved_70_30"):
        train_entries, validation_entries = _split_entries(
            entries, split_id=split_id, validation_fraction=validation_fraction
        )
        families = _fit_family_coefficients(
            train_entries=train_entries,
            inherited_coefficients=inherited_coefficients,
            ridge_alpha=ridge_alpha,
            wls_policy=wls_policy,
        )
        include_subsets = split_id == "sorted_aZN_70_30"
        baseline_summaries = {
            family_id: _summarize_family(
                family=family,
                entries=entries,
                train_entries=train_entries,
                validation_entries=validation_entries,
                include_subsets=include_subsets,
            )
            for family_id, family in families.items()
        }
        comparisons = {
            family_id: _comparison_vs_inherited(
                inherited=baseline_summaries["inherited_result0015_nmd0002_frozen"],
                candidate=baseline_summaries[family_id],
            )
            for family_id in families
            if family_id != "inherited_result0015_nmd0002_frozen"
        }
        splits_output[split_id] = {
            "description": declared_splits[split_id],
            "train_count": len(train_entries),
            "validation_holdout_count": len(validation_entries),
            "subset_breakdown_included": include_subsets,
            "baseline_summaries": baseline_summaries,
            "comparisons_vs_inherited": comparisons,
        }

    split_sensitivity = _split_sensitivity_diagnostic(splits_output)
    region_diagnostic = _region_coefficient_diagnostic(
        entries=entries,
        validation_fraction=validation_fraction,
    )
    recommendation = _recommendation(
        split_sensitivity=split_sensitivity,
        region_diagnostic=region_diagnostic,
        splits_output=splits_output,
    )

    return {
        "task_id": "TASK-0535",
        "benchmark_id": "nmd0003-baseline-family-gate",
        "input_references": {
            "dataset": str(dataset_path),
            "split_manifest": str(split_manifest_path),
            "inherited_baseline_result": str(inherited_result_path),
            "prior_run": "agent_runs/AGENT-RUN-0055/metrics.json",
        },
        "dataset_summary": {
            "dataset_id": dataset.dataset_id,
            "row_count": len(entries),
            "post_ame2020_holdout_excluded": True,
        },
        "declared_baseline_families": _declared_family_descriptions(ridge_alpha, wls_policy),
        "declared_splits": declared_splits,
        "stop_conditions": list(config.get("stop_conditions", [])),
        "splits": splits_output,
        "split_sensitivity_diagnostic": split_sensitivity,
        "region_coefficient_diagnostic": region_diagnostic,
        "recommendation": recommendation,
        "verdict": "INCONCLUSIVE",
        "limitations": [
            "Both splits are retrospective inside AME2020 measured rows, not a "
            "post-AME2020 reveal.",
            "All families are five-coefficient liquid-drop baselines; no "
            "residual-feature, shell-axis, or local-curvature family is tested.",
            "The primary post-AME2020 holdout remains excluded and unscored.",
            "Sandbox benchmark evidence only; no PRED, CLAIM, KNOW, or discovery "
            "wording is promoted.",
        ],
    }


# --------------------------------------------------------------------------- #
# Splits
# --------------------------------------------------------------------------- #


def _split_entries(
    entries: list[NuclearMassEntry],
    *,
    split_id: str,
    validation_fraction: float,
) -> tuple[list[NuclearMassEntry], list[NuclearMassEntry]]:
    if split_id == "sorted_aZN_70_30":
        split_index = max(1, int(round((1.0 - validation_fraction) * len(entries))))
        split_index = min(split_index, len(entries) - 1)
        return entries[:split_index], entries[split_index:]
    if split_id == "stratified_interleaved_70_30":
        # Deterministic modulo stratification over the sorted order. A validation
        # fraction of 0.3 maps to "index % 10 in {7, 8, 9}".
        cutoff = int(round((1.0 - validation_fraction) * 10))
        train = [entry for index, entry in enumerate(entries) if index % 10 < cutoff]
        validation = [entry for index, entry in enumerate(entries) if index % 10 >= cutoff]
        return train, validation
    raise ValueError(f"Unknown split id: {split_id}")


# --------------------------------------------------------------------------- #
# Family fitting
# --------------------------------------------------------------------------- #


def _fit_family_coefficients(
    *,
    train_entries: list[NuclearMassEntry],
    inherited_coefficients: SemiEmpiricalCoefficients,
    ridge_alpha: float,
    wls_policy: str,
) -> dict[str, dict[str, Any]]:
    ols = fit_semi_empirical_coefficients(train_entries)
    weights = _weight_vector(train_entries, policy=wls_policy)
    wls = fit_semi_empirical_coefficients_weighted(train_entries, weights=weights)
    ridge = fit_semi_empirical_coefficients_ridge(train_entries, alpha=ridge_alpha)
    region_coefficients = _fit_region_coefficients(train_entries, fallback=ols)

    return {
        "inherited_result0015_nmd0002_frozen": {
            "fit_policy": "frozen_external",
            "evaluator": _global_evaluator(inherited_coefficients),
            "coefficients": inherited_coefficients.to_dict(),
        },
        "nmd0003_train_fitted_ols": {
            "fit_policy": "fit_train_split_only_ols",
            "evaluator": _global_evaluator(ols),
            "coefficients": ols.to_dict(),
        },
        "nmd0003_train_fitted_wls": {
            "fit_policy": f"fit_train_split_only_wls:{wls_policy}",
            "evaluator": _global_evaluator(wls),
            "coefficients": wls.to_dict(),
        },
        "nmd0003_train_fitted_ridge": {
            "fit_policy": f"fit_train_split_only_ridge:alpha={ridge_alpha}",
            "evaluator": _global_evaluator(ridge),
            "coefficients": ridge.to_dict(),
        },
        "nmd0003_region_stratified_diagnostic": {
            "fit_policy": "fit_train_split_only_region_stratified_ols",
            "evaluator": _region_evaluator(region_coefficients, fallback=ols),
            "coefficients": {
                region: coefficients.to_dict()
                for region, coefficients in region_coefficients.items()
            },
        },
    }


def _weight_vector(entries: Iterable[NuclearMassEntry], *, policy: str) -> list[float]:
    if policy == "inverse_mass_number":
        return [1.0 / float(entry.A) for entry in entries]
    raise ValueError(f"Unknown weighted-least-squares policy: {policy}")


def _fit_region_coefficients(
    train_entries: list[NuclearMassEntry],
    *,
    fallback: SemiEmpiricalCoefficients,
) -> dict[str, SemiEmpiricalCoefficients]:
    grouped: dict[str, list[NuclearMassEntry]] = {}
    for entry in train_entries:
        grouped.setdefault(_a_region(entry.A), []).append(entry)
    region_coefficients: dict[str, SemiEmpiricalCoefficients] = {}
    for region in A_REGION_BOUNDS:
        rows = grouped.get(region, [])
        if len(rows) >= REGION_MIN_TRAIN_ROWS:
            region_coefficients[region] = fit_semi_empirical_coefficients(rows)
        else:
            region_coefficients[region] = fallback
    return region_coefficients


def _global_evaluator(
    coefficients: SemiEmpiricalCoefficients,
) -> Callable[[list[NuclearMassEntry], str], list[Any]]:
    def evaluator(entries: list[NuclearMassEntry], model_id: str) -> list[Any]:
        return evaluate_baseline(entries=entries, model_id=model_id, coefficients=coefficients)

    return evaluator


def _region_evaluator(
    region_coefficients: dict[str, SemiEmpiricalCoefficients],
    *,
    fallback: SemiEmpiricalCoefficients,
) -> Callable[[list[NuclearMassEntry], str], list[Any]]:
    def evaluator(entries: list[NuclearMassEntry], model_id: str) -> list[Any]:
        rows: list[Any] = []
        for region in A_REGION_BOUNDS:
            region_entries = [entry for entry in entries if _a_region(entry.A) == region]
            if not region_entries:
                continue
            coefficients = region_coefficients.get(region, fallback)
            rows.extend(
                evaluate_baseline(
                    entries=region_entries, model_id=model_id, coefficients=coefficients
                )
            )
        rows.sort(key=lambda row: (row.A, row.Z, row.N, row.nuclide_id))
        return rows

    return evaluator


# --------------------------------------------------------------------------- #
# Summaries
# --------------------------------------------------------------------------- #


def _summarize_family(
    *,
    family: dict[str, Any],
    entries: list[NuclearMassEntry],
    train_entries: list[NuclearMassEntry],
    validation_entries: list[NuclearMassEntry],
    include_subsets: bool,
) -> dict[str, Any]:
    evaluator: Callable[[list[NuclearMassEntry], str], list[Any]] = family["evaluator"]
    model_id = "baseline_family"
    full_rows = evaluator(entries, model_id)
    train_rows = evaluator(train_entries, model_id)
    validation_rows = evaluator(validation_entries, model_id)
    summary: dict[str, Any] = {
        "fit_policy": family["fit_policy"],
        "coefficients": family["coefficients"],
        "complexity_score": len(COEFFICIENT_KEYS),
        "metrics": {
            "train": _residual_summary(train_rows),
            "validation_holdout": _residual_summary(validation_rows),
            "full_nmd0003_training_surface": _residual_summary(full_rows),
        },
    }
    if include_subsets:
        summary["subset_metrics"] = _subset_metrics(full_rows)
        summary["top_abs_residual_rows"] = _top_abs_residuals(full_rows, limit=10)
    return summary


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
            "mean_abs_normalized_residual": None,
        }
    residuals = np.asarray([row.residual_mev for row in row_list], dtype=float)
    abs_residuals = np.abs(residuals)
    normalized = [
        abs(row.normalized_residual) for row in row_list if row.normalized_residual is not None
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
        "a_range": _grouped_summary(rows, lambda row: _a_region(row.A)),
        "z_range": _grouped_summary(rows, _z_bin),
        "n_range": _grouped_summary(rows, _n_bin),
        "magic_distance": _grouped_summary(rows, _magic_distance_bin),
        "odd_even_class": _grouped_summary(rows, lambda row: row.pairing_class),
        "neutron_richness": _grouped_summary(
            rows,
            lambda row: "neutron_rich" if row.neutron_rich else "not_neutron_rich",
        ),
    }


def _grouped_summary(rows: list[Any], key_fn: Callable[[Any], str]) -> dict[str, Any]:
    grouped: dict[str, list[Any]] = {}
    for row in rows:
        grouped.setdefault(str(key_fn(row)), []).append(row)
    return {key: _residual_summary(value) for key, value in sorted(grouped.items())}


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


def _comparison_vs_inherited(
    *, inherited: dict[str, Any], candidate: dict[str, Any]
) -> dict[str, Any]:
    comparison: dict[str, Any] = {}
    for split_name in ("train", "validation_holdout", "full_nmd0003_training_surface"):
        comparison[split_name] = _improvement_metrics(
            inherited_metrics=inherited["metrics"][split_name],
            candidate_metrics=candidate["metrics"][split_name],
        )
    return comparison


def _improvement_metrics(
    *, inherited_metrics: dict[str, Any], candidate_metrics: dict[str, Any]
) -> dict[str, float]:
    inherited_mae = float(inherited_metrics["mae_mev"])
    candidate_mae = float(candidate_metrics["mae_mev"])
    inherited_rmse = float(inherited_metrics["rmse_mev"])
    candidate_rmse = float(candidate_metrics["rmse_mev"])
    return {
        "mae_improvement_mev": round(inherited_mae - candidate_mae, 6),
        "mae_relative_improvement": round((inherited_mae - candidate_mae) / inherited_mae, 6),
        "rmse_improvement_mev": round(inherited_rmse - candidate_rmse, 6),
        "rmse_relative_improvement": round((inherited_rmse - candidate_rmse) / inherited_rmse, 6),
    }


# --------------------------------------------------------------------------- #
# Diagnostics
# --------------------------------------------------------------------------- #


def _split_sensitivity_diagnostic(splits_output: dict[str, Any]) -> dict[str, Any]:
    """Compare candidate-family validation behavior across the two splits.

    If a family regresses on the sorted (extrapolation) holdout but improves on
    the stratified (interpolation) holdout, the TASK-0531 regression is dominated
    by domain mismatch rather than baseline-family weakness.
    """
    families = (
        "nmd0003_train_fitted_ols",
        "nmd0003_train_fitted_wls",
        "nmd0003_train_fitted_ridge",
        "nmd0003_region_stratified_diagnostic",
    )
    per_family: dict[str, Any] = {}
    for family_id in families:
        sorted_val = splits_output["sorted_aZN_70_30"]["comparisons_vs_inherited"][family_id][
            "validation_holdout"
        ]["mae_relative_improvement"]
        stratified_val = splits_output["stratified_interleaved_70_30"][
            "comparisons_vs_inherited"
        ][family_id]["validation_holdout"]["mae_relative_improvement"]
        per_family[family_id] = {
            "sorted_validation_mae_relative_improvement": sorted_val,
            "stratified_validation_mae_relative_improvement": stratified_val,
            "regresses_on_sorted_split": sorted_val < 0.0,
            "improves_on_stratified_split": stratified_val > 0.0,
            "domain_mismatch_signature": sorted_val < 0.0 and stratified_val > 0.0,
        }

    ols = per_family["nmd0003_train_fitted_ols"]
    if ols["domain_mismatch_signature"]:
        interpretation = (
            "The ordinary least-squares refit regresses on the sorted "
            "(extrapolation) validation holdout but improves on the stratified "
            "(interpolation) validation holdout. The TASK-0531 validation "
            "regression is therefore dominated by domain mismatch: the sorted "
            "split places the heavy-mass tail entirely in the holdout, so the "
            "refit is being asked to extrapolate beyond its train support. It is "
            "not primarily evidence that the liquid-drop baseline family is weak."
        )
        dominant_factor = "domain_mismatch_extrapolation_split"
    elif ols["sorted_validation_mae_relative_improvement"] < 0.0:
        interpretation = (
            "The ordinary least-squares refit regresses on both the sorted and "
            "stratified validation holdouts versus the inherited frozen baseline. "
            "The TASK-0531 regression is not explained by the extrapolation split "
            "alone, which points at baseline-family weakness or inherited-coefficient "
            "advantage rather than pure domain mismatch."
        )
        dominant_factor = "baseline_family_weakness"
    else:
        interpretation = (
            "The ordinary least-squares refit improves the sorted validation "
            "holdout, so the specific TASK-0531 regression signature is not "
            "reproduced under this configuration."
        )
        dominant_factor = "no_regression_reproduced"

    return {
        "per_family": per_family,
        "dominant_factor": dominant_factor,
        "interpretation": interpretation,
    }


def _region_coefficient_diagnostic(
    *, entries: list[NuclearMassEntry], validation_fraction: float
) -> dict[str, Any]:
    """Report how the fitted liquid-drop coefficients drift across mass regions.

    Large drift between region coefficients indicates that a single global
    coefficient vector cannot fit all mass regions at once, which is a structural
    (baseline-family) limitation independent of the split.
    """
    train_entries, _ = _split_entries(
        entries, split_id="sorted_aZN_70_30", validation_fraction=validation_fraction
    )
    global_coefficients = fit_semi_empirical_coefficients(train_entries)
    region_coefficients = _fit_region_coefficients(train_entries, fallback=global_coefficients)

    region_dict = {
        region: coefficients.to_dict() for region, coefficients in region_coefficients.items()
    }
    spreads: dict[str, dict[str, float]] = {}
    for key in COEFFICIENT_KEYS:
        values = [region_dict[region][key] for region in A_REGION_BOUNDS]
        global_value = getattr(global_coefficients, key)
        spreads[key] = {
            "min": round(float(min(values)), 6),
            "max": round(float(max(values)), 6),
            "range": round(float(max(values) - min(values)), 6),
            "global": round(float(global_value), 6),
            "relative_range": (
                round(float((max(values) - min(values)) / abs(global_value)), 6)
                if global_value != 0.0
                else None
            ),
        }
    max_relative_range = max(
        spread["relative_range"]
        for spread in spreads.values()
        if spread["relative_range"] is not None
    )
    return {
        "global_train_coefficients": global_coefficients.to_dict(),
        "region_train_coefficients": region_dict,
        "coefficient_spread": spreads,
        "max_relative_coefficient_range": round(float(max_relative_range), 6),
        "interpretation": (
            "Liquid-drop coefficients fitted independently per mass region differ "
            "from the global train fit; the largest relative coefficient range "
            f"across regions is {max_relative_range:.3f}. A non-trivial drift means "
            "a single global five-coefficient vector is itself a limiting factor, "
            "separate from the split choice."
        ),
    }


def _recommendation(
    *,
    split_sensitivity: dict[str, Any],
    region_diagnostic: dict[str, Any],
    splits_output: dict[str, Any],
) -> dict[str, Any]:
    dominant_factor = split_sensitivity["dominant_factor"]
    best_family_id, best_strat_improvement = _best_stratified_family(splits_output)
    coefficient_drift = float(region_diagnostic["max_relative_coefficient_range"])

    if dominant_factor == "domain_mismatch_extrapolation_split":
        decision = "create_narrower_baseline_follow_up"
        rationale = (
            "The TASK-0531 validation regression is a sorted-split extrapolation "
            "artifact, not baseline-family failure. Before any residual-feature "
            "sprint, adopt a stratified (interpolation) validation split so the "
            "Nuclear gate measures interpolation skill rather than heavy-mass "
            "extrapolation. The follow-up should freeze the stratified split policy "
            "and the winning baseline family, then re-evaluate readiness."
        )
    elif dominant_factor == "baseline_family_weakness":
        decision = "pause_nuclear_factory_work_until_baseline_or_split_coverage_improves"
        rationale = (
            "Refitting the liquid-drop family regresses on both splits, so neither "
            "a better fit policy nor a stratified split rescues the inherited "
            "baseline. Pause residual-feature factory work until a stronger "
            "baseline family or improved source/split coverage is available."
        )
    else:
        decision = "create_narrower_baseline_follow_up"
        rationale = (
            "The specific TASK-0531 regression signature was not reproduced. A "
            "narrower follow-up should confirm the winning baseline family and "
            "split policy before committing to a residual-feature sprint."
        )

    return {
        "decision": decision,
        "winning_family_under_stratified_split": best_family_id,
        "winning_family_stratified_validation_mae_relative_improvement": best_strat_improvement,
        "region_coefficient_drift_relative_range": coefficient_drift,
        "rationale": rationale,
        "allowed_options_considered": [
            "promote a scoped baseline benchmark result",
            "create a narrower baseline follow-up",
            "permit a bounded residual-feature sprint with the winning baseline frozen",
            "pause Nuclear factory work until source/split coverage improves",
        ],
    }


def _best_stratified_family(splits_output: dict[str, Any]) -> tuple[str, float]:
    comparisons = splits_output["stratified_interleaved_70_30"]["comparisons_vs_inherited"]
    best_family = ""
    best_value = float("-inf")
    for family_id, comparison in comparisons.items():
        value = float(comparison["validation_holdout"]["mae_relative_improvement"])
        if value > best_value:
            best_value = value
            best_family = family_id
    return best_family, round(best_value, 6)


# --------------------------------------------------------------------------- #
# Shared helpers
# --------------------------------------------------------------------------- #


def _declared_family_descriptions(ridge_alpha: float, wls_policy: str) -> dict[str, str]:
    return {
        "inherited_result0015_nmd0002_frozen": (
            "Control: frozen RESULT-0015 / NMD-0002 coefficients reused without refit."
        ),
        "nmd0003_train_fitted_ols": (
            "Ordinary least squares on the train split (the TASK-0531 NMD-0003 global refit)."
        ),
        "nmd0003_train_fitted_wls": (
            "Weighted least squares on the train split with per-row weights from policy "
            f"'{wls_policy}' (inverse mass number, down-weighting heavy-mass leverage)."
        ),
        "nmd0003_train_fitted_ridge": (
            "Ridge-regularized liquid-drop coefficients on standardized design columns "
            f"with penalty alpha={ridge_alpha} (no intercept)."
        ),
        "nmd0003_region_stratified_diagnostic": (
            "Region-stratified diagnostic: independent ordinary least-squares coefficients "
            "fit per A region (A<=40, 41-100, 101-180, A>180) on the train split, each "
            "region scored with its own coefficients."
        ),
    }


def _assert_split_manifest_matches_dataset(
    split_manifest: dict[str, Any],
    entries: list[NuclearMassEntry],
    dataset_path: Path,
) -> None:
    if str(split_manifest.get("source_dataset")) != str(dataset_path):
        raise ValueError("NMD-0003 split manifest source_dataset does not match config dataset.")
    training_split = split_manifest.get("training_split", {})
    training_ids = {str(item) for item in training_split.get("nuclide_ids", [])}
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


def _a_region(a: int) -> str:
    if a <= 40:
        return "A<=40"
    if a <= 100:
        return "41<=A<=100"
    if a <= 180:
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
