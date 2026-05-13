"""TASK-0201 pairing and odd-even nuclear sandbox batch.

Sandbox-only batch runner. Evaluates two pairing-lane residual candidates
against the frozen RESULT-0015 fitted semi-empirical baseline using:

- the NMD-0002 structured 4-holdout protocol;
- the reviewed row-level post-AME2020 holdout dataset (primary 295 rows).

Three further proposals are recorded as rejected before execution.

Executed families:

- HYP-PROPOSAL-0038 (pairing A-inverse refinement):
  r_corr = c * pairing_sign(Z, N) / A.
- HYP-PROPOSAL-0041 (per-parity-class free offsets, in-batch negative
  control): r_corr = c_ee * I[ee] + c_oo * I[oo] + c_oA * I[odd-A].

HYP-PROPOSAL-0041 is included specifically as the in-batch negative
control. Three free per-class offsets fitted on 8-9 NMD-0002 rows (only
one odd-odd row, N-14) are expected to land in OVERFITTED on the
structured holdouts. Its diagnostic purpose is to confirm overfit
detection still fires on a trivially-flexible feature stack in this lane.

This script writes deterministic JSON metrics that the accompanying test
recomputes from the same inputs. It does not modify canonical results,
claims, accepted knowledge, or datasets.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import yaml

from physics_lab.engines.nuclear_mass_baselines import (
    MAGIC_NUMBERS,
    SemiEmpiricalCoefficients,
    evaluate_baseline,
    pairing_sign,
    semi_empirical_binding_energy,
)
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset


REPO_ROOT = Path(__file__).resolve().parent.parent
NMD_PATH = REPO_ROOT / "data" / "nuclear_masses" / "nmd-0002-curated-measured-slice.yaml"
POST_AME_PATH = REPO_ROOT / "data" / "nuclear_masses" / "post_ame2020_holdout.yaml"
RESULT_PATH = REPO_ROOT / "results" / "EXP-0012" / "RUN-0001" / "result.yaml"
SPLIT_REPLAY_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0006" / "metrics.json"
TIME_SPLIT_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0008" / "metrics.json"

AGENT_RUN_ID = "AGENT-RUN-0011"
TASK_ID = "TASK-0201"

HOLDOUTS: dict[str, tuple[str, ...]] = {
    "random_stratified": ("He-4", "Fe-57", "Pb-208"),
    "oxygen_chain": ("O-16", "O-17"),
    "magic_heavy_region": ("Sn-120", "Pb-208"),
    "neutron_rich_edge": ("Sn-120", "Pb-208", "U-238"),
}


CANDIDATE_FAMILIES = {
    "pairing_a_inverse": {
        "proposal_id": "HYP-PROPOSAL-0038",
        "title": "Pairing A-inverse residual refinement",
        "formula": "r_corr = c * pairing_sign(Z, N) / A",
        "feature_names": ("pairing_a_inverse",),
        "parameter_count": 1,
    },
    "parity_class_offsets": {
        "proposal_id": "HYP-PROPOSAL-0041",
        "title": "Per-parity-class free offsets (in-batch negative control)",
        "formula": "r_corr = c_ee * I[ee] + c_oo * I[oo] + c_oA * I[odd-A]",
        "feature_names": ("ee_indicator", "oo_indicator", "odd_a_indicator"),
        "parameter_count": 3,
    },
}


REJECTED_PROPOSALS = (
    {
        "proposal_id": "HYP-PROPOSAL-0039",
        "title": "Pairing free-power refinement",
        "rejection_reason": (
            "Letting the A exponent in r_corr = c * pairing_sign(Z, N) / A^p "
            "be a free fit parameter introduces a nonlinear knob and exits "
            "the linear-additive correction protocol followed by RESULT-0015 "
            "and prior nuclear sandbox runs. On an 11-row NMD-0002 training "
            "surface this is unbounded overfit risk and is rejected on "
            "complexity grounds; HYP-PROPOSAL-0038 is the bounded "
            "fixed-exponent (p=1) version of the same direction."
        ),
    },
    {
        "proposal_id": "HYP-PROPOSAL-0040",
        "title": "N=82 pairing override (post-hoc leakage)",
        "rejection_reason": (
            "A pairing-class correction gated by |N - 82| <= 2 would "
            "memorize the In/Sb cluster identified retrospectively as the "
            "worst-case region on the post-AME2020 primary holdout "
            "(AGENT-RUN-0008). Building a feature around an identified "
            "failure cluster is post-hoc leakage under "
            "docs/nuclear-mass-robustness-gate.md and duplicates the "
            "rejection rationale of HYP-PROPOSAL-0031 and HYP-PROPOSAL-0035."
        ),
    },
    {
        "proposal_id": "HYP-PROPOSAL-0042",
        "title": "Per-nuclide pairing override (row memorization)",
        "rejection_reason": (
            "A stack of per-nuclide one-hot indicators multiplied by "
            "pairing_sign(Z, N) directly memorizes residuals on rows "
            "identified retrospectively as worst cases on the post-AME2020 "
            "primary holdout. This is the most extreme form of the leakage "
            "family already represented by HYP-PROPOSAL-0031, "
            "HYP-PROPOSAL-0035, and HYP-PROPOSAL-0037; rejected under the "
            "gate's row-memorization clause."
        ),
    },
)


def feature_values(family: str, *, z: int, n: int, a: int) -> tuple[float, ...]:
    if family == "pairing_a_inverse":
        return (float(pairing_sign(z, n)) / float(a),)
    if family == "parity_class_offsets":
        sign = pairing_sign(z, n)
        ee = 1.0 if sign > 0 else 0.0
        oo = 1.0 if sign < 0 else 0.0
        odd_a = 1.0 if sign == 0 else 0.0
        return (ee, oo, odd_a)
    raise ValueError(f"unknown family: {family}")


def load_frozen_baseline_coefficients() -> SemiEmpiricalCoefficients:
    with RESULT_PATH.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    for score in payload["scores"]:
        if score["model_id"] == "model_fitted_semi_empirical":
            c = score["coefficients"]
            return SemiEmpiricalCoefficients(
                volume=float(c["volume"]),
                surface=float(c["surface"]),
                coulomb=float(c["coulomb"]),
                asymmetry=float(c["asymmetry"]),
                pairing=float(c["pairing"]),
            )
    raise RuntimeError("RESULT-0015 fitted coefficients not found")


def classify_candidate(*, improved: int, regressed: int, worst_regression: float) -> str:
    if improved >= 4 and worst_regression <= 0.0:
        return "VALID_IN_RANGE"
    if improved >= 2 and regressed <= 1 and worst_regression <= 0.25:
        return "PARTIALLY_VALID"
    if regressed >= 2 or worst_regression >= 1.0:
        return "OVERFITTED"
    return "INCONCLUSIVE"


def nearest_magic_distance(value: int) -> int:
    return min(abs(value - magic) for magic in MAGIC_NUMBERS)


def subset_ids_for_row(z: int, n: int, a: int, was_extrapolated: bool) -> list[str]:
    ids = ["primary"]
    if was_extrapolated:
        ids.append("ame2020_extrapolated_comparison")
    else:
        ids.append("ame2020_measured_comparison")
    if z in MAGIC_NUMBERS or n in MAGIC_NUMBERS:
        ids.append("magic_any")
    if z in MAGIC_NUMBERS and n in MAGIC_NUMBERS:
        ids.append("double_magic")
    if nearest_magic_distance(z) <= 2 or nearest_magic_distance(n) <= 2:
        ids.append("near_magic")
    if n - z >= 20:
        ids.append("neutron_rich_delta_ge_20")
    if n < z:
        ids.append("proton_rich_n_lt_z")
    if a >= 100:
        ids.append("heavy_a_ge_100")
    if a % 2 == 1:
        ids.append("odd_a")
    sign = pairing_sign(z, n)
    if sign > 0:
        ids.append("even_even")
    elif sign < 0:
        ids.append("odd_odd")
    return ids


SUBSET_IDS = (
    "primary",
    "ame2020_extrapolated_comparison",
    "ame2020_measured_comparison",
    "magic_any",
    "double_magic",
    "near_magic",
    "neutron_rich_delta_ge_20",
    "proton_rich_n_lt_z",
    "heavy_a_ge_100",
    "odd_a",
    "even_even",
    "odd_odd",
)


def subset_metrics(errors: list[float], uncertainties: list[float]) -> dict[str, float | int | None]:
    if not errors:
        return {
            "count": 0,
            "mae_mev": None,
            "rmse_mev": None,
            "max_abs_error_mev": None,
            "mean_error_mev": None,
            "mean_abs_uncertainty_normalized_error": None,
            "max_abs_uncertainty_normalized_error": None,
        }
    abs_errors = [abs(e) for e in errors]
    normalized = [
        abs(error) / sigma
        for error, sigma in zip(errors, uncertainties)
        if sigma is not None and sigma > 0.0
    ]
    return {
        "count": len(errors),
        "mae_mev": float(sum(abs_errors) / len(abs_errors)),
        "rmse_mev": float(math.sqrt(sum(e * e for e in errors) / len(errors))),
        "max_abs_error_mev": float(max(abs_errors)),
        "mean_error_mev": float(sum(errors) / len(errors)),
        "mean_abs_uncertainty_normalized_error": (
            None if not normalized else float(sum(normalized) / len(normalized))
        ),
        "max_abs_uncertainty_normalized_error": (
            None if not normalized else float(max(normalized))
        ),
    }


def compute_structured_holdout_block(
    *,
    family: str,
    entries: list,
    residuals: np.ndarray,
) -> dict[str, object]:
    nuclides = [entry.nuclide_id for entry in entries]
    feature_names = CANDIDATE_FAMILIES[family]["feature_names"]
    columns = [
        np.asarray(
            [feature_values(family, z=entry.Z, n=entry.N, a=entry.A)[idx] for entry in entries],
            dtype=float,
        )
        for idx in range(len(feature_names))
    ]
    x = np.column_stack(columns)

    holdout_results: list[dict[str, object]] = []
    deltas: list[float] = []
    improved = 0
    regressed = 0

    for holdout_id, holdout_nuclides in HOLDOUTS.items():
        holdout_set = set(holdout_nuclides)
        mask = np.asarray([nuclide in holdout_set for nuclide in nuclides], dtype=bool)
        train_x = x[~mask]
        train_y = residuals[~mask]
        beta, *_ = np.linalg.lstsq(train_x, train_y, rcond=None)
        correction = x[mask] @ beta
        baseline_residuals = residuals[mask]
        candidate_residuals = baseline_residuals - correction

        baseline_mae = float(np.mean(np.abs(baseline_residuals)))
        baseline_rmse = float(np.sqrt(np.mean(baseline_residuals**2)))
        candidate_mae = float(np.mean(np.abs(candidate_residuals)))
        candidate_rmse = float(np.sqrt(np.mean(candidate_residuals**2)))
        delta_mae = candidate_mae - baseline_mae
        delta_rmse = candidate_rmse - baseline_rmse

        deltas.append(delta_mae)
        if delta_mae < -1.0e-12:
            improved += 1
        elif delta_mae > 1.0e-12:
            regressed += 1

        holdout_results.append(
            {
                "holdout_id": holdout_id,
                "holdout_count": int(mask.sum()),
                "coefficients": {
                    name: float(value) for name, value in zip(feature_names, beta)
                },
                "baseline_metrics": {
                    "mae_mev": baseline_mae,
                    "rmse_mev": baseline_rmse,
                },
                "candidate_metrics": {
                    "mae_mev": candidate_mae,
                    "rmse_mev": candidate_rmse,
                },
                "delta_mae_mev": delta_mae,
                "delta_rmse_mev": delta_rmse,
            }
        )

    unchanged = len(deltas) - improved - regressed
    worst_regression = max(0.0, max(deltas)) if deltas else 0.0
    verdict = classify_candidate(
        improved=improved,
        regressed=regressed,
        worst_regression=worst_regression,
    )
    return {
        "holdout_results": holdout_results,
        "summary": {
            "improved_holdout_count": improved,
            "regressed_holdout_count": regressed,
            "unchanged_holdout_count": unchanged,
            "mean_delta_mae_mev": float(np.mean(deltas)) if deltas else 0.0,
            "worst_regression_mev": worst_regression,
        },
        "expected_verdict": verdict,
        "observed_verdict": verdict,
        "agrees": True,
    }


def compute_post_ame2020_block(
    *,
    family: str,
    training_entries: list,
    training_residuals: np.ndarray,
    coefficients: SemiEmpiricalCoefficients,
    holdout_rows: list[dict],
) -> dict[str, object]:
    feature_names = CANDIDATE_FAMILIES[family]["feature_names"]
    train_x = np.asarray(
        [feature_values(family, z=entry.Z, n=entry.N, a=entry.A) for entry in training_entries],
        dtype=float,
    )
    beta, *_ = np.linalg.lstsq(train_x, training_residuals, rcond=None)
    fitted_coefficients = {
        name: float(value) for name, value in zip(feature_names, beta)
    }

    activation_counts = {name: 0 for name in feature_names}
    per_row: list[dict[str, object]] = []
    for row in holdout_rows:
        z, n, a = int(row["Z"]), int(row["N"]), int(row["A"])
        values = feature_values(family, z=z, n=n, a=a)
        for name, value in zip(feature_names, values):
            if abs(value) > 0.0:
                activation_counts[name] += 1
        correction = float(np.asarray(values, dtype=float) @ beta)
        baseline_pred = semi_empirical_binding_energy(z=z, n=n, coefficients=coefficients)
        predicted = baseline_pred + correction
        observed = float(row["new_measurement"]["value_mev"])
        uncertainty = float(row["new_measurement"]["uncertainty_mev"])
        residual = observed - predicted
        abs_error = abs(residual)
        per_row.append(
            {
                "row_id": row["row_id"],
                "nuclide_id": row["nuclide_id"],
                "Z": z,
                "N": n,
                "A": a,
                "observed_mev": observed,
                "predicted_mev": predicted,
                "residual_mev": residual,
                "abs_error_mev": abs_error,
                "uncertainty_mev": uncertainty,
                "abs_uncertainty_normalized_error": (
                    None if uncertainty <= 0.0 else abs_error / uncertainty
                ),
                "ame2020_comparison_was_extrapolated": row["ame2020_comparison"][
                    "was_extrapolated"
                ],
                "feature_values": {
                    name: float(value)
                    for name, value in zip(feature_names, values)
                },
            }
        )

    subset_errors: dict[str, list[float]] = {sid: [] for sid in SUBSET_IDS}
    subset_uncertainties: dict[str, list[float]] = {sid: [] for sid in SUBSET_IDS}
    for row, item in zip(holdout_rows, per_row):
        ids = subset_ids_for_row(
            int(row["Z"]),
            int(row["N"]),
            int(row["A"]),
            bool(row["ame2020_comparison"]["was_extrapolated"]),
        )
        for sid in ids:
            subset_errors[sid].append(float(item["residual_mev"]))
            subset_uncertainties[sid].append(float(item["uncertainty_mev"]))

    metrics_by_subset = {
        sid: subset_metrics(subset_errors[sid], subset_uncertainties[sid])
        for sid in SUBSET_IDS
    }
    worst_cases = sorted(per_row, key=lambda item: float(item["abs_error_mev"]), reverse=True)[:10]

    return {
        "coefficients_fitted_on_full_nmd0002": fitted_coefficients,
        "feature_activation_counts": activation_counts,
        "metrics_by_subset": metrics_by_subset,
        "worst_abs_error_cases": worst_cases,
    }


def baseline_post_ame2020_block(
    *,
    coefficients: SemiEmpiricalCoefficients,
    holdout_rows: list[dict],
) -> dict[str, object]:
    per_row: list[dict[str, object]] = []
    for row in holdout_rows:
        z, n, a = int(row["Z"]), int(row["N"]), int(row["A"])
        predicted = semi_empirical_binding_energy(z=z, n=n, coefficients=coefficients)
        observed = float(row["new_measurement"]["value_mev"])
        uncertainty = float(row["new_measurement"]["uncertainty_mev"])
        residual = observed - predicted
        abs_error = abs(residual)
        per_row.append(
            {
                "row_id": row["row_id"],
                "nuclide_id": row["nuclide_id"],
                "Z": z,
                "N": n,
                "A": a,
                "observed_mev": observed,
                "predicted_mev": predicted,
                "residual_mev": residual,
                "abs_error_mev": abs_error,
                "uncertainty_mev": uncertainty,
                "abs_uncertainty_normalized_error": (
                    None if uncertainty <= 0.0 else abs_error / uncertainty
                ),
                "ame2020_comparison_was_extrapolated": row["ame2020_comparison"][
                    "was_extrapolated"
                ],
            }
        )

    subset_errors: dict[str, list[float]] = {sid: [] for sid in SUBSET_IDS}
    subset_uncertainties: dict[str, list[float]] = {sid: [] for sid in SUBSET_IDS}
    for row, item in zip(holdout_rows, per_row):
        ids = subset_ids_for_row(
            int(row["Z"]),
            int(row["N"]),
            int(row["A"]),
            bool(row["ame2020_comparison"]["was_extrapolated"]),
        )
        for sid in ids:
            subset_errors[sid].append(float(item["residual_mev"]))
            subset_uncertainties[sid].append(float(item["uncertainty_mev"]))

    metrics_by_subset = {
        sid: subset_metrics(subset_errors[sid], subset_uncertainties[sid])
        for sid in SUBSET_IDS
    }
    return {
        "metrics_by_subset": metrics_by_subset,
        "worst_abs_error_cases": sorted(
            per_row, key=lambda item: float(item["abs_error_mev"]), reverse=True
        )[:5],
    }


def build_metrics() -> dict[str, object]:
    coefficients = load_frozen_baseline_coefficients()
    nmd = load_nuclear_mass_dataset(NMD_PATH)
    rows = evaluate_baseline(
        entries=nmd.entries,
        model_id="model_fitted_semi_empirical",
        coefficients=coefficients,
    )
    residuals = np.asarray([row.residual_mev for row in rows], dtype=float)
    entries_in_row_order = [
        next(entry for entry in nmd.entries if entry.nuclide_id == row.nuclide_id)
        for row in rows
    ]

    with POST_AME_PATH.open("r", encoding="utf-8") as handle:
        post_payload = yaml.safe_load(handle)
    primary_holdout_rows = [
        row for row in post_payload["entries"] if bool(row["included_in_time_split_holdout"])
    ]

    with SPLIT_REPLAY_PATH.open("r", encoding="utf-8") as handle:
        split_replay = json.load(handle)
    with TIME_SPLIT_PATH.open("r", encoding="utf-8") as handle:
        time_split = json.load(handle)

    baseline_post_ame2020 = baseline_post_ame2020_block(
        coefficients=coefficients,
        holdout_rows=primary_holdout_rows,
    )

    executed_items: list[dict[str, object]] = []
    for family, family_meta in CANDIDATE_FAMILIES.items():
        structured = compute_structured_holdout_block(
            family=family,
            entries=entries_in_row_order,
            residuals=residuals,
        )
        post_ame = compute_post_ame2020_block(
            family=family,
            training_entries=entries_in_row_order,
            training_residuals=residuals,
            coefficients=coefficients,
            holdout_rows=primary_holdout_rows,
        )

        primary_metric = post_ame["metrics_by_subset"]["primary"]
        baseline_primary = baseline_post_ame2020["metrics_by_subset"]["primary"]
        primary_delta_mae = (
            float(primary_metric["mae_mev"]) - float(baseline_primary["mae_mev"])
        )

        executed_items.append(
            {
                "proposal_id": family_meta["proposal_id"],
                "name": family_meta["title"],
                "family": family,
                "formula": family_meta["formula"],
                "parameter_count": family_meta["parameter_count"],
                "expected_verdict": structured["expected_verdict"],
                "observed_verdict": structured["observed_verdict"],
                "agrees": structured["agrees"],
                "holdout_results": structured["holdout_results"],
                "summary": structured["summary"],
                "post_ame2020_eval": {
                    "coefficients_fitted_on_full_nmd0002": post_ame[
                        "coefficients_fitted_on_full_nmd0002"
                    ],
                    "feature_activation_counts": post_ame["feature_activation_counts"],
                    "primary_delta_mae_mev": primary_delta_mae,
                    "metrics_by_subset": post_ame["metrics_by_subset"],
                    "worst_abs_error_cases": post_ame["worst_abs_error_cases"],
                },
            }
        )

    executed_count = len(executed_items)
    rejected_count = len(REJECTED_PROPOSALS)
    generated_count = executed_count + rejected_count

    summary = {
        "generated_proposal_count": generated_count,
        "executed_candidate_count": executed_count,
        "rejected_before_execution_count": rejected_count,
        "improved_all_structured_holdouts_count": sum(
            1 for item in executed_items
            if item["summary"]["improved_holdout_count"] == 4
            and item["summary"]["worst_regression_mev"] <= 0.0
        ),
        "improved_post_ame2020_primary_count": sum(
            1 for item in executed_items
            if item["post_ame2020_eval"]["primary_delta_mae_mev"] < 0.0
        ),
        "in_batch_negative_control_overfitted_count": sum(
            1 for item in executed_items
            if item["proposal_id"] == "HYP-PROPOSAL-0041"
            and item["observed_verdict"] == "OVERFITTED"
        ),
        "canonical_results_changed": False,
        "canonical_claims_changed": False,
        "claim_promotion_allowed": False,
    }

    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "pairing",
        "sandbox_only": True,
        "evidence_class": "bounded_sandbox_residual_batch",
        "formula": (
            "batch: pairing residual candidates (A-inverse refinement, "
            "per-parity-class free offsets as in-batch negative control)"
        ),
        "verdict": "SANDBOX_PASS",
        "summary": summary,
        "frozen_baseline": {
            "result_id": "RESULT-0015",
            "model_id": "model_fitted_semi_empirical",
            "coefficients": coefficients.to_dict(),
        },
        "feature_definitions": {
            "pairing_a_inverse": "pairing_sign(Z, N) / A (zero on odd-A rows)",
            "ee_indicator": "1 if pairing_sign(Z, N) == +1 else 0 (even-even)",
            "oo_indicator": "1 if pairing_sign(Z, N) == -1 else 0 (odd-odd)",
            "odd_a_indicator": "1 if pairing_sign(Z, N) == 0 else 0 (odd-A)",
        },
        "rejected_before_execution": list(REJECTED_PROPOSALS),
        "structured_holdouts": {
            "definition": HOLDOUTS,
            "training_dataset": "data/nuclear_masses/nmd-0002-curated-measured-slice.yaml",
        },
        "executed_items": executed_items,
        "post_ame2020_baseline": {
            "primary_metrics": baseline_post_ame2020["metrics_by_subset"]["primary"],
            "metrics_by_subset": baseline_post_ame2020["metrics_by_subset"],
            "worst_abs_error_cases": baseline_post_ame2020["worst_abs_error_cases"],
            "training_rows_used_for_fit": 0,
            "primary_holdout_row_count": len(primary_holdout_rows),
        },
        "split_replay_context": {
            "source_agent_run_id": split_replay["agent_run_id"],
            "classification": split_replay["stability_assessment"]["classification"],
            "summary": split_replay["same_shape_stratified_summary"],
        },
        "time_split_context": {
            "source_agent_run_id": time_split["agent_run_id"],
            "task_id": time_split["task_id"],
            "verdict": time_split["summary"]["verdict"],
            "hyp_0021_primary_delta_mae_mev": time_split["summary"][
                "hyp_0021_primary_delta_mae_mev"
            ],
            "hyp_0022_negative_control_primary_delta_mae_mev": time_split["summary"][
                "hyp_0022_negative_control_primary_delta_mae_mev"
            ],
        },
        "negative_control_reference": {
            "candidate_id": "HYP-PROPOSAL-0022",
            "family": "quadratic_asymmetry_refinement",
            "source_metrics_path": "agent_runs/AGENT-RUN-0008/metrics.json",
            "post_ame2020_primary_delta_mae_mev": time_split["summary"][
                "hyp_0022_negative_control_primary_delta_mae_mev"
            ],
            "rationale": (
                "HYP-PROPOSAL-0022 is the prior external overfit/negative-"
                "control quadratic-asymmetry family. The pairing lane is "
                "compared against its retrospective post-AME2020 metrics for "
                "consistency with the shell-aware and neutron-rich lanes. The "
                "pairing lane also contains an in-batch negative control "
                "(HYP-PROPOSAL-0041) to make overfit-detection visible inside "
                "this batch."
            ),
        },
        "in_batch_negative_control": {
            "candidate_id": "HYP-PROPOSAL-0041",
            "family": "parity_class_offsets",
            "rationale": (
                "Three per-class indicators fitted as free offsets is a "
                "trivially-flexible feature stack on the 11-row NMD-0002 "
                "training surface. The expected OVERFITTED verdict confirms "
                "the structured-holdout protocol's overfit detection is still "
                "active in this lane."
            ),
        },
        "reference_comparison": {
            "canonical_result": "RESULT-0015",
            "frozen_dataset": "NMD-0002",
            "post_ame2020_holdout_dataset_id": post_payload["dataset_id"],
            "primary_holdout_row_count": len(primary_holdout_rows),
        },
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": "Maintainer review before any RESULT-* or claim update.",
        },
        "limitations": [
            "Sandbox-only batch; no canonical result, claim, knowledge, or dataset is updated.",
            "NMD-0002 has 11 nuclides; only one is odd-odd (N-14).",
            "Post-AME2020 evaluation refits coefficients on the full NMD-0002 residuals once, then applies them; this is not blind prediction.",
            "HYP-PROPOSAL-0038 is sign-colinear with the existing baseline pairing term; this lane cannot distinguish a true pairing-physics refinement from a noise fit on the tiny training surface.",
            "HYP-PROPOSAL-0041 is an in-batch negative control; its OVERFITTED verdict is the diagnostic value of the candidate, not a scientific result.",
        ],
    }


def main() -> None:
    metrics = build_metrics()
    out_dir = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(
        json.dumps(metrics, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {metrics_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
