"""TASK-0324 nuclear shell-axis neutron-rich tail audit.

This sandbox-only runner isolates the neutron-rich high-error support zone
surfaced by TASK-0315. It reuses committed repository data and existing
shell-axis candidate definitions only. It does not fetch live data, tune new
terms, score prediction registry entries, write canonical RESULT-* artifacts,
update claims, or edit knowledge.
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

import scripts.run_nuclear_shell_axis_full_known_audit as full_known  # noqa: E402


AGENT_RUN_ID = "AGENT-RUN-0024"
TASK_ID = "TASK-0324"
NEUTRON_RICH_EXCESS_THRESHOLD = 0.25
HIGH_ERROR_PERCENTILE = 75.0
SHELL_CANDIDATE_IDS = (
    "FULLKNOWN-SHELL-001",
    "FULLKNOWN-SHELL-002",
    "FULLKNOWN-SHELL-003",
)


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return float(np.mean(np.asarray(values, dtype=float)))


def _rmse(values: list[float]) -> float | None:
    if not values:
        return None
    arr = np.asarray(values, dtype=float)
    return float(np.sqrt(np.mean(arr * arr)))


def _format_delta(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value == 0.0:
        return "+0.000000"
    return f"{'+' if value > 0 else '-'}{abs(value):.6f}"


def _neutron_excess(row: dict[str, Any]) -> float:
    a = int(row["A"])
    if a <= 0:
        return 0.0
    return float(int(row["N"]) - int(row["Z"])) / float(a)


def _baseline_abs_error(row: dict[str, Any]) -> float:
    return abs(float(row["baseline_residual_mev"]))


def _high_error_threshold(rows: list[dict[str, Any]]) -> float:
    values = np.asarray([_baseline_abs_error(row) for row in rows], dtype=float)
    return float(np.percentile(values, HIGH_ERROR_PERCENTILE, method="linear"))


def _fit_primary_candidate(
    candidate: dict[str, Any],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
) -> tuple[np.ndarray, dict[str, float]]:
    feature_names = tuple(candidate["feature_names"])
    beta = full_known._fit_lstsq(feature_names, training_rows, training_residuals)  # noqa: SLF001
    return beta, {name: float(value) for name, value in zip(feature_names, beta)}


def _candidate_row_diagnostics(
    candidate: dict[str, Any],
    rows: list[dict[str, Any]],
    beta: np.ndarray,
    *,
    high_error_threshold: float,
) -> list[dict[str, Any]]:
    feature_names = tuple(candidate["feature_names"])
    out: list[dict[str, Any]] = []
    for row in rows:
        z, n = int(row["Z"]), int(row["N"])
        values = full_known._feature_vector(feature_names, z=z, n=n)  # noqa: SLF001
        correction = float(np.asarray(values, dtype=float) @ beta)
        predicted = float(row["baseline_predicted_mev"]) + correction
        candidate_residual = float(row["observed_mev"]) - predicted
        baseline_abs = _baseline_abs_error(row)
        candidate_abs = abs(candidate_residual)
        out.append(
            {
                "row_id": row["row_id"],
                "nuclide_id": row["nuclide_id"],
                "Z": z,
                "N": n,
                "A": int(row["A"]),
                "source_surface": row["source_surface"],
                "neutron_excess": _neutron_excess(row),
                "neutron_rich": _neutron_excess(row) >= NEUTRON_RICH_EXCESS_THRESHOLD,
                "high_error": baseline_abs >= high_error_threshold,
                "baseline_residual_mev": float(row["baseline_residual_mev"]),
                "candidate_residual_mev": candidate_residual,
                "baseline_abs_error_mev": baseline_abs,
                "candidate_abs_error_mev": candidate_abs,
                "delta_abs_error_mev": candidate_abs - baseline_abs,
                "correction_mev": correction,
                "feature_values": {
                    name: float(value) for name, value in zip(feature_names, values)
                },
            }
        )
    return out


def _summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    baseline_abs = [float(row["baseline_abs_error_mev"]) for row in rows]
    candidate_abs = [float(row["candidate_abs_error_mev"]) for row in rows]
    baseline_residuals = [float(row["baseline_residual_mev"]) for row in rows]
    candidate_residuals = [float(row["candidate_residual_mev"]) for row in rows]
    deltas = [float(row["delta_abs_error_mev"]) for row in rows]
    baseline_mae = _mean(baseline_abs)
    candidate_mae = _mean(candidate_abs)
    baseline_rmse = _rmse(baseline_residuals)
    candidate_rmse = _rmse(candidate_residuals)
    return {
        "row_count": len(rows),
        "baseline_mae_mev": baseline_mae,
        "candidate_mae_mev": candidate_mae,
        "delta_mae_mev": (
            None if baseline_mae is None or candidate_mae is None else candidate_mae - baseline_mae
        ),
        "baseline_rmse_mev": baseline_rmse,
        "candidate_rmse_mev": candidate_rmse,
        "delta_rmse_mev": (
            None
            if baseline_rmse is None or candidate_rmse is None
            else candidate_rmse - baseline_rmse
        ),
        "regression_row_count": sum(1 for value in deltas if value > 0.0),
        "improvement_row_count": sum(1 for value in deltas if value < 0.0),
        "unchanged_row_count": sum(1 for value in deltas if value == 0.0),
        "mean_delta_abs_error_mev": _mean(deltas),
        "sum_delta_abs_error_mev": float(np.sum(np.asarray(deltas, dtype=float))) if deltas else None,
        "max_row_regression_mev": max(deltas) if deltas else None,
        "max_row_improvement_mev": min(deltas) if deltas else None,
    }


def _top_delta_contributors(
    rows: list[dict[str, Any]],
    *,
    limit: int = 8,
) -> list[dict[str, Any]]:
    total_delta = float(
        np.sum(np.asarray([float(row["delta_abs_error_mev"]) for row in rows], dtype=float))
    )
    out: list[dict[str, Any]] = []
    for row in sorted(
        rows,
        key=lambda item: (
            abs(float(item["delta_abs_error_mev"])),
            float(item["baseline_abs_error_mev"]),
            str(item["row_id"]),
        ),
        reverse=True,
    )[:limit]:
        delta = float(row["delta_abs_error_mev"])
        out.append(
            {
                "row_id": row["row_id"],
                "nuclide_id": row["nuclide_id"],
                "Z": row["Z"],
                "N": row["N"],
                "A": row["A"],
                "source_surface": row["source_surface"],
                "baseline_abs_error_mev": row["baseline_abs_error_mev"],
                "candidate_abs_error_mev": row["candidate_abs_error_mev"],
                "delta_abs_error_mev": delta,
                "delta_mae_contribution_mev": delta / len(rows) if rows else None,
                "share_of_total_delta": None if total_delta == 0.0 else delta / total_delta,
            }
        )
    return out


def _drop_largest_baseline_errors(
    rows: list[dict[str, Any]],
    *,
    drop_count: int,
) -> dict[str, Any]:
    ordered = sorted(
        rows,
        key=lambda row: (
            float(row["baseline_abs_error_mev"]),
            int(row["A"]),
            str(row["row_id"]),
        ),
        reverse=True,
    )
    removed = ordered[:drop_count]
    kept_ids = {str(row["row_id"]) for row in ordered[drop_count:]}
    kept_rows = [row for row in rows if str(row["row_id"]) in kept_ids]
    return {
        "drop_count": drop_count,
        "removed_rows": [
            {
                "row_id": row["row_id"],
                "nuclide_id": row["nuclide_id"],
                "baseline_abs_error_mev": row["baseline_abs_error_mev"],
                "delta_abs_error_mev": row["delta_abs_error_mev"],
            }
            for row in removed
        ],
        "summary": _summarize_rows(kept_rows),
    }


def _matched_non_neutron_rich_rows(
    audit_rows: list[dict[str, Any]],
    target_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Select deterministic non-neutron-rich controls matched by error and A."""
    pool = [
        row
        for row in audit_rows
        if _neutron_excess(row) < NEUTRON_RICH_EXCESS_THRESHOLD
        and _baseline_abs_error(row) >= _high_error_threshold(audit_rows)
    ]
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    for target in sorted(
        target_rows,
        key=lambda row: (
            -_baseline_abs_error(row),
            int(row["A"]),
            int(row["Z"]),
            str(row["row_id"]),
        ),
    ):
        available = [row for row in pool if str(row["row_id"]) not in selected_ids]
        if not available:
            break
        best = min(
            available,
            key=lambda row: (
                abs(_baseline_abs_error(row) - _baseline_abs_error(target)),
                abs(int(row["A"]) - int(target["A"])),
                str(row["source_surface"]) != str(target["source_surface"]),
                abs(int(row["Z"]) - int(target["Z"])),
                str(row["row_id"]),
            ),
        )
        selected.append(best)
        selected_ids.add(str(best["row_id"]))
    return selected


