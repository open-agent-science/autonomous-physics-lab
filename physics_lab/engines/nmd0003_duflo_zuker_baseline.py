"""Duflo-Zuker-structured NMD-0003 extrapolation benchmark helper.

This module implements a deterministic, linear, Duflo-Zuker-structured
baseline for TASK-0823. It is intentionally conservative: the feature family
uses the published DZ10 anatomy (macroscopic liquid-drop asymptotics plus
harmonic-oscillator / extruder-intruder shell occupancy proxies), but it does
not claim to be the archival DZ10 code.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import numpy as np
import yaml

from physics_lab.engines.nuclear_mass_baselines import (
    SemiEmpiricalCoefficients,
    fit_semi_empirical_coefficients,
    semi_empirical_binding_energy,
)
from physics_lab.engines.nuclear_masses import NuclearMassEntry, load_nuclear_mass_dataset


FEATURE_NAMES = (
    "volume_a",
    "surface_a_2_3",
    "dz_asymmetry_volume",
    "dz_asymmetry_surface",
    "coulomb",
    "pairing",
    "ho_shell_master",
    "ei_shell_master",
    "ei_deformation_proxy",
    "intercept",
)

HO_CLOSURES = (0, 2, 8, 20, 40, 70, 112, 168, 240)
EI_CLOSURES = (0, 2, 8, 14, 28, 50, 82, 126, 184, 258)
SURVIVAL_MARGIN_MEV = 0.25


def duflo_zuker_feature_row(z: int, n: int) -> tuple[float, ...]:
    """Return the deterministic 10-term DZ-structured feature row."""
    a = z + n
    if a <= 0:
        raise ValueError("A must be positive")
    a_float = float(a)
    t = abs(n - z) / 2.0
    rho = _rho(z, n)
    pairing = _pairing_sign(z, n) / np.sqrt(a_float)
    ho_shell = (_shell_occupancy_term(n, HO_CLOSURES) + _shell_occupancy_term(z, HO_CLOSURES)) / rho
    ei_n = _shell_occupancy_term(n, EI_CLOSURES)
    ei_z = _shell_occupancy_term(z, EI_CLOSURES)
    ei_shell = (ei_n + ei_z) / rho
    deformation = (ei_n * ei_z) / (a_float * rho)
    return (
        a_float,
        -(a_float ** (2.0 / 3.0)),
        -(4.0 * t * (t + 1.0)) / a_float,
        (4.0 * t * (t + 1.0)) / (a_float ** (4.0 / 3.0)),
        -(z * (z - 1)) / (a_float ** (1.0 / 3.0)),
        pairing,
        ho_shell,
        ei_shell,
        deformation,
        1.0,
    )


def duflo_zuker_design_matrix(entries: Iterable[NuclearMassEntry]) -> np.ndarray:
    """Return the TASK-0823 DZ-structured design matrix."""
    return np.asarray(
        [duflo_zuker_feature_row(entry.Z, entry.N) for entry in entries],
        dtype=float,
    )


def fit_duflo_zuker_structured_coefficients(
    entries: Iterable[NuclearMassEntry],
) -> dict[str, float]:
    """Fit DZ-structured coefficients on training rows only."""
    rows = list(entries)
    design = duflo_zuker_design_matrix(rows)
    targets = np.asarray([entry.binding_energy_mev for entry in rows], dtype=float)
    solution, *_ = np.linalg.lstsq(design, targets, rcond=None)
    return {
        name: float(value)
        for name, value in zip(FEATURE_NAMES, solution, strict=True)
    }


def predict_duflo_zuker_binding_energy(
    *, z: int, n: int, coefficients: dict[str, float]
) -> float:
    """Predict binding energy for one nuclide from fitted DZ-structured terms."""
    row = duflo_zuker_feature_row(z, n)
    return float(
        sum(coefficients[name] * value for name, value in zip(FEATURE_NAMES, row, strict=True))
    )


def run_nmd0003_duflo_zuker_baseline(config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run the deterministic TASK-0823 benchmark."""
    config = dict(config or {})
    dataset_path = Path(
        config.get("dataset_path", "data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml")
    )
    holdout_path = Path(
        config.get("holdout_path", "data/nuclear_masses/post_ame2020_holdout.yaml")
    )
    inherited_result_path = Path(
        config.get("inherited_result_path", "results/EXP-0012/RUN-0001/result.yaml")
    )

    dataset = load_nuclear_mass_dataset(dataset_path)
    entries = sorted(dataset.entries, key=lambda entry: (entry.A, entry.Z, entry.N, entry.nuclide_id))
    train_entries, validation_entries = _sorted_split(entries)
    coefficients = fit_duflo_zuker_structured_coefficients(train_entries)

    inherited_coefficients = _load_frozen_coefficients(inherited_result_path)
    liquid_drop_coefficients = fit_semi_empirical_coefficients(train_entries)
    holdout_rows = _post_ame2020_rows(holdout_path)

    dz_surfaces = {
        "train": _entry_metrics(train_entries, coefficients),
        "sorted_validation_holdout": _entry_metrics(validation_entries, coefficients),
        "post_ame2020_holdout": _holdout_metrics(holdout_rows, coefficients),
    }
    controls = {
        "inherited_result0015_frozen": {
            "fit_policy": "frozen_RESULT_0015_coefficients",
            "post_ame2020_holdout": _holdout_metrics_semi_empirical(
                holdout_rows,
                inherited_coefficients,
            ),
        },
        "nmd0003_train_fitted_liquid_drop": {
            "fit_policy": "fit_train_split_only_liquid_drop_ols",
            "post_ame2020_holdout": _holdout_metrics_semi_empirical(
                holdout_rows,
                liquid_drop_coefficients,
            ),
        },
        "smooth_a_quadratic_control": {
            "fit_policy": "fit_train_split_only_quadratic_in_A",
            "post_ame2020_holdout": _smooth_a_control(train_entries, holdout_rows),
        },
    }
    best_control = min(
        (
            (control_id, float(payload["post_ame2020_holdout"]["mae_mev"]))
            for control_id, payload in controls.items()
        ),
        key=lambda item: item[1],
    )
    dz_mae = float(dz_surfaces["post_ame2020_holdout"]["mae_mev"])
    margin_vs_best = best_control[1] - dz_mae
    clears_margin = margin_vs_best >= SURVIVAL_MARGIN_MEV

    if clears_margin:
        verdict = "VALID_IN_RANGE"
        routing = "RESULT_CANDIDATE_REQUIRES_GATE_A"
    elif margin_vs_best > 0.0:
        verdict = "PARTIALLY_VALID"
        routing = "SANDBOX_ONLY_MARGIN_TOO_SMALL_FOR_GATE_A"
    else:
        verdict = "INCONCLUSIVE"
        routing = "SANDBOX_ONLY_NO_CONTROL_SURVIVING_GAIN"

    return {
        "task_id": "TASK-0823",
        "benchmark_id": "nmd0003-duflo-zuker-structured-baseline",
        "model_scope": {
            "model_id": "dz_structured_10_term_proxy",
            "not_canonical_dz10_code": True,
            "publication_blocker": (
                "The implementation uses DZ10-published term structure and shell "
                "occupancy proxies, but it is not the archival Duflo-Zuker code. "
                "Any canonical RESULT publication would need maintainer review or "
                "a direct published-code parity check."
            ),
            "primary_sources": [
                "J. Duflo and A. P. Zuker, Phys. Rev. C 52, R23 (1995).",
                "J. Mendoza-Temis, J. G. Hirsch, and A. P. Zuker, arXiv:0912.0882.",
            ],
        },
        "input_references": {
            "training_dataset": dataset_path.as_posix(),
            "post_ame2020_holdout": holdout_path.as_posix(),
            "inherited_baseline_result": inherited_result_path.as_posix(),
        },
        "dataset_summary": {
            "nmd0003_row_count": len(entries),
            "train_count": len(train_entries),
            "sorted_validation_holdout_count": len(validation_entries),
            "post_ame2020_primary_holdout_count": len(holdout_rows),
            "post_ame2020_rows_used_for_fit": 0,
        },
        "feature_names": list(FEATURE_NAMES),
        "feature_basis_note": (
            "The first six terms follow the liquid-drop / DZ asymptotic form; "
            "the remaining terms are deterministic harmonic-oscillator and "
            "extruder-intruder shell occupancy proxies plus a midshell "
            "deformation proxy."
        ),
        "fit_policy": "ordinary_least_squares_on_sorted_train_split_only",
        "coefficients": {key: round(value, 12) for key, value in coefficients.items()},
        "surfaces": dz_surfaces,
        "controls": controls,
        "best_control_on_post_ame2020_holdout": {
            "control_id": best_control[0],
            "mae_mev": round(best_control[1], 6),
        },
        "comparison": {
            "post_ame2020_mae_mev": round(dz_mae, 6),
            "margin_vs_best_control_mev": round(margin_vs_best, 6),
            "survival_margin_mev": SURVIVAL_MARGIN_MEV,
            "clears_survival_margin": clears_margin,
        },
        "verdict": verdict,
        "output_routing": {
            "canonical_destination": "agent_runs/AGENT-RUN-0078/ plus docs/reviews/",
            "review_tier": "none",
            "gate_a_status": "not_attempted",
            "gate_b_status": "not_applicable",
            "claim_impact": "no claim change",
            "knowledge_impact": "no knowledge change",
            "routing_decision": routing,
        },
        "limitations": [
            "This is a DZ-structured proxy, not an archival DZ10 reproduction.",
            "The post-AME2020 surface is retrospective time-split evidence, not a strict blind reveal.",
            "The model is fitted by ordinary least squares on the committed NMD-0003 train split only.",
            "No PRED, CLAIM, KNOW, or canonical RESULT artifact is created.",
        ],
    }


