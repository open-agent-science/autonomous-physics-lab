"""Workflow adapter for the Stellar M-L high-mass DEBCat transfer RESULT-0024.

Regenerates the canonical ``results/EXP-0017/RUN-0001/`` transfer-benchmark
artifact from committed CC-BY-4.0 DEBCat rows and the published input snapshots
via ``physics-lab run`` so the Gate B independent-replay validator
(:mod:`physics_lab.registry.agent_replay_validation`) can re-run the same
supported command shape and compare numeric fields (TASK-0917).

This adapter is a thin bridge, not a second implementation. All scientific
numbers come from the frozen deterministic engine
(:func:`physics_lab.engines.stellar_ml_high_mass_transfer.compute_transfer_metrics`)
and are packaged by the shared writer
(:func:`scripts.run_stellar_ml_high_mass_transfer.write_result_package`) that the
standalone script already uses, so the workflow route and the original
standalone route produce a byte-identical scientific payload. The only fields
this route changes are ``command`` (the supported ``physics-lab run`` shape) and
``code_reference`` (this adapter module).

The frozen RESULT-0022 relation is NOT refit, the committed DEBCat rows are NOT
edited, RESULT-0022 is NOT touched, and no CLAIM/PRED/KNOW artifact is promoted.
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

WORKFLOW_CODE_REFERENCE = "physics_lab/workflows/stellar_ml_high_mass_transfer.py"


def run_stellar_ml_high_mass_transfer_with_output(
    config_path: str | Path,
    output_dir: str | Path | None = None,
) -> ExperimentOutcome:
    """Regenerate the Stellar M-L high-mass DEBCat transfer RESULT-0024.

    Reads the frozen engine metrics and the published RESULT-0024 input
    snapshots, then writes the full result package (result.yaml plus siblings)
    to the resolved run directory. With ``output_dir`` set (Gate B replay), the
    package is written under a disposable directory instead of the committed
    canonical path, so the committed artifact is never overwritten by a replay.
    """
    # Import here to avoid importing the scripts package at module import time
    # (the workflow package must stay importable without the scripts path).
    from scripts.run_stellar_ml_high_mass_transfer import (
        RESULT_ID,
        RESULT_RUN_ID,
        _build_metrics,
        write_result_package,
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
    if run_id != RESULT_RUN_ID or result_id != RESULT_ID:
        raise ValueError(
            "Config run_id/result_id must match the published RESULT-0024 package: "
            f"{run_id}/{result_id} != {RESULT_RUN_ID}/{RESULT_ID}"
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

    metrics = _build_metrics()
    write_result_package(
        metrics,
        run_dir,
        command=command,
        code_reference=WORKFLOW_CODE_REFERENCE,
    )

    prim = metrics["primary_high_mass_main_sequence_holdout"]
    run_directory = run_dir
    return ExperimentOutcome(
        title=str(experiment["title"]),
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(hypothesis["id"]),
        task_id=task_id,
        artifacts=ExperimentArtifacts(
            result_path=run_directory / "result.yaml",
            report_path=run_directory / "report.md",
            metrics_path=run_directory / "metrics.json",
            claim_update_path=run_directory / "claim_update.md",
            claim_update_patch_path=run_directory / "claim_update.patch.md",
            knowledge_update_path=run_directory / "knowledge_update.md",
            knowledge_update_patch_path=run_directory / "knowledge_update.patch.md",
            review_summary_path=run_directory / "review_summary.md",
            review_metadata_path=run_directory / "review_metadata.yaml",
        ),
        best_model_id="model_result0022_frozen_alpha_transfer",
        verdicts={"model_result0022_frozen_alpha_transfer": "VALID_IN_RANGE"},
        summary_lines=(
            "Stellar M-L high-mass DEBCat transfer regenerated; Gate B replayable via physics-lab run.",
            (
                "Boundary: same-source high-mass transfer of the frozen RESULT-0022 relation "
                f"(primary holdout MAE {prim['frozen_relation_holdout_mae_dex']} dex); not a universal law."
            ),
        ),
    )


__all__ = ["run_stellar_ml_high_mass_transfer_with_output"]
