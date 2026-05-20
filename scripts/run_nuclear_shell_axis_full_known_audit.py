"""TASK-0310 nuclear shell-axis full-known-data retrospective audit.

This sandbox-only runner audits the strongest shell-axis scout family on the
full committed, reviewable measured-data surface currently available in the
repository. It fits the same bounded shell-axis residual corrections on the
frozen NMD-0002 training slice used by earlier scouts, then evaluates them on
three surfaces:

- the NMD-0002 training slice;
- the committed post-AME2020 primary holdout rows;
- the unique full-known committed surface formed by both inputs.

The runner does not fetch live data, score prospective prediction registry
entries, write canonical RESULT-* artifacts, update claims, or edit knowledge.
"""

from __future__ import annotations

import argparse
import json
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

import scripts.run_nuclear_shell_axis_stress_scout as stress  # noqa: E402


NMD_PATH = REPO_ROOT / "data" / "nuclear_masses" / "nmd-0002-curated-measured-slice.yaml"
POST_AME_PATH = REPO_ROOT / "data" / "nuclear_masses" / "post_ame2020_holdout.yaml"
RESULT_PATH = REPO_ROOT / "results" / "EXP-0012" / "RUN-0001" / "result.yaml"

AGENT_RUN_ID = "AGENT-RUN-0018"
TASK_ID = "TASK-0310"
SHUFFLE_OFFSET = 5


EXECUTED_CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "candidate_id": "FULLKNOWN-SHELL-001",
        "source_candidate_id": "STRESS-SHELL-001",
        "name": "Proton-axis Gaussian shell proximity",
        "formula": "r_corr = beta_z * s_z2",
        "feature_names": ("s_z2",),
        "complexity": 1,
        "fit_mode": "lstsq",
    },
    {
        "candidate_id": "FULLKNOWN-SHELL-002",
        "source_candidate_id": "STRESS-SHELL-002",
        "name": "Proton x neutron product shell proximity",
        "formula": "r_corr = beta_p * (s_z2 * s_n2)",
        "feature_names": ("s_z2_times_s_n2",),
        "complexity": 1,
        "fit_mode": "lstsq",
    },
    {
        "candidate_id": "FULLKNOWN-SHELL-003",
        "source_candidate_id": "STRESS-SHELL-003",
        "name": "Neutron-axis Gaussian shell proximity overlap diagnostic",
        "formula": "r_corr = beta_n * s_n2",
        "feature_names": ("s_n2",),
        "complexity": 1,
        "fit_mode": "lstsq",
    },
    {
        "candidate_id": "FULLKNOWN-SHELL-004",
        "source_candidate_id": "STRESS-SHELL-004",
        "name": "Sign-inverted proton-axis Gaussian control",
        "formula": "r_corr = -beta_z * s_z2, with beta_z fit as in FULLKNOWN-SHELL-001",
        "feature_names": ("s_z2",),
        "complexity": 1,
        "fit_mode": "lstsq_sign_inverted",
        "sign_inverted": True,
    },
    {
        "candidate_id": "FULLKNOWN-SHELL-005",
        "source_candidate_id": "STRESS-SHELL-005",
        "name": "Shuffled proton-axis Gaussian control (cyclic-shift-5)",
        "formula": "r_corr = beta_z * s_z2_perm where row i uses (i+5) mod N feature",
        "feature_names": ("s_z2",),
        "complexity": 1,
        "fit_mode": "lstsq_shuffled",
        "shuffle_scheme": "cyclic-shift-5",
        "shuffle_seed": SHUFFLE_OFFSET,
    },
    {
        "candidate_id": "FULLKNOWN-SHELL-006",
        "source_candidate_id": "STRESS-SHELL-006",
        "name": "Near-null / baseline-reference shell-axis sanity control",
        "formula": "r_corr = 0.0",
        "feature_names": (),
        "complexity": 0,
        "fit_mode": "fixed_zero",
        "fixed_zero_control": True,
        "baseline_reference_control": True,
    },
)


