from __future__ import annotations

from pathlib import Path

from physics_lab.registry.scientific_memory_integrity import (
    collect_scientific_memory_integrity_issues,
    result_artifact_policy_advice,
)


def test_policy_advice_flags_non_exempt_task_without_policy(tmp_path: Path) -> None:
    advice = result_artifact_policy_advice(
        {"id": "TASK-A", "type": "tooling_reliability"}, root_path=tmp_path
    )
    assert advice is not None
    assert "result_artifact_policy" in advice


def test_policy_advice_silent_for_exempt_type(tmp_path: Path) -> None:
    assert (
        result_artifact_policy_advice(
            {"id": "TASK-B", "type": "tooling_fix"}, root_path=tmp_path
        )
        is None
    )


def test_policy_advice_silent_when_policy_declared(tmp_path: Path) -> None:
    payload = {
        "id": "TASK-C",
        "type": "tooling_reliability",
        "result_artifact_policy": {"required": False, "reason": "no result expected"},
    }
    assert result_artifact_policy_advice(payload, root_path=tmp_path) is None


def test_policy_advice_silent_when_pred_artifact_linked(tmp_path: Path) -> None:
    pred = tmp_path / "prediction_registry" / "nuclear_masses" / "PRED-0001.yaml"
    pred.parent.mkdir(parents=True)
    pred.write_text("prediction_id: PRED-0001\n", encoding="utf-8")
    payload = {
        "id": "TASK-D",
        "type": "tooling_reliability",
        "accepted_outputs": ["prediction_registry/nuclear_masses/PRED-0001.yaml"],
    }
    assert result_artifact_policy_advice(payload, root_path=tmp_path) is None


def test_policy_advice_silent_when_result_artifact_linked(tmp_path: Path) -> None:
    result = tmp_path / "results" / "EXP-0001" / "RUN-0001" / "result.yaml"
    result.parent.mkdir(parents=True)
    result.write_text("result_id: RESULT-0001\n", encoding="utf-8")
    payload = {
        "id": "TASK-E",
        "type": "scientific_benchmark",
        "accepted_outputs": ["results/EXP-0001/RUN-0001/result.yaml"],
    }
    assert result_artifact_policy_advice(payload, root_path=tmp_path) is None


def test_scientific_memory_integrity_reports_orphan_result(tmp_path: Path) -> None:
    result_path = tmp_path / "results" / "EXP-TEST" / "RUN-TEST" / "result.yaml"
    result_path.parent.mkdir(parents=True)
    result_payload = {
        "result_id": "RESULT-TEST",
        "task_id": "TASK-TEST",
        "artifacts": {},
        "input_file_hashes": {},
    }

    issues = collect_scientific_memory_integrity_issues(
        hypotheses=[],
        tasks=[],
        claims=[],
        knowledge_files=[],
        example_configs=[],
        results=[(result_path, result_payload)],
        root_path=tmp_path,
    )

    assert any(issue.code == "orphan_result" for issue in issues)
    assert any(issue.code == "missing_run_artifact" for issue in issues)


def test_scientific_memory_integrity_reports_draft_claim_with_passing_evidence(
    tmp_path: Path,
) -> None:
    claim_path = tmp_path / "claims" / "CLAIM-TEST.md"
    result_path = tmp_path / "results" / "EXP-TEST" / "RUN-TEST" / "result.yaml"
    claim_payload = {
        "status": "DRAFT",
        "scope": "Configured range only.",
        "body": "Draft claim body.",
        "evidence": {"results": ["RESULT-TEST"]},
    }
    result_payload = {
        "result_id": "RESULT-TEST",
        "task_id": "TASK-TEST",
        "best_verdict": "VALID",
        "verification": {"passed": True},
        "artifacts": {},
        "input_file_hashes": {},
    }

    issues = collect_scientific_memory_integrity_issues(
        hypotheses=[],
        tasks=[],
        claims=[(claim_path, claim_payload)],
        knowledge_files=[],
        example_configs=[],
        results=[(result_path, result_payload)],
        root_path=tmp_path,
    )

    assert any(issue.code == "draft_with_passing_evidence" for issue in issues)


