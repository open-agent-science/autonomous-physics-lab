"""DZ10 published-equation NMD-0003 extrapolation benchmark helper.

This module implements the ten-term Duflo-Zuker DZ10 equations documented in
Mendoza-Temis, Hirsch, and Zuker, Nucl. Phys. A843:14-36 (2010),
arXiv:0912.0882. It is not the unavailable AMDC/archival Fortran code; the
occupancy convention is recorded explicitly so the run is replayable and reviewable.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from pathlib import Path
import subprocess
from typing import Any, Iterable

import numpy as np
import yaml

from physics_lab.engines.nuclear_mass_baselines import (
    SemiEmpiricalCoefficients,
    fit_semi_empirical_coefficients,
    semi_empirical_binding_energy,
)
from physics_lab.engines.nuclear_masses import NuclearMassEntry, load_nuclear_mass_dataset


ENGINE_VERSION = "nmd0003_dz10_published_equation_variant_v2"
MODEL_ID = "dz10_published_equation_variant"
SURVIVAL_MARGIN_MEV = 0.25
DOMAIN_MIN_N_OR_Z = 8

FEATURE_NAMES = (
    "m_plus_s",
    "negative_m_over_rho",
    "negative_coulomb",
    "negative_asymmetry",
    "surface_asymmetry",
    "pairing",
    "spherical_s3",
    "negative_spherical_s3_over_rho",
    "spherical_s4",
    "deformation_d4",
)

PUBLISHED_DZ10_FULL_COEFFICIENTS = {
    "m_plus_s": 17.766,
    "negative_m_over_rho": 16.314,
    "negative_coulomb": 0.707,
    "negative_asymmetry": 37.515,
    "surface_asymmetry": 53.351,
    "pairing": 6.199,
    "spherical_s3": 0.478,
    "negative_spherical_s3_over_rho": 2.183,
    "spherical_s4": 0.022,
    "deformation_d4": 41.338,
}

HO_MAX_P = 10
EI_CLOSURES = (0, 2, 8, 14, 28, 50, 82, 126, 184, 258)


@dataclass(frozen=True)
class Dz10TermBreakdown:
    """Published-equation DZ10 terms before coefficients are applied."""

    m_plus_s: float
    negative_m_over_rho: float
    negative_coulomb: float
    negative_asymmetry: float
    surface_asymmetry: float
    pairing: float
    spherical_s3: float
    negative_spherical_s3_over_rho: float
    spherical_s4: float
    deformation_d4: float
    active_sector: str
    rho: float

    def feature_row(self) -> tuple[float, ...]:
        if self.active_sector == "spherical":
            return (
                self.m_plus_s,
                self.negative_m_over_rho,
                self.negative_coulomb,
                self.negative_asymmetry,
                self.surface_asymmetry,
                self.pairing,
                self.spherical_s3,
                self.negative_spherical_s3_over_rho,
                self.spherical_s4,
                0.0,
            )
        return (
            self.m_plus_s,
            self.negative_m_over_rho,
            self.negative_coulomb,
            self.negative_asymmetry,
            self.surface_asymmetry,
            self.pairing,
            0.0,
            0.0,
            0.0,
            self.deformation_d4,
        )


def duflo_zuker_term_breakdown(
    z: int,
    n: int,
    coefficients_for_sector: dict[str, float] | None = None,
) -> Dz10TermBreakdown:
    """Return DZ10 terms for one nuclide using the documented convention.

    The macroscopic equations follow arXiv:0912.0882 Eqs. (M), (S), and
    (dz_macro). Spherical/deformed microscopic terms follow Eqs. (s3), (s4),
    and (dz_def). For ``Z >= 50`` the active sector is selected by the larger
    published-coefficient microscopic binding contribution, mirroring Eq. (dz10)
    without using any fitted holdout information.
    """
    if z < 0 or n < 0 or z + n <= 0:
        raise ValueError("Z and N must be non-negative with A > 0.")

    coefficients_for_sector = dict(
        coefficients_for_sector or PUBLISHED_DZ10_FULL_COEFFICIENTS
    )
    a = float(z + n)
    t_raw = float(n - z)
    t = abs(t_raw) / 2.0
    rho = _rho(z, n)
    n_ho = _ho_shell_occupancies(n)
    z_ho = _ho_shell_occupancies(z)
    m_sum = 0.0
    t_sum = 0.0
    for p in range(HO_MAX_P + 1):
        degeneracy = _ho_degeneracy(p)
        n_p = n_ho.get(p, 0.0)
        z_p = z_ho.get(p, 0.0)
        m_sum += (n_p + z_p) / math.sqrt(degeneracy)
        t_sum += (n_p - z_p) / math.sqrt(degeneracy)
    master_m = 0.5 * (m_sum**2 + t_sum**2) / rho
    spin_orbit_s = (_spin_orbit_s(n) + _spin_orbit_s(z)) / rho

    z_pair = float(max(z * (z - 1), 0))
    charge_radius = (a ** (1.0 / 3.0)) * (1.0 - (t / a) ** 2)
    coulomb = (z_pair + 0.76 * (z_pair ** (2.0 / 3.0))) / charge_radius
    asymmetry = (4.0 * t * (t + 1.0)) / ((a ** (2.0 / 3.0)) * rho)
    surface_asymmetry = (
        (4.0 * t * (t + 1.0)) / ((a ** (2.0 / 3.0)) * (rho**2))
        - (4.0 * t * (t - 0.5)) / (a * (rho**4))
    )
    pairing = _pairing_term(z, n, t=t, a=a, rho=rho)
    spherical_s3, spherical_s4 = _spherical_terms(z, n, rho=rho)
    deformation_d4 = _deformation_term(z, n, rho=rho)
    spherical_energy = (
        coefficients_for_sector["spherical_s3"] * spherical_s3
        + coefficients_for_sector["negative_spherical_s3_over_rho"]
        * (-spherical_s3 / rho)
        + coefficients_for_sector["spherical_s4"] * spherical_s4
    )
    deformation_energy = coefficients_for_sector["deformation_d4"] * deformation_d4
    active_sector = (
        "spherical"
        if z < 50 or spherical_energy >= deformation_energy
        else "deformed"
    )

    return Dz10TermBreakdown(
        m_plus_s=master_m + spin_orbit_s,
        negative_m_over_rho=-(master_m / rho),
        negative_coulomb=-coulomb,
        negative_asymmetry=-asymmetry,
        surface_asymmetry=surface_asymmetry,
        pairing=pairing,
        spherical_s3=spherical_s3,
        negative_spherical_s3_over_rho=-(spherical_s3 / rho),
        spherical_s4=spherical_s4,
        deformation_d4=deformation_d4,
        active_sector=active_sector,
        rho=rho,
    )


def duflo_zuker_feature_row(z: int, n: int) -> tuple[float, ...]:
    """Return the active-sector DZ10 published-equation feature row."""
    return duflo_zuker_term_breakdown(z, n).feature_row()


def duflo_zuker_design_matrix(entries: Iterable[NuclearMassEntry]) -> np.ndarray:
    """Return the TASK-0823 DZ10 published-equation design matrix."""
    return np.asarray(
        [duflo_zuker_feature_row(entry.Z, entry.N) for entry in entries],
        dtype=float,
    )


def fit_duflo_zuker_published_variant_coefficients(
    entries: Iterable[NuclearMassEntry],
) -> dict[str, float]:
    """Fit DZ10 coefficients on the committed NMD-0003 training rows only."""
    rows = [entry for entry in entries if _within_dz10_domain(entry.Z, entry.N)]
    if not rows:
        raise ValueError("No rows satisfy the DZ10 N,Z >= 8 published-fit domain.")
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
    """Predict binding energy for one nuclide from active DZ10 terms."""
    row = duflo_zuker_feature_row(z, n)
    return float(
        sum(coefficients[name] * value for name, value in zip(FEATURE_NAMES, row, strict=True))
    )


def run_nmd0003_duflo_zuker_baseline(config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run the deterministic TASK-0823 DZ10 published-equation benchmark."""
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
    all_entries = sorted(
        dataset.entries,
        key=lambda entry: (entry.A, entry.Z, entry.N, entry.nuclide_id),
    )
    fit_entries = [entry for entry in all_entries if _within_dz10_domain(entry.Z, entry.N)]
    coefficients = fit_duflo_zuker_published_variant_coefficients(fit_entries)

    inherited_coefficients = _load_frozen_coefficients(inherited_result_path)
    liquid_drop_coefficients = fit_semi_empirical_coefficients(fit_entries)
    holdout_rows = _post_ame2020_rows(holdout_path)
    dz_holdout_rows = [
        row for row in holdout_rows if _within_dz10_domain(int(row["Z"]), int(row["N"]))
    ]

    dz_surfaces = {
        "nmd0003_fit_surface": _entry_metrics(fit_entries, coefficients),
        "post_ame2020_holdout": _holdout_metrics(dz_holdout_rows, coefficients),
    }
    published_coefficient_reference = {
        "post_ame2020_holdout": _holdout_metrics(
            dz_holdout_rows,
            PUBLISHED_DZ10_FULL_COEFFICIENTS,
        )
    }
    controls = {
        "inherited_result0015_frozen": {
            "fit_policy": "frozen_RESULT_0015_coefficients",
            "post_ame2020_holdout": _holdout_metrics_semi_empirical(
                dz_holdout_rows,
                inherited_coefficients,
            ),
        },
        "nmd0003_train_fitted_liquid_drop": {
            "fit_policy": "fit_nmd0003_training_rows_only_liquid_drop_ols",
            "post_ame2020_holdout": _holdout_metrics_semi_empirical(
                dz_holdout_rows,
                liquid_drop_coefficients,
            ),
        },
        "smooth_a_quadratic_control": {
            "fit_policy": "fit_nmd0003_training_rows_only_quadratic_in_A",
            "post_ame2020_holdout": _smooth_a_control(fit_entries, dz_holdout_rows),
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
        diagnostic_outcome = "CONTROL_SURVIVING_GAIN_UNDER_REVIEWABLE_DZ10_EQUATION_VARIANT"
    elif margin_vs_best > 0.0:
        diagnostic_outcome = "POSITIVE_MARGIN_TOO_SMALL_FOR_SURVIVAL"
    else:
        diagnostic_outcome = "NO_CONTROL_SURVIVING_GAIN"
    verdict = "INCONCLUSIVE"
    routing = "SANDBOX_ONLY_DZ10_PARITY_BLOCKED_TASK_REMAINS_READY"

    return {
        "task_id": "TASK-0823",
        "agent_run_id": "AGENT-RUN-0078",
        "benchmark_id": "nmd0003-dz10-published-equation-baseline",
        "engine_version": ENGINE_VERSION,
        "model_scope": {
            "model_id": MODEL_ID,
            "published_variant": True,
            "archival_dz10_code_reproduction": False,
            "archival_code_status": (
                "AMDC dz.html endpoint cited by the paper was unreachable during "
                "this run; implementation follows the published equations and "
                "records the occupancy convention for review."
            ),
            "primary_sources": [
                "J. Duflo and A. P. Zuker, Phys. Rev. C 52, R23 (1995).",
                "J. Mendoza-Temis, J. G. Hirsch, and A. P. Zuker, Nucl. Phys. A843:14-36 (2010), arXiv:0912.0882.",
            ],
            "paper_equations": [
                "rho / Eq. (rc)",
                "master M / Eq. (M)",
                "spin-orbit S / Eq. (S)",
                "macroscopic binding / Eq. (dz_macro)",
                "spherical terms / Eqs. (s3), (s4), (dz_sph)",
                "deformed term / Eq. (dz_def)",
                "sector selection / Eq. (dz10)",
            ],
        },
        "gate_b_replay": {
            "pinned_command": (
                "python scripts/run_nmd0003_duflo_zuker_baseline.py "
                "--output-dir agent_runs/AGENT-RUN-0078 "
                "--review-path docs/reviews/nmd0003-duflo-zuker-structured-baseline.md"
            ),
            "code_reference": "physics_lab/engines/nmd0003_duflo_zuker_baseline.py::run_nmd0003_duflo_zuker_baseline",
            "engine_version": ENGINE_VERSION,
            "git_commit_at_generation": _git_commit(),
            "input_file_hashes": {
                dataset_path.as_posix(): _sha256(dataset_path),
                holdout_path.as_posix(): _sha256(holdout_path),
                inherited_result_path.as_posix(): _sha256(inherited_result_path),
            },
        },
        "input_references": {
            "training_dataset": dataset_path.as_posix(),
            "post_ame2020_holdout": holdout_path.as_posix(),
            "inherited_baseline_result": inherited_result_path.as_posix(),
        },
        "dataset_summary": {
            "nmd0003_row_count": len(all_entries),
            "dz10_fit_domain": "N >= 8 and Z >= 8, matching the paper's fit domain",
            "fit_count": len(fit_entries),
            "nmd0003_rows_outside_fit_domain": len(all_entries) - len(fit_entries),
            "post_ame2020_primary_holdout_count": len(holdout_rows),
            "post_ame2020_primary_holdout_count_in_dz10_domain": len(dz_holdout_rows),
            "post_ame2020_rows_used_for_fit": 0,
        },
        "task_completion": {
            "completes_task": False,
            "task_status_after_pr": "READY",
            "reason": (
                "The reviewable published-equation variant is useful diagnostic "
                "evidence, but it is not an archival DZ10 parity reproduction. "
                "TASK-0823 therefore remains READY for a true published-code or "
                "published-fixture parity implementation."
            ),
        },
        "published_table_reference": {
            "source": "arXiv:0912.0882 Table II, full 10-term DZ10 fit column",
            "coefficients": PUBLISHED_DZ10_FULL_COEFFICIENTS,
            "post_ame2020_holdout_metrics": published_coefficient_reference[
                "post_ame2020_holdout"
            ],
        },
        "feature_names": list(FEATURE_NAMES),
        "occupancy_convention": {
            "ho_shell_degeneracy": "D_p = (p + 1)(p + 2)",
            "ho_fill_order": "major shells filled by increasing p",
            "spin_orbit_split": (
                "within each HO major shell, j(p) capacity 2(p+1) fills before "
                "the r(p) partner capacity p(p+1)"
            ),
            "ei_closures": list(EI_CLOSURES),
            "ei_terms": (
                "spherical/deformed valence terms use the explicit EI closure "
                "interval containing each species."
            ),
        },
        "fit_policy": "ordinary_least_squares_on_committed_nmd0003_training_rows_only",
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
            "diagnostic_outcome": diagnostic_outcome,
        },
        "verdict": verdict,
        "output_routing": {
            "canonical_destination": "agent_runs/AGENT-RUN-0078/ plus docs/reviews/",
            "review_tier": "sandbox",
            "gate_a_status": "not_attempted",
            "gate_b_status": "replayable",
            "claim_impact": "no claim change",
            "knowledge_impact": "no knowledge change",
            "routing_decision": routing,
        },
        "limitations": [
            "This follows the published DZ10 equations, but it is not a parity run of the unavailable AMDC/archival code.",
            "The occupancy convention is explicit and reviewable; maintainer review is required before any canonical RESULT route.",
            "The post-AME2020 surface is retrospective time-split evidence, not a strict blind reveal.",
            "The model is fitted by ordinary least squares on committed NMD-0003 training rows in the paper's N,Z >= 8 domain.",
            "No PRED, CLAIM, KNOW, or canonical RESULT artifact is created.",
        ],
    }


def _within_dz10_domain(z: int, n: int) -> bool:
    return z >= DOMAIN_MIN_N_OR_Z and n >= DOMAIN_MIN_N_OR_Z


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
    train_design = np.asarray(
        [_smooth_a_features(entry.Z, entry.N) for entry in train_entries],
        dtype=float,
    )
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
    t_raw = float(n - z)
    return (a ** (1.0 / 3.0)) * (1.0 - 0.5 * (t_raw / a) ** 2) ** 2


def _pairing_term(z: int, n: int, *, t: float, a: float, rho: float) -> float:
    if n % 2 == 0 and z % 2 == 0:
        return (2.0 - (2.0 * t / a)) / rho
    if n % 2 == 1 and z % 2 == 1:
        return (2.0 * t) / (a * rho)
    if n > z:
        return ((1.0 - (2.0 * t / a)) / rho) if n % 2 == 0 else (1.0 / rho)
    return (1.0 / rho) if n % 2 == 0 else ((1.0 - (2.0 * t / a)) / rho)


def _ho_degeneracy(p: int) -> int:
    return (p + 1) * (p + 2)


def _ho_shell_occupancies(count: int) -> dict[int, float]:
    remaining = float(count)
    occupancies: dict[int, float] = {}
    for p in range(HO_MAX_P + 1):
        capacity = float(_ho_degeneracy(p))
        occupancy = min(max(remaining, 0.0), capacity)
        occupancies[p] = occupancy
        remaining -= occupancy
        if remaining <= 0.0:
            break
    if remaining > 0.0:
        raise ValueError(f"Nucleon count {count} exceeds HO_MAX_P={HO_MAX_P}.")
    return occupancies


def _spin_orbit_s(count: int) -> float:
    remaining = float(count)
    total = 0.0
    for p in range(HO_MAX_P + 1):
        shell_capacity = float(_ho_degeneracy(p))
        shell_occupancy = min(max(remaining, 0.0), shell_capacity)
        if shell_occupancy <= 0.0:
            break
        j_capacity = float(2 * (p + 1))
        r_capacity = float(p * (p + 1))
        j_occupancy = min(shell_occupancy, j_capacity)
        r_occupancy = min(max(shell_occupancy - j_capacity, 0.0), r_capacity)
        s_p = (p * j_occupancy - 2.0 * r_occupancy) / (2.0 * (p + 1))
        d_p = float(_ho_degeneracy(p))
        total += s_p * ((p * p + 4 * p - 5) / (math.sqrt(d_p) * (p + 2)))
        total += (
            shell_occupancy
            * s_p
            * ((p * p - 4 * p + 5) / (d_p * (p + 2)))
        )
        remaining -= shell_occupancy
    if remaining > 0.0:
        raise ValueError(f"Nucleon count {count} exceeds HO_MAX_P={HO_MAX_P}.")
    return total


def _ei_valence(count: int) -> tuple[float, float, float, int]:
    lower, upper, p_index = EI_CLOSURES[-2], EI_CLOSURES[-1], len(EI_CLOSURES) - 2
    for index, (left, right) in enumerate(zip(EI_CLOSURES, EI_CLOSURES[1:], strict=False)):
        if left <= count <= right:
            lower, upper, p_index = left, right, index
            break
    degeneracy = float(upper - lower)
    particles = float(min(max(count - lower, 0), upper - lower))
    holes = degeneracy - particles
    return particles, holes, degeneracy, max(p_index, 1)


def _spherical_terms(z: int, n: int, *, rho: float) -> tuple[float, float]:
    n_particles, n_holes, n_degeneracy, n_p = _ei_valence(n)
    z_particles, z_holes, z_degeneracy, z_p = _ei_valence(z)
    s3 = (
        (n_particles * n_holes * (n_particles - n_holes) / n_degeneracy)
        + (z_particles * z_holes * (z_particles - z_holes) / z_degeneracy)
    ) / rho
    s4 = (
        (2.0 ** (math.sqrt(float(z_p)) + math.sqrt(float(n_p))))
        * (n_particles * n_holes / n_degeneracy)
        * (z_particles * z_holes / z_degeneracy)
    ) / rho
    return s3, s4


def _deformation_term(z: int, n: int, *, rho: float) -> float:
    n_particles, n_holes, n_degeneracy, _ = _ei_valence(n)
    z_particles, z_holes, z_degeneracy, _ = _ei_valence(z)
    n_prime = n_particles - 4.0
    z_prime = z_particles - 4.0
    if n_prime <= 0.0 or z_prime <= 0.0:
        return 0.0
    n_hole_prime = n_holes + 4.0
    z_hole_prime = z_holes + 4.0
    return (
        (n_prime * n_hole_prime / (n_degeneracy ** 1.5))
        * (z_prime * z_hole_prime / (z_degeneracy ** 1.5))
    ) / rho


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            encoding="utf-8",
        )
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"
    return completed.stdout.strip()