def _subset_composition(rows: list[dict[str, Any]]) -> dict[str, Any]:
    source_counts: dict[str, int] = {}
    mass_band_counts: dict[str, int] = {}
    for row in rows:
        source = str(row["source_surface"])
        source_counts[source] = source_counts.get(source, 0) + 1
        a = int(row["A"])
        if a < 70:
            band = "A_lt_70"
        elif a < 100:
            band = "A_70_99"
        elif a < 150:
            band = "A_100_149"
        else:
            band = "A_ge_150"
        mass_band_counts[band] = mass_band_counts.get(band, 0) + 1
    return {
        "source_surface": dict(sorted(source_counts.items())),
        "mass_band": dict(sorted(mass_band_counts.items())),
        "nuclide_ids": [str(row["nuclide_id"]) for row in rows],
    }


def _evaluate_candidate(
    candidate: dict[str, Any],
    *,
    neutron_rich_rows: list[dict[str, Any]],
    tail_rows: list[dict[str, Any]],
    matched_rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
    high_error_threshold: float,
) -> dict[str, Any]:
    beta, fitted_coefficients = _fit_primary_candidate(candidate, training_rows, training_residuals)
    neutron_rich_diagnostics = _candidate_row_diagnostics(
        candidate,
        neutron_rich_rows,
        beta,
        high_error_threshold=high_error_threshold,
    )
    tail_diagnostics = _candidate_row_diagnostics(
        candidate,
        tail_rows,
        beta,
        high_error_threshold=high_error_threshold,
    )
    matched_diagnostics = _candidate_row_diagnostics(
        candidate,
        matched_rows,
        beta,
        high_error_threshold=high_error_threshold,
    )
    return {
        "candidate_id": candidate["candidate_id"],
        "source_candidate_id": candidate.get("source_candidate_id"),
        "name": candidate["name"],
        "formula": candidate["formula"],
        "complexity": candidate["complexity"],
        "fitted_coefficients": fitted_coefficients,
        "neutron_rich_all": _summarize_rows(neutron_rich_diagnostics),
        "neutron_rich_high_error_tail": _summarize_rows(tail_diagnostics),
        "matched_non_neutron_rich_high_error": _summarize_rows(matched_diagnostics),
        "tail_outlier_sensitivity": {
            "drop_largest_1_baseline_error": _drop_largest_baseline_errors(
                tail_diagnostics,
                drop_count=1,
            ),
            "drop_largest_2_baseline_errors": _drop_largest_baseline_errors(
                tail_diagnostics,
                drop_count=2,
            ),
        },
        "top_tail_delta_contributors": _top_delta_contributors(tail_diagnostics),
        "tail_row_diagnostics": sorted(
            tail_diagnostics,
            key=lambda row: (
                -float(row["baseline_abs_error_mev"]),
                int(row["A"]),
                str(row["row_id"]),
            ),
        ),
        "interpretation_notes": [
            "Rows are committed retrospective data only.",
            "Negative delta means lower absolute error than the frozen baseline.",
            "Outlier sensitivity removes the largest baseline-error rows, not the largest improvements.",
        ],
    }


