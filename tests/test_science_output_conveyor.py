from __future__ import annotations

from pathlib import Path

import yaml

from physics_lab.registry.science_output_conveyor import (
    build_science_output_conveyor_report,
    render_science_output_conveyor_markdown,
    science_output_conveyor_json,
)


def _write_task(
    root: Path,
    task_id: str,
    *,
    status: str,
    task_type: str = "scientific_validation",
    domain: str = "test_surface",
    priority: str = "high",
    difficulty: str = "medium",
) -> None:
    task_dir = root / "tasks"
    task_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "id": task_id,
        "title": f"{task_id} test task",
        "type": task_type,
        "status": status,
        "difficulty": difficulty,
        "priority": priority,
        "input": {
            "mode": "workflow",
            "related_domain": domain,
            "related_objects": ["tests"],
            "planning_context": "Test task for conveyor report.",
        },
        "requirements": ["Keep this test task bounded."],
        "accepted_outputs": ["test output"],
        "can_be_done_by": ["codex"],
    }
    (task_dir / f"{task_id}-test-task.yaml").write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )


def _write_result(root: Path) -> None:
    result_dir = root / "results" / "EXP-9999" / "RUN-0001"
    result_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "result_id": "RESULT-9999",
        "run_id": "RUN-0001",
        "experiment_id": "EXP-9999",
        "title": "Conveyor Test Result",
        "hypothesis_id": "HYP-9999",
        "task_id": "TASK-9001",
        "code_reference": "tests/test_science_output_conveyor.py",
        "limitations": ["Synthetic result for tests."],
        "engine_version": "0.1.0",
        "generated_at": "2026-05-25T00:00:00+00:00",
        "command": "pytest conveyor",
        "input_file_hashes": {
            "config": {"path": "config.yaml", "sha256": "a" * 64},
            "experiment": {"path": "experiment.yaml", "sha256": "b" * 64},
            "hypothesis": {"path": "hypothesis.yaml", "sha256": "c" * 64},
            "task": {"path": "task.yaml", "sha256": "d" * 64},
        },
        "git_commit": None,
        "best_verdict": "PARTIALLY_VALID",
        "comparison_summary": [
            {
                "target_id": "target_test",
                "label": "synthetic target",
                "reference_value": 1.0,
                "observed_value": 1.0,
                "unit": None,
                "absolute_difference": 0.0,
                "relative_difference": 0.0,
            }
        ],
        "uncertainty_summary": {
            "method": "synthetic",
            "observed_uncertainty": None,
            "reference_uncertainty": None,
            "combined_uncertainty": None,
            "z_score": None,
            "within_combined_uncertainty": None,
        },
        "verification": {
            "passed": True,
            "checks": [
                {
                    "name": "synthetic_check",
                    "status": "PASS",
                    "details": "Synthetic check passed.",
                    "metrics": {"rows": 1},
                }
            ],
        },
        "artifacts": {
            "report": "report.md",
            "metrics": "metrics.json",
            "claim_update": "claim_update.md",
            "claim_update_patch": "claim_update.patch.md",
            "knowledge_update": "knowledge_update.md",
            "knowledge_update_patch": "knowledge_update.patch.md",
            "review_summary": "review_summary.md",
            "review_metadata": "review_metadata.yaml",
        },
    }
    (result_dir / "result.yaml").write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )


def _write_agent_run(root: Path) -> None:
    run_dir = root / "agent_runs" / "AGENT-RUN-9999"
    run_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "id": "AGENT-RUN-9999",
        "campaign_profile_id": "test_surface",
        "task_id": "TASK-9002",
        "verdict": "SANDBOX_PASS",
        "promotion_boundary": {
            "claim_promotion_allowed": False,
        },
    }
    (run_dir / "agent_run.yaml").write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )


def _write_review(root: Path) -> None:
    review_dir = root / "docs" / "reviews"
    review_dir.mkdir(parents=True, exist_ok=True)
    (review_dir / "test-blocker-review.md").write_text(
        "# Test Blocker Review\n\n## Decision\n\nBLOCKED by source blocker.\n",
        encoding="utf-8",
    )


def test_conveyor_reports_ready_and_blocked_task_health(tmp_path: Path) -> None:
    _write_task(tmp_path, "TASK-9001", status="READY", domain="surface_a")
    _write_task(tmp_path, "TASK-9002", status="READY", domain="surface_b")
    _write_task(tmp_path, "TASK-9003", status="BLOCKED", domain="surface_c")
    _write_task(tmp_path, "TASK-9004", status="DONE", domain="surface_c")

    report = build_science_output_conveyor_report(tmp_path)

    assert report.ready_science_task_count == 2
    assert report.task_queue_needed is True
    assert report.ready_science_surfaces == ("surface_a", "surface_b")
    assert [item.task_id for item in report.blocked_lane_reasons] == ["TASK-9003"]
    assert report.blocked_lane_reasons[0].notes
    assert [item.task_id for item in report.recent_task_transitions] == ["TASK-9004"]


def test_conveyor_detects_result_candidates_and_reviews(tmp_path: Path) -> None:
    _write_task(tmp_path, "TASK-9001", status="READY")
    _write_result(tmp_path)
    _write_agent_run(tmp_path)
    _write_review(tmp_path)

    report = build_science_output_conveyor_report(tmp_path)
    json_report = science_output_conveyor_json(report)
    markdown = render_science_output_conveyor_markdown(report)

    assert "RESULT-9999 / TASK-9001" in report.result_candidates[0]
    assert any("AGENT-RUN-9999" in item for item in report.result_candidates)
    assert report.blocker_reviews[0].path == "docs/reviews/test-blocker-review.md"
    assert '"task_queue_needed": true' in json_report
    assert "## Overclaim Risk" in markdown
    assert "Advisory only" in markdown
