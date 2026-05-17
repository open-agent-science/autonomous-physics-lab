"""TASK-0278 shell-neighborhood nuclear sandbox scout.

This is a sandbox-only residual scout. It evaluates bounded shell-neighborhood
correction features against the frozen RESULT-0015 fitted semi-empirical
baseline using repository-pinned datasets only. It does not write prediction
registry entries, canonical results, claims, or knowledge artifacts.
"""

from __future__ import annotations

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

AGENT_RUN_ID = "AGENT-RUN-0012"
TASK_ID = "TASK-0278"


EXECUTED_CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "candidate_id": "SHELL-SCOUT-001",
        "name": "Z+N Gaussian shell proximity, sigma 2",
        "formula": "r_corr = beta_z*s_z2 + beta_n*s_n2",
        "feature_names": ("s_z2", "s_n2"),
        "complexity": 2,
    },
    {
        "candidate_id": "SHELL-SCOUT-002",
        "name": "Neutron-axis Gaussian shell proximity, sigma 2",
        "formula": "r_corr = beta_n*s_n2",
        "feature_names": ("s_n2",),
        "complexity": 1,
    },
    {
        "candidate_id": "SHELL-SCOUT-003",
        "name": "Proton-axis Gaussian shell proximity, sigma 2",
        "formula": "r_corr = beta_z*s_z2",
        "feature_names": ("s_z2",),
        "complexity": 1,
    },
    {
        "candidate_id": "SHELL-SCOUT-004",
        "name": "Shell-axis contrast, neutron minus proton proximity",
        "formula": "r_corr = beta_c*(s_n2 - s_z2)",
        "feature_names": ("s_n2_minus_s_z2",),
        "complexity": 1,
    },
    {
        "candidate_id": "SHELL-SCOUT-005",
        "name": "Double-neighborhood product shell proximity",
        "formula": "r_corr = beta_p*(s_z2*s_n2)",
        "feature_names": ("s_z2_times_s_n2",),
        "complexity": 1,
    },
    {
        "candidate_id": "SHELL-SCOUT-006",
        "name": "Near-null shell sanity control",
        "formula": "r_corr = 0.0",
        "feature_names": (),
        "complexity": 0,
        "fixed_zero_control": True,
    },
)


REJECTED_BEFORE_EXECUTION: tuple[dict[str, str], ...] = (
    {
        "candidate_id": "SHELL-SCOUT-007",
        "name": "N=82-only switch",
        "rejection_reason": (
            "Rejected before sandbox evaluation because an N=82-only switch is too close "
            "to known post-AME2020 shell residual clusters and would be a post-hoc "
            "targeted feature rather than a bounded general shell-neighborhood scout."
        ),
    },
    {
        "candidate_id": "SHELL-SCOUT-008",
        "name": "Free sigma shell Gaussian grid",
        "rejection_reason": (
            "Rejected before execution because fitting or selecting sigma on the 11-row "
            "NMD-0002 slice adds a nonlinear tuning knob with high overfit risk."
        ),
    },
    {
        "candidate_id": "SHELL-SCOUT-009",
        "name": "Binary near-magic threshold sweep",
        "rejection_reason": (
            "Rejected before execution because threshold sweeps duplicate the continuous "
            "Gaussian proximity candidates while adding arbitrary cutoffs."
        ),
    },
)


def nearest_magic_distance(value: int) -> int:
    """Distance to the nearest canonical magic number."""
    return min(abs(value - magic) for magic in MAGIC_NUMBERS)


def shell_gaussian(value: int, *, sigma: float = 2.0) -> float:
    """Continuous proximity to the nearest magic number."""
    distance = nearest_magic_distance(value)
    return float(math.exp(-(distance * distance) / (2.0 * sigma * sigma)))