def test_scientific_memory_integrity_skips_factory_example_configs(
    tmp_path: Path,
) -> None:
    example_path = tmp_path / "examples" / "factory.yaml"
    example_payload = {
        "config_kind": "nuclear_prediction_variant_factory",
    }

    issues = collect_scientific_memory_integrity_issues(
        hypotheses=[],
        tasks=[],
        claims=[],
        knowledge_files=[],
        example_configs=[(example_path, example_payload)],
        results=[],
        root_path=tmp_path,
    )

    assert not any(issue.code == "missing_canonical_result" for issue in issues)


def test_scientific_memory_integrity_skips_quantum_sandbox_config(
    tmp_path: Path,
) -> None:
    example_path = tmp_path / "examples" / "quantum.yaml"
    example_payload = {
        "config_kind": "quantum_size_effects_baseline",
    }

    issues = collect_scientific_memory_integrity_issues(
        hypotheses=[],
        tasks=[],
        claims=[],
        knowledge_files=[],
        example_configs=[(example_path, example_payload)],
        results=[],
        root_path=tmp_path,
    )

    assert not any(issue.code == "missing_canonical_result" for issue in issues)


def test_scientific_memory_integrity_allows_done_tooling_tasks_without_results(
    tmp_path: Path,
) -> None:
    tasks = [
        (
            tmp_path / "tasks" / "TASK-TOOL.yaml",
            {"id": "TASK-TOOL", "status": "DONE", "type": "scientific_tooling"},
        ),
        (
            tmp_path / "tasks" / "TASK-TEST.yaml",
            {"id": "TASK-TEST", "status": "DONE", "type": "test_infrastructure"},
        ),
        (
            tmp_path / "tasks" / "TASK-FALSIFIER.yaml",
            {"id": "TASK-FALSIFIER", "status": "DONE", "type": "scientific_falsification"},
        ),
        (
            tmp_path / "tasks" / "TASK-CI.yaml",
            {"id": "TASK-CI", "status": "DONE", "type": "ci_optimization"},
        ),
        (
            tmp_path / "tasks" / "TASK-DEV-INFRA.yaml",
            {"id": "TASK-DEV-INFRA", "status": "DONE", "type": "developer_infrastructure"},
        ),
        (
            tmp_path / "tasks" / "TASK-SCI-COMM.yaml",
            {"id": "TASK-SCI-COMM", "status": "DONE", "type": "scientific_communication"},
        ),
        (
            tmp_path / "tasks" / "TASK-SCI-BENCHMARK.yaml",
            {"id": "TASK-SCI-BENCHMARK", "status": "DONE", "type": "scientific_benchmark"},
        ),
        (
            tmp_path / "tasks" / "TASK-TOOLING-FIX.yaml",
            {"id": "TASK-TOOLING-FIX", "status": "DONE", "type": "tooling_fix"},
        ),
        (
            tmp_path / "tasks" / "TASK-SNAPSHOT-TOOLING.yaml",
            {"id": "TASK-SNAPSHOT-TOOLING", "status": "DONE", "type": "snapshot_tooling"},
        ),
        (
            tmp_path / "tasks" / "TASK-DATASET-SCHEMA.yaml",
            {"id": "TASK-DATASET-SCHEMA", "status": "DONE", "type": "scientific_dataset_schema"},
        ),
        (
            tmp_path / "tasks" / "TASK-VALIDATION-INFRA.yaml",
            {
                "id": "TASK-VALIDATION-INFRA",
                "status": "DONE",
                "type": "validation_infrastructure",
            },
        ),
        (
            tmp_path / "tasks" / "TASK-WORKFLOW-PROTOCOL.yaml",
            {"id": "TASK-WORKFLOW-PROTOCOL", "status": "DONE", "type": "workflow_protocol"},
        ),
        (
            tmp_path / "tasks" / "TASK-CLAIM-REVIEW.yaml",
            {"id": "TASK-CLAIM-REVIEW", "status": "DONE", "type": "claim_review"},
        ),
        (
            tmp_path / "tasks" / "TASK-CAMPAIGN-STATUS.yaml",
            {
                "id": "TASK-CAMPAIGN-STATUS",
                "status": "DONE",
                "type": "campaign_status_refresh",
            },
        ),
        (
            tmp_path / "tasks" / "TASK-ARTIFACT-SCHEMA.yaml",
            {"id": "TASK-ARTIFACT-SCHEMA", "status": "DONE", "type": "artifact_schema"},
        ),
        (
            tmp_path / "tasks" / "TASK-MAINTAINER-TOOLING.yaml",
            {"id": "TASK-MAINTAINER-TOOLING", "status": "DONE", "type": "maintainer_tooling"},
        ),
        (
            tmp_path / "tasks" / "TASK-REPO-ARCHITECTURE.yaml",
            {"id": "TASK-REPO-ARCHITECTURE", "status": "DONE", "type": "repo_architecture"},
        ),
        (
            tmp_path / "tasks" / "TASK-REPOSITORY-HARDENING.yaml",
            {
                "id": "TASK-REPOSITORY-HARDENING",
                "status": "DONE",
                "type": "repository_hardening",
            },
        ),
        (
            tmp_path / "tasks" / "TASK-WORKFLOW-HARDENING.yaml",
            {
                "id": "TASK-WORKFLOW-HARDENING",
                "status": "DONE",
                "type": "workflow_hardening",
            },
        ),
    ]

    issues = collect_scientific_memory_integrity_issues(
        hypotheses=[],
        tasks=tasks,
        claims=[],
        knowledge_files=[],
        example_configs=[],
        results=[],
        root_path=tmp_path,
    )

    assert not any(issue.code == "done_task_without_result" for issue in issues)


