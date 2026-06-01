from __future__ import annotations

from pathlib import Path

from physics_lab.registry.task_validation_plan import build_task_validation_plan


def _write_task(root: Path) -> None:
    tasks = root / "tasks"
    tasks.mkdir()
    (tasks / "TASK-9999-example.yaml").write_text(
        "\n".join(
            [
                "id: TASK-9999",
                'title: "Example"',
                "type: maintainer_workflow",
                "status: READY",
                "difficulty: low",
                "priority: low",
                "input:",
                "  mode: workflow",
                "  related_objects:",
                '    - "tests/test_example.py"',
                '  planning_context: "Test task"',
                "requirements:",
                '  - "Test planner"',
                "accepted_outputs:",
                '  - "Planner report"',
                "validation:",
                "  commands:",
                '    - "python3 -m pytest tests/test_example.py"',
                "can_be_done_by:",
                "  - codex",
            ]
        ),
        encoding="utf-8",
    )


def test_narrow_docs_diff_keeps_parallel_fast_lane_optional(tmp_path: Path) -> None:
    _write_task(tmp_path)

    plan = build_task_validation_plan(
        tmp_path,
        "TASK-9999",
        changed_files=("docs/testing.md", "tasks/TASK-9999-example.yaml"),
        system="Windows",
    )

    assert plan.fast_lane_recommended is False
    assert plan.windows_runtime_probe_recommended is True
    assert plan.task_commands == ("python3 -m pytest tests/test_example.py",)
    assert plan.validation_layers[2].startswith("resource_sensitive:")
    assert plan.validation_layers[-1].startswith("full_repo:")
    assert any("serial full-suite" in note for note in plan.notes)


def test_runtime_diff_recommends_parallel_fast_lane(tmp_path: Path) -> None:
    _write_task(tmp_path)

    plan = build_task_validation_plan(
        tmp_path,
        "TASK-9999",
        changed_files=("physics_lab/workflows/pendulum.py",),
        system="Linux",
    )

    assert plan.fast_lane_recommended is True
    assert plan.windows_runtime_probe_recommended is False
    assert "validate_fast.py" in plan.validation_layers[1]
    assert any("parallel fast lane" in note for note in plan.notes)
