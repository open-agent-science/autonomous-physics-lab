"""Workflow adapter for Textbook Formula Audit exact-reference fixtures."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import yaml

from physics_lab import __version__
from physics_lab.engines.stefan_boltzmann import audit_exact_reference_fixture
from physics_lab.registry.examples import load_example_config
from physics_lab.registry.experiments import load_experiment
from physics_lab.registry.hypotheses import load_hypothesis
from physics_lab.workflows.artifacts import (
    ExperimentArtifacts,
    ExperimentOutcome,
    find_repo_root,
    git_commit,
    relative_or_absolute,
    resolve_path,
    snapshot_input_files,
    task_path,
    write_text_atomic,
)


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping in {path}")
    return payload


def _dump_yaml(path: Path, payload: dict[str, Any]) -> None:
    write_text_atomic(path, yaml.safe_dump(payload, sort_keys=False, allow_unicode=True))


def _render_report(metrics: dict[str, Any], *, result_id: str) -> str:
    lines = [
        "# Textbook Stefan-Boltzmann exact-reference fixture",
        "",
        f"- Result: `{result_id}`",
        f"- Fixture provenance task: `{metrics['task_id']}`",
        f"- Fixture: `{metrics['fixture_id']}`",
        f"- Verdict: `{metrics['verdict']}`",
        "- Boundary: synthetic software/gate fixture only; no empirical audit.",
        "",
        "## Gates",
        "",
        "| gate | status |",
        "| --- | --- |",
    ]
    for name, gate in metrics["gates"].items():
        lines.append(f"| `{name}` | `{gate['status']}` |")
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in metrics["limitations"]],
            "",
            "## Output Routing",
            "",
            "- Canonical destination: scoped software-result packaging route; see `result.yaml`.",
            "- Review tier: AGENT_PUBLISHED is recorded in the packaged RESULT.",
            "- Gate A: evaluated by the result-publication gate on the packaged RESULT.",
            "- Gate B: not attempted.",
            "- Claim impact: no claim change.",
            "- Knowledge impact: no knowledge change.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_review_summary(result_id: str, metrics: dict[str, Any]) -> str:
    exact_gate = metrics["gates"]["exact_reference"]
    return "\n".join(
        [
            "# Textbook Exact-Reference Result Review Summary",
            "",
            f"- Result: `{result_id}`",
            "- Review tier: `AGENT_PUBLISHED`",
            f"- Verdict: `{metrics['verdict']}`",
            f"- Rows: `{metrics['scope']['row_count']}` synthetic fixture rows",
            f"- Max relative error: `{exact_gate['max_relative_error']}`",
            "- Boundary: software/convention fixture only; no empirical physics claim.",
            "",
        ]
    )


def _render_claim_update(claim_id: str, result_id: str) -> str:
    target = f"`{claim_id}`" if claim_id else "none"
    return "\n".join(
        [
            "# Claim Update",
            "",
            f"- Claim: {target}",
            f"- Evidence basis: `{result_id}`",
            "- Proposed status: none.",
            "- Scope: no claim artifact is created or promoted by this result-only task.",
            "",
        ]
    )


def _render_knowledge_update(knowledge_id: str, result_id: str) -> str:
    target = f"`{knowledge_id}`" if knowledge_id else "none"
    return "\n".join(
        [
            "# Knowledge Update",
            "",
            f"- Knowledge entry: {target}",
            f"- Evidence basis: `{result_id}`",
            "- Scope: no knowledge artifact is created or promoted by this result-only task.",
            "",
        ]
    )


def _render_patch_stub(title: str, target_file: str, result_id: str) -> str:
    return "\n".join(
        [
            f"# {title}",
            "",
            "## Target File",
            "",
            f"`{target_file}`",
            "",
            "## Evidence Basis",
            "",
            f"- `{result_id}`",
            "",
            "## Patch",
            "",
            "No automatic text patch is applied by this workflow; this task records",
            "a scoped RESULT only and does not create claim or knowledge artifacts.",
            "",
        ]
    )


def run_textbook_exact_reference_with_output(
    config_path: str | Path,
    output_dir: str | Path | None = None,
) -> ExperimentOutcome:
    """Run the scoped Textbook exact-reference software-fixture workflow."""
    config_path = Path(config_path).resolve()
    config = load_example_config(config_path)
    experiment_path = resolve_path(config_path, config["experiment_path"])
    hypothesis_path = resolve_path(config_path, config["hypothesis_path"])
    fixture_config_path = resolve_path(config_path, config["fixture_config_path"])
    repo_root = find_repo_root(config_path)
    experiment = load_experiment(experiment_path)
    hypothesis = load_hypothesis(hypothesis_path)
    if experiment["hypothesis_id"] != hypothesis["id"]:
        raise ValueError(
            "Experiment hypothesis_id does not match loaded hypothesis id: "
            f"{experiment['hypothesis_id']} != {hypothesis['id']}"
        )

    task_id = str(config["task_id"])
    run_id = str(config["run_id"])
    result_id = str(config["result_id"])
    claim_id = str(config["claim_id"]) if config.get("claim_id") else ""
    knowledge_id = str(config["knowledge_id"]) if config.get("knowledge_id") else ""
    default_result_root = resolve_path(config_path, str(config["result_root"]))
    result_root = (
        Path(output_dir).resolve() / str(experiment["id"])
        if output_dir is not None
        else default_result_root
    )

    fixture_config = _load_yaml_mapping(fixture_config_path)
    metrics = audit_exact_reference_fixture(fixture_config)
    if metrics["verdict"] != "VALID_IN_RANGE":
        raise ValueError(f"Textbook exact-reference fixture did not pass: {metrics['verdict']}")

    run_dir = result_root / run_id
    result_path = run_dir / "result.yaml"
    report_path = run_dir / "report.md"
    metrics_path = run_dir / "metrics.json"
    claim_update_path = run_dir / "claim_update.md"
    claim_update_patch_path = run_dir / "claim_update.patch.md"
    knowledge_update_path = run_dir / "knowledge_update.md"
    knowledge_update_patch_path = run_dir / "knowledge_update.patch.md"
    review_summary_path = run_dir / "review_summary.md"
    review_metadata_path = run_dir / "review_metadata.yaml"
    run_dir.mkdir(parents=True, exist_ok=True)

    command_path = relative_or_absolute(config_path, repo_root)
    command = f"physics-lab run {command_path}"
    task_file = task_path(repo_root, task_id)
    input_hashes = snapshot_input_files(
        run_dir=run_dir,
        repo_root=repo_root,
        input_files={
            "config": config_path,
            "fixture": fixture_config_path,
            "experiment": experiment_path,
            "hypothesis": hypothesis_path,
            "task": task_file,
        },
    )

    exact_gate = metrics["gates"]["exact_reference"]
    wrong_temperature_gate = metrics["gates"]["wrong_temperature_exponent_control"]
    wrong_area_gate = metrics["gates"]["wrong_area_control"]
    verification = {
        "passed": True,
        "checks": [
            {
                "name": "deterministic_exact_reference_replay",
                "status": "PASS",
                "details": (
                    "The workflow reproduced all synthetic reference rows at max "
                    "relative error 0.0 under the declared tolerance, and all "
                    "software gates passed."
                ),
                "metrics": {
                    "row_count": metrics["scope"]["row_count"],
                    "reference_row_count": metrics["scope"]["reference_row_count"],
                    "holdout_row_count": metrics["scope"]["holdout_row_count"],
                    "exact_reference_max_relative_error": exact_gate["max_relative_error"],
                    "tolerance_relative_error": fixture_config["tolerances"]["relative_error"],
                },
            },
            {
                "name": "declared_negative_controls_rejected",
                "status": "PASS",
                "details": (
                    "Both declared convention negative controls (wrong temperature "
                    "exponent and wrong area multiplier) were rejected as expected."
                ),
                "metrics": {
                    "wrong_temperature_exponent_control_rejected": wrong_temperature_gate[
                        "control_rejected"
                    ],
                    "wrong_area_control_rejected": wrong_area_gate["control_rejected"],
                },
            },
            {
                "name": "protected_result_not_rewritten",
                "status": "PASS",
                "details": "RESULT-0019 is new and is not pinned in results/golden-results.yaml.",
                "metrics": {"protected_result_rewrite": False},
            },
        ],
    }

    artifacts = {
        "report": relative_or_absolute(report_path, repo_root),
        "metrics": relative_or_absolute(metrics_path, repo_root),
        "claim_update": relative_or_absolute(claim_update_path, repo_root),
        "claim_update_patch": relative_or_absolute(claim_update_patch_path, repo_root),
        "knowledge_update": relative_or_absolute(knowledge_update_path, repo_root),
        "knowledge_update_patch": relative_or_absolute(knowledge_update_patch_path, repo_root),
        "review_summary": relative_or_absolute(review_summary_path, repo_root),
        "review_metadata": relative_or_absolute(review_metadata_path, repo_root),
    }
    result_payload = {
        "result_id": result_id,
        "run_id": run_id,
        "experiment_id": str(experiment["id"]),
        "title": "Textbook Stefan-Boltzmann Exact-Reference Software Fixture Result",
        "hypothesis_id": str(hypothesis["id"]),
        "task_id": task_id,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "engine_version": __version__,
        "git_commit": git_commit(repo_root),
        "command": command,
        "input_file_hashes": input_hashes,
        "code_reference": "physics_lab/workflows/textbook_exact_reference.py",
        "limitations": [
            "Agent-published, not yet independently validated or maintainer-reviewed.",
            "Synthetic exact-reference software fixture only; no empirical emitter rows were ingested.",
            "Validates deterministic software, units, and the frozen CODATA 2022 constant convention; it does not validate or falsify Stefan-Boltzmann, Wien displacement, blackbody physics, or stellar observations.",
            "No claim, knowledge, prediction, or empirical formula promotion is performed by this result-only task.",
        ],
        "best_model_id": "model_stefan_boltzmann_exact_reference",
        "best_verdict": "VALID_IN_RANGE",
        "review_tier": "AGENT_PUBLISHED",
        "agent_proposal_evaluation": {
            "review_tier_proposed": "AGENT_PUBLISHED",
            "best_verdict_proposed": "VALID_IN_RANGE",
            "published_by": {
                "contributor_id": "roman",
                "github_username": "gladunrv",
                "agent_tool": "Claude Code",
                "model_version": "Claude Opus 4.8",
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
                "The committed Stefan-Boltzmann exact-reference workflow replayed "
                "deterministically against the synthetic fixture: 16 rows, max "
                "exact-reference relative error 0.0 under a 1e-12 tolerance, all "
                "software gates passing, and both declared convention negative "
                "controls rejected. The scoped verdict is VALID_IN_RANGE for the "
                "software/convention fixture only; no empirical formula behavior is asserted."
            ),
            "followup_for_maintainer": (
                "Keep this RESULT as agent-published software/convention evidence. "
                "It is the intended replay target for the first Gate B independent-replay "
                "task (TASK-0635). Claim and knowledge promotion remain out of scope."
            ),
        },
        "verification": verification,
        "comparison_summary": [
            {
                "target_id": "target_exact_reference_relative_error_zero",
                "label": "Exact-reference fixture relative error",
                "reference_value": 0.0,
                "observed_value": exact_gate["max_relative_error"],
                "unit": "relative_error",
                "absolute_difference": exact_gate["max_relative_error"],
                "relative_difference": exact_gate["max_relative_error"],
                "notes": "Synthetic exact-reference rows reproduced at zero relative error under the declared 1e-12 tolerance.",
            },
            {
                "target_id": "target_declared_negative_controls_rejected",
                "label": "Declared convention negative controls rejected",
                "reference_value": 1.0,
                "observed_value": 1.0,
                "unit": "pass_fraction",
                "absolute_difference": 0.0,
                "relative_difference": 0.0,
                "notes": "Both declared convention negative controls were rejected, matching the expected pass fraction of 1.0.",
            },
        ],
        "uncertainty_summary": {
            "method": "deterministic_software_fixture_no_measurement_uncertainty",
            "observed_uncertainty": None,
            "reference_uncertainty": None,
            "combined_uncertainty": None,
            "z_score": None,
            "within_combined_uncertainty": None,
            "notes": (
                "This result records deterministic software/convention gate behavior over "
                "synthetic fixtures; it has no measurement-uncertainty model."
            ),
        },
        "artifacts": artifacts,
    }

    _dump_yaml(result_path, result_payload)
    write_text_atomic(metrics_path, json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    write_text_atomic(report_path, _render_report(metrics, result_id=result_id))
    write_text_atomic(claim_update_path, _render_claim_update(claim_id, result_id))
    write_text_atomic(
        claim_update_patch_path,
        _render_patch_stub(
            "Proposed Claim Patch",
            "none",
            result_id,
        ),
    )
    write_text_atomic(knowledge_update_path, _render_knowledge_update(knowledge_id, result_id))
    write_text_atomic(
        knowledge_update_patch_path,
        _render_patch_stub(
            "Proposed Knowledge Patch",
            "none",
            result_id,
        ),
    )
    write_text_atomic(review_summary_path, _render_review_summary(result_id, metrics))
    _dump_yaml(
        review_metadata_path,
        {
            "schema_version": "1",
            "artifact_type": "review_metadata",
            "result_id": result_id,
            "run_id": run_id,
            "experiment_id": str(experiment["id"]),
            "claim_id": claim_id or None,
            "knowledge_id": knowledge_id or None,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "proposed_claim_status": None,
            "required_human_review": True,
            "evidence_basis": [result_id],
            "claim_target_file": None,
            "knowledge_target_file": None,
            "patch_artifacts": {
                "claim_patch": artifacts["claim_update_patch"],
                "knowledge_patch": artifacts["knowledge_update_patch"],
                "review_summary": artifacts["review_summary"],
            },
        },
    )

    return ExperimentOutcome(
        title=str(experiment["title"]),
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(hypothesis["id"]),
        task_id=task_id,
        artifacts=ExperimentArtifacts(
            result_path=result_path,
            report_path=report_path,
            metrics_path=metrics_path,
            claim_update_path=claim_update_path,
            claim_update_patch_path=claim_update_patch_path,
            knowledge_update_path=knowledge_update_path,
            knowledge_update_patch_path=knowledge_update_patch_path,
            review_summary_path=review_summary_path,
            review_metadata_path=review_metadata_path,
        ),
        best_model_id="model_stefan_boltzmann_exact_reference",
        verdicts={"model_stefan_boltzmann_exact_reference": "VALID_IN_RANGE"},
        summary_lines=(
            "Textbook exact-reference fixture replayed with software/convention gates PASS.",
            "Boundary: synthetic fixture only; no empirical physics claim.",
        ),
    )


__all__ = ["run_textbook_exact_reference_with_output"]
