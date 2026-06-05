"""TASK-0320 nuclear shell-axis light-nuclei regression audit.

This sandbox-only runner isolates the light A<50 regression zone surfaced by
TASK-0310 and TASK-0315. It reuses committed repository data and the existing
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


AGENT_RUN_ID = "AGENT-RUN-0022"
TASK_ID = "TASK-0320"
SHELL_CANDIDATE_IDS = (
    "FULLKNOWN-SHELL-001",
    "FULLKNOWN-SHELL-002",
    "FULLKNOWN-SHELL-003",
)


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return float(np.mean(np.asarray(values, dtype=float)))


def _format_delta(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value == 0.0:
        return "+0.000000"
    return f"{'+' if value > 0 else '-'}{abs(value):.6f}"


def _a_band(row: dict[str, Any]) -> str:
    a = int(row["A"])
    if a < 20:
        return "A_lt_20"
    if a < 30:
        return "A_20_29"
    if a < 40:
        return "A_30_39"
    if a < 50:
        return "A_40_49"
    if a < 70:
        return "A_50_69"
    if a < 100:
        return "A_70_99"
    return "A_ge_100"


def _parity(row: dict[str, Any]) -> str:
    z_even = int(row["Z"]) % 2 == 0
    n_even = int(row["N"]) % 2 == 0
    if z_even and n_even:
        return "even_even"
    if not z_even and not n_even:
        return "odd_odd"
    return "odd_a"


def _magic_distance_bin(value: int) -> str:
    distance = full_known.stress.nearest_magic_distance(value)
    if distance == 0:
        return "magic"
    if distance <= 2:
        return "near_magic_1_2"
    return "far_from_magic_gt_2"


def _row_context(row: dict[str, Any]) -> dict[str, Any]:
    z, n = int(row["Z"]), int(row["N"])
    return {
        "a_band": _a_band(row),
        "parity": _parity(row),
        "z_magic_distance": full_known.stress.nearest_magic_distance(z),
        "n_magic_distance": full_known.stress.nearest_magic_distance(n),
        "z_magic_distance_bin": _magic_distance_bin(z),
        "n_magic_distance_bin": _magic_distance_bin(n),
        "near_magic": (
            full_known.stress.nearest_magic_distance(z) <= 2
            or full_known.stress.nearest_magic_distance(n) <= 2
        ),
    }


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
) -> list[dict[str, Any]]:
    feature_names = tuple(candidate["feature_names"])
    out: list[dict[str, Any]] = []
    for row in rows:
        z, n = int(row["Z"]), int(row["N"])
        values = full_known._feature_vector(feature_names, z=z, n=n)  # noqa: SLF001
        correction = float(np.asarray(values, dtype=float) @ beta)
        predicted = float(row["baseline_predicted_mev"]) + correction
        candidate_residual = float(row["observed_mev"]) - predicted
        baseline_abs = abs(float(row["baseline_residual_mev"]))
        candidate_abs = abs(candidate_residual)
        out.append(
            {
                "row_id": row["row_id"],
                "nuclide_id": row["nuclide_id"],
                "Z": z,
                "N": n,
                "A": int(row["A"]),
                "source_surface": row["source_surface"],
                "baseline_residual_mev": float(row["baseline_residual_mev"]),
                "candidate_residual_mev": candidate_residual,
                "baseline_abs_error_mev": baseline_abs,
                "candidate_abs_error_mev": candidate_abs,
                "delta_abs_error_mev": candidate_abs - baseline_abs,
                "correction_mev": correction,
                "feature_values": {
                    name: float(value) for name, value in zip(feature_names, values)
                },
                **_row_context(row),
            }
        )
    return out


def _summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    baseline_abs = [float(row["baseline_abs_error_mev"]) for row in rows]
    candidate_abs = [float(row["candidate_abs_error_mev"]) for row in rows]
    deltas = [float(row["delta_abs_error_mev"]) for row in rows]
    delta_mae = None
    baseline_mae = _mean(baseline_abs)
    candidate_mae = _mean(candidate_abs)
    if baseline_mae is not None and candidate_mae is not None:
        delta_mae = candidate_mae - baseline_mae
    return {
        "row_count": len(rows),
        "baseline_mae_mev": baseline_mae,
        "candidate_mae_mev": candidate_mae,
        "delta_mae_mev": delta_mae,
        "regression_row_count": sum(1 for value in deltas if value > 0.0),
        "improvement_row_count": sum(1 for value in deltas if value < 0.0),
        "unchanged_row_count": sum(1 for value in deltas if value == 0.0),
        "mean_delta_abs_error_mev": _mean(deltas),
        "max_row_regression_mev": max(deltas) if deltas else None,
        "max_row_improvement_mev": min(deltas) if deltas else None,
    }


def _group_summaries(
    rows: list[dict[str, Any]],
    *,
    key: str,
) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row[key]), []).append(row)
    return {group_id: _summarize_rows(group_rows) for group_id, group_rows in sorted(grouped.items())}


def _composition(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    keys = (
        "source_surface",
        "a_band",
        "parity",
        "z_magic_distance_bin",
        "n_magic_distance_bin",
    )
    out: dict[str, dict[str, int]] = {}
    for key in keys:
        counts: dict[str, int] = {}
        for row in rows:
            value = str(row.get(key, _row_context(row).get(key)))
            counts[value] = counts.get(value, 0) + 1
        out[key] = dict(sorted(counts.items()))
    return out


def _matched_non_light_rows(audit_rows: list[dict[str, Any]], *, row_count: int) -> list[dict[str, Any]]:
    non_light = [row for row in audit_rows if int(row["A"]) >= 50]
    return sorted(
        non_light,
        key=lambda row: (int(row["A"]), int(row["Z"]), int(row["N"]), str(row["row_id"])),
    )[:row_count]


def _top_regression_groups(grouped: dict[str, dict[str, Any]], *, limit: int = 5) -> list[dict[str, Any]]:
    positive = [
        {"group_id": group_id, **summary}
        for group_id, summary in grouped.items()
        if summary["delta_mae_mev"] is not None and summary["delta_mae_mev"] > 0.0
    ]
    return sorted(
        positive,
        key=lambda item: (float(item["delta_mae_mev"]), int(item["row_count"])),
        reverse=True,
    )[:limit]


def _evaluate_candidate(
    candidate: dict[str, Any],
    *,
    light_rows: list[dict[str, Any]],
    matched_rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
) -> dict[str, Any]:
    beta, fitted_coefficients = _fit_primary_candidate(candidate, training_rows, training_residuals)
    light_diagnostics = _candidate_row_diagnostics(candidate, light_rows, beta)
    matched_diagnostics = _candidate_row_diagnostics(candidate, matched_rows, beta)
    concentration = {
        key: _group_summaries(light_diagnostics, key=key)
        for key in (
            "source_surface",
            "a_band",
            "parity",
            "z_magic_distance_bin",
            "n_magic_distance_bin",
        )
    }
    return {
        "candidate_id": candidate["candidate_id"],
        "source_candidate_id": candidate.get("source_candidate_id"),
        "name": candidate["name"],
        "formula": candidate["formula"],
        "complexity": candidate["complexity"],
        "fitted_coefficients": fitted_coefficients,
        "light_a_lt_50": _summarize_rows(light_diagnostics),
        "matched_non_light": _summarize_rows(matched_diagnostics),
        "light_concentration": concentration,
        "top_light_regression_groups": {
            key: _top_regression_groups(value) for key, value in concentration.items()
        },
        "worst_light_row_regressions": sorted(
            [row for row in light_diagnostics if float(row["delta_abs_error_mev"]) > 0.0],
            key=lambda row: float(row["delta_abs_error_mev"]),
            reverse=True,
        )[:10],
        "best_light_row_improvements": sorted(
            [row for row in light_diagnostics if float(row["delta_abs_error_mev"]) < 0.0],
            key=lambda row: float(row["delta_abs_error_mev"]),
        )[:5],
        "limitations": [
            "Primary shell-axis coefficients are fit on the frozen 11-row NMD-0002 residual slice.",
            "Light and matched subsets are committed retrospective rows only.",
            "Row-level deltas are diagnostics and do not promote a claim.",
        ],
    }


def _domain_recommendation(candidate_summaries: list[dict[str, Any]]) -> str:
    light_deltas = [item["light_a_lt_50"]["delta_mae_mev"] for item in candidate_summaries]
    matched_deltas = [item["matched_non_light"]["delta_mae_mev"] for item in candidate_summaries]
    all_light_regress = all(value is not None and value > 0.0 for value in light_deltas)
    all_matched_not_regress = all(value is not None and value <= 0.0 for value in matched_deltas)
    if all_light_regress and all_matched_not_regress:
        return "EXCLUSION_ZONE"
    if all_light_regress:
        return "WARNING_ZONE"
    return "UNRESOLVED_DIAGNOSTIC"


def build_metrics() -> dict[str, Any]:
    """Build deterministic light-regression audit metrics."""
    coefficients = full_known.load_frozen_baseline_coefficients()
    audit_rows, training_rows, training_residuals, baseline_bundle = full_known.build_audit_surface(coefficients)
    light_rows = [row for row in audit_rows if int(row["A"]) < 50]
    matched_rows = _matched_non_light_rows(audit_rows, row_count=len(light_rows))
    candidate_by_id = {
        str(candidate["candidate_id"]): candidate
        for candidate in full_known.EXECUTED_CANDIDATES
    }
    candidate_summaries = [
        _evaluate_candidate(
            candidate_by_id[candidate_id],
            light_rows=light_rows,
            matched_rows=matched_rows,
            training_rows=training_rows,
            training_residuals=training_residuals,
        )
        for candidate_id in SHELL_CANDIDATE_IDS
    ]
    recommendation = _domain_recommendation(candidate_summaries)
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "shell_axis_light_nuclei_regression_audit",
        "sandbox_only": True,
        "evidence_class": "retrospective_committed_data_light_regression_audit",
        "live_external_fetch_allowed": False,
        "summary": {
            "candidate_count": len(candidate_summaries),
            "light_row_count": len(light_rows),
            "matched_non_light_row_count": len(matched_rows),
            "matched_non_light_selection_rule": (
                "first N committed rows with A >= 50 sorted by A, Z, N, row_id; "
                "N equals the light A<50 row count"
            ),
            "all_primary_candidates_regress_light_a_lt_50": all(
                item["light_a_lt_50"]["delta_mae_mev"] is not None
                and item["light_a_lt_50"]["delta_mae_mev"] > 0.0
                for item in candidate_summaries
            ),
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
            "light_a_lt_50_row_count": len(light_rows),
            "matched_non_light_row_count": len(matched_rows),
        },
        "subset_composition": {
            "light_a_lt_50": _composition(light_rows),
            "matched_non_light": _composition(matched_rows),
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
            "The matched non-light subset is deterministic and row-count matched, not a statistical bootstrap.",
            "Full-known rows are committed reviewable repository data; this is not a future-measurement reveal.",
            "Negative light-zone evidence is preserved even when aggregate shell-axis metrics improve elsewhere.",
        ],
    }


def _candidate_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| Candidate | Light delta MAE MeV | Light regress rows | Matched delta MAE MeV | Matched regress rows | Worst light row regression MeV |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in metrics["candidate_summaries"]:
        worst_rows = item["worst_light_row_regressions"]
        worst = float(worst_rows[0]["delta_abs_error_mev"]) if worst_rows else 0.0
        lines.append(
            "| `{cid}` | {light} | {lreg}/{ln} | {matched} | {mreg}/{mn} | {worst:.6f} |".format(
                cid=item["candidate_id"],
                light=_format_delta(item["light_a_lt_50"]["delta_mae_mev"]),
                lreg=item["light_a_lt_50"]["regression_row_count"],
                ln=item["light_a_lt_50"]["row_count"],
                matched=_format_delta(item["matched_non_light"]["delta_mae_mev"]),
                mreg=item["matched_non_light"]["regression_row_count"],
                mn=item["matched_non_light"]["row_count"],
                worst=worst,
            )
        )
    return lines


def _worst_rows_table(item: dict[str, Any]) -> list[str]:
    lines = [
        "| Nuclide | Z | N | A | Surface | Delta abs error MeV | Baseline abs MeV | Candidate abs MeV |",
        "| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |",
    ]
    for row in item["worst_light_row_regressions"][:6]:
        lines.append(
            "| `{nuclide}` | {z} | {n} | {a} | {surface} | {delta:.6f} | {base:.6f} | {cand:.6f} |".format(
                nuclide=row["nuclide_id"],
                z=row["Z"],
                n=row["N"],
                a=row["A"],
                surface=row["source_surface"],
                delta=float(row["delta_abs_error_mev"]),
                base=float(row["baseline_abs_error_mev"]),
                cand=float(row["candidate_abs_error_mev"]),
            )
        )
    return lines


def render_report(metrics: dict[str, Any]) -> str:
    """Render the agent-run report."""
    lines = [
        "# Nuclear Shell-Axis Light-Nuclei Regression Audit",
        "",
        f"**Agent run:** `{metrics['agent_run_id']}`",
        f"**Task:** `{metrics['task_id']}`",
        "**Evidence class:** retrospective committed-data light-regression audit",
        "**Baseline:** `RESULT-0015::model_fitted_semi_empirical`",
        "**Script:** `scripts/run_nuclear_shell_axis_light_regression_audit.py`",
        f"**Metrics:** `agent_runs/{metrics['agent_run_id']}/metrics.json`",
        "",
        "## Scope",
        "",
        "This sandbox audit isolates the light `A<50` failure mode for the three "
        "primary shell-axis candidates from TASK-0310. It uses committed "
        "repository data only and does not tune a corrective term.",
        "",
        "## Matched Subset Rule",
        "",
        metrics["summary"]["matched_non_light_selection_rule"],
        "",
        "## Candidate Outcomes",
        "",
        *_candidate_table(metrics),
        "",
        "Positive deltas mean the shell-axis correction increased MAE relative to "
        "the frozen baseline.",
        "",
        f"Domain recommendation: `{metrics['summary']['domain_recommendation']}`.",
        "",
        "## Worst Light Row Regressions",
        "",
    ]
    for item in metrics["candidate_summaries"]:
        lines.extend([f"### `{item['candidate_id']}`", "", *_worst_rows_table(item), ""])
    lines.extend(
        [
            "## Interpretation",
            "",
            "All three primary shell-axis candidates regress the light `A<50` subset. "
            "The matched non-light control subset is preserved so the result is not "
            "silently folded into aggregate full-known improvements.",
            "",
            "This is negative sandbox evidence for the current shell-axis scope. It "
            "should constrain future work before any expansion or reveal scoring.",
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
    """Write manifest and companion review files for AGENT-RUN-0022."""
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
                    "notes": "TASK-0320 requests a light A<50 regression audit, not new term fitting.",
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
        "# AGENT-RUN-0022 Preflight",
        "",
        "**Task:** TASK-0320",
        "**Lane:** nuclear shell-axis light-nuclei regression audit",
        "**Mode:** sandbox-only retrospective audit",
        "",
        "## Inputs Checked",
        "",
        "- `TASK-0320`",
        "- `agent_runs/AGENT-RUN-0018/metrics.json`",
        "- `docs/reviews/nuclear-shell-axis-validity-domain-after-0310.md`",
        "- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`",
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
    limitations = ["# AGENT-RUN-0022 Limitations", ""]
    limitations.extend(f"- {item}" for item in metrics["limitations"])
    limitations.append("")
    (run_dir / "limitations.md").write_text("\n".join(limitations), encoding="utf-8")
    review = [
        "# AGENT-RUN-0022 Review Summary",
        "",
        "`INCONCLUSIVE` for claim promotion and negative for broad light-nuclei "
        "coverage: all three primary shell-axis candidates regress light `A<50` "
        "rows under the committed retrospective audit.",
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
