"""Cross-material quantum-dot size-confinement transfer benchmark (TASK-0842).

This engine runs a strict cross-material transfer test for the Quantum Size
Effects campaign. A size-confinement model is calibrated on one material's
direct-size rows, frozen, and used to predict a held-out *second* material's
direct-size rows without any refit on the holdout.

Design (frozen before any holdout error was inspected):

- The residual axis is the SIZE-CONFINEMENT term ``conf = E1s - E_bulk`` in eV,
  not the absolute 1S energy. The bulk gap ``E_bulk`` is an explicit per-material
  INPUT (cited literature values), never fitted to a holdout. This removes the
  trivial bulk-gap offset so the transfer tests the *size scaling*, not the
  material's band edge.
- The confinement form is a physically-motivated power law
  ``conf = C * d^(-n)`` (particle-in-a-box-like confinement; ideal n=2, but the
  exponent is fitted on the calibration material because Coulomb and finite-
  barrier corrections soften it). Both ``C`` and ``n`` are frozen from the
  calibration material and applied to the holdout material with no refit.
- The two committed datasets report different size axes: InP (qd-0003) is a
  tetrahedral TEM ``edge_length_nm``; ZnSe (qd-0004) is a spherical SAXS
  ``diameter_nm``. To compare confinement on a physically-comparable axis the
  primary framing converts the InP tetrahedral edge to an EQUIVALENT SPHERICAL
  DIAMETER (regular-tetrahedron volume -> equal-volume sphere). A linear size-
  axis rescale leaves the fitted exponent ``n`` and the InP train residuals
  invariant; it only repositions the InP confinement curve onto the shared
  diameter axis. A ``characteristic_length`` sensitivity framing (each material's
  reported size axis used verbatim, no morphology conversion) is also computed
  and reported.

Controls on the held-out material (controls-first, predeclared margin):

- ``per_material_mean`` (null): predict the held-out material's own mean
  confinement, independent of size. This is the honest no-size baseline.
- ``shuffled_size``: deterministically permute the held-out sizes before
  applying the frozen transferred model, breaking the size-energy pairing.

The predeclared survival rule (frozen before reveal): the transferred model
clears the controls only if its holdout confinement MAE beats the BEST (lowest
MAE) control by at least ``required_margin_ev`` eV. The margin is fixed at
0.05 eV, matching the campaign baseline convention. If the transferred model
does not clear the margin, the engine records the honest material-specificity
negative; it does NOT refit, add parameters, or fall back to absolute-energy
fitting.

The engine is deterministic: re-running with identical inputs yields identical
metrics.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import random
from typing import Any

import numpy as np
import yaml

# Predeclared, frozen survival margin (eV) of the transferred model over the
# best control on the held-out material. Matches the TASK-0225 baseline
# convention. Frozen before any holdout confinement error was inspected.
REQUIRED_MARGIN_EV = 0.05

# Deterministic permutation seed for the shuffled-size control.
SHUFFLE_SEED = 842

# Explicit per-material bulk band gaps (eV), literature inputs. NOT fitted.
# - InP: 1.34 eV room-temperature bulk gap (the value cited by the Almeida 2023
#   source context and qd-0004 planning context; standard InP Eg(300 K) ~1.344 eV,
#   Madelung, Semiconductors: Data Handbook, 3rd ed.).
# - ZnSe: 2.70 eV room-temperature bulk gap (the value reported by the Toufanian
#   2021 ZnSe source; standard ZnSe Eg(300 K) ~2.7 eV, Madelung).
BULK_GAP_EV: dict[str, float] = {
    "InP": 1.34,
    "ZnSe": 2.70,
}

# Equal-volume sphere diameter for a regular tetrahedron of edge ``a``:
#   V_tet = a**3 / (6*sqrt(2)); V_sphere = (pi/6) * d**3  =>  d = a * (1/(pi*sqrt(2)))**(1/3)
TETRA_EDGE_TO_EQUIV_DIAMETER = (1.0 / (math.pi * math.sqrt(2.0))) ** (1.0 / 3.0)


@dataclass(frozen=True)
class TransferRow:
    """One direct-size quantum-dot row used in the transfer judge."""

    entry_id: str
    material: str
    size_axis: str
    size_nm: float
    equiv_diameter_nm: float
    value_ev: float
    bulk_gap_ev: float

    @property
    def confinement_ev(self) -> float:
        """Size-confinement term ``E1s - E_bulk`` (eV)."""
        return self.value_ev - self.bulk_gap_ev


def _equivalent_diameter_nm(size_axis: str, size_nm: float, morphology: str) -> float:
    """Map a reported size to an equivalent spherical diameter (nm)."""
    if size_axis == "diameter_nm":
        return float(size_nm)
    if size_axis == "edge_length_nm" and morphology == "tetrahedral":
        return float(size_nm) * TETRA_EDGE_TO_EQUIV_DIAMETER
    raise ValueError(
        f"Unsupported (size_axis, morphology) for equivalent diameter: "
        f"({size_axis!r}, {morphology!r})"
    )


def _load_direct_rows(
    path: str | Path,
    *,
    expected_dataset_id: str,
    expected_material: str,
    size_axis: str,
) -> list[TransferRow]:
    """Load admitted direct-size absorption rows for one material."""
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if payload.get("dataset_id") != expected_dataset_id:
        raise ValueError(
            f"Expected dataset {expected_dataset_id!r}, got {payload.get('dataset_id')!r}"
        )
    bulk_gap = BULK_GAP_EV[expected_material]
    rows: list[TransferRow] = []
    for entry in payload.get("entries", []):
        if entry.get("inclusion_status") != "included":
            continue
        if entry.get("material") != expected_material:
            raise ValueError(
                f"{expected_dataset_id} must contain only {expected_material} rows"
            )
        if entry.get("property_kind") != "absorption_peak_eV":
            raise ValueError("Transfer judge must not mix property kinds")
        if entry.get("measurement_type") != "optical_absorption":
            raise ValueError("Transfer judge requires optical-absorption rows")
        if size_axis not in entry:
            raise ValueError(f"{entry.get('entry_id')} lacks size axis {size_axis!r}")
        size_nm = float(entry[size_axis])
        equiv = _equivalent_diameter_nm(
            size_axis, size_nm, str(entry.get("morphology", ""))
        )
        rows.append(
            TransferRow(
                entry_id=str(entry["entry_id"]),
                material=expected_material,
                size_axis=size_axis,
                size_nm=size_nm,
                equiv_diameter_nm=round(equiv, 9),
                value_ev=float(entry["value_eV"]),
                bulk_gap_ev=bulk_gap,
            )
        )
    rows.sort(key=lambda row: row.equiv_diameter_nm)
    if len(rows) < 6:
        raise ValueError(
            f"{expected_dataset_id} must provide at least six direct rows, found {len(rows)}"
        )
    return rows


def load_inp_rows(path: str | Path) -> list[TransferRow]:
    """Load the admitted six direct InP (qd-0003, tetrahedral TEM) rows."""
    return _load_direct_rows(
        path,
        expected_dataset_id="qd-0003-almeida-2023-inp-optical",
        expected_material="InP",
        size_axis="edge_length_nm",
    )


def load_znse_rows(path: str | Path) -> list[TransferRow]:
    """Load the admitted ten direct ZnSe (qd-0004, spherical SAXS) rows."""
    return _load_direct_rows(
        path,
        expected_dataset_id="qd-0004-toufanian-2021-znse-absorption",
        expected_material="ZnSe",
        size_axis="diameter_nm",
    )


def _fit_power_law_confinement(
    rows: list[TransferRow], *, size_attr: str
) -> dict[str, float]:
    """Fit ``conf = C * d^(-n)`` by ordinary least squares in log-log space.

    The calibration uses the confinement term (``E1s - E_bulk``) so the bulk-gap
    offset is removed before fitting. Both ``C`` and ``n`` come from the
    calibration material only.
    """
    sizes = np.array([getattr(row, size_attr) for row in rows], dtype=float)
    conf = np.array([row.confinement_ev for row in rows], dtype=float)
    if np.any(conf <= 0.0):
        raise ValueError(
            "Confinement term must be positive for all calibration rows "
            "(E1s must exceed the bulk gap)"
        )
    design = np.column_stack((np.ones(len(sizes)), np.log(sizes)))
    intercept, slope = np.linalg.lstsq(design, np.log(conf), rcond=None)[0]
    coefficient = float(math.exp(intercept))
    exponent = float(-slope)
    return {"coefficient": round(coefficient, 12), "exponent": round(exponent, 12)}


def _predict_confinement(model: dict[str, float], size_nm: float) -> float:
    return float(model["coefficient"] * size_nm ** (-model["exponent"]))


def _confinement_mae(
    model: dict[str, float], rows: list[TransferRow], sizes_nm: list[float]
) -> float:
    residuals = [
        _predict_confinement(model, size) - row.confinement_ev
        for row, size in zip(rows, sizes_nm, strict=True)
    ]
    return float(np.mean(np.abs(residuals)))


def _metrics(residuals: list[float]) -> dict[str, float]:
    arr = np.array(residuals, dtype=float)
    return {
        "mae_ev": round(float(np.mean(np.abs(arr))), 9),
        "rmse_ev": round(float(np.sqrt(np.mean(arr**2))), 9),
        "max_abs_residual_ev": round(float(np.max(np.abs(arr))), 9),
    }


def _direction_predictions(
    *,
    model: dict[str, float],
    calib_rows: list[TransferRow],
    holdout_rows: list[TransferRow],
    size_attr: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Apply the frozen confinement model to the held-out material.

    Returns per-row predictions plus the transferred-model + control metrics on
    the held-out material's confinement axis.
    """
    holdout_sizes = [getattr(row, size_attr) for row in holdout_rows]

    transferred_predictions: list[dict[str, Any]] = []
    transferred_residuals: list[float] = []
    for row, size in zip(holdout_rows, holdout_sizes, strict=True):
        pred_conf = _predict_confinement(model, size)
        residual = pred_conf - row.confinement_ev
        transferred_residuals.append(residual)
        transferred_predictions.append(
            {
                "entry_id": row.entry_id,
                "material": row.material,
                "size_nm": row.size_nm,
                "equiv_diameter_nm": row.equiv_diameter_nm,
                "transfer_size_nm": round(size, 9),
                "bulk_gap_ev": row.bulk_gap_ev,
                "observed_e1s_ev": row.value_ev,
                "observed_confinement_ev": round(row.confinement_ev, 9),
                "predicted_confinement_ev": round(pred_conf, 9),
                "predicted_e1s_ev": round(pred_conf + row.bulk_gap_ev, 9),
                "confinement_residual_ev": round(residual, 9),
                "abs_confinement_residual_ev": round(abs(residual), 9),
            }
        )

    # Control 1: per-material mean confinement (null, size-independent).
    holdout_mean_conf = float(np.mean([row.confinement_ev for row in holdout_rows]))
    mean_residuals = [holdout_mean_conf - row.confinement_ev for row in holdout_rows]

    # Control 2: shuffled-size. Deterministically permute the held-out sizes,
    # then apply the frozen transferred model. Breaks the size-energy pairing.
    shuffled_sizes = list(holdout_sizes)
    random.Random(SHUFFLE_SEED).shuffle(shuffled_sizes)
    shuffled_residuals = [
        _predict_confinement(model, size) - row.confinement_ev
        for row, size in zip(holdout_rows, shuffled_sizes, strict=True)
    ]

    controls = {
        "per_material_mean": {
            "description": "Predict the held-out material's own mean confinement (size-independent null).",
            "mean_confinement_ev": round(holdout_mean_conf, 9),
            **_metrics(mean_residuals),
        },
        "shuffled_size": {
            "description": "Frozen transferred model applied to a deterministically permuted held-out size axis.",
            "shuffle_seed": SHUFFLE_SEED,
            "shuffled_sizes_nm": [round(s, 9) for s in shuffled_sizes],
            **_metrics(shuffled_residuals),
        },
    }
    transferred_metrics = _metrics(transferred_residuals)

    best_control_id = min(controls, key=lambda key: controls[key]["mae_ev"])
    best_control_mae = controls[best_control_id]["mae_ev"]
    margin = best_control_mae - transferred_metrics["mae_ev"]
    clears_margin = margin >= REQUIRED_MARGIN_EV

    summary = {
        "transferred": transferred_metrics,
        "controls": controls,
        "best_control_id": best_control_id,
        "best_control_mae_ev": round(best_control_mae, 9),
        "transfer_margin_vs_best_control_ev": round(margin, 9),
        "required_margin_ev": REQUIRED_MARGIN_EV,
        "clears_predeclared_margin": clears_margin,
        "predictions": transferred_predictions,
    }
    return transferred_predictions, summary


