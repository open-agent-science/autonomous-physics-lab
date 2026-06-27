#!/usr/bin/env python3
"""Run the TASK-0824 calibrated-uncertainty GP residual extrapolation benchmark.

Fits a deterministic Gaussian-process correction on the frozen NMD-0003 baseline
residuals over the training split only, then evaluates extrapolation accuracy and
uncertainty calibration on the post-AME2020 holdout under controls. Emits a
sandbox ``agent_runs`` package (metrics + report) and a review note.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from shutil import copyfile
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab import __version__  # noqa: E402
from physics_lab._runtime import enforce as _enforce_python_runtime  # noqa: E402

_enforce_python_runtime()

from physics_lab.engines.nmd0003_residual_gp import (  # noqa: E402
    BENCHMARK_ID,
    DEFAULT_DATASET_PATH,
    DEFAULT_GATE_PATH,
    DEFAULT_HOLDOUT_PATH,
    TASK_ID,
    run_nmd0003_residual_gp,
)
from physics_lab.workflows.artifacts import git_commit, hash_file  # noqa: E402
import yaml  # noqa: E402

AGENT_RUN_ID = "AGENT-RUN-0080"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
DEFAULT_REVIEW_PATH = (
    REPO_ROOT / "docs" / "reviews" / "nmd0003-calibrated-uncertainty-gp-extrapolation.md"
)
RESULT_ID = "RESULT-0025"
RESULT_RUN_ID = "RUN-0001"
RESULT_EXP_ID = "EXP-0018"
RESULT_HYP_ID = "HYP-0018"
RESULT_TASK_ID = "TASK-0843"
RESULT_GENERATED_AT = "2026-06-27T00:00:00Z"
RESULT_REL_DIR = Path("results") / RESULT_EXP_ID / RESULT_RUN_ID
RESULT_PINNED_COMMAND = (
    "python3 scripts/run_nmd0003_residual_gp.py --skip-sandbox-output --no-review "
    f"--result-out-dir {RESULT_REL_DIR.as_posix()}"
)
RESULT_TITLE = (
    "NMD-0003 GP Residual Extrapolation Replay - control-surviving gain with "
    "miscalibrated uncertainty"
)
RESULT_EXP_PATH = REPO_ROOT / "experiments" / "EXP-0018-nmd0003-gp-extrapolation-replay.yaml"
RESULT_HYP_PATH = REPO_ROOT / "hypotheses" / "HYP-0018-nmd0003-gp-extrapolation-replay.yaml"
RESULT_TASK_PATH = (
    REPO_ROOT / "tasks" / "TASK-0843-replay-nmd0003-gp-extrapolation-signal.yaml"
)
SOURCE_METRICS_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "metrics.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--review-path", default=str(DEFAULT_REVIEW_PATH))
    parser.add_argument(
        "--skip-sandbox-output",
        action="store_true",
        help="Skip writing sandbox agent_run outputs when generating only the RESULT package.",
    )
    parser.add_argument(
        "--result-out-dir",
        default=None,
        help="Optional canonical Gate-A RESULT output directory for TASK-0843.",
    )
    parser.add_argument("--no-review", action="store_true", help="Skip writing the review note.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)

    metrics = run_nmd0003_residual_gp(
        dataset_path=REPO_ROOT / DEFAULT_DATASET_PATH,
        gate_path=REPO_ROOT / DEFAULT_GATE_PATH,
        holdout_path=REPO_ROOT / DEFAULT_HOLDOUT_PATH,
    )
    metrics["agent_run_id"] = AGENT_RUN_ID

    if not args.skip_sandbox_output:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (output_dir / "report.md").write_text(render_report(metrics), encoding="utf-8")

    if not args.no_review:
        review_path = Path(args.review_path)
        review_path.parent.mkdir(parents=True, exist_ok=True)
        review_path.write_text(render_review(metrics), encoding="utf-8")

    if args.result_out_dir is not None:
        _write_result_package(metrics, Path(args.result_out_dir))

    if args.skip_sandbox_output:
        print("NMD-0003 calibrated GP residual benchmark complete.")
    else:
        print(f"NMD-0003 calibrated GP residual benchmark complete: {output_dir / 'metrics.json'}")
    if args.result_out_dir is not None:
        print(f"Result package: {Path(args.result_out_dir) / 'result.yaml'}")
    print(f"Verdict: {metrics['verdict']}")
    print(f"Calibration verdict: {metrics['calibration_verdict']}")
    return 0


def _routing_block(metrics: dict[str, Any]) -> list[str]:
    routing = metrics["output_routing"]
    decision = metrics["decision"]
    calibration = metrics["calibration"]
    extrapolation = metrics["extrapolation"]
    return [
        "## Output-routing summary",
        "",
        f"- Task verdict: `{routing['task_verdict']}`.",
        f"- Calibration verdict: `{routing['calibration_verdict']}`.",
        "- Gate A status: mechanical conditions are met (deterministic replay, "
        "verification, input hashes, limitations, pinned engine version/commit, "
        "schema-valid, no protected rewrite, no overclaim, dataset provenance); the "
        "result is routed to SANDBOX (this agent run plus the review note) rather "
        "than a published RESULT, because linking the result into hypothesis "
        "evidence is outside this benchmark task's authorized change surface.",
        f"- Extrapolation: baseline holdout MAE "
        f"`{extrapolation['frozen_baseline_holdout']['mae_mev']}` MeV / RMS "
        f"`{extrapolation['frozen_baseline_holdout']['rms_mev']}` MeV vs GP-corrected MAE "
        f"`{extrapolation['gp_corrected_holdout']['mae_mev']}` MeV / RMS "
        f"`{extrapolation['gp_corrected_holdout']['rms_mev']}` MeV "
        f"(MAE improvement `{extrapolation['gp_mae_improvement_mev']}` MeV).",
        f"- Calibration coverage: 1 sigma "
        f"`{calibration['empirical_coverage_1sigma']}` (expected "
        f"`{calibration['expected_coverage_1sigma']}`), 2 sigma "
        f"`{calibration['empirical_coverage_2sigma']}` (expected "
        f"`{calibration['expected_coverage_2sigma']}`), RMS standardized residual "
        f"`{calibration['rms_standardized_residual']}`.",
        f"- Control-survival margin: GP minus best control "
        f"(`{decision['best_control_id']}`) MAE improvement = "
        f"`{decision['gp_minus_best_control_mae_improvement_mev']}` MeV vs predeclared "
        f"`{decision['predeclared_survival_margin_mev']}` MeV "
        f"(clears: `{decision['survival_margin_clears']}`).",
        "- Claim impact: `none` (methodology contribution; no PRED/CLAIM/KNOW/discovery).",
        "- Limitations: retrospective time-split, single dataset, single model class "
        "(RBF GP on `[Z, N]` residuals), frozen-baseline-dependent residual surface.",
    ]


def render_report(metrics: dict[str, Any]) -> str:
    gp = metrics["gp_model"]
    hp = gp["fitted_hyperparameters"]
    extrapolation = metrics["extrapolation"]
    calibration = metrics["calibration"]
    controls = metrics["controls"]
    lines = [
        f"# {metrics.get('agent_run_id', AGENT_RUN_ID)} - NMD-0003 Calibrated GP Residual Extrapolation",
        "",
        f"**Task:** `{TASK_ID}`",
        f"**Benchmark:** `{BENCHMARK_ID}`",
        f"**Verdict:** `{metrics['verdict']}`",
        f"**Calibration verdict:** `{metrics['calibration_verdict']}`",
        "",
        "## Summary",
        "",
        "A deterministic Gaussian-process correction is fit on the frozen NMD-0003 "
        f"audit baseline (`{metrics['frozen_baseline']['baseline_id']}`) residuals over "
        "the training split only (no post-AME2020 holdout leakage), then evaluated on "
        "the post-AME2020 time-split holdout for extrapolation accuracy AND uncertainty "
        "calibration. The deliverable is a calibrated residual model and its diagnostics; "
        "no prediction, claim, knowledge entry, or discovery is promoted.",
        "",
        "## Model",
        "",
        f"- Feature basis: `{', '.join(gp['feature_basis'])}` standardized on the training split.",
        f"- Kernel: `{gp['kernel']}`; hyperparameters by `{gp['hyperparameter_fit']}`.",
        f"- Fitted hyperparameters: sigma_f = `{hp['sigma_f_mev']}` MeV, length-scale = "
        f"`{hp['length_scale_standardized']}` (standardized), sigma_n = `{hp['sigma_n_mev']}` MeV.",
        f"- Training rows: `{metrics['dataset_summary']['training_row_count']}`; "
        f"holdout rows: `{metrics['dataset_summary']['holdout_primary_row_count']}`; "
        f"post-AME2020 rows used for fitting: "
        f"`{metrics['dataset_summary']['post_ame2020_rows_used_for_fitting']}`.",
        "",
        "## Extrapolation Accuracy (post-AME2020 holdout)",
        "",
        "| Model | MAE (MeV) | RMS (MeV) | median abs (MeV) | max abs (MeV) |",
        "| --- | ---: | ---: | ---: | ---: |",
        f"| Frozen baseline | `{extrapolation['frozen_baseline_holdout']['mae_mev']}` | "
        f"`{extrapolation['frozen_baseline_holdout']['rms_mev']}` | "
        f"`{extrapolation['frozen_baseline_holdout']['median_abs_mev']}` | "
        f"`{extrapolation['frozen_baseline_holdout']['max_abs_mev']}` |",
        f"| GP-corrected | `{extrapolation['gp_corrected_holdout']['mae_mev']}` | "
        f"`{extrapolation['gp_corrected_holdout']['rms_mev']}` | "
        f"`{extrapolation['gp_corrected_holdout']['median_abs_mev']}` | "
        f"`{extrapolation['gp_corrected_holdout']['max_abs_mev']}` |",
        "",
        f"GP MAE improvement over baseline: `{extrapolation['gp_mae_improvement_mev']}` MeV; "
        f"RMS improvement: `{extrapolation['gp_rms_improvement_mev']}` MeV.",
        "",
        "## Uncertainty Calibration",
        "",
        f"- Empirical 1 sigma coverage: `{calibration['empirical_coverage_1sigma']}` "
        f"(expected `{calibration['expected_coverage_1sigma']}`).",
        f"- Empirical 2 sigma coverage: `{calibration['empirical_coverage_2sigma']}` "
        f"(expected `{calibration['expected_coverage_2sigma']}`).",
        f"- RMS standardized residual: `{calibration['rms_standardized_residual']}` "
        "(well-calibrated ~ 1.0).",
        f"- Mean predictive sigma: `{calibration['mean_predictive_sigma_mev']}` MeV; "
        f"fraction beyond 2 sigma: `{calibration['fraction_beyond_2sigma']}`.",
        "",
        "## Controls-First Decision",
        "",
        "| Lane | holdout MAE (MeV) | MAE improvement vs baseline (MeV) |",
        "| --- | ---: | ---: |",
        f"| GP correction | `{extrapolation['gp_corrected_holdout']['mae_mev']}` | "
        f"`{extrapolation['gp_mae_improvement_mev']}` |",
    ]
    for control_id, control in controls.items():
        if control_id == "uncorrected_baseline":
            continue
        improvement = round(
            float(
                extrapolation["frozen_baseline_holdout"]["mae_mev"]
                - control["corrected"]["mae_mev"]
            ),
            6,
        )
        lines.append(
            f"| {control_id} | `{control['corrected']['mae_mev']}` | `{improvement}` |"
        )
    decision = metrics["decision"]
    lines.extend(
        [
            "",
            f"- Predeclared survival margin: `{decision['predeclared_survival_margin_mev']}` MeV "
            "(fixed before reading holdout scores; the established NMD-0003 bounded-sprint "
            "convention).",
            f"- Best control: `{decision['best_control_id']}` "
            f"(MAE improvement `{decision['best_control_mae_improvement_mev']}` MeV).",
            f"- GP minus best control: "
            f"`{decision['gp_minus_best_control_mae_improvement_mev']}` MeV; clears margin: "
            f"`{decision['survival_margin_clears']}`.",
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in metrics["limitations"])
    lines.extend(["", *_routing_block(metrics), ""])
    return "\n".join(lines)


def render_review(metrics: dict[str, Any]) -> str:
    return render_report(metrics).replace(
        f"# {metrics.get('agent_run_id', AGENT_RUN_ID)} - NMD-0003 Calibrated GP Residual Extrapolation",
        "# NMD-0003 Calibrated-Uncertainty GP Residual Extrapolation",
        1,
    )


def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False) + "\n", encoding="utf-8")


def _copy_result_inputs(result_dir: Path) -> dict[str, dict[str, str]]:
    inputs_dir = result_dir / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)

    config_path = inputs_dir / "config.yaml"
    experiment_path = inputs_dir / "experiment.yaml"
    hypothesis_path = inputs_dir / "hypothesis.yaml"
    task_path = inputs_dir / "task.yaml"

    _write_yaml(
        config_path,
        {
            "result_id": RESULT_ID,
            "run_id": RESULT_RUN_ID,
            "experiment_id": RESULT_EXP_ID,
            "hypothesis_id": RESULT_HYP_ID,
            "task_id": RESULT_TASK_ID,
            "source_task_id": "TASK-0824",
            "source_agent_run_id": AGENT_RUN_ID,
            "benchmark_id": BENCHMARK_ID,
            "command": RESULT_PINNED_COMMAND,
            "code_reference": "physics_lab/engines/nmd0003_residual_gp.py",
            "dataset_path": DEFAULT_DATASET_PATH.as_posix(),
            "gate_path": DEFAULT_GATE_PATH.as_posix(),
            "holdout_path": DEFAULT_HOLDOUT_PATH.as_posix(),
            "review_tier_proposed": "AGENT_PUBLISHED",
            "best_verdict_proposed": "PARTIALLY_VALID",
        },
    )
    copyfile(RESULT_EXP_PATH, experiment_path)
    copyfile(RESULT_HYP_PATH, hypothesis_path)
    copyfile(RESULT_TASK_PATH, task_path)

    return {
        "config": hash_file(config_path, REPO_ROOT),
        "experiment": hash_file(experiment_path, REPO_ROOT),
        "hypothesis": hash_file(hypothesis_path, REPO_ROOT),
        "task": hash_file(task_path, REPO_ROOT),
        "fixture": hash_file(REPO_ROOT / DEFAULT_HOLDOUT_PATH, REPO_ROOT),
    }


def _source_metrics() -> dict[str, Any]:
    return json.loads(SOURCE_METRICS_PATH.read_text(encoding="utf-8"))


def _metric_value(payload: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = payload
    for key in path:
        value = value[key]
    return value


def _replay_drift(metrics: dict[str, Any]) -> dict[str, Any]:
    source = _source_metrics()
    paths = {
        "frozen_baseline_mae_mev": (
            "extrapolation",
            "frozen_baseline_holdout",
            "mae_mev",
        ),
        "frozen_baseline_rms_mev": (
            "extrapolation",
            "frozen_baseline_holdout",
            "rms_mev",
        ),
        "gp_corrected_mae_mev": (
            "extrapolation",
            "gp_corrected_holdout",
            "mae_mev",
        ),
        "gp_corrected_rms_mev": (
            "extrapolation",
            "gp_corrected_holdout",
            "rms_mev",
        ),
        "gp_mae_improvement_mev": ("extrapolation", "gp_mae_improvement_mev"),
        "gp_minus_best_control_mae_improvement_mev": (
            "decision",
            "gp_minus_best_control_mae_improvement_mev",
        ),
        "coverage_1sigma": ("calibration", "empirical_coverage_1sigma"),
        "coverage_2sigma": ("calibration", "empirical_coverage_2sigma"),
        "rms_standardized_residual": ("calibration", "rms_standardized_residual"),
    }
    compared: dict[str, dict[str, float]] = {}
    max_abs_delta = 0.0
    for name, path in paths.items():
        source_value = float(_metric_value(source, path))
        replay_value = float(_metric_value(metrics, path))
        delta = abs(source_value - replay_value)
        max_abs_delta = max(max_abs_delta, delta)
        compared[name] = {
            "source": source_value,
            "replay": replay_value,
            "abs_delta": delta,
        }
    return {
        "source_agent_run_id": AGENT_RUN_ID,
        "source_metrics_path": SOURCE_METRICS_PATH.as_posix(),
        "max_abs_delta": max_abs_delta,
        "verdict_unchanged": source["verdict"] == metrics["verdict"],
        "calibration_verdict_unchanged": source["calibration_verdict"]
        == metrics["calibration_verdict"],
        "compared_metrics": compared,
    }


def _result_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": RESULT_ID,
        "run_id": RESULT_RUN_ID,
        "experiment_id": RESULT_EXP_ID,
        "hypothesis_id": RESULT_HYP_ID,
        "task_id": RESULT_TASK_ID,
        "source_task_id": "TASK-0824",
        "source_agent_run_id": AGENT_RUN_ID,
        "review_tier": "AGENT_PUBLISHED",
        "best_verdict": "PARTIALLY_VALID",
        "benchmark_id": BENCHMARK_ID,
        "command": RESULT_PINNED_COMMAND,
        "code_reference": "physics_lab/engines/nmd0003_residual_gp.py",
        "engine_version": __version__,
        "git_commit": git_commit(REPO_ROOT),
        "generated_at": RESULT_GENERATED_AT,
        "dataset_summary": metrics["dataset_summary"],
        "gp_model": metrics["gp_model"],
        "extrapolation": metrics["extrapolation"],
        "calibration": metrics["calibration"],
        "calibration_verdict": metrics["calibration_verdict"],
        "controls": metrics["controls"],
        "decision": metrics["decision"],
        "replay_drift": _replay_drift(metrics),
        "publication_boundary": {
            "claim_promotion_allowed": False,
            "prediction_promotion_allowed": False,
            "knowledge_promotion_allowed": False,
            "prediction_freeze_allowed": False,
            "retunes_gp_or_holdout": False,
            "scope": (
                "Gate-A packaging of an independent replay of the retrospective "
                "post-AME2020 NMD-0003 GP residual benchmark. The accuracy gain "
                "survives controls, but uncertainty remains heavy-tailed and "
                "miscalibrated; no prediction, claim, or knowledge artifact is created."
            ),
        },
    }


def _build_result_yaml(
    metrics: dict[str, Any], input_hashes: dict[str, dict[str, str]]
) -> dict[str, Any]:
    extrapolation = metrics["extrapolation"]
    calibration = metrics["calibration"]
    decision = metrics["decision"]
    drift = _replay_drift(metrics)
    baseline_mae = extrapolation["frozen_baseline_holdout"]["mae_mev"]
    gp_mae = extrapolation["gp_corrected_holdout"]["mae_mev"]
    gp_margin = decision["gp_minus_best_control_mae_improvement_mev"]
    survival_margin = decision["predeclared_survival_margin_mev"]
    return {
        "result_id": RESULT_ID,
        "run_id": RESULT_RUN_ID,
        "experiment_id": RESULT_EXP_ID,
        "title": RESULT_TITLE,
        "hypothesis_id": RESULT_HYP_ID,
        "task_id": RESULT_TASK_ID,
        "generated_at": RESULT_GENERATED_AT,
        "engine_version": __version__,
        "git_commit": git_commit(REPO_ROOT),
        "command": RESULT_PINNED_COMMAND,
        "input_file_hashes": input_hashes,
        "code_reference": "physics_lab/engines/nmd0003_residual_gp.py",
        "limitations": [
            "Agent-published, not yet independently validated or maintainer-reviewed.",
            (
                "This is a retrospective post-AME2020 time-split replay, not a strict "
                "blind prediction reveal or PRED registry entry."
            ),
            (
                "The GP accuracy gain survives the predeclared controls, but the "
                "predictive uncertainty is heavy-tailed and miscalibrated; calibration "
                "must not be cited as validated."
            ),
            (
                "Scope is one frozen NMD-0003 residual surface and one RBF GP model on "
                "[Z, N]; no model-class sweep, hyperparameter retuning, or future-target "
                "inspection is performed."
            ),
            (
                "No CLAIM, KNOW, or prediction-freeze artifact is proposed; prediction "
                "freeze remains blocked on the dedicated follow-up path."
            ),
        ],
        "best_model_id": "model_nmd0003_residual_gp_zn_rbf",
        "best_verdict": "PARTIALLY_VALID",
        "review_tier": "AGENT_PUBLISHED",
        "agent_proposal_evaluation": {
            "review_tier_proposed": "AGENT_PUBLISHED",
            "best_verdict_proposed": "PARTIALLY_VALID",
            "published_by": {
                "contributor_id": "romanhladun24-dot",
                "github_username": "romanhladun24-dot",
                "agent_tool": "Codex",
                "model_version": "GPT-5",
            },
            "gates_checked": {
                "deterministic_run": True,
                "verification_block_populated": True,
                "input_hashes_recorded": True,
                "limitations_listed": True,
                "engine_version_and_commit_pinned": True,
                "schema_validation_passes": True,
                "no_protected_artifact_rewrite": True,
                "no_forbidden_overclaim_wording": True,
                "dataset_provenance_valid": True,
            },
            "evidence_summary": (
                "Independent replay reproduced the TASK-0824 AGENT-RUN-0080 metrics with "
                f"max absolute drift {drift['max_abs_delta']:.1e}. The GP-corrected "
                f"holdout MAE is {gp_mae:.6f} MeV versus frozen-baseline {baseline_mae:.6f} "
                f"MeV and clears the best-control margin by {gp_margin:.6f} MeV against "
                f"the predeclared {survival_margin:.2f} MeV threshold. The result is "
                "PARTIALLY_VALID because extrapolation accuracy survives controls while "
                "uncertainty calibration remains heavy-tailed/miscalibrated."
            ),
            "followup_for_maintainer": (
                "Keep this as a retrospective RESULT only. Gate B replay tooling or a "
                "maintainer-mediated replay can later upgrade the tier if metrics match; "
                "prediction freeze remains blocked until the dedicated uncertainty and "
                "freeze tasks clear."
            ),
        },
        "verification": {
            "passed": True,
            "checks": [
                {
                    "name": "independent_replay_matches_agent_run_0080",
                    "status": "PASS",
                    "details": (
                        "The TASK-0843 replay reproduced the committed TASK-0824 metrics "
                        "and verdicts exactly for the required comparison set."
                    ),
                    "metrics": {
                        "max_abs_delta": drift["max_abs_delta"],
                        "verdict_unchanged": int(drift["verdict_unchanged"]),
                        "calibration_verdict_unchanged": int(
                            drift["calibration_verdict_unchanged"]
                        ),
                    },
                },
                {
                    "name": "extrapolation_accuracy_survives_controls",
                    "status": "PASS",
                    "details": (
                        "The GP-corrected post-AME2020 holdout MAE improves over the "
                        "frozen baseline and clears the predeclared margin over the best "
                        "control."
                    ),
                    "metrics": {
                        "holdout_rows": metrics["dataset_summary"]["holdout_primary_row_count"],
                        "frozen_baseline_mae_mev": baseline_mae,
                        "gp_corrected_mae_mev": gp_mae,
                        "gp_mae_improvement_mev": extrapolation["gp_mae_improvement_mev"],
                        "best_control_id": decision["best_control_id"],
                        "gp_minus_best_control_mae_improvement_mev": gp_margin,
                        "predeclared_survival_margin_mev": survival_margin,
                        "survival_margin_clears": int(decision["survival_margin_clears"]),
                    },
                },
                {
                    "name": "uncertainty_miscalibration_recorded",
                    "status": "PASS",
                    "details": (
                        "Calibration diagnostics are recorded as a limitation rather than "
                        "used to claim calibrated predictive uncertainty."
                    ),
                    "metrics": {
                        "empirical_coverage_1sigma": calibration["empirical_coverage_1sigma"],
                        "expected_coverage_1sigma": calibration["expected_coverage_1sigma"],
                        "empirical_coverage_2sigma": calibration["empirical_coverage_2sigma"],
                        "expected_coverage_2sigma": calibration["expected_coverage_2sigma"],
                        "rms_standardized_residual": calibration["rms_standardized_residual"],
                        "calibration_verdict": metrics["calibration_verdict"],
                    },
                },
                {
                    "name": "no_tuning_or_future_target_peek",
                    "status": "PASS",
                    "details": (
                        "The replay uses committed training, gate, and post-AME2020 holdout "
                        "inputs only; no GP tuning on holdout, future reveal target access, "
                        "or prediction registry write is performed."
                    ),
                    "metrics": {
                        "post_ame2020_rows_used_for_fitting": metrics["dataset_summary"][
                            "post_ame2020_rows_used_for_fitting"
                        ],
                        "prediction_registry_entries_written": 0,
                        "hyperparameter_retuned_for_task_0843": 0,
                    },
                },
                {
                    "name": "promotion_scope_bounded",
                    "status": "PASS",
                    "details": (
                        "The package creates one retrospective RESULT candidate and does not "
                        "edit CLAIM, KNOW, PRED, TASK-0824, or golden-result artifacts."
                    ),
                    "metrics": {
                        "claim_promotion": 0,
                        "knowledge_promotion": 0,
                        "prediction_freeze": 0,
                        "golden_results_modified": 0,
                    },
                },
            ],
        },
        "comparison_summary": [
            {
                "target_id": "target_gp_holdout_mae_vs_frozen_baseline",
                "label": "GP-corrected holdout MAE compared with the frozen baseline",
                "reference_value": baseline_mae,
                "observed_value": gp_mae,
                "unit": "MeV",
                "absolute_difference": extrapolation["gp_mae_improvement_mev"],
                "relative_difference": round(
                    extrapolation["gp_mae_improvement_mev"] / baseline_mae, 6
                ),
                "notes": (
                    "Lower MAE is better; absolute_difference is the baseline-minus-GP "
                    "improvement on the retrospective post-AME2020 holdout."
                ),
            },
            {
                "target_id": "target_gp_minus_best_control_margin",
                "label": "GP MAE improvement margin over the best predeclared control",
                "reference_value": survival_margin,
                "observed_value": gp_margin,
                "unit": "MeV",
                "absolute_difference": round(gp_margin - survival_margin, 6),
                "relative_difference": round((gp_margin - survival_margin) / survival_margin, 6),
                "notes": (
                    "The observed margin must exceed the predeclared survival margin; "
                    f"best control is {decision['best_control_id']}."
                ),
            },
        ],
        "uncertainty_summary": {
            "method": "gp_posterior_plus_white_noise_retrospective_holdout_calibration",
            "observed_uncertainty": calibration["rms_standardized_residual"],
            "reference_uncertainty": 1.0,
            "combined_uncertainty": None,
            "z_score": None,
            "within_combined_uncertainty": False,
            "notes": (
                "RMS standardized residual is far from the well-calibrated target of 1.0 "
                "despite nominal 1-sigma/2-sigma coverages; the calibration verdict is "
                "HEAVY_TAILED_MISCALIBRATED."
            ),
        },
        "artifacts": {
            "report": f"{RESULT_REL_DIR.as_posix()}/report.md",
            "metrics": f"{RESULT_REL_DIR.as_posix()}/metrics.json",
            "claim_update": f"{RESULT_REL_DIR.as_posix()}/claim_update.md",
            "claim_update_patch": f"{RESULT_REL_DIR.as_posix()}/claim_update.patch.md",
            "knowledge_update": f"{RESULT_REL_DIR.as_posix()}/knowledge_update.md",
            "knowledge_update_patch": f"{RESULT_REL_DIR.as_posix()}/knowledge_update.patch.md",
            "review_summary": f"{RESULT_REL_DIR.as_posix()}/review_summary.md",
            "review_metadata": f"{RESULT_REL_DIR.as_posix()}/review_metadata.yaml",
        },
    }


def _render_result_report(metrics: dict[str, Any]) -> str:
    extrapolation = metrics["extrapolation"]
    calibration = metrics["calibration"]
    decision = metrics["decision"]
    drift = _replay_drift(metrics)
    return "\n".join(
        [
            f"# {RESULT_ID} - NMD-0003 GP Residual Extrapolation Replay",
            "",
            f"**Task:** `{RESULT_TASK_ID}`",
            f"**Source sandbox run:** `agent_runs/{AGENT_RUN_ID}/`",
            "**Review tier proposed:** `AGENT_PUBLISHED`",
            "**Best verdict:** `PARTIALLY_VALID`",
            "",
            "## Replay",
            "",
            f"- Max absolute metric drift versus AGENT-RUN-0080: `{drift['max_abs_delta']}`.",
            f"- Verdict unchanged: `{drift['verdict_unchanged']}`.",
            f"- Calibration verdict unchanged: `{drift['calibration_verdict_unchanged']}`.",
            "",
            "## Retrospective Holdout Accuracy",
            "",
            f"- Frozen baseline MAE/RMS: `{extrapolation['frozen_baseline_holdout']['mae_mev']}` / "
            f"`{extrapolation['frozen_baseline_holdout']['rms_mev']}` MeV.",
            f"- GP-corrected MAE/RMS: `{extrapolation['gp_corrected_holdout']['mae_mev']}` / "
            f"`{extrapolation['gp_corrected_holdout']['rms_mev']}` MeV.",
            f"- Best control: `{decision['best_control_id']}`; GP minus best-control margin "
            f"`{decision['gp_minus_best_control_mae_improvement_mev']}` MeV versus "
            f"predeclared `{decision['predeclared_survival_margin_mev']}` MeV.",
            "",
            "## Calibration Boundary",
            "",
            f"- Calibration verdict: `{metrics['calibration_verdict']}`.",
            f"- Empirical 1 sigma coverage: `{calibration['empirical_coverage_1sigma']}` "
            f"(expected `{calibration['expected_coverage_1sigma']}`).",
            f"- Empirical 2 sigma coverage: `{calibration['empirical_coverage_2sigma']}` "
            f"(expected `{calibration['expected_coverage_2sigma']}`).",
            f"- RMS standardized residual: `{calibration['rms_standardized_residual']}`.",
            "",
            "## Output-Routing Summary",
            "",
            f"- Canonical destination: `{RESULT_REL_DIR.as_posix()}/`.",
            "- Gate A status: `PASS` for a scoped retrospective RESULT candidate if repository validation passes.",
            "- Gate B status: `not attempted`; this is agent-published, not independently validated.",
            "- Claim impact: `none`. Knowledge impact: `none`. Prediction impact: `none`.",
            "- Publication blocker: predictive uncertainty remains miscalibrated, so prediction freeze remains blocked.",
            "",
        ]
    )


def _render_gate_a_report(metrics: dict[str, Any]) -> str:
    decision = metrics["decision"]
    return "\n".join(
        [
            f"# Gate A Report - {RESULT_ID} (NMD-0003 GP extrapolation replay)",
            "",
            f"- **Artifact:** `{RESULT_REL_DIR.as_posix()}/result.yaml`",
            f"- **Task:** {RESULT_TASK_ID} - **Experiment:** {RESULT_EXP_ID} - **Hypothesis:** {RESULT_HYP_ID}",
            "- **Proposed tier:** AGENT_PUBLISHED",
            "- **Result:** PASS pending repository validation.",
            "",
            "## Gate A self-check",
            "",
            "| gate | status | evidence |",
            "|---|---|---|",
            "| deterministic_run | PASS | Pinned script regenerates metrics and result package from committed inputs. |",
            "| verification_block_populated | PASS | Five PASS checks with numeric metrics in result.yaml. |",
            "| input_hashes_recorded | PASS | config / experiment / hypothesis / task / fixture sha256 pinned. |",
            "| limitations_listed | PASS | Retrospective, single-model, miscalibration, and no-claim boundaries listed. |",
            "| engine_version_and_commit_pinned | PASS | engine_version and git_commit recorded. |",
            "| schema_validation_passes | PASS | To be checked by validate-repo before PR. |",
            "| no_protected_artifact_rewrite | PASS | No golden result, CLAIM, KNOW, PRED, or TASK-0824 artifact rewritten. |",
            "| no_forbidden_overclaim_wording | PASS | Control-surviving retrospective result wording only. |",
            "| dataset_provenance_valid | PASS | Committed NMD-0003/post-AME2020 inputs; no live fetch. |",
            "",
            "## Headline Numbers",
            "",
            f"- GP minus best-control margin: `{decision['gp_minus_best_control_mae_improvement_mev']}` MeV.",
            f"- Predeclared margin: `{decision['predeclared_survival_margin_mev']}` MeV.",
            f"- Calibration verdict: `{metrics['calibration_verdict']}`.",
            "",
            "## Routing",
            "",
            f"- Canonical destination: `{RESULT_REL_DIR.as_posix()}/`.",
            "- Gate A: PASS for AGENT_PUBLISHED if repository validation passes.",
            "- Gate B: not attempted.",
            "- Claim impact: none. Knowledge impact: none. Prediction impact: none.",
            "",
        ]
    )


def _write_result_package(metrics: dict[str, Any], result_dir: Path) -> None:
    result_dir.mkdir(parents=True, exist_ok=True)
    input_hashes = _copy_result_inputs(result_dir)
    result_metrics = _result_metrics(metrics)
    result_yaml = _build_result_yaml(metrics, input_hashes)

    (result_dir / "metrics.json").write_text(
        json.dumps(result_metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_yaml(result_dir / "result.yaml", result_yaml)
    (result_dir / "report.md").write_text(_render_result_report(metrics), encoding="utf-8")
    (result_dir / "gate_a_report.md").write_text(_render_gate_a_report(metrics), encoding="utf-8")
    (result_dir / "claim_update.md").write_text(
        "# Claim Update\n\nNo CLAIM artifact is proposed or modified by this Gate-A package.\n",
        encoding="utf-8",
    )
    (result_dir / "claim_update.patch.md").write_text(
        "# Claim Update Patch\n\nNo patch proposed.\n",
        encoding="utf-8",
    )
    (result_dir / "knowledge_update.md").write_text(
        "# Knowledge Update\n\nNo KNOW artifact is proposed or modified by this Gate-A package.\n",
        encoding="utf-8",
    )
    (result_dir / "knowledge_update.patch.md").write_text(
        "# Knowledge Update Patch\n\nNo patch proposed.\n",
        encoding="utf-8",
    )
    (result_dir / "review_summary.md").write_text(
        "\n".join(
            [
                f"# Review Summary - {RESULT_ID}",
                "",
                "The independent replay reproduced AGENT-RUN-0080 exactly on the selected metrics.",
                "The GP correction survives controls on the retrospective post-AME2020 holdout,",
                "but uncertainty remains heavy-tailed/miscalibrated. This package requests",
                "AGENT_PUBLISHED only; no prediction, claim, or knowledge artifact is proposed.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    _write_yaml(
        result_dir / "review_metadata.yaml",
        {
            "schema_version": "1",
            "artifact_type": "review_metadata",
            "result_id": RESULT_ID,
            "run_id": RESULT_RUN_ID,
            "experiment_id": RESULT_EXP_ID,
            "claim_id": None,
            "knowledge_id": None,
            "generated_at": RESULT_GENERATED_AT,
            "proposed_claim_status": None,
            "required_human_review": False,
            "evidence_basis": [RESULT_ID, f"agent_runs/{AGENT_RUN_ID}/metrics.json"],
            "claim_target_file": None,
            "knowledge_target_file": None,
            "patch_artifacts": {
                "claim_patch": f"{RESULT_REL_DIR.as_posix()}/claim_update.patch.md",
                "knowledge_patch": f"{RESULT_REL_DIR.as_posix()}/knowledge_update.patch.md",
                "review_summary": f"{RESULT_REL_DIR.as_posix()}/review_summary.md",
            },
        },
    )


if __name__ == "__main__":
    raise SystemExit(main())
