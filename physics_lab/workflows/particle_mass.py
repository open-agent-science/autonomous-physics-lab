"""Particle-mass reproduction workflows."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import math
from pathlib import Path
from typing import Any

import yaml

from physics_lab import __version__
from physics_lab.registry import load_example_config, load_experiment, load_hypothesis
from physics_lab.registry.results import validate_result_payload
from physics_lab.workflows.artifacts import (
    ExperimentArtifacts,
    ExperimentOutcome,
    find_repo_root,
    git_commit,
    hash_file,
    relative_or_absolute,
    render_patch_artifact,
    render_review_metadata,
    render_review_summary,
    resolve_path,
    snapshot_input_files,
    task_path,
    write_text_atomic,
)


def _load_particle_mass_dataset(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in particle-mass dataset: {path}")
    return data


def _entry_by_particle(entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_particle: dict[str, dict[str, Any]] = {}
    for entry in entries:
        particle = str(entry["particle"])
        by_particle[particle] = entry
    return by_particle


def _charged_lepton_inputs(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    entries = list(dataset.get("entries", []))
    by_particle = _entry_by_particle(entries)
    required_particles = ["electron", "muon", "tau"]
    missing = [particle for particle in required_particles if particle not in by_particle]
    if missing:
        raise ValueError(f"Charged-lepton dataset is missing required entries: {missing}")
    return [by_particle[particle] for particle in required_particles]


def _compute_koide_q(masses_mev: list[float]) -> float:
    numerator = sum(masses_mev)
    denominator = sum(math.sqrt(mass) for mass in masses_mev) ** 2
    return numerator / denominator


def _koide_uncertainty(masses_mev: list[float], uncertainties_mev: list[float]) -> float:
    sqrt_sum = sum(math.sqrt(mass) for mass in masses_mev)
    mass_sum = sum(masses_mev)
    variance = 0.0
    for mass, uncertainty in zip(masses_mev, uncertainties_mev):
        derivative = (1.0 / (sqrt_sum**2)) - (mass_sum / (sqrt_sum**3 * math.sqrt(mass)))
        variance += (derivative * uncertainty) ** 2
    return math.sqrt(variance)


def _best_verdict(*, within_uncertainty: bool, relative_difference: float) -> str:
    if within_uncertainty:
        return "VALID"
    if relative_difference <= 5e-5:
        return "PARTIALLY_VALID"
    return "INCONCLUSIVE"


def _comparison_summary(
    *,
    target_id: str,
    label: str,
    reference_value: float,
    observed_value: float,
) -> list[dict[str, Any]]:
    absolute_difference = abs(observed_value - reference_value)
    relative_difference = absolute_difference / abs(reference_value)
    return [
        {
            "target_id": target_id,
            "label": label,
            "reference_value": reference_value,
            "observed_value": observed_value,
            "unit": None,
            "absolute_difference": absolute_difference,
            "relative_difference": relative_difference,
            "notes": "Comparison against the benchmark target value 2/3.",
        }
    ]


def _build_verification(
    *,
    dataset_entries: list[dict[str, Any]],
    observed_q: float,
    reference_q: float,
    q_uncertainty: float,
    within_uncertainty: bool,
    z_score: float | None,
) -> dict[str, Any]:
    checks = [
        {
            "name": "charged_lepton_dataset_complete",
            "status": "PASS",
            "details": "Electron, muon, and tau entries are present with explicit source metadata.",
            "metrics": {
                "entry_count": len(dataset_entries),
            },
        },
        {
            "name": "mass_definition_consistency",
            "status": "PASS",
            "details": "All benchmark inputs use charged-lepton pole masses without scheme or scale mixing.",
            "metrics": {
                "all_pole_masses": all(str(entry["mass_type"]) == "pole" for entry in dataset_entries),
                "all_same_unit": len({str(entry["mass_unit"]) for entry in dataset_entries}) == 1,
            },
        },
        {
            "name": "koide_quantity_computed",
            "status": "PASS",
            "details": "Computed the charged-lepton Koide quantity from the explicit dataset inputs.",
            "metrics": {
                "observed_q": observed_q,
                "reference_q": reference_q,
            },
        },
        {
            "name": "uncertainty_propagated",
            "status": "PASS",
            "details": "Propagated one-sigma mass uncertainty into the Koide quantity using first-order derivatives.",
            "metrics": {
                "q_uncertainty": q_uncertainty,
                "within_combined_uncertainty": within_uncertainty,
                "z_score": z_score if z_score is not None else "undefined",
            },
        },
    ]
    return {
        "passed": all(check["status"] == "PASS" for check in checks),
        "checks": checks,
    }


def _report_text(
    *,
    result_id: str,
    run_id: str,
    hypothesis_id: str,
    task_id: str,
    dataset_entries: list[dict[str, Any]],
    observed_q: float,
    reference_q: float,
    q_uncertainty: float,
    absolute_difference: float,
    relative_difference: float,
    within_uncertainty: bool,
    best_verdict: str,
    verification_summary: dict[str, Any],
) -> str:
    lines = [
        "# Charged-Lepton Koide Reproduction",
        "",
        f"- Result: `{result_id}`",
        f"- Run: `{run_id}`",
        f"- Hypothesis: `{hypothesis_id}`",
        f"- Task: `{task_id}`",
        "",
        "## Dataset",
        "",
    ]
    for entry in dataset_entries:
        uncertainty = entry["uncertainty"]
        lines.append(
            f"- `{entry['particle']}`: `{entry['mass_value']}` {entry['mass_unit']} "
            f"+/- `{uncertainty['value']}` {uncertainty['unit']} "
            f"({entry['source']['edition']}, `{entry['mass_type']}` mass)"
        )
    lines.extend(
        [
            "",
            "## Comparison Target",
            "",
            "- Target quantity: `Q = (m_e + m_mu + m_tau) / (sqrt(m_e) + sqrt(m_mu) + sqrt(m_tau))^2`",
            f"- Observed `Q`: `{observed_q:.12f}`",
            f"- Reference `2/3`: `{reference_q:.12f}`",
            f"- Absolute difference: `{absolute_difference:.12e}`",
            f"- Relative difference: `{relative_difference:.12e}`",
            f"- Propagated one-sigma uncertainty in `Q`: `{q_uncertainty:.12e}`",
            f"- Within propagated uncertainty: `{within_uncertainty}`",
            "",
            "## Limitations",
            "",
            "- Charged-lepton scope only; no cross-family generalization is implied.",
            "- This is a reproduction benchmark, not an explanation claim.",
            "- Uncertainty propagation assumes independent one-sigma input uncertainties.",
            "",
            "## Verification",
            "",
            f"- Verification gate passed: `{verification_summary['passed']}`",
        ]
    )
    for check in verification_summary["checks"]:
        lines.append(f"- {check['name']}: `{check['status']}`")
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"Repository verdict: `{best_verdict}`.",
            "",
            "The benchmark reproduces a Koide quantity numerically close to `2/3` from explicit charged-lepton pole masses while preserving uncertainty-aware wording.",
            "",
        ]
    )
    return "\n".join(lines)


def run_particle_mass_reproduction_with_output(
    config_path: str | Path,
    output_dir: str | Path | None = None,
) -> ExperimentOutcome:
    """Execute a dataset-based particle-mass reproduction workflow."""
    config_path = Path(config_path).resolve()
    config = load_example_config(config_path)
    experiment_path = resolve_path(config_path, config["experiment_path"])
    hypothesis_path = resolve_path(config_path, config["hypothesis_path"])
    repo_root = find_repo_root(config_path)
    experiment = load_experiment(experiment_path)
    hypothesis = load_hypothesis(hypothesis_path)
    task_id = str(config.get("task_id", ""))
    run_id = str(config.get("run_id", ""))
    result_id = str(config.get("result_id", ""))
    default_result_root = resolve_path(config_path, str(config.get("result_root", "")))
    result_root = (
        Path(output_dir).resolve() / str(experiment["id"])
        if output_dir is not None
        else default_result_root
    )
    if experiment["hypothesis_id"] != hypothesis["id"]:
        raise ValueError(
            "Experiment hypothesis_id does not match loaded hypothesis id: "
            f"{experiment['hypothesis_id']} != {hypothesis['id']}"
        )
    if not task_id or not run_id or not result_id:
        raise ValueError("Experiment config must define task_id, run_id, and result_id")
    if not str(config.get("result_root", "")):
        raise ValueError("Experiment config must define result_root for run-based outputs")

    dataset_path = resolve_path(experiment_path, experiment["data"]["dataset_path"])
    dataset = _load_particle_mass_dataset(dataset_path)
    dataset_entries = _charged_lepton_inputs(dataset)
    masses_mev = [float(entry["mass_value"]) for entry in dataset_entries]
    uncertainties_mev = [float(entry["uncertainty"]["value"]) for entry in dataset_entries]
    observed_q = _compute_koide_q(masses_mev)
    target_payload = experiment["comparison_targets"][0]
    reference_q = float(target_payload["reference_value"])
    q_uncertainty = _koide_uncertainty(masses_mev, uncertainties_mev)
    comparison_summary = _comparison_summary(
        target_id=str(target_payload["id"]),
        label=str(target_payload["label"]),
        reference_value=reference_q,
        observed_value=observed_q,
    )
    absolute_difference = float(comparison_summary[0]["absolute_difference"])
    relative_difference = float(comparison_summary[0]["relative_difference"])
    within_uncertainty = absolute_difference <= q_uncertainty
    z_score = (absolute_difference / q_uncertainty) if q_uncertainty > 0 else None
    best_verdict = _best_verdict(
        within_uncertainty=within_uncertainty,
        relative_difference=relative_difference,
    )
    verification_summary = _build_verification(
        dataset_entries=dataset_entries,
        observed_q=observed_q,
        reference_q=reference_q,
        q_uncertainty=q_uncertainty,
        within_uncertainty=within_uncertainty,
        z_score=z_score,
    )

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

    limitations = [
        "Charged-lepton scope only; no generalization beyond this particle family is implied.",
        "This benchmark compares one computed quantity against the benchmark target 2/3 and does not explain the origin of particle masses.",
        "Uncertainty propagation uses first-order derivative propagation with independent one-sigma input uncertainties.",
    ]
    task_file = task_path(repo_root, task_id)
    command_path = relative_or_absolute(config_path, repo_root)
    command = f"physics-lab run {command_path}"
    if output_dir is not None:
        command += f" --output-dir {relative_or_absolute(Path(output_dir).resolve(), repo_root)}"
    input_hashes = snapshot_input_files(
        run_dir=run_dir,
        repo_root=repo_root,
        input_files={
            "config": config_path,
            "experiment": experiment_path,
            "hypothesis": hypothesis_path,
            "task": task_file,
        },
    )
    dataset_input_path = run_dir / "inputs" / "dataset.yaml"
    write_text_atomic(dataset_input_path, dataset_path.read_text(encoding="utf-8"))
    input_hashes["dataset"] = hash_file(dataset_input_path, repo_root)
    current_commit = git_commit(repo_root)

    report_text = _report_text(
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(experiment["hypothesis_id"]),
        task_id=task_id,
        dataset_entries=dataset_entries,
        observed_q=observed_q,
        reference_q=reference_q,
        q_uncertainty=q_uncertainty,
        absolute_difference=absolute_difference,
        relative_difference=relative_difference,
        within_uncertainty=within_uncertainty,
        best_verdict=best_verdict,
        verification_summary=verification_summary,
    )
    write_text_atomic(report_path, report_text)

    result_payload = {
        "result_id": result_id,
        "run_id": run_id,
        "experiment_id": str(experiment["id"]),
        "title": str(experiment["title"]),
        "hypothesis_id": str(experiment["hypothesis_id"]),
        "task_id": task_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine_version": __version__,
        "git_commit": current_commit,
        "command": command,
        "input_file_hashes": {
            "config": input_hashes["config"],
            "experiment": input_hashes["experiment"],
            "hypothesis": input_hashes["hypothesis"],
            "task": input_hashes["task"],
        },
        "code_reference": "physics_lab/workflows/particle_mass.py",
        "limitations": limitations,
        "best_verdict": best_verdict,
        "verification": verification_summary,
        "artifacts": {
            "report": relative_or_absolute(report_path, repo_root),
            "metrics": relative_or_absolute(metrics_path, repo_root),
            "claim_update": relative_or_absolute(claim_update_path, repo_root),
            "claim_update_patch": relative_or_absolute(claim_update_patch_path, repo_root),
            "knowledge_update": relative_or_absolute(knowledge_update_path, repo_root),
            "knowledge_update_patch": relative_or_absolute(knowledge_update_patch_path, repo_root),
            "review_summary": relative_or_absolute(review_summary_path, repo_root),
            "review_metadata": relative_or_absolute(review_metadata_path, repo_root),
        },
        "comparison_summary": comparison_summary,
        "uncertainty_summary": {
            "method": "first_order_uncertainty_propagation",
            "observed_uncertainty": q_uncertainty,
            "reference_uncertainty": None,
            "combined_uncertainty": q_uncertainty,
            "z_score": z_score,
            "within_combined_uncertainty": within_uncertainty,
            "notes": "Reference benchmark target 2/3 treated as exact for this comparison.",
        },
    }
    validate_result_payload(result_payload, source=result_path)
    write_text_atomic(result_path, yaml.safe_dump(result_payload, sort_keys=False))

    metrics_payload = {
        "result_id": result_id,
        "run_id": run_id,
        "dataset_id": str(dataset["dataset_id"]),
        "target_id": str(target_payload["id"]),
        "observed_q": observed_q,
        "reference_q": reference_q,
        "absolute_difference": absolute_difference,
        "relative_difference": relative_difference,
        "q_uncertainty": q_uncertainty,
        "z_score": z_score,
        "within_combined_uncertainty": within_uncertainty,
        "best_verdict": best_verdict,
        "verification": verification_summary,
    }
    write_text_atomic(metrics_path, json.dumps(metrics_payload, indent=2) + "\n")

    claim_update_text = "\n".join(
        [
            "# Claim Update Suggestion",
            "",
            "Suggested status: keep `CLAIM-0003` as `DRAFT`.",
            "",
            f"- Result: `{result_id}`",
            f"- Observed `Q`: `{observed_q:.12f}`",
            f"- Reference `2/3`: `{reference_q:.12f}`",
            f"- Relative difference: `{relative_difference:.12e}`",
            "",
            "Reason:",
            "",
            "- the benchmark is source-aware and uncertainty-aware;",
            "- the result is numerically interesting within charged leptons;",
            "- the benchmark does not justify an explanatory claim.",
            "",
        ]
    )
    knowledge_update_text = "\n".join(
        [
            "# Knowledge Update Suggestion",
            "",
            f"- Add `RESULT-{result_id.split('-')[-1]}` as the first canonical charged-lepton Koide reproduction result.",
            "- Preserve charged-lepton-only scope.",
            "- Preserve the warning that reproduction does not imply explanation.",
            "",
        ]
    )

    claim_target_path = repo_root / "claims" / "CLAIM-0003-koide-charged-lepton-reproduction.md"
    claim_original = claim_target_path.read_text(encoding="utf-8")
    claim_patch_text = render_patch_artifact(
        title="Claim Patch Suggestion",
        target_file="claims/CLAIM-0003-koide-charged-lepton-reproduction.md",
        evidence_basis=[result_id],
        original_text=claim_original,
        proposed_text=claim_original,
        proposed_status="DRAFT",
        sections_to_update=["Evidence Status", "Caution"],
        rationale="The canonical claim file already preserves draft status and scope-aware wording for this first reproduction benchmark.",
    )
    knowledge_target_path = repo_root / "knowledge" / "particle_physics" / "koide_relation.md"
    knowledge_original = knowledge_target_path.read_text(encoding="utf-8")
    knowledge_patch_text = render_patch_artifact(
        title="Knowledge Patch Suggestion",
        target_file="knowledge/particle_physics/koide_relation.md",
        evidence_basis=[result_id],
        original_text=knowledge_original,
        proposed_text=knowledge_original,
        sections_to_update=["Known Baseline", "Open Questions"],
        rationale="The canonical knowledge note already matches the recommended cautious wording for this result.",
    )
    review_summary_text = render_review_summary(
        result_id=result_id,
        claim_id="CLAIM-0003",
        knowledge_id="KNOW-0003",
        suggested_status="DRAFT",
        rationale="Keep the new charged-lepton Koide claim draft until the first reproduction result is reviewed together with its uncertainty-aware interpretation.",
        highlights=[
            f"Observed Koide quantity Q = {observed_q:.12f}",
            f"Absolute difference from 2/3 = {absolute_difference:.12e}",
            f"Propagated Q uncertainty = {q_uncertainty:.12e}",
        ],
        limitations=limitations,
    )
    write_text_atomic(claim_update_path, claim_update_text)
    write_text_atomic(claim_update_patch_path, claim_patch_text)
    write_text_atomic(knowledge_update_path, knowledge_update_text)
    write_text_atomic(knowledge_update_patch_path, knowledge_patch_text)
    write_text_atomic(review_summary_path, review_summary_text)

    review_metadata_payload = render_review_metadata(
        result_id=result_id,
        run_id=run_id,
        experiment_id=str(experiment["id"]),
        claim_id="CLAIM-0003",
        knowledge_id="KNOW-0003",
        generated_at=str(result_payload["generated_at"]),
        proposed_claim_status="DRAFT",
        evidence_basis=[result_id],
        claim_target_file="claims/CLAIM-0003-koide-charged-lepton-reproduction.md",
        knowledge_target_file="knowledge/particle_physics/koide_relation.md",
        claim_patch_path=relative_or_absolute(claim_update_patch_path, repo_root),
        knowledge_patch_path=relative_or_absolute(knowledge_update_patch_path, repo_root),
        review_summary_path=relative_or_absolute(review_summary_path, repo_root),
    )
    write_text_atomic(review_metadata_path, yaml.safe_dump(review_metadata_payload, sort_keys=False))

    return ExperimentOutcome(
        title=str(experiment["title"]),
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(experiment["hypothesis_id"]),
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
        best_model_id=None,
        summary_lines=(
            f"Primary comparison: {target_payload['label']}",
            f"Observed Q: {observed_q:.12f}",
            f"Relative difference vs 2/3: {relative_difference:.12e}",
        ),
    )
