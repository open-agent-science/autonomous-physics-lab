"""TASK-0288 nuclear shell-axis adversarial stress scout.

This sandbox-only stress scout re-evaluates the strongest post-PRED-0062 shell
axis sandbox signals (SHELL-SCOUT-003 proton-only Gaussian, SHELL-SCOUT-005
proton x neutron product, SHELL-SCOUT-002 neutron-only overlap diagnostic)
against the frozen RESULT-0015 fitted semi-empirical baseline using only
repository-pinned data, and adds adversarial controls (sign-inverted, shuffled
shell-distance, and a near-null sanity control). It also computes a
repeated-target-pressure block that records whether overrepresented registry
targets (Ni-76, Ca-55, Ga-85, Zn-80) appear in the post-AME2020 holdout, and
whether their isotope-chain neighbors do. The scout does not fetch live
measurements, write prediction registry entries, mutate canonical results,
update claims, or promote sandbox outcomes.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.engines.nuclear_mass_baselines import (  # noqa: E402
    MAGIC_NUMBERS,
    SemiEmpiricalCoefficients,
    evaluate_baseline,
    semi_empirical_binding_energy,
)
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset  # noqa: E402


NMD_PATH = REPO_ROOT / "data" / "nuclear_masses" / "nmd-0002-curated-measured-slice.yaml"
POST_AME_PATH = REPO_ROOT / "data" / "nuclear_masses" / "post_ame2020_holdout.yaml"
RESULT_PATH = REPO_ROOT / "results" / "EXP-0012" / "RUN-0001" / "result.yaml"

AGENT_RUN_ID = "AGENT-RUN-0016"
TASK_ID = "TASK-0288"

SHELL_SIGMA = 2.0
SHUFFLE_OFFSET = 5

# Registry repeated-target counts from
# docs/reviews/nuclear-prediction-registry-coverage-audit.md.
REGISTRY_REPEAT_TARGETS: tuple[dict[str, Any], ...] = (
    {"nuclide_id": "Ni-76", "Z": 28, "A": 76, "registry_entry_count": 18},
    {"nuclide_id": "Ca-55", "Z": 20, "A": 55, "registry_entry_count": 14},
    {"nuclide_id": "Ga-85", "Z": 31, "A": 85, "registry_entry_count": 14},
    {"nuclide_id": "Zn-80", "Z": 30, "A": 80, "registry_entry_count": 14},
)


EXECUTED_CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "candidate_id": "STRESS-SHELL-001",
        "name": "Proton-axis Gaussian shell proximity (re-eval of SHELL-SCOUT-003)",
        "formula": "r_corr = beta_z * s_z2",
        "feature_names": ("s_z2",),
        "complexity": 1,
        "fit_mode": "lstsq",
    },
    {
        "candidate_id": "STRESS-SHELL-002",
        "name": "Proton x neutron product shell proximity (re-eval of SHELL-SCOUT-005)",
        "formula": "r_corr = beta_p * (s_z2 * s_n2)",
        "feature_names": ("s_z2_times_s_n2",),
        "complexity": 1,
        "fit_mode": "lstsq",
    },
    {
        "candidate_id": "STRESS-SHELL-003",
        "name": "Neutron-axis Gaussian shell proximity overlap diagnostic (re-eval of SHELL-SCOUT-002)",
        "formula": "r_corr = beta_n * s_n2",
        "feature_names": ("s_n2",),
        "complexity": 1,
        "fit_mode": "lstsq",
    },
    {
        "candidate_id": "STRESS-SHELL-004",
        "name": "Sign-inverted proton-axis Gaussian adversarial control",
        "formula": "r_corr = -beta_z * s_z2 (beta_z fit as in STRESS-SHELL-001)",
        "feature_names": ("s_z2",),
        "complexity": 1,
        "fit_mode": "lstsq_sign_inverted",
        "sign_inverted": True,
    },
    {
        "candidate_id": "STRESS-SHELL-005",
        "name": "Shuffled proton-axis Gaussian control (cyclic-shift-5)",
        "formula": "r_corr = beta_z * s_z2_perm where row i uses (i+5) mod N feature",
        "feature_names": ("s_z2",),
        "complexity": 1,
        "fit_mode": "lstsq_shuffled",
        "shuffle_scheme": "cyclic-shift-5",
        "shuffle_seed": SHUFFLE_OFFSET,
    },
    {
        "candidate_id": "STRESS-SHELL-006",
        "name": "Near-null shell-axis sanity control",
        "formula": "r_corr = 0.0",
        "feature_names": (),
        "complexity": 0,
        "fit_mode": "fixed_zero",
        "fixed_zero_control": True,
    },
)


REJECTED_BEFORE_EXECUTION: tuple[dict[str, str], ...] = (
    {
        "candidate_id": "STRESS-SHELL-007",
        "name": "Free-sigma proton Gaussian",
        "rejection_reason": (
            "Rejected before execution because tuning sigma on an 11-row NMD-0002 "
            "residual slice adds a nonlinear free knob with high overfit risk and "
            "duplicates the fixed-sigma proton-axis probe STRESS-SHELL-001."
        ),
    },
    {
        "candidate_id": "STRESS-SHELL-008",
        "name": "Per-magic-number offsets",
        "rejection_reason": (
            "Rejected before execution because one coefficient per element of "
            "{2,8,20,28,50,82,126} introduces 7 free coefficients on an 11-row "
            "residual training slice, which inflates degrees of freedom and "
            "memorizes training shell-cluster rows."
        ),
    },
    {
        "candidate_id": "STRESS-SHELL-009",
        "name": "SHELL-SCOUT-001 additive form re-test",
        "rejection_reason": (
            "Rejected before execution because SHELL-SCOUT-001 "
            "(beta_z*s_z2 + beta_n*s_n2) is already documented as OVERFITTED in "
            "docs/reviews/nuclear-scout-lane-synthesis-after-pred-0062.md, so "
            "re-running it would be duplicate-search rather than adversarial stress."
        ),
    },
)


def nearest_magic_distance(value: int) -> int:
    """Distance to the nearest canonical magic number."""
    return min(abs(value - magic) for magic in MAGIC_NUMBERS)


def shell_gaussian(value: int, *, sigma: float = SHELL_SIGMA) -> float:
    """Continuous proximity to the nearest magic number."""
    distance = nearest_magic_distance(value)
    return float(math.exp(-(distance * distance) / (2.0 * sigma * sigma)))


def feature_vector(feature_names: tuple[str, ...], *, z: int, n: int) -> tuple[float, ...]:
    """Return feature values for one target row."""
    sz2 = shell_gaussian(z)
    sn2 = shell_gaussian(n)
    values = {
        "s_z2": sz2,
        "s_n2": sn2,
        "s_z2_times_s_n2": sz2 * sn2,
    }
    return tuple(values[name] for name in feature_names)


def load_frozen_baseline_coefficients() -> SemiEmpiricalCoefficients:
    """Load RESULT-0015 fitted semi-empirical coefficients."""
    with RESULT_PATH.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    for score in payload["scores"]:
        if score["model_id"] == "model_fitted_semi_empirical":
            coeffs = score["coefficients"]
            return SemiEmpiricalCoefficients(
                volume=float(coeffs["volume"]),
                surface=float(coeffs["surface"]),
                coulomb=float(coeffs["coulomb"]),
                asymmetry=float(coeffs["asymmetry"]),
                pairing=float(coeffs["pairing"]),
            )
    raise RuntimeError("RESULT-0015 fitted semi-empirical coefficients not found")


def chain_neighbor_target(z: int, a: int) -> str | None:
    """Return the registry target id whose chain neighborhood (same Z, |A-A_target| <= 2) contains (Z, A)."""
    for target in REGISTRY_REPEAT_TARGETS:
        if int(target["Z"]) == int(z) and abs(int(target["A"]) - int(a)) <= 2:
            return str(target["nuclide_id"])
    return None


def subset_ids(*, z: int, n: int, a: int, nuclide_id: str, was_extrapolated: bool) -> tuple[str, ...]:
    """Subset labels used for shell-axis stress diagnostics."""
    ids = ["primary"]
    ids.append("ame2020_extrapolated_comparison" if was_extrapolated else "ame2020_measured_comparison")
    if z in MAGIC_NUMBERS or n in MAGIC_NUMBERS:
        ids.append("magic_any")
    if z in MAGIC_NUMBERS and n in MAGIC_NUMBERS:
        ids.append("double_magic")
    if z in MAGIC_NUMBERS:
        ids.append("magic_z")
    if n in MAGIC_NUMBERS:
        ids.append("magic_n")
    if nearest_magic_distance(z) <= 2 or nearest_magic_distance(n) <= 2:
        ids.append("near_magic")
    if a >= 100:
        ids.append("heavy_a_ge_100")
    if 50 <= a <= 150:
        ids.append("mid_mass")
    if a < 50:
        ids.append("light_a_lt_50")
    asymmetry = float(n - z) / float(a) if a > 0 else 0.0
    if asymmetry >= 0.25:
        ids.append("neutron_rich_high")
    repeat_target_ids = {str(target["nuclide_id"]) for target in REGISTRY_REPEAT_TARGETS}
    if nuclide_id in repeat_target_ids:
        ids.append("registry_repeat_target")
    if chain_neighbor_target(z=z, a=a) is not None:
        ids.append("registry_repeat_chain_neighbor")
    return tuple(ids)


def summarize_errors(errors: list[float]) -> dict[str, float | int | None]:
    """Summarize signed residuals."""
    if not errors:
        return {
            "count": 0,
            "mae_mev": None,
            "rmse_mev": None,
            "mean_error_mev": None,
            "max_abs_error_mev": None,
        }
    abs_errors = [abs(error) for error in errors]
    return {
        "count": len(errors),
        "mae_mev": float(sum(abs_errors) / len(abs_errors)),
        "rmse_mev": float(math.sqrt(sum(error * error for error in errors) / len(errors))),
        "mean_error_mev": float(sum(errors) / len(errors)),
        "max_abs_error_mev": float(max(abs_errors)),
    }


def baseline_post_ame2020_rows(
    coefficients: SemiEmpiricalCoefficients,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build baseline residual rows and subset metrics for the pinned post-AME2020 holdout."""
    with POST_AME_PATH.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    rows = [row for row in payload["entries"] if bool(row["included_in_time_split_holdout"])]
    per_row: list[dict[str, Any]] = []
    subset_errors: dict[str, list[float]] = {}
    for row in rows:
        z, n, a = int(row["Z"]), int(row["N"]), int(row["A"])
        predicted = semi_empirical_binding_energy(z=z, n=n, coefficients=coefficients)
        observed = float(row["new_measurement"]["value_mev"])
        residual = observed - predicted
        nuclide_id = str(row["nuclide_id"])
        was_extrapolated = bool(row["ame2020_comparison"]["was_extrapolated"])
        item = {
            "row_id": row["row_id"],
            "nuclide_id": nuclide_id,
            "Z": z,
            "N": n,
            "A": a,
            "observed_mev": observed,
            "baseline_predicted_mev": predicted,
            "baseline_residual_mev": residual,
            "was_extrapolated": was_extrapolated,
        }
        per_row.append(item)
        for subset_id in subset_ids(
            z=z,
            n=n,
            a=a,
            nuclide_id=nuclide_id,
            was_extrapolated=was_extrapolated,
        ):
            subset_errors.setdefault(subset_id, []).append(residual)
    return per_row, {key: summarize_errors(value) for key, value in sorted(subset_errors.items())}


