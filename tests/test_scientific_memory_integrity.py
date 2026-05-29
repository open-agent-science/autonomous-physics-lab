from __future__ import annotations

from pathlib import Path

from physics_lab.registry.scientific_memory_integrity import (
    collect_scientific_memory_integrity_issues,
)


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
            tmp_path / "tasks" / "TASK-TOOLING-FIX.yaml",
            {"id": "TASK-TOOLING-FIX", "status": "DONE", "type": "tooling_fix"},
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
