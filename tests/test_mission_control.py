from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path
import subprocess
import sys

import yaml

from physics_lab.registry import mission_control
from physics_lab.registry.mission_control import (
    TaskAvailabilitySnapshot,
    collect_github_task_availability,
    load_current_missions,
    mission_json,
    ready_science_pool_health,
    render_agent_prompt,
    render_human_mission,
    render_onboarding_prompt,
    select_mission,
    task_candidates,
)


FROZEN_REPO_SNAPSHOT_PATTERNS = {
    "hardcoded current task id": re.compile(r"TASK-(?:0[5-9][0-9]{2}|[1-9][0-9]{3})"),
    "hardcoded project stage": re.compile(r"Stage:\s*v[0-9]"),
}


def test_registry_board_tests_do_not_freeze_live_repo_snapshots() -> None:
    """Keep mission/board/status tests tied to fixtures or live state, not today."""
    repo_root = Path(__file__).resolve().parents[1]
    scanned_files = (
        "tests/test_mission_control.py",
        "tests/test_pendulum.py",
        "tests/test_task_views.py",
    )
    offenders: list[str] = []
    for relative_path in scanned_files:
        path = repo_root / relative_path
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for label, pattern in FROZEN_REPO_SNAPSHOT_PATTERNS.items():
                if pattern.search(line):
                    offenders.append(f"{relative_path}:{line_number}: {label}")

    assert offenders == []


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


def _write_task(
    root: Path,
    *,
    task_id: str,
    title: str,
    status: str,
    task_type: str,
    priority: str,
    related_domain: str = "test_domain",
) -> None:
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
              related_domain: {related_domain}
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
    assert rendered["live_task_candidates"][0]["mode"] in {"research", "support"}
    assert rendered["live_task_candidates"][1]["mode"] == "support"
    assert rendered["live_task_candidates"][0]["estimated_time"] == "~5-10 min"
    assert "parallel_agents" in rendered["parallel_work_policy"]
    assert rendered["ready_science_pool_health"]["warning_only"] is True


def test_ready_science_pool_health_reports_warning_only_short_pool(tmp_path: Path) -> None:
    for index in range(7):
        _write_task(
            tmp_path,
            task_id=f"TASK-01{index:02d}",
            title=f"Research candidate {index}",
            status="READY",
            task_type="scientific_validation",
            priority="high",
            related_domain="surface_a" if index < 3 else "surface_b",
        )
    _write_task(
        tmp_path,
        task_id="TASK-0200",
        title="Support candidate",
        status="READY",
        task_type="documentation",
        priority="high",
        related_domain="support_surface",
    )

    health = ready_science_pool_health(tmp_path)

    assert health.minimum_ready_science_tasks == 12
    assert health.preferred_ready_science_tasks == 24
    assert health.target_active_surfaces == 6
    assert health.preferred_active_surfaces == 8
    assert health.max_ready_science_surface_share == 0.40
    assert health.ready_science_count == 7
    assert health.active_surfaces == ("surface_a", "surface_b")
    assert health.surface_task_counts == {"surface_a": 3, "surface_b": 4}
    assert health.below_minimum is True
    assert health.below_surface_target is True
    assert health.below_preferred_surface_target is True
    assert health.above_surface_concentration_target is True
    assert health.task_queue_needed is True
    assert health.warning_only is True


def test_ready_science_pool_health_accepts_minimum_across_six_surfaces(tmp_path: Path) -> None:
    for index, surface in enumerate(
        (
            "surface_a",
            "surface_a",
            "surface_a",
            "surface_b",
            "surface_b",
            "surface_b",
            "surface_c",
            "surface_c",
            "surface_d",
            "surface_d",
            "surface_e",
            "surface_f",
        )
    ):
        _write_task(
            tmp_path,
            task_id=f"TASK-02{index:02d}",
            title=f"Research candidate {index}",
            status="READY",
            task_type="scientific_validation",
            priority="high",
            related_domain=surface,
        )

    health = ready_science_pool_health(tmp_path)

    assert health.ready_science_count == 12
    assert health.active_surfaces == (
        "surface_a",
        "surface_b",
        "surface_c",
        "surface_d",
        "surface_e",
        "surface_f",
    )
    assert health.below_minimum is False
    assert health.below_surface_target is False
    assert health.below_preferred_surface_target is True
    assert health.above_surface_concentration_target is False
    assert health.task_queue_needed is True
    assert health.below_preferred is True


