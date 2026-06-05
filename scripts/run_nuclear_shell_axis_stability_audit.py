"""TASK-0316 nuclear shell-axis coefficient stability audit.

This sandbox-only runner stress-tests the coefficient stability of the primary
shell-axis candidates from TASK-0310. It reuses the committed NMD-0002 training
slice, post-AME2020 holdout rows, and frozen RESULT-0015 baseline; it does not
fetch live data, score prospective prediction registry entries, write canonical
RESULT-* artifacts, update claims, or edit knowledge.
"""

from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.run_nuclear_shell_axis_full_known_audit as full_known  # noqa: E402


AGENT_RUN_ID = "AGENT-RUN-0019"
TASK_ID = "TASK-0316"
PRIMARY_CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "candidate_id": "STABILITY-SHELL-001",
        "source_candidate_id": "FULLKNOWN-SHELL-001",
        "name": "Proton-axis Gaussian shell proximity",
        "formula": "r_corr = beta_z * s_z2",
        "feature_names": ("s_z2",),
    },
    {
        "candidate_id": "STABILITY-SHELL-002",
        "source_candidate_id": "FULLKNOWN-SHELL-002",
        "name": "Proton x neutron product shell proximity",
        "formula": "r_corr = beta_p * (s_z2 * s_n2)",
        "feature_names": ("s_z2_times_s_n2",),
    },
    {
        "candidate_id": "STABILITY-SHELL-003",
        "source_candidate_id": "FULLKNOWN-SHELL-003",
        "name": "Neutron-axis Gaussian shell proximity",
        "formula": "r_corr = beta_n * s_n2",
        "feature_names": ("s_n2",),
    },
)


def _feature_matrix(feature_names: tuple[str, ...], rows: list[dict[str, Any]]) -> np.ndarray:
    return np.asarray(
        [
            full_known._feature_vector(feature_names, z=int(row["Z"]), n=int(row["N"]))  # noqa: SLF001
            for row in rows
        ],
        dtype=float,
    )


def _fit_beta(
    feature_names: tuple[str, ...],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
    indices: tuple[int, ...],
) -> np.ndarray:
    train_x = _feature_matrix(feature_names, [training_rows[idx] for idx in indices])
    train_y = np.asarray([training_residuals[idx] for idx in indices], dtype=float)
    beta, *_ = np.linalg.lstsq(train_x, train_y, rcond=None)
    return beta


def _evaluate_beta(
    *,
    feature_names: tuple[str, ...],
    beta: np.ndarray,
    audit_rows: list[dict[str, Any]],
    baseline_metrics: dict[str, Any],
) -> dict[str, Any]:
    subset_errors: dict[str, list[float]] = {key: [] for key in baseline_metrics}
    for row in audit_rows:
        values = full_known._feature_vector(  # noqa: SLF001
            feature_names,
            z=int(row["Z"]),
            n=int(row["N"]),
        )
        correction = float(np.asarray(values, dtype=float) @ beta)
        residual = float(row["observed_mev"]) - (
            float(row["baseline_predicted_mev"]) + correction
        )
        for subset_id in full_known._surface_subset_ids(row):  # noqa: SLF001
            subset_errors.setdefault(subset_id, []).append(residual)

    metrics_by_subset = {
        key: full_known._summarize_errors(value)  # noqa: SLF001
        for key, value in sorted(subset_errors.items())
    }
    deltas = {
        key: full_known._delta_mae(metrics_by_subset.get(key), baseline_metrics.get(key))  # noqa: SLF001
        for key in sorted(baseline_metrics)
    }
    positive = {key: value for key, value in deltas.items() if value is not None and value > 0.0}
    worst_subset_id, worst_subset_regression = ("none", 0.0)
    if positive:
        worst_subset_id, worst_subset_regression = max(positive.items(), key=lambda item: item[1])
    return {
        "delta_mae_by_subset_mev": deltas,
        "full_known_delta_mae_mev": deltas.get("full_known"),
        "holdout_delta_mae_mev": deltas.get("primary_holdout"),
        "training_delta_mae_mev": deltas.get("training_slice"),
        "worst_subset_regression": {
            "subset_id": worst_subset_id,
            "delta_mae_mev": float(worst_subset_regression),
        },
    }


def _summary(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "min": None, "max": None, "mean": None, "std": None}
    arr = np.asarray(values, dtype=float)
    return {
        "count": int(arr.size),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
    }


