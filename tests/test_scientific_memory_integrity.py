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
