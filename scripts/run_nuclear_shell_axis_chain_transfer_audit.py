"""TASK-0323 nuclear shell-axis isotope-chain transfer audit.

This sandbox-only runner checks whether the committed shell-axis signal
transfers across isotope chains or hides chain-local regressions. It reuses
committed TASK-0310 shell-axis candidates and TASK-0317 non-shell controls.
It does not fetch live data, fit new formula families, score prediction
registry entries, write canonical RESULT-* artifacts, update claims, or edit
knowledge.
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
import scripts.run_nuclear_shell_axis_specificity_controls as specificity  # noqa: E402


AGENT_RUN_ID = "AGENT-RUN-0023"
TASK_ID = "TASK-0323"
CHAIN_MIN_ROWS = 3
SHELL_CANDIDATE_IDS = (
    "FULLKNOWN-SHELL-001",
    "FULLKNOWN-SHELL-002",
    "FULLKNOWN-SHELL-003",
)
NON_SHELL_CONTROL_IDS = (
    "SPECIFICITY-CONTROL-001",
    "SPECIFICITY-CONTROL-002",
    "SPECIFICITY-CONTROL-003",
    "SPECIFICITY-CONTROL-004",
)


def _mean_abs(values: list[float]) -> float | None:
    if not values:
        return None
    return float(np.mean(np.abs(np.asarray(values, dtype=float))))


def _format_delta(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value == 0.0:
        return "+0.000000"
    return f"{'+' if value > 0 else '-'}{abs(value):.6f}"


def _chain_key(row: dict[str, Any]) -> str:
    return f"Z_{int(row['Z']):03d}"


def _group_chains(rows: list[dict[str, Any]]) -> dict[str, list[int]]:
    grouped: dict[str, list[int]] = {}
    for idx, row in enumerate(rows):
        grouped.setdefault(_chain_key(row), []).append(idx)
    return dict(sorted(grouped.items(), key=lambda item: int(item[0].split("_")[1])))


def _fit_shell_candidate(
    candidate: dict[str, Any],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
) -> tuple[np.ndarray, dict[str, float]]:
    feature_names = tuple(candidate["feature_names"])
    beta = full_known._fit_lstsq(feature_names, training_rows, training_residuals)  # noqa: SLF001
    return beta, {name: float(value) for name, value in zip(feature_names, beta)}


def _shell_residuals(
    candidate: dict[str, Any],
    *,
    rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
) -> tuple[list[float], dict[str, float]]:
    feature_names = tuple(candidate["feature_names"])
    beta, fitted = _fit_shell_candidate(candidate, training_rows, training_residuals)
    residuals: list[float] = []
    for row in rows:
        values = full_known._feature_vector(  # noqa: SLF001
            feature_names,
            z=int(row["Z"]),
            n=int(row["N"]),
        )
        correction = float(np.asarray(values, dtype=float) @ beta)
        predicted = float(row["baseline_predicted_mev"]) + correction
        residuals.append(float(row["observed_mev"]) - predicted)
    return residuals, fitted


def _control_residuals(
    control: dict[str, Any],
    *,
    rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
) -> tuple[list[float], dict[str, float]]:
    beta, fitted = specificity._fit_control(control, training_rows, training_residuals)  # noqa: SLF001
    residuals: list[float] = []
    for row in rows:
        values = np.asarray(control["feature_fn"](row), dtype=float)
        correction = 0.0 if control["fit_mode"] == "fixed_zero" else float(values @ beta)
        predicted = float(row["baseline_predicted_mev"]) + correction
        residuals.append(float(row["observed_mev"]) - predicted)
    return residuals, fitted


def _mae_delta_for_indices(
    candidate_residuals: list[float],
    baseline_residuals: list[float],
    indices: list[int],
) -> float | None:
    baseline_mae = _mean_abs([baseline_residuals[idx] for idx in indices])
    candidate_mae = _mean_abs([candidate_residuals[idx] for idx in indices])
    if baseline_mae is None or candidate_mae is None:
        return None
    return candidate_mae - baseline_mae


def _chain_summary(
    *,
    rows: list[dict[str, Any]],
    baseline_residuals: list[float],
    shell_residuals_by_id: dict[str, list[float]],
    control_residuals_by_id: dict[str, list[float]],
    chain_id: str,
    indices: list[int],
) -> dict[str, Any]:
    shell_deltas = {
        candidate_id: _mae_delta_for_indices(residuals, baseline_residuals, indices)
        for candidate_id, residuals in shell_residuals_by_id.items()
    }
    control_deltas = {
        control_id: _mae_delta_for_indices(residuals, baseline_residuals, indices)
        for control_id, residuals in control_residuals_by_id.items()
    }
    best_shell_id, best_shell_delta = min(
        shell_deltas.items(),
        key=lambda item: float("inf") if item[1] is None else float(item[1]),
    )
    best_control_id, best_control_delta = min(
        control_deltas.items(),
        key=lambda item: float("inf") if item[1] is None else float(item[1]),
    )
    row_nuclides = [str(rows[idx]["nuclide_id"]) for idx in indices]
    a_values = [int(rows[idx]["A"]) for idx in indices]
    baseline_mae = _mean_abs([baseline_residuals[idx] for idx in indices])
    return {
        "chain_id": chain_id,
        "Z": int(rows[indices[0]]["Z"]),
        "row_count": len(indices),
        "nuclide_ids": row_nuclides,
        "A_min": min(a_values),
        "A_max": max(a_values),
        "baseline_mae_mev": baseline_mae,
        "shell_axis_delta_mae_mev": shell_deltas,
        "best_shell_candidate_id": best_shell_id,
        "best_shell_delta_mae_mev": best_shell_delta,
        "best_non_shell_control_id": best_control_id,
        "best_non_shell_control_delta_mae_mev": best_control_delta,
        "shell_beats_best_non_shell_control": (
            best_shell_delta is not None
            and best_control_delta is not None
            and best_shell_delta < best_control_delta
        ),
        "diagnostic_class": "too_sparse" if len(indices) < CHAIN_MIN_ROWS else "interpretable",
    }


def _candidate_transfer_summary(chain_items: list[dict[str, Any]]) -> dict[str, Any]:
    interpretable = [
        item for item in chain_items if item["diagnostic_class"] == "interpretable"
    ]
    out: dict[str, Any] = {}
    for candidate_id in SHELL_CANDIDATE_IDS:
        deltas = [
            item["shell_axis_delta_mae_mev"][candidate_id]
            for item in interpretable
            if item["shell_axis_delta_mae_mev"][candidate_id] is not None
        ]
        improved = sum(1 for value in deltas if value < 0.0)
        regressed = sum(1 for value in deltas if value > 0.0)
        out[candidate_id] = {
            "interpretable_chain_count": len(deltas),
            "improved_chain_count": improved,
            "regressed_chain_count": regressed,
            "neutral_chain_count": len(deltas) - improved - regressed,
            "improvement_rate": improved / len(deltas) if deltas else None,
            "regression_rate": regressed / len(deltas) if deltas else None,
            "worst_chain_regressions": sorted(
                [
                    {
                        "chain_id": item["chain_id"],
                        "Z": item["Z"],
                        "row_count": item["row_count"],
                        "delta_mae_mev": item["shell_axis_delta_mae_mev"][candidate_id],
                    }
                    for item in interpretable
                    if item["shell_axis_delta_mae_mev"][candidate_id] is not None
                    and item["shell_axis_delta_mae_mev"][candidate_id] > 0.0
                ],
                key=lambda item: float(item["delta_mae_mev"]),
                reverse=True,
            )[:8],
        }
    return out


def _overall_transfer_verdict(chain_items: list[dict[str, Any]]) -> dict[str, Any]:
    interpretable = [
        item for item in chain_items if item["diagnostic_class"] == "interpretable"
    ]
    best_deltas = [
        item["best_shell_delta_mae_mev"]
        for item in interpretable
        if item["best_shell_delta_mae_mev"] is not None
    ]
    if len(best_deltas) < 5:
        verdict = "TOO_SPARSE_TO_INTERPRET"
    else:
        improved = sum(1 for value in best_deltas if value < 0.0)
        regressed = sum(1 for value in best_deltas if value > 0.0)
        improvement_rate = improved / len(best_deltas)
        regression_rate = regressed / len(best_deltas)
        if improvement_rate >= 0.67 and regression_rate <= 0.25:
            verdict = "CHAIN_TRANSFERABLE_BUT_BOUNDED"
        elif improved > 0 and regressed > 0:
            verdict = "MIXED_CHAIN_LOCAL"
        elif improved > 0:
            verdict = "CHAIN_LOCAL_SPARSE_SUPPORT"
        else:
            verdict = "NO_CHAIN_TRANSFER_SUPPORT"
    return {
        "verdict": verdict,
        "interpretable_chain_count": len(best_deltas),
        "too_sparse_chain_count": len(chain_items) - len(interpretable),
        "best_shell_improved_chain_count": sum(1 for value in best_deltas if value < 0.0),
        "best_shell_regressed_chain_count": sum(1 for value in best_deltas if value > 0.0),
        "interpretation": (
            "Shell-axis behavior transfers unevenly by isotope chain; chain-level "
            "regressions remain visible and block broad support wording."
            if verdict == "MIXED_CHAIN_LOCAL"
            else "Shell-axis chain transfer remains bounded and sandbox-only."
        ),
        "claim_promotion_allowed": False,
    }


def evaluate_chain_transfer() -> dict[str, Any]:
    """Evaluate shell-axis and non-shell controls across isotope chains."""
    coefficients = full_known.load_frozen_baseline_coefficients()
    rows, training_rows, training_residuals, baseline_bundle = full_known.build_audit_surface(
        coefficients
    )
    baseline_residuals = [float(row["baseline_residual_mev"]) for row in rows]
    chain_index = _group_chains(rows)
    candidate_by_id = {
        str(candidate["candidate_id"]): candidate
        for candidate in full_known.EXECUTED_CANDIDATES
    }
    control_by_id = {
        str(control["candidate_id"]): control
        for control in specificity.NON_SHELL_CONTROLS
    }
    shell_residuals_by_id: dict[str, list[float]] = {}
    shell_coefficients: dict[str, dict[str, float]] = {}
    for candidate_id in SHELL_CANDIDATE_IDS:
        residuals, fitted = _shell_residuals(
            candidate_by_id[candidate_id],
            rows=rows,
            training_rows=training_rows,
            training_residuals=training_residuals,
        )
        shell_residuals_by_id[candidate_id] = residuals
        shell_coefficients[candidate_id] = fitted

    control_residuals_by_id: dict[str, list[float]] = {}
    control_coefficients: dict[str, dict[str, float]] = {}
    for control_id in NON_SHELL_CONTROL_IDS:
        residuals, fitted = _control_residuals(
            control_by_id[control_id],
            rows=rows,
            training_rows=training_rows,
            training_residuals=training_residuals,
        )
        control_residuals_by_id[control_id] = residuals
        control_coefficients[control_id] = fitted

    chain_items = [
        _chain_summary(
            rows=rows,
            baseline_residuals=baseline_residuals,
            shell_residuals_by_id=shell_residuals_by_id,
            control_residuals_by_id=control_residuals_by_id,
            chain_id=chain_id,
            indices=indices,
        )
        for chain_id, indices in chain_index.items()
    ]
    return {
        "coefficients": coefficients,
        "baseline_bundle": baseline_bundle,
        "chain_index": chain_index,
        "chain_items": chain_items,
        "shell_coefficients": shell_coefficients,
        "control_coefficients": control_coefficients,
    }


def build_metrics() -> dict[str, Any]:
    """Build deterministic isotope-chain transfer metrics."""
    evaluated = evaluate_chain_transfer()
    chain_items = evaluated["chain_items"]
    transfer = _overall_transfer_verdict(chain_items)
    coefficients = evaluated["coefficients"]
    baseline_bundle = evaluated["baseline_bundle"]
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "shell_axis_isotope_chain_transfer_audit",
        "sandbox_only": True,
        "evidence_class": "retrospective_full_known_isotope_chain_transfer_audit",
        "live_external_fetch_allowed": False,
        "summary": {
            "chain_count": len(chain_items),
            "chain_min_rows_for_interpretation": CHAIN_MIN_ROWS,
            "transfer_verdict": transfer["verdict"],
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
        "candidate_fit_coefficients": evaluated["shell_coefficients"],
        "non_shell_control_fit_coefficients": evaluated["control_coefficients"],
        "transfer_summary": transfer,
        "candidate_transfer_summary": _candidate_transfer_summary(chain_items),
        "chain_items": chain_items,
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
            "Chains with fewer than three committed rows are diagnostic only.",
            "Best non-shell controls reuse TASK-0317 definitions; no new formula family is fit.",
            "Shell-axis and control coefficients are fit on the 11-row NMD-0002 residual slice.",
            "The full-known surface is committed repository data; this is not a future-measurement reveal.",
        ],
    }


def _chain_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| Chain | Rows | A range | Baseline MAE | Best shell delta | Best shell | Best non-shell delta | Best non-shell | Class |",
        "| --- | ---: | ---: | ---: | ---: | --- | ---: | --- | --- |",
    ]
    for item in metrics["chain_items"]:
        lines.append(
            "| `{chain}` | {rows} | {amin}-{amax} | {base:.6f} | {shell} | `{shell_id}` | {control} | `{control_id}` | {klass} |".format(
                chain=item["chain_id"],
                rows=item["row_count"],
                amin=item["A_min"],
                amax=item["A_max"],
                base=float(item["baseline_mae_mev"]),
                shell=_format_delta(item["best_shell_delta_mae_mev"]),
                shell_id=item["best_shell_candidate_id"],
                control=_format_delta(item["best_non_shell_control_delta_mae_mev"]),
                control_id=item["best_non_shell_control_id"],
                klass=item["diagnostic_class"],
            )
        )
    return lines


def _candidate_summary_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| Candidate | Interpretable chains | Improved | Regressed | Improvement rate | Worst regression chain |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for candidate_id, item in metrics["candidate_transfer_summary"].items():
        worst = item["worst_chain_regressions"][0] if item["worst_chain_regressions"] else None
        worst_text = (
            f"`{worst['chain_id']}` {float(worst['delta_mae_mev']):+.6f} MeV"
            if worst is not None
            else "none"
        )
        rate = item["improvement_rate"]
        lines.append(
            "| `{cid}` | {n} | {imp} | {reg} | {rate} | {worst} |".format(
                cid=candidate_id,
                n=item["interpretable_chain_count"],
                imp=item["improved_chain_count"],
                reg=item["regressed_chain_count"],
                rate="n/a" if rate is None else f"{float(rate):.3f}",
                worst=worst_text,
            )
        )
    return lines


def render_report(metrics: dict[str, Any]) -> str:
    """Render the agent-run report."""
    lines = [
        "# Nuclear Shell-Axis Isotope-Chain Transfer Audit",
        "",
        f"**Agent run:** `{metrics['agent_run_id']}`",
        f"**Task:** `{metrics['task_id']}`",
        "**Evidence class:** retrospective full-known isotope-chain transfer audit",
        "**Baseline:** `RESULT-0015::model_fitted_semi_empirical`",
        "**Script:** `scripts/run_nuclear_shell_axis_chain_transfer_audit.py`",
        f"**Metrics:** `agent_runs/{metrics['agent_run_id']}/metrics.json`",
        "",
        "## Scope",
        "",
        "This sandbox audit groups committed full-known rows by isotope chain "
        "using fixed `Z` and asks whether shell-axis improvements transfer "
        "across chains or remain chain-local. It does not score future "
        "measurements or promote claims.",
        "",
        "## Transfer Verdict",
        "",
        f"`{metrics['transfer_summary']['verdict']}`",
        "",
        metrics["transfer_summary"]["interpretation"],
        "",
        "## Candidate Transfer Summary",
        "",
        *_candidate_summary_table(metrics),
        "",
        "## Per-Chain Outcomes",
        "",
        *_chain_table(metrics),
        "",
        "Negative deltas mean lower retrospective MAE than the frozen baseline. "
        "Positive deltas are regressions.",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in metrics["limitations"])
    lines.extend(
        [
            "",
            "## Promotion Boundary",
            "",
            "- Prediction registry files are not edited.",
            "- Canonical `RESULT-*` files are not edited.",
            "- Claims and knowledge files are not edited.",
            "- No future measurement reveal is scored.",
            "",
        ]
    )
    return "\n".join(lines)


def write_agent_run_support_files(metrics: dict[str, Any], run_dir: Path) -> None:
    """Write manifest and companion review files for AGENT-RUN-0023."""
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
                    "notes": "TASK-0323 requests isotope-chain transfer diagnostics, not reveal scoring.",
                },
                {
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": "Only committed repository datasets are used; no live external fetch is performed.",
                },
                {
                    "name": "control_boundary",
                    "status": "PASS",
                    "notes": "Best non-shell control deltas reuse committed TASK-0317 control definitions.",
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
        "# AGENT-RUN-0023 Preflight",
        "",
        "**Task:** TASK-0323",
        "**Lane:** nuclear shell-axis isotope-chain transfer audit",
        "**Mode:** sandbox-only retrospective audit",
        "",
        "## Inputs Checked",
        "",
        "- `TASK-0323`",
        "- `agent_runs/AGENT-RUN-0018/metrics.json`",
        "- `agent_runs/AGENT-RUN-0020/metrics.json`",
        "- `agent_runs/AGENT-RUN-0021/metrics.json`",
        "- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`",
        "- `data/nuclear_masses/post_ame2020_holdout.yaml`",
        "",
        "## Guardrails",
        "",
        "- Live external fetch: not allowed and not used.",
        "- Prediction registry writes: not allowed and not used.",
        "- Canonical results, claims, and knowledge promotion: not allowed and not used.",
        "- New formula families: not fit.",
        "",
    ]
    (run_dir / "preflight.md").write_text("\n".join(preflight), encoding="utf-8")
    limitations = ["# AGENT-RUN-0023 Limitations", ""]
    limitations.extend(f"- {item}" for item in metrics["limitations"])
    limitations.append("")
    (run_dir / "limitations.md").write_text("\n".join(limitations), encoding="utf-8")
    review = [
        "# AGENT-RUN-0023 Review Summary",
        "",
        "`INCONCLUSIVE` for claim promotion: isotope-chain transfer is a "
        f"`{metrics['transfer_summary']['verdict']}` sandbox diagnostic, not a "
        "canonical result or prediction-registry update.",
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
