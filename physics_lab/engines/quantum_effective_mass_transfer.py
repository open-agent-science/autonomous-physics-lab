"""Literature-effective-mass confinement transfer for TASK-0850.

The TASK-0842 power-law coefficient and exponent are calibrated on one material
only. The coefficient is then scaled by the pre-registered reduced-mass ratio
before scoring the other material. No holdout value is used to fit or rescue the
model.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from physics_lab.engines import quantum_cross_material_transfer as baseline

REQUIRED_MARGIN_EV = baseline.REQUIRED_MARGIN_EV
SHUFFLE_SEED = 850


def load_effective_mass_inputs(path: str | Path) -> dict[str, dict[str, Any]]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if payload.get("task_id") != "TASK-0850" or payload.get("frozen_before_scoring") is not True:
        raise ValueError("Effective-mass inputs must be the pre-registered TASK-0850 contract")
    materials = payload.get("materials")
    if not isinstance(materials, dict) or set(materials) != {"InP", "ZnSe"}:
        raise ValueError("Effective-mass inputs must contain exactly InP and ZnSe")
    for material, values in materials.items():
        for field in ("electron_effective_mass", "hole_effective_mass"):
            if float(values[field]) <= 0.0:
                raise ValueError(f"{material} {field} must be positive")
        if not values.get("source", {}).get("doi"):
            raise ValueError(f"{material} effective masses require a DOI-pinned source")
    return materials


def reduced_mass(electron_mass: float, hole_mass: float) -> float:
    """Return the electron-hole reduced mass in units of free-electron mass."""
    return 1.0 / ((1.0 / electron_mass) + (1.0 / hole_mass))


def _constant_metrics(value: float, rows: list[baseline.TransferRow]) -> dict[str, float]:
    residuals = [value - row.confinement_ev for row in rows]
    return baseline._metrics(residuals)


def _model_metrics(
    model: dict[str, float], rows: list[baseline.TransferRow], sizes: list[float]
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    residuals: list[float] = []
    predictions: list[dict[str, Any]] = []
    for row, size in zip(rows, sizes, strict=True):
        prediction = baseline._predict_confinement(model, size)
        residual = prediction - row.confinement_ev
        residuals.append(residual)
        predictions.append(
            {
                "entry_id": row.entry_id,
                "material": row.material,
                "transfer_size_nm": round(size, 9),
                "observed_confinement_ev": round(row.confinement_ev, 9),
                "predicted_confinement_ev": round(prediction, 9),
                "residual_ev": round(residual, 9),
            }
        )
    return baseline._metrics(residuals), predictions


def _run_direction(
    *,
    direction_id: str,
    calibration_material: str,
    holdout_material: str,
    calibration_rows: list[baseline.TransferRow],
    holdout_rows: list[baseline.TransferRow],
    size_attr: str,
    masses: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    bulk_gap_model = baseline._fit_power_law_confinement(
        calibration_rows, size_attr=size_attr
    )
    mu_source = reduced_mass(
        float(masses[calibration_material]["electron_effective_mass"]),
        float(masses[calibration_material]["hole_effective_mass"]),
    )
    mu_target = reduced_mass(
        float(masses[holdout_material]["electron_effective_mass"]),
        float(masses[holdout_material]["hole_effective_mass"]),
    )
    scaling_factor = mu_source / mu_target
    mass_scaled_model = {
        "coefficient": bulk_gap_model["coefficient"] * scaling_factor,
        "exponent": bulk_gap_model["exponent"],
    }
    holdout_sizes = [getattr(row, size_attr) for row in holdout_rows]
    scaled_metrics, predictions = _model_metrics(
        mass_scaled_model, holdout_rows, holdout_sizes
    )
    baseline_metrics, _ = _model_metrics(
        bulk_gap_model, holdout_rows, holdout_sizes
    )

    calibration_mean = float(np.mean([row.confinement_ev for row in calibration_rows]))
    holdout_mean = float(np.mean([row.confinement_ev for row in holdout_rows]))
    shuffled_sizes = list(holdout_sizes)
    random.Random(SHUFFLE_SEED).shuffle(shuffled_sizes)
    shuffled_metrics, _ = _model_metrics(
        mass_scaled_model, holdout_rows, shuffled_sizes
    )
    controls = {
        "calibration_mean_null": {
            "description": "Calibration-material mean confinement; no holdout labels used.",
            **_constant_metrics(calibration_mean, holdout_rows),
        },
        "per_material_mean": {
            "description": "Held-out material mean confinement; size-independent upper-bound control.",
            **_constant_metrics(holdout_mean, holdout_rows),
        },
        "shuffled_size": {
            "description": "Mass-scaled model on a deterministic permutation of held-out sizes.",
            "shuffle_seed": SHUFFLE_SEED,
            **shuffled_metrics,
        },
    }
    best_control_id = min(controls, key=lambda key: controls[key]["mae_ev"])
    best_control_mae = float(controls[best_control_id]["mae_ev"])
    margin = best_control_mae - scaled_metrics["mae_ev"]
    improvement_vs_baseline = baseline_metrics["mae_ev"] - scaled_metrics["mae_ev"]
    return {
        "direction_id": direction_id,
        "calibration_material": calibration_material,
        "holdout_material": holdout_material,
        "no_holdout_fit": True,
        "literature_effective_masses_m0": {
            calibration_material: {
                "electron": masses[calibration_material]["electron_effective_mass"],
                "hole": masses[calibration_material]["hole_effective_mass"],
                "reduced": round(mu_source, 12),
            },
            holdout_material: {
                "electron": masses[holdout_material]["electron_effective_mass"],
                "hole": masses[holdout_material]["hole_effective_mass"],
                "reduced": round(mu_target, 12),
            },
        },
        "frozen_model": {
            "formula": "conf_target=(C_source*mu_source/mu_target)*d^(-n_source)",
            "source_coefficient": bulk_gap_model["coefficient"],
            "source_exponent": bulk_gap_model["exponent"],
            "reduced_mass_scaling_factor": round(scaling_factor, 12),
            "target_coefficient": round(mass_scaled_model["coefficient"], 12),
        },
        "mass_scaled_transfer": scaled_metrics,
        "bulk_gap_only_transfer": baseline_metrics,
        "mass_scaled_improvement_vs_bulk_gap_only_ev": round(improvement_vs_baseline, 9),
        "controls": controls,
        "best_control_id": best_control_id,
        "best_control_mae_ev": round(best_control_mae, 9),
        "mass_scaled_margin_vs_best_control_ev": round(margin, 9),
        "required_margin_ev": REQUIRED_MARGIN_EV,
        "clears_predeclared_margin": bool(margin >= REQUIRED_MARGIN_EV),
        "predictions": predictions,
    }


def run_effective_mass_transfer(
    *,
    inp_dataset_path: str | Path,
    znse_dataset_path: str | Path,
    effective_mass_path: str | Path,
) -> dict[str, Any]:
    """Run both transfer directions under the frozen literature-mass contract."""
    masses = load_effective_mass_inputs(effective_mass_path)
    inp_rows = baseline.load_inp_rows(inp_dataset_path)
    znse_rows = baseline.load_znse_rows(znse_dataset_path)
    framings: dict[str, Any] = {}
    for framing, size_attr in (
        ("equivalent_diameter", "equiv_diameter_nm"),
        ("characteristic_length", "size_nm"),
    ):
        framings[framing] = {
            "forward_inp_to_znse": _run_direction(
                direction_id="InP_to_ZnSe",
                calibration_material="InP",
                holdout_material="ZnSe",
                calibration_rows=inp_rows,
                holdout_rows=znse_rows,
                size_attr=size_attr,
                masses=masses,
            ),
            "reverse_znse_to_inp": _run_direction(
                direction_id="ZnSe_to_InP",
                calibration_material="ZnSe",
                holdout_material="InP",
                calibration_rows=znse_rows,
                holdout_rows=inp_rows,
                size_attr=size_attr,
                masses=masses,
            ),
        }

    primary = framings["equivalent_diameter"]
    both_clear = all(item["clears_predeclared_margin"] for item in primary.values())
    both_improve = all(
        item["mass_scaled_improvement_vs_bulk_gap_only_ev"] > 0.0
        for item in primary.values()
    )
    if both_clear:
        verdict = "TRANSFER_SUPPORTED_IN_SCOPE"
    elif both_improve:
        verdict = "INCONCLUSIVE_DIRECTION_OR_MARGIN_LIMITED"
    else:
        verdict = "MATERIAL_SPECIFIC_AFTER_EFFECTIVE_MASS_SCALING"

    return {
        "benchmark_id": "quantum-effective-mass-scaled-confinement-transfer-inp-znse",
        "task_id": "TASK-0850",
        "source_task_id": "TASK-0842",
        "primary_framing": "equivalent_diameter",
        "required_margin_ev": REQUIRED_MARGIN_EV,
        "shuffle_seed": SHUFFLE_SEED,
        "effective_mass_input_path": str(effective_mass_path),
        "effective_mass_sources": {
            material: values["source"] for material, values in masses.items()
        },
        "framings": framings,
        "both_primary_directions_clear_margin": both_clear,
        "both_primary_directions_improve_over_bulk_gap_only": both_improve,
        "scientific_verdict": verdict,
        "agent_verdict": "REVIEW_NEEDED",
        "claim_impact": "none",
    }


__all__ = ["load_effective_mass_inputs", "reduced_mass", "run_effective_mass_transfer"]