def test_ready_science_pool_health_accepts_preferred_target_across_surfaces(
    tmp_path: Path,
) -> None:
    surfaces = (
        "surface_a",
        "surface_a",
        "surface_a",
        "surface_b",
        "surface_b",
        "surface_b",
        "surface_c",
        "surface_c",
        "surface_c",
        "surface_d",
        "surface_d",
        "surface_d",
        "surface_e",
        "surface_e",
        "surface_e",
        "surface_f",
        "surface_f",
        "surface_f",
        "surface_g",
        "surface_g",
        "surface_g",
        "surface_h",
        "surface_h",
        "surface_h",
    )
    for index, surface in enumerate(surfaces):
        _write_task(
            tmp_path,
            task_id=f"TASK-04{index:02d}",
            title=f"Research candidate {index}",
            status="READY",
            task_type="scientific_validation",
            priority="high",
            related_domain=surface,
        )

    health = ready_science_pool_health(tmp_path)

    assert health.ready_science_count == 24
    assert health.below_minimum is False
    assert health.below_preferred is False
    assert health.below_surface_target is False
    assert health.below_preferred_surface_target is False
    assert health.above_surface_concentration_target is False
    assert health.task_queue_needed is False


def test_ready_science_pool_health_flags_same_surface_concentration(tmp_path: Path) -> None:
    surfaces = (
        "surface_a",
        "surface_a",
        "surface_a",
        "surface_a",
        "surface_b",
        "surface_b",
        "surface_c",
        "surface_c",
        "surface_d",
        "surface_d",
        "surface_e",
        "surface_f",
    )
    for index, surface in enumerate(surfaces):
        _write_task(
            tmp_path,
            task_id=f"TASK-03{index:02d}",
            title=f"Research candidate {index}",
            status="READY",
            task_type="scientific_validation",
            priority="high",
            related_domain=surface,
        )

    health = ready_science_pool_health(tmp_path)

    assert health.ready_science_count == 12
    assert health.below_minimum is False
    assert health.below_surface_target is False
    assert health.below_preferred_surface_target is True
    assert health.above_surface_concentration_target is False
    assert health.below_preferred is True
    assert health.task_queue_needed is True

    for offset in range(2):
        _write_task(
            tmp_path,
            task_id=f"TASK-039{offset}",
            title=f"Over-concentrated research candidate {offset}",
            status="READY",
            task_type="scientific_validation",
            priority="high",
            related_domain="surface_a",
        )

    concentrated = ready_science_pool_health(tmp_path)

    assert concentrated.ready_science_count == 14
    assert concentrated.surface_task_counts["surface_a"] == 6
    assert concentrated.above_surface_concentration_target is True
    assert concentrated.task_queue_needed is True


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


def test_task_candidates_omit_live_github_occupied_tasks(tmp_path: Path) -> None:
    for task_id in ("TASK-0005", "TASK-0006"):
        _write_task(
            tmp_path,
            task_id=task_id,
            title=f"Candidate {task_id}",
            status="READY",
            task_type="scientific_audit",
            priority="high",
        )

    candidates = task_candidates(
        tmp_path,
        mode="research",
        unavailable_task_ids=frozenset({"TASK-0005"}),
    )

    assert [candidate.task_id for candidate in candidates] == ["TASK-0006"]