def _sorted_split(
    entries: list[NuclearMassEntry],
    *,
    validation_fraction: float = 0.3,
) -> tuple[list[NuclearMassEntry], list[NuclearMassEntry]]:
    split_index = max(1, int(round((1.0 - validation_fraction) * len(entries))))
    split_index = min(split_index, len(entries) - 1)
    return entries[:split_index], entries[split_index:]


def _entry_metrics(
    entries: list[NuclearMassEntry],
    coefficients: dict[str, float],
) -> dict[str, float | int]:
    observed = [entry.binding_energy_mev for entry in entries]
    predicted = [
        predict_duflo_zuker_binding_energy(z=entry.Z, n=entry.N, coefficients=coefficients)
        for entry in entries
    ]
    return _metrics(observed, predicted)


def _holdout_metrics(
    rows: list[dict[str, Any]],
    coefficients: dict[str, float],
) -> dict[str, float | int]:
    observed = [float(row["observed_mev"]) for row in rows]
    predicted = [
        predict_duflo_zuker_binding_energy(
            z=int(row["Z"]),
            n=int(row["N"]),
            coefficients=coefficients,
        )
        for row in rows
    ]
    return _metrics(observed, predicted)


def _holdout_metrics_semi_empirical(
    rows: list[dict[str, Any]],
    coefficients: SemiEmpiricalCoefficients,
) -> dict[str, float | int]:
    observed = [float(row["observed_mev"]) for row in rows]
    predicted = [
        semi_empirical_binding_energy(
            z=int(row["Z"]),
            n=int(row["N"]),
            coefficients=coefficients,
        )
        for row in rows
    ]
    return _metrics(observed, predicted)


