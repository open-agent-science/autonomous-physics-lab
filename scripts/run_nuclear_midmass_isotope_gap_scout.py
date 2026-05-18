"""TASK-0286 nuclear mid-mass and isotope-chain gap sandbox scout.

This sandbox-only scout evaluates bounded mid-mass and isotope-chain residual
correction candidates against the frozen RESULT-0015 fitted semi-empirical
baseline using repository-pinned datasets only. It probes the registry
coverage gaps surfaced by TASK-0272 (thin mid-mass coverage and isotope-chain
slices) without fetching live data, writing prediction registry entries,
canonical results, claims, or knowledge artifacts.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
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

AGENT_RUN_ID = "AGENT-RUN-0015"
TASK_ID = "TASK-0286"

MIDMASS_LOW = 50
MIDMASS_HIGH = 150
MIDMASS_GAUSSIAN_SIGMA = 20.0
MIDMASS_GAUSSIAN_CENTER = 100.0
SHELL_FALLOFF_DENOM = 8.0
ISOTOPE_CHAIN_Z_VALUES: tuple[int, ...] = (20, 28, 50)


EXECUTED_CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "candidate_id": "MIDMASS-SCOUT-001",
        "name": "Mid-mass Gaussian peak (sigma 20, center A=100)",
        "formula": "r_corr = beta * exp(-((A-100)^2) / (2*20^2))",
        "feature_names": ("midmass_gaussian",),
        "complexity": 1,
    },
    {
        "candidate_id": "MIDMASS-SCOUT-002",
        "name": "Mid-mass indicator times asymmetry",
        "formula": "r_corr = beta * I[50<=A<=150] * ((N-Z)/A)",
        "feature_names": ("midmass_times_asymmetry",),
        "complexity": 1,
    },
    {
        "candidate_id": "MIDMASS-SCOUT-003",
        "name": "Isotope-chain slope, N minus per-Z median N",
        "formula": "r_corr = beta * (N - N_ref_for_Z)",
        "feature_names": ("isotope_chain_offset",),
        "complexity": 1,
    },
    {
        "candidate_id": "MIDMASS-SCOUT-004",
        "name": "Mid-mass shell-distance Gaussian fall-off",
        "formula": "r_corr = beta * I[50<=A<=150] * exp(-(min_magic_distance)^2 / 8)",
        "feature_names": ("midmass_shell_falloff",),
        "complexity": 1,
    },
    {
        "candidate_id": "MIDMASS-SCOUT-005",
        "name": "Near-null mid-mass sanity control",
        "formula": "r_corr = 0.0",
        "feature_names": (),
        "complexity": 0,
        "fixed_zero_control": True,
    },
)


REJECTED_BEFORE_EXECUTION: tuple[dict[str, str], ...] = (
    {
        "candidate_id": "MIDMASS-SCOUT-006",
        "name": "Per-Z fitted intercepts",
        "rejection_reason": (
            "Rejected before execution because per-Z intercepts on an 11-row "
            "NMD-0002 training slice memorize individual rows rather than test "
            "a bounded mid-mass or isotope-chain residual feature."
        ),
    },
    {
        "candidate_id": "MIDMASS-SCOUT-007",
        "name": "A-binned 8-bin step function",
        "rejection_reason": (
            "Rejected before execution because an 8-bin A-step function inflates "
            "degrees of freedom relative to the 11-row residual training slice "
            "and would be a row-memorizing overfit risk."
        ),
    },
    {
        "candidate_id": "MIDMASS-SCOUT-008",
        "name": "Free sigma in mid-mass Gaussian",
        "rejection_reason": (
            "Rejected before execution because tuning sigma adds a nonlinear "
            "free knob on an 11-row residual slice and duplicates the "
            "fixed-sigma continuous probe MIDMASS-SCOUT-001."
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


def midmass_indicator(a: int) -> float:
    """Indicator: 1.0 when 50 <= A <= 150 else 0.0."""
    return 1.0 if MIDMASS_LOW <= int(a) <= MIDMASS_HIGH else 0.0


def midmass_gaussian(a: int) -> float:
    """Continuous mid-mass Gaussian peak centered at A=100, sigma=20."""
    delta = float(a) - MIDMASS_GAUSSIAN_CENTER
    return float(math.exp(-(delta * delta) / (2.0 * MIDMASS_GAUSSIAN_SIGMA ** 2)))


def asymmetry(z: int, n: int, a: int) -> float:
    """Standard (N-Z)/A asymmetry."""
    return float(n - z) / float(a)


def min_magic_distance(z: int, n: int) -> int:
    """Minimum over magic numbers of |N-magic| + |Z-magic| (L1 to nearest shell point)."""
    return min(abs(n - m) + abs(z - m) for m in MAGIC_NUMBERS)


def midmass_shell_falloff(z: int, n: int, a: int) -> float:
    """Mid-mass-gated shell-distance Gaussian fall-off feature."""
    if midmass_indicator(a) == 0.0:
        return 0.0
    distance = min_magic_distance(z, n)
    return float(math.exp(-(distance * distance) / SHELL_FALLOFF_DENOM))


def build_isotope_chain_reference(training_entries: list[Any]) -> dict[int, float]:
    """Median N per Z value across the training slice; default 0.0 if Z absent."""
    by_z: dict[int, list[int]] = {}
    for entry in training_entries:
        by_z.setdefault(int(entry.Z), []).append(int(entry.N))
    return {z: float(statistics.median(values)) for z, values in by_z.items()}


def isotope_chain_offset(
    z: int,
    n: int,
    *,
    reference_by_z: dict[int, float],
) -> float:
    """N minus per-Z median N; 0.0 if Z absent from training."""
    return float(n) - float(reference_by_z.get(int(z), 0.0))


def feature_vector(
    feature_names: tuple[str, ...],
    *,
    z: int,
    n: int,
    a: int,
    reference_by_z: dict[int, float],
) -> tuple[float, ...]:
    """Return mid-mass/isotope-chain feature values for one target row."""
    values = {
        "midmass_gaussian": midmass_gaussian(a),
        "midmass_times_asymmetry": midmass_indicator(a) * asymmetry(z, n, a),
        "isotope_chain_offset": isotope_chain_offset(z, n, reference_by_z=reference_by_z),
        "midmass_shell_falloff": midmass_shell_falloff(z, n, a),
    }
    return tuple(values[name] for name in feature_names)


def subset_ids(*, z: int, n: int, a: int, was_extrapolated: bool) -> tuple[str, ...]:
    """Subset labels covering primary, mass-bands, and isotope-chain reveals."""
    ids = ["primary"]
    ids.append("ame2020_extrapolated_comparison" if was_extrapolated else "ame2020_measured_comparison")
    if a < MIDMASS_LOW:
        ids.append("light")
    elif a <= MIDMASS_HIGH:
        ids.append("mid_mass")
    else:
        ids.append("heavy")
    if z == 20:
        ids.append("isotope_chain_z20")
    if z == 28:
        ids.append("isotope_chain_z28")
    if z == 50:
        ids.append("isotope_chain_z50")
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
    """Return mid_mass delta minus average of light/heavy deltas."""
    mid = deltas.get("mid_mass")
    light = deltas.get("light")
    heavy = deltas.get("heavy")
    if mid is None or light is None or heavy is None:
        return None
    return float(mid) - 0.5 * (float(light) + float(heavy))


def verdict_for_candidate(
    *,
    candidate: dict[str, Any],
    delta_by_subset: dict[str, float | None],
    frontier_contrast_value: float | None,
) -> str:
    """Assign conservative scout verdicts without promoting scientific claims."""
    material = 1.0e-6
    if candidate.get("fixed_zero_control"):
        return "INCONCLUSIVE"
    primary = delta_by_subset.get("primary")
    if primary is None:
        return "INCONCLUSIVE"
    numeric_deltas = [value for value in delta_by_subset.values() if value is not None]
    worst_regression = max([0.0, *numeric_deltas])
    if primary > 1.0 or worst_regression > 2.0:
        return "OVERFITTED"
    if primary > 0.25 and worst_regression > 1.0:
        return "OVERFITTED"
    if candidate["complexity"] >= 3 and primary > 0.1 and worst_regression > 0.25:
        return "OVERFITTED"
    mid = delta_by_subset.get("mid_mass")
    chain_improved = any(
        delta_by_subset.get(key) is not None and delta_by_subset.get(key) < -material
        for key in ("isotope_chain_z20", "isotope_chain_z28", "isotope_chain_z50")
    )
    mid_improved = mid is not None and mid < -material
    if mid_improved and worst_regression <= 0.5:
        if frontier_contrast_value is not None and frontier_contrast_value > 0.25:
            return "INCONCLUSIVE"
        return "PARTIALLY_VALID"
    if chain_improved and primary <= 0.25 and worst_regression <= 0.75:
        return "PARTIALLY_VALID"
    if primary < -material and worst_regression <= 0.5:
        return "PARTIALLY_VALID"
    return "INCONCLUSIVE"


def evaluate_candidate(
    candidate: dict[str, Any],
    *,
    training_entries: list[Any],
    training_residuals: np.ndarray,
    post_rows: list[dict[str, Any]],
    baseline_metrics: dict[str, Any],
    reference_by_z: dict[int, float],
) -> dict[str, Any]:
    """Fit a candidate on NMD-0002 residuals and evaluate on pinned holdout rows."""
    feature_names = tuple(candidate["feature_names"])
    if candidate.get("fixed_zero_control"):
        beta = np.asarray([], dtype=float)
    else:
        train_x = np.asarray(
            [
                feature_vector(
                    feature_names,
                    z=entry.Z,
                    n=entry.N,
                    a=entry.A,
                    reference_by_z=reference_by_z,
                )
                for entry in training_entries
            ],
            dtype=float,
        )
        beta, *_ = np.linalg.lstsq(train_x, training_residuals, rcond=None)

    subset_errors: dict[str, list[float]] = {key: [] for key in baseline_metrics}
    per_row: list[dict[str, Any]] = []
    activation_counts = {name: 0 for name in feature_names}
    for row in post_rows:
        z, n, a = int(row["Z"]), int(row["N"]), int(row["A"])
        values = feature_vector(
            feature_names,
            z=z,
            n=n,
            a=a,
            reference_by_z=reference_by_z,
        )
        for name, value in zip(feature_names, values):
            if abs(value) > 0.0:
                activation_counts[name] += 1
        correction = 0.0 if candidate.get("fixed_zero_control") else float(np.asarray(values) @ beta)
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
    frontier_contrast_value = frontier_contrast(delta_by_subset)
    numeric_deltas = [value for value in delta_by_subset.values() if value is not None]
    worst_subset_regression = max([0.0, *numeric_deltas])
    verdict = verdict_for_candidate(
        candidate=candidate,
        delta_by_subset=delta_by_subset,
        frontier_contrast_value=frontier_contrast_value,
    )

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
        "frontier_contrast_mev": frontier_contrast_value,
        "worst_subset_regression_mae_mev": worst_subset_regression,
        "worst_abs_error_cases": sorted(
            per_row, key=lambda item: float(item["candidate_abs_error_mev"]), reverse=True
        )[:5],
        "verdict": verdict,
        "limitations": [
            "Feature coefficients are fit on the 11-row NMD-0002 residual slice.",
            "Post-AME2020 evaluation uses committed retrospective rows only; it is not a reveal of new live measurements.",
            "Isotope-chain subsets are small (Z=20 has 2 rows, Z=28 has 3 rows, Z=50 has 1 row in the primary holdout).",
            "Verdict is a sandbox triage label, not a promoted claim.",
        ],
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
    reference_by_z = build_isotope_chain_reference(training_entries)

    post_rows, baseline_metrics = baseline_post_ame2020_rows(coefficients)
    executed_items = [
        evaluate_candidate(
            candidate,
            training_entries=training_entries,
            training_residuals=residuals,
            post_rows=post_rows,
            baseline_metrics=baseline_metrics,
            reference_by_z=reference_by_z,
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

    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "midmass_isotope_gap_scout",
        "sandbox_only": True,
        "evidence_class": "bounded_sandbox_residual_scout",
        "live_external_fetch_allowed": False,
        "summary": {
            "generated_candidate_count": len(generated_candidates),
            "executed_candidate_count": len(EXECUTED_CANDIDATES),
            "rejected_before_execution_count": len(REJECTED_BEFORE_EXECUTION),
            "near_null_control_preserved": any(
                item["candidate_id"] == "MIDMASS-SCOUT-005" and item["verdict"] == "INCONCLUSIVE"
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
            "mid_mass": f"{MIDMASS_LOW} <= A <= {MIDMASS_HIGH}",
            "light": f"A < {MIDMASS_LOW}",
            "heavy": f"A > {MIDMASS_HIGH}",
            "isotope_chain_z20": "Z = 20 (calcium chain)",
            "isotope_chain_z28": "Z = 28 (nickel chain)",
            "isotope_chain_z50": "Z = 50 (tin chain)",
            "frontier_contrast": "mid_mass delta MAE minus 0.5 * (light delta MAE + heavy delta MAE)",
        },
        "feature_definitions": {
            "midmass_gaussian": (
                f"exp(-((A - {MIDMASS_GAUSSIAN_CENTER:.0f})^2) / "
                f"(2 * {MIDMASS_GAUSSIAN_SIGMA:.0f}^2))"
            ),
            "midmass_times_asymmetry": "I[50<=A<=150] * (N - Z) / A",
            "isotope_chain_offset": "N - median_N_for_Z across training slice (0.0 if Z absent)",
            "midmass_shell_falloff": (
                "I[50<=A<=150] * exp(-(min_magic_distance)^2 / 8) where "
                "min_magic_distance = min_m in {2,8,20,28,50,82,126} (|N-m| + |Z-m|)"
            ),
        },
        "isotope_chain_reference": {
            "training_median_N_by_Z": {int(z): float(median) for z, median in sorted(reference_by_z.items())},
            "isotope_chain_subset_Z_values": list(ISOTOPE_CHAIN_Z_VALUES),
        },
        "baseline_metrics_by_subset": baseline_metrics,
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
            "Isotope-chain subsets are small (Z=20 has 2 rows, Z=28 has 3 rows, Z=50 has 1 row in the primary holdout); per-chain deltas are highly fragile.",
            "Rejected candidates are preserved to document overfit and row-memorization boundaries.",
        ],
    }


def render_report(metrics: dict[str, Any]) -> str:
    """Render a markdown report mirroring the scout-001 review pattern."""
    lines: list[str] = []
    lines.append("# Nuclear Mid-Mass And Isotope-Chain Gap Scout")
    lines.append("")
    lines.append(f"**Agent run:** {metrics['agent_run_id']}  ")
    lines.append(f"**Task:** {metrics['task_id']}  ")
    lines.append("**Evidence class:** bounded sandbox residual scout  ")
    lines.append("**Baseline:** `RESULT-0015::model_fitted_semi_empirical`  ")
    lines.append("**Script:** `scripts/run_nuclear_midmass_isotope_gap_scout.py`  ")
    lines.append(
        f"**Metrics:** `agent_runs/{metrics['agent_run_id']}/metrics.json`"
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    summary = metrics["summary"]
    lines.append(
        "This scout generated "
        f"{summary['generated_candidate_count']} bounded mid-mass and isotope-chain "
        "candidate ideas. "
        f"{summary['executed_candidate_count']} were evaluated and "
        f"{summary['rejected_before_execution_count']} were rejected before execution "
        "due to row-memorization, degree-of-freedom inflation, or duplicate-search risk."
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
        "| Candidate | Feature family | Primary delta MAE MeV | Mid-mass delta MAE MeV | Light delta MAE MeV | Heavy delta MAE MeV | Frontier contrast MeV | Verdict |"
    )
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |")
    for item in metrics["executed_items"]:
        deltas = item["delta_mae_by_subset_mev"]
        lines.append(
            "| `{cid}` | {family} | {primary} | {mid} | {light} | {heavy} | {fc} | `{verdict}` |".format(
                cid=item["candidate_id"],
                family=item["name"],
                primary=_format_delta(deltas.get("primary")),
                mid=_format_delta(deltas.get("mid_mass")),
                light=_format_delta(deltas.get("light")),
                heavy=_format_delta(deltas.get("heavy")),
                fc=_format_delta(item.get("frontier_contrast_mev")),
                verdict=item["verdict"],
            )
        )
    lines.append("")
    lines.append("Isotope-chain deltas (small subsets, fragile):")
    lines.append("")
    lines.append(
        "| Candidate | Z=20 delta MAE MeV | Z=28 delta MAE MeV | Z=50 delta MAE MeV |"
    )
    lines.append("| --- | ---: | ---: | ---: |")
    for item in metrics["executed_items"]:
        deltas = item["delta_mae_by_subset_mev"]
        lines.append(
            "| `{cid}` | {z20} | {z28} | {z50} |".format(
                cid=item["candidate_id"],
                z20=_format_delta(deltas.get("isotope_chain_z20")),
                z28=_format_delta(deltas.get("isotope_chain_z28")),
                z50=_format_delta(deltas.get("isotope_chain_z50")),
            )
        )
    lines.append("")
    lines.append(
        "Negative deltas mean lower retrospective MAE than the frozen baseline on "
        "that subset. Positive deltas mean regression."
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
        "scout triage evidence only and are not promoted as discoveries."
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
    if partially_valid:
        lines.append(
            "`PARTIALLY_VALID` candidates: "
            + ", ".join(f"`{cid}`" for cid in partially_valid)
            + ". Frontier-contrast values are reported so any mid-mass-only gain that "
            "regresses light or heavy bands is flagged as fragile."
        )
    else:
        lines.append(
            "No candidate reached `PARTIALLY_VALID`. The lane preserves negative and "
            "null evidence rather than promoting a signal."
        )
    if overfit:
        lines.append("")
        lines.append(
            "`OVERFITTED` candidates: " + ", ".join(f"`{cid}`" for cid in overfit) + "."
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


def _format_delta(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value == 0.0:
        return "+0.000000"
    sign = "+" if value > 0 else "-"
    return f"{sign}{abs(value):.6f}"


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
    out_path.write_text(json.dumps(metrics, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")

    if args.report is not None:
        report = render_report(metrics)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
        print(f"wrote {args.report}")


if __name__ == "__main__":
    main()