def test_collect_github_task_availability_reports_open_claims_and_prs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    for task_id in ("TASK-0005", "TASK-0006", "TASK-0008"):
        _write_task(
            tmp_path,
            task_id=task_id,
            title=f"Ready candidate {task_id}",
            status="READY",
            task_type="scientific_audit",
            priority="high",
        )
    _write_task(
        tmp_path,
        task_id="TASK-0009",
        title="Already closed out",
        status="DONE",
        task_type="scientific_audit",
        priority="high",
    )
    responses = [
        subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps(
                [
                    {
                        "number": 10,
                        "title": "TASK-0005: open implementation",
                        "state": "OPEN",
                        "mergedAt": None,
                        "headRefName": "agent/roman/codex/task-0005-open",
                    },
                    {
                        "number": 11,
                        "title": "TASK-0006: merged implementation",
                        "state": "MERGED",
                        "mergedAt": "2026-06-01T00:00:00Z",
                        "headRefName": "agent/roman/codex/task-0006-merged",
                    },
                    {
                        "number": 12,
                        "title": "TASK-0007: closed replacement",
                        "state": "CLOSED",
                        "mergedAt": None,
                        "headRefName": "agent/roman/codex/task-0007-closed",
                    },
                    {
                        "number": 14,
                        "title": "TASK-0009: merged and closed out",
                        "state": "MERGED",
                        "mergedAt": "2026-06-01T00:00:00Z",
                        "headRefName": "agent/roman/codex/task-0009-done",
                    },
                ]
            ),
            stderr="",
        ),
        subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps(
                [
                    {
                        "number": 13,
                        "title": "Task claim: TASK-0008 claimed",
                        "body": "Task ID: TASK-0008",
                    }
                ]
            ),
            stderr="",
        ),
    ]
    monkeypatch.setattr(mission_control, "find_gh_path", lambda env=None: "gh")
    monkeypatch.setattr(
        mission_control.subprocess,
        "run",
        lambda *args, **kwargs: responses.pop(0),
    )

    snapshot = collect_github_task_availability(tmp_path, env={"PATH": ""})

    assert snapshot.checked is True
    assert snapshot.excluded_task_ids == ("TASK-0005", "TASK-0006", "TASK-0008")
    assert snapshot.reasons["TASK-0005"] == ("open PR #10",)
    assert snapshot.reasons["TASK-0006"] == ("merged PR #11 pending local closeout",)
    assert snapshot.reasons["TASK-0008"] == ("open claim #13",)
    assert "TASK-0007" not in snapshot.reasons
    assert "TASK-0009" not in snapshot.reasons


def test_collect_github_task_availability_degrades_on_known_proxy(
    tmp_path: Path,
    monkeypatch,
) -> None:
    def unexpected_run(*args, **kwargs):
        raise AssertionError("gh should not run without explicit proxy bypass")

    monkeypatch.setattr(mission_control.subprocess, "run", unexpected_run)

    snapshot = collect_github_task_availability(
        tmp_path,
        env={"HTTPS_PROXY": "http://127.0.0.1:9"},
    )

    assert snapshot.checked is False
    assert snapshot.source == "local_registry_only"
    assert "--ignore-suspicious-proxy" in snapshot.warnings[0]


def test_render_onboarding_prompt_omits_live_github_occupied_task(tmp_path: Path) -> None:
    _write_missions(tmp_path)
    for task_id in ("TASK-0007", "TASK-0008"):
        _write_task(
            tmp_path,
            task_id=task_id,
            title=f"Scientific replay {task_id}",
            status="READY",
            task_type="scientific_audit",
            priority="high",
        )
    payload = load_current_missions(tmp_path)
    availability = TaskAvailabilitySnapshot(
        checked=True,
        source="github",
        excluded_task_ids=("TASK-0007",),
        reasons={"TASK-0007": ("open PR #20",)},
        warnings=(),
    )

    rendered = render_onboarding_prompt(
        payload,
        root=tmp_path,
        availability=availability,
    )

    assert "TASK-0007" in rendered
    assert "omitted occupied or merged-pending-closeout tasks: TASK-0007" in rendered
    assert "- TASK-0007: Scientific replay TASK-0007" not in rendered
    assert "- TASK-0008: Scientific replay TASK-0008" in rendered