def feature_vector(feature_names: tuple[str, ...], *, z: int, n: int) -> tuple[float, ...]:
    """Return feature values for one target row."""
    sz2 = shell_gaussian(z, sigma=2.0)
    sn2 = shell_gaussian(n, sigma=2.0)
    values = {
        "s_z2": sz2,
        "s_n2": sn2,
        "s_n2_minus_s_z2": sn2 - sz2,
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


def subset_ids(*, z: int, n: int, a: int, was_extrapolated: bool) -> tuple[str, ...]:
    """Subset labels used for shell-neighborhood diagnostics."""
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


def baseline_post_ame2020_rows(coefficients: SemiEmpiricalCoefficients) -> tuple[list[dict[str, Any]], dict[str, Any]]:
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
        item = {
            "row_id": row["row_id"],
            "nuclide_id": row["nuclide_id"],
            "Z": z,
            "N": n,
            "A": a,
            "observed_mev": observed,
            "baseline_predicted_mev": predicted,
            "baseline_residual_mev": residual,
            "was_extrapolated": bool(row["ame2020_comparison"]["was_extrapolated"]),
        }
        per_row.append(item)
        for subset_id in subset_ids(
            z=z,
            n=n,
            a=a,
            was_extrapolated=bool(row["ame2020_comparison"]["was_extrapolated"]),
        ):
            subset_errors.setdefault(subset_id, []).append(residual)
    return per_row, {key: summarize_errors(value) for key, value in sorted(subset_errors.items())}


def evaluate_candidate(
    candidate: dict[str, Any],
    *,
    training_entries: list[Any],
    training_residuals: np.ndarray,
    post_rows: list[dict[str, Any]],
    baseline_metrics: dict[str, Any],
) -> dict[str, Any]:
    """Fit a candidate on NMD-0002 residuals and evaluate it on pinned holdout rows."""
    feature_names = tuple(candidate["feature_names"])
    if candidate.get("fixed_zero_control"):
        beta = np.asarray([], dtype=float)
    else:
        train_x = np.asarray(
            [
                feature_vector(feature_names, z=entry.Z, n=entry.N)
                for entry in training_entries
            ],
            dtype=float,
        )
        beta, *_ = np.linalg.lstsq(train_x, training_residuals, rcond=None)

    subset_errors: dict[str, list[float]] = {key: [] for key in baseline_metrics}
    per_row: list[dict[str, Any]] = []
    activation_counts = {name: 0 for name in feature_names}
    for row in post_rows:
        values = feature_vector(feature_names, z=int(row["Z"]), n=int(row["N"]))
        for name, value in zip(feature_names, values):
            if abs(value) > 0.0:
                activation_counts[name] += 1
        correction = 0.0 if candidate.get("fixed_zero_control") else float(np.asarray(values) @ beta)
        residual = float(row["baseline_residual_mev"]) - correction
        item = {
            "row_id": row["row_id"],
            "nuclide_id": row["nuclide_id"],
            "Z": row["Z"],
            "N": row["N"],
            "A": row["A"],
            "correction_mev": correction,
            "candidate_residual_mev": residual,
            "candidate_abs_error_mev": abs(residual),
            "feature_values": {
                name: float(value)
                for name, value in zip(feature_names, values)
            },
        }
        per_row.append(item)
        for subset_id in subset_ids(
            z=int(row["Z"]),
            n=int(row["N"]),
            a=int(row["A"]),
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
    return {
        "candidate_id": candidate["candidate_id"],
        "name": candidate["name"],
        "formula": candidate["formula"],
        "complexity": candidate["complexity"],
        "fitted_coefficients": {
            name: float(value) for name, value in zip(feature_names, beta)
        },
        "feature_activation_counts": activation_counts,
        "metrics_by_subset": metrics_by_subset,
        "delta_mae_by_subset_mev": delta_by_subset,
        "worst_abs_error_cases": sorted(
            per_row, key=lambda item: float(item["candidate_abs_error_mev"]), reverse=True
        )[:5],
        "verdict": classify_candidate(delta_by_subset),
    }


def classify_candidate(delta_by_subset: dict[str, float | None]) -> str:
    """Conservative scout verdict from subset MAE deltas."""
    primary = delta_by_subset.get("primary")
    magic_any = delta_by_subset.get("magic_any")
    near_magic = delta_by_subset.get("near_magic")
    shell_deltas = [
        value
        for key, value in delta_by_subset.items()
        if key in {"magic_any", "magic_n", "magic_z", "near_magic", "double_magic"}
        and value is not None
    ]
    improved_shell = sum(1 for value in shell_deltas if value < -1.0e-12)
    regressed_shell = sum(1 for value in shell_deltas if value > 1.0e-12)
    worst_regression = max([0.0] + [value for value in delta_by_subset.values() if value is not None])
    if (
        primary is not None
        and magic_any is not None
        and near_magic is not None
        and primary < 0.0
        and magic_any < 0.0
        and near_magic <= 0.0
        and worst_regression <= 0.25
    ):
        return "PARTIALLY_VALID"
    if primary is not None and primary > 0.5:
        return "OVERFITTED"
    if regressed_shell >= 2 or worst_regression >= 1.0:
        return "OVERFITTED"
    if improved_shell >= 2:
        return "INCONCLUSIVE"
    return "INCONCLUSIVE"


def _delta_mae(candidate: dict[str, Any] | None, baseline: dict[str, Any] | None) -> float | None:
    if not candidate or not baseline:
        return None
    if candidate["mae_mev"] is None or baseline["mae_mev"] is None:
        return None
    return float(candidate["mae_mev"]) - float(baseline["mae_mev"])


def build_metrics() -> dict[str, Any]:
    """Build deterministic scout metrics."""
    coefficients = load_frozen_baseline_coefficients()
    nmd = load_nuclear_mass_dataset(NMD_PATH)
    baseline_rows = evaluate_baseline(
        entries=nmd.entries,
        model_id="model_fitted_semi_empirical",
        coefficients=coefficients,
    )
    residuals = np.asarray([row.residual_mev for row in baseline_rows], dtype=float)
    training_entries = [
        next(entry for entry in nmd.entries if entry.nuclide_id == row.nuclide_id)
        for row in baseline_rows
    ]
    post_rows, baseline_metrics = baseline_post_ame2020_rows(coefficients)
    executed = [
        evaluate_candidate(
            candidate,
            training_entries=training_entries,
            training_residuals=residuals,
            post_rows=post_rows,
            baseline_metrics=baseline_metrics,
        )
        for candidate in EXECUTED_CANDIDATES
    ]
    verdict_counts: dict[str, int] = {}
    for item in executed:
        verdict_counts[item["verdict"]] = verdict_counts.get(item["verdict"], 0) + 1
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "shell_neighborhood_variant_scout",
        "sandbox_only": True,
        "evidence_class": "bounded_sandbox_residual_scout",
        "live_external_fetch_allowed": False,
        "summary": {
            "generated_candidate_count": len(EXECUTED_CANDIDATES) + len(REJECTED_BEFORE_EXECUTION),
            "executed_candidate_count": len(EXECUTED_CANDIDATES),
            "rejected_before_execution_count": len(REJECTED_BEFORE_EXECUTION),
            "near_null_control_preserved": any(
                item["candidate_id"] == "SHELL-SCOUT-006" for item in executed
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
        "baseline_metrics_by_subset": baseline_metrics,
        "generated_candidates": [
            {
                "candidate_id": item["candidate_id"],
                "name": item["name"],
                "formula": item["formula"],
                "decision": "executed",
            }
            for item in EXECUTED_CANDIDATES
        ]
        + [
            {
                "candidate_id": item["candidate_id"],
                "name": item["name"],
                "decision": "rejected_before_execution",
                "rejection_reason": item["rejection_reason"],
            }
            for item in REJECTED_BEFORE_EXECUTION
        ],
        "executed_items": executed,
        "rejected_before_execution": list(REJECTED_BEFORE_EXECUTION),
        "promotion_boundary": {
            "writes_canonical_result": False,
            "writes_prediction_registry": False,
            "claim_promotion_allowed": False,
            "required_next_step": "Maintainer review before any registry selection, RESULT-* artifact, or claim update.",
        },
        "limitations": [
            "Sandbox-only scout; no prediction registry, canonical result, claim, or knowledge artifact is updated.",
            "Candidates are fitted on the 11-row NMD-0002 residual slice, so overfit risk is high.",
            "Post-AME2020 evaluation uses a repository-pinned dataset and is retrospective diagnostic evidence, not a reveal.",
            "Shell-neighborhood features are empirical residual probes, not a physical shell model.",
        ],
    }


def main() -> None:
    metrics = build_metrics()
    out_dir = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"wrote {metrics_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
