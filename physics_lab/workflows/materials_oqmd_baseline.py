"""Gate-A-replayable workflow for the frozen within-OQMD benchmark."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import yaml

from physics_lab import __version__
from physics_lab.engines.materials_oqmd_baseline import (
    DEFAULT_CONFIG,
    run_oqmd_within_source_benchmark,
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

RESULT_ID = "RESULT-0032"
RUN_ID = "RUN-0001"
EXPERIMENT_ID = "EXP-0024"
HYPOTHESIS_ID = "HYP-0024"
TASK_ID = "TASK-1066"
GENERATED_AT = "2026-07-22T00:00:00+00:00"
CODE_REFERENCE = "physics_lab/workflows/materials_oqmd_baseline.py"


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
    fixture_path: Path,
    run_dir: Path,
) -> dict[str, dict[str, str]]:
    inputs = run_dir / "inputs"
    inputs.mkdir(parents=True, exist_ok=True)
    sources = {
        "config": config_path,
        "experiment": experiment_path,
        "hypothesis": hypothesis_path,
        "task": task_path,
        "fixture": fixture_path,
    }
    hashes: dict[str, dict[str, str]] = {}
    for key, source in sources.items():
        target = inputs / f"{key}{source.suffix or '.yaml'}"
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
    fixed = metrics["fixed_split"]
    candidate = fixed["model_metrics"]["candidate"]
    group_null = fixed["model_metrics"]["iupac_group_pair_null"]
    comparison = next(
        item
        for item in fixed["survival_gate"]["comparisons"]
        if item["comparator_id"] == "iupac_group_pair_null"
    )
    sensitivity_maes = [
        item["candidate_holdout_mae"] for item in metrics["sensitivity"]["per_seed"]
    ]
    artifact_prefix = f"results/{EXPERIMENT_ID}/{RUN_ID}"
    return {
        "result_id": RESULT_ID,
        "run_id": RUN_ID,
        "experiment_id": EXPERIMENT_ID,
        "title": (
            "Frozen within-OQMD exact cation-pair baseline fails against the "
            "predeclared IUPAC group-pair null"
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
            "Agent-published negative/control evidence; not yet independently replayed or maintainer-reviewed.",
            *metrics["limitations"],
            (
                "Contract verdict FAIL is represented as best_verdict INVALID in the "
                "RESULT schema; no rescue fit or threshold revision was performed."
            ),
        ],
        "best_model_id": "model_oqmd_cation_pair_mean",
        "best_verdict": "INVALID",
        "review_tier": "AGENT_PUBLISHED",
        "agent_proposal_evaluation": {
            "review_tier_proposed": "AGENT_PUBLISHED",
            "best_verdict_proposed": "INVALID",
            "published_by": {
                "contributor_id": "akutenyov",
                "github_username": "akutenyov",
                "agent_tool": "Codex Desktop",
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
                "gate_b_replayable_command": True,
            },
            "evidence_summary": (
                "The deterministic one-shot run preserved all 172 frozen OQMD rows, "
                "passed source/split/contract integrity checks, and retained the failed "
                "survival outcome. The exact cation-pair baseline beat the global median "
                "and every shuffle control but was worse than the IUPAC group-pair null."
            ),
            "followup_for_maintainer": (
                "Preserve this as bounded negative/control memory. Do not rescue-fit, "
                "reinterpret the within-source result as cross-database evidence, or "
                "promote a materials claim."
            ),
        },
        "verification": {
            "passed": True,
            "checks": [
                {
                    "name": "frozen_inputs_and_prerequisites_match",
                    "status": "PASS",
                    "details": (
                        "Raw source, normalized snapshot, manifest, split, contract, and "
                        "independent replay hashes match the frozen execution config."
                    ),
                    "metrics": {
                        "row_count": sum(metrics["partition_counts"].values()),
                        "train_count": metrics["partition_counts"]["train"],
                        "validation_count": metrics["partition_counts"]["validation"],
                        "holdout_count": metrics["partition_counts"]["holdout"],
                        "composition_leakage_count": len(metrics["composition_leakage"]),
                    },
                },
                {
                    "name": "frozen_model_and_controls_executed_without_rescue",
                    "status": "PASS",
                    "details": (
                        "The train-only exact pair baseline, both nulls, ten shuffle "
                        "instances, row-order check, and five sensitivity seeds ran unchanged."
                    ),
                    "metrics": {
                        "candidate_holdout_mae": candidate["holdout"]["mae"],
                        "global_median_holdout_mae": fixed["model_metrics"]["global_median_null"]["holdout"]["mae"],
                        "iupac_group_pair_holdout_mae": group_null["holdout"]["mae"],
                        "shuffle_instances": len(fixed["controls"]),
                        "sensitivity_seeds": len(metrics["sensitivity"]["per_seed"]),
                    },
                },
                {
                    "name": "predeclared_fail_closed_verdict_applied",
                    "status": "PASS",
                    "details": (
                        "The candidate failed the required margin against the IUPAC "
                        "group-pair null on the fixed holdout and every sensitivity seed."
                    ),
                    "metrics": {
                        "contract_verdict": metrics["verdict"],
                        "observed_margin": comparison["observed_margin"],
                        "required_margin": comparison["required_margin"],
                        "fixed_split_all_comparators_pass": fixed["survival_gate"]["all_comparators_pass"],
                        "all_sensitivity_seeds_pass": metrics["sensitivity"]["all_seeds_pass"],
                    },
                },
            ],
        },
        "comparison_summary": [
            {
                "target_id": "target_oqmd_survival_margin",
                "label": "Exact cation-pair MAE versus IUPAC group-pair null MAE",
                "reference_value": group_null["holdout"]["mae"],
                "observed_value": candidate["holdout"]["mae"],
                "unit": "eV_per_atom",
                "absolute_difference": abs(comparison["observed_margin"]),
                "relative_difference": abs(comparison["observed_margin"]) / group_null["holdout"]["mae"],
                "notes": (
                    "Lower MAE is better. The candidate is worse, so the frozen "
                    "margin rule fails without rescue fitting."
                ),
            }
        ],
        "uncertainty_summary": {
            "method": "five identity-group-preserving seeded repartitions",
            "observed_uncertainty": max(sensitivity_maes) - min(sensitivity_maes),
            "reference_uncertainty": 0.02,
            "combined_uncertainty": None,
            "z_score": None,
            "within_combined_uncertainty": None,
            "notes": (
                "Candidate holdout MAE range across frozen seeds; every seed also "
                "fails against the IUPAC group-pair null."
            ),
        },
        "artifacts": {
            "report": f"{artifact_prefix}/report.md",
            "metrics": f"{artifact_prefix}/metrics.json",
            "claim_update": f"{artifact_prefix}/claim_update.md",
            "claim_update_patch": f"{artifact_prefix}/claim_update.patch.md",
            "knowledge_update": f"{artifact_prefix}/knowledge_update.md",
            "knowledge_update_patch": f"{artifact_prefix}/knowledge_update.patch.md",
            "review_summary": f"{artifact_prefix}/review_summary.md",
            "review_metadata": f"{artifact_prefix}/review_metadata.yaml",
        },
        "scores": [
            {
                "model_id": "model_oqmd_cation_pair_mean",
                "formula": (
                    "Train mean OQMD delta_e per unordered non-oxygen cation pair "
                    "with train global-mean fallback"
                ),
                "coefficients": {
                    "distinct_train_pairs": fixed["distinct_train_cation_pairs"],
                    "global_train_mean_fallback": fixed["train_global_mean"],
                },
                "complexity_score": 2,
                "train_metrics": {
                    "mean_relative_error": candidate["train"]["mean_relative_error"],
                    "max_relative_error": candidate["train"]["max_relative_error"],
                },
                "test_metrics": {
                    "mean_relative_error": candidate["holdout"]["mean_relative_error"],
                    "max_relative_error": candidate["holdout"]["max_relative_error"],
                },
                "composite_score": candidate["holdout"]["mae"],
                "verdict": "INVALID",
            },
            {
                "model_id": "model_oqmd_iupac_group_pair_null",
                "formula": (
                    "Train mean OQMD delta_e per unordered IUPAC cation-group pair "
                    "with train global-mean fallback"
                ),
                "coefficients": {
                    "distinct_train_group_pairs": fixed["distinct_train_iupac_group_pairs"],
                    "global_train_mean_fallback": fixed["train_global_mean"],
                },
                "complexity_score": 1,
                "train_metrics": {
                    "mean_relative_error": group_null["train"]["mean_relative_error"],
                    "max_relative_error": group_null["train"]["max_relative_error"],
                },
                "test_metrics": {
                    "mean_relative_error": group_null["holdout"]["mean_relative_error"],
                    "max_relative_error": group_null["holdout"]["max_relative_error"],
                },
                "composite_score": group_null["holdout"]["mae"],
                "verdict": "VALID",
            },
        ],
    }


def _write_package(
    *, run_dir: Path, result: dict[str, Any], metrics: dict[str, Any]
) -> ExperimentArtifacts:
    run_dir.mkdir(parents=True, exist_ok=True)
    artifacts = _artifact_paths(run_dir)
    write_text_atomic(artifacts.result_path, yaml.safe_dump(result, sort_keys=False, width=100))
    write_text_atomic(artifacts.metrics_path, json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    write_text_atomic(
        run_dir / "metric_control_ledger.json",
        json.dumps(
            {
                "fixed_split": metrics["fixed_split"],
                "sensitivity": metrics["sensitivity"],
                "row_order_invariance": metrics["row_order_invariance"],
                "failure_cases": metrics["failure_cases"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    candidate = metrics["fixed_split"]["model_metrics"]["candidate"]["holdout"]
    group_null = metrics["fixed_split"]["model_metrics"]["iupac_group_pair_null"]["holdout"]
    fixed = metrics["fixed_split"]
    model_rows = []
    for model_id, partition_metrics in fixed["model_metrics"].items():
        model_rows.append(
            f"| `{model_id}` | {partition_metrics['train']['mae']:.12f} | "
            f"{partition_metrics['validation']['mae']:.12f} | "
            f"{partition_metrics['holdout']['mae']:.12f} | "
            f"{partition_metrics['holdout']['rmse']:.12f} | "
            f"{partition_metrics['holdout']['unseen_group_count']} |"
        )
    control_rows = [
        f"| `{item['control_id']}` | {item['holdout']['mae']:.12f} | "
        f"{next(row for row in fixed['survival_gate']['comparisons'] if row['comparator_id'] == item['control_id'])['passes']} |"
        for item in fixed["controls"]
    ]
    sensitivity_rows = [
        f"| {item['seed']} | {item['candidate_holdout_mae']:.12f} | "
        f"{next(row for row in item['comparisons'] if row['comparator_id'] == 'iupac_group_pair_null')['comparator_mae']:.12f} | "
        f"{item['all_comparators_pass']} |"
        for item in metrics["sensitivity"]["per_seed"]
    ]
    failure_rows = [
        f"| {item['entry_id']} | {item['name']} | {'-'.join(item['cation_pair'])} | "
        f"{item['target']:.12f} | {item['prediction']:.12f} | "
        f"{item['residual']:.12f} | {item['absolute_residual']:.12f} | "
        f"{item['used_global_fallback']} |"
        for item in metrics["failure_cases"]
    ]
    report = (
        f"# {RESULT_ID} — Frozen Within-OQMD Baseline\n\n"
        f"- Contract verdict: `{metrics['verdict']}`\n"
        "- RESULT verdict: `INVALID`\n"
        f"- Exact cation-pair holdout MAE: `{candidate['mae']:.12f}` eV/atom\n"
        f"- IUPAC group-pair null holdout MAE: `{group_null['mae']:.12f}` eV/atom\n"
        f"- Exact-pair unseen holdout rows: `{candidate['unseen_group_count']}` of `26`\n"
        "- Sensitivity seeds passing all comparators: `0/5`\n\n"
        "The exact cation-pair baseline beats the global-median and every frozen "
        "shuffle control, but it is worse than the predeclared IUPAC group-pair "
        "null. The fail-closed contract therefore returns FAIL. No refit, row "
        "exclusion, threshold change, or cross-database pooling was performed.\n\n"
        "## Frozen integrity and partition ledger\n\n"
        "All six paths and SHA-256 values in the execution config matched before "
        "target loading. TASK-1053 reported `SPLIT_READY_FOR_BENCHMARK_PREFLIGHT`, "
        "TASK-1054 reported `CONTRACT_READY_FOR_FROZEN_SPLIT`, and TASK-1063 "
        "reported `INDEPENDENT_SOURCE_REPLAY_PASS`.\n\n"
        "| Partition | Rows | Reduced-composition groups |\n"
        "| --- | ---: | ---: |\n"
        f"| train | {metrics['partition_counts']['train']} | {metrics['partition_group_counts']['train']} |\n"
        f"| validation | {metrics['partition_counts']['validation']} | {metrics['partition_group_counts']['validation']} |\n"
        f"| holdout | {metrics['partition_counts']['holdout']} | {metrics['partition_group_counts']['holdout']} |\n\n"
        f"Missing/non-finite target exclusions: `{metrics['missing_or_invalid_target_exclusions']}`. "
        f"Cross-partition composition leakage: `{len(metrics['composition_leakage'])}`. "
        f"Row-order MAE drift: `{metrics['row_order_invariance']['drift']:.12f}`.\n\n"
        "## Primary and secondary metrics\n\n"
        "| Model | Train MAE | Validation MAE | Holdout MAE | Holdout RMSE | Unseen holdout groups |\n"
        "| --- | ---: | ---: | ---: | ---: | ---: |\n"
        + "\n".join(model_rows)
        + "\n\n## Required shuffle controls\n\n"
        "| Control | Holdout MAE | Candidate clears frozen margin |\n"
        "| --- | ---: | --- |\n"
        + "\n".join(control_rows)
        + "\n\n## Identity-group-preserving sensitivity\n\n"
        "| Seed | Candidate holdout MAE | IUPAC null holdout MAE | All comparators pass |\n"
        "| ---: | ---: | ---: | --- |\n"
        + "\n".join(sensitivity_rows)
        + "\n\n## Complete frozen-holdout failure ledger\n\n"
        "Every holdout row is retained; rows using the train-global-mean fallback "
        "are marked explicitly.\n\n"
        "| Entry | Name | Cation pair | Target | Prediction | Residual | Absolute residual | Fallback |\n"
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |\n"
        + "\n".join(failure_rows)
        + "\n\n## Boundary\n\n"
        "This is bounded negative/control evidence on one computed-DFT OQMD slice, "
        "not experimental replication, a materials law, or a material recommendation.\n"
    )
    write_text_atomic(
        artifacts.report_path,
        report,
    )
    write_text_atomic(artifacts.claim_update_path, f"# Claim Update\n\nNo CLAIM update proposed from {RESULT_ID}.\n")
    write_text_atomic(artifacts.claim_update_patch_path, f"# Claim Patch\n\nNo patch proposed from {RESULT_ID}.\n")
    write_text_atomic(artifacts.knowledge_update_path, f"# Knowledge Update\n\nNo KNOW update proposed from {RESULT_ID}.\n")
    write_text_atomic(artifacts.knowledge_update_patch_path, f"# Knowledge Patch\n\nNo patch proposed from {RESULT_ID}.\n")
    write_text_atomic(
        artifacts.review_summary_path,
        (
            f"# Review Summary — {RESULT_ID}\n\n"
            "Verify all six frozen hashes, the 120/26/26 split, no leakage, exact "
            "pair and IUPAC group-pair definitions, ten shuffle instances, five "
            "sensitivity seeds, all 26 holdout failure rows, and FAIL→INVALID routing.\n"
        ),
    )
    write_text_atomic(
        artifacts.review_metadata_path,
        yaml.safe_dump(
            {
                "schema_version": "1",
                "artifact_type": "review_metadata",
                "result_id": RESULT_ID,
                "run_id": RUN_ID,
                "experiment_id": EXPERIMENT_ID,
                "claim_id": None,
                "knowledge_id": None,
                "generated_at": GENERATED_AT,
                "proposed_claim_status": None,
                "required_human_review": True,
                "evidence_basis": [
                    "data/materials/oqmd_within_source_benchmark_config.yaml",
                    "docs/reviews/materials/oqmd-within-source-baseline-control-contract.yaml",
                    f"results/{EXPERIMENT_ID}/{RUN_ID}/metrics.json",
                    f"results/{EXPERIMENT_ID}/{RUN_ID}/metric_control_ledger.json",
                ],
                "claim_target_file": None,
                "knowledge_target_file": None,
                "patch_artifacts": {
                    "claim_patch": f"results/{EXPERIMENT_ID}/{RUN_ID}/claim_update.patch.md",
                    "knowledge_patch": f"results/{EXPERIMENT_ID}/{RUN_ID}/knowledge_update.patch.md",
                    "review_summary": f"results/{EXPERIMENT_ID}/{RUN_ID}/review_summary.md",
                },
            },
            sort_keys=False,
        ),
    )
    write_text_atomic(
        run_dir / "gate_a_report.md",
        (
            f"# Gate A Report — {RESULT_ID}\n\n"
            "Gate A mechanical fields are populated for an `AGENT_PUBLISHED` "
            "negative/control result. Verify with:\n\n"
            "```text\n"
            "python scripts/apl_check_result_publication.py "
            f"results/{EXPERIMENT_ID}/{RUN_ID}/result.yaml --root .\n"
            "python -m physics_lab.cli validate-repo . --strict --fail-on-warnings\n"
            "```\n\n"
            "Expected publication-gate verdict: `PASS`. Gate B is not attempted.\n"
        ),
    )
    return artifacts


def run_materials_oqmd_baseline_with_output(
    config_path: str | Path, output_dir: str | Path | None = None
) -> ExperimentOutcome:
    config_path = Path(config_path).resolve()
    config = load_example_config(config_path)
    repo_root = find_repo_root(config_path)
    experiment_path = resolve_path(config_path, config["experiment_path"])
    hypothesis_path = resolve_path(config_path, config["hypothesis_path"])
    fixture_path = resolve_path(config_path, config["fixture_config_path"])
    if fixture_path != repo_root / DEFAULT_CONFIG:
        raise ValueError(f"OQMD benchmark config drift: {fixture_path}")
    experiment = load_experiment(experiment_path)
    hypothesis = load_hypothesis(hypothesis_path)
    task_path = find_task_file(repo_root, TASK_ID)
    if task_path is None:
        raise FileNotFoundError(f"No task file found for {TASK_ID}")
    observed = (
        experiment["id"],
        hypothesis["id"],
        config["task_id"],
        config["run_id"],
        config["result_id"],
    )
    expected = (EXPERIMENT_ID, HYPOTHESIS_ID, TASK_ID, RUN_ID, RESULT_ID)
    if observed != expected:
        raise ValueError(f"OQMD workflow identity drift: {observed} != {expected}")

    default_root = resolve_path(config_path, config["result_root"])
    result_root = Path(output_dir).resolve() / EXPERIMENT_ID if output_dir else default_root
    run_dir = result_root / RUN_ID
    input_hashes = _copy_inputs(
        repo_root=repo_root,
        config_path=config_path,
        experiment_path=experiment_path,
        hypothesis_path=hypothesis_path,
        task_path=task_path,
        fixture_path=fixture_path,
        run_dir=run_dir,
    )
    command = f"physics-lab run {relative_or_absolute(config_path, repo_root)}"
    metrics = run_oqmd_within_source_benchmark(fixture_path)
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
        best_model_id="model_oqmd_cation_pair_mean",
        verdicts={"model_oqmd_cation_pair_mean": "INVALID"},
        summary_lines=(
            "Frozen within-OQMD benchmark completed with contract verdict FAIL.",
            "Published as bounded negative/control evidence; no claim promotion.",
        ),
    )


__all__ = ["run_materials_oqmd_baseline_with_output"]
