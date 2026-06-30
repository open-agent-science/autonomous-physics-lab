"""No-peek NMD-0003 GP uncertainty-calibration metric audit (TASK-0899).

This module runs a *no-peek* calibration audit of the merged NMD-0003 residual
Gaussian-process (GP) predictive uncertainty (``physics_lab/engines/nmd0003_residual_gp.py``).
It does **not** re-fit or modify the GP. It freezes a calibration config using
**train / leave-one-out (LOO) diagnostics only**, then scores the already
recorded post-AME2020 holdout *after* the config is frozen.

The route families are fixed by the merged TASK-0865 preflight
(``docs/reviews/nmd0003-gp-no-peek-uncertainty-route-preflight.md``):

1. ``global_robust_tail`` -- a single train-only Student-t calibration on the
   LOO standardized-residual distribution. The Student-t degrees of freedom
   ``nu`` are chosen by matching the LOO absolute-standardized ``p95/p68`` ratio
   to the Student-t ratio (a tail-shape match), and the scale is anchored so the
   nominal 1-sigma multiplier equals the LOO 68.2689 percentile.
2. ``region_quantile_min_count`` -- per-region LOO absolute-standardized
   quantile calibration over the predeclared ``a_band`` mass-number regions,
   applied only for regions whose LOO count meets a predeclared minimum; sparse
   regions fall back to the ``global_robust_tail`` multipliers.
3. ``conformal_global`` -- a global train-only split-conformal baseline using the
   LOO absolute-standardized empirical 68.2689 / 95.4500 percentiles directly as
   the 1-sigma / 2-sigma interval multipliers.

**No-peek discipline.** Every calibration parameter (Student-t ``nu``/scale,
region labels, region quantiles, minimum region count, fallback rule, and the
predeclared interval-width inflation limits and coverage targets) is computed
from the training-split LOO diagnostics *before* the holdout is scored. The
post-AME2020 holdout is read only to *evaluate* the frozen config. The LOO
predictive mean/variance use the exact closed-form GP LOO identities
(Rasmussen & Williams, Eq. 5.10-5.12) on the cached training kernel, so the
diagnostics are deterministic and reproduce the values recorded in the merged
TASK-0844 adjudication note exactly.

**Scope.** This is a calibration audit only. It creates no ``PRED``, ``RESULT``,
``CLAIM``, or ``KNOW`` artifact, does not modify ``RESULT-0025``, does not inspect
future reveal targets, and does not unblock the TASK-0827 prediction freeze. If
the predeclared success conditions do not pass, the audit is preserved as an
honest negative/blocker memory and TASK-0827 stays blocked.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import yaml
from scipy.stats import t as student_t

from physics_lab.engines.nmd0003_residual_gp import (
    DEFAULT_DATASET_PATH,
    DEFAULT_GATE_PATH,
    DEFAULT_HOLDOUT_PATH,
    GPFit,
    _frozen_baseline_coefficients,
    _holdout_arrays,
    _training_residuals,
    fit_residual_gp,
)
from physics_lab.engines.nuclear_mass_baselines import MAGIC_NUMBERS
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset
from physics_lab.registry.post_ame2020_holdout import load_post_ame2020_holdout_dataset

TASK_ID = "TASK-0899"
BENCHMARK_ID = "nmd0003-gp-uncertainty-calibration-audit"
ENGINE_VERSION = "0.1.0"
SOURCE_TASK_ID = "TASK-0824"
SOURCE_AGENT_RUN_ID = "AGENT-RUN-0080"
ROUTE_PREFLIGHT_TASK_ID = "TASK-0865"
PREDICTION_FREEZE_TASK_ID = "TASK-0827"

# Jitter used by the merged GP engine; mirrored here so the LOO kernel matches.
_JITTER = 1e-8

# --------------------------------------------------------------------------- #
# Predeclared region label definitions (frozen; identical to the TASK-0844
# adjudication note). The neutron-excess band uses eta = (N - Z) / A.
# --------------------------------------------------------------------------- #

# Nominal Gaussian central-interval coverages.
_NOMINAL_1SIGMA = 0.682689
_NOMINAL_2SIGMA = 0.954500

# Percentile points (in percent) used for the LOO quantile/conformal rules. These
# match the nominal central coverages so a quantile multiplier of q means "the
# train-only interval that empirically covered the nominal fraction of LOO points".
_P1SIGMA_PCT = 68.2689
_P2SIGMA_PCT = 95.4500


def _a_band(mass_number: float) -> str:
    if mass_number < 60:
        return "light_A_lt_60"
    if mass_number < 140:
        return "medium_60_le_A_lt_140"
    return "heavy_A_ge_140"


_A_BAND_REGIONS = ("light_A_lt_60", "medium_60_le_A_lt_140", "heavy_A_ge_140")


def _nearest_magic_distance(value: float) -> int:
    return int(min(abs(int(value) - magic) for magic in MAGIC_NUMBERS))


def _magic_band(z: float, n: float) -> str:
    if _nearest_magic_distance(z) <= 2 or _nearest_magic_distance(n) <= 2:
        return "near_magic_within_2"
    return "not_near_magic"


def _neutron_excess_band(z: float, n: float, mass_number: float) -> str:
    eta = (n - z) / mass_number
    if eta < 0.15:
        return "low_eta_lt_0_15"
    if eta < 0.25:
        return "mid_0_15_le_eta_lt_0_25"
    return "high_eta_ge_0_25"


# --------------------------------------------------------------------------- #
# Predeclared FROZEN audit policy (set before any holdout scoring).
# --------------------------------------------------------------------------- #

# Minimum LOO count for a region-quantile stratum to use its own calibration;
# otherwise the region falls back to the global robust-tail multipliers. Fixed
# from the route preflight requirement for predeclared minimum counts.
REGION_MIN_LOO_COUNT = 40

# Region partition used by the region-quantile family. ``a_band`` is the
# predeclared partition (predeclared in the preflight required-inputs list).
REGION_PARTITION = "a_band"

# Student-t nu search grid for the global robust-tail family.
_NU_GRID = tuple(range(2, 41))

# ----- Predeclared success conditions (fixed BEFORE holdout scoring) -------- #
# Central calibration: empirical 1-sigma and 2-sigma coverage must both fall
# within these absolute tolerances of nominal for the route to "pass centrally".
SUCCESS_COVERAGE_1SIGMA_TOL = 0.05
SUCCESS_COVERAGE_2SIGMA_TOL = 0.03
# Tail control: the post-calibration RMS standardized residual must fall in this
# band (a well-calibrated envelope sits near 1.0). The uncalibrated holdout RMS
# standardized residual is 2.826769, so this is a genuine tail-control target.
SUCCESS_RMS_Z_LOW = 0.85
SUCCESS_RMS_Z_HIGH = 1.20
# Sharpness: the median and p90 predictive-interval width inflation (calibrated
# 1-sigma half-width relative to the raw GP 1-sigma) must not exceed this factor.
# An inflation above this makes the interval operationally useless for PRED
# semantics, which is a predeclared STOP condition in the route preflight.
SUCCESS_MAX_MEDIAN_WIDTH_INFLATION = 3.0
SUCCESS_MAX_P90_WIDTH_INFLATION = 4.0

PREDECLARED_SUCCESS_CONDITIONS = {
    "no_peek": (
        "All route parameters (Student-t nu/scale, region labels, region "
        "quantiles, minimum region LOO count, fallback rule, width-inflation "
        "limits, coverage targets) are frozen from training/LOO diagnostics "
        "before the post-AME2020 holdout is scored."
    ),
    "central_calibration": (
        f"abs(empirical_1sigma_coverage - {_NOMINAL_1SIGMA}) <= "
        f"{SUCCESS_COVERAGE_1SIGMA_TOL} AND abs(empirical_2sigma_coverage - "
        f"{_NOMINAL_2SIGMA}) <= {SUCCESS_COVERAGE_2SIGMA_TOL}."
    ),
    "tail_control": (
        f"{SUCCESS_RMS_Z_LOW} <= post_calibration_rms_standardized_residual <= "
        f"{SUCCESS_RMS_Z_HIGH} (uncalibrated holdout is 2.826769)."
    ),
    "sharpness": (
        f"median interval-width inflation <= {SUCCESS_MAX_MEDIAN_WIDTH_INFLATION} "
        f"AND p90 interval-width inflation <= {SUCCESS_MAX_P90_WIDTH_INFLATION}."
    ),
    "coverage_surface": (
        "Any abstained/fallback region is reported explicitly; no holdout target "
        "is silently dropped."
    ),
    "scope": (
        "Output remains a calibration audit; no PRED/RESULT/CLAIM/KNOW artifact "
        "is created and TASK-0827 stays blocked unless every condition passes."
    ),
}

# Named stop conditions mirrored from the route preflight; surfaced when tripped.
_STOP_CONDITIONS = {
    "needs_holdout_to_select_parameters": (
        "A route parameter would require post-AME2020 holdout values to choose "
        "regions, thresholds, exclusions, or tail parameters."
    ),
    "sparse_region_without_fallback": (
        "A region-stratified bin is too sparse for a stable LOO quantile and no "
        "global fallback is predeclared."
    ),
    "tail_fix_overcovers_center": (
        "A route improves the tail only by making central coverage more "
        "overcovered than the uncalibrated blocker."
    ),
    "excludes_future_targets": (
        "A route excludes future targets based on a known/suspected revealed error."
    ),
    "interval_width_explodes": (
        "Interval widths inflate beyond the predeclared sharpness limit, so the "
        "output is no longer useful for PRED uncertainty semantics."
    ),
    "not_reproducible_from_committed_inputs": (
        "The calibrated route cannot be reproduced from committed inputs without "
        "a live external fetch."
    ),
}


# --------------------------------------------------------------------------- #
# Train-only leave-one-out diagnostics (closed-form GP LOO).
# --------------------------------------------------------------------------- #


def _loo_diagnostics(
    fit: GPFit, residual_train: np.ndarray
) -> dict[str, np.ndarray]:
    """Closed-form GP leave-one-out predictive mean/variance on the training set.

    Uses the standard exact-GP LOO identities (Rasmussen & Williams, Eq. 5.10-
    5.12) on the cached training kernel:

    * ``mu_i - y_i = [K^{-1} y_centered]_i / [K^{-1}]_ii``
    * ``var_i = 1 / [K^{-1}]_ii``

    so the LOO-corrected residual is ``y_i - mu_i`` and the LOO standardized
    residual is ``(y_i - mu_i) / sqrt(var_i)``. No holdout information is used.
    """
    features = fit.train_features
    n = features.shape[0]
    sq = (
        np.sum(features**2, axis=1)[:, None]
        + np.sum(features**2, axis=1)[None, :]
        - 2.0 * features @ features.T
    )
    sq = np.maximum(sq, 0.0)
    kernel = (fit.sigma_f**2) * np.exp(-0.5 * sq / (fit.length_scale**2))
    kernel[np.diag_indices(n)] += fit.sigma_n**2 + _JITTER
    kernel_inv = np.linalg.inv(kernel)
    diag = np.diag(kernel_inv)
    y_centered = residual_train - fit.target_mean
    alpha = kernel_inv @ y_centered
    loo_mean_minus_y = alpha / diag
    loo_variance = 1.0 / diag
    loo_sigma = np.sqrt(loo_variance)
    loo_corrected_residual = -loo_mean_minus_y
    loo_standardized = loo_corrected_residual / loo_sigma
    return {
        "loo_sigma": loo_sigma,
        "loo_corrected_residual": loo_corrected_residual,
        "loo_standardized": loo_standardized,
    }


def _abs_quantile(values: np.ndarray, percent: float) -> float:
    return float(np.percentile(np.abs(values), percent))


def _standardized_summary(standardized: np.ndarray) -> dict[str, float | int]:
    abs_std = np.abs(standardized)
    return {
        "count": int(standardized.size),
        "rms_standardized_residual": round(float(np.sqrt(np.mean(standardized**2))), 6),
        "abs_p68": round(_abs_quantile(standardized, _P1SIGMA_PCT), 6),
        "abs_p95": round(_abs_quantile(standardized, _P2SIGMA_PCT), 6),
        "abs_p99": round(_abs_quantile(standardized, 99.0), 6),
        "abs_max": round(float(np.max(abs_std)), 6),
        "fraction_beyond_2sigma": round(float(np.mean(abs_std > 2.0)), 6),
        "fraction_beyond_3sigma": round(float(np.mean(abs_std > 3.0)), 6),
    }


# --------------------------------------------------------------------------- #
# Frozen config construction (LOO only).
# --------------------------------------------------------------------------- #


def _freeze_global_robust_tail(loo_standardized: np.ndarray) -> dict[str, Any]:
    """Student-t calibration frozen from the LOO standardized residuals only."""
    q68 = _abs_quantile(loo_standardized, _P1SIGMA_PCT)
    q95 = _abs_quantile(loo_standardized, _P2SIGMA_PCT)
    emp_ratio = q95 / q68

    def t_ratio(nu: int) -> float:
        return float(
            student_t.ppf(0.9772499, nu) / student_t.ppf(0.8413447, nu)
        )

    nu_star = min(_NU_GRID, key=lambda nu: abs(t_ratio(nu) - emp_ratio))
    # Anchor the scale so the nominal 1-sigma multiplier equals the LOO p68.
    scale = q68 / float(student_t.ppf(0.8413447, nu_star))
    multiplier_1sigma = scale * float(student_t.ppf(0.8413447, nu_star))
    multiplier_2sigma = scale * float(student_t.ppf(0.9772499, nu_star))
    return {
        "family": "global_robust_tail",
        "method": "student_t_loo_tail_shape_match",
        "loo_abs_p68": round(q68, 6),
        "loo_abs_p95": round(q95, 6),
        "loo_abs_p95_over_p68_ratio": round(emp_ratio, 6),
        "student_t_nu": int(nu_star),
        "scale": round(scale, 6),
        "interval_multiplier_1sigma": round(multiplier_1sigma, 6),
        "interval_multiplier_2sigma": round(multiplier_2sigma, 6),
    }


def _freeze_conformal_global(loo_standardized: np.ndarray) -> dict[str, Any]:
    """Global split-conformal multipliers frozen from the LOO standardized residuals."""
    q68 = _abs_quantile(loo_standardized, _P1SIGMA_PCT)
    q95 = _abs_quantile(loo_standardized, _P2SIGMA_PCT)
    return {
        "family": "conformal_global",
        "method": "loo_absolute_standardized_empirical_quantiles",
        "interval_multiplier_1sigma": round(q68, 6),
        "interval_multiplier_2sigma": round(q95, 6),
    }


def _freeze_region_quantile(
    loo_standardized: np.ndarray,
    a_band_labels: np.ndarray,
    global_robust_tail: Mapping[str, Any],
) -> dict[str, Any]:
    """Per-``a_band``-region LOO quantile multipliers with a predeclared min count."""
    fallback_1sigma = float(global_robust_tail["interval_multiplier_1sigma"])
    fallback_2sigma = float(global_robust_tail["interval_multiplier_2sigma"])
    regions: dict[str, Any] = {}
    for region in _A_BAND_REGIONS:
        mask = a_band_labels == region
        count = int(mask.sum())
        if count >= REGION_MIN_LOO_COUNT:
            regions[region] = {
                "loo_count": count,
                "uses_fallback": False,
                "interval_multiplier_1sigma": round(
                    _abs_quantile(loo_standardized[mask], _P1SIGMA_PCT), 6
                ),
                "interval_multiplier_2sigma": round(
                    _abs_quantile(loo_standardized[mask], _P2SIGMA_PCT), 6
                ),
            }
        else:
            regions[region] = {
                "loo_count": count,
                "uses_fallback": True,
                "interval_multiplier_1sigma": round(fallback_1sigma, 6),
                "interval_multiplier_2sigma": round(fallback_2sigma, 6),
            }
    return {
        "family": "region_quantile_min_count",
        "method": "per_a_band_loo_absolute_standardized_quantiles",
        "partition": REGION_PARTITION,
        "min_loo_count": REGION_MIN_LOO_COUNT,
        "fallback_family": "global_robust_tail",
        "regions": regions,
    }


def _build_frozen_config(
    loo_standardized: np.ndarray, a_band_labels: np.ndarray
) -> dict[str, Any]:
    """Assemble the full frozen config from LOO diagnostics only (no holdout read)."""
    global_robust_tail = _freeze_global_robust_tail(loo_standardized)
    conformal_global = _freeze_conformal_global(loo_standardized)
    region_quantile = _freeze_region_quantile(
        loo_standardized, a_band_labels, global_robust_tail
    )
    return {
        "frozen_before_holdout_scoring": True,
        "route_preflight_task": ROUTE_PREFLIGHT_TASK_ID,
        "region_partition": REGION_PARTITION,
        "region_min_loo_count": REGION_MIN_LOO_COUNT,
        "nominal_coverage": {
            "central_1sigma": _NOMINAL_1SIGMA,
            "central_2sigma": _NOMINAL_2SIGMA,
        },
        "families": {
            "global_robust_tail": global_robust_tail,
            "region_quantile_min_count": region_quantile,
            "conformal_global": conformal_global,
        },
        "predeclared_success_conditions": PREDECLARED_SUCCESS_CONDITIONS,
        "predeclared_success_thresholds": {
            "coverage_1sigma_tol": SUCCESS_COVERAGE_1SIGMA_TOL,
            "coverage_2sigma_tol": SUCCESS_COVERAGE_2SIGMA_TOL,
            "rms_z_low": SUCCESS_RMS_Z_LOW,
            "rms_z_high": SUCCESS_RMS_Z_HIGH,
            "max_median_width_inflation": SUCCESS_MAX_MEDIAN_WIDTH_INFLATION,
            "max_p90_width_inflation": SUCCESS_MAX_P90_WIDTH_INFLATION,
        },
    }


# --------------------------------------------------------------------------- #
# Holdout scoring (after freeze).
# --------------------------------------------------------------------------- #


def _score_intervals(
    corrected_residual: np.ndarray,
    raw_sigma: np.ndarray,
    multiplier_1sigma: np.ndarray,
    multiplier_2sigma: np.ndarray,
) -> dict[str, float | int]:
    """Empirical coverage / width-inflation metrics for a frozen interval rule.

    ``multiplier_*`` are per-row multipliers on the raw GP 1-sigma; the calibrated
    1-sigma half-width is ``multiplier_1sigma * raw_sigma``. Coverage is the
    empirical fraction of holdout corrected residuals inside the half-width.
    Width inflation compares the calibrated 1-sigma half-width to the raw GP
    1-sigma half-width on the same rows.
    """
    half_1sigma = multiplier_1sigma * raw_sigma
    half_2sigma = multiplier_2sigma * raw_sigma
    abs_res = np.abs(corrected_residual)
    width_inflation = half_1sigma / raw_sigma  # == multiplier_1sigma
    # Post-calibration standardized residual scales the raw residual by the
    # per-row 1-sigma multiplier (the calibrated 1-sigma half-width).
    calibrated_standardized = corrected_residual / half_1sigma
    return {
        "count": int(corrected_residual.size),
        "empirical_coverage_1sigma": round(float(np.mean(abs_res <= half_1sigma)), 6),
        "empirical_coverage_2sigma": round(float(np.mean(abs_res <= half_2sigma)), 6),
        "coverage_1sigma_minus_nominal": round(
            float(np.mean(abs_res <= half_1sigma) - _NOMINAL_1SIGMA), 6
        ),
        "coverage_2sigma_minus_nominal": round(
            float(np.mean(abs_res <= half_2sigma) - _NOMINAL_2SIGMA), 6
        ),
        "rms_standardized_residual": round(
            float(np.sqrt(np.mean(calibrated_standardized**2))), 6
        ),
        "median_width_inflation": round(float(np.median(width_inflation)), 6),
        "p90_width_inflation": round(float(np.percentile(width_inflation, 90)), 6),
        "max_width_inflation": round(float(np.max(width_inflation)), 6),
        "median_1sigma_halfwidth_mev": round(float(np.median(half_1sigma)), 6),
    }


def _evaluate_success(metrics: Mapping[str, float | int]) -> dict[str, Any]:
    """Evaluate the predeclared success conditions against a family's holdout metrics."""
    cov1 = float(metrics["empirical_coverage_1sigma"])
    cov2 = float(metrics["empirical_coverage_2sigma"])
    rms_z = float(metrics["rms_standardized_residual"])
    median_infl = float(metrics["median_width_inflation"])
    p90_infl = float(metrics["p90_width_inflation"])

    central_ok = (
        abs(cov1 - _NOMINAL_1SIGMA) <= SUCCESS_COVERAGE_1SIGMA_TOL
        and abs(cov2 - _NOMINAL_2SIGMA) <= SUCCESS_COVERAGE_2SIGMA_TOL
    )
    tail_ok = SUCCESS_RMS_Z_LOW <= rms_z <= SUCCESS_RMS_Z_HIGH
    sharpness_ok = (
        median_infl <= SUCCESS_MAX_MEDIAN_WIDTH_INFLATION
        and p90_infl <= SUCCESS_MAX_P90_WIDTH_INFLATION
    )

    tripped_stops: list[str] = []
    if not sharpness_ok:
        tripped_stops.append("interval_width_explodes")
    # Tail-fix-overcovers-center: the tail target failed while 1-sigma coverage
    # is even more over-covered than the uncalibrated blocker (0.823729).
    if not tail_ok and cov1 > 0.823729:
        tripped_stops.append("tail_fix_overcovers_center")

    return {
        "central_calibration_pass": central_ok,
        "tail_control_pass": tail_ok,
        "sharpness_pass": sharpness_ok,
        "all_conditions_pass": bool(central_ok and tail_ok and sharpness_ok),
        "tripped_stop_conditions": tripped_stops,
    }