def _delta_mae(candidate: dict[str, Any] | None, baseline: dict[str, Any] | None) -> float | None:
    if not candidate or not baseline:
        return None
    if candidate.get("mae_mev") is None or baseline.get("mae_mev") is None:
        return None
    return float(candidate["mae_mev"]) - float(baseline["mae_mev"])


def frontier_contrast(deltas: dict[str, float | None]) -> float | None:
    """Return mid_mass delta minus the mean of light_a_lt_50 and heavy_a_ge_100 deltas."""
    mid = deltas.get("mid_mass")
    light = deltas.get("light_a_lt_50")
    heavy = deltas.get("heavy_a_ge_100")
    if mid is None or light is None or heavy is None:
        return None
    return float(mid) - 0.5 * (float(light) + float(heavy))


def verdict_for_candidate(
    *,
    candidate: dict[str, Any],
    delta_by_subset: dict[str, float | None],
    primary_delta: float | None,
    chain_neighbor_delta: float | None,
) -> str:
    """Conservative scout verdict for the adversarial stress lane."""
    material = 1.0e-6
    if candidate.get("fixed_zero_control"):
        return "INCONCLUSIVE"
    if primary_delta is None:
        return "INCONCLUSIVE"
    numeric_deltas = [value for value in delta_by_subset.values() if value is not None]
    worst_subset_regression = max([0.0, *numeric_deltas])
    if candidate.get("sign_inverted") and primary_delta < -material:
        return "OVERFITTED"
    if primary_delta > 0.5 or worst_subset_regression > 2.0:
        return "OVERFITTED"
    if primary_delta > 0.05:
        improving_subsets = [
            key
            for key, value in delta_by_subset.items()
            if value is not None and value < -material
        ]
        improving_counts = []
        for key in improving_subsets:
            # Skip if the subset has no count in either side (defensive).
            count = (
                candidate.get("subset_counts", {}).get(key)
                if isinstance(candidate.get("subset_counts"), dict)
                else None
            )
            improving_counts.append(count if count is not None else 0)
        if improving_subsets and all(
            (count is not None and count <= 3) for count in improving_counts
        ):
            return "OVERFITTED"
    if primary_delta < -material and worst_subset_regression <= 0.5:
        return "PARTIALLY_VALID"
    _ = chain_neighbor_delta  # Reserved for future tighter triage; preserved for documentation.
    return "INCONCLUSIVE"