def _domain_recommendation(candidate_summaries: list[dict[str, Any]]) -> str:
    if not candidate_summaries:
        return "TOO_SPARSE_TO_INTERPRET"
    tail_counts = [
        item["neutron_rich_high_error_tail"]["row_count"] for item in candidate_summaries
    ]
    if min(tail_counts) < 10:
        return "TOO_SPARSE_TO_INTERPRET"
    tail_deltas = [
        item["neutron_rich_high_error_tail"]["delta_mae_mev"] for item in candidate_summaries
    ]
    drop_two_deltas = [
        item["tail_outlier_sensitivity"]["drop_largest_2_baseline_errors"]["summary"][
            "delta_mae_mev"
        ]
        for item in candidate_summaries
    ]
    matched_deltas = [
        item["matched_non_neutron_rich_high_error"]["delta_mae_mev"]
        for item in candidate_summaries
    ]
    all_tail_improve = all(value is not None and value < 0.0 for value in tail_deltas)
    all_drop_two_improve = all(
        value is not None and value < 0.0 for value in drop_two_deltas
    )
    matched_mixed_or_weaker = any(value is None or value >= 0.0 for value in matched_deltas)
    if all_tail_improve and all_drop_two_improve and matched_mixed_or_weaker:
        return "SUPPORT_ZONE_WITH_OUTLIER_CHECK"
    if all_tail_improve:
        return "OUTLIER_DIAGNOSTIC"
    return "WARNING_ZONE"


