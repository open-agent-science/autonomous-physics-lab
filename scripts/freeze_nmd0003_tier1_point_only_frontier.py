#!/usr/bin/env python3
"""Execute the TASK-0933 tier-1 point-only NMD-0003 frontier prediction freeze.

Implements exactly the Tier-1 Candidate Specification approved at Gate C on
2026-07-05 (Option A on the TASK-0929 decision packet,
``docs/reviews/nmd0003-two-tier-point-only-freeze-contract-packet.md``):

* re-verifies, at freeze time, the no-peek source-state of every
  ``FRONTIER-PRED-TARGETS-0001`` target against the committed in-repo screens
  (a target that gained a committed measured value since design time is
  dropped and recorded, never replaced);
* reproduces the frozen NMD-0003 residual GP surface
  (``model_nmd0003_residual_gp_zn_rbf``, RESULT-0025) deterministically from
  committed inputs and freezes the GP posterior MEAN per surviving target —
  no posterior standard deviation, no interval multiplier, and no derived
  uncertainty field enters any payload;
* freezes the three comparator central values over the same surviving targets
  from committed deterministic engine code: the DZ10 published-equation
  variant (``nmd0003_dz10_published_equation_variant_v2``), the frozen
  liquid-drop baseline of record (``nmd0003_train_fitted_ols``), and the
  ``smooth_a_gp`` predeclared control;
* self-checks every reproduced surface against the committed published
  metrics (RESULT-0025 metrics and AGENT-RUN-0078 metrics) and stops with
  ``FREEZE_BLOCKED`` on any drift instead of weakening a gate;
* emits the four tier-1 ``PRED-*`` registry entries (``freeze_tier:
  point_only``) plus a freeze summary for the review note.

The script is deterministic: given the same committed inputs it produces
byte-identical outputs on every run. It never fetches anything live and it
never reads any measured value for a frontier target (none exists in-repo;
that is what the source-state screen verifies).
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab._runtime import enforce as _enforce_python_runtime  # noqa: E402

_enforce_python_runtime()

import numpy as np  # noqa: E402
from scipy.optimize import minimize  # noqa: E402
import yaml  # noqa: E402

from physics_lab.engines.nmd0003_duflo_zuker_baseline import (  # noqa: E402
    ENGINE_VERSION as DZ10_ENGINE_VERSION,
)
from physics_lab.engines.nmd0003_duflo_zuker_baseline import (  # noqa: E402
    FEATURE_NAMES,
    _holdout_metrics,
    _post_ame2020_rows,
    _within_dz10_domain,
    fit_duflo_zuker_published_variant_coefficients,
    predict_duflo_zuker_binding_energy,
)
from physics_lab.engines.nmd0003_residual_gp import (  # noqa: E402
    _JITTER,
    _LOG_BOUNDS,
    _OPTIMIZER_MAXITER,
    DEFAULT_DATASET_PATH,
    DEFAULT_GATE_PATH,
    DEFAULT_HOLDOUT_PATH,
    FROZEN_BASELINE_ID,
    _frozen_baseline_coefficients,
    _holdout_arrays,
    _negative_log_marginal_likelihood,
    _training_residuals,
    fit_residual_gp,
)
from physics_lab.engines.nmd0003_residual_gp import (  # noqa: E402
    ENGINE_VERSION as GP_ENGINE_VERSION,
)
from physics_lab.engines.nuclear_mass_baselines import (  # noqa: E402
    semi_empirical_binding_energy,
)
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset  # noqa: E402
from physics_lab.registry.post_ame2020_holdout import (  # noqa: E402
    load_post_ame2020_holdout_dataset,
)

TASK_ID = "TASK-0933"
FREEZE_TIER = "point_only"
TARGET_SET_LABEL = "frontier-prediction-targets-0001"
MANIFEST_ID = "FRONTIER-PRED-TARGETS-0001"

MANIFEST_PATH = Path("data/nuclear_masses/frontier_prediction_targets.yaml")
NMD0002_SLICE_PATH = Path("data/nuclear_masses/nmd-0002-curated-measured-slice.yaml")
RESULT_0025_METRICS_PATH = Path("results/EXP-0018/RUN-0001/metrics.json")
AGENT_RUN_0078_METRICS_PATH = Path("agent_runs/AGENT-RUN-0078/metrics.json")
RESULT_0025_PATH = Path("results/EXP-0018/RUN-0001/result.yaml")
RESULT_0015_PATH = Path("results/EXP-0012/RUN-0001/result.yaml")
GATE_PATH = Path(DEFAULT_GATE_PATH)
TRAINING_PATH = Path(DEFAULT_DATASET_PATH)
HOLDOUT_PATH = Path(DEFAULT_HOLDOUT_PATH)

PREDICTION_IDS = {
    "gp": "PRED-0069",
    "dz10": "PRED-0070",
    "liquid_drop": "PRED-0071",
    "smooth_a_gp": "PRED-0072",
}

# Mandatory caveat wording from the approved TASK-0929 decision packet
# (docs/reviews/nmd0003-two-tier-point-only-freeze-contract-packet.md,
# "Mandatory Caveat Wording"). Carried verbatim, unweakened, in every tier-1
# artifact produced by this freeze.
MANDATORY_CAVEAT = (
    "**Tier-1 point-only freeze — mandatory caveat.** The NMD-0003 predictive "
    "uncertainty calibration **failed** the no-peek audit (`TASK-0899`): all three "
    "predeclared route families missed the predeclared coverage and "
    "standardized-residual conditions (best family ~`0.62` 1-sigma coverage, "
    "RMS standardized residual ~`4.3`). **Calibrated prediction intervals are "
    "unavailable.** This freeze registers **point (central-value) forecasts "
    "only**. It makes **no interval or uncertainty claim**, **no** statement of "
    "trustworthy 1-sigma / 2-sigma predictive coverage, and **no** prediction-"
    "readiness or \"prediction-ready\" wording. It is scored at reveal by **MAE and "
    "rank against frozen baselines only**. It is **not** a reveal result and **not** "
    "a blind-prediction success until an admissible source is revealed and scored. "
    "This tier-1 freeze does **not** unblock `TASK-0827`: `TASK-0827` remains the "
    "interval-bearing freeze and remains **blocked** for interval-bearing freezes "
    "until calibration is validated on a fresh surface per the `TASK-0925` "
    "contract. It establishes **no** nuclear-mass law, **no** broad mass formula, "
    "and **no** discovery."
)

# Maintainer disjointness requirement recorded with the Gate C approval.
DISJOINTNESS_REQUIREMENT = (
    "Disjointness requirement (maintainer, Gate C 2026-07-05): any future tier-2 "
    "calibration-validation set (set A) under the TASK-0925 fresh-surface contract "
    "must be disjoint from these frozen tier-1 targets; tier-2 interval coverage is "
    "never reported in-sample on them."
)

HOLDOUT_PROTOCOL_REFERENCES = [
    "docs/blind-holdout-benchmark-protocol.md",
    "docs/nuclear-mass-holdout-protocol.md",
    "docs/prediction-registry-policy.md",
    "docs/nuclear-prediction-reveal-protocol.md",
    "docs/nuclear-reveal-source-readiness-checklist.md",
]


class FreezeBlockedError(RuntimeError):
    """Raised when a freeze stop-condition trips; the freeze must not proceed."""


@dataclass(frozen=True)
class FrontierTarget:
    """One (Z, N)-identity frontier target from the committed manifest."""

    nuclide_id: str
    z: int
    n: int
    a: int
    region_id: str


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping in {path}")
    return payload


# --------------------------------------------------------------------------- #
# Source-state re-verification (reveal-protocol no-peek screen at freeze time)
# --------------------------------------------------------------------------- #


def load_manifest_targets(manifest_path: Path) -> tuple[list[FrontierTarget], dict[str, Any]]:
    """Load the frontier manifest targets in committed manifest order."""
    payload = _load_yaml(manifest_path)
    if payload.get("manifest_id") != MANIFEST_ID:
        raise FreezeBlockedError(
            f"FREEZE_BLOCKED: manifest_id changed; expected {MANIFEST_ID}, "
            f"got {payload.get('manifest_id')!r}."
        )
    targets: list[FrontierTarget] = []
    for region in payload["regions"]:
        for row in region["targets"]:
            target = FrontierTarget(
                nuclide_id=str(row["nuclide_id"]),
                z=int(row["Z"]),
                n=int(row["N"]),
                a=int(row["A"]),
                region_id=str(region["region_id"]),
            )
            if target.a != target.z + target.n:
                raise FreezeBlockedError(
                    f"FREEZE_BLOCKED: manifest target {target.nuclide_id} has A != Z + N."
                )
            targets.append(target)
    return targets, payload


def _committed_identity_screens(
    *,
    training_path: Path,
    holdout_path: Path,
    nmd0002_slice_path: Path,
) -> dict[str, dict[str, set[Any]]]:
    """Collect committed (Z, N) and nuclide-id identities from the screen files."""
    screens: dict[str, dict[str, set[Any]]] = {}

    dataset = load_nuclear_mass_dataset(training_path)
    screens[training_path.as_posix()] = {
        "zn": {(entry.Z, entry.N) for entry in dataset.entries},
        "nuclide_ids": {entry.nuclide_id for entry in dataset.entries},
    }

    holdout_payload = load_post_ame2020_holdout_dataset(holdout_path)
    holdout_rows = holdout_payload["entries"]
    screens[holdout_path.as_posix()] = {
        "zn": {(int(row["Z"]), int(row["N"])) for row in holdout_rows},
        "nuclide_ids": {str(row["nuclide_id"]) for row in holdout_rows},
    }

    slice_payload = _load_yaml(nmd0002_slice_path)
    slice_rows = slice_payload["entries"]
    screens[nmd0002_slice_path.as_posix()] = {
        "zn": {(int(row["Z"]), int(row["N"])) for row in slice_rows},
        "nuclide_ids": {str(row["nuclide_id"]) for row in slice_rows},
    }
    return screens


def reverify_source_state(
    targets: list[FrontierTarget],
    manifest_payload: dict[str, Any],
    screens: dict[str, dict[str, set[Any]]],
) -> tuple[list[FrontierTarget], list[dict[str, Any]]]:
    """Re-verify the no-peek source state of every target at freeze time.

    Returns (surviving targets in manifest order, dropped-target ledger).
    Dropped targets are recorded and never replaced. The excluded committed
    neighbors documented by the manifest must not appear among the targets.
    """
    excluded = manifest_payload.get("excluded_committed_neighbors", {})
    excluded_zn = {
        (int(row["Z"]), int(row["N"]))
        for key in ("in_nmd0003_training", "in_post_ame2020_holdout")
        for row in excluded.get(key, [])
    }
    for target in targets:
        if (target.z, target.n) in excluded_zn:
            raise FreezeBlockedError(
                "FREEZE_BLOCKED: excluded committed neighbor "
                f"{target.nuclide_id} appears in the target list."
            )

    surviving: list[FrontierTarget] = []
    dropped: list[dict[str, Any]] = []
    for target in targets:
        hits: list[str] = []
        for screen_path, identity_sets in screens.items():
            if (target.z, target.n) in identity_sets["zn"]:
                hits.append(f"{screen_path}::zn")
            if target.nuclide_id in identity_sets["nuclide_ids"]:
                hits.append(f"{screen_path}::nuclide_id")
        if hits:
            dropped.append(
                {
                    "nuclide_id": target.nuclide_id,
                    "Z": target.z,
                    "N": target.n,
                    "A": target.a,
                    "region_id": target.region_id,
                    "reason": "committed_measured_value_found_at_freeze_time",
                    "screen_hits": sorted(hits),
                }
            )
        else:
            surviving.append(target)

    if not surviving:
        raise FreezeBlockedError(
            "FREEZE_BLOCKED: the target manifest failed wholesale source-state "
            "re-verification; zero targets survived."
        )
    return surviving, dropped


# --------------------------------------------------------------------------- #
# Frozen surfaces (reproduced deterministically from committed inputs)
# --------------------------------------------------------------------------- #


def _require_equal(name: str, reproduced: float, committed: float) -> None:
    if reproduced != committed:
        raise FreezeBlockedError(
            f"FREEZE_BLOCKED: frozen-surface identity check failed for {name}: "
            f"reproduced {reproduced!r} != committed {committed!r}. The engine "
            "command is non-deterministic or the committed surface changed; "
            "no gate is weakened."
        )


@dataclass(frozen=True)
class SmoothAFit:
    """Deterministic 1-D smooth-A GP refit (identical math to the engine control)."""

    a_mean: float
    a_std: float
    target_mean: float
    sigma_f: float
    length_scale: float
    sigma_n: float
    x_train: np.ndarray
    alpha: np.ndarray

    def predict_mean(self, a_values: np.ndarray) -> np.ndarray:
        x_eval = ((np.asarray(a_values, dtype=float) - self.a_mean) / self.a_std)[:, None]
        k_star = (self.sigma_f**2) * np.exp(
            -0.5
            * np.maximum(
                np.sum(x_eval**2, axis=1)[:, None]
                + np.sum(self.x_train**2, axis=1)[None, :]
                - 2.0 * x_eval @ self.x_train.T,
                0.0,
            )
            / (self.length_scale**2)
        )
        return k_star @ self.alpha + self.target_mean


def fit_smooth_a_gp(
    z_train: np.ndarray, n_train: np.ndarray, residual_train: np.ndarray
) -> SmoothAFit:
    """Refit the ``smooth_a_gp`` predeclared control exactly as the frozen engine does.

    This mirrors ``physics_lab.engines.nmd0003_residual_gp._smooth_a_control``
    operation-for-operation (same initialisation, bounds, optimizer options,
    jitter, and linear algebra), exposing the fitted posterior so the control
    can be evaluated at the frontier targets. Identity with the committed
    engine control is enforced by the holdout-MAE equality self-check.
    """
    a_train = z_train + n_train
    mean = a_train.mean()
    std = a_train.std() or 1.0
    x_train = ((a_train - mean) / std)[:, None]
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
    return SmoothAFit(
        a_mean=float(mean),
        a_std=float(std),
        target_mean=target_mean,
        sigma_f=sigma_f,
        length_scale=length,
        sigma_n=sigma_n,
        x_train=x_train,
        alpha=alpha,
    )


def compute_freeze(repo_root: Path) -> dict[str, Any]:
    """Reproduce the frozen surfaces, verify identity, and compute frozen forecasts."""
    manifest_path = repo_root / MANIFEST_PATH
    training_path = repo_root / TRAINING_PATH
    gate_path = repo_root / GATE_PATH
    holdout_path = repo_root / HOLDOUT_PATH
    slice_path = repo_root / NMD0002_SLICE_PATH

    targets, manifest_payload = load_manifest_targets(manifest_path)
    screens = _committed_identity_screens(
        training_path=training_path,
        holdout_path=holdout_path,
        nmd0002_slice_path=slice_path,
    )
    surviving, dropped = reverify_source_state(targets, manifest_payload, screens)

    # Committed published anchors for the frozen-surface identity checks.
    result_0025_metrics = json.loads(
        (repo_root / RESULT_0025_METRICS_PATH).read_text(encoding="utf-8")
    )
    agent_run_0078_metrics = json.loads(
        (repo_root / AGENT_RUN_0078_METRICS_PATH).read_text(encoding="utf-8")
    )

    # --- Frozen liquid-drop baseline of record (residual reference). ---------
    gate = _load_yaml(gate_path)
    coefficients = _frozen_baseline_coefficients(gate)

    dataset = load_nuclear_mass_dataset(training_path)
    entries = sorted(
        dataset.entries, key=lambda entry: (entry.A, entry.Z, entry.N, entry.nuclide_id)
    )
    holdout_payload = load_post_ame2020_holdout_dataset(holdout_path)
    holdout_rows = [
        row for row in holdout_payload["entries"] if bool(row["included_in_time_split_holdout"])
    ]
    z_train, n_train, residual_train = _training_residuals(entries, coefficients)
    holdout = _holdout_arrays(holdout_rows, coefficients)

    baseline_holdout_mae = round(float(np.mean(np.abs(holdout["baseline_residual"]))), 6)
    _require_equal(
        "frozen_liquid_drop_baseline_holdout_mae_mev",
        baseline_holdout_mae,
        float(
            result_0025_metrics["extrapolation"]["frozen_baseline_holdout"]["mae_mev"]
        ),
    )

    # --- Frozen NMD-0003 residual GP (point estimator). -----------------------
    gp_fit = fit_residual_gp(z_train, n_train, residual_train)
    committed_hp = result_0025_metrics["gp_model"]["fitted_hyperparameters"]
    _require_equal("gp_sigma_f_mev", round(gp_fit.sigma_f, 6), float(committed_hp["sigma_f_mev"]))
    _require_equal(
        "gp_length_scale_standardized",
        round(gp_fit.length_scale, 6),
        float(committed_hp["length_scale_standardized"]),
    )
    _require_equal("gp_sigma_n_mev", round(gp_fit.sigma_n, 6), float(committed_hp["sigma_n_mev"]))
    _require_equal(
        "gp_log_marginal_likelihood",
        round(gp_fit.log_marginal_likelihood, 6),
        float(committed_hp["log_marginal_likelihood"]),
    )
    holdout_gp_mean, _unused_sigma = gp_fit.predict(holdout["Z"], holdout["N"])
    gp_holdout_mae = round(
        float(np.mean(np.abs(holdout["baseline_residual"] - holdout_gp_mean))), 6
    )
    _require_equal(
        "gp_corrected_holdout_mae_mev",
        gp_holdout_mae,
        float(result_0025_metrics["extrapolation"]["gp_corrected_holdout"]["mae_mev"]),
    )

    # --- smooth_a_gp predeclared control. -------------------------------------
    smooth_fit = fit_smooth_a_gp(z_train, n_train, residual_train)
    smooth_holdout_mean = smooth_fit.predict_mean(holdout["Z"] + holdout["N"])
    smooth_holdout_mae = round(
        float(np.mean(np.abs(holdout["baseline_residual"] - smooth_holdout_mean))), 6
    )
    _require_equal(
        "smooth_a_gp_holdout_mae_mev",
        smooth_holdout_mae,
        float(result_0025_metrics["controls"]["smooth_a_gp"]["corrected"]["mae_mev"]),
    )

    # --- DZ10 published-equation variant v2. -----------------------------------
    # The frozen comparator vector is the committed AGENT-RUN-0078 coefficient
    # record itself (OLS fit on the committed NMD-0003 training rows in the
    # paper's N,Z >= 8 domain, published at 12-decimal rounding), so the frozen
    # forecasts are a deterministic function of committed bytes and the
    # committed closed-form equation only. A freeze-time deterministic refit
    # must still reproduce that committed vector to within last-ulp lstsq
    # variance (<= 2e-12 per coefficient); the published holdout MAE identity
    # check below stays exact.
    dz10_coefficients = {
        name: float(agent_run_0078_metrics["coefficients"][name]) for name in FEATURE_NAMES
    }
    fit_entries = [entry for entry in entries if _within_dz10_domain(entry.Z, entry.N)]
    refit_dz10 = fit_duflo_zuker_published_variant_coefficients(fit_entries)
    for name in FEATURE_NAMES:
        refit_value = round(refit_dz10[name], 12)
        committed_value = dz10_coefficients[name]
        if abs(refit_value - committed_value) > 2e-12:
            raise FreezeBlockedError(
                "FREEZE_BLOCKED: frozen-surface identity check failed for "
                f"dz10_coefficient_{name}: deterministic refit {refit_value!r} is "
                f"not within last-ulp tolerance of committed {committed_value!r}."
            )
    dz_holdout_rows = [
        row
        for row in _post_ame2020_rows(holdout_path)
        if _within_dz10_domain(int(row["Z"]), int(row["N"]))
    ]
    dz10_holdout = _holdout_metrics(dz_holdout_rows, dz10_coefficients)
    _require_equal(
        "dz10_published_variant_holdout_mae_mev",
        float(dz10_holdout["mae_mev"]),
        float(agent_run_0078_metrics["surfaces"]["post_ame2020_holdout"]["mae_mev"]),
    )

    # --- Frozen point forecasts over the surviving targets. --------------------
    for target in surviving:
        if not _within_dz10_domain(target.z, target.n):
            raise FreezeBlockedError(
                "FREEZE_BLOCKED: surviving target "
                f"{target.nuclide_id} is outside the DZ10 N,Z >= 8 fit domain; "
                "the comparator set cannot cover the full surviving target set."
            )

    z_eval = np.array([target.z for target in surviving], dtype=float)
    n_eval = np.array([target.n for target in surviving], dtype=float)
    baseline_eval = np.array(
        [
            semi_empirical_binding_energy(z=target.z, n=target.n, coefficients=coefficients)
            for target in surviving
        ],
        dtype=float,
    )
    gp_mean_eval, _discarded_sigma = gp_fit.predict(z_eval, n_eval)
    # Point-only freeze: the posterior standard deviation returned above is
    # intentionally discarded and never recorded anywhere.
    smooth_mean_eval = smooth_fit.predict_mean(z_eval + n_eval)

    forecasts: dict[str, list[float]] = {
        "gp": [round(float(value), 6) for value in baseline_eval + gp_mean_eval],
        "dz10": [
            round(
                predict_duflo_zuker_binding_energy(
                    z=target.z, n=target.n, coefficients=dz10_coefficients
                ),
                6,
            )
            for target in surviving
        ],
        "liquid_drop": [round(float(value), 6) for value in baseline_eval],
        "smooth_a_gp": [round(float(value), 6) for value in baseline_eval + smooth_mean_eval],
    }

    input_hashes = {
        path.as_posix(): _sha256(repo_root / path)
        for path in (
            MANIFEST_PATH,
            TRAINING_PATH,
            GATE_PATH,
            HOLDOUT_PATH,
            NMD0002_SLICE_PATH,
            RESULT_0025_METRICS_PATH,
            AGENT_RUN_0078_METRICS_PATH,
        )
    }

    return {
        "surviving": surviving,
        "dropped": dropped,
        "manifest_target_count": len(targets),
        "forecasts": forecasts,
        "input_hashes": input_hashes,
        "identity_checks": {
            "frozen_liquid_drop_baseline_holdout_mae_mev": baseline_holdout_mae,
            "gp_corrected_holdout_mae_mev": gp_holdout_mae,
            "smooth_a_gp_holdout_mae_mev": smooth_holdout_mae,
            "dz10_published_variant_holdout_mae_mev": float(dz10_holdout["mae_mev"]),
            "gp_fitted_hyperparameters": {
                "sigma_f_mev": round(gp_fit.sigma_f, 6),
                "length_scale_standardized": round(gp_fit.length_scale, 6),
                "sigma_n_mev": round(gp_fit.sigma_n, 6),
                "log_marginal_likelihood": round(gp_fit.log_marginal_likelihood, 6),
            },
            "dz10_coefficients": dict(dz10_coefficients),
            "dz10_refit_max_abs_deviation": max(
                abs(round(refit_dz10[name], 12) - dz10_coefficients[name])
                for name in FEATURE_NAMES
            ),
            "frozen_baseline_id": FROZEN_BASELINE_ID,
            "frozen_baseline_coefficients": coefficients.to_dict(),
            "training_row_count": len(entries),
            "holdout_primary_row_count": len(holdout_rows),
        },
    }


# --------------------------------------------------------------------------- #
# PRED entry packaging (Gate A fields inside the committed schema)
# --------------------------------------------------------------------------- #


def _pinned_command(source_commit: str, registered_at: str) -> str:
    return (
        "python3 scripts/freeze_nmd0003_tier1_point_only_frontier.py "
        f"--source-commit {source_commit} --registered-at {registered_at} "
        "--output-dir prediction_registry/nuclear_masses"
    )


def _hash_lines(input_hashes: dict[str, str]) -> str:
    return "; ".join(f"sha256({path})={digest}" for path, digest in sorted(input_hashes.items()))


def _model_specs(freeze: dict[str, Any]) -> dict[str, dict[str, str]]:
    checks = freeze["identity_checks"]
    gp_hp = checks["gp_fitted_hyperparameters"]
    dz10 = checks["dz10_coefficients"]
    baseline = checks["frozen_baseline_coefficients"]
    return {
        "gp": {
            "model_id": "RESULT-0025::model_nmd0003_residual_gp_zn_rbf",
            "source_path": RESULT_0025_PATH.as_posix(),
            "code_reference": "physics_lab/engines/nmd0003_residual_gp.py",
            "engine_version": GP_ENGINE_VERSION,
            "title": (
                "NMD-0003 tier-1 point-only frontier freeze: frozen residual-GP "
                "posterior-mean forecasts (no interval)"
            ),
            "frozen_note": (
                "Frozen NMD-0003 residual GP (model_nmd0003_residual_gp_zn_rbf) as "
                "published in RESULT-0025: single RBF GP on standardized [Z, N] "
                "residuals over the frozen liquid-drop audit baseline "
                f"{FROZEN_BASELINE_ID} (coefficients {baseline}). Deterministically "
                "refit from committed inputs with no re-fit policy change, no "
                "hyperparameter retune, and no baseline change; reproduced "
                f"hyperparameters {gp_hp} matched RESULT-0025 exactly, and the "
                "reproduced holdout MAEs matched RESULT-0025 exactly (baseline "
                "2.979273 MeV, GP-corrected 0.462129 MeV). Payload freezes the GP "
                "posterior MEAN per target only: the posterior standard deviation "
                "and every derived interval multiplier are excluded as the "
                "miscalibrated quantity (TASK-0899)."
            ),
        },
        "dz10": {
            "model_id": "AGENT-RUN-0078::dz10_published_equation_variant",
            "source_path": AGENT_RUN_0078_METRICS_PATH.as_posix(),
            "code_reference": "physics_lab/engines/nmd0003_duflo_zuker_baseline.py",
            "engine_version": DZ10_ENGINE_VERSION,
            "title": (
                "NMD-0003 tier-1 point-only frontier freeze: DZ10 published-equation "
                "variant v2 frozen comparator forecasts"
            ),
            "frozen_note": (
                "DZ10 published-equation variant "
                f"({DZ10_ENGINE_VERSION}; arXiv:0912.0882 ten-term equations, not an "
                "archival AMDC code parity run). The frozen coefficient vector is "
                "pinned verbatim from the committed AGENT-RUN-0078 metrics "
                f"({dz10}; ordinary-least-squares fit on the committed NMD-0003 "
                "training rows in the paper's N,Z >= 8 domain), so the frozen "
                "forecasts depend only on committed bytes and the committed "
                "closed-form equation. A freeze-time deterministic refit "
                "reproduced the committed vector within 2e-12 per coefficient "
                "(last-ulp lstsq variance), and the frozen vector reproduced the "
                "committed post-AME2020 holdout MAE 1.256383 MeV exactly. Frozen "
                "comparator central values only; no uncertainty field."
            ),
        },
        "liquid_drop": {
            "model_id": f"{FROZEN_BASELINE_ID}::frozen_liquid_drop_baseline_of_record",
            "source_path": GATE_PATH.as_posix(),
            "code_reference": "physics_lab/engines/nuclear_mass_baselines.py",
            "engine_version": GP_ENGINE_VERSION,
            "title": (
                "NMD-0003 tier-1 point-only frontier freeze: frozen liquid-drop "
                "baseline-of-record comparator forecasts"
            ),
            "frozen_note": (
                "Frozen liquid-drop baseline of record: the five-coefficient "
                f"single-vector OLS audit baseline {FROZEN_BASELINE_ID} "
                f"(coefficients {baseline}) recorded in the committed NMD-0003 "
                "stratified baseline gate. This is the null-of-record the GP "
                "residual correction is layered on (post-AME2020 holdout MAE "
                "2.979273 MeV per RESULT-0025; reproduced exactly at freeze time). "
                "The approved packet cites this comparator's lineage as 'RESULT-0012 "
                "(results/EXP-0012/RUN-0001/result.yaml)'; the committed file at "
                "that path is RESULT-0015, the origin of the inherited liquid-drop "
                "family, and the operative frozen coefficients are the gate-file "
                f"{FROZEN_BASELINE_ID} values above (see the freeze review note). "
                "Frozen comparator central values only; no uncertainty field."
            ),
        },
        "smooth_a_gp": {
            "model_id": "RESULT-0025::smooth_a_gp_predeclared_control",
            "source_path": RESULT_0025_PATH.as_posix(),
            "code_reference": "physics_lab/engines/nmd0003_residual_gp.py",
            "engine_version": GP_ENGINE_VERSION,
            "title": (
                "NMD-0003 tier-1 point-only frontier freeze: smooth_a_gp predeclared-"
                "control comparator forecasts"
            ),
            "frozen_note": (
                "smooth_a_gp predeclared control from the RESULT-0025 survival test: "
                "a 1-D GP on a smooth function of mass number A only (no Z, N "
                "locality) fit on the same frozen liquid-drop baseline residuals "
                "over the committed NMD-0003 training rows, refit deterministically "
                "with the identical initialisation, bounds, optimizer, and linear "
                "algebra as the committed engine control; the reproduced post-"
                "AME2020 holdout MAE matched the committed 2.331441 MeV exactly. It "
                "was the best predeclared control in RESULT-0025 and is frozen so "
                "the reveal can score whether frontier structure matters beyond a "
                "smooth global trend. Frozen comparator central values only; no "
                "uncertainty field."
            ),
        },
    }


def build_pred_entries(
    freeze: dict[str, Any],
    *,
    source_commit: str,
    registered_at: str,
) -> dict[str, dict[str, Any]]:
    """Assemble the four tier-1 point-only PRED payloads (schema-exact)."""
    surviving: list[FrontierTarget] = freeze["surviving"]
    dropped: list[dict[str, Any]] = freeze["dropped"]
    forecasts = freeze["forecasts"]
    specs = _model_specs(freeze)
    pinned_command = _pinned_command(source_commit, registered_at)
    hash_note = _hash_lines(freeze["input_hashes"])
    dropped_summary = (
        f"{len(surviving)} of {freeze['manifest_target_count']} manifest targets survived "
        f"freeze-time source-state re-verification; {len(dropped)} dropped"
    )
    if dropped:
        dropped_ids = ", ".join(str(row["nuclide_id"]) for row in dropped)
        dropped_summary += f" ({dropped_ids}; recorded in the freeze review note, not replaced)"
    dropped_summary += "."

    entries: dict[str, dict[str, Any]] = {}
    for model_key, prediction_id in PREDICTION_IDS.items():
        spec = specs[model_key]
        target_rows = [
            {
                "nuclide_id": target.nuclide_id,
                "Z": target.z,
                "N": target.n,
                "A": target.a,
                "predicted_value_mev": forecasts[model_key][index],
                "uncertainty_mev": None,
                "confidence_note": (
                    "Tier-1 point-only frozen central value (binding energy, MeV) "
                    f"from {spec['model_id']} for {TARGET_SET_LABEL} "
                    f"({target.region_id}). No posterior standard deviation, "
                    "interval, coverage, or pre-reveal confidence ranking is "
                    "recorded or claimed (TASK-0899 calibration failure)."
                ),
            }
            for index, target in enumerate(surviving)
        ]
        entries[prediction_id] = {
            "prediction_id": prediction_id,
            "title": spec["title"],
            "registry_status": "REGISTERED",
            "campaign_profile_id": "nuclear-mass-surface",
            "task_id": TASK_ID,
            "evidence_class": "prospective_prediction_registry",
            "freeze_tier": FREEZE_TIER,
            "claim_ceiling": (
                "Tier-1 point-only prospective registration under the maintainer-"
                "approved two-tier amendment (TASK-0929 packet, Option A, "
                "2026-07-05): frozen central-value forecasts only; no claim, "
                "canonical result, accepted knowledge, reveal score, or success "
                "verdict before later maintainer-reviewed comparison; no interval "
                "or uncertainty claim (TASK-0899 calibration failed); TASK-0827 "
                "remains blocked as the interval-bearing freeze."
            ),
            "registered_by": {
                "contributor_id": "gladunrv",
                "agent_id": "claude",
            },
            "registered_at_utc": registered_at,
            "source_state": {
                "git_commit": source_commit,
                "model_reference": {
                    "model_id": spec["model_id"],
                    "source_path": spec["source_path"],
                    "frozen_parameters_note": (
                        f"{spec['frozen_note']} code_reference: "
                        f"{spec['code_reference']}; engine_version: "
                        f"{spec['engine_version']}; pinned freeze command: "
                        f"{pinned_command}; target set: {MANIFEST_ID} "
                        f"({MANIFEST_PATH.as_posix()})."
                    ),
                },
                "baseline_reference": {
                    "result_id": "RESULT-0015",
                    "source_path": RESULT_0015_PATH.as_posix(),
                },
                "training_data_references": [
                    TRAINING_PATH.as_posix(),
                    GATE_PATH.as_posix(),
                ],
                "holdout_protocol_references": list(HOLDOUT_PROTOCOL_REFERENCES),
                "live_external_fetch_allowed": False,
                "source_data_state_note": (
                    "Registered from committed repository state at git commit "
                    f"{source_commit} under the maintainer-approved tier-1 point-"
                    "only freeze (TASK-0929 packet, Option A). Freeze-time no-peek "
                    "source-state re-verification per "
                    "docs/nuclear-prediction-reveal-protocol.md screened every "
                    f"{MANIFEST_ID} target identity against the committed training, "
                    "post-AME2020 holdout, and NMD-0002 slice files: "
                    f"{dropped_summary} No live external measurement source was "
                    "fetched, revealed, scored, or compared, and no committed "
                    "measured value exists in-repo for any surviving target. "
                    f"Input file hashes: {hash_note}"
                ),
            },
            "target_set": {
                "label": TARGET_SET_LABEL,
                "quantity": "binding_energy_mev",
                "unit": "MeV",
                "target_nuclides": target_rows,
            },
            "uncertainty_semantics": {
                "type": "point_estimate_only",
                "note": (
                    "Tier-1 point-only freeze: every uncertainty_mev is "
                    "intentionally null. The NMD-0003 predictive-uncertainty "
                    "calibration failed the TASK-0899 no-peek audit, so no "
                    "posterior standard deviation, interval multiplier, or derived "
                    "uncertainty field is frozen, recorded, or claimed anywhere in "
                    "this payload."
                ),
            },
            "reveal_conditions": {
                "reveal_trigger": (
                    "The next AME/NUBASE-class evaluation published after this "
                    "registration, or a qualifying flagged Penning-trap / storage-"
                    "ring measurement subset in a watched frontier region, admitted "
                    "under docs/nuclear-prediction-reveal-protocol.md with its own "
                    "source manifest, checksum record, registry snapshot, and "
                    "no-peek audit by a separate maintainer-reviewed reveal task."
                ),
                "comparison_data_reference": (
                    "Future pinned source manifest per docs/nuclear-prediction-"
                    "reveal-protocol.md and docs/nuclear-reveal-source-readiness-"
                    "checklist.md. Tier-1 reveal metrics are MAE (MeV) and rank "
                    "against the frozen baseline set (PRED-0069, PRED-0070, "
                    "PRED-0071, PRED-0072) ONLY, per region and pooled; no interval "
                    "coverage, sharpness, or calibration metric is in scope. If the "
                    "pinned source reports mass excess or atomic mass, the "
                    "conversion to binding energy must be the deterministic "
                    "committed convention in physics_lab/engines/nuclear_masses.py "
                    "and be documented by the reveal task."
                ),
                "reveal_owner": "maintainer or maintainer-authorized review agent",
                "no_peek_rule": (
                    "Do not alter model family, frozen parameters, target nuclides, "
                    "prediction values, source commit, or reveal rule after later "
                    "measurements become visible. Later comparison must be a "
                    "separate reviewed reveal task and may reveal only eligible "
                    "measured subsets; unrevealed targets stay unchanged under "
                    "partial reveal. Any future tier-2 upgrade adds intervals as an "
                    "additive amendment bound to these already-frozen central "
                    "values, only after fresh-surface calibration validation per "
                    "the TASK-0925 contract, without re-freezing or re-timing the "
                    "points."
                ),
            },
            "limitations": [
                MANDATORY_CAVEAT,
                (
                    "Prospective registry entry only; not a claim, result package, "
                    "success verdict, or accepted knowledge; scored at a future "
                    "reveal by MAE and rank against the frozen baselines only."
                ),
                DISJOINTNESS_REQUIREMENT,
                (
                    "Freeze-time source-state screen ledger: " + dropped_summary + " "
                    "The screen covers the committed in-repo files only; it is not "
                    "a positive claim that any target is unmeasured in the wider "
                    "literature."
                ),
                (
                    "Scope inherited from RESULT-0025: one frozen NMD-0003 residual "
                    "surface over one frozen liquid-drop audit baseline; a "
                    "different baseline or model class would shift the residual "
                    "surface. The comparator set is frozen for rank scoring only."
                ),
                (
                    "No live external measurement source was fetched, revealed, "
                    "scored, or compared during registration."
                ),
            ],
            "review_boundary": {
                "retrospective_equivalence_forbidden": True,
                "pre_reveal_claim_promotion_allowed": False,
                "post_reveal_claim_promotion_requires_review": True,
                "canonical_result_allowed_pre_reveal": False,
            },
        }
    return entries


# --------------------------------------------------------------------------- #
# Output writing
# --------------------------------------------------------------------------- #


def write_outputs(
    entries: dict[str, dict[str, Any]],
    freeze: dict[str, Any],
    *,
    output_dir: Path,
    summary_out: Path | None,
    source_commit: str,
    registered_at: str,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    for prediction_id, payload in entries.items():
        path = output_dir / f"{prediction_id}.yaml"
        path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=False, width=96),
            encoding="utf-8",
        )

    surviving: list[FrontierTarget] = freeze["surviving"]
    summary = {
        "task_id": TASK_ID,
        "freeze_tier": FREEZE_TIER,
        "freeze_outcome": "EXECUTED",
        "source_commit": source_commit,
        "registered_at_utc": registered_at,
        "target_manifest": {
            "manifest_id": MANIFEST_ID,
            "path": MANIFEST_PATH.as_posix(),
            "manifest_target_count": freeze["manifest_target_count"],
            "surviving_target_count": len(surviving),
            "dropped_target_count": len(freeze["dropped"]),
        },
        "dropped_target_ledger": freeze["dropped"],
        "prediction_entries": {
            model_key: prediction_id for model_key, prediction_id in PREDICTION_IDS.items()
        },
        "identity_checks": freeze["identity_checks"],
        "input_file_hashes": freeze["input_hashes"],
        "pinned_command": _pinned_command(source_commit, registered_at),
        "per_target_frozen_values_mev": [
            {
                "nuclide_id": target.nuclide_id,
                "Z": target.z,
                "N": target.n,
                "A": target.a,
                "region_id": target.region_id,
                "gp_posterior_mean": freeze["forecasts"]["gp"][index],
                "dz10_published_variant": freeze["forecasts"]["dz10"][index],
                "frozen_liquid_drop": freeze["forecasts"]["liquid_drop"][index],
                "smooth_a_gp": freeze["forecasts"]["smooth_a_gp"][index],
            }
            for index, target in enumerate(surviving)
        ],
    }
    summary_text = yaml.safe_dump(summary, sort_keys=False, allow_unicode=False, width=96)
    if summary_out is not None:
        summary_out.parent.mkdir(parents=True, exist_ok=True)
        summary_out.write_text(summary_text, encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-commit",
        required=True,
        help="Git commit of the committed input state the freeze reproduces from.",
    )
    parser.add_argument(
        "--registered-at",
        required=True,
        help="Frozen registration timestamp (UTC, e.g. 2026-07-05T19:35:00Z).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory that receives the four PRED-*.yaml tier-1 entries.",
    )
    parser.add_argument(
        "--summary-out",
        type=Path,
        default=None,
        help="Optional path for the YAML freeze summary (per-target value table).",
    )
    args = parser.parse_args(argv)

    try:
        freeze = compute_freeze(REPO_ROOT)
        entries = build_pred_entries(
            freeze,
            source_commit=args.source_commit,
            registered_at=args.registered_at,
        )
        write_outputs(
            entries,
            freeze,
            output_dir=args.output_dir,
            summary_out=args.summary_out,
            source_commit=args.source_commit,
            registered_at=args.registered_at,
        )
    except FreezeBlockedError as error:
        print(str(error), file=sys.stderr)
        return 2

    surviving = freeze["surviving"]
    dropped = freeze["dropped"]
    print(
        "FREEZE_EXECUTED: "
        f"{len(surviving)} surviving targets, {len(dropped)} dropped; wrote "
        + ", ".join(sorted(PREDICTION_IDS.values()))
        + f" to {args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