def _metrics(
    observed_mev: Iterable[float],
    predicted_mev: Iterable[float],
) -> dict[str, float | int]:
    observed = np.asarray(list(observed_mev), dtype=float)
    predicted = np.asarray(list(predicted_mev), dtype=float)
    if observed.shape != predicted.shape:
        raise ValueError("observed and predicted arrays must have the same shape")
    residuals = observed - predicted
    abs_residuals = np.abs(residuals)
    return {
        "count": int(observed.size),
        "mae_mev": round(float(np.mean(abs_residuals)), 6),
        "rmse_mev": round(float(np.sqrt(np.mean(np.square(residuals)))), 6),
        "median_abs_error_mev": round(float(np.median(abs_residuals)), 6),
        "p90_abs_error_mev": round(float(np.percentile(abs_residuals, 90)), 6),
        "max_abs_error_mev": round(float(np.max(abs_residuals)), 6),
        "mean_error_mev": round(float(np.mean(residuals)), 6),
    }


def _smooth_a_control(
    train_entries: list[NuclearMassEntry],
    holdout_rows: list[dict[str, Any]],
) -> dict[str, float | int]:
    train_design = np.asarray([_smooth_a_features(entry.Z, entry.N) for entry in train_entries], dtype=float)
    train_targets = np.asarray([entry.binding_energy_mev for entry in train_entries], dtype=float)
    coefficients, *_ = np.linalg.lstsq(train_design, train_targets, rcond=None)
    observed = [float(row["observed_mev"]) for row in holdout_rows]
    predicted = [
        float(np.dot(coefficients, _smooth_a_features(int(row["Z"]), int(row["N"]))))
        for row in holdout_rows
    ]
    metrics = _metrics(observed, predicted)
    metrics["coefficient_count"] = int(coefficients.size)
    return metrics


