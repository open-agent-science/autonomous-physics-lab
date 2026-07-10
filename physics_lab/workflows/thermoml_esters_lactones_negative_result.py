"""Gate-B-safe workflow adapter for ThermoML RESULT-0028.

The adapter reuses the deterministic RESULT-0028 package writer and changes
only route metadata to the supported ``physics-lab run`` command shape. It
does not fetch ThermoML bytes, alter the five-row failed-family slice, refit
Joback, or change any scientific metric or verdict.
"""

from __future__ import annotations

from pathlib import Path

from physics_lab.registry.examples import load_example_config
from physics_lab.registry.experiments import load_experiment
from physics_lab.registry.hypotheses import load_hypothesis
from physics_lab.workflows.artifacts import (
    ExperimentArtifacts,
    ExperimentOutcome,
    find_repo_root,
    relative_or_absolute,
    resolve_path,
)

WORKFLOW_CODE_REFERENCE = (
    "physics_lab/workflows/thermoml_esters_lactones_negative_result.py"
)


def run_thermoml_esters_lactones_negative_result_with_output(
    config_path: str | Path,
    output_dir: str | Path | None = None,
) -> ExperimentOutcome:
    """Regenerate RESULT-0028 through the supported workflow command path."""
    from scripts.package_thermoml_esters_lactones_negative_result import (
        git_commit,
        write_package,
    )

    config_path = Path(config_path).resolve()
    config = load_example_config(config_path)
    experiment_path = resolve_path(config_path, config["experiment_path"])
    hypothesis_path = resolve_path(config_path, config["hypothesis_path"])
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
    if task_id != "TASK-0936" or run_id != "RUN-0002" or result_id != "RESULT-0028":
        raise ValueError(
            "Workflow config must preserve canonical RESULT-0028 identity: "
            f"{task_id}/{run_id}/{result_id}"
        )

    default_result_root = resolve_path(config_path, str(config["result_root"]))
    result_root = (
        Path(output_dir).resolve() / str(experiment["id"])
        if output_dir is not None
        else default_result_root
    )
    run_dir = result_root / run_id
    command_path = relative_or_absolute(config_path, repo_root)
    command = f"physics-lab run {command_path}"
    write_package(
        run_dir,
        commit=git_commit(),
        command=command,
        code_reference=WORKFLOW_CODE_REFERENCE,
    )

    return ExperimentOutcome(
        title=str(experiment["title"]),
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(hypothesis["id"]),
        task_id=task_id,
        artifacts=ExperimentArtifacts(
            result_path=run_dir / "result.yaml",
            report_path=run_dir / "report.md",
            metrics_path=run_dir / "metrics.json",
            claim_update_path=run_dir / "claim_update.md",
            claim_update_patch_path=run_dir / "claim_update.patch.md",
            knowledge_update_path=run_dir / "knowledge_update.md",
            knowledge_update_patch_path=run_dir / "knowledge_update.patch.md",
            review_summary_path=run_dir / "review_summary.md",
            review_metadata_path=run_dir / "review_metadata.yaml",
        ),
        best_model_id="model_joback_frozen_tb",
        verdicts={"model_joback_frozen_tb": "INVALID"},
        summary_lines=(
            "ThermoML RESULT-0028 negative/control package regenerated through a Gate-B-safe workflow.",
            "Boundary: committed five-row esters/lactones slice only; no refit, fetch, or claim promotion.",
        ),
    )


__all__ = ["run_thermoml_esters_lactones_negative_result_with_output"]