def _run_direction(
    *,
    direction_id: str,
    calib_material: str,
    holdout_material: str,
    calib_rows: list[TransferRow],
    holdout_rows: list[TransferRow],
    size_attr: str,
) -> dict[str, Any]:
    """Calibrate on ``calib_rows``, freeze, predict ``holdout_rows``."""
    model = _fit_power_law_confinement(calib_rows, size_attr=size_attr)
    calib_sizes = [getattr(row, size_attr) for row in calib_rows]
    calib_train_mae = _confinement_mae(model, calib_rows, calib_sizes)
    _, transfer = _direction_predictions(
        model=model,
        calib_rows=calib_rows,
        holdout_rows=holdout_rows,
        size_attr=size_attr,
    )
    return {
        "direction_id": direction_id,
        "calibration_material": calib_material,
        "holdout_material": holdout_material,
        "frozen_model": {
            "formula": "conf = C * d^(-n); conf = E1s - E_bulk",
            "coefficient_C": model["coefficient"],
            "exponent_n": model["exponent"],
            "calibration_train_confinement_mae_ev": round(calib_train_mae, 9),
        },
        "transfer": transfer,
    }


def _verdict(primary_forward: dict[str, Any]) -> tuple[str, str]:
    """Map the primary forward (InP->ZnSe, equivalent-diameter) transfer outcome.

    The campaign-honest outcome space:
    - clears the predeclared margin over the best control -> bounded evidence of
      partial confinement universality (positive transfer);
    - beats the best control but not by the margin -> partially valid;
    - does not beat the best control -> material-specific (honest negative).
    """
    transfer = primary_forward["transfer"]
    margin = transfer["transfer_margin_vs_best_control_ev"]
    if transfer["clears_predeclared_margin"]:
        return "PARTIALLY_VALID", "SANDBOX_PASS"
    if margin > 0.0:
        return "INCONCLUSIVE", "REVIEW_NEEDED"
    return "INVALID", "FALSIFIED"


