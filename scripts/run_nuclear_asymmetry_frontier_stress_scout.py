"""TASK-0289 nuclear asymmetry-frontier adversarial stress scout.

This sandbox-only scout adversarially re-evaluates the small asymmetry-frontier
signal first surfaced by NR-SCOUT-003 and NR-SCOUT-004 (AGENT-RUN-0013), with
NR-SCOUT-005 included as a required overfit negative-control neighbor. It also
adds a sign-inverted control, a clipped asymmetry variant, and a near-null
sanity control. The runner fits bounded additive residual features on the
frozen `RESULT-0015::model_fitted_semi_empirical` baseline using only
repository-pinned data; it does not write prediction registry entries,
canonical results, claims, or knowledge artifacts.
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
    SemiEmpiricalCoefficients,
    evaluate_baseline,
    semi_empirical_binding_energy,
)
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset  # noqa: E402


NMD_PATH = REPO_ROOT / "data" / "nuclear_masses" / "nmd-0002-curated-measured-slice.yaml"
POST_AME_PATH = REPO_ROOT / "data" / "nuclear_masses" / "post_ame2020_holdout.yaml"
RESULT_PATH = REPO_ROOT / "results" / "EXP-0012" / "RUN-0001" / "result.yaml"

AGENT_RUN_ID = "AGENT-RUN-0017"
TASK_ID = "TASK-0289"

CLIPPED_ASYMMETRY_THRESHOLD = 0.25


EXECUTED_CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "candidate_id": "ASYM-STRESS-001",
        "name": "Positive asymmetry fraction (re-eval of NR-SCOUT-003)",
        "formula": "r_corr = beta * max((N-Z)/A, 0)",
        "feature_names": ("positive_asymmetry_fraction",),
        "complexity": 1,
    },
    {
        "candidate_id": "ASYM-STRESS-002",
        "name": "Frontier excess beyond N-Z = 20 (re-eval of NR-SCOUT-004)",
        "formula": "r_corr = beta * max(N-Z-20, 0) / A",
        "feature_names": ("frontier_excess_after_20_over_a",),
        "complexity": 1,
    },
    {
        "candidate_id": "ASYM-STRESS-003",
        "name": "Quadratic+cubic neutron-excess matched pair (overfit neighbor of NR-SCOUT-005)",
        "formula": (
            "r_corr = beta_q * max(N-Z, 0)^2 / A "
            "+ beta_c * max(N-Z, 0)^3 / A^2"
        ),
        "feature_names": ("quadratic_neutron_excess", "cubic_neutron_excess"),
        "complexity": 2,
        "expected_overfit_neighbor": True,
    },
    {
        "candidate_id": "ASYM-STRESS-004",
        "name": "Sign-inverted positive asymmetry fraction (adversarial control)",
        "formula": (
            "Fit beta on training using positive_asymmetry_fraction as in 001; "
            "apply correction with NEGATED sign (-beta * feature) on the holdout."
        ),
        "feature_names": ("positive_asymmetry_fraction",),
        "complexity": 1,
        "sign_inverted": True,
    },
    {
        "candidate_id": "ASYM-STRESS-005",
        "name": "Clipped asymmetry above 0.25",
        "formula": "r_corr = beta * max((N-Z)/A - 0.25, 0)",
        "feature_names": ("clipped_asymmetry_above_0_25",),
        "complexity": 1,
    },
    {
        "candidate_id": "ASYM-STRESS-006",
        "name": "Near-null asymmetry sanity control",
        "formula": "r_corr = 0.0",
        "feature_names": (),
        "complexity": 0,
        "fixed_zero_control": True,
    },
)


REJECTED_BEFORE_EXECUTION: tuple[dict[str, str], ...] = (
    {
        "candidate_id": "ASYM-STRESS-007",
        "name": "Free-power asymmetry exponent",
        "rejection_reason": (
            "Rejected before execution because a free exponent on ((N-Z)/A)^p "
            "is a nonlinear knob fitted on the 11-row NMD-0002 residual "
            "training slice with high overfit risk; mirrors the NR-SCOUT-007 "
            "rejection from the original neutron-rich lane."
        ),
    },
    {
        "candidate_id": "ASYM-STRESS-008",
        "name": "Per-Z asymmetry slopes",
        "rejection_reason": (
            "Rejected before execution because per-Z separate coefficients on "
            "an 11-row training slice memorize individual training rows and "
            "inflate degrees of freedom beyond what the bounded linear scout "
            "contract allows."
        ),
    },
    {
        "candidate_id": "ASYM-STRESS-009",
        "name": "Asymmetry-threshold sweep grid",
        "rejection_reason": (
            "Rejected before execution because sweeping separate indicators "
            "for thresholds in {0.10, 0.15, 0.20, 0.25, 0.30} adds arbitrary "
            "cutoffs and duplicates the continuous positive_asymmetry_fraction "
            "probe; mirrors the NR-SCOUT-009 rejection."
        ),
    },
)


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


def asymmetry(z: int, n: int, a: int) -> float:
    """Standard (N-Z)/A asymmetry."""
    return float(n - z) / float(a)


def feature_vector(
    feature_names: tuple[str, ...],
    *,
    z: int,
    n: int,
    a: int,
) -> tuple[float, ...]:
    """Return asymmetry-frontier feature values for one target row."""
    asym = asymmetry(z, n, a)
    excess = max(n - z, 0)
    values = {
        "positive_asymmetry_fraction": max(asym, 0.0),
        "frontier_excess_after_20_over_a": float(max(n - z - 20, 0)) / float(a),
        "clipped_asymmetry_above_0_25": max(asym - CLIPPED_ASYMMETRY_THRESHOLD, 0.0),
        # ASYM-STRESS-003 matched pair: re-use NR-SCOUT-001/-002 / NR-SCOUT-005
        # scalings so the catastrophic +1.37 MeV primary blow-up from
        # AGENT-RUN-0013 is reproduced. The pair is included as the required
        # OVERFITTED negative-control neighbor.
        "quadratic_neutron_excess": float(excess * excess) / float(a),
        "cubic_neutron_excess": float(excess * excess * excess) / float(a * a),
    }
    return tuple(values[name] for name in feature_names)


def subset_ids(*, z: int, n: int, a: int, was_extrapolated: bool) -> tuple[str, ...]:
    """Subset labels covering primary, asymmetry, frontier-edge, and mass-bands."""
    asym = asymmetry(z, n, a)
    delta = n - z
    ids = ["primary"]
    ids.append("ame2020_extrapolated_comparison" if was_extrapolated else "ame2020_measured_comparison")
    if asym >= 0.20:
        ids.append("asymmetry_ge_0_20")
    if asym >= 0.25:
        ids.append("asymmetry_ge_0_25")
    if delta >= 20:
        ids.append("n_z_ge_20")
    if delta >= 30:
        ids.append("n_z_ge_30")
    if a >= 100:
        ids.append("heavy_a_ge_100")
    if 50 <= a <= 150:
        ids.append("mid_mass")
    if a < 50:
        ids.append("light_a_lt_50")
    return tuple(ids)


def summarize_errors(errors: list[float]) -> dict[str, float | int | None]:
    """Summarize signed residuals into MAE/RMSE/mean/max."""
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


def _delta(candidate: dict[str, Any] | None, baseline: dict[str, Any] | None) -> float | None:
    if not candidate or not baseline:
        return None
    if candidate.get("mae_mev") is None or baseline.get("mae_mev") is None:
        return None
    return float(candidate["mae_mev"]) - float(baseline["mae_mev"])


def frontier_contrast(deltas: dict[str, float | None]) -> float | None:
    """Return asymmetry_ge_0_25 delta minus 0.5*(mid_mass + light_a_lt_50)."""
    high = deltas.get("asymmetry_ge_0_25")
    mid = deltas.get("mid_mass")
    light = deltas.get("light_a_lt_50")
    if high is None or mid is None or light is None:
        return None
    return float(high) - 0.5 * (float(mid) + float(light))


def verdict_for_candidate(
    *,
    candidate: dict[str, Any],
    delta_by_subset: dict[str, float | None],
    count_by_subset: dict[str, int],
) -> str:
    """Assign conservative scout verdicts without promoting scientific claims."""
    material = 1.0e-6
    if candidate.get("fixed_zero_control"):
        return "INCONCLUSIVE"
    primary = delta_by_subset.get("primary")
    if primary is None:
        return "INCONCLUSIVE"
    numeric_deltas = [value for value in delta_by_subset.values() if value is not None]
    worst_subset_regression = max([0.0, *numeric_deltas])
    if candidate.get("expected_overfit_neighbor") and primary > 0.5:
        return "OVERFITTED"
    if candidate.get("sign_inverted") and primary < -material:
        return "OVERFITTED"
    if primary > 1.0 or worst_subset_regression > 2.0:
        return "OVERFITTED"
    if primary > 0.05:
        improving_keys = [
            key
            for key, value in delta_by_subset.items()
            if value is not None and value < -material
        ]
        if improving_keys and all(
            count_by_subset.get(key, 0) <= 3 for key in improving_keys
        ):
            return "OVERFITTED"
    high_asym_delta = delta_by_subset.get("asymmetry_ge_0_25")
    if (
        high_asym_delta is not None
        and high_asym_delta < -material
        and primary <= 0.05
        and worst_subset_regression <= 0.5
    ):
        return "PARTIALLY_VALID"
    if primary < -material and worst_subset_regression <= 0.5:
        return "PARTIALLY_VALID"
    return "INCONCLUSIVE"


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
                feature_vector(feature_names, z=entry.Z, n=entry.N, a=entry.A)
                for entry in training_entries
            ],
            dtype=float,
        )
        beta, *_ = np.linalg.lstsq(train_x, training_residuals, rcond=None)

    sign_inverted = bool(candidate.get("sign_inverted"))
    applied_beta = -np.asarray(beta) if sign_inverted else np.asarray(beta)

    subset_errors: dict[str, list[float]] = {key: [] for key in baseline_metrics}
    per_row: list[dict[str, Any]] = []
    activation_counts = {name: 0 for name in feature_names}
    for row in post_rows:
        z, n, a = int(row["Z"]), int(row["N"]), int(row["A"])
        values = feature_vector(feature_names, z=z, n=n, a=a)
        for name, value in zip(feature_names, values):
            if abs(value) > 0.0:
                activation_counts[name] += 1
        correction = (
            0.0
            if candidate.get("fixed_zero_control")
            else float(np.asarray(values) @ applied_beta)
        )
        predicted = float(row["baseline_predicted_mev"]) + correction
        residual = float(row["observed_mev"]) - predicted
        item = {
            "row_id": row["row_id"],
            "nuclide_id": row["nuclide_id"],
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
            was_extrapolated=bool(row["was_extrapolated"]),
        ):
            subset_errors.setdefault(subset_id, []).append(residual)

    metrics_by_subset = {
        key: summarize_errors(value) for key, value in sorted(subset_errors.items())
    }
    delta_by_subset = {
        key: _delta(metrics_by_subset.get(key), baseline_metrics.get(key))
        for key in sorted(baseline_metrics)
    }
    count_by_subset = {
        key: int(metric.get("count", 0)) for key, metric in metrics_by_subset.items()
    }

    frontier_contrast_value = frontier_contrast(delta_by_subset)
    numeric_deltas = [value for value in delta_by_subset.values() if value is not None]
    worst_subset_regression = max([0.0, *numeric_deltas])
    verdict = verdict_for_candidate(
        candidate=candidate,
        delta_by_subset=delta_by_subset,
        count_by_subset=count_by_subset,
    )

    result: dict[str, Any] = {
        "candidate_id": candidate["candidate_id"],
        "name": candidate["name"],
        "formula": candidate["formula"],
        "complexity": candidate["complexity"],
        "fitted_coefficients": {
            name: float(value) for name, value in zip(feature_names, applied_beta)
        },
        "feature_activation_counts": activation_counts,
        "metrics_by_subset": metrics_by_subset,
        "delta_mae_by_subset_mev": delta_by_subset,
        "frontier_contrast_mev": frontier_contrast_value,
        "worst_subset_regression_mae_mev": worst_subset_regression,
        "worst_abs_error_cases": sorted(
            per_row,
            key=lambda item: float(item["candidate_abs_error_mev"]),
            reverse=True,
        )[:5],
        "verdict": verdict,
        "limitations": [
            "Feature coefficients are fit on the 11-row NMD-0002 residual slice.",
            "Post-AME2020 evaluation uses committed retrospective rows only; it is not a reveal of new live measurements.",
            "Verdict is a sandbox triage label, not a promoted claim.",
        ],
    }
    if candidate.get("expected_overfit_neighbor"):
        result["expected_overfit_neighbor"] = True
    if candidate.get("sign_inverted"):
        result["sign_inverted"] = True
    if candidate.get("fixed_zero_control"):
        result["fixed_zero_control"] = True
    return result


def _lane_recommendation(executed_items: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute the deterministic lane recommendation block."""
    by_id = {item["candidate_id"]: item for item in executed_items}
    primary_signal_ids = ("ASYM-STRESS-001", "ASYM-STRESS-002", "ASYM-STRESS-005")
    keep_evidence: list[str] = []
    watchlist_evidence: list[str] = []
    for cid in primary_signal_ids:
        item = by_id.get(cid)
        if item is None:
            continue
        deltas = item["delta_mae_by_subset_mev"]
        primary = deltas.get("primary")
        high = deltas.get("asymmetry_ge_0_25")
        worst = float(item.get("worst_subset_regression_mae_mev") or 0.0)
        if primary is None or high is None:
            continue
        if high < -0.02 and primary <= 0.05 and worst <= 0.5:
            keep_evidence.append(
                f"{cid}: asymmetry_ge_0_25 delta {high:+.6f} MeV, "
                f"primary delta {primary:+.6f} MeV, worst regression {worst:+.6f} MeV"
            )
        elif high < -0.02 and (primary > 0.05 or worst > 0.5):
            watchlist_evidence.append(
                f"{cid}: asymmetry_ge_0_25 delta {high:+.6f} MeV but "
                f"primary delta {primary:+.6f} MeV / worst regression {worst:+.6f} MeV"
            )
    if keep_evidence:
        return {
            "value": "keep_as_review_surface",
            "rationale": (
                "At least one of the asymmetry-frontier candidates concentrates "
                "improvement on the high-asymmetry subset with a flat primary "
                "surface and a small worst-subset regression; the lane should "
                "remain available as a future maintainer-reviewed surface."
            ),
            "evidence_points": keep_evidence,
        }
    if watchlist_evidence:
        return {
            "value": "demote_to_watchlist",
            "rationale": (
                "An asymmetry-frontier candidate improves the high-asymmetry "
                "subset but pays for it with primary or worst-subset "
                "regression; demote the lane to a watchlist surface rather "
                "than a recommended review."
            ),
            "evidence_points": watchlist_evidence,
        }
    overfit_evidence: list[str] = []
    overfit_item = by_id.get("ASYM-STRESS-003")
    if overfit_item is not None:
        deltas = overfit_item["delta_mae_by_subset_mev"]
        overfit_evidence.append(
            "ASYM-STRESS-003: primary delta "
            f"{float(deltas.get('primary') or 0.0):+.6f} MeV, asymmetry_ge_0_25 delta "
            f"{float(deltas.get('asymmetry_ge_0_25') or 0.0):+.6f} MeV - matched "
            "quadratic+cubic neighbor remains an overfit reference."
        )
    sign_item = by_id.get("ASYM-STRESS-004")
    if sign_item is not None:
        deltas = sign_item["delta_mae_by_subset_mev"]
        overfit_evidence.append(
            "ASYM-STRESS-004 (sign-inverted): primary delta "
            f"{float(deltas.get('primary') or 0.0):+.6f} MeV - applied "
            "negated coefficient is preserved as adversarial evidence."
        )
    return {
        "value": "preserve_as_negative_evidence",
        "rationale": (
            "No asymmetry-frontier candidate produced a concentrated "
            "high-asymmetry improvement that survived primary and worst-subset "
            "regression thresholds. Preserve the lane as documented negative "
            "and adversarial evidence rather than a review surface."
        ),
        "evidence_points": overfit_evidence,
    }


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
    entries_by_id = {entry.nuclide_id: entry for entry in nmd.entries}
    training_entries = [entries_by_id[row.nuclide_id] for row in baseline_rows]

    post_rows, baseline_metrics = baseline_post_ame2020_rows(coefficients)
    executed_items = [
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

    lane_recommendation = _lane_recommendation(executed_items)

    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "asymmetry_frontier_adversarial_stress_scout",
        "sandbox_only": True,
        "evidence_class": "bounded_sandbox_residual_scout",
        "live_external_fetch_allowed": False,
        "summary": {
            "generated_candidate_count": len(generated_candidates),
            "executed_candidate_count": len(EXECUTED_CANDIDATES),
            "rejected_before_execution_count": len(REJECTED_BEFORE_EXECUTION),
            "near_null_control_preserved": any(
                item["candidate_id"] == "ASYM-STRESS-006"
                and item["verdict"] == "INCONCLUSIVE"
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
            "asymmetry_ge_0_20": "(N-Z)/A >= 0.20",
            "asymmetry_ge_0_25": "(N-Z)/A >= 0.25",
            "n_z_ge_20": "N - Z >= 20 (frontier-edge)",
            "n_z_ge_30": "N - Z >= 30 (deeper frontier)",
            "heavy_a_ge_100": "A >= 100",
            "mid_mass": "50 <= A <= 150",
            "light_a_lt_50": "A < 50",
            "frontier_contrast": (
                "asymmetry_ge_0_25 delta MAE minus 0.5 * (mid_mass delta MAE + "
                "light_a_lt_50 delta MAE)"
            ),
        },
        "feature_definitions": {
            "positive_asymmetry_fraction": "max((N - Z) / A, 0)",
            "frontier_excess_after_20_over_a": "max(N - Z - 20, 0) / A",
            "clipped_asymmetry_above_0_25": (
                f"max((N - Z) / A - {CLIPPED_ASYMMETRY_THRESHOLD}, 0)"
            ),
            "quadratic_neutron_excess": (
                "max(N - Z, 0)^2 / A (matched-pair feature re-used from "
                "NR-SCOUT-001 to reproduce the NR-SCOUT-005 overfit blow-up)"
            ),
            "cubic_neutron_excess": (
                "max(N - Z, 0)^3 / A^2 (matched-pair feature re-used from "
                "NR-SCOUT-002)"
            ),
            "sign_inverted_application": (
                "ASYM-STRESS-004 fits beta on training as in ASYM-STRESS-001, then "
                "applies the correction with negated sign on the holdout."
            ),
        },
        "baseline_metrics_by_subset": baseline_metrics,
        "lane_recommendation": lane_recommendation,
        "generated_candidates": generated_candidates,
        "executed_items": executed_items,
        "rejected_before_execution": list(REJECTED_BEFORE_EXECUTION),
        "promotion_boundary": {
            "writes_prediction_registry": False,
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": "Maintainer review before any registry selection, RESULT-* artifact, claim, or knowledge update.",
        },
        "limitations": [
            "Sandbox-only scout; no prediction registry, canonical result, claim, or knowledge artifact is updated.",
            "Feature coefficients are fit on the 11-row NMD-0002 residual slice.",
            "Post-AME2020 evaluation uses committed retrospective rows only and is not a live reveal.",
            "ASYM-STRESS-003 is intentionally included as an expected-overfit negative-control neighbor; its OVERFITTED verdict is part of the lane design.",
            "ASYM-STRESS-004 negates the fitted coefficient on the holdout to probe sign-direction stability; it is not a physical correction proposal.",
            "Rejected candidates are preserved to document overfit, row-memorization, and duplicate-search boundaries.",
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
    """Render a markdown report mirroring the scout review pattern."""
    lines: list[str] = []
    lines.append("# Nuclear Asymmetry-Frontier Adversarial Stress Scout")
    lines.append("")
    lines.append(f"**Agent run:** {metrics['agent_run_id']}  ")
    lines.append(f"**Task:** {metrics['task_id']}  ")
    lines.append("**Evidence class:** bounded sandbox residual scout  ")
    lines.append("**Baseline:** `RESULT-0015::model_fitted_semi_empirical`  ")
    lines.append(
        "**Script:** `scripts/run_nuclear_asymmetry_frontier_stress_scout.py`  "
    )
    lines.append(
        f"**Metrics:** `agent_runs/{metrics['agent_run_id']}/metrics.json`"
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    summary = metrics["summary"]
    lines.append(
        "This scout generated "
        f"{summary['generated_candidate_count']} bounded asymmetry-frontier "
        "stress candidate ideas. "
        f"{summary['executed_candidate_count']} were evaluated and "
        f"{summary['rejected_before_execution_count']} were rejected before "
        "execution due to overfit, row-memorization, or duplicate-search risk."
    )
    lines.append("")
    lines.append("| Item | Count |")
    lines.append("| --- | ---: |")
    lines.append(f"| Generated candidates | {summary['generated_candidate_count']} |")
    lines.append(f"| Executed candidates | {summary['executed_candidate_count']} |")
    lines.append(
        f"| Rejected before execution | {summary['rejected_before_execution_count']} |"
    )
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
        "| Candidate | Feature family | Primary ΔMAE MeV | asymmetry>=0.25 ΔMAE MeV "
        "| n_z_ge_20 ΔMAE MeV | heavy_a_ge_100 ΔMAE MeV | mid_mass ΔMAE MeV "
        "| Frontier contrast MeV | Verdict |"
    )
    lines.append(
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |"
    )
    for item in metrics["executed_items"]:
        deltas = item["delta_mae_by_subset_mev"]
        lines.append(
            "| `{cid}` | {family} | {primary} | {high} | {nz20} | {heavy} | {mid} | {fc} | `{verdict}` |".format(
                cid=item["candidate_id"],
                family=item["name"],
                primary=_format_delta(deltas.get("primary")),
                high=_format_delta(deltas.get("asymmetry_ge_0_25")),
                nz20=_format_delta(deltas.get("n_z_ge_20")),
                heavy=_format_delta(deltas.get("heavy_a_ge_100")),
                mid=_format_delta(deltas.get("mid_mass")),
                fc=_format_delta(item.get("frontier_contrast_mev")),
                verdict=item["verdict"],
            )
        )
    lines.append("")
    lines.append(
        "Negative ΔMAE means lower retrospective MAE than the frozen baseline on "
        "that subset. Positive ΔMAE means regression."
    )
    lines.append("")

    lines.append("## Adversarial Controls")
    lines.append("")
    by_id = {item["candidate_id"]: item for item in metrics["executed_items"]}
    overfit = by_id.get("ASYM-STRESS-003")
    sign_inverted = by_id.get("ASYM-STRESS-004")
    base_signal = by_id.get("ASYM-STRESS-001")
    if overfit is not None:
        primary = overfit["delta_mae_by_subset_mev"].get("primary")
        lines.append(
            "- `ASYM-STRESS-003` (matched quadratic+cubic): primary ΔMAE = "
            f"{_format_delta(primary)} MeV. Reproduces the NR-SCOUT-005 "
            "catastrophic overfit and is preserved as an OVERFITTED negative "
            "control neighbor."
        )
    if sign_inverted is not None and base_signal is not None:
        si_coef = sign_inverted["fitted_coefficients"].get(
            "positive_asymmetry_fraction"
        )
        base_coef = base_signal["fitted_coefficients"].get(
            "positive_asymmetry_fraction"
        )
        lines.append(
            "- `ASYM-STRESS-004` (sign-inverted): applied coefficient on "
            f"`positive_asymmetry_fraction` = {si_coef:+.6f} MeV, which is the "
            f"negation of ASYM-STRESS-001's fitted coefficient {base_coef:+.6f} MeV."
        )
    null_item = by_id.get("ASYM-STRESS-006")
    if null_item is not None:
        lines.append(
            "- `ASYM-STRESS-006` (near-null control): all subset deltas are 0.0; "
            "verdict `INCONCLUSIVE`."
        )
    lines.append("")

    lines.append("## Lane Recommendation")
    lines.append("")
    rec = metrics["lane_recommendation"]
    lines.append(f"**Value:** `{rec['value']}`")
    lines.append("")
    lines.append(rec["rationale"])
    lines.append("")
    if rec["evidence_points"]:
        lines.append("Evidence:")
        lines.append("")
        for point in rec["evidence_points"]:
            lines.append(f"- {point}")
        lines.append("")

    lines.append("## Rejected Before Execution")
    lines.append("")
    for rejected in metrics["rejected_before_execution"]:
        lines.append(
            f"- `{rejected['candidate_id']}` ({rejected['name']}): "
            f"{rejected['rejection_reason']}"
        )
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "Sandbox signals are sub-MeV and fitted on an 11-row residual slice. They "
        "are scout triage evidence only and are not promoted as discoveries."
    )
    partially_valid = [
        item["candidate_id"]
        for item in metrics["executed_items"]
        if item["verdict"] == "PARTIALLY_VALID"
    ]
    overfit_ids = [
        item["candidate_id"]
        for item in metrics["executed_items"]
        if item["verdict"] == "OVERFITTED"
    ]
    if partially_valid:
        lines.append("")
        lines.append(
            "`PARTIALLY_VALID` candidates: "
            + ", ".join(f"`{cid}`" for cid in partially_valid)
            + ". Frontier-contrast values are reported so any high-asymmetry-only "
            "gain that masks mid-mass or light regression is flagged as fragile."
        )
    else:
        lines.append("")
        lines.append(
            "No candidate reached `PARTIALLY_VALID`. The lane preserves negative "
            "and null evidence rather than promoting a signal."
        )
    if overfit_ids:
        lines.append("")
        lines.append(
            "`OVERFITTED` candidates: "
            + ", ".join(f"`{cid}`" for cid in overfit_ids)
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
    """Write the deterministic scout metrics artifact and optional report."""
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
    out_path.write_text(
        json.dumps(metrics, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )
    print(f"wrote {out_path}")

    if args.report is not None:
        report = render_report(metrics)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
        print(f"wrote {args.report}")


if __name__ == "__main__":
    main()