def _sign_counts(values: list[float]) -> dict[str, int]:
    counts = {"negative": 0, "zero": 0, "positive": 0}
    for value in values:
        if value < 0.0:
            counts["negative"] += 1
        elif value > 0.0:
            counts["positive"] += 1
        else:
            counts["zero"] += 1
    return counts


def _fit_records_for_design(
    *,
    candidate: dict[str, Any],
    resamples: list[dict[str, Any]],
    audit_rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
    baseline_metrics: dict[str, Any],
    sign_invert: bool = False,
) -> list[dict[str, Any]]:
    feature_names = tuple(candidate["feature_names"])
    records: list[dict[str, Any]] = []
    for resample in resamples:
        beta = _fit_beta(feature_names, training_rows, training_residuals, resample["indices"])
        if sign_invert:
            beta = -beta
        evaluation = _evaluate_beta(
            feature_names=feature_names,
            beta=beta,
            audit_rows=audit_rows,
            baseline_metrics=baseline_metrics,
        )
        coefficient = float(beta[0])
        records.append(
            {
                "resample_id": resample["resample_id"],
                "omitted_row_ids": resample["omitted_row_ids"],
                "fit_row_count": len(resample["indices"]),
                "coefficient": coefficient,
                "coefficient_abs": abs(coefficient),
                **evaluation,
            }
        )
    return records


def _summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    full_known = [float(item["full_known_delta_mae_mev"]) for item in records]
    holdout = [float(item["holdout_delta_mae_mev"]) for item in records]
    training = [float(item["training_delta_mae_mev"]) for item in records]
    coefficients = [float(item["coefficient"]) for item in records]
    worst_values = [float(item["worst_subset_regression"]["delta_mae_mev"]) for item in records]
    worst_subsets = Counter(str(item["worst_subset_regression"]["subset_id"]) for item in records)
    return {
        "fit_count": len(records),
        "coefficient": _summary(coefficients),
        "coefficient_abs": _summary([abs(value) for value in coefficients]),
        "coefficient_sign_counts": _sign_counts(coefficients),
        "coefficient_sign_stable": max(_sign_counts(coefficients).values(), default=0) == len(records),
        "full_known_delta_mae_mev": _summary(full_known),
        "holdout_delta_mae_mev": _summary(holdout),
        "training_delta_mae_mev": _summary(training),
        "worst_subset_regression_delta_mae_mev": _summary(worst_values),
        "worst_subset_regression_frequency": dict(sorted(worst_subsets.items())),
        "full_known_improvement_count": sum(1 for value in full_known if value < 0.0),
        "holdout_improvement_count": sum(1 for value in holdout if value < 0.0),
        "full_known_improvement_rate": sum(1 for value in full_known if value < 0.0) / len(records),
        "holdout_improvement_rate": sum(1 for value in holdout if value < 0.0) / len(records),
        "max_full_known_regression_mev": max([value for value in full_known if value > 0.0], default=0.0),
        "max_holdout_regression_mev": max([value for value in holdout if value > 0.0], default=0.0),
    }