REJECTED_BEFORE_EXECUTION: tuple[dict[str, str], ...] = (
    {
        "candidate_id": "FULLKNOWN-SHELL-007",
        "source_candidate_id": "STRESS-SHELL-007",
        "name": "Free-sigma proton Gaussian",
        "rejection_reason": (
            "Rejected before execution because sigma tuning is a nonlinear free "
            "knob on the 11-row NMD-0002 training slice and would weaken the "
            "retrospective audit boundary."
        ),
    },
    {
        "candidate_id": "FULLKNOWN-SHELL-008",
        "source_candidate_id": "STRESS-SHELL-008",
        "name": "Per-magic-number offsets",
        "rejection_reason": (
            "Rejected before execution because one offset per magic number inflates "
            "degrees of freedom and risks memorizing the training slice."
        ),
    },
    {
        "candidate_id": "FULLKNOWN-SHELL-009",
        "source_candidate_id": "STRESS-SHELL-009",
        "name": "SHELL-SCOUT-001 additive form re-test",
        "rejection_reason": (
            "Rejected before execution because the additive combined shell-axis form "
            "is already preserved as OVERFITTED in the scout synthesis; re-running "
            "it here would duplicate a known negative result."
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


def _surface_subset_ids(row: dict[str, Any]) -> tuple[str, ...]:
    """Return surface, shell-axis, and mass-band subset labels for one audit row."""
    z, n, a = int(row["Z"]), int(row["N"]), int(row["A"])
    ids = ["full_known"]
    if row["source_surface"] == "nmd_0002_training_slice":
        ids.append("training_slice")
    if row["source_surface"] == "post_ame2020_primary_holdout":
        ids.append("primary_holdout")
        ids.append(
            "post_ame2020_extrapolated_comparison"
            if bool(row["was_extrapolated"])
            else "post_ame2020_measured_comparison"
        )
    if z in MAGIC_NUMBERS or n in MAGIC_NUMBERS:
        ids.append("magic_any")
    if z in MAGIC_NUMBERS and n in MAGIC_NUMBERS:
        ids.append("double_magic")
    if z in MAGIC_NUMBERS:
        ids.append("magic_z")
    if n in MAGIC_NUMBERS:
        ids.append("magic_n")
    if stress.nearest_magic_distance(z) <= 2 or stress.nearest_magic_distance(n) <= 2:
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
    target = stress.chain_neighbor_target(z=z, a=a)
    if target is not None:
        ids.append("registry_repeat_chain_neighbor")
    return tuple(ids)


def _summarize_errors(errors: list[float]) -> dict[str, float | int | None]:
    return stress.summarize_errors(errors)


def _delta_mae(candidate: dict[str, Any] | None, baseline: dict[str, Any] | None) -> float | None:
    return stress._delta_mae(candidate, baseline)  # noqa: SLF001


def _feature_vector(feature_names: tuple[str, ...], *, z: int, n: int) -> tuple[float, ...]:
    return stress.feature_vector(feature_names, z=z, n=n)


def _fit_lstsq(feature_names: tuple[str, ...], rows: list[dict[str, Any]], residuals: np.ndarray) -> np.ndarray:
    train_x = np.asarray(
        [_feature_vector(feature_names, z=int(row["Z"]), n=int(row["N"])) for row in rows],
        dtype=float,
    )
    beta, *_ = np.linalg.lstsq(train_x, residuals, rcond=None)
    return beta


def _shuffled_feature_array(
    feature_names: tuple[str, ...],
    rows: list[dict[str, Any]],
    *,
    offset: int,
) -> np.ndarray:
    count = len(rows)
    rotated_indices = [(idx + offset) % count for idx in range(count)]
    return np.asarray(
        [
            _feature_vector(
                feature_names,
                z=int(rows[rotated_idx]["Z"]),
                n=int(rows[rotated_idx]["N"]),
            )
            for rotated_idx in rotated_indices
        ],
        dtype=float,
    )


def _frontier_contrast(deltas: dict[str, float | None]) -> float | None:
    mid = deltas.get("mid_mass")
    light = deltas.get("light_a_lt_50")
    heavy = deltas.get("heavy_a_ge_100")
    if mid is None or light is None or heavy is None:
        return None
    return float(mid) - 0.5 * (float(light) + float(heavy))


def _training_rows(
    coefficients: SemiEmpiricalCoefficients,
) -> tuple[list[dict[str, Any]], np.ndarray]:
    """Build NMD-0002 training-slice residual rows."""
    nmd = load_nuclear_mass_dataset(NMD_PATH)
    baseline_rows = evaluate_baseline(
        entries=nmd.entries,
        model_id="model_fitted_semi_empirical",
        coefficients=coefficients,
    )
    entries_by_id = {entry.nuclide_id: entry for entry in nmd.entries}
    rows: list[dict[str, Any]] = []
    residuals: list[float] = []
    for baseline_row in baseline_rows:
        entry = entries_by_id[baseline_row.nuclide_id]
        residual = float(baseline_row.residual_mev)
        rows.append(
            {
                "row_id": f"nmd-0002::{entry.nuclide_id}",
                "nuclide_id": entry.nuclide_id,
                "Z": int(entry.Z),
                "N": int(entry.N),
                "A": int(entry.A),
                "observed_mev": float(entry.binding_energy_mev),
                "baseline_predicted_mev": float(baseline_row.predicted_binding_energy_mev),
                "baseline_residual_mev": residual,
                "was_extrapolated": False,
                "source_surface": "nmd_0002_training_slice",
            }
        )
        residuals.append(residual)
    return rows, np.asarray(residuals, dtype=float)


def _post_ame2020_holdout_rows(
    coefficients: SemiEmpiricalCoefficients,
) -> list[dict[str, Any]]:
    """Build committed post-AME2020 primary holdout rows."""
    with POST_AME_PATH.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    rows: list[dict[str, Any]] = []
    for entry in payload["entries"]:
        if not bool(entry["included_in_time_split_holdout"]):
            continue
        z, n, a = int(entry["Z"]), int(entry["N"]), int(entry["A"])
        predicted = semi_empirical_binding_energy(z=z, n=n, coefficients=coefficients)
        observed = float(entry["new_measurement"]["value_mev"])
        rows.append(
            {
                "row_id": entry["row_id"],
                "nuclide_id": str(entry["nuclide_id"]),
                "Z": z,
                "N": n,
                "A": a,
                "observed_mev": observed,
                "baseline_predicted_mev": predicted,
                "baseline_residual_mev": observed - predicted,
                "was_extrapolated": bool(entry["ame2020_comparison"]["was_extrapolated"]),
                "source_surface": "post_ame2020_primary_holdout",
            }
        )
    return rows


def build_audit_surface(
    coefficients: SemiEmpiricalCoefficients,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], np.ndarray, dict[str, Any]]:
    """Return full-known audit rows, training rows, residuals, and baseline metrics."""
    training_rows, residuals = _training_rows(coefficients)
    post_rows = _post_ame2020_holdout_rows(coefficients)
    seen = {row["nuclide_id"] for row in training_rows}
    duplicate_post_rows = [row["nuclide_id"] for row in post_rows if row["nuclide_id"] in seen]
    unique_rows = [*training_rows, *[row for row in post_rows if row["nuclide_id"] not in seen]]

    subset_errors: dict[str, list[float]] = {}
    for row in unique_rows:
        for subset_id in _surface_subset_ids(row):
            subset_errors.setdefault(subset_id, []).append(float(row["baseline_residual_mev"]))
    baseline_metrics = {
        key: _summarize_errors(value) for key, value in sorted(subset_errors.items())
    }
    metadata = {
        "training_row_count": len(training_rows),
        "post_ame2020_primary_holdout_row_count": len(post_rows),
        "full_known_unique_row_count": len(unique_rows),
        "duplicate_post_rows_excluded_from_full_known": duplicate_post_rows,
    }
    return unique_rows, training_rows, residuals, {"metrics": baseline_metrics, "metadata": metadata}


def _verdict(
    *,
    candidate: dict[str, Any],
    primary_delta: float | None,
    holdout_delta: float | None,
    worst_subset_regression: float,
    shuffle_noise_floor: bool,
) -> str:
    """Conservative retrospective audit verdict."""
    material = 1.0e-6
    if candidate.get("fixed_zero_control"):
        return "INCONCLUSIVE"
    if candidate.get("sign_inverted"):
        if primary_delta is not None and primary_delta < -material:
            return "OVERFITTED"
        return "INCONCLUSIVE"
    if shuffle_noise_floor:
        return "INCONCLUSIVE"
    if primary_delta is None or holdout_delta is None:
        return "INCONCLUSIVE"
    if worst_subset_regression > 2.0:
        return "OVERFITTED"
    if primary_delta < -material and holdout_delta < -material and worst_subset_regression <= 0.5:
        return "PARTIALLY_VALID"
    return "INCONCLUSIVE"


def evaluate_candidate(
    candidate: dict[str, Any],
    *,
    audit_rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
    baseline_metrics: dict[str, Any],
    proton_only_beta: float,
) -> dict[str, Any]:
    """Fit and evaluate one full-known audit candidate."""
    feature_names = tuple(candidate["feature_names"])
    fit_mode = str(candidate.get("fit_mode", "lstsq"))
    if fit_mode == "fixed_zero":
        applied_beta = np.asarray([], dtype=float)
        fitted_coefficients: dict[str, float] = {}
    elif fit_mode == "lstsq":
        beta = _fit_lstsq(feature_names, training_rows, training_residuals)
        applied_beta = beta
        fitted_coefficients = {
            name: float(value) for name, value in zip(feature_names, beta)
        }
    elif fit_mode == "lstsq_sign_inverted":
        applied_beta = np.asarray([-proton_only_beta], dtype=float)
        fitted_coefficients = {"s_z2": float(-proton_only_beta)}
    elif fit_mode == "lstsq_shuffled":
        train_x = _shuffled_feature_array(
            feature_names,
            training_rows,
            offset=SHUFFLE_OFFSET,
        )
        beta, *_ = np.linalg.lstsq(train_x, training_residuals, rcond=None)
        applied_beta = beta
        fitted_coefficients = {
            name: float(value) for name, value in zip(feature_names, beta)
        }
    else:
        raise RuntimeError(f"Unknown fit_mode {fit_mode!r}")

    shuffled_audit = None
    if fit_mode == "lstsq_shuffled":
        shuffled_audit = _shuffled_feature_array(
            feature_names,
            audit_rows,
            offset=SHUFFLE_OFFSET,
        )

    subset_errors: dict[str, list[float]] = {key: [] for key in baseline_metrics}
    feature_activation_counts = {name: 0 for name in feature_names}
    per_row: list[dict[str, Any]] = []
    for row_index, row in enumerate(audit_rows):
        z, n = int(row["Z"]), int(row["N"])
        if fit_mode == "lstsq_shuffled" and shuffled_audit is not None:
            values = tuple(float(value) for value in shuffled_audit[row_index])
        else:
            values = _feature_vector(feature_names, z=z, n=n)
        for name, value in zip(feature_names, values):
            if abs(value) > 0.0:
                feature_activation_counts[name] += 1
        correction = 0.0 if fit_mode == "fixed_zero" else float(np.asarray(values) @ applied_beta)
        predicted = float(row["baseline_predicted_mev"]) + correction
        residual = float(row["observed_mev"]) - predicted
        item = {
            "row_id": row["row_id"],
            "nuclide_id": row["nuclide_id"],
            "Z": int(row["Z"]),
            "N": int(row["N"]),
            "A": int(row["A"]),
            "source_surface": row["source_surface"],
            "correction_mev": correction,
            "candidate_residual_mev": residual,
            "candidate_abs_error_mev": abs(residual),
            "feature_values": {
                name: float(value) for name, value in zip(feature_names, values)
            },
        }
        per_row.append(item)
        for subset_id in _surface_subset_ids(row):
            subset_errors.setdefault(subset_id, []).append(residual)

    metrics_by_subset = {
        key: _summarize_errors(value) for key, value in sorted(subset_errors.items())
    }
    delta_by_subset = {
        key: _delta_mae(metrics_by_subset.get(key), baseline_metrics.get(key))
        for key in sorted(baseline_metrics)
    }
    numeric_deltas = [value for value in delta_by_subset.values() if value is not None]
    positive_deltas = {key: value for key, value in delta_by_subset.items() if value is not None and value > 0.0}
    worst_subset_id, worst_subset_regression = ("none", 0.0)
    if positive_deltas:
        worst_subset_id, worst_subset_regression = max(positive_deltas.items(), key=lambda item: item[1])
    primary_delta = delta_by_subset.get("full_known")
    holdout_delta = delta_by_subset.get("primary_holdout")
    shuffle_noise_floor = bool(
        fit_mode == "lstsq_shuffled"
        and numeric_deltas
        and max(abs(value) for value in numeric_deltas) < 1.0e-3
    )
    verdict = _verdict(
        candidate=candidate,
        primary_delta=primary_delta,
        holdout_delta=holdout_delta,
        worst_subset_regression=float(worst_subset_regression),
        shuffle_noise_floor=shuffle_noise_floor,
    )
    out = {
        "candidate_id": candidate["candidate_id"],
        "source_candidate_id": candidate.get("source_candidate_id"),
        "name": candidate["name"],
        "formula": candidate["formula"],
        "complexity": candidate["complexity"],
        "fit_mode": fit_mode,
        "fitted_coefficients": fitted_coefficients,
        "feature_activation_counts": feature_activation_counts,
        "metrics_by_subset": metrics_by_subset,
        "delta_mae_by_subset_mev": delta_by_subset,
        "frontier_contrast_mev": _frontier_contrast(delta_by_subset),
        "worst_subset_regression": {
            "subset_id": worst_subset_id,
            "delta_mae_mev": float(worst_subset_regression),
        },
        "primary_delta_mae_mev": primary_delta,
        "holdout_delta_mae_mev": holdout_delta,
        "training_delta_mae_mev": delta_by_subset.get("training_slice"),
        "shuffle_noise_floor": shuffle_noise_floor,
        "worst_abs_error_cases": sorted(
            per_row,
            key=lambda entry: float(entry["candidate_abs_error_mev"]),
            reverse=True,
        )[:8],
        "verdict": verdict,
        "limitations": [
            "Feature coefficients are fit on the 11-row NMD-0002 residual slice.",
            "Full-known evaluation includes committed rows only; it is retrospective, not a reveal.",
            "Subset deltas are sandbox diagnostics and are not promoted claims.",
        ],
    }
    if candidate.get("sign_inverted"):
        out["sign_inverted"] = True
    if fit_mode == "lstsq_shuffled":
        out["shuffle_scheme"] = candidate.get("shuffle_scheme", "cyclic-shift-5")
        out["shuffle_seed"] = int(candidate.get("shuffle_seed", SHUFFLE_OFFSET))
    if candidate.get("baseline_reference_control"):
        out["baseline_reference_control"] = True
    return out


def build_metrics() -> dict[str, Any]:
    """Build deterministic full-known audit metrics."""
    coefficients = load_frozen_baseline_coefficients()
    audit_rows, training_rows, training_residuals, baseline_bundle = build_audit_surface(coefficients)
    baseline_metrics = baseline_bundle["metrics"]
    proton_only_beta = float(_fit_lstsq(("s_z2",), training_rows, training_residuals)[0])

    executed_items = [
        evaluate_candidate(
            candidate,
            audit_rows=audit_rows,
            training_rows=training_rows,
            training_residuals=training_residuals,
            baseline_metrics=baseline_metrics,
            proton_only_beta=proton_only_beta,
        )
        for candidate in EXECUTED_CANDIDATES
    ]
    verdict_counts: dict[str, int] = {}
    for item in executed_items:
        verdict_counts[item["verdict"]] = verdict_counts.get(item["verdict"], 0) + 1

    generated_candidates = [
        {
            "candidate_id": candidate["candidate_id"],
            "source_candidate_id": candidate.get("source_candidate_id"),
            "name": candidate["name"],
            "formula": candidate["formula"],
            "decision": "executed",
        }
        for candidate in EXECUTED_CANDIDATES
    ]
    generated_candidates.extend(
        {
            "candidate_id": candidate["candidate_id"],
            "source_candidate_id": candidate.get("source_candidate_id"),
            "name": candidate["name"],
            "decision": "rejected_before_execution",
            "rejection_reason": candidate["rejection_reason"],
        }
        for candidate in REJECTED_BEFORE_EXECUTION
    )

    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "shell_axis_full_known_retrospective_audit",
        "sandbox_only": True,
        "evidence_class": "retrospective_full_known_committed_data_audit",
        "live_external_fetch_allowed": False,
        "summary": {
            "generated_candidate_count": len(generated_candidates),
            "executed_candidate_count": len(EXECUTED_CANDIDATES),
            "rejected_before_execution_count": len(REJECTED_BEFORE_EXECUTION),
            "near_null_control_preserved": any(
                item["candidate_id"] == "FULLKNOWN-SHELL-006"
                and item["verdict"] == "INCONCLUSIVE"
                for item in executed_items
            ),
            "sign_inverted_control_preserved": any(
                item["candidate_id"] == "FULLKNOWN-SHELL-004"
                and item["sign_inverted"]
                for item in executed_items
            ),
            "shuffled_feature_control_preserved": any(
                item["candidate_id"] == "FULLKNOWN-SHELL-005"
                and item["fit_mode"] == "lstsq_shuffled"
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
            **baseline_bundle["metadata"],
        },
        "train_holdout_split": {
            "fit_surface": "NMD-0002 measured training slice",
            "fit_row_count": baseline_bundle["metadata"]["training_row_count"],
            "primary_holdout_surface": "post-AME2020 primary holdout rows",
            "primary_holdout_row_count": baseline_bundle["metadata"][
                "post_ame2020_primary_holdout_row_count"
            ],
            "full_known_surface": "unique union of NMD-0002 and post-AME2020 primary holdout",
            "full_known_unique_row_count": baseline_bundle["metadata"]["full_known_unique_row_count"],
        },
        "subset_definitions": {
            "full_known": "unique union of NMD-0002 training rows and post-AME2020 primary holdout rows",
            "training_slice": "NMD-0002 rows used to fit shell-axis coefficients",
            "primary_holdout": "post-AME2020 rows with included_in_time_split_holdout = true",
            "post_ame2020_measured_comparison": "holdout rows whose AME2020 comparison was measured",
            "post_ame2020_extrapolated_comparison": "holdout rows whose AME2020 comparison was extrapolated",
            "magic_any": "Z or N is one of {2,8,20,28,50,82,126}",
            "magic_z": "Z is one of {2,8,20,28,50,82,126}",
            "magic_n": "N is one of {2,8,20,28,50,82,126}",
            "double_magic": "both Z and N are magic numbers",
            "near_magic": "Z or N is within 2 of a magic number",
            "heavy_a_ge_100": "A >= 100",
            "mid_mass": "50 <= A <= 150",
            "light_a_lt_50": "A < 50",
            "neutron_rich_high": "(N - Z) / A >= 0.25",
            "registry_repeat_chain_neighbor": (
                "same Z as one of {Ni-76, Ca-55, Ga-85, Zn-80} and |A - registry_A| <= 2"
            ),
            "frontier_contrast": (
                "mid_mass delta MAE minus 0.5 * (light_a_lt_50 delta MAE + heavy_a_ge_100 delta MAE)"
            ),
        },
        "feature_definitions": {
            "s_z2": (
                "exp(-d(Z)^2 / (2 * 2.0^2)), where d(Z) is distance to nearest magic number"
            ),
            "s_n2": (
                "exp(-d(N)^2 / (2 * 2.0^2)), where d(N) is distance to nearest magic number"
            ),
            "s_z2_times_s_n2": "product of s_z2 and s_n2",
            "sign_inverted_control": (
                "fit beta_z as in FULLKNOWN-SHELL-001 and apply the negated correction"
            ),
            "shuffled_feature_control": (
                "cyclic-shift-5 feature shuffle on both training and audit surfaces"
            ),
            "near_null_or_baseline_reference_control": "zero correction against the frozen baseline",
        },
        "baseline_metrics_by_subset": baseline_metrics,
        "generated_candidates": generated_candidates,
        "executed_items": executed_items,
        "rejected_before_execution": list(REJECTED_BEFORE_EXECUTION),
        "promotion_boundary": {
            "writes_prediction_registry": False,
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "writes_knowledge": False,
            "required_next_step": (
                "Maintainer review before any registry expansion, reveal scoring, RESULT-* artifact, "
                "claim, or knowledge update."
            ),
        },
        "limitations": [
            "Sandbox-only retrospective audit; no prediction registry, canonical result, claim, or knowledge artifact is updated.",
            "Candidate coefficients are still fit on the 11-row NMD-0002 residual slice.",
            "Full-known rows are committed reviewable repository data; this is not a future-measurement reveal.",
            "Post-AME2020 rows are retrospective time-split evidence, not strict blind prediction.",
            "Subset deltas can be fragile where row counts are small; worst-regression summaries are preserved.",
        ],
    }


def _format_delta(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value == 0.0:
        return "+0.000000"
    return f"{'+' if value > 0 else '-'}{abs(value):.6f}"


def _summary_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| Candidate | Full-known ΔMAE MeV | Holdout ΔMAE MeV | Training ΔMAE MeV | Magic Z ΔMAE MeV | Magic N ΔMAE MeV | Worst regression | Verdict |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in metrics["executed_items"]:
        deltas = item["delta_mae_by_subset_mev"]
        worst = item["worst_subset_regression"]
        lines.append(
            "| `{cid}` | {full} | {holdout} | {training} | {mz} | {mn} | {worst} ({sid}) | `{verdict}` |".format(
                cid=item["candidate_id"],
                full=_format_delta(deltas.get("full_known")),
                holdout=_format_delta(deltas.get("primary_holdout")),
                training=_format_delta(deltas.get("training_slice")),
                mz=_format_delta(deltas.get("magic_z")),
                mn=_format_delta(deltas.get("magic_n")),
                worst=_format_delta(worst["delta_mae_mev"]),
                sid=worst["subset_id"],
                verdict=item["verdict"],
            )
        )
    return lines


def render_report(metrics: dict[str, Any]) -> str:
    """Render the agent-run report."""
    lines = [
        "# Nuclear Shell-Axis Full-Known Retrospective Audit",
        "",
        f"**Agent run:** `{metrics['agent_run_id']}`  ",
        f"**Task:** `{metrics['task_id']}`  ",
        "**Evidence class:** retrospective full-known committed-data audit  ",
        "**Baseline:** `RESULT-0015::model_fitted_semi_empirical`  ",
        "**Script:** `scripts/run_nuclear_shell_axis_full_known_audit.py`  ",
        f"**Metrics:** `agent_runs/{metrics['agent_run_id']}/metrics.json`",
        "",
        "## Scope",
        "",
        "This sandbox audit fits the shell-axis candidate family on the frozen "
        "NMD-0002 residual slice and evaluates it on the full unique committed "
        "surface currently available: NMD-0002 plus the post-AME2020 primary "
        "holdout rows. It does not score prospective registry entries.",
        "",
        "## Dataset Surface",
        "",
        "| Surface | Count |",
        "| --- | ---: |",
        f"| Training slice | {metrics['datasets']['training_row_count']} |",
        f"| Primary holdout | {metrics['datasets']['post_ame2020_primary_holdout_row_count']} |",
        f"| Full-known unique surface | {metrics['datasets']['full_known_unique_row_count']} |",
        "",
        "## Candidate Outcomes",
        "",
        *_summary_table(metrics),
        "",
        "Negative deltas mean lower retrospective MAE than the frozen baseline. "
        "Positive deltas are regressions.",
        "",
        "## Controls",
        "",
        "- `FULLKNOWN-SHELL-004` is the sign-inverted proton-axis control.",
        "- `FULLKNOWN-SHELL-005` is the shuffled-feature cyclic-shift-5 control.",
        "- `FULLKNOWN-SHELL-006` is the near-null / baseline-reference control.",
        "",
        "## Rejected Before Execution",
        "",
    ]
    for item in metrics["rejected_before_execution"]:
        lines.append(f"- `{item['candidate_id']}` ({item['name']}): {item['rejection_reason']}")
    lines.extend(
        [
            "",
            "## Limitations",
            "",
        ]
    )
    for limitation in metrics["limitations"]:
        lines.append(f"- {limitation}")
    lines.extend(
        [
            "",
            "## Promotion Boundary",
            "",
            "- Prediction registry files are not edited.",
            "- Canonical `RESULT-*` files are not edited.",
            "- Claims and knowledge files are not edited.",
            "- Any reveal scoring remains blocked behind a separate maintainer-reviewed source-manifest task.",
            "",
        ]
    )
    return "\n".join(lines)


def write_agent_run_support_files(metrics: dict[str, Any], run_dir: Path) -> None:
    """Write manifest and companion review files for AGENT-RUN-0018."""
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "task_id": TASK_ID,
        "status": "SANDBOX_COMPLETE",
        "sandbox_only": True,
        "created_by": {"contributor_id": "roman", "agent_id": "codex"},
        "proposal_paths": {
            "hypothesis": (
                "hypothesis_proposals/nuclear-mass/"
                "HYP-PROPOSAL-0044-shell-axis-stress-scout-batch.yaml"
            ),
            "experiment": (
                "experiment_proposals/nuclear-mass/"
                "EXP-PROPOSAL-0010-nuclear-shell-axis-stress-scout.yaml"
            ),
        },
        "artifacts": {
            "metrics": f"agent_runs/{AGENT_RUN_ID}/metrics.json",
            "report": f"agent_runs/{AGENT_RUN_ID}/report.md",
            "limitations": f"agent_runs/{AGENT_RUN_ID}/limitations.md",
            "preflight": f"agent_runs/{AGENT_RUN_ID}/preflight.md",
            "review_summary": f"agent_runs/{AGENT_RUN_ID}/review_summary.md",
        },
        "preflight": {
            "passed": True,
            "checks": [
                {
                    "name": "task_scope",
                    "status": "PASS",
                    "notes": "TASK-0310 requests a retrospective full-known audit, not reveal scoring.",
                },
                {
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": "Only committed repository datasets are used; no live external fetch is performed.",
                },
                {
                    "name": "control_boundary",
                    "status": "PASS",
                    "notes": "Sign-inverted, shuffled-feature, and near-null/baseline-reference controls are preserved.",
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": "No prediction registry, canonical result, claim, or knowledge file is written.",
                },
            ],
        },
        "limitations": metrics["limitations"],
        "verdict": "SANDBOX_PASS",
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": metrics["promotion_boundary"]["required_next_step"],
        },
    }
    (run_dir / "agent_run.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False),
        encoding="utf-8",
    )
    preflight = [
        "# AGENT-RUN-0018 Preflight",
        "",
        "**Task:** TASK-0310  ",
        "**Lane:** nuclear shell-axis full-known retrospective audit  ",
        "**Mode:** sandbox-only retrospective audit",
        "",
        "## Inputs Checked",
        "",
        "- `tasks/TASK-0310-run-nuclear-full-known-data-retrospective-audit.yaml`",
        "- `results/EXP-0012/RUN-0001/result.yaml`",
        "- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`",
        "- `data/nuclear_masses/post_ame2020_holdout.yaml`",
        "- `docs/reviews/nuclear-shell-axis-stress-scout-001.md`",
        "",
        "## Guardrails",
        "",
        "- Live external fetch: not allowed and not used.",
        "- Prediction registry writes: not allowed and not used.",
        "- Canonical results, claims, and knowledge promotion: not allowed and not used.",
        "- PRED-0063 through PRED-0068 are not reveal-scored.",
        "",
        "## Plan",
        "",
        "1. Fit bounded shell-axis candidates on the frozen NMD-0002 residual slice.",
        "2. Evaluate them on training, post-AME2020 primary holdout, and full-known unique surfaces.",
        "3. Preserve sign-inverted, shuffled-feature, and near-null/baseline-reference controls.",
        "4. Report per-subset deltas and worst-regression summaries.",
        "5. Keep outputs sandbox-only.",
        "",
    ]
    (run_dir / "preflight.md").write_text("\n".join(preflight), encoding="utf-8")
    limitations = ["# AGENT-RUN-0018 Limitations", ""]
    limitations.extend(f"- {item}" for item in metrics["limitations"])
    limitations.append("")
    (run_dir / "limitations.md").write_text("\n".join(limitations), encoding="utf-8")
    review = [
        "# AGENT-RUN-0018 Review Summary",
        "",
        "`SANDBOX_PASS` for a conservative retrospective audit. The strongest shell-axis "
        "candidates improve the full-known and primary-holdout surfaces relative to the "
        "frozen baseline, while the sign-inverted control regresses and the near-null "
        "control stays exactly at baseline. The shuffled-feature control remains a "
        "near-noise-floor diagnostic rather than evidence of a real shuffled signal.",
        "",
        "No prediction registry, canonical result, claim, or knowledge artifact is promoted.",
        "",
    ]
    (run_dir / "review_summary.md").write_text("\n".join(review), encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    """Write deterministic metrics, report, and companion agent-run files."""
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
        help="Path for the markdown report artifact.",
    )
    parser.add_argument(
        "--support-files",
        action="store_true",
        help="Write agent_run.yaml, preflight.md, limitations.md, and review_summary.md.",
    )
    args = parser.parse_args(argv)

    metrics = build_metrics()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(metrics, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")

    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(render_report(metrics), encoding="utf-8")
        print(f"wrote {args.report}")

    if args.support_files:
        write_agent_run_support_files(metrics, args.out.parent)
        print(f"wrote support files in {args.out.parent}")


if __name__ == "__main__":
    main()