def test_scientific_memory_integrity_allows_explicit_no_result_policy(
    tmp_path: Path,
) -> None:
    tasks = [
        (
            tmp_path / "tasks" / "TASK-REPLAY.yaml",
            {
                "id": "TASK-REPLAY",
                "status": "DONE",
                "type": "scientific_replay_validation",
                "result_artifact_policy": {
                    "required": False,
                    "reason": "Gate B replay updates an existing result artifact.",
                    "evidence": ["results/EXP-0013/RUN-0001/result.yaml"],
                },
            },
        ),
    ]

    issues = collect_scientific_memory_integrity_issues(
        hypotheses=[],
        tasks=tasks,
        claims=[],
        knowledge_files=[],
        example_configs=[],
        results=[],
        root_path=tmp_path,
    )

    assert not any(issue.code == "done_task_without_result" for issue in issues)


def test_scientific_memory_integrity_allows_done_prediction_tasks_with_pred_artifact(
    tmp_path: Path,
) -> None:
    prediction_path = (
        tmp_path / "prediction_registry" / "exoplanet_mass_radius" / "PRED-0001.yaml"
    )
    prediction_path.parent.mkdir(parents=True)
    prediction_path.write_text("prediction_id: PRED-0001\n", encoding="utf-8")
    tasks = [
        (
            tmp_path / "tasks" / "TASK-PREDICTION.yaml",
            {
                "id": "TASK-PREDICTION",
                "status": "DONE",
                "type": "prediction_registry",
                "accepted_outputs": [
                    "prediction_registry/exoplanet_mass_radius/PRED-0001.yaml",
                ],
            },
        ),
    ]

    issues = collect_scientific_memory_integrity_issues(
        hypotheses=[],
        tasks=tasks,
        claims=[],
        knowledge_files=[],
        example_configs=[],
        results=[],
        root_path=tmp_path,
    )

    assert not any(issue.code == "done_task_without_result" for issue in issues)


def test_scientific_memory_integrity_warns_when_prediction_task_lacks_pred_artifact(
    tmp_path: Path,
) -> None:
    tasks = [
        (
            tmp_path / "tasks" / "TASK-PREDICTION.yaml",
            {
                "id": "TASK-PREDICTION",
                "status": "DONE",
                "type": "prediction_registry",
                "accepted_outputs": [
                    "prediction_registry/exoplanet_mass_radius/PRED-0001.yaml",
                ],
            },
        ),
    ]

    issues = collect_scientific_memory_integrity_issues(
        hypotheses=[],
        tasks=tasks,
        claims=[],
        knowledge_files=[],
        example_configs=[],
        results=[],
        root_path=tmp_path,
    )

    assert any(issue.code == "done_task_without_result" for issue in issues)