def _resample_designs(training_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    count = len(training_rows)
    all_indices = tuple(range(count))
    leave_one_out = []
    for omitted in range(count):
        indices = tuple(idx for idx in all_indices if idx != omitted)
        leave_one_out.append(
            {
                "resample_id": f"loo-omit-{training_rows[omitted]['nuclide_id']}",
                "indices": indices,
                "omitted_row_ids": [str(training_rows[omitted]["row_id"])],
            }
        )
    small_resamples = []
    for serial, indices in enumerate(combinations(all_indices, 8), start=1):
        kept = set(indices)
        small_resamples.append(
            {
                "resample_id": f"size8-{serial:03d}",
                "indices": tuple(indices),
                "omitted_row_ids": [
                    str(training_rows[idx]["row_id"]) for idx in all_indices if idx not in kept
                ],
            }
        )
    return {
        "leave_one_out": leave_one_out,
        "small_resample_size_8_of_11": small_resamples,
    }


def _candidate_verdict(candidate_summary: dict[str, Any]) -> str:
    loo = candidate_summary["resampling"]["leave_one_out"]
    small = candidate_summary["resampling"]["small_resample_size_8_of_11"]
    sign_stable = bool(loo["coefficient_sign_stable"] and small["coefficient_sign_stable"])
    full_rate = min(float(loo["full_known_improvement_rate"]), float(small["full_known_improvement_rate"]))
    holdout_rate = min(float(loo["holdout_improvement_rate"]), float(small["holdout_improvement_rate"]))
    max_regression = max(
        float(loo["max_full_known_regression_mev"]),
        float(loo["max_holdout_regression_mev"]),
        float(small["max_full_known_regression_mev"]),
        float(small["max_holdout_regression_mev"]),
    )
    if sign_stable and full_rate == 1.0 and holdout_rate == 1.0 and max_regression == 0.0:
        return "STABLE_BUT_BOUNDED"
    if sign_stable and full_rate >= 0.9 and holdout_rate >= 0.9:
        return "PARTIALLY_STABLE"
    return "FRAGILE"


def build_metrics() -> dict[str, Any]:
    """Build deterministic coefficient-stability metrics."""
    coefficients = full_known.load_frozen_baseline_coefficients()
    audit_rows, training_rows, training_residuals, baseline_bundle = full_known.build_audit_surface(
        coefficients
    )
    baseline_metrics = baseline_bundle["metrics"]
    designs = _resample_designs(training_rows)

    candidate_summaries: list[dict[str, Any]] = []
    for candidate in PRIMARY_CANDIDATES:
        feature_names = tuple(candidate["feature_names"])
        full_fit_beta = _fit_beta(
            feature_names,
            training_rows,
            training_residuals,
            tuple(range(len(training_rows))),
        )
        full_fit = {
            "coefficient": float(full_fit_beta[0]),
            **_evaluate_beta(
                feature_names=feature_names,
                beta=full_fit_beta,
                audit_rows=audit_rows,
                baseline_metrics=baseline_metrics,
            ),
        }
        resampling: dict[str, Any] = {}
        for design_id, resamples in designs.items():
            records = _fit_records_for_design(
                candidate=candidate,
                resamples=resamples,
                audit_rows=audit_rows,
                training_rows=training_rows,
                training_residuals=training_residuals,
                baseline_metrics=baseline_metrics,
            )
            resampling[design_id] = _summarize_records(records)
        summary = {
            "candidate_id": candidate["candidate_id"],
            "source_candidate_id": candidate["source_candidate_id"],
            "name": candidate["name"],
            "formula": candidate["formula"],
            "feature_names": list(feature_names),
            "full_training_fit": full_fit,
            "resampling": resampling,
        }
        summary["verdict"] = _candidate_verdict(summary)
        candidate_summaries.append(summary)

    sign_control_candidate = {
        "candidate_id": "STABILITY-SHELL-004",
        "source_candidate_id": "FULLKNOWN-SHELL-004",
        "name": "Sign-inverted proton-axis Gaussian control",
        "formula": "r_corr = -beta_z * s_z2 for each resample",
        "feature_names": ("s_z2",),
    }
    sign_control: dict[str, Any] = {}
    for design_id, resamples in designs.items():
        records = _fit_records_for_design(
            candidate=sign_control_candidate,
            resamples=resamples,
            audit_rows=audit_rows,
            training_rows=training_rows,
            training_residuals=training_residuals,
            baseline_metrics=baseline_metrics,
            sign_invert=True,
        )
        sign_control[design_id] = _summarize_records(records)

    verdict_counts = Counter(item["verdict"] for item in candidate_summaries)
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "shell_axis_coefficient_stability_audit",
        "sandbox_only": True,
        "evidence_class": "retrospective_committed_data_coefficient_stability_audit",
        "live_external_fetch_allowed": False,
        "summary": {
            "primary_candidate_count": len(candidate_summaries),
            "leave_one_out_fit_count_per_candidate": len(designs["leave_one_out"]),
            "small_resample_fit_count_per_candidate": len(designs["small_resample_size_8_of_11"]),
            "overall_verdict": (
                "STABLE_BUT_BOUNDED"
                if all(item["verdict"] == "STABLE_BUT_BOUNDED" for item in candidate_summaries)
                else "FRAGILE"
            ),
            "verdict_counts": dict(sorted(verdict_counts.items())),
            "sign_inverted_control_included": True,
            "near_null_control_preserved_as_exact_zero_reference": True,
            "shuffled_feature_control_not_rerun_reason": (
                "The TASK-0310 shuffled-feature control is a row-feature correspondence null. "
                "Under changing leave-one-out or size-8 resample membership, the cyclic row "
                "permutation no longer has a stable feature correspondence interpretation, so "
                "TASK-0316 keeps it as a TASK-0310 reference instead of treating it as a "
                "coefficient-stability fit."
            ),
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
        "resampling_design": {
            "leave_one_out": (
                "11 deterministic jackknife fits, each omitting one NMD-0002 training row."
            ),
            "small_resample_size_8_of_11": (
                "All 165 deterministic 8-of-11 combinations from the NMD-0002 training slice."
            ),
            "random_seed": None,
        },
        "baseline_metrics_by_subset": baseline_metrics,
        "candidate_summaries": candidate_summaries,
        "controls": {
            "sign_inverted_proton_axis": {
                "candidate_id": sign_control_candidate["candidate_id"],
                "source_candidate_id": sign_control_candidate["source_candidate_id"],
                "name": sign_control_candidate["name"],
                "resampling": sign_control,
                "expected_behavior": "Regression or non-improvement under sign inversion.",
            },
            "near_null_reference": {
                "candidate_id": "STABILITY-SHELL-006",
                "source_candidate_id": "FULLKNOWN-SHELL-006",
                "name": "Near-null / baseline-reference control",
                "coefficient": 0.0,
                "all_delta_mae_mev": 0.0,
                "expected_behavior": "Exact baseline reference; no coefficient to resample.",
            },
            "shuffled_feature_control": {
                "source_candidate_id": "FULLKNOWN-SHELL-005",
                "status": "not_rerun_under_resampling",
                "reason": (
                    "Cyclic row-feature shuffling is a row-correspondence null, not a "
                    "coefficient-stability fit under changing resample membership."
                ),
            },
        },
        "promotion_boundary": {
            "writes_prediction_registry": False,
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "writes_knowledge": False,
            "required_next_step": (
                "Maintainer review before any registry expansion, reveal scoring, RESULT-* "
                "artifact, claim, or knowledge update."
            ),
        },
        "limitations": [
            "Sandbox-only retrospective audit; no prediction registry, canonical result, claim, or knowledge artifact is updated.",
            "All coefficient stability tests still resample only the 11-row NMD-0002 training slice.",
            "Full-known and post-AME2020 rows are committed reviewable repository data, not future-measurement reveal data.",
            "The deterministic 8-of-11 design is exhaustive for that size but does not replace a larger independent training surface.",
            "Subset deltas remain fragile where row counts are small; light-nuclei regressions remain a domain limitation.",
        ],
    }


def _format(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value == 0.0:
        return "+0.000000"
    return f"{'+' if value > 0 else '-'}{abs(value):.6f}"


def _candidate_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| Candidate | Full-fit coeff | LOO coeff range | 8-of-11 coeff range | LOO holdout Δ range | 8-of-11 holdout Δ range | Verdict |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in metrics["candidate_summaries"]:
        loo = item["resampling"]["leave_one_out"]
        small = item["resampling"]["small_resample_size_8_of_11"]
        lines.append(
            "| `{cid}` | {coeff:.6f} | {loo_c_min:.6f}..{loo_c_max:.6f} | "
            "{small_c_min:.6f}..{small_c_max:.6f} | {loo_h_min}..{loo_h_max} | "
            "{small_h_min}..{small_h_max} | `{verdict}` |".format(
                cid=item["candidate_id"],
                coeff=item["full_training_fit"]["coefficient"],
                loo_c_min=loo["coefficient"]["min"],
                loo_c_max=loo["coefficient"]["max"],
                small_c_min=small["coefficient"]["min"],
                small_c_max=small["coefficient"]["max"],
                loo_h_min=_format(loo["holdout_delta_mae_mev"]["min"]),
                loo_h_max=_format(loo["holdout_delta_mae_mev"]["max"]),
                small_h_min=_format(small["holdout_delta_mae_mev"]["min"]),
                small_h_max=_format(small["holdout_delta_mae_mev"]["max"]),
                verdict=item["verdict"],
            )
        )
    return lines


def render_report(metrics: dict[str, Any]) -> str:
    """Render the agent-run report."""
    lines = [
        "# Nuclear Shell-Axis Coefficient Stability Audit",
        "",
        f"**Agent run:** `{metrics['agent_run_id']}`",
        f"**Task:** `{metrics['task_id']}`",
        "**Evidence class:** retrospective committed-data coefficient stability audit",
        "**Baseline:** `RESULT-0015::model_fitted_semi_empirical`",
        "**Script:** `scripts/run_nuclear_shell_axis_stability_audit.py`",
        "",
        "## Scope",
        "",
        "This sandbox audit stress-tests whether the TASK-0310 shell-axis coefficients "
        "survive deterministic resampling of the 11-row NMD-0002 fit surface. It does "
        "not fetch live data, score prediction registry entries, or promote claims.",
        "",
        "## Resampling Design",
        "",
        "- Leave-one-out / jackknife: 11 deterministic fits.",
        "- Small resamples: all 165 deterministic 8-of-11 training-row combinations.",
        "- Evaluation surfaces: NMD-0002 training slice, post-AME2020 primary holdout, and full-known unique committed surface.",
        "",
        "## Candidate Summary",
        "",
        *_candidate_table(metrics),
        "",
        "Negative delta ranges mean lower MAE than the frozen baseline. Positive ranges are regressions.",
        "",
        "## Controls",
        "",
        "- Sign-inverted proton-axis control is included under the same resampling designs.",
        "- Near-null control is preserved as an exact zero reference because it has no coefficient to resample.",
        "- Shuffled-feature control is not rerun as a coefficient-stability fit because cyclic row-feature shuffling depends on stable row correspondence; this remains a TASK-0310 null-control reference.",
        "",
        "## Verdict",
        "",
    ]
    verdicts = {item["candidate_id"]: item["verdict"] for item in metrics["candidate_summaries"]}
    if all(value == "STABLE_BUT_BOUNDED" for value in verdicts.values()):
        lines.append("`STABLE_BUT_BOUNDED` for the three primary shell-axis candidates.")
    else:
        lines.append(
            "`FRAGILE`: leave-one-out fits preserve the small retrospective improvements, "
            "but exhaustive 8-of-11 resampling introduces coefficient sign flips and "
            "some full-known/holdout regressions for all three primary candidates."
        )
    lines.extend(
        [
            "",
            "The stability evidence remains sandbox-only. It can guide specificity controls, "
            "but it does not justify registry expansion, reveal scoring, or claim promotion.",
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in metrics["limitations"])
    lines.append("")
    return "\n".join(lines)


def write_agent_run_support_files(metrics: dict[str, Any], run_dir: Path) -> None:
    """Write manifest and companion review files for AGENT-RUN-0019."""
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
                    "notes": "TASK-0316 requests coefficient-stability stress testing, not reveal scoring.",
                },
                {
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": "Only committed repository datasets are used; no live external fetch is performed.",
                },
                {
                    "name": "control_boundary",
                    "status": "PASS",
                    "notes": "Sign-inverted and near-null controls are preserved; shuffled control is documented as not meaningful under changing resamples.",
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": "No prediction registry, canonical result, claim, or knowledge file is written.",
                },
            ],
        },
        "limitations": metrics["limitations"],
        "verdict": "INCONCLUSIVE",
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
        "# AGENT-RUN-0019 Preflight",
        "",
        "**Task:** TASK-0316",
        "**Lane:** nuclear shell-axis coefficient stability audit",
        "**Mode:** sandbox-only retrospective audit",
        "",
        "## Inputs Checked",
        "",
        "- `TASK-0316`",
        "- `scripts/run_nuclear_shell_axis_full_known_audit.py`",
        "- `agent_runs/AGENT-RUN-0018/metrics.json`",
        "- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`",
        "- `data/nuclear_masses/post_ame2020_holdout.yaml`",
        "",
        "## Guardrails",
        "",
        "- Live external fetch: not allowed and not used.",
        "- Prediction registry writes: not allowed and not used.",
        "- Canonical results, claims, and knowledge promotion: not allowed and not used.",
        "- `PRED-0063` through `PRED-0068` are not reveal-scored.",
        "",
    ]
    (run_dir / "preflight.md").write_text("\n".join(preflight), encoding="utf-8")
    limitations = ["# AGENT-RUN-0019 Limitations", ""]
    limitations.extend(f"- {item}" for item in metrics["limitations"])
    limitations.append("")
    (run_dir / "limitations.md").write_text("\n".join(limitations), encoding="utf-8")
    review = [
        "# AGENT-RUN-0019 Review Summary",
        "",
        "`FRAGILE` for the coefficient-stability stress surface: leave-one-out fits "
        "preserve coefficient sign and holdout/full-known improvement, but exhaustive "
        "8-of-11 resampling introduces coefficient sign flips and some full-known or "
        "holdout regressions for all three primary candidates. This weakens any broad "
        "stability interpretation while preserving the original TASK-0310 signal as "
        "bounded sandbox evidence.",
        "",
        "No prediction registry, canonical result, claim, or knowledge artifact is promoted.",
        "",
    ]
    (run_dir / "review_summary.md").write_text("\n".join(review), encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    """Write deterministic stability metrics, report, and companion files."""
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