def test_task_candidates_shuffle_equal_rank_research_groups(tmp_path: Path, monkeypatch) -> None:
    class FakeRandomizer:
        def shuffle(self, items: list) -> None:
            items.reverse()

    monkeypatch.setattr(mission_control, "RANDOMIZER", FakeRandomizer())
    for task_id in ("TASK-0010", "TASK-0011", "TASK-0012"):
        _write_task(
            tmp_path,
            task_id=task_id,
            title=f"Research candidate {task_id}",
            status="READY",
            task_type="scientific_audit",
            priority="high",
        )
    _write_task(
        tmp_path,
        task_id="TASK-0013",
        title="Lower priority research candidate",
        status="READY",
        task_type="scientific_audit",
        priority="medium",
    )

    stable = task_candidates(tmp_path, mode="research", shuffle_equal_rank=False)
    shuffled = task_candidates(tmp_path, mode="research", shuffle_equal_rank=True)

    assert [candidate.task_id for candidate in stable] == [
        "TASK-0010",
        "TASK-0011",
        "TASK-0012",
        "TASK-0013",
    ]
    assert [candidate.task_id for candidate in shuffled] == [
        "TASK-0012",
        "TASK-0011",
        "TASK-0010",
        "TASK-0013",
    ]


def test_task_candidates_do_not_shuffle_support_mode_by_default(tmp_path: Path, monkeypatch) -> None:
    class FakeRandomizer:
        def shuffle(self, items: list) -> None:
            items.reverse()

    monkeypatch.setattr(mission_control, "RANDOMIZER", FakeRandomizer())
    _write_task(
        tmp_path,
        task_id="TASK-0014",
        title="Support docs A",
        status="READY",
        task_type="documentation",
        priority="high",
    )
    _write_task(
        tmp_path,
        task_id="TASK-0015",
        title="Support docs B",
        status="READY",
        task_type="documentation",
        priority="high",
    )

    candidates = task_candidates(tmp_path, mode="support")

    assert [candidate.task_id for candidate in candidates] == ["TASK-0014", "TASK-0015"]


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
    assert "~5-10 min" in rendered
    assert "separate branches or worktrees" in rendered


def test_render_agent_prompt_mentions_full_pr_loop(tmp_path: Path) -> None:
    _write_missions(tmp_path)
    payload = load_current_missions(tmp_path)

    rendered = render_agent_prompt(payload, root=tmp_path)

    assert "Agent First Research Mode" in rendered
    assert "Use canonical task TASK-0002" in rendered
    assert "Execute the full loop autonomously" in rendered
    assert "preserve all meaningful outcomes" in rendered
    assert "open a draft PR" in rendered
    assert "not a reason to stop before editing files" in rendered
    assert "commit only after the files are ready" in rendered
    assert "request permission/escalation" in rendered
    assert "GitHub/MCP tools" in rendered
    assert "Do not promote claims" in rendered
    assert "separate branches or worktrees" in rendered
    assert "list only executable READY tasks" in rendered
    assert "Do not offer REVIEW_READY tasks" in rendered


def test_render_onboarding_prompt_waits_for_user_choice(tmp_path: Path) -> None:
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

    rendered = render_onboarding_prompt(payload, root=tmp_path)

    assert "with onboarding" in rendered
    assert "Do not edit files yet" in rendered
    assert "wait for my choice" in rendered or "wait for the user's choice" in rendered
    assert "TASK-0007" in rendered
    assert "~5-10 min" in rendered
    assert "After the user chooses" in rendered
    assert "follow `docs/agent-task-protocol.md` end-to-end" in rendered
    assert "science-execution work over tooling" in rendered
    assert "macOS/Linux/WSL/Git Bash" in rendered
    assert "plain Windows shells" in rendered
    assert "git worktree add <path> -b <branch> origin/main" in rendered
    assert "finish the local work" in rendered
    assert "stop before editing files and report the blocker" not in rendered


