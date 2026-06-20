"""Strict scientific-memory integrity checks for repository validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.validation import validate_document


RANGE_LANGUAGE_MARKERS = (
    "valid only",
    "tested range",
    "configured range",
    "range-limited",
    "within the tested",
    "within the sampled",
    "in scope",
    "linear, unforced",
)
STRICT_DONE_TASK_TYPES_WITHOUT_RESULTS = {
    "agent_workflow",
    "artifact_schema",
    "code_quality_refactor",
    "evidence_policy",
    "knowledge_update",
    "repository_validation",
    "repository_hardening",
    "research_quality_gate",
    "research_infrastructure",
    "research_protocol",
    "reproducibility",
    "release_preparation",
    "release_prep",
    "release_review",
    "repo_architecture",
    "review_workflow",
    "benchmark_planning",
    "contributor_experience",
    "contributor_validation",
    "contributor_workflow",
    "contributor_pilot",
    "developer_infrastructure",
    "maintainer_workflow",
    "maintainer_tooling",
    "numerical_audit",
    "documentation",
    "physics_reference",
    "scientific_governance",
    "scientific_audit",
    "scientific_benchmark",
    "scientific_falsification",
    "scientific_result_publication",
    "negative_result_memory",
    "benchmark_protocol",
    "ci_infrastructure",
    "ci_optimization",
    "campaign_scaffold",
    "campaign_status_refresh",
    "claim_review",
    "dataset_workflow",
    "physics_dataset_extension",
    "scientific_dataset",
    "scientific_dataset_schema",
    "scientific_campaign",
    "scientific_communication",
    "scientific_visualization",
    "scientific_safety_review",
    "scientific_tooling",
    "scientific_workflow",
    "scientific_validation",
    "schema_extension",
    "scoring_design",
    "snapshot_tooling",
    "test_infrastructure",
    "tooling_fix",
    "thought_experiment_planning",
    "scientific_microtask_execution",
    "workflow_pilot",
    "workflow_protocol",
    "workflow_hardening",
    "validation",
    "validation_infrastructure",
    "autonomous_research_pilot",
}


@dataclass(frozen=True)
class ScientificMemoryIssue:
    """Strict scientific-memory validation issue."""

    severity: str
    code: str
    message: str
    path: str | None = None


def collect_scientific_memory_integrity_issues(
    *,
    hypotheses: list[tuple[Path, dict[str, Any]]],
    tasks: list[tuple[Path, dict[str, Any]]],
    claims: list[tuple[Path, dict[str, Any]]],
    knowledge_files: list[tuple[Path, dict[str, Any]]],
    example_configs: list[tuple[Path, dict[str, Any]]],
    results: list[tuple[Path, dict[str, Any]]],
    root_path: Path,
) -> list[ScientificMemoryIssue]:
    """Collect strict integrity issues for result, claim, task, and knowledge memory."""
    issues: list[ScientificMemoryIssue] = []
    results_by_id = {payload["result_id"]: payload for _, payload in results}
    referenced_result_ids = {
        result_id
        for _, payload in hypotheses
        for result_id in payload["evidence"].get("results", [])
    } | {
        result_id
        for _, payload in claims
        for result_id in payload["evidence"]["results"]
    }
    result_task_ids = {str(payload["task_id"]) for _, payload in results}

    for result_path, result_payload in results:
        issues.extend(
            _required_run_artifact_issues(
                result_path,
                result_payload,
                root_path=root_path,
            )
        )
        result_id = str(result_payload["result_id"])
        if result_id not in referenced_result_ids:
            issues.append(
                _issue(
                    "WARNING",
                    "orphan_result",
                    "Result artifact is not referenced by any hypothesis or claim evidence.",
                    path=result_path,
                    root=root_path,
                )
            )

    for claim_path, claim_payload in claims:
        referenced_results = [
            results_by_id[result_id]
            for result_id in claim_payload["evidence"]["results"]
            if result_id in results_by_id
        ]
        issues.extend(
            _claim_status_issues(
                claim_path,
                claim_payload,
                referenced_results=referenced_results,
                root_path=root_path,
            )
        )

    for task_path, task_payload in tasks:
        task_id = str(task_payload["id"])
        task_status = str(task_payload["status"])
        task_type = str(task_payload["type"])
        if (
            task_status == "DONE"
            and task_id not in result_task_ids
            and task_type not in STRICT_DONE_TASK_TYPES_WITHOUT_RESULTS
            and not _task_has_committed_prediction_output(task_payload, root_path=root_path)
            and not _task_declares_result_artifact_not_required(task_payload)
        ):
            issues.append(
                _issue(
                    "WARNING",
                    "done_task_without_result",
                    "DONE task does not have a linked result artifact and is not on the documented exception list.",
                    path=task_path,
                    root=root_path,
                )
            )

    for knowledge_path, knowledge_payload in knowledge_files:
        linked = knowledge_payload["linked_objects"]
        if not any(linked.values()):
            issues.append(
                _issue(
                    "WARNING",
                    "knowledge_without_links",
                    "Knowledge note has no linked objects.",
                    path=knowledge_path,
                    root=root_path,
                )
            )

    for example_path, example_payload in example_configs:
        if example_payload.get("config_kind") in {
            "nuclear_prediction_variant_factory",
            "nuclear_prediction_synthetic_reveal",
            "quantum_size_effects_baseline",
            "textbook_wien_exact_reference_fixture",
        }:
            continue
        result_root = (example_path.parent / example_payload["result_root"]).resolve()
        expected_run_dir = result_root / str(example_payload["run_id"])
        canonical_result = expected_run_dir / "result.yaml"
        if not canonical_result.exists():
            issues.append(
                _issue(
                    "ERROR",
                    "missing_canonical_result",
                    "Example config points to a run directory without canonical result.yaml.",
                    path=example_path,
                    root=root_path,
                )
            )

    return issues


def _task_has_committed_prediction_output(
    task_payload: dict[str, Any], *, root_path: Path
) -> bool:
    """Return true when a DONE task points at a committed PRED artifact."""
    for output in task_payload.get("accepted_outputs", []):
        if not isinstance(output, str):
            continue
        output_path = Path(output)
        if (
            output_path.parts
            and output_path.parts[0] == "prediction_registry"
            and output_path.name.startswith("PRED-")
            and output_path.suffix == ".yaml"
            and (root_path / output_path).is_file()
        ):
            return True
    return False


def _task_declares_result_artifact_not_required(task_payload: dict[str, Any]) -> bool:
    """Return true when a task explicitly documents why no RESULT is expected."""
    policy = task_payload.get("result_artifact_policy")
    if not isinstance(policy, dict):
        return False
    if policy.get("required") is not False:
        return False
    reason = str(policy.get("reason") or "").strip()
    return bool(reason)


def _task_links_result_artifact(
    task_payload: dict[str, Any], *, root_path: Path
) -> bool:
    """Return true when an accepted output points at a committed result.yaml."""
    for output in task_payload.get("accepted_outputs", []):
        if not isinstance(output, str):
            continue
        output_path = Path(output)
        if (
            output_path.parts
            and output_path.parts[0] == "results"
            and output_path.name == "result.yaml"
            and (root_path / output_path).is_file()
        ):
            return True
    return False


def result_artifact_policy_advice(
    task_payload: dict[str, Any], *, root_path: Path
) -> str | None:
    """Return shift-left advice when a task is at risk of `done_task_without_result`.

    Mirrors the DONE-time rule (type not on the no-result exemption list, no
    committed PRED output, no linked ``results/.../result.yaml``, and no
    ``result_artifact_policy``) without scanning the whole results tree, so
    closeout and PR helpers can warn *before* a task is set ``DONE`` rather than
    only when strict validation runs at closeout. Returns ``None`` when the task
    is already fine.
    """
    task_type = str(task_payload.get("type") or "")
    if task_type in STRICT_DONE_TASK_TYPES_WITHOUT_RESULTS:
        return None
    if _task_declares_result_artifact_not_required(task_payload):
        return None
    if _task_has_committed_prediction_output(task_payload, root_path=root_path):
        return None
    if _task_links_result_artifact(task_payload, root_path=root_path):
        return None
    return (
        f"Task type '{task_type}' is not on the no-result exemption list and the "
        "task declares no result_artifact_policy. If this task produces no RESULT "
        "or PRED artifact, add a result_artifact_policy block (required: false, "
        "reason: ...) before setting it DONE, or strict closeout validation will "
        "warn (done_task_without_result). See docs/agent-task-protocol.md."
    )


def _required_run_artifact_issues(
    result_path: Path,
    payload: dict[str, Any],
    *,
    root_path: Path,
) -> list[ScientificMemoryIssue]:
    issues: list[ScientificMemoryIssue] = []
    run_dir = result_path.parent
    required_paths = {
        "result.yaml": run_dir / "result.yaml",
        "metrics.json": run_dir / "metrics.json",
        "report.md": run_dir / "report.md",
        "claim_update.md": run_dir / "claim_update.md",
        "claim_update.patch.md": run_dir / "claim_update.patch.md",
        "knowledge_update.md": run_dir / "knowledge_update.md",
        "knowledge_update.patch.md": run_dir / "knowledge_update.patch.md",
        "review_summary.md": run_dir / "review_summary.md",
        "review_metadata.yaml": run_dir / "review_metadata.yaml",
        "inputs/config.yaml": run_dir / "inputs" / "config.yaml",
        "inputs/experiment.yaml": run_dir / "inputs" / "experiment.yaml",
        "inputs/hypothesis.yaml": run_dir / "inputs" / "hypothesis.yaml",
        "inputs/task.yaml": run_dir / "inputs" / "task.yaml",
    }
    for label, required_path in required_paths.items():
        if not required_path.exists():
            issues.append(
                _issue(
                    "ERROR",
                    "missing_run_artifact",
                    f"Missing required run artifact: {label}",
                    path=result_path,
                    root=root_path,
                )
            )

    review_metadata_path = run_dir / "review_metadata.yaml"
    if review_metadata_path.exists():
        try:
            review_metadata_data = yaml.safe_load(
                review_metadata_path.read_text(encoding="utf-8")
            )
            validate_document(review_metadata_data, "review_metadata", review_metadata_path)
        except Exception as exc:
            issues.append(
                _issue(
                    "ERROR",
                    "invalid_review_metadata",
                    f"review_metadata.yaml failed schema validation: {exc}",
                    path=result_path,
                    root=root_path,
                )
            )

    expected_artifact_paths = {
        "report": _relative_path(run_dir / "report.md", root_path),
        "metrics": _relative_path(run_dir / "metrics.json", root_path),
        "claim_update": _relative_path(run_dir / "claim_update.md", root_path),
        "claim_update_patch": _relative_path(run_dir / "claim_update.patch.md", root_path),
        "knowledge_update": _relative_path(run_dir / "knowledge_update.md", root_path),
        "knowledge_update_patch": _relative_path(run_dir / "knowledge_update.patch.md", root_path),
        "review_summary": _relative_path(run_dir / "review_summary.md", root_path),
        "review_metadata": _relative_path(run_dir / "review_metadata.yaml", root_path),
    }
    for artifact_name, expected_path in expected_artifact_paths.items():
        actual_path = str(payload["artifacts"].get(artifact_name, ""))
        if actual_path != expected_path:
            issues.append(
                _issue(
                    "ERROR",
                    "noncanonical_artifact_path",
                    f"{artifact_name} should point to {expected_path}, not {actual_path or 'missing value'}",
                    path=result_path,
                    root=root_path,
                )
            )

    expected_input_paths = {
        "config": _relative_path(run_dir / "inputs" / "config.yaml", root_path),
        "experiment": _relative_path(run_dir / "inputs" / "experiment.yaml", root_path),
        "hypothesis": _relative_path(run_dir / "inputs" / "hypothesis.yaml", root_path),
        "task": _relative_path(run_dir / "inputs" / "task.yaml", root_path),
    }
    for artifact_name, expected_path in expected_input_paths.items():
        actual_path = str(payload["input_file_hashes"].get(artifact_name, {}).get("path", ""))
        if actual_path != expected_path:
            issues.append(
                _issue(
                    "ERROR",
                    "noncanonical_input_snapshot",
                    f"{artifact_name} hash should point to immutable run snapshot {expected_path}, not {actual_path or 'missing value'}",
                    path=result_path,
                    root=root_path,
                )
            )
    return issues


def _claim_status_issues(
    claim_path: Path,
    claim_payload: dict[str, Any],
    *,
    referenced_results: list[dict[str, Any]],
    root_path: Path,
) -> list[ScientificMemoryIssue]:
    issues: list[ScientificMemoryIssue] = []
    claim_status = str(claim_payload["status"])
    verification_all_pass = all(bool(result["verification"]["passed"]) for result in referenced_results)
    has_range_limited_result = any(
        str(result["best_verdict"]) == "VALID_IN_RANGE" for result in referenced_results
    )
    scope_text = str(claim_payload["scope"])
    body_text = str(claim_payload["body"])
    combined_text = f"{scope_text}\n{body_text}".lower()

    if claim_status == "PARTIALLY_SUPPORTED":
        if not referenced_results:
            issues.append(
                _issue(
                    "ERROR",
                    "claim_without_results",
                    "PARTIALLY_SUPPORTED claim must reference at least one result.",
                    path=claim_path,
                    root=root_path,
                )
            )
        if not verification_all_pass:
            issues.append(
                _issue(
                    "ERROR",
                    "claim_failed_verification",
                    "PARTIALLY_SUPPORTED claim references result evidence with failing verification checks.",
                    path=claim_path,
                    root=root_path,
                )
            )
        if has_range_limited_result and not any(marker in combined_text for marker in RANGE_LANGUAGE_MARKERS):
            issues.append(
                _issue(
                    "ERROR",
                    "claim_missing_range_language",
                    "PARTIALLY_SUPPORTED claim with range-limited evidence must describe scope explicitly.",
                    path=claim_path,
                    root=root_path,
                )
            )

    if claim_status == "DRAFT" and referenced_results and verification_all_pass:
        issues.append(
            _issue(
                "INFO",
                "draft_with_passing_evidence",
                "Claim remains DRAFT despite passing referenced evidence; human review may still be appropriate.",
                path=claim_path,
                root=root_path,
            )
        )

    return issues


def _issue(
    severity: str,
    code: str,
    message: str,
    *,
    path: Path | str | None = None,
    root: Path | None = None,
) -> ScientificMemoryIssue:
    normalized_path: str | None = None
    if path is not None:
        if isinstance(path, Path):
            normalized_path = _relative_path(path, root or path.parent)
        else:
            normalized_path = path
    return ScientificMemoryIssue(
        severity=severity,
        code=code,
        message=message,
        path=normalized_path,
    )


def _relative_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())
