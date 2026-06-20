"""Deterministic quantum-dot size-effect baseline benchmark."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import random
import re
from typing import Any, Callable

import numpy as np
import yaml


UNCERTAINTY_PATTERN = re.compile(r"\+/-\s*([0-9.]+)\s*nm")


@dataclass(frozen=True)
class QuantumSizeRow:
    entry_id: str
    material: str
    edge_length_nm: float
    value_ev: float
    size_sigma_nm: float


def load_direct_inp_absorption_rows(path: str | Path) -> list[QuantumSizeRow]:
    """Load the admitted QD-0003 InP absorption rows."""
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if payload.get("dataset_id") != "qd-0003-almeida-2023-inp-optical":
        raise ValueError("TASK-0225 requires the admitted QD-0003 Almeida dataset")

    rows: list[QuantumSizeRow] = []
    for entry in payload.get("entries", []):
        if entry.get("inclusion_status") != "included":
            continue
        if entry.get("material") != "InP":
            raise ValueError("TASK-0225 first baseline is restricted to InP")
        if entry.get("property_kind") != "absorption_peak_eV":
            raise ValueError("TASK-0225 must not mix property kinds")
        if entry.get("measurement_type") != "optical_absorption":
            raise ValueError("TASK-0225 requires optical-absorption rows")
        match = UNCERTAINTY_PATTERN.search(str(entry.get("notes", "")))
        if match is None:
            raise ValueError(
                f"{entry.get('entry_id')} lacks structured size uncertainty in notes"
            )
        rows.append(
            QuantumSizeRow(
                entry_id=str(entry["entry_id"]),
                material="InP",
                edge_length_nm=float(entry["edge_length_nm"]),
                value_ev=float(entry["value_eV"]),
                size_sigma_nm=float(match.group(1)),
            )
        )
    rows.sort(key=lambda row: row.edge_length_nm)
    if len(rows) != 6:
        raise ValueError(f"TASK-0225 requires exactly six admitted rows, found {len(rows)}")
    return rows


def _metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    residual = predicted - actual
    return {
        "mae_ev": round(float(np.mean(np.abs(residual))), 9),
        "rmse_ev": round(float(np.sqrt(np.mean(residual**2))), 9),
        "max_abs_residual_ev": round(float(np.max(np.abs(residual))), 9),
    }


def _linear_feature_fit(
    train_rows: list[QuantumSizeRow], power: int
) -> tuple[dict[str, float], Callable[[float], float], Callable[[float], float]]:
    sizes = np.array([row.edge_length_nm for row in train_rows], dtype=float)
    energies = np.array([row.value_ev for row in train_rows], dtype=float)
    design = np.column_stack((np.ones(len(sizes)), sizes ** (-power)))
    intercept, coefficient = np.linalg.lstsq(design, energies, rcond=None)[0]

    def predict(size_nm: float) -> float:
        return float(intercept + coefficient * size_nm ** (-power))

    def derivative(size_nm: float) -> float:
        return float(-power * coefficient * size_nm ** (-power - 1))

    return (
        {
            "intercept_ev": round(float(intercept), 12),
            "coefficient_ev_nm_power": round(float(coefficient), 12),
            "power": power,
        },
        predict,
        derivative,
    )


def _fixed_almeida() -> tuple[dict[str, float], Callable[[float], float], Callable[[float], float]]:
    intercept = 1.33
    coefficient = 9.128
    exponent = -0.684

    def predict(size_nm: float) -> float:
        size_angstrom = 10.0 * size_nm
        return intercept + coefficient * size_angstrom**exponent

    def derivative(size_nm: float) -> float:
        size_angstrom = 10.0 * size_nm
        return coefficient * exponent * size_angstrom ** (exponent - 1.0) * 10.0

    return (
        {
            "intercept_ev": intercept,
            "coefficient": coefficient,
            "exponent": exponent,
            "input_unit": "angstrom",
            "dataset_conversion": "L_A = 10 * L_nm",
        },
        predict,
        derivative,
    )


def _evaluate_model(
    *,
    model_id: str,
    formula: str,
    coefficients: dict[str, Any],
    predict: Callable[[float], float],
    derivative: Callable[[float], float],
    rows: list[QuantumSizeRow],
    holdout_id: str,
    fitted_parameters: int,
) -> dict[str, Any]:
    predictions: list[dict[str, Any]] = []
    for row in rows:
        predicted = predict(row.edge_length_nm)
        residual = predicted - row.value_ev
        predictions.append(
            {
                "entry_id": row.entry_id,
                "split": "holdout" if row.entry_id == holdout_id else "train",
                "material": row.material,
                "edge_length_nm": row.edge_length_nm,
                "size_sigma_nm": row.size_sigma_nm,
                "observed_ev": row.value_ev,
                "predicted_ev": round(predicted, 9),
                "residual_ev": round(residual, 9),
                "abs_residual_ev": round(abs(residual), 9),
                "size_sensitivity_ev": round(
                    abs(derivative(row.edge_length_nm)) * row.size_sigma_nm, 9
                ),
            }
        )
    train = [row for row in predictions if row["split"] == "train"]
    holdout = [row for row in predictions if row["split"] == "holdout"]
    train_actual = np.array([row["observed_ev"] for row in train])
    train_predicted = np.array([row["predicted_ev"] for row in train])
    holdout_actual = np.array([row["observed_ev"] for row in holdout])
    holdout_predicted = np.array([row["predicted_ev"] for row in holdout])
    return {
        "model_id": model_id,
        "formula": formula,
        "fitted_parameters": fitted_parameters,
        "coefficients": coefficients,
        "train": _metrics(train_actual, train_predicted),
        "holdout": _metrics(holdout_actual, holdout_predicted),
        "all_rows": _metrics(
            np.concatenate((train_actual, holdout_actual)),
            np.concatenate((train_predicted, holdout_predicted)),
        ),
        "predictions": predictions,
    }


def run_quantum_size_baseline(
    *,
    dataset_path: str | Path,
    holdout_id: str,
    shuffle_seed: int = 225,
    required_holdout_improvement_ev: float = 0.05,
) -> dict[str, Any]:
    """Run the frozen TASK-0225 model slate and decision rule."""
    rows = load_direct_inp_absorption_rows(dataset_path)
    train_rows = [row for row in rows if row.entry_id != holdout_id]
    if len(train_rows) != 5:
        raise ValueError("Frozen split must contain five train rows and one holdout row")
    holdout_rows = [row for row in rows if row.entry_id == holdout_id]
    if len(holdout_rows) != 1 or holdout_rows[0] != rows[-1]:
        raise ValueError("Frozen holdout must be the largest QD-0003 row")

    fixed_coefficients, fixed_predict, fixed_derivative = _fixed_almeida()
    inv_coefficients, inv_predict, inv_derivative = _linear_feature_fit(train_rows, 1)
    inv2_coefficients, inv2_predict, inv2_derivative = _linear_feature_fit(train_rows, 2)

    mean_ev = float(np.mean([row.value_ev for row in train_rows]))

    def mean_predict(_: float) -> float:
        return mean_ev

    def zero_derivative(_: float) -> float:
        return 0.0

    shuffled_sizes = [row.edge_length_nm for row in train_rows]
    random.Random(shuffle_seed).shuffle(shuffled_sizes)
    shuffled_design = np.column_stack(
        (np.ones(len(shuffled_sizes)), np.array(shuffled_sizes, dtype=float) ** -1)
    )
    train_energies = np.array([row.value_ev for row in train_rows], dtype=float)
    shuffled_intercept, shuffled_coefficient = np.linalg.lstsq(
        shuffled_design, train_energies, rcond=None
    )[0]

    def shuffled_predict(size_nm: float) -> float:
        return float(shuffled_intercept + shuffled_coefficient / size_nm)

    def shuffled_derivative(size_nm: float) -> float:
        return float(-shuffled_coefficient / size_nm**2)

    model_specs = [
        (
            "almeida_fixed_reference",
            "E = 1.33 + 9.128 * L_A^-0.684; L_A = 10 * L_nm",
            fixed_coefficients,
            fixed_predict,
            fixed_derivative,
            0,
        ),
        (
            "inverse_edge_fit",
            "E = c + a/L_nm",
            inv_coefficients,
            inv_predict,
            inv_derivative,
            2,
        ),
        (
            "inverse_square_fit",
            "E = c + a/L_nm^2",
            inv2_coefficients,
            inv2_predict,
            inv2_derivative,
            2,
        ),
        (
            "constant_train_mean",
            "E = mean(E_train)",
            {"mean_ev": round(mean_ev, 12)},
            mean_predict,
            zero_derivative,
            1,
        ),
        (
            "shuffled_size_inverse_edge",
            "E = c + a/L_nm after deterministic train-size shuffle",
            {
                "intercept_ev": round(float(shuffled_intercept), 12),
                "coefficient_ev_nm": round(float(shuffled_coefficient), 12),
                "shuffle_seed": shuffle_seed,
                "shuffled_train_sizes_nm": shuffled_sizes,
            },
            shuffled_predict,
            shuffled_derivative,
            2,
        ),
    ]
    models = [
        _evaluate_model(
            model_id=model_id,
            formula=formula,
            coefficients=coefficients,
            predict=predict,
            derivative=derivative,
            rows=rows,
            holdout_id=holdout_id,
            fitted_parameters=fitted_parameters,
        )
        for model_id, formula, coefficients, predict, derivative, fitted_parameters in model_specs
    ]
    model_by_id = {model["model_id"]: model for model in models}
    size_aware_ids = {
        "almeida_fixed_reference",
        "inverse_edge_fit",
        "inverse_square_fit",
    }
    selected = min(
        (model for model in models if model["model_id"] in size_aware_ids),
        key=lambda model: (
            model["train"]["mae_ev"],
            model["fitted_parameters"],
            model["model_id"],
        ),
    )
    null_model = model_by_id["constant_train_mean"]
    shuffled_model = model_by_id["shuffled_size_inverse_edge"]
    improvement = null_model["holdout"]["mae_ev"] - selected["holdout"]["mae_ev"]
    beats_shuffle = selected["holdout"]["mae_ev"] < shuffled_model["holdout"]["mae_ev"]
    if improvement >= required_holdout_improvement_ev and beats_shuffle:
        scientific_verdict = "VALID_IN_RANGE"
        agent_verdict = "SANDBOX_PASS"
    elif improvement > 0:
        scientific_verdict = "PARTIALLY_VALID"
        agent_verdict = "INCONCLUSIVE"
    else:
        scientific_verdict = "INVALID"
        agent_verdict = "FALSIFIED"

    selected_predictions = selected["predictions"]
    size_bins = {
        "small_lt_2nm": [row for row in selected_predictions if row["edge_length_nm"] < 2.0],
        "mid_2_to_3nm": [
            row for row in selected_predictions if 2.0 <= row["edge_length_nm"] <= 3.0
        ],
        "large_gt_3nm": [row for row in selected_predictions if row["edge_length_nm"] > 3.0],
    }
    size_bin_metrics = {
        name: {
            "row_count": len(bin_rows),
            **_metrics(
                np.array([row["observed_ev"] for row in bin_rows]),
                np.array([row["predicted_ev"] for row in bin_rows]),
            ),
        }
        for name, bin_rows in size_bins.items()
    }
    outliers = sorted(
        selected_predictions,
        key=lambda row: (-row["abs_residual_ev"], row["entry_id"]),
    )
    return {
        "benchmark_id": "quantum-size-effects-almeida-inp-baseline",
        "dataset_id": "qd-0003-almeida-2023-inp-optical",
        "property_kind": "absorption_peak_eV",
        "size_axis": "edge_length_nm",
        "row_count": len(rows),
        "train_count": len(train_rows),
        "holdout_count": len(holdout_rows),
        "holdout_entry_id": holdout_id,
        "shuffle_seed": shuffle_seed,
        "required_holdout_improvement_ev": required_holdout_improvement_ev,
        "models": models,
        "selected_model_id": selected["model_id"],
        "selected_train_mae_ev": selected["train"]["mae_ev"],
        "selected_holdout_mae_ev": selected["holdout"]["mae_ev"],
        "constant_null_holdout_mae_ev": null_model["holdout"]["mae_ev"],
        "shuffled_control_holdout_mae_ev": shuffled_model["holdout"]["mae_ev"],
        "holdout_improvement_vs_null_ev": round(improvement, 9),
        "beats_shuffled_control": beats_shuffle,
        "size_bin_metrics": size_bin_metrics,
        "outliers": outliers,
        "scientific_verdict": scientific_verdict,
        "agent_verdict": agent_verdict,
    }


__all__ = ["QuantumSizeRow", "load_direct_inp_absorption_rows", "run_quantum_size_baseline"]