def _fit_lstsq(feature_names: tuple[str, ...], training_entries: list[Any], residuals: np.ndarray) -> np.ndarray:
    train_x = np.asarray(
        [feature_vector(feature_names, z=int(entry.Z), n=int(entry.N)) for entry in training_entries],
        dtype=float,
    )
    beta, *_ = np.linalg.lstsq(train_x, residuals, rcond=None)
    return beta


def _shuffled_feature_array(
    feature_names: tuple[str, ...],
    items: list[Any],
    *,
    z_of: callable,
    n_of: callable,
    offset: int,
) -> np.ndarray:
    """Build feature array where row i is replaced by row (i+offset) mod N values."""
    count = len(items)
    rotated_indices = [(i + offset) % count for i in range(count)]
    rotated_features = [
        feature_vector(feature_names, z=int(z_of(items[idx])), n=int(n_of(items[idx])))
        for idx in rotated_indices
    ]
    return np.asarray(rotated_features, dtype=float)


def evaluate_candidate(
    candidate: dict[str, Any],
    *,
    training_entries: list[Any],
    training_residuals: np.ndarray,
    post_rows: list[dict[str, Any]],
    baseline_metrics: dict[str, Any],
    proton_only_beta: float | None,
) -> dict[str, Any]:
    """Fit and evaluate one stress-scout candidate."""
    feature_names = tuple(candidate["feature_names"])
    fit_mode = candidate.get("fit_mode", "lstsq")

    if fit_mode == "fixed_zero":
        beta = np.asarray([], dtype=float)
        applied_beta = beta
        fitted_coeffs: dict[str, float] = {}
    elif fit_mode == "lstsq":
        beta = _fit_lstsq(feature_names, training_entries, training_residuals)
        applied_beta = beta
        fitted_coeffs = {
            name: float(value) for name, value in zip(feature_names, beta)
        }
    elif fit_mode == "lstsq_sign_inverted":
        # Fit beta as in STRESS-SHELL-001, then apply the negated coefficient.
        if proton_only_beta is None:
            raise RuntimeError("STRESS-SHELL-004 requires the proton-only beta from STRESS-SHELL-001.")
        beta = np.asarray([proton_only_beta], dtype=float)
        applied_beta = np.asarray([-proton_only_beta], dtype=float)
        fitted_coeffs = {"s_z2": float(-proton_only_beta)}
    elif fit_mode == "lstsq_shuffled":
        train_x = _shuffled_feature_array(
            feature_names,
            training_entries,
            z_of=lambda entry: entry.Z,
            n_of=lambda entry: entry.N,
            offset=SHUFFLE_OFFSET,
        )
        beta, *_ = np.linalg.lstsq(train_x, training_residuals, rcond=None)
        applied_beta = beta
        fitted_coeffs = {
            name: float(value) for name, value in zip(feature_names, beta)
        }
    else:
        raise RuntimeError(f"Unknown fit_mode {fit_mode!r} for candidate {candidate['candidate_id']!r}")

    subset_errors: dict[str, list[float]] = {key: [] for key in baseline_metrics}
    per_row: list[dict[str, Any]] = []
    activation_counts = {name: 0 for name in feature_names}

    if fit_mode == "lstsq_shuffled":
        shuffled_post = _shuffled_feature_array(
            feature_names,
            post_rows,
            z_of=lambda row: row["Z"],
            n_of=lambda row: row["N"],
            offset=SHUFFLE_OFFSET,
        )

    for row_index, row in enumerate(post_rows):
        z, n, a = int(row["Z"]), int(row["N"]), int(row["A"])
        nuclide_id = str(row["nuclide_id"])
        if fit_mode == "lstsq_shuffled":
            values = tuple(float(v) for v in shuffled_post[row_index])
        else:
            values = feature_vector(feature_names, z=z, n=n)
        for name, value in zip(feature_names, values):
            if abs(value) > 0.0:
                activation_counts[name] += 1
        if fit_mode == "fixed_zero":
            correction = 0.0
        else:
            correction = float(np.asarray(values) @ applied_beta)
        predicted = float(row["baseline_predicted_mev"]) + correction
        residual = float(row["observed_mev"]) - predicted
        item = {
            "row_id": row["row_id"],
            "nuclide_id": nuclide_id,
            "Z": z,
            "N": n,
            "A": a,
            "correction_mev": correction,
            "candidate_residual_mev": residual,
            "candidate_abs_error_mev": abs(residual),
            "feature_values": {
                name: float(value) for name, value in zip(feature_names, values)
            },
        }
        per_row.append(item)
        for subset_id in subset_ids(
            z=z,
            n=n,
            a=a,
            nuclide_id=nuclide_id,
            was_extrapolated=bool(row["was_extrapolated"]),
        ):
            subset_errors.setdefault(subset_id, []).append(residual)

    metrics_by_subset = {
        key: summarize_errors(value) for key, value in sorted(subset_errors.items())
    }
    delta_by_subset = {
        key: _delta_mae(metrics_by_subset.get(key), baseline_metrics.get(key))
        for key in sorted(baseline_metrics)
    }
    numeric_deltas = [value for value in delta_by_subset.values() if value is not None]
    worst_subset_regression = max([0.0, *numeric_deltas])
    subset_counts = {
        key: int(metrics_by_subset.get(key, {}).get("count") or 0)
        for key in metrics_by_subset
    }
    primary_delta = delta_by_subset.get("primary")
    chain_neighbor_delta = delta_by_subset.get("registry_repeat_chain_neighbor")
    candidate_with_counts = dict(candidate)
    candidate_with_counts["subset_counts"] = subset_counts
    verdict = verdict_for_candidate(
        candidate=candidate_with_counts,
        delta_by_subset=delta_by_subset,
        primary_delta=primary_delta,
        chain_neighbor_delta=chain_neighbor_delta,
    )
    frontier_contrast_value = frontier_contrast(delta_by_subset)

    out = {
        "candidate_id": candidate["candidate_id"],
        "name": candidate["name"],
        "formula": candidate["formula"],
        "complexity": candidate["complexity"],
        "fit_mode": fit_mode,
        "fitted_coefficients": fitted_coeffs,
        "feature_activation_counts": activation_counts,
        "metrics_by_subset": metrics_by_subset,
        "delta_mae_by_subset_mev": delta_by_subset,
        "frontier_contrast_mev": frontier_contrast_value,
        "worst_subset_regression_mae_mev": worst_subset_regression,
        "primary_delta_mae_mev": primary_delta,
        "chain_neighbor_delta_mae_mev": chain_neighbor_delta,
        "worst_abs_error_cases": sorted(
            per_row, key=lambda entry: float(entry["candidate_abs_error_mev"]), reverse=True
        )[:5],
        "verdict": verdict,
        "limitations": [
            "Feature coefficients are fit on the 11-row NMD-0002 residual slice.",
            "Post-AME2020 evaluation uses committed retrospective rows only; it is not a reveal of new live measurements.",
            "Sub-MeV deltas are scout-triage diagnostics, not promoted claims.",
            "Verdict labels are sandbox triage signals only.",
        ],
    }
    if candidate.get("sign_inverted"):
        out["sign_inverted"] = True
    if fit_mode == "lstsq_shuffled":
        out["shuffle_scheme"] = candidate.get("shuffle_scheme", "cyclic-shift-5")
        out["shuffle_seed"] = int(candidate.get("shuffle_seed", SHUFFLE_OFFSET))
    return out


