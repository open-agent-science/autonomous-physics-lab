from __future__ import annotations

from pathlib import Path

from physics_lab.registry.mission_freshness import validate_mission_freshness


def _write_task(
    root: Path,
    *,
    task_id: str,
    title: str,
    status: str,
    task_type: str = "documentation",
) -> None:
    (root / "tasks").mkdir(parents=True, exist_ok=True)
    (root / "tasks" / f"{task_id}-example.yaml").write_text(
        "\n".join(
            [
                f"id: {task_id}",
                f'title: "{title}"',
                f"type: {task_type}",
                f"status: {status}",
                "difficulty: medium",
                "priority: high",
                "",
                "input:",
                "  mode: workflow",
                '  related_domain: "maintainer_review"',
                "  related_objects: []",
                f'  planning_context: "{title}"',
                "",
                "requirements:",
                '  - "Keep work deterministic"',
                "",
                "accepted_outputs:",
                '  - "docs/example.md"',
                "",
                "validation:",
                "  commands:",
                '    - "python3 -m physics_lab.cli validate-repo ."',
                "",
                "can_be_done_by:",
                "  - human",
                "  - codex",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _write_current_missions(
    root: Path,
    *,
    support_task_id: str = "TASK-0001",
    include_curator_cycle: bool = True,
    mission_title: str = "Nuclear Mass Surface",
) -> None:
    (root / "missions").mkdir(parents=True, exist_ok=True)
    lines = [
        "default_mode: research",
        'updated: "2026-05-14"',
    ]
    if include_curator_cycle:
        lines.extend(
            [
                "curator_cycle:",
                "  decision: updated",
                '  updated: "2026-05-14"',
                '  source: "TASK-0243"',
                '  note: "Mission metadata refreshed after generated view sync."',
            ]
        )
    lines.extend(
        [
            "missions:",
            "  - id: nuclear-mass-surface",
            f'    title: "{mission_title}"',
            "    rank: 1",
            "    actions:",
            "      - id: choose-live-task",
            '        label: "Choose live candidate"',
            "        mode: research",
            "        recommended: true",
            "support_actions:",
            "  - id: docs-sync",
            '    label: "Docs sync"',
            f"    task_id: {support_task_id}",
            "maintainer_actions: []",
        ]
    )
    (root / "missions" / "current.yaml").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def _write_current_missions_doc(root: Path, *, title: str = "Nuclear Mass Surface") -> None:
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "current-missions.md").write_text(
        "\n".join(
            [
                "# Current Missions",
                "",
                "## Recommended Mission Now",
                "",
                f"**{title}** is the current flagship validation mission.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_validate_mission_freshness_accepts_current_ready_references(tmp_path: Path) -> None:
    _write_task(tmp_path, task_id="TASK-0001", title="Docs sync", status="READY")
    _write_current_missions(tmp_path)
    _write_current_missions_doc(tmp_path)

    issues = validate_mission_freshness(tmp_path)

    assert issues == ()


def test_validate_mission_freshness_flags_done_support_action(tmp_path: Path) -> None:
    _write_task(tmp_path, task_id="TASK-0001", title="Old docs sync", status="DONE")
    _write_current_missions(tmp_path)
    _write_current_missions_doc(tmp_path)

    issues = validate_mission_freshness(tmp_path)

    assert any(issue.code == "mission_stale_task_reference" for issue in issues)


def test_validate_mission_freshness_flags_missing_curator_cycle_and_title_drift(
    tmp_path: Path,
) -> None:
    _write_task(tmp_path, task_id="TASK-0001", title="Docs sync", status="READY")
    _write_current_missions(tmp_path, include_curator_cycle=False, mission_title="Mission A")
    _write_current_missions_doc(tmp_path, title="Mission B")

    issues = validate_mission_freshness(tmp_path)

    assert any(issue.code == "mission_missing_curator_cycle" for issue in issues)
    assert any(issue.code == "mission_flagship_mismatch" for issue in issues)