def test_render_human_modes_keep_support_and_maintainer_explicit(tmp_path: Path) -> None:
    _write_missions(tmp_path)
    payload = load_current_missions(tmp_path)

    support = render_human_mission(payload, "support")
    maintainer = render_human_mission(payload, "maintainer")

    assert "Support Mode" in support
    assert "Clean docs" in support
    assert "Maintainer Mode" in maintainer
    assert "Review PR" in maintainer
    assert "python3 scripts/apl_mission.py --mode support" in support
    assert "python3 scripts/apl_mission.py --mode maintainer" in maintainer


def test_apl_mission_script_json_runs_from_repo_root() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/apl_mission.py", "--json"],
        check=True,
        capture_output=True,
        text=True,
    )

    rendered = json.loads(result.stdout)
    assert rendered["default_mode"] == "research"
    assert rendered["recommended"]["mission"] == "materials-property-residuals"
    assert "live_task_candidates" in rendered


def test_apl_mission_script_onboarding_runs_from_repo_root() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/apl_mission.py", "--output", "onboarding", "--github-availability", "off"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "with onboarding" in result.stdout
    assert "Do not edit files yet" in result.stdout
    assert "estimated time" in result.stdout
    assert "docs/result-promotion-protocol.md" in result.stdout


def test_apl_mission_script_legacy_onboarding_alias_runs_from_repo_root() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/apl_mission.py", "--onboarding", "--github-availability", "off"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "with onboarding" in result.stdout
    assert "Do not edit files yet" in result.stdout


def test_apl_mission_script_output_agent_runs_from_repo_root() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/apl_mission.py", "--output", "agent"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Agent First Research Mode" in result.stdout
    assert "Execute the full loop autonomously" in result.stdout
    assert "list only executable READY tasks" in result.stdout


def test_cli_mission_json_runs_from_repo_root() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "physics_lab.cli", "mission", "--json"],
        check=True,
        capture_output=True,
        text=True,
    )

    rendered = json.loads(result.stdout)
    payload = load_current_missions(Path(__file__).resolve().parents[1])
    selection = select_mission(payload)
    assert selection.action is not None
    expected_task_id = selection.action.get("task_id")

    assert rendered["selected_mode"] == "research"
    assert rendered["recommended"]["mission"] == selection.mission["id"]
    assert rendered["recommended"]["action"] == selection.action["id"]
    assert rendered["recommended"]["task_id"] == expected_task_id
    assert rendered["recommended"]["is_executable"] is bool(expected_task_id)
    assert rendered["recommended"]["guidance_only"] is bool(not expected_task_id)
    assert "parallel_work_policy" in rendered
    assert any(
        "result-promotion-protocol.md" in item
        for item in rendered["policy"]["defaults"]
    )
    # The mission must surface a well-formed, currently-READY task as its top
    # live candidate (or fall through to the READY-only policy note). Check the
    # candidate dynamically against the task registry rather than a frozen
    # snapshot, so legitimate task completions and unblocks do not break this
    # smoke test.
    tasks_dir = Path(__file__).resolve().parents[1] / "tasks"
    ready_task_ids = {
        payload["id"]
        for payload in (
            yaml.safe_load(task_file.read_text(encoding="utf-8"))
            for task_file in tasks_dir.glob("TASK-*.yaml")
        )
        if payload.get("status") == "READY"
    }
    if rendered["live_task_candidates"]:
        top_candidate = rendered["live_task_candidates"][0]
        assert top_candidate["task_id"] in ready_task_ids
        assert top_candidate["mode"] in {"research", "support"}
    else:
        assert rendered["task_visibility_policy"]["executor_modes"].startswith(
            "Only READY tasks"
        )