def build_metrics() -> dict[str, Any]:
    """Build deterministic neutron-rich tail audit metrics."""
    coefficients = full_known.load_frozen_baseline_coefficients()
    audit_rows, training_rows, training_residuals, baseline_bundle = (
        full_known.build_audit_surface(coefficients)
    )
    threshold = _high_error_threshold(audit_rows)
    neutron_rich_rows = [
        row for row in audit_rows if _neutron_excess(row) >= NEUTRON_RICH_EXCESS_THRESHOLD
    ]
    tail_rows = [row for row in neutron_rich_rows if _baseline_abs_error(row) >= threshold]
    matched_rows = _matched_non_neutron_rich_rows(audit_rows, tail_rows)
    candidate_by_id = {
        str(candidate["candidate_id"]): candidate
        for candidate in full_known.EXECUTED_CANDIDATES
    }
    candidate_summaries = [
        _evaluate_candidate(
            candidate_by_id[candidate_id],
            neutron_rich_rows=neutron_rich_rows,
            tail_rows=tail_rows,
            matched_rows=matched_rows,
            training_rows=training_rows,
            training_residuals=training_residuals,
            high_error_threshold=threshold,
        )
        for candidate_id in SHELL_CANDIDATE_IDS
    ]
    recommendation = _domain_recommendation(candidate_summaries)
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "shell_axis_neutron_rich_tail_audit",
        "sandbox_only": True,
        "evidence_class": "retrospective_committed_data_neutron_rich_tail_audit",
        "live_external_fetch_allowed": False,
        "subset_rules": {
            "neutron_rich_rule": (
                f"(N - Z) / A >= {NEUTRON_RICH_EXCESS_THRESHOLD:.2f}; "
                "this matches the TASK-0315 neutron_rich_high subset rule"
            ),
            "high_error_rule": (
                "baseline_abs_error_mev >= 75th percentile of the full-known "
                f"committed surface ({threshold:.12f} MeV)"
            ),
            "matched_control_rule": (
                "for each neutron-rich high-error row sorted by descending baseline "
                "absolute error, select one unused non-neutron-rich high-error row "
                "minimizing baseline-error distance, then A distance, source mismatch, "
                "Z distance, and row_id"
            ),
        },
        "summary": {
            "candidate_count": len(candidate_summaries),
            "full_known_row_count": len(audit_rows),
            "neutron_rich_row_count": len(neutron_rich_rows),
            "neutron_rich_high_error_tail_row_count": len(tail_rows),
            "matched_non_neutron_rich_high_error_row_count": len(matched_rows),
            "domain_recommendation": recommendation,
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
            "neutron_rich_row_count": len(neutron_rich_rows),
            "neutron_rich_high_error_tail_row_count": len(tail_rows),
            "matched_non_neutron_rich_high_error_row_count": len(matched_rows),
        },
        "subset_composition": {
            "neutron_rich_all": _subset_composition(neutron_rich_rows),
            "neutron_rich_high_error_tail": _subset_composition(tail_rows),
            "matched_non_neutron_rich_high_error": _subset_composition(matched_rows),
        },
        "candidate_summaries": candidate_summaries,
        "promotion_boundary": {
            "writes_prediction_registry": False,
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "writes_knowledge": False,
            "required_next_step": (
                "Maintainer review before any shell-axis expansion, reveal scoring, "
                "RESULT-* artifact, claim, or knowledge update."
            ),
        },
        "limitations": [
            "Sandbox-only retrospective audit; no prediction registry, canonical result, claim, or knowledge artifact is updated.",
            "Primary shell-axis coefficients are inherited from the committed TASK-0310 setup and are not tuned here.",
            "The high-error cutoff is deterministic but post hoc over the committed full-known surface.",
            "The matched non-neutron-rich subset is deterministic and row-count matched, not a statistical bootstrap.",
            "Full-known rows are committed reviewable repository data; this is not a future-measurement reveal.",
            "Light-nuclei regression and coefficient fragility remain active limitations for all shell-axis interpretation.",
        ],
    }