def run_cross_material_transfer(
    *,
    inp_dataset_path: str | Path,
    znse_dataset_path: str | Path,
    run_reverse: bool = True,
) -> dict[str, Any]:
    """Run the frozen InP<->ZnSe cross-material confinement transfer benchmark.

    Primary judge: forward InP->ZnSe on the equivalent-diameter axis. The
    characteristic-length framing and the reverse direction (when
    ``run_reverse``) are reported for transparency and symmetry but do not change
    the primary verdict.
    """
    inp_rows = load_inp_rows(inp_dataset_path)
    znse_rows = load_znse_rows(znse_dataset_path)

    framings: dict[str, dict[str, Any]] = {}
    for framing_id, size_attr in (
        ("equivalent_diameter", "equiv_diameter_nm"),
        ("characteristic_length", "size_nm"),
    ):
        forward = _run_direction(
            direction_id="InP_to_ZnSe",
            calib_material="InP",
            holdout_material="ZnSe",
            calib_rows=inp_rows,
            holdout_rows=znse_rows,
            size_attr=size_attr,
        )
        directions: dict[str, Any] = {"forward_inp_to_znse": forward}
        if run_reverse:
            directions["reverse_znse_to_inp"] = _run_direction(
                direction_id="ZnSe_to_InP",
                calib_material="ZnSe",
                holdout_material="InP",
                calib_rows=znse_rows,
                holdout_rows=inp_rows,
                size_attr=size_attr,
            )
        framings[framing_id] = directions

    primary_forward = framings["equivalent_diameter"]["forward_inp_to_znse"]
    scientific_verdict, agent_verdict = _verdict(primary_forward)

    return {
        "benchmark_id": "quantum-cross-material-confinement-transfer-inp-znse",
        "campaign_profile_id": "quantum-size-effects",
        "task_id": "TASK-0842",
        "property_kind": "absorption_peak_eV",
        "residual_axis": "confinement_ev (E1s - E_bulk)",
        "confinement_form": "conf = C * d^(-n)",
        "bulk_gap_ev": dict(BULK_GAP_EV),
        "bulk_gap_source": {
            "InP": "room-temperature bulk gap cited in the qd-0004 planning context; standard InP Eg(300 K) ~1.344 eV.",
            "ZnSe": "room-temperature bulk gap reported by the Toufanian 2021 ZnSe source; standard ZnSe Eg(300 K) ~2.7 eV.",
        },
        "tetra_edge_to_equiv_diameter_factor": round(TETRA_EDGE_TO_EQUIV_DIAMETER, 9),
        "inp_row_count": len(inp_rows),
        "znse_row_count": len(znse_rows),
        "primary_framing": "equivalent_diameter",
        "primary_direction": "forward_inp_to_znse",
        "required_margin_ev": REQUIRED_MARGIN_EV,
        "shuffle_seed": SHUFFLE_SEED,
        "framings": framings,
        "primary_transfer_mae_ev": primary_forward["transfer"]["transferred"]["mae_ev"],
        "primary_best_control_id": primary_forward["transfer"]["best_control_id"],
        "primary_best_control_mae_ev": primary_forward["transfer"]["best_control_mae_ev"],
        "primary_transfer_margin_vs_best_control_ev": primary_forward["transfer"][
            "transfer_margin_vs_best_control_ev"
        ],
        "primary_clears_predeclared_margin": primary_forward["transfer"][
            "clears_predeclared_margin"
        ],
        "scientific_verdict": scientific_verdict,
        "agent_verdict": agent_verdict,
    }


__all__ = [
    "TransferRow",
    "BULK_GAP_EV",
    "REQUIRED_MARGIN_EV",
    "load_inp_rows",
    "load_znse_rows",
    "run_cross_material_transfer",
]
