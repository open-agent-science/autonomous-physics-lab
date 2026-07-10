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


def _schema_valid_task_payload(
    *, closeout: str | None = None, closeout_review_reason: str | None = None
) -> dict:
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
    if closeout_review_reason is not None:
        payload["closeout_review_reason"] = closeout_review_reason
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


def test_task_schema_accepts_closeout_review_reason() -> None:
    schema = _task_schema()

    jsonschema.validate(
        instance=_schema_valid_task_payload(
            closeout="review",
            closeout_review_reason="Result-bearing task; maintainer closeout required.",
        ),
        schema=schema,
    )

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            instance=_schema_valid_task_payload(
                closeout="review",
                closeout_review_reason="",
            ),
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


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _prediction_schema() -> dict:
    schema_path = (
        _repo_root() / "physics_lab" / "schemas" / "prediction.schema.json"
    )
    return json.loads(schema_path.read_text(encoding="utf-8"))


def test_prediction_registry_kind_routing_per_domain() -> None:
    from physics_lab.registry import infer_kind_from_path

    assert (
        infer_kind_from_path("prediction_registry/nuclear_masses/PRED-0001.yaml")
        == "nuclear_mass_prediction"
    )
    assert (
        infer_kind_from_path("prediction_registry/radio_transients/PRED-0001.yaml")
        == "prediction"
    )
    assert (
        infer_kind_from_path("prediction_registry/exoplanet_mass_radius/PRED-0001.yaml")
        == "prediction"
    )
    assert (
        infer_kind_from_path("prediction_registry/some_future_domain/PRED-0002.yaml")
        == "prediction"
    )
    assert infer_kind_from_path("prediction_registry/PRED-0009.yaml") == "prediction"


def test_generic_prediction_schema_rejects_maintainer_placeholders() -> None:
    import yaml

    entry_path = (
        _repo_root() / "prediction_registry" / "exoplanet_mass_radius" / "PRED-0001.yaml"
    )
    entry = yaml.safe_load(entry_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(_prediction_schema())

    assert list(validator.iter_errors(entry)) == []

    staged = json.loads(json.dumps(entry))
    staged["registered_at_utc"] = "SET_BY_MAINTAINER_PREDICTION_FREEZE_DECISION"
    staged["source_state"]["git_commit"] = "SET_TO_APPROVED_FREEZE_COMMIT"
    failing_paths = {
        "/".join(str(part) for part in error.path)
        for error in validator.iter_errors(staged)
    }
    assert "registered_at_utc" in failing_paths
    assert "source_state/git_commit" in failing_paths


def test_repository_pattern_covers_all_prediction_registry_domains() -> None:
    registry_dir = _repo_root() / "prediction_registry"
    matched = sorted(
        path.relative_to(_repo_root()).as_posix()
        for path in registry_dir.glob(repository.PATTERNS["prediction_registry"])
    )

    assert "prediction_registry/exoplanet_mass_radius/PRED-0001.yaml" in matched
    assert any(entry.startswith("prediction_registry/nuclear_masses/") for entry in matched)
