from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from physics_lab.registry import repository


REPO_ROOT = Path(__file__).resolve().parents[1]


def _task_payload(
    *,
    status: str = "REVIEW_READY",
    commands: tuple[str, ...],
    accepted_outputs: tuple[str, ...] = ("review report",),
) -> dict:
    return {
        "id": "TASK-9999",
        "status": status,
        "validation": {"commands": list(commands)},
        "accepted_outputs": list(accepted_outputs),
    }


def _issues_for(tmp_path: Path, payload: dict) -> tuple[repository.ValidationIssue, ...]:
    task_path = tmp_path / "tasks" / "TASK-9999-example.yaml"
    return tuple(
        repository._strict_task_validation_command_path_issues(
            tasks=[(task_path, payload)],
            root_path=tmp_path,
        )
    )


def _schema_valid_task_payload(*, closeout: str | None = None) -> dict:
    payload = {
        "id": "TASK-9999",
        "title": "Closeout policy fixture",
        "type": "maintainer_workflow",
        "status": "READY",
        "difficulty": "low",
        "priority": "medium",
        "input": {
            "mode": "workflow",
            "related_objects": [],
            "planning_context": "fixture",
        },
        "requirements": ["fixture requirement"],
        "accepted_outputs": ["fixture output"],
        "validation": {"commands": ["python3 -m physics_lab.cli validate-repo ."]},
        "can_be_done_by": ["human"],
    }
    if closeout is not None:
        payload["closeout"] = closeout
    return payload


def _task_schema() -> dict:
    return json.loads((REPO_ROOT / "physics_lab/schemas/task.schema.json").read_text())


def test_task_schema_accepts_closeout_policy_values() -> None:
    schema = _task_schema()

    jsonschema.validate(instance=_schema_valid_task_payload(), schema=schema)
    jsonschema.validate(instance=_schema_valid_task_payload(closeout="auto"), schema=schema)
    jsonschema.validate(instance=_schema_valid_task_payload(closeout="review"), schema=schema)

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            instance=_schema_valid_task_payload(closeout="manual"),
            schema=schema,
        )


def test_task_validation_command_paths_accept_existing_repo_local_paths(
    tmp_path: Path,
) -> None:
    tests_dir = tmp_path / "tests"
    scripts_dir = tmp_path / "scripts"
    tests_dir.mkdir()
    scripts_dir.mkdir()
    (tests_dir / "test_example.py").write_text("def test_ok():\n    pass\n", encoding="utf-8")
    (scripts_dir / "run_example.py").write_text("print('ok')\n", encoding="utf-8")

    issues = _issues_for(
        tmp_path,
        _task_payload(
            commands=(
                "python3 -m pytest tests/test_example.py -q",
                "python3 scripts/run_example.py",
            )
        ),
    )

    assert issues == ()


def test_task_validation_command_paths_error_for_review_ready_missing_path(
    tmp_path: Path,
) -> None:
    issues = _issues_for(
        tmp_path,
        _task_payload(commands=("python3 -m pytest tests/test_missing.py -q",)),
    )

    assert len(issues) == 1
    assert issues[0].severity == "ERROR"
    assert issues[0].code == "missing_task_validation_command_path"
    assert "tests/test_missing.py" in issues[0].message


def test_task_validation_command_paths_info_for_ready_missing_path(
    tmp_path: Path,
) -> None:
    issues = _issues_for(
        tmp_path,
        _task_payload(
            status="READY",
            commands=("python3 -m pytest tests/test_missing.py -q",),
        ),
    )

    assert len(issues) == 1
    assert issues[0].severity == "INFO"


def test_task_validation_command_paths_ignore_non_paths_and_accepted_outputs(
    tmp_path: Path,
) -> None:
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "run_example.py").write_text("print('ok')\n", encoding="utf-8")

    issues = _issues_for(
        tmp_path,
        _task_payload(
            commands=(
                "python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings",
                "python3 scripts/run_example.py --output agent_runs/AGENT-RUN-9999/report.md",
            ),
            accepted_outputs=("agent_runs/AGENT-RUN-9999/report.md",),
        ),
    )

    assert issues == ()
