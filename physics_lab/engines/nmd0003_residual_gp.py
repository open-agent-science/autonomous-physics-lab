"""Deterministic Gaussian-process residual model for the NMD-0003 baseline (TASK-0824).

This module fits a self-contained Gaussian-process (GP) regression on the frozen
liquid-drop baseline *residuals* (``measured_binding_energy - baseline_binding_energy``)
over the **NMD-0003 training split only**, then evaluates extrapolation accuracy
and uncertainty calibration on the reviewed post-AME2020 time-split holdout.

Design (all deterministic; no scikit-learn dependency):

* **Frozen baseline.** The comparison reference is the frozen NMD-0003
  ``required_audit_baseline`` (``nmd0003_train_fitted_ols``) recorded in
  ``data/nuclear_masses/nmd-0003-stratified-baseline-gate.yaml``. That five
  coefficient liquid-drop fit was produced on the NMD-0003 training split only,
  so taking its residuals introduces no post-AME2020 holdout leakage. The GP is
  a *correction* on top of this frozen baseline, never a refit of it.
* **Feature basis.** Each nuclide maps to ``x = [Z, N]`` standardized by the
  training-split mean/standard deviation. The RBF kernel then measures locality
  in the proton/neutron plane, the physically natural coordinate for a smooth
  residual surface. The basis is intentionally simple and consistent with the
  existing baseline/diagnostic features (``Z``, ``N``).
* **Kernel.** ``k(x, x') = sigma_f^2 * exp(-||x - x'||^2 / (2 * l^2))`` with an
  additive white-noise variance ``sigma_n^2`` on the diagonal.
* **Hyperparameters.** ``(log sigma_f, log l, log sigma_n)`` are fit by
  deterministic marginal-likelihood maximisation (SciPy L-BFGS-B from a fixed
  initialisation, with bounded log-parameters). L-BFGS-B with the default
  numerical gradient is fully deterministic here, so the fit is bit-reproducible
  with no random seed. ``DEFAULT_RANDOM_SEED`` is still recorded and threaded
  through the (seed-controlled) control shuffles so any stochastic step is
  pinned.
* **Predictive uncertainty.** The predicted ``1 sigma`` band for a *new noisy
  observation* is ``sqrt(posterior_latent_variance + sigma_n^2)``. Calibration is
  the empirical coverage of the predicted 1 sigma / 2 sigma bands by the actual
  GP-corrected holdout residuals.
* **Controls-first.** A ``predeclared`` survival margin (``SURVIVAL_MARGIN_MEV``)
  must be cleared by the GP MAE improvement over the *best* control before the
  extrapolation gain counts as control-surviving. Controls are: a null shuffled
  target GP (breaks the ``(Z, N) -> residual`` link), a 1-D smooth-``A`` GP
  (smooth mass-number trend only), and the uncorrected baseline.

The deliverable is a calibrated residual *model and its diagnostics*. It does not
promote a prediction, claim, knowledge entry, or discovery; an improved fit or
calibration is a methodology contribution only.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from scipy.optimize import minimize

from physics_lab.engines.nuclear_mass_baselines import (
    SemiEmpiricalCoefficients,
    semi_empirical_binding_energy,
)
from physics_lab.engines.nuclear_masses import NuclearMassEntry, load_nuclear_mass_dataset
from physics_lab.registry.post_ame2020_holdout import load_post_ame2020_holdout_dataset

TASK_ID = "TASK-0824"
BENCHMARK_ID = "nmd0003-calibrated-uncertainty-residual-gp"
ENGINE_VERSION = "0.1.0"

DEFAULT_DATASET_PATH = Path("data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml")
DEFAULT_GATE_PATH = Path("data/nuclear_masses/nmd-0003-stratified-baseline-gate.yaml")
DEFAULT_HOLDOUT_PATH = Path("data/nuclear_masses/post_ame2020_holdout.yaml")

# Frozen NMD-0003 baseline used as the residual reference. The audit baseline is
# a global ordinary-least-squares liquid-drop fit on the NMD-0003 training split
# only, so its residuals carry no post-AME2020 holdout information.
FROZEN_BASELINE_ID = "nmd0003_train_fitted_ols"

# Predeclared controls-first survival margin (MeV). This mirrors the established
# NMD-0003 bounded-sprint convention and is fixed BEFORE the holdout scores are
# read: the GP only counts as a control-surviving extrapolation gain if its
# holdout MAE improvement beats the best control by at least this margin.
SURVIVAL_MARGIN_MEV = 0.25

# Fixed seed for any stochastic step (control target shuffles). The GP fit itself
# is deterministic and does not consume the seed.
DEFAULT_RANDOM_SEED = 824

# Bounded log-hyperparameter search box: signal sigma_f in [0.1, 50] MeV,
# length-scale l in [0.1, 5] standardized units, noise sigma_n in [0.05, 5] MeV.
_LOG_BOUNDS = (
    (float(np.log(0.1)), float(np.log(50.0))),
    (float(np.log(0.1)), float(np.log(5.0))),
    (float(np.log(0.05)), float(np.log(5.0))),
)
_OPTIMIZER_MAXITER = 100
_JITTER = 1e-8


@dataclass(frozen=True)
class GPFit:
    """A fitted GP correction model on standardized ``[Z, N]`` features."""

    feature_mean: np.ndarray
    feature_std: np.ndarray
    target_mean: float
    sigma_f: float
    length_scale: float
    sigma_n: float
    log_marginal_likelihood: float
    train_features: np.ndarray
    alpha: np.ndarray
    cholesky_lower: np.ndarray

    def predict(self, z: np.ndarray, n: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Return (posterior mean, predictive 1-sigma) for new (Z, N) points."""
        x_star = self._standardize(z, n)
        k_star = _rbf(x_star, self.train_features, self.sigma_f, self.length_scale)
        mean = k_star @ self.alpha + self.target_mean
        v = np.linalg.solve(self.cholesky_lower, k_star.T)
        latent_var = np.maximum(self.sigma_f**2 - np.sum(v**2, axis=0), 0.0)
        predictive_sigma = np.sqrt(latent_var + self.sigma_n**2)
        return mean, predictive_sigma

    def predict_with_targets(
        self, z: np.ndarray, n: np.ndarray, targets: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Posterior mean/1-sigma at this fit's hyperparameters but new train targets.

        Reuses the cached Cholesky factor (the kernel only depends on the training
        features and hyperparameters), refitting only the posterior weights for the
        supplied ``targets``. Used by the fixed-hyperparameter null control.
        """
        targets = np.asarray(targets, dtype=float)
        target_mean = float(targets.mean())
        centered = targets - target_mean
        alpha = np.linalg.solve(
            self.cholesky_lower.T, np.linalg.solve(self.cholesky_lower, centered)
        )
        x_star = self._standardize(z, n)
        k_star = _rbf(x_star, self.train_features, self.sigma_f, self.length_scale)
        mean = k_star @ alpha + target_mean
        v = np.linalg.solve(self.cholesky_lower, k_star.T)
        latent_var = np.maximum(self.sigma_f**2 - np.sum(v**2, axis=0), 0.0)
        predictive_sigma = np.sqrt(latent_var + self.sigma_n**2)
        return mean, predictive_sigma

    def _standardize(self, z: np.ndarray, n: np.ndarray) -> np.ndarray:
        return np.column_stack(
            [
                (np.asarray(z, dtype=float) - self.feature_mean[0]) / self.feature_std[0],
                (np.asarray(n, dtype=float) - self.feature_mean[1]) / self.feature_std[1],
            ]
        )


def _rbf(a: np.ndarray, b: np.ndarray, sigma_f: float, length_scale: float) -> np.ndarray:
    sq = (
        np.sum(a**2, axis=1)[:, None]
        + np.sum(b**2, axis=1)[None, :]
        - 2.0 * a @ b.T
    )
    sq = np.maximum(sq, 0.0)
    return (sigma_f**2) * np.exp(-0.5 * sq / (length_scale**2))


def _negative_log_marginal_likelihood(
    log_theta: np.ndarray, sq_dist: np.ndarray, y_centered: np.ndarray
) -> tuple[float, np.ndarray]:
    """Return (negative log marginal likelihood, analytic gradient w.r.t. log_theta).

    The analytic gradient lets L-BFGS-B converge in a handful of objective
    evaluations instead of one numerical-gradient sweep per step, which keeps the
    full-surface GP fit deterministic *and* fast enough for CI.
    """
    log_sf, log_l, log_sn = log_theta
    sigma_f2 = np.exp(2.0 * log_sf)
    length = np.exp(log_l)
    sigma_n2 = np.exp(2.0 * log_sn)
    n = y_centered.shape[0]
    rbf = np.exp(-0.5 * sq_dist / (length**2))
    kernel = sigma_f2 * rbf
    kernel[np.diag_indices(n)] += sigma_n2 + _JITTER
    try:
        lower = np.linalg.cholesky(kernel)
    except np.linalg.LinAlgError:
        return 1e25, np.zeros(3)
    alpha = np.linalg.solve(lower.T, np.linalg.solve(lower, y_centered))
    nll = float(
        0.5 * y_centered @ alpha
        + np.sum(np.log(np.diag(lower)))
        + 0.5 * n * np.log(2.0 * np.pi)
    )
    kernel_inv = np.linalg.solve(lower.T, np.linalg.solve(lower, np.eye(n)))
    factor = np.outer(alpha, alpha) - kernel_inv  # 0.5 * tr(factor @ dK/dtheta)
    grad_sf = -0.5 * float(np.sum(factor * (2.0 * sigma_f2 * rbf)))
    grad_l = -0.5 * float(np.sum(factor * (sigma_f2 * rbf * (sq_dist / length**2))))
    grad_sn = -0.5 * float(np.sum(np.diag(factor) * (2.0 * sigma_n2)))
    return nll, np.array([grad_sf, grad_l, grad_sn])


def fit_residual_gp(
    z: Sequence[float],
    n: Sequence[float],
    residual: Sequence[float],
) -> GPFit:
    """Fit a deterministic RBF GP on baseline residuals over standardized [Z, N]."""
    z_arr = np.asarray(z, dtype=float)
    n_arr = np.asarray(n, dtype=float)
    y_arr = np.asarray(residual, dtype=float)
    raw = np.column_stack([z_arr, n_arr])
    mean = raw.mean(axis=0)
    std = raw.std(axis=0)
    std = np.where(std == 0.0, 1.0, std)
    features = (raw - mean) / std
    target_mean = float(y_arr.mean())
    y_centered = y_arr - target_mean

    sq_dist = (
        np.sum(features**2, axis=1)[:, None]
        + np.sum(features**2, axis=1)[None, :]
        - 2.0 * features @ features.T
    )
    sq_dist = np.maximum(sq_dist, 0.0)

    init = np.array(
        [np.log(max(y_arr.std(), 1e-3)), np.log(0.5), np.log(0.5)], dtype=float
    )
    result = minimize(
        _negative_log_marginal_likelihood,
        init,
        args=(sq_dist, y_centered),
        method="L-BFGS-B",
        jac=True,
        bounds=_LOG_BOUNDS,
        options={"maxiter": _OPTIMIZER_MAXITER},
    )
    log_sf, log_l, log_sn = result.x
    sigma_f = float(np.exp(log_sf))
    length_scale = float(np.exp(log_l))
    sigma_n = float(np.exp(log_sn))

    kernel = (sigma_f**2) * np.exp(-0.5 * sq_dist / (length_scale**2))
    kernel[np.diag_indices(features.shape[0])] += sigma_n**2 + _JITTER
    lower = np.linalg.cholesky(kernel)
    alpha = np.linalg.solve(lower.T, np.linalg.solve(lower, y_centered))

    return GPFit(
        feature_mean=mean,
        feature_std=std,
        target_mean=target_mean,
        sigma_f=sigma_f,
        length_scale=length_scale,
        sigma_n=sigma_n,
        log_marginal_likelihood=float(-result.fun),
        train_features=features,
        alpha=alpha,
        cholesky_lower=lower,
    )


# --------------------------------------------------------------------------- #
# Data assembly
# --------------------------------------------------------------------------- #


def _frozen_baseline_coefficients(gate: Mapping[str, Any]) -> SemiEmpiricalCoefficients:
    contract = gate["baseline_contract"]["required_audit_baseline"]
    if contract["baseline_id"] != FROZEN_BASELINE_ID:
        raise ValueError(
            "NMD-0003 audit baseline id changed; expected "
            f"{FROZEN_BASELINE_ID}, got {contract['baseline_id']}."
        )
    return SemiEmpiricalCoefficients(**contract["coefficients"])


def _training_residuals(
    entries: Sequence[NuclearMassEntry], coefficients: SemiEmpiricalCoefficients
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    z = np.array([entry.Z for entry in entries], dtype=float)
    n = np.array([entry.N for entry in entries], dtype=float)
    residual = np.array(
        [
            entry.binding_energy_mev
            - semi_empirical_binding_energy(z=entry.Z, n=entry.N, coefficients=coefficients)
            for entry in entries
        ],
        dtype=float,
    )
    return z, n, residual


def _holdout_arrays(
    holdout_rows: Sequence[Mapping[str, Any]], coefficients: SemiEmpiricalCoefficients
) -> dict[str, np.ndarray]:
    z = np.array([int(row["Z"]) for row in holdout_rows], dtype=float)
    n = np.array([int(row["N"]) for row in holdout_rows], dtype=float)
    observed = np.array(
        [float(row["new_measurement"]["value_mev"]) for row in holdout_rows], dtype=float
    )
    baseline = np.array(
        [
            semi_empirical_binding_energy(
                z=int(row["Z"]), n=int(row["N"]), coefficients=coefficients
            )
            for row in holdout_rows
        ],
        dtype=float,
    )
    return {
        "Z": z,
        "N": n,
        "observed": observed,
        "baseline": baseline,
        "baseline_residual": observed - baseline,
    }


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #


def _error_summary(errors: np.ndarray) -> dict[str, float | int]:
    abs_err = np.abs(errors)
    return {
        "count": int(errors.size),
        "mae_mev": round(float(np.mean(abs_err)), 6),
        "rms_mev": round(float(np.sqrt(np.mean(errors**2))), 6),
        "median_abs_mev": round(float(np.median(abs_err)), 6),
        "p90_abs_mev": round(float(np.percentile(abs_err, 90)), 6),
        "max_abs_mev": round(float(np.max(abs_err)), 6),
    }


def _calibration_summary(
    corrected_residual: np.ndarray, predictive_sigma: np.ndarray
) -> dict[str, float | int]:
    standardized = corrected_residual / predictive_sigma
    abs_z = np.abs(standardized)
    return {
        "count": int(corrected_residual.size),
        "empirical_coverage_1sigma": round(float(np.mean(abs_z <= 1.0)), 6),
        "empirical_coverage_2sigma": round(float(np.mean(abs_z <= 2.0)), 6),
        "expected_coverage_1sigma": 0.682689,
        "expected_coverage_2sigma": 0.954500,
        "coverage_1sigma_minus_expected": round(float(np.mean(abs_z <= 1.0) - 0.682689), 6),
        "coverage_2sigma_minus_expected": round(float(np.mean(abs_z <= 2.0) - 0.954500), 6),
        "rms_standardized_residual": round(float(np.sqrt(np.mean(standardized**2))), 6),
        "mean_predictive_sigma_mev": round(float(np.mean(predictive_sigma)), 6),
        "median_predictive_sigma_mev": round(float(np.median(predictive_sigma)), 6),
        "fraction_beyond_2sigma": round(float(np.mean(abs_z > 2.0)), 6),
    }


def _calibration_verdict(calibration: Mapping[str, float | int]) -> str:
    rms_z = float(calibration["rms_standardized_residual"])
    cov2 = float(calibration["empirical_coverage_2sigma"])
    cov1 = float(calibration["empirical_coverage_1sigma"])
    if 0.85 <= rms_z <= 1.20 and abs(cov1 - 0.682689) <= 0.05 and abs(cov2 - 0.9545) <= 0.03:
        return "WELL_CALIBRATED"
    if rms_z > 1.20 or cov2 < 0.9545 - 0.03:
        return "UNDERCONFIDENT_HEAVY_TAILED" if cov1 >= 0.682689 else "OVERCONFIDENT"
    return "MILDLY_MISCALIBRATED"


# --------------------------------------------------------------------------- #
# Controls
# --------------------------------------------------------------------------- #


def _shuffled_target_control(
    fit: GPFit,
    residual_train: np.ndarray,
    holdout: Mapping[str, np.ndarray],
    *,
    seed: int,
) -> dict[str, Any]:
    # Reuse the real fit's kernel hyperparameters and feature standardization, but
    # refit the posterior on residuals randomly permuted across nuclides. Holding
    # the model capacity fixed makes this a strictly comparable null: only the
    # (Z, N) -> residual association is destroyed, so any apparent holdout gain
    # would have to come from that broken association.
    shuffled = residual_train.copy()
    np.random.default_rng(seed).shuffle(shuffled)
    mean, _ = fit.predict_with_targets(holdout["Z"], holdout["N"], shuffled)
    corrected = holdout["baseline_residual"] - mean
    return {
        "control_id": "null_shuffled_target_gp",
        "description": (
            "GP posterior refit on training residuals randomly permuted across "
            "nuclides at the real fit's fixed hyperparameters (breaks the "
            "(Z, N) -> residual link); seed-controlled."
        ),
        "seed": seed,
        "corrected": _error_summary(corrected),
    }


def _smooth_a_control(
    z_train: np.ndarray,
    n_train: np.ndarray,
    residual_train: np.ndarray,
    holdout: Mapping[str, np.ndarray],
) -> dict[str, Any]:
    a_train = z_train + n_train
    a_hold = holdout["Z"] + holdout["N"]
    mean = a_train.mean()
    std = a_train.std() or 1.0
    x_train = ((a_train - mean) / std)[:, None]
    x_hold = ((a_hold - mean) / std)[:, None]
    target_mean = float(residual_train.mean())
    y_centered = residual_train - target_mean

    sq = (
        np.sum(x_train**2, axis=1)[:, None]
        + np.sum(x_train**2, axis=1)[None, :]
        - 2.0 * x_train @ x_train.T
    )
    sq = np.maximum(sq, 0.0)
    init = np.array([np.log(max(residual_train.std(), 1e-3)), np.log(0.5), np.log(0.5)])
    result = minimize(
        _negative_log_marginal_likelihood,
        init,
        args=(sq, y_centered),
        method="L-BFGS-B",
        jac=True,
        bounds=_LOG_BOUNDS,
        options={"maxiter": _OPTIMIZER_MAXITER},
    )
    sigma_f = float(np.exp(result.x[0]))
    length = float(np.exp(result.x[1]))
    sigma_n = float(np.exp(result.x[2]))
    kernel = (sigma_f**2) * np.exp(-0.5 * sq / (length**2))
    kernel[np.diag_indices(x_train.shape[0])] += sigma_n**2 + _JITTER
    lower = np.linalg.cholesky(kernel)
    alpha = np.linalg.solve(lower.T, np.linalg.solve(lower, y_centered))
    k_star = (sigma_f**2) * np.exp(
        -0.5
        * np.maximum(
            np.sum(x_hold**2, axis=1)[:, None]
            + np.sum(x_train**2, axis=1)[None, :]
            - 2.0 * x_hold @ x_train.T,
            0.0,
        )
        / (length**2)
    )
    mean_hold = k_star @ alpha + target_mean
    corrected = holdout["baseline_residual"] - mean_hold
    return {
        "control_id": "smooth_a_gp",
        "description": (
            "1-D GP on a smooth function of mass number A only (no Z, N "
            "locality); a structural smoothness control."
        ),
        "corrected": _error_summary(corrected),
    }


# --------------------------------------------------------------------------- #
# Top-level run
# --------------------------------------------------------------------------- #


def _repo_relative_posix(path: Path) -> str:
    """Return a repo-relative POSIX path so recorded references stay portable.

    Recording an absolute worktree path would both leak a machine-local path
    (rejected by the repo's tracked-text guard) and break Gate B replay on
    another checkout. The repo root is located by walking up to the directory
    that contains ``data`` and ``physics_lab``.
    """
    resolved = path.resolve()
    for parent in [resolved, *resolved.parents]:
        if (parent / "data").is_dir() and (parent / "physics_lab").is_dir():
            try:
                return resolved.relative_to(parent).as_posix()
            except ValueError:  # pragma: no cover - defensive
                break
    return path.as_posix()


def run_nmd0003_residual_gp(
    *,
    dataset_path: Path | str = DEFAULT_DATASET_PATH,
    gate_path: Path | str = DEFAULT_GATE_PATH,
    holdout_path: Path | str = DEFAULT_HOLDOUT_PATH,
    survival_margin_mev: float = SURVIVAL_MARGIN_MEV,
    seed: int = DEFAULT_RANDOM_SEED,
) -> dict[str, Any]:
    """Run the deterministic TASK-0824 calibrated GP residual extrapolation benchmark."""
    import yaml

    dataset_path = Path(dataset_path)
    gate_path = Path(gate_path)
    holdout_path = Path(holdout_path)

    dataset = load_nuclear_mass_dataset(dataset_path)
    entries = sorted(
        dataset.entries, key=lambda entry: (entry.A, entry.Z, entry.N, entry.nuclide_id)
    )
    gate = yaml.safe_load(gate_path.read_text(encoding="utf-8"))
    coefficients = _frozen_baseline_coefficients(gate)

    holdout_payload = load_post_ame2020_holdout_dataset(holdout_path)
    holdout_rows = [
        row for row in holdout_payload["entries"] if bool(row["included_in_time_split_holdout"])
    ]
    if not holdout_rows:
        raise ValueError("post-AME2020 holdout has no primary evaluation rows.")

    z_train, n_train, residual_train = _training_residuals(entries, coefficients)
    holdout = _holdout_arrays(holdout_rows, coefficients)

    fit = fit_residual_gp(z_train, n_train, residual_train)

    # In-sample (training) GP fit quality, for context only.
    train_mean, _ = fit.predict(z_train, n_train)
    train_corrected = residual_train - train_mean

    # Extrapolation on the post-AME2020 holdout.
    holdout_mean, holdout_sigma = fit.predict(holdout["Z"], holdout["N"])
    corrected_residual = holdout["baseline_residual"] - holdout_mean

    baseline_holdout = _error_summary(holdout["baseline_residual"])
    gp_holdout = _error_summary(corrected_residual)
    calibration = _calibration_summary(corrected_residual, holdout_sigma)

    controls = {
        "null_shuffled_target_gp": _shuffled_target_control(
            fit, residual_train, holdout, seed=seed
        ),
        "smooth_a_gp": _smooth_a_control(z_train, n_train, residual_train, holdout),
        "uncorrected_baseline": {
            "control_id": "uncorrected_baseline",
            "description": "Frozen NMD-0003 audit baseline with no GP correction.",
            "corrected": baseline_holdout,
        },
    }

    baseline_mae = baseline_holdout["mae_mev"]
    gp_mae_improvement = round(float(baseline_mae - gp_holdout["mae_mev"]), 6)
    control_improvements = {
        control_id: round(float(baseline_mae - control["corrected"]["mae_mev"]), 6)
        for control_id, control in controls.items()
        if control_id != "uncorrected_baseline"
    }
    best_control_id = max(control_improvements, key=control_improvements.get)
    best_control_improvement = control_improvements[best_control_id]
    survival_margin = round(float(gp_mae_improvement - best_control_improvement), 6)
    margin_clears = survival_margin >= survival_margin_mev

    calibration_verdict = _calibration_verdict(calibration)
    verdict = _verdict(
        margin_clears=margin_clears,
        gp_mae_improvement=gp_mae_improvement,
        calibration_verdict=calibration_verdict,
    )

    return {
        "task_id": TASK_ID,
        "benchmark_id": BENCHMARK_ID,
        "engine_version": ENGINE_VERSION,
        "seed": seed,
        "input_references": {
            "dataset": _repo_relative_posix(dataset_path),
            "frozen_gate": _repo_relative_posix(gate_path),
            "post_ame2020_holdout": _repo_relative_posix(holdout_path),
            "frozen_baseline_id": FROZEN_BASELINE_ID,
        },
        "dataset_summary": {
            "dataset_id": dataset.dataset_id,
            "training_row_count": len(entries),
            "holdout_primary_row_count": len(holdout_rows),
            "post_ame2020_rows_used_for_fitting": 0,
        },
        "frozen_baseline": {
            "baseline_id": FROZEN_BASELINE_ID,
            "coefficients": coefficients.to_dict(),
            "training_residual_mev": {
                "mean": round(float(residual_train.mean()), 6),
                "std": round(float(residual_train.std()), 6),
                "mae": round(float(np.mean(np.abs(residual_train))), 6),
            },
        },
        "gp_model": {
            "model_id": "nmd0003_residual_gp_zn_rbf",
            "feature_basis": ["Z", "N"],
            "feature_standardization": "training-split mean/std on [Z, N]",
            "kernel": "rbf_plus_white_noise",
            "hyperparameter_fit": "deterministic_marginal_likelihood_lbfgsb_fixed_init",
            "fitted_hyperparameters": {
                "sigma_f_mev": round(fit.sigma_f, 6),
                "length_scale_standardized": round(fit.length_scale, 6),
                "sigma_n_mev": round(fit.sigma_n, 6),
                "log_marginal_likelihood": round(fit.log_marginal_likelihood, 6),
            },
            "log_hyperparameter_bounds": {
                "sigma_f_mev": [0.1, 50.0],
                "length_scale_standardized": [0.1, 5.0],
                "sigma_n_mev": [0.05, 5.0],
            },
            "train_corrected_residual_mev": _error_summary(train_corrected),
        },
        "extrapolation": {
            "frozen_baseline_holdout": baseline_holdout,
            "gp_corrected_holdout": gp_holdout,
            "gp_mae_improvement_mev": gp_mae_improvement,
            "gp_rms_improvement_mev": round(
                float(baseline_holdout["rms_mev"] - gp_holdout["rms_mev"]), 6
            ),
        },
        "calibration": calibration,
        "calibration_verdict": calibration_verdict,
        "controls": controls,
        "decision": {
            "predeclared_survival_margin_mev": survival_margin_mev,
            "gp_mae_improvement_mev": gp_mae_improvement,
            "control_mae_improvements_mev": control_improvements,
            "best_control_id": best_control_id,
            "best_control_mae_improvement_mev": best_control_improvement,
            "gp_minus_best_control_mae_improvement_mev": survival_margin,
            "survival_margin_clears": margin_clears,
        },
        "verdict": verdict,
        "limitations": [
            "Retrospective post-AME2020 time-split evaluation; not a strict blind "
            "prediction reveal.",
            "Single dataset (NMD-0003 / post-AME2020 holdout) and a single model "
            "class (RBF Gaussian process on [Z, N] residuals); no model-class sweep.",
            "The frozen liquid-drop audit baseline is the residual reference; a "
            "different frozen baseline would shift the residual surface the GP learns.",
            "Predictive uncertainty is the GP posterior plus white-noise variance; "
            "it does not separately model heavy-tailed exotic-nuclide structure, so "
            "tail coverage is the primary calibration limitation.",
            "Methodology contribution only: no PRED, CLAIM, KNOW, or discovery "
            "artifact is created, and improved fit/calibration is not a discovery.",
        ],
        "output_routing": {
            "task_verdict": verdict,
            "calibration_verdict": calibration_verdict,
            "canonical_destination": "sandbox_agent_run_plus_review_note",
            "gate_a_status": "mechanical_conditions_met_routed_to_sandbox",
            "claim_impact": "none",
            "knowledge_impact": "none",
            "result_impact": "calibrated residual model + extrapolation/calibration diagnostics",
        },
    }


def _verdict(
    *, margin_clears: bool, gp_mae_improvement: float, calibration_verdict: str
) -> str:
    if gp_mae_improvement <= 0.0:
        return "NEGATIVE_RESULT_NO_EXTRAPOLATION_GAIN"
    if not margin_clears:
        return "INCONCLUSIVE_CONTROL_DOMINATED"
    if calibration_verdict == "WELL_CALIBRATED":
        return "CONTROL_SURVIVING_GAIN_WELL_CALIBRATED"
    return "CONTROL_SURVIVING_GAIN_MISCALIBRATED_UNCERTAINTY"