def _outlier_ledger(
    nuclide_ids: Sequence[str],
    z: np.ndarray,
    n: np.ndarray,
    corrected_residual: np.ndarray,
    raw_sigma: np.ndarray,
    top: int = 5,
) -> list[dict[str, Any]]:
    standardized = corrected_residual / raw_sigma
    order = np.argsort(-np.abs(standardized))[:top]
    ledger: list[dict[str, Any]] = []
    for idx in order:
        ledger.append(
            {
                "nuclide_id": str(nuclide_ids[idx]),
                "Z": int(z[idx]),
                "N": int(n[idx]),
                "A": int(z[idx] + n[idx]),
                "corrected_residual_mev": round(float(corrected_residual[idx]), 6),
                "raw_sigma_mev": round(float(raw_sigma[idx]), 6),
                "standardized_residual": round(float(standardized[idx]), 6),
                "a_band": _a_band(int(z[idx] + n[idx])),
                "neutron_excess_band": _neutron_excess_band(
                    int(z[idx]), int(n[idx]), int(z[idx] + n[idx])
                ),
                "magic_neighborhood": _magic_band(int(z[idx]), int(n[idx])),
            }
        )
    return ledger


# --------------------------------------------------------------------------- #
# Top-level audit.
# --------------------------------------------------------------------------- #