def _smooth_a_features(z: int, n: int) -> tuple[float, ...]:
    a = float(z + n)
    asymmetry = ((n - z) ** 2) / a
    return (a, a ** (2.0 / 3.0), a ** (1.0 / 3.0), asymmetry, 1.0)


def _post_ame2020_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    rows: list[dict[str, Any]] = []
    for entry in payload["entries"]:
        if not bool(entry["included_in_time_split_holdout"]):
            continue
        rows.append(
            {
                "row_id": str(entry["row_id"]),
                "nuclide_id": str(entry["nuclide_id"]),
                "Z": int(entry["Z"]),
                "N": int(entry["N"]),
                "A": int(entry["A"]),
                "observed_mev": float(entry["new_measurement"]["value_mev"]),
                "observed_uncertainty_mev": float(entry["new_measurement"]["uncertainty_mev"]),
                "ame2020_comparison_mev": float(entry["ame2020_comparison"]["value_mev"]),
                "ame2020_was_extrapolated": bool(entry["ame2020_comparison"]["was_extrapolated"]),
            }
        )
    rows.sort(key=lambda row: (row["A"], row["Z"], row["N"], row["row_id"]))
    return rows


def _load_frozen_coefficients(path: Path) -> SemiEmpiricalCoefficients:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for score in payload.get("scores", []):
        if score.get("model_id") != "model_fitted_semi_empirical":
            continue
        coefficients = score.get("coefficients", {})
        return SemiEmpiricalCoefficients(
            volume=float(coefficients["volume"]),
            surface=float(coefficients["surface"]),
            coulomb=float(coefficients["coulomb"]),
            asymmetry=float(coefficients["asymmetry"]),
            pairing=float(coefficients["pairing"]),
        )
    raise ValueError(f"model_fitted_semi_empirical coefficients not found in {path}")


def _rho(z: int, n: int) -> float:
    a = float(z + n)
    t = float(n - z)
    return (a ** (1.0 / 3.0)) * (1.0 - 0.5 * (t / a) ** 2) ** 2


def _pairing_sign(z: int, n: int) -> int:
    if z % 2 == 0 and n % 2 == 0:
        return 1
    if z % 2 == 1 and n % 2 == 1:
        return -1
    return 0


def _shell_occupancy_term(value: int, closures: tuple[int, ...]) -> float:
    lower, upper = closures[-2], closures[-1]
    for left, right in zip(closures, closures[1:], strict=False):
        if left <= value <= right:
            lower, upper = left, right
            break
    capacity = max(1, upper - lower)
    valence = min(max(value - lower, 0), capacity)
    return float(valence * (capacity - valence)) / float(capacity)
