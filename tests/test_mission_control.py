from __future__ import annotations

import json
import textwrap
from pathlib import Path
import subprocess
import sys

from physics_lab.registry.mission_control import (
    load_current_missions,
    mission_json,
    render_agent_prompt,
    render_human_mission,
    select_mission,
    task_candidates,
)


def _write_missions(root: Path) -> None:
    mission_dir = root / "missions"
    mission_dir.mkdir()
    (mission_dir / "current.yaml").write_text(
        textwrap.dedent(
            """\
            default_mode: research
            policy:
              summary: "Research first."
            global_forbidden:
              - "no claim promotion"
            modes:
              research:
                label: "Research Mode"
                description: "Default research lane."
              support:
                label: "Support Mode"
                description: "Support lane."
              audit:
                label: "Audit Mode"
                description: "Audit lane."
              maintainer:
                label: "Maintainer Mode"
                description: "Maintainer lane."
            missions:
              - id: nuclear
                title: Nuclear
                rank: 1
                why_now:
                  - "best current campaign"
                forbidden:
                  - "no discovery wording"
                actions:
                  - id: split
                    label: "Run split replay"
                    mode: research
                    task_id: TASK-0002
                    priority: high
                    difficulty: medium
                    recommended: true
                  - id: audit-run
                    label: "Audit run"
                    mode: audit
                    priority: high
            support_actions:
              - id: docs
                label: "Clean docs"
                task_id: TASK-0001
            maintainer_actions:
              - id: review-pr
                label: "Review PR"
                command: "python3 scripts/apl_review_pr.py --pr <number>"
            """
        ),
        encoding="utf-8",
    )


def _write_task(root: Path, *, task_id: str, title: str, status: str, task_type: str, priority: str) -> None:
    tasks_dir = root / "tasks"
    tasks_dir.mkdir(exist_ok=True)
    (tasks_dir / f"{task_id}-example.yaml").write_text(
        textwrap.dedent(
            f"""\
            id: {task_id}
            title: "{title}"
            type: {task_type}
            status: {status}
            difficulty: medium
            priority: {priority}
            input:
              mode: workflow
              related_objects: []
              planning_context: "Mission candidate test task"
            requirements:
              - "Keep work reviewable"
            accepted_outputs:
              - "docs/example.md"
            validation:
              commands:
                - "python3 -m physics_lab.cli validate-repo ."
            can_be_done_by:
              - human
              - codex
            """
        ),
        encoding="utf-8",
    )


def test_select_mission_defaults_to_research(tmp_path: Path) -> None:
    _write_missions(tmp_path)
    payload = load_current_missions(tmp_path)

    selection = select_mission(payload)

    assert selection.mode == "research"
    assert selection.mission is not None
    assert selection.mission["id"] == "nuclear"
    assert selection.action is not None
    assert selection.action["id"] == "split"
    assert selection.action["task_id"] == "TASK-0002"


def test_mission_json_includes_guardrails(tmp_path: Path) -> None:
    _write_missions(tmp_path)
    payload = load_current_missions(tmp_path)

    rendered = json.loads(mission_json(payload))

    assert rendered["default_mode"] == "research"
    assert rendered["recommended"]["mission"] == "nuclear"
    assert rendered["recommended"]["task_id"] == "TASK-0002"
    assert rendered["recommended"]["forbidden"] == ["no discovery wording"]
    assert rendered["global_forbidden"] == ["no claim promotion"]


def test_mission_json_omits_inactive_configured_actions(tmp_path: Path) -> None:
    _write_missions(tmp_path)
    mission_path = tmp_path / "missions" / "current.yaml"
    text = mission_path.read_text(encoding="utf-8")
    mission_path.write_text(
        text.replace(
            "                  - id: audit-run\n"
            "                    label: \"Audit run\"\n"
            "                    mode: audit\n"
            "                    priority: high\n",
            "                  - id: done-replay\n"
            "                    label: \"Done replay\"\n"
            "                    mode: research\n"
            "                    status: done\n"
            "                    priority: high\n"
            "                  - id: blocked-replay\n"
            "                    label: \"Blocked replay\"\n"
            "                    mode: research\n"
            "                    status: blocked\n"
            "                    priority: high\n"
            "                  - id: audit-run\n"
            "                    label: \"Audit run\"\n"
            "                    mode: audit\n"
            "                    priority: high\n",
        ),
        encoding="utf-8",
    )
    payload = load_current_missions(tmp_path)

    rendered = json.loads(mission_json(payload))

    actions = [action["action"] for action in rendered["alternatives"]]
    assert "done-replay" not in actions
    assert "blocked-replay" not in actions