def _repo_relative_posix(path: Path) -> str:
    resolved = path.resolve()
    for parent in [resolved, *resolved.parents]:
        if (parent / "data").is_dir() and (parent / "physics_lab").is_dir():
            try:
                return resolved.relative_to(parent).as_posix()
            except ValueError:  # pragma: no cover - defensive
                break
    return path.as_posix()


def run_nmd0003_gp_calibration_audit(
    *,
    dataset_path: Path | str = DEFAULT_DATASET_PATH,
    gate_path: Path | str = DEFAULT_GATE_PATH,
    holdout_path: Path | str = DEFAULT_HOLDOUT_PATH,
) -> dict[str, Any]:
    """Run the deterministic no-peek NMD-0003 GP uncertainty-calibration audit."""
    dataset_path = Path(dataset_path)
    gate_path = Path(gate_path)
    holdout_path = Path(holdout_path)

    dataset = load_nuclear_mass_dataset(dataset_path)
    entries = sorted(
        dataset.entries, key=lambda entry: (entry.A, entry.Z, entry.N, entry.nuclide_id)
    )
    gate = yaml.safe_load(gate_path.read_text(encoding="utf-8"))
    coefficients = _frozen_baseline_coefficients(gate)

    z_train, n_train, residual_train = _training_residuals(entries, coefficients)
    a_train = z_train + n_train
    a_band_labels = np.array([_a_band(a) for a in a_train])

    # Fit the merged GP exactly as the engine does (no re-tuning, no holdout).
    fit = fit_residual_gp(z_train, n_train, residual_train)

    # ---- Train-only LOO diagnostics ----
    loo = _loo_diagnostics(fit, residual_train)
    loo_standardized = loo["loo_standardized"]
    loo_summary = _standardized_summary(loo_standardized)

    # ---- FREEZE the config from LOO only (BEFORE reading the holdout) ----
    frozen_config = _build_frozen_config(loo_standardized, a_band_labels)

    # ===================================================================== #
    # Everything below this line reads the post-AME2020 holdout. The config
    # above is already frozen and must not be modified using these values.
    # ===================================================================== #
    holdout_payload = load_post_ame2020_holdout_dataset(holdout_path)
    holdout_rows = [
        row
        for row in holdout_payload["entries"]
        if bool(row["included_in_time_split_holdout"])
    ]
    if not holdout_rows:
        raise ValueError("post-AME2020 holdout has no primary evaluation rows.")
    holdout_rows = sorted(
        holdout_rows, key=lambda row: (int(row["Z"]) + int(row["N"]), int(row["Z"]))
    )
    nuclide_ids = [str(row["nuclide_id"]) for row in holdout_rows]
    holdout = _holdout_arrays(holdout_rows, coefficients)
    holdout_mean, holdout_sigma = fit.predict(holdout["Z"], holdout["N"])
    corrected_residual = holdout["baseline_residual"] - holdout_mean
    holdout_standardized = corrected_residual / holdout_sigma
    holdout_z = holdout["Z"]
    holdout_n = holdout["N"]
    holdout_a = holdout_z + holdout_n
    holdout_a_band = np.array([_a_band(a) for a in holdout_a])

    # Uncalibrated (raw GP) holdout calibration, for reference (multiplier == 1).
    ones = np.ones_like(holdout_sigma)
    uncalibrated = _score_intervals(corrected_residual, holdout_sigma, ones, 2.0 * ones)
    uncalibrated_summary = _standardized_summary(holdout_standardized)

    # ---- Score each frozen family on the holdout ----
    families = frozen_config["families"]

    grt = families["global_robust_tail"]
    grt_metrics = _score_intervals(
        corrected_residual,
        holdout_sigma,
        float(grt["interval_multiplier_1sigma"]) * ones,
        float(grt["interval_multiplier_2sigma"]) * ones,
    )

    conf = families["conformal_global"]
    conf_metrics = _score_intervals(
        corrected_residual,
        holdout_sigma,
        float(conf["interval_multiplier_1sigma"]) * ones,
        float(conf["interval_multiplier_2sigma"]) * ones,
    )

    region_cfg = families["region_quantile_min_count"]
    region_mult_1 = np.empty_like(holdout_sigma)
    region_mult_2 = np.empty_like(holdout_sigma)
    region_assignment_counts: dict[str, int] = {}
    for region in _A_BAND_REGIONS:
        mask = holdout_a_band == region
        region_assignment_counts[region] = int(mask.sum())
        spec = region_cfg["regions"][region]
        region_mult_1[mask] = float(spec["interval_multiplier_1sigma"])
        region_mult_2[mask] = float(spec["interval_multiplier_2sigma"])
    region_metrics = _score_intervals(
        corrected_residual, holdout_sigma, region_mult_1, region_mult_2
    )
    region_metrics["holdout_region_counts"] = region_assignment_counts
    region_metrics["fallback_regions"] = sorted(
        region for region in _A_BAND_REGIONS if region_cfg["regions"][region]["uses_fallback"]
    )

    family_results = {
        "global_robust_tail": {
            "frozen": grt,
            "holdout_metrics": grt_metrics,
            "success": _evaluate_success(grt_metrics),
        },
        "region_quantile_min_count": {
            "frozen": region_cfg,
            "holdout_metrics": region_metrics,
            "success": _evaluate_success(region_metrics),
        },
        "conformal_global": {
            "frozen": conf,
            "holdout_metrics": conf_metrics,
            "success": _evaluate_success(conf_metrics),
        },
    }

    any_pass = any(
        result["success"]["all_conditions_pass"] for result in family_results.values()
    )
    passing_families = sorted(
        name
        for name, result in family_results.items()
        if result["success"]["all_conditions_pass"]
    )
    audit_verdict = (
        "NO_PEEK_CALIBRATION_PASS"
        if any_pass
        else "NO_PEEK_CALIBRATION_FAIL_TASK_0827_STILL_BLOCKED"
    )

    tripped_stops = sorted(
        {
            stop
            for result in family_results.values()
            for stop in result["success"]["tripped_stop_conditions"]
        }
    )

    return {
        "task_id": TASK_ID,
        "benchmark_id": BENCHMARK_ID,
        "engine_version": ENGINE_VERSION,
        "source_task_id": SOURCE_TASK_ID,
        "source_agent_run_id": SOURCE_AGENT_RUN_ID,
        "route_preflight_task": ROUTE_PREFLIGHT_TASK_ID,
        "prediction_freeze_task": PREDICTION_FREEZE_TASK_ID,
        "input_references": {
            "dataset": _repo_relative_posix(dataset_path),
            "frozen_gate": _repo_relative_posix(gate_path),
            "post_ame2020_holdout": _repo_relative_posix(holdout_path),
            "gp_engine": "physics_lab/engines/nmd0003_residual_gp.py",
        },
        "dataset_summary": {
            "dataset_id": dataset.dataset_id,
            "training_row_count": len(entries),
            "holdout_primary_row_count": len(holdout_rows),
            "post_ame2020_rows_used_for_calibration": 0,
        },
        "gp_fitted_hyperparameters": {
            "sigma_f_mev": round(fit.sigma_f, 6),
            "length_scale_standardized": round(fit.length_scale, 6),
            "sigma_n_mev": round(fit.sigma_n, 6),
        },
        "train_only_loo_diagnostics": loo_summary,
        "frozen_config": frozen_config,
        "holdout_uncalibrated_reference": {
            "interval_metrics": uncalibrated,
            "standardized_summary": uncalibrated_summary,
        },
        "family_results": family_results,
        "outlier_ledger": _outlier_ledger(
            nuclide_ids, holdout_z, holdout_n, corrected_residual, holdout_sigma
        ),
        "audit_decision": {
            "any_family_passes": any_pass,
            "passing_families": passing_families,
            "tripped_stop_conditions": tripped_stops,
            "stop_condition_definitions": _STOP_CONDITIONS,
        },
        "verdict": audit_verdict,
        "prediction_freeze_impact": (
            "unchanged_task_0827_remains_blocked"
            if not any_pass
            else "task_0827_unblock_candidate_pending_maintainer_review"
        ),
        "limitations": [
            "Calibration audit only: no PRED/RESULT/CLAIM/KNOW artifact is created "
            "and RESULT-0025 is not modified.",
            "Retrospective post-AME2020 time-split holdout, not a strict blind "
            "prediction reveal.",
            "Single GP model class (RBF on [Z, N] residuals) and one frozen "
            "liquid-drop baseline; a different baseline or model would shift the "
            "residual surface and the LOO diagnostics.",
            "Three predeclared TASK-0865 route families only; no broader "
            "calibration-method search is performed (by design, to stay no-peek).",
            "LOO diagnostics use the exact closed-form GP leave-one-out identities "
            "on the cached training kernel; they characterize the training surface "
            "and need not match the heavier-tailed holdout, which is exactly what "
            "this audit measures.",
        ],
        "output_routing": {
            "task_verdict": audit_verdict,
            "canonical_destination": "sandbox_agent_run_plus_review_note",
            "claim_impact": "none",
            "knowledge_impact": "none",
            "result_impact": "none",
            "prediction_impact": "none",
        },
    }
