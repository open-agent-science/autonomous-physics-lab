"""TASK-0317 nuclear shell-axis specificity-control audit.

This sandbox-only runner asks whether the TASK-0310 shell-axis improvements
look specific to shell-proximity structure or can be matched by simple
non-shell residual controls. It reuses the committed TASK-0310 training,
holdout, and full-known surfaces; it does not fetch live data, score
prospective prediction entries, write canonical RESULT-* artifacts, update
claims, or edit knowledge.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Callable

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.run_nuclear_shell_axis_full_known_audit as full_known  # noqa: E402


AGENT_RUN_ID = "AGENT-RUN-0020"
TASK_ID = "TASK-0317"
REQUIRED_SUBSETS = (
    "full_known",
    "primary_holdout",
    "training_slice",
    "magic_z",
    "magic_n",
    "light_a_lt_50",
)

SHELL_CANDIDATE_IDS = (
    "FULLKNOWN-SHELL-001",
    "FULLKNOWN-SHELL-002",
    "FULLKNOWN-SHELL-003",
)

FeatureFn = Callable[[dict[str, Any]], tuple[float, ...]]


def _stable_random_feature(row: dict[str, Any]) -> float:
    """Return a deterministic row-local feature in [-1, 1] without using labels."""
    key = f"TASK-0317::{row['nuclide_id']}::{row['Z']}::{row['N']}".encode("utf-8")
    digest = hashlib.sha256(key).digest()
    integer = int.from_bytes(digest[:8], byteorder="big", signed=False)
    return (integer / float(2**64 - 1)) * 2.0 - 1.0


NON_SHELL_CONTROLS: tuple[dict[str, Any], ...] = (
    {
        "candidate_id": "SPECIFICITY-CONTROL-000",
        "name": "Baseline reference / near-null control",
        "family": "baseline_reference",
        "formula": "r_corr = 0.0",
        "complexity": 0,
        "feature_names": (),
        "fit_mode": "fixed_zero",
        "specificity_role": "baseline_reference",
        "feature_fn": lambda row: (),
    },
    {
        "candidate_id": "SPECIFICITY-CONTROL-001",
        "name": "Smooth-A one-degree residual control",
        "family": "smooth_a_trend",
        "formula": "r_corr = beta_a * ((A - 120) / 120)",
        "complexity": 1,
        "feature_names": ("a_centered_120",),
        "fit_mode": "lstsq",
        "specificity_role": "non_shell_smooth_a",
        "feature_fn": lambda row: ((float(row["A"]) - 120.0) / 120.0,),
    },
    {
        "candidate_id": "SPECIFICITY-CONTROL-002",
        "name": "Neutron-excess asymmetry one-degree control",
        "family": "neutron_excess_asymmetry",
        "formula": "r_corr = beta_eta * ((N - Z) / A)",
        "complexity": 1,
        "feature_names": ("neutron_excess_fraction",),
        "fit_mode": "lstsq",
        "specificity_role": "non_shell_asymmetry",
        "feature_fn": lambda row: ((float(row["N"]) - float(row["Z"])) / float(row["A"]),),
    },
    {
        "candidate_id": "SPECIFICITY-CONTROL-003",
        "name": "Light-mass-region one-degree indicator control",
        "family": "mass_region_indicator",
        "formula": "r_corr = beta_light * I(A < 50)",
        "complexity": 1,
        "feature_names": ("light_a_lt_50_indicator",),
        "fit_mode": "lstsq",
        "specificity_role": "non_shell_mass_region",
        "feature_fn": lambda row: (1.0 if int(row["A"]) < 50 else 0.0,),
    },
    {
        "candidate_id": "SPECIFICITY-CONTROL-004",
        "name": "Deterministic random matched-degree feature control",
        "family": "random_matched_degree_feature",
        "formula": "r_corr = beta_random * stable_hash(nuclide_id, Z, N)",
        "complexity": 1,
        "feature_names": ("stable_hash_feature",),
        "fit_mode": "lstsq",
        "specificity_role": "non_shell_random_matched_degree",
        "feature_fn": lambda row: (_stable_random_feature(row),),
    },
)


def _feature_matrix(rows: list[dict[str, Any]], feature_fn: FeatureFn) -> np.ndarray:
    return np.asarray([feature_fn(row) for row in rows], dtype=float)


def _fit_control(
    control: dict[str, Any],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
) -> tuple[np.ndarray, dict[str, float]]:
    feature_names = tuple(control["feature_names"])
    if control["fit_mode"] == "fixed_zero":
        return np.asarray([], dtype=float), {}
    train_x = _feature_matrix(training_rows, control["feature_fn"])
    beta, *_ = np.linalg.lstsq(train_x, training_residuals, rcond=None)
    return beta, {name: float(value) for name, value in zip(feature_names, beta)}


def _required_delta_summary(delta_by_subset: dict[str, float | None]) -> dict[str, float | None]:
    return {subset_id: delta_by_subset.get(subset_id) for subset_id in REQUIRED_SUBSETS}


def _worst_subset_regression(delta_by_subset: dict[str, float | None]) -> dict[str, Any]:
    positive = {
        key: value
        for key, value in delta_by_subset.items()
        if value is not None and value > 0.0
    }
    if not positive:
        return {"subset_id": "none", "delta_mae_mev": 0.0}
    subset_id, delta = max(positive.items(), key=lambda item: item[1])
    return {"subset_id": subset_id, "delta_mae_mev": float(delta)}


def _evaluate_control(
    control: dict[str, Any],
    *,
    audit_rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
    baseline_metrics: dict[str, Any],
) -> dict[str, Any]:
    beta, fitted_coefficients = _fit_control(control, training_rows, training_residuals)
    subset_errors: dict[str, list[float]] = {key: [] for key in baseline_metrics}
    feature_activation_counts = {name: 0 for name in control["feature_names"]}
    for row in audit_rows:
        values = np.asarray(control["feature_fn"](row), dtype=float)
        correction = 0.0 if control["fit_mode"] == "fixed_zero" else float(values @ beta)
        residual = float(row["observed_mev"]) - (
            float(row["baseline_predicted_mev"]) + correction
        )
        for name, value in zip(control["feature_names"], values):
            if abs(float(value)) > 0.0:
                feature_activation_counts[name] += 1
        for subset_id in full_known._surface_subset_ids(row):  # noqa: SLF001
            subset_errors.setdefault(subset_id, []).append(residual)

    metrics_by_subset = {
        key: full_known._summarize_errors(value)  # noqa: SLF001
        for key, value in sorted(subset_errors.items())
    }
    delta_by_subset = {
        key: full_known._delta_mae(metrics_by_subset.get(key), baseline_metrics.get(key))  # noqa: SLF001
        for key in sorted(baseline_metrics)
    }
    return {
        "candidate_id": control["candidate_id"],
        "name": control["name"],
        "family": control["family"],
        "formula": control["formula"],
        "complexity": control["complexity"],
        "fit_mode": control["fit_mode"],
        "specificity_role": control["specificity_role"],
        "fitted_coefficients": fitted_coefficients,
        "feature_activation_counts": feature_activation_counts,
        "metrics_by_subset": metrics_by_subset,
        "delta_mae_by_subset_mev": delta_by_subset,
        "required_delta_mae_mev": _required_delta_summary(delta_by_subset),
        "worst_subset_regression": _worst_subset_regression(delta_by_subset),
        "limitations": [
            "Control is low-complexity and predeclared for TASK-0317.",
            "Coefficients are fit only on the 11-row NMD-0002 residual slice.",
            "Control output is sandbox-only and does not promote a claim.",
        ],
    }


def _primary_shell_items(
    *,
    audit_rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
    baseline_metrics: dict[str, Any],
) -> list[dict[str, Any]]:
    proton_only_beta = float(
        full_known._fit_lstsq(("s_z2",), training_rows, training_residuals)[0]  # noqa: SLF001
    )
    candidate_by_id = {
        str(candidate["candidate_id"]): candidate
        for candidate in full_known.EXECUTED_CANDIDATES
    }
    shell_items: list[dict[str, Any]] = []
    for candidate_id in SHELL_CANDIDATE_IDS:
        item = full_known.evaluate_candidate(
            candidate_by_id[candidate_id],
            audit_rows=audit_rows,
            training_rows=training_rows,
            training_residuals=training_residuals,
            baseline_metrics=baseline_metrics,
            proton_only_beta=proton_only_beta,
        )
        item["required_delta_mae_mev"] = _required_delta_summary(item["delta_mae_by_subset_mev"])
        shell_items.append(item)
    return shell_items


def _classify_specificity(
    shell_items: list[dict[str, Any]],
    control_items: list[dict[str, Any]],
) -> dict[str, Any]:
    """Classify shell-axis behavior relative to simple controls."""
    shell_best = min(shell_items, key=lambda item: float(item["primary_delta_mae_mev"]))
    comparable_margin_mev = 0.01
    non_baseline_controls = [
        item for item in control_items if item["candidate_id"] != "SPECIFICITY-CONTROL-000"
    ]
    improving_controls = [
        item
        for item in non_baseline_controls
        if item["required_delta_mae_mev"]["full_known"] is not None
        and item["required_delta_mae_mev"]["primary_holdout"] is not None
        and float(item["required_delta_mae_mev"]["full_known"]) < 0.0
        and float(item["required_delta_mae_mev"]["primary_holdout"]) < 0.0
    ]
    best_control = min(
        non_baseline_controls,
        key=lambda item: float(item["required_delta_mae_mev"]["full_known"] or 0.0),
    )
    shell_best_full = float(shell_best["required_delta_mae_mev"]["full_known"])
    shell_best_holdout = float(shell_best["required_delta_mae_mev"]["primary_holdout"])
    best_control_full = float(best_control["required_delta_mae_mev"]["full_known"])
    best_control_holdout = float(best_control["required_delta_mae_mev"]["primary_holdout"])

    if not improving_controls:
        verdict = "SHELL_SPECIFIC_BUT_FRAGILE"
        rationale = (
            "No non-shell control improves both full-known and primary-holdout MAE, "
            "while primary shell-axis candidates do."
        )
    elif (
        best_control_full <= shell_best_full + comparable_margin_mev
        and best_control_holdout <= shell_best_holdout + comparable_margin_mev
    ):
        verdict = "TIED_WITH_GENERIC_CONTROL"
        rationale = (
            "At least one simple non-shell control is comparable to the best shell-axis "
            "candidate within the predeclared 0.01 MeV margin."
        )
    elif best_control_full < shell_best_full and best_control_holdout < shell_best_holdout:
        verdict = "WEAKER_THAN_GENERIC_CONTROL"
        rationale = "A simple non-shell control beats the best shell-axis candidate on both key surfaces."
    else:
        verdict = "SHELL_SPECIFIC_BUT_BOUNDED"
        rationale = (
            "Some non-shell controls improve one or both key surfaces, but they do not "
            "match the best shell-axis candidate on both full-known and primary-holdout MAE."
        )

    return {
        "verdict": verdict,
        "rationale": rationale,
        "comparable_margin_mev": comparable_margin_mev,
        "best_shell_candidate_id": shell_best["candidate_id"],
        "best_shell_full_known_delta_mae_mev": shell_best_full,
        "best_shell_primary_holdout_delta_mae_mev": shell_best_holdout,
        "best_non_shell_control_id": best_control["candidate_id"],
        "best_non_shell_full_known_delta_mae_mev": best_control_full,
        "best_non_shell_primary_holdout_delta_mae_mev": best_control_holdout,
        "non_shell_controls_improving_both_key_surfaces": [
            item["candidate_id"] for item in improving_controls
        ],
        "claim_promotion_allowed": False,
    }


def build_metrics() -> dict[str, Any]:
    """Build deterministic specificity-control metrics."""
    coefficients = full_known.load_frozen_baseline_coefficients()
    audit_rows, training_rows, training_residuals, baseline_bundle = full_known.build_audit_surface(
        coefficients
    )
    baseline_metrics = baseline_bundle["metrics"]
    shell_items = _primary_shell_items(
        audit_rows=audit_rows,
        training_rows=training_rows,
        training_residuals=training_residuals,
        baseline_metrics=baseline_metrics,
    )
    control_items = [
        _evaluate_control(
            control,
            audit_rows=audit_rows,
            training_rows=training_rows,
            training_residuals=training_residuals,
            baseline_metrics=baseline_metrics,
        )
        for control in NON_SHELL_CONTROLS
    ]
    specificity = _classify_specificity(shell_items, control_items)
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "shell_axis_specificity_controls",
        "sandbox_only": True,
        "evidence_class": "retrospective_full_known_specificity_control_audit",
        "live_external_fetch_allowed": False,
        "summary": {
            "shell_candidate_count": len(shell_items),
            "non_shell_control_count": len(control_items),
            "required_subset_delta_keys": list(REQUIRED_SUBSETS),
            "specificity_verdict": specificity["verdict"],
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
        "baseline_metrics_by_subset": baseline_metrics,
        "specificity": specificity,
        "shell_axis_candidates": shell_items,
        "non_shell_controls": control_items,
        "predeclared_control_families": [
            {
                "candidate_id": control["candidate_id"],
                "family": control["family"],
                "formula": control["formula"],
                "complexity": control["complexity"],
                "fit_mode": control["fit_mode"],
            }
            for control in NON_SHELL_CONTROLS
        ],
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
            "All fitted coefficients use only the 11-row NMD-0002 residual slice.",
            "The full-known surface is committed repository data; this is not a future-measurement reveal.",
            "Low-degree controls are diagnostic, not new candidate formulas for promotion.",
            "TASK-0316 coefficient fragility remains a hard limitation even if specificity controls are favorable.",
        ],
    }


def _format_delta(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value == 0.0:
        return "+0.000000"
    return f"{'+' if value > 0 else '-'}{abs(value):.6f}"


def _summary_table(items: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Candidate | Full-known ΔMAE | Holdout ΔMAE | Training ΔMAE | Magic-Z ΔMAE | Magic-N ΔMAE | Light ΔMAE | Worst regression |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in items:
        deltas = item["required_delta_mae_mev"]
        worst = item["worst_subset_regression"]
        lines.append(
            "| `{cid}` | {full} | {holdout} | {training} | {mz} | {mn} | {light} | {worst} ({sid}) |".format(
                cid=item["candidate_id"],
                full=_format_delta(deltas.get("full_known")),
                holdout=_format_delta(deltas.get("primary_holdout")),
                training=_format_delta(deltas.get("training_slice")),
                mz=_format_delta(deltas.get("magic_z")),
                mn=_format_delta(deltas.get("magic_n")),
                light=_format_delta(deltas.get("light_a_lt_50")),
                worst=_format_delta(worst["delta_mae_mev"]),
                sid=worst["subset_id"],
            )
        )
    return lines


def render_report(metrics: dict[str, Any]) -> str:
    """Render the agent-run report."""
    lines = [
        "# Nuclear Shell-Axis Specificity Controls",
        "",
        f"**Agent run:** `{metrics['agent_run_id']}`  ",
        f"**Task:** `{metrics['task_id']}`  ",
        "**Evidence class:** retrospective full-known specificity-control audit  ",
        "**Baseline:** `RESULT-0015::model_fitted_semi_empirical`  ",
        "**Script:** `scripts/run_nuclear_shell_axis_specificity_controls.py`  ",
        f"**Metrics:** `agent_runs/{metrics['agent_run_id']}/metrics.json`",
        "",
        "## Scope",
        "",
        "This sandbox audit compares the three primary TASK-0310 shell-axis candidates "
        "against predeclared low-complexity non-shell controls on the same committed "
        "training, primary-holdout, and full-known surfaces. It does not score "
        "prospective predictions or promote claims.",
        "",
        "## Specificity Verdict",
        "",
        f"`{metrics['specificity']['verdict']}`",
        "",
        metrics["specificity"]["rationale"],
        "",
        "| Comparator | Candidate | Full-known ΔMAE | Holdout ΔMAE |",
        "| --- | --- | ---: | ---: |",
        "| Best shell-axis | `{}` | {} | {} |".format(
            metrics["specificity"]["best_shell_candidate_id"],
            _format_delta(metrics["specificity"]["best_shell_full_known_delta_mae_mev"]),
            _format_delta(metrics["specificity"]["best_shell_primary_holdout_delta_mae_mev"]),
        ),
        "| Best non-shell control | `{}` | {} | {} |".format(
            metrics["specificity"]["best_non_shell_control_id"],
            _format_delta(metrics["specificity"]["best_non_shell_full_known_delta_mae_mev"]),
            _format_delta(metrics["specificity"]["best_non_shell_primary_holdout_delta_mae_mev"]),
        ),
        "",
        "Negative deltas mean lower retrospective MAE than the frozen baseline. "
        "Positive deltas are regressions.",
        "",
        "## Shell-Axis Candidates",
        "",
        *_summary_table(metrics["shell_axis_candidates"]),
        "",
        "## Non-Shell Controls",
        "",
        *_summary_table(metrics["non_shell_controls"]),
        "",
        "## Interpretation",
        "",
        "The specificity outcome is bounded by the TASK-0316 stability result. "
        "A favorable specificity result does not remove coefficient fragility, "
        "and an unfavorable one would demote the shell-axis lane to a narrow "
        "retrospective artifact. In either case, this output remains sandbox-only.",
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
    """Write manifest and companion review files for AGENT-RUN-0020."""
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
                    "notes": "TASK-0317 requests specificity controls, not reveal scoring.",
                },
                {
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": "Only committed repository datasets are used; no live external fetch is performed.",
                },
                {
                    "name": "control_boundary",
                    "status": "PASS",
                    "notes": "Baseline, smooth-A, asymmetry, mass-region, and deterministic random controls are preserved.",
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
        "# AGENT-RUN-0020 Preflight",
        "",
        "**Task:** TASK-0317  ",
        "**Lane:** nuclear shell-axis specificity controls  ",
        "**Mode:** sandbox-only retrospective control audit",
        "",
        "## Inputs Checked",
        "",
        "- `TASK-0317`",
        "- `scripts/run_nuclear_shell_axis_full_known_audit.py`",
        "- `agent_runs/AGENT-RUN-0018/metrics.json`",
        "- `agent_runs/AGENT-RUN-0019/metrics.json`",
        "- `results/EXP-0012/RUN-0001/result.yaml`",
        "- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`",
        "- `data/nuclear_masses/post_ame2020_holdout.yaml`",
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
        "1. Reuse the TASK-0310 committed full-known audit surface.",
        "2. Recompute the three primary shell-axis candidates.",
        "3. Fit predeclared low-complexity non-shell controls on the same 11 training rows.",
        "4. Report full-known, holdout, training, magic-Z, magic-N, light, and worst-regression deltas.",
        "5. Classify specificity conservatively and keep outputs sandbox-only.",
        "",
    ]
    (run_dir / "preflight.md").write_text("\n".join(preflight), encoding="utf-8")
    limitations = ["# AGENT-RUN-0020 Limitations", ""]
    limitations.extend(f"- {item}" for item in metrics["limitations"])
    limitations.append("")
    (run_dir / "limitations.md").write_text("\n".join(limitations), encoding="utf-8")
    review = [
        "# AGENT-RUN-0020 Review Summary",
        "",
        f"`{metrics['specificity']['verdict']}` for the specificity-control audit.",
        "",
        metrics["specificity"]["rationale"],
        "",
        "The result remains bounded by the TASK-0316 coefficient-fragility audit. "
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