def test_mission_json_includes_live_task_candidates(tmp_path: Path) -> None:
    _write_missions(tmp_path)
    _write_task(
        tmp_path,
        task_id="TASK-0003",
        title="Replay scientific candidate",
        status="READY",
        task_type="scientific_audit",
        priority="high",
    )
    _write_task(
        tmp_path,
        task_id="TASK-0004",
        title="Support docs cleanup",
        status="READY",
        task_type="documentation",
        priority="medium",
    )
    payload = load_current_missions(tmp_path)

    rendered = json.loads(mission_json(payload, root=tmp_path))

    candidate_ids = [candidate["task_id"] for candidate in rendered["live_task_candidates"]]
    assert candidate_ids == ["TASK-0003", "TASK-0004"]
    assert rendered["live_task_candidates"][0]["mode"] == "research"
    assert rendered["live_task_candidates"][1]["mode"] == "support"
    assert "parallel_agents" in rendered["parallel_work_policy"]


def test_task_candidates_support_parallel_safe_options(tmp_path: Path) -> None:
    _write_task(
        tmp_path,
        task_id="TASK-0005",
        title="Hard replay",
        status="READY",
        task_type="scientific_audit",
        priority="high",
    )
    _write_task(
        tmp_path,
        task_id="TASK-0006",
        title="Already in review",
        status="REVIEW_READY",
        task_type="scientific_audit",
        priority="high",
    )

    candidates = task_candidates(tmp_path, mode="research")

    assert [candidate.task_id for candidate in candidates] == ["TASK-0005"]
    assert "separate branch/worktree" in candidates[0].parallel_hint


def test_task_candidates_do_not_offer_review_ready_without_ready_tasks(tmp_path: Path) -> None:
    _write_task(
        tmp_path,
        task_id="TASK-0006",
        title="Already in review",
        status="REVIEW_READY",
        task_type="scientific_audit",
        priority="high",
    )

    candidates = task_candidates(tmp_path, mode="research")

    assert candidates == ()


def test_mission_json_marks_review_ready_as_non_executor_work(tmp_path: Path) -> None:
    _write_missions(tmp_path)
    _write_task(
        tmp_path,
        task_id="TASK-0006",
        title="Already in review",
        status="REVIEW_READY",
        task_type="scientific_audit",
        priority="high",
    )
    payload = load_current_missions(tmp_path)

    rendered = json.loads(mission_json(payload, root=tmp_path))

    assert rendered["live_task_candidates"] == []
    assert "Only READY tasks" in rendered["task_visibility_policy"]["executor_modes"]
    assert "REVIEW_READY tasks are hidden" in rendered["task_visibility_policy"]["review_ready"]


def test_render_human_support_mode_uses_support_actions(tmp_path: Path) -> None:
    _write_missions(tmp_path)
    payload = load_current_missions(tmp_path)

    rendered = render_human_mission(payload, "support")

    assert "Support Mode" in rendered
    assert "Clean docs" in rendered
    assert "TASK-0001" in rendered


def test_render_human_mission_shows_live_candidates(tmp_path: Path) -> None:
    _write_missions(tmp_path)
    _write_task(
        tmp_path,
        task_id="TASK-0007",
        title="Scientific replay",
        status="READY",
        task_type="scientific_audit",
        priority="high",
    )
    payload = load_current_missions(tmp_path)

    rendered = render_human_mission(payload, root=tmp_path)

    assert "Live task candidates from task registry" in rendered
    assert "TASK-0007" in rendered
    assert "separate branches or worktrees" in rendered


def test_render_agent_prompt_mentions_full_pr_loop(tmp_path: Path) -> None:
    _write_missions(tmp_path)
    payload = load_current_missions(tmp_path)

    rendered = render_agent_prompt(payload, root=tmp_path)

    assert "Agent First Research Mode" in rendered
    assert "Use canonical task TASK-0002" in rendered
    assert "prepare a PR" in rendered
    assert "Do not promote claims" in rendered
    assert "separate branches or worktrees" in rendered
    assert "list only executable READY tasks" in rendered
    assert "Do not offer REVIEW_READY tasks" in rendered


def test_apl_mission_script_json_runs_from_repo_root() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/apl_mission.py", "--json"],
        check=True,
        capture_output=True,
        text=True,
    )

    rendered = json.loads(result.stdout)
    assert rendered["default_mode"] == "research"
    assert rendered["recommended"]["mission"] == "nuclear-mass-surface"
    assert "live_task_candidates" in rendered


def test_cli_mission_json_runs_from_repo_root() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "physics_lab.cli", "mission", "--json"],
        check=True,
        capture_output=True,
        text=True,
    )

    rendered = json.loads(result.stdout)
    assert rendered["selected_mode"] == "research"
    assert rendered["recommended"]["action"] == "nuclear-validation-queue"
    assert rendered["recommended"]["task_id"] is None
    assert "parallel_work_policy" in rendered
    assert rendered["live_task_candidates"]
    nuclear_validation_queue_ids = {
        "TASK-0200",
        "TASK-0201",
        "TASK-0202",
        "TASK-0203",
    }
    assert (
        rendered["live_task_candidates"][0]["task_id"]
        in nuclear_validation_queue_ids
    )
    assert rendered["live_task_candidates"][0]["mode"] == "research"