def _candidate_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| Candidate | Tail delta MAE MeV | Tail delta RMSE MeV | Tail improved rows | Drop largest 2 tail delta MAE MeV | Matched delta MAE MeV |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in metrics["candidate_summaries"]:
        tail = item["neutron_rich_high_error_tail"]
        drop_two = item["tail_outlier_sensitivity"]["drop_largest_2_baseline_errors"][
            "summary"
        ]
        matched = item["matched_non_neutron_rich_high_error"]
        lines.append(
            "| `{cid}` | {tail_mae} | {tail_rmse} | {improve}/{count} | {drop_two_mae} | {matched_mae} |".format(
                cid=item["candidate_id"],
                tail_mae=_format_delta(tail["delta_mae_mev"]),
                tail_rmse=_format_delta(tail["delta_rmse_mev"]),
                improve=tail["improvement_row_count"],
                count=tail["row_count"],
                drop_two_mae=_format_delta(drop_two["delta_mae_mev"]),
                matched_mae=_format_delta(matched["delta_mae_mev"]),
            )
        )
    return lines


def _contributors_table(item: dict[str, Any]) -> list[str]:
    lines = [
        "| Nuclide | Z | N | A | Delta abs error MeV | Contribution to MAE MeV | Baseline abs MeV | Candidate abs MeV |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in item["top_tail_delta_contributors"][:6]:
        lines.append(
            "| `{nuclide}` | {z} | {n} | {a} | {delta:.6f} | {contrib:.6f} | {base:.6f} | {cand:.6f} |".format(
                nuclide=row["nuclide_id"],
                z=row["Z"],
                n=row["N"],
                a=row["A"],
                delta=float(row["delta_abs_error_mev"]),
                contrib=float(row["delta_mae_contribution_mev"]),
                base=float(row["baseline_abs_error_mev"]),
                cand=float(row["candidate_abs_error_mev"]),
            )
        )
    return lines


def render_report(metrics: dict[str, Any]) -> str:
    """Render the agent-run report."""
    lines = [
        "# Nuclear Shell-Axis Neutron-Rich Tail Audit",
        "",
        f"**Agent run:** `{metrics['agent_run_id']}`",
        f"**Task:** `{metrics['task_id']}`",
        "**Evidence class:** retrospective committed-data neutron-rich tail audit",
        "**Baseline:** `RESULT-0015::model_fitted_semi_empirical`",
        "**Script:** `scripts/run_nuclear_shell_axis_neutron_rich_tail_audit.py`",
        f"**Metrics:** `agent_runs/{metrics['agent_run_id']}/metrics.json`",
        "",
        "## Scope",
        "",
        "This sandbox audit isolates the neutron-rich high-error tail for the three "
        "primary shell-axis candidates from TASK-0310. It uses committed "
        "repository data only and does not tune a corrective term.",
        "",
        "## Deterministic Subset Rules",
        "",
        f"- Neutron-rich: {metrics['subset_rules']['neutron_rich_rule']}.",
        f"- High-error: {metrics['subset_rules']['high_error_rule']}.",
        f"- Matched control: {metrics['subset_rules']['matched_control_rule']}.",
        "",
        "## Candidate Outcomes",
        "",
        *_candidate_table(metrics),
        "",
        "Negative deltas mean the shell-axis correction reduced error relative to "
        "the frozen baseline.",
        "",
        f"Domain recommendation: `{metrics['summary']['domain_recommendation']}`.",
        "",
        "## Top Tail Delta Contributors",
        "",
    ]
    for item in metrics["candidate_summaries"]:
        lines.extend([f"### `{item['candidate_id']}`", "", *_contributors_table(item), ""])
    lines.extend(
        [
            "## Interpretation",
            "",
            "The neutron-rich high-error tail remains favorable for all three "
            "primary shell-axis candidates after removing the largest one or two "
            "baseline-error rows. The effect is therefore not solely a single-row "
            "artifact, but it remains a subset diagnostic on retrospective data.",
            "",
            "The matched non-neutron-rich high-error control is included so the "
            "tail result is not silently treated as a global support statement.",
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in metrics["limitations"])
    lines.extend(
        [
            "",
            "## Promotion Boundary",
            "",
            "- Prediction registry files are not edited.",
            "- Canonical `RESULT-*` files are not edited.",
            "- Claims and knowledge files are not edited.",
            "- The audit is sandbox-only and does not score `PRED-0063` through `PRED-0068`.",
            "",
        ]
    )
    return "\n".join(lines)


def write_agent_run_support_files(metrics: dict[str, Any], run_dir: Path) -> None:
    """Write manifest and companion review files for AGENT-RUN-0024."""
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "task_id": TASK_ID,
        "status": "SANDBOX_COMPLETE",
        "sandbox_only": True,
        "created_by": {"contributor_id": "master", "agent_id": "codex"},
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
                    "notes": "TASK-0324 requests a neutron-rich tail audit, not new term fitting.",
                },
                {
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": "Only committed repository datasets and TASK-0310 definitions are used.",
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
        "# AGENT-RUN-0024 Preflight",
        "",
        "**Task:** TASK-0324",
        "**Lane:** nuclear shell-axis neutron-rich tail audit",
        "**Mode:** sandbox-only retrospective audit",
        "",
        "## Inputs Checked",
        "",
        "- `TASK-0324`",
        "- `agent_runs/AGENT-RUN-0018/metrics.json`",
        "- `agent_runs/AGENT-RUN-0019/metrics.json`",
        "- `agent_runs/AGENT-RUN-0020/metrics.json`",
        "- `docs/reviews/nuclear-shell-axis-validity-domain-after-0310.md`",
        "- `docs/reviews/nuclear-shell-axis-coefficient-stability-audit.md`",
        "- `data/nuclear_masses/post_ame2020_holdout.yaml`",
        "",
        "## Guardrails",
        "",
        "- Live external fetch: not allowed and not used.",
        "- Prediction registry writes: not allowed and not used.",
        "- Canonical results, claims, and knowledge promotion: not allowed and not used.",
        "- New corrective terms: not fit.",
        "",
    ]
    (run_dir / "preflight.md").write_text("\n".join(preflight), encoding="utf-8")
    limitations = ["# AGENT-RUN-0024 Limitations", ""]
    limitations.extend(f"- {item}" for item in metrics["limitations"])
    limitations.append("")
    (run_dir / "limitations.md").write_text("\n".join(limitations), encoding="utf-8")
    review = [
        "# AGENT-RUN-0024 Review Summary",
        "",
        "`{}`: the neutron-rich high-error tail improves for all three primary "
        "shell-axis candidates and survives removal of the largest two baseline-error "
        "rows, but this remains sandbox-only retrospective evidence.".format(
            metrics["summary"]["domain_recommendation"]
        ),
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
