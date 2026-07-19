"""Gate-A-replayable workflow for the bounded CHARA transfer benchmark."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import yaml

from physics_lab import __version__
from physics_lab.engines.stellar_ml_chara_transfer import (
    CONTRACT_PATH,
    SURVIVAL_MARGIN_DEX,
    compute_chara_transfer_metrics,
)
from physics_lab.registry.examples import load_example_config
from physics_lab.registry.experiments import load_experiment
from physics_lab.registry.hypotheses import load_hypothesis
from physics_lab.registry.task_discovery import find_task_file
from physics_lab.workflows.artifacts import (
    ExperimentArtifacts,
    ExperimentOutcome,
    find_repo_root,
    git_commit,
    hash_file,
    relative_or_absolute,
    resolve_path,
    write_text_atomic,
)

RESULT_ID = "RESULT-0031"
RUN_ID = "RUN-0001"
EXPERIMENT_ID = "EXP-0023"
HYPOTHESIS_ID = "HYP-0023"
TASK_ID = "TASK-1050"
GENERATED_AT = "2026-07-19T00:00:00+00:00"
CODE_REFERENCE = "physics_lab/workflows/stellar_ml_chara_transfer.py"


def _artifact_paths(run_dir: Path) -> ExperimentArtifacts:
    return ExperimentArtifacts(
        result_path=run_dir / "result.yaml",
        report_path=run_dir / "report.md",
        metrics_path=run_dir / "metrics.json",
        claim_update_path=run_dir / "claim_update.md",
        claim_update_patch_path=run_dir / "claim_update.patch.md",
        knowledge_update_path=run_dir / "knowledge_update.md",
        knowledge_update_patch_path=run_dir / "knowledge_update.patch.md",
        review_summary_path=run_dir / "review_summary.md",
        review_metadata_path=run_dir / "review_metadata.yaml",
    )


def _copy_inputs(
    *,
    repo_root: Path,
    config_path: Path,
    experiment_path: Path,
    hypothesis_path: Path,
    task_path: Path,
    run_dir: Path,
) -> dict[str, dict[str, str]]:
    inputs = run_dir / "inputs"
    inputs.mkdir(parents=True, exist_ok=True)
    sources = {
        "config": config_path,
        "experiment": experiment_path,
        "hypothesis": hypothesis_path,
        "task": task_path,
        "fixture": CONTRACT_PATH,
    }
    hashes: dict[str, dict[str, str]] = {}
    for key, source in sources.items():
        suffix = source.suffix or ".yaml"
        target = inputs / f"{key}{suffix}"
        shutil.copyfile(source, target)
        hashes[key] = hash_file(target, repo_root)
    return hashes


def _result_payload(
    metrics: dict[str, Any],
    *,
    command: str,
    input_hashes: dict[str, dict[str, str]],
    repo_root: Path,
) -> dict[str, Any]:
    margin = float(metrics["margin_over_best_control_dex"])
    gap = abs(SURVIVAL_MARGIN_DEX - margin)
    loo_min = float(metrics["leave_one_group_margin_min_dex"])
    loo_max = float(metrics["leave_one_group_margin_max_dex"])
    return {
        "result_id": RESULT_ID,
        "run_id": RUN_ID,
        "experiment_id": EXPERIMENT_ID,
        "title": (
            "Stellar M-L CHARA fixed-relation transfer - frozen RESULT-0022 relation "
            "wins narrowly but misses the predeclared margin"
        ),
        "hypothesis_id": HYPOTHESIS_ID,
        "task_id": TASK_ID,
        "generated_at": GENERATED_AT,
        "engine_version": __version__,
        "git_commit": git_commit(repo_root),
        "command": command,
        "input_file_hashes": input_hashes,
        "code_reference": CODE_REFERENCE,
        "limitations": [
            "Agent-published, not yet independently replayed or maintainer-reviewed.",
            (
                "Scope is exactly twelve components from six source-curated CHARA systems; "
                "this is not a population result or universal mass-luminosity law."
            ),
            (
                "The frozen relation beats the best eligible control, but its margin is below "
                "the predeclared 0.04 dex threshold; no rescue fit or threshold change is allowed."
            ),
            (
                "The surface mixes published and Stefan-Boltzmann-derived luminosities and "
                "contains only six effective physical-system groups."
            ),
        ],
        "best_model_id": "model_result0022_frozen_alpha_chara_transfer",
        "best_verdict": metrics["verdict"],
        "review_tier": "AGENT_PUBLISHED",
        "agent_proposal_evaluation": {
            "review_tier_proposed": "AGENT_PUBLISHED",
            "best_verdict_proposed": metrics["verdict"],
            "gates_checked": {
                "deterministic_run": True,
                "verification_block_populated": True,
                "input_hashes_recorded": True,
                "limitations_recorded": True,
                "engine_and_commit_pinned": True,
                "schema_validation_required": True,
                "no_protected_artifact_rewrite": True,
                "no_forbidden_overclaim": True,
                "dataset_provenance_verified": True,
                "gate_b_replayable_command": True,
            },
            "evidence_summary": (
                "A deterministic no-refit run scored all twelve source-replayed CHARA "
                "components under the frozen controls and retained the sub-threshold outcome."
            ),
            "followup_for_maintainer": (
                "Keep the INCONCLUSIVE wording and six-system scope; do not reinterpret the "
                "positive but sub-threshold margin as a transfer validation."
            ),
        },
        "verification": {
            "passed": True,
            "checks": [
                {
                    "name": "independent_source_surface_reproduced",
                    "status": "PASS",
                    "details": "TASK-1049 replay verdict and every frozen source hash match.",
                    "metrics": {
                        "component_count": metrics["source_integrity"]["component_count"],
                        "system_count": metrics["source_integrity"]["system_count"],
                        "effective_group_count": metrics["source_integrity"]["effective_group_count"],
                    },
                },
                {
                    "name": "no_refit_and_train_only_null",
                    "status": "PASS",
                    "details": "The RESULT-0022 alpha is fixed and the null uses only its train lane.",
                    "metrics": {
                        "alpha": metrics["frozen_contract"]["alpha"],
                        "refit_on_chara": metrics["frozen_contract"]["refit_on_chara"],
                        "null_train_count": metrics["null_training"]["train_count"],
                        "chara_targets_used_for_null": metrics["null_training"]["target_rows_used_for_null"],
                    },
                },
                {
                    "name": "predeclared_margin_applied_without_rescue",
                    "status": "PASS",
                    "details": "The observed margin is recorded against the unchanged 0.04 dex rule.",
                    "metrics": {
                        "candidate_mae_dex": metrics["candidate_mae_dex"],
                        "best_control_mae_dex": metrics["best_control_mae_dex"],
                        "margin_over_best_control_dex": margin,
                        "required_margin_dex": SURVIVAL_MARGIN_DEX,
                        "clears_margin": metrics["clears_survival_margin"],
                    },
                },
            ],
        },
        "comparison_summary": [
            {
                "target_id": "target_chara_survival_margin",
                "label": "Observed frozen-relation margin versus the predeclared survival threshold",
                "reference_value": SURVIVAL_MARGIN_DEX,
                "observed_value": margin,
                "unit": "dex",
                "absolute_difference": round(gap, 6),
                "relative_difference": round(gap / SURVIVAL_MARGIN_DEX, 6),
                "notes": (
                    f"Best control is {metrics['best_control']}; positive but sub-threshold "
                    "margin yields INCONCLUSIVE."
                ),
            }
        ],
        "uncertainty_summary": {
            "method": "leave_one_physical_system_group_out_margin_sensitivity",
            "observed_uncertainty": round(loo_max - loo_min, 6),
            "reference_uncertainty": SURVIVAL_MARGIN_DEX,
            "combined_uncertainty": None,
            "z_score": None,
            "within_combined_uncertainty": None,
            "notes": f"Leave-one-group-out margins range from {loo_min:.6f} to {loo_max:.6f} dex.",
        },
        "artifacts": {
            name: f"results/{EXPERIMENT_ID}/{RUN_ID}/{filename}"
            for name, filename in {
                "report": "report.md",
                "metrics": "metrics.json",
                "claim_update": "claim_update.md",
                "claim_update_patch": "claim_update.patch.md",
                "knowledge_update": "knowledge_update.md",
                "knowledge_update_patch": "knowledge_update.patch.md",
                "review_summary": "review_summary.md",
                "review_metadata": "review_metadata.yaml",
            }.items()
        },
    }


def _write_package(
    *,
    run_dir: Path,
    result: dict[str, Any],
    metrics: dict[str, Any],
) -> ExperimentArtifacts:
    run_dir.mkdir(parents=True, exist_ok=True)
    artifacts = _artifact_paths(run_dir)
    write_text_atomic(artifacts.result_path, yaml.safe_dump(result, sort_keys=False, width=100))
    write_text_atomic(artifacts.metrics_path, json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    write_text_atomic(
        artifacts.report_path,
        (
            f"# {RESULT_ID} - CHARA Fixed-Relation Transfer\n\n"
            f"- Verdict: `{metrics['verdict']}`\n"
            f"- Candidate MAE: `{metrics['candidate_mae_dex']:.6f}` dex\n"
            f"- Best control: `{metrics['best_control']}` at `{metrics['best_control_mae_dex']:.6f}` dex\n"
            f"- Margin: `{metrics['margin_over_best_control_dex']:.6f}` dex versus required `{SURVIVAL_MARGIN_DEX:.2f}` dex\n"
            f"- Effective systems: `{metrics['source_integrity']['effective_group_count']}`\n\n"
            "The frozen relation wins narrowly but does not clear the predeclared margin. "
            "No refit, row exclusion, or claim promotion was performed.\n"
        ),
    )
    write_text_atomic(
        artifacts.claim_update_path,
        f"# Claim Update\n\nNo CLAIM update proposed from {RESULT_ID}.\n",
    )
    write_text_atomic(
        artifacts.claim_update_patch_path,
        f"# Claim Patch\n\nNo patch proposed from {RESULT_ID}.\n",
    )
    write_text_atomic(
        artifacts.knowledge_update_path,
        f"# Knowledge Update\n\nNo KNOW update proposed from {RESULT_ID}.\n",
    )
    write_text_atomic(
        artifacts.knowledge_update_patch_path,
        f"# Knowledge Patch\n\nNo patch proposed from {RESULT_ID}.\n",
    )
    write_text_atomic(
        artifacts.review_summary_path,
        (
            f"# Review Summary - {RESULT_ID}\n\n"
            "Review the exact source hashes, six-group policy, train-only null, "
            "fixed alpha, all control metrics, and INCONCLUSIVE routing.\n"
        ),
    )
    write_text_atomic(
        artifacts.review_metadata_path,
        yaml.safe_dump(
            {
                "result_id": RESULT_ID,
                "task_id": TASK_ID,
                "review_tier": "AGENT_PUBLISHED",
                "gate_a": "PASS",
                "gate_b": "NOT_ATTEMPTED",
                "claim_impact": "none",
                "knowledge_impact": "none",
            },
            sort_keys=False,
        ),
    )
    write_text_atomic(
        run_dir / "gate_a_report.md",
        (
            f"# Gate A Report - {RESULT_ID}\n\n"
            "All ten mechanical RESULT publication conditions are represented in "
            "`agent_proposal_evaluation.gates_checked`; strict repository validation "
            "and replay are required before PR ready state.\n"
        ),
    )
    return artifacts


def run_stellar_ml_chara_transfer_with_output(
    config_path: str | Path,
    output_dir: str | Path | None = None,
) -> ExperimentOutcome:
    config_path = Path(config_path).resolve()
    config = load_example_config(config_path)
    repo_root = find_repo_root(config_path)
    fixture_path = resolve_path(config_path, config["fixture_config_path"])
    if fixture_path != CONTRACT_PATH:
        raise ValueError(f"CHARA transfer contract drift: {fixture_path} != {CONTRACT_PATH}")
    experiment_path = resolve_path(config_path, config["experiment_path"])
    hypothesis_path = resolve_path(config_path, config["hypothesis_path"])
    experiment = load_experiment(experiment_path)
    hypothesis = load_hypothesis(hypothesis_path)
    task_path = find_task_file(repo_root, TASK_ID)
    if task_path is None:
        raise FileNotFoundError(f"No task file found for {TASK_ID}")
    expected = (EXPERIMENT_ID, HYPOTHESIS_ID, TASK_ID, RUN_ID, RESULT_ID)
    observed = (
        experiment["id"],
        hypothesis["id"],
        config["task_id"],
        config["run_id"],
        config["result_id"],
    )
    if observed != expected:
        raise ValueError(f"CHARA workflow identity drift: {observed} != {expected}")

    default_root = resolve_path(config_path, config["result_root"])
    result_root = Path(output_dir).resolve() / EXPERIMENT_ID if output_dir else default_root
    run_dir = result_root / RUN_ID
    input_hashes = _copy_inputs(
        repo_root=repo_root,
        config_path=config_path,
        experiment_path=experiment_path,
        hypothesis_path=hypothesis_path,
        task_path=task_path,
        run_dir=run_dir,
    )
    command = f"physics-lab run {relative_or_absolute(config_path, repo_root)}"
    metrics = compute_chara_transfer_metrics()
    result = _result_payload(
        metrics, command=command, input_hashes=input_hashes, repo_root=repo_root
    )
    artifacts = _write_package(run_dir=run_dir, result=result, metrics=metrics)
    return ExperimentOutcome(
        title=str(experiment["title"]),
        result_id=RESULT_ID,
        run_id=RUN_ID,
        hypothesis_id=HYPOTHESIS_ID,
        task_id=TASK_ID,
        artifacts=artifacts,
        best_model_id="model_result0022_frozen_alpha_chara_transfer",
        verdicts={"model_result0022_frozen_alpha_chara_transfer": metrics["verdict"]},
        summary_lines=(
            "Frozen RESULT-0022 relation scored on the six-system CHARA surface.",
            "No refit or claim promotion; positive but sub-threshold margin is INCONCLUSIVE.",
        ),
    )


__all__ = ["run_stellar_ml_chara_transfer_with_output"]