def build_repeated_target_pressure(post_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Diagnostic block summarizing how holdout rows relate to overrepresented registry targets."""
    holdout_ids = {row["nuclide_id"] for row in post_rows}
    holdout_target_overlap = {
        str(target["nuclide_id"]): bool(target["nuclide_id"] in holdout_ids)
        for target in REGISTRY_REPEAT_TARGETS
    }
    chain_neighbor_rows: list[dict[str, Any]] = []
    for row in post_rows:
        target = chain_neighbor_target(z=int(row["Z"]), a=int(row["A"]))
        if target is None:
            continue
        chain_neighbor_rows.append(
            {
                "nuclide_id": str(row["nuclide_id"]),
                "Z": int(row["Z"]),
                "N": int(row["N"]),
                "A": int(row["A"]),
                "registry_target": target,
            }
        )
    chain_neighbor_rows.sort(key=lambda entry: (entry["registry_target"], entry["A"], entry["nuclide_id"]))
    return {
        "overrepresented_registry_targets": [dict(target) for target in REGISTRY_REPEAT_TARGETS],
        "holdout_target_overlap": holdout_target_overlap,
        "holdout_chain_neighbor_rows": chain_neighbor_rows,
    }


def build_metrics() -> dict[str, Any]:
    """Build deterministic stress-scout metrics."""
    coefficients = load_frozen_baseline_coefficients()
    nmd = load_nuclear_mass_dataset(NMD_PATH)
    baseline_rows = evaluate_baseline(
        entries=nmd.entries,
        model_id="model_fitted_semi_empirical",
        coefficients=coefficients,
    )
    residuals = np.asarray([row.residual_mev for row in baseline_rows], dtype=float)
    entries_by_id = {entry.nuclide_id: entry for entry in nmd.entries}
    training_entries = [entries_by_id[row.nuclide_id] for row in baseline_rows]

    post_rows, baseline_metrics = baseline_post_ame2020_rows(coefficients)

    # Fit STRESS-SHELL-001 first so STRESS-SHELL-004 can reuse the proton-only beta.
    proton_only_beta = float(
        _fit_lstsq(("s_z2",), training_entries, residuals)[0]
    )

    executed_items: list[dict[str, Any]] = []
    for candidate in EXECUTED_CANDIDATES:
        executed_items.append(
            evaluate_candidate(
                candidate,
                training_entries=training_entries,
                training_residuals=residuals,
                post_rows=post_rows,
                baseline_metrics=baseline_metrics,
                proton_only_beta=proton_only_beta,
            )
        )

    verdict_counts: dict[str, int] = {}
    for item in executed_items:
        verdict_counts[item["verdict"]] = verdict_counts.get(item["verdict"], 0) + 1

    generated_candidates = [
        {
            "candidate_id": candidate["candidate_id"],
            "name": candidate["name"],
            "formula": candidate["formula"],
            "decision": "executed",
        }
        for candidate in EXECUTED_CANDIDATES
    ]
    generated_candidates.extend(
        {
            "candidate_id": candidate["candidate_id"],
            "name": candidate["name"],
            "decision": "rejected_before_execution",
            "rejection_reason": candidate["rejection_reason"],
        }
        for candidate in REJECTED_BEFORE_EXECUTION
    )

    repeated_target_pressure = build_repeated_target_pressure(post_rows)

    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "shell_axis_adversarial_stress_scout",
        "sandbox_only": True,
        "evidence_class": "bounded_sandbox_residual_scout",
        "live_external_fetch_allowed": False,
        "summary": {
            "generated_candidate_count": len(generated_candidates),
            "executed_candidate_count": len(EXECUTED_CANDIDATES),
            "rejected_before_execution_count": len(REJECTED_BEFORE_EXECUTION),
            "near_null_control_preserved": any(
                item["candidate_id"] == "STRESS-SHELL-006" and item["verdict"] == "INCONCLUSIVE"
                for item in executed_items
            ),
            "verdict_counts": dict(sorted(verdict_counts.items())),
            "canonical_results_changed": False,
            "canonical_claims_changed": False,
            "prediction_registry_changed": False,
            "claim_promotion_allowed": False,
        },
        "frozen_baseline": {
            "result_id": "RESULT-0015",
            "model_id": "model_fitted_semi_empirical",
            "coefficients": coefficients.to_dict(),
        },
        "datasets": {
            "training_residual_source": "data/nuclear_masses/nmd-0002-curated-measured-slice.yaml",
            "holdout_source": "data/nuclear_masses/post_ame2020_holdout.yaml",
            "holdout_row_count": len(post_rows),
        },
        "subset_definitions": {
            "primary": "all post-AME2020 holdout rows with included_in_time_split_holdout = true",
            "ame2020_measured_comparison": "ame2020_comparison.was_extrapolated == false",
            "ame2020_extrapolated_comparison": "ame2020_comparison.was_extrapolated == true",
            "magic_any": "Z in {2,8,20,28,50,82,126} OR N in {2,8,20,28,50,82,126}",
            "magic_z": "Z in {2,8,20,28,50,82,126}",
            "magic_n": "N in {2,8,20,28,50,82,126}",
            "double_magic": "Z in magic AND N in magic",
            "near_magic": "min(|Z-m|) <= 2 OR min(|N-m|) <= 2 over magic numbers",
            "heavy_a_ge_100": "A >= 100",
            "mid_mass": "50 <= A <= 150",
            "light_a_lt_50": "A < 50",
            "neutron_rich_high": "(N - Z) / A >= 0.25",
            "registry_repeat_target": "nuclide_id in {Ni-76, Ca-55, Ga-85, Zn-80}",
            "registry_repeat_chain_neighbor": (
                "same Z as one of {Ni-76, Ca-55, Ga-85, Zn-80} AND |A - registry_A| <= 2"
            ),
            "frontier_contrast": (
                "mid_mass delta MAE minus 0.5 * (light_a_lt_50 delta MAE + heavy_a_ge_100 delta MAE)"
            ),
        },
        "feature_definitions": {
            "s_z2": (
                f"exp(-d(Z)^2 / (2 * {SHELL_SIGMA}^2)) where "
                "d(Z) = min over magic numbers {2,8,20,28,50,82,126} of |Z - m|"
            ),
            "s_n2": (
                f"exp(-d(N)^2 / (2 * {SHELL_SIGMA}^2)) where "
                "d(N) = min over magic numbers {2,8,20,28,50,82,126} of |N - m|"
            ),
            "s_z2_times_s_n2": "product of s_z2 and s_n2",
            "shuffle_scheme": (
                "STRESS-SHELL-005 uses cyclic-shift-5: training row i is fit with the "
                "feature value of training row (i+5) mod 11, and holdout row i is "
                "evaluated with the feature value of holdout row (i+5) mod 295"
            ),
            "sign_inverted_scheme": (
                "STRESS-SHELL-004 fits beta_z by lstsq on training as in STRESS-SHELL-001 "
                "and then applies the correction -beta_z * s_z2 on the holdout; "
                "fitted_coefficients reports the applied (negated) sign"
            ),
        },
        "baseline_metrics_by_subset": baseline_metrics,
        "repeated_target_pressure": repeated_target_pressure,
        "generated_candidates": generated_candidates,
        "executed_items": executed_items,
        "rejected_before_execution": list(REJECTED_BEFORE_EXECUTION),
        "promotion_boundary": {
            "writes_prediction_registry": False,
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "writes_knowledge": False,
            "required_next_step": (
                "Maintainer review before any registry selection, RESULT-* artifact, "
                "claim, or knowledge update."
            ),
        },
        "limitations": [
            "Sandbox-only scout; no prediction registry, canonical result, claim, or knowledge artifact is updated.",
            "Feature coefficients are fit on the 11-row NMD-0002 residual slice.",
            "Post-AME2020 evaluation uses committed retrospective rows only and is not a live reveal.",
            "Adversarial controls (sign-inverted, shuffled, near-null) are sandbox diagnostics, not promoted claims.",
            "Rejected candidates are preserved to document overfit and duplicate-search boundaries.",
        ],
    }


def _format_delta(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value == 0.0:
        return "+0.000000"
    sign = "+" if value > 0 else "-"
    return f"{sign}{abs(value):.6f}"


def render_report(metrics: dict[str, Any]) -> str:
    """Render a markdown report mirroring the scout-001 pattern."""
    lines: list[str] = []
    lines.append("# Nuclear Shell-Axis Adversarial Stress Scout")
    lines.append("")
    lines.append(f"**Agent run:** {metrics['agent_run_id']}  ")
    lines.append(f"**Task:** {metrics['task_id']}  ")
    lines.append("**Evidence class:** bounded sandbox residual scout  ")
    lines.append("**Baseline:** `RESULT-0015::model_fitted_semi_empirical`  ")
    lines.append("**Script:** `scripts/run_nuclear_shell_axis_stress_scout.py`  ")
    lines.append(
        f"**Metrics:** `agent_runs/{metrics['agent_run_id']}/metrics.json`"
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    summary = metrics["summary"]
    lines.append(
        "This stress scout generated "
        f"{summary['generated_candidate_count']} adversarial shell-axis candidate ideas. "
        f"{summary['executed_candidate_count']} were evaluated and "
        f"{summary['rejected_before_execution_count']} were rejected before execution "
        "due to overfit, degree-of-freedom inflation, or duplicate-search risk."
    )
    lines.append("")
    lines.append("| Item | Count |")
    lines.append("| --- | ---: |")
    lines.append(f"| Generated candidates | {summary['generated_candidate_count']} |")
    lines.append(f"| Executed candidates | {summary['executed_candidate_count']} |")
    lines.append(f"| Rejected before execution | {summary['rejected_before_execution_count']} |")
    lines.append(
        f"| Near-null control preserved | {'yes' if summary['near_null_control_preserved'] else 'no'} |"
    )
    lines.append("")
    lines.append("Verdict counts:")
    lines.append("")
    lines.append("| Verdict | Count |")
    lines.append("| --- | ---: |")
    for verdict, count in sorted(summary["verdict_counts"].items()):
        lines.append(f"| `{verdict}` | {count} |")
    lines.append("")

    lines.append("## Candidate Outcomes")
    lines.append("")
    lines.append(
        "| Candidate | Feature family | Primary ΔMAE MeV | Magic Z ΔMAE MeV | Magic N ΔMAE MeV | Heavy A>=100 ΔMAE MeV | Chain-neighbor ΔMAE MeV | Verdict |"
    )
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |")
    for item in metrics["executed_items"]:
        deltas = item["delta_mae_by_subset_mev"]
        lines.append(
            "| `{cid}` | {family} | {primary} | {mz} | {mn} | {heavy} | {chain} | `{verdict}` |".format(
                cid=item["candidate_id"],
                family=item["name"],
                primary=_format_delta(deltas.get("primary")),
                mz=_format_delta(deltas.get("magic_z")),
                mn=_format_delta(deltas.get("magic_n")),
                heavy=_format_delta(deltas.get("heavy_a_ge_100")),
                chain=_format_delta(deltas.get("registry_repeat_chain_neighbor")),
                verdict=item["verdict"],
            )
        )
    lines.append("")
    lines.append("Frontier and additional subset deltas:")
    lines.append("")
    lines.append(
        "| Candidate | Mid-mass ΔMAE MeV | Light A<50 ΔMAE MeV | Heavy A>=100 ΔMAE MeV | Frontier contrast MeV | Neutron-rich (N-Z)/A>=0.25 ΔMAE MeV |"
    )
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for item in metrics["executed_items"]:
        deltas = item["delta_mae_by_subset_mev"]
        lines.append(
            "| `{cid}` | {mid} | {light} | {heavy} | {fc} | {nr} |".format(
                cid=item["candidate_id"],
                mid=_format_delta(deltas.get("mid_mass")),
                light=_format_delta(deltas.get("light_a_lt_50")),
                heavy=_format_delta(deltas.get("heavy_a_ge_100")),
                fc=_format_delta(item.get("frontier_contrast_mev")),
                nr=_format_delta(deltas.get("neutron_rich_high")),
            )
        )
    lines.append("")
    lines.append(
        "Negative deltas mean lower retrospective MAE than the frozen baseline on "
        "that subset. Positive deltas mean regression."
    )
    lines.append("")

    pressure = metrics["repeated_target_pressure"]
    lines.append("## Repeated-Target Pressure")
    lines.append("")
    lines.append("Overrepresented registry targets and whether they appear in the holdout:")
    lines.append("")
    lines.append("| Target | Z | A | Registry entry count | In holdout |")
    lines.append("| --- | ---: | ---: | ---: | --- |")
    for target in pressure["overrepresented_registry_targets"]:
        nuclide_id = str(target["nuclide_id"])
        present = pressure["holdout_target_overlap"].get(nuclide_id, False)
        lines.append(
            f"| `{nuclide_id}` | {target['Z']} | {target['A']} | "
            f"{target['registry_entry_count']} | {'yes' if present else 'no'} |"
        )
    lines.append("")
    lines.append("Chain-neighbor holdout rows (same Z, |A - registry_A| <= 2):")
    lines.append("")
    lines.append("| Nuclide | Z | N | A | Registry target |")
    lines.append("| --- | ---: | ---: | ---: | --- |")
    for row in pressure["holdout_chain_neighbor_rows"]:
        lines.append(
            f"| `{row['nuclide_id']}` | {row['Z']} | {row['N']} | {row['A']} | `{row['registry_target']}` |"
        )
    lines.append("")

    lines.append("## Rejected Before Execution")
    lines.append("")
    for rejected in metrics["rejected_before_execution"]:
        lines.append(f"- `{rejected['candidate_id']}` ({rejected['name']}): {rejected['rejection_reason']}")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "Sandbox signals are sub-MeV and fitted on an 11-row residual slice. They are "
        "scout-triage evidence only and are not promoted as discoveries."
    )
    lines.append("")
    partially_valid = [
        item["candidate_id"]
        for item in metrics["executed_items"]
        if item["verdict"] == "PARTIALLY_VALID"
    ]
    overfit = [
        item["candidate_id"]
        for item in metrics["executed_items"]
        if item["verdict"] == "OVERFITTED"
    ]
    inconclusive = [
        item["candidate_id"]
        for item in metrics["executed_items"]
        if item["verdict"] == "INCONCLUSIVE"
    ]
    if partially_valid:
        lines.append(
            "`PARTIALLY_VALID` candidates: "
            + ", ".join(f"`{cid}`" for cid in partially_valid)
            + "."
        )
    else:
        lines.append("No candidate reached `PARTIALLY_VALID`.")
    if overfit:
        lines.append("")
        lines.append(
            "`OVERFITTED` candidates: " + ", ".join(f"`{cid}`" for cid in overfit) + "."
        )
    if inconclusive:
        lines.append("")
        lines.append(
            "`INCONCLUSIVE` candidates: "
            + ", ".join(f"`{cid}`" for cid in inconclusive)
            + "."
        )
    lines.append("")

    lines.append("## Promotion Boundary")
    lines.append("")
    lines.append("- No prediction registry files were edited.")
    lines.append("- No canonical result files were edited.")
    lines.append("- No claims or knowledge files were edited.")
    lines.append("- No claim promotion is allowed by this task.")
    lines.append("")
    lines.append(
        "Any future registry or reveal work must be a separate maintainer-reviewed task."
    )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    """Write the deterministic stress-scout metrics artifact and optional report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "metrics.json",
        help="Path for the metrics JSON artifact.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "report.md",
        help="Path for the optional markdown report artifact.",
    )
    args = parser.parse_args(argv)

    metrics = build_metrics()
    out_path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(metrics, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")

    if args.report is not None:
        report = render_report(metrics)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
        print(f"wrote {args.report}")


if __name__ == "__main__":
    main()
