from __future__ import annotations

import json
import textwrap
from pathlib import Path
import subprocess
import sys

from physics_lab.registry import mission_control
from physics_lab.registry.mission_control import (
    load_current_missions,
    mission_json,
    ready_science_pool_health,
    render_agent_prompt,
    render_human_mission,
    render_onboarding_prompt,
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
    for index in range(4):
        _write_task(
            tmp_path,
            task_id=f"TASK-01{index:02d}",
            title=f"Research candidate {index}",
            status="READY",
            task_type="scientific_validation",
            priority="high",
            related_domain="surface_a" if index < 2 else "surface_b",
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

    assert health.ready_science_count == 4
    assert health.active_surfaces == ("surface_a", "surface_b")
    assert health.below_minimum is True
    assert health.below_surface_target is True
    assert health.task_queue_needed is True
    assert health.warning_only is True


def test_ready_science_pool_health_accepts_minimum_across_three_surfaces(tmp_path: Path) -> None:
    for index, surface in enumerate(
        ("surface_a", "surface_a", "surface_b", "surface_c", "surface_c")
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

    assert health.ready_science_count == 5
    assert health.active_surfaces == ("surface_a", "surface_b", "surface_c")
    assert health.below_minimum is False
    assert health.below_surface_target is False
    assert health.task_queue_needed is False
    assert health.below_preferred is True


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
    assert rendered["recommended"]["mission"] == "exoplanet-mass-radius"
    assert "live_task_candidates" in rendered


def test_apl_mission_script_onboarding_runs_from_repo_root() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/apl_mission.py", "--output", "onboarding"],
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
        [sys.executable, "scripts/apl_mission.py", "--onboarding"],
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


def test_cli_mission_json_runs_from_repo_root() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "physics_lab.cli", "mission", "--json"],
        check=True,
        capture_output=True,
        text=True,
    )

    rendered = json.loads(result.stdout)
    assert rendered["selected_mode"] == "research"
    assert rendered["recommended"]["action"] == "exoplanet-control-aware-go-no-go"
    assert rendered["recommended"]["task_id"] is None
    assert "parallel_work_policy" in rendered
    assert any(
        "result-promotion-protocol.md" in item
        for item in rendered["policy"]["defaults"]
    )
    # Accept any current research-mode top candidate from the live queue.
    # Depending on which nuclear tasks are already claimed, the mission helper
    # may surface nuclear follow-ups (`TASK-0189`, `TASK-0228`-`TASK-0237`,
    # `TASK-0250`-`TASK-0290`, `TASK-0320`-`TASK-0324`,
    # `TASK-0330`-`TASK-0347`), rotate to
    # the other READY research lanes
    # (`TASK-0222`-`TASK-0227`, `TASK-0291`-`TASK-0292`, `TASK-0307`,
    # `TASK-0310`-`TASK-0317`),
    # include non-saturated NEXT planning surfaces (`TASK-0308`-`TASK-0309`),
    # or fall through
    # to support candidates when the research queue is already review-ready.
    nuclear_validation_queue_ids = {
        "TASK-0189",
        "TASK-0200",
        "TASK-0201",
        "TASK-0202",
        "TASK-0203",
        "TASK-0204",
        "TASK-0205",
        "TASK-0206",
        "TASK-0177",
        "TASK-0222",
        "TASK-0223",
        "TASK-0224",
        "TASK-0225",
        "TASK-0226",
        "TASK-0227",
        "TASK-0228",
        "TASK-0229",
        "TASK-0230",
        "TASK-0231",
        "TASK-0232",
        "TASK-0233",
        "TASK-0234",
        "TASK-0235",
        "TASK-0236",
        "TASK-0237",
        "TASK-0250",
        "TASK-0251",
        "TASK-0242",
        "TASK-0252",
        "TASK-0253",
        "TASK-0254",
        "TASK-0264",
        "TASK-0265",
        "TASK-0266",
        "TASK-0272",
        "TASK-0273",
        "TASK-0274",
        "TASK-0278",
        "TASK-0279",
        "TASK-0280",
        "TASK-0281",
        "TASK-0282",
        "TASK-0283",
        "TASK-0285",
        "TASK-0286",
        "TASK-0287",
        "TASK-0289",
        "TASK-0290",
        "TASK-0291",
        "TASK-0292",
        "TASK-0294",
        "TASK-0295",
        "TASK-0296",
        "TASK-0298",
        "TASK-0303",
        "TASK-0304",
        "TASK-0306",
        "TASK-0307",
        "TASK-0308",
        "TASK-0309",
        "TASK-0310",
        "TASK-0311",
        "TASK-0312",
        "TASK-0315",
        "TASK-0316",
        "TASK-0317",
        "TASK-0320",
        "TASK-0321",
        "TASK-0323",
        "TASK-0324",
        "TASK-0325",
        "TASK-0326",
        "TASK-0327",
        "TASK-0328",
        "TASK-0330",
        "TASK-0331",
        "TASK-0332",
        "TASK-0333",
        "TASK-0334",
        "TASK-0335",
        "TASK-0336",
        "TASK-0337",
        "TASK-0338",
        "TASK-0339",
        "TASK-0340",
        "TASK-0341",
        "TASK-0342",
        "TASK-0343",
        "TASK-0344",
        "TASK-0345",
        "TASK-0346",
        "TASK-0347",
        "TASK-0351",
        "TASK-0352",
        "TASK-0353",
        "TASK-0354",
        "TASK-0355",
        "TASK-0356",
        "TASK-0361",
        "TASK-0362",
        "TASK-0363",
        "TASK-0364",
        "TASK-0365",
        "TASK-0367",
        "TASK-0368",
        "TASK-0369",
        "TASK-0370",
        "TASK-0371",
        "TASK-0372",
        "TASK-0373",
        "TASK-0374",
        "TASK-0375",
        "TASK-0376",
        "TASK-0377",
        "TASK-0378",
        "TASK-0379",
        "TASK-0380",
        "TASK-0381",
        "TASK-0382",
        "TASK-0383",
        "TASK-0384",
        "TASK-0390",
        "TASK-0391",
        "TASK-0392",
        "TASK-0393",
        "TASK-0394",
        "TASK-0395",
        "TASK-0396",
        "TASK-0397",
        "TASK-0398",
        "TASK-0399",
        "TASK-0400",
        "TASK-0401",
        "TASK-0402",
        "TASK-0403",
        "TASK-0404",
        "TASK-0407",
        "TASK-0408",
        "TASK-0409",
        "TASK-0410",
        "TASK-0411",
        "TASK-0412",
        "TASK-0413",
        "TASK-0414",
        "TASK-0415",
        "TASK-0416",
        "TASK-0417",
        "TASK-0418",
        "TASK-0419",
        "TASK-0420",
        "TASK-0421",
        "TASK-0422",
        "TASK-0423",
        "TASK-0427",
        "TASK-0428",
        "TASK-0432",
        "TASK-0444",
        "TASK-0448",
        "TASK-0449",
        "TASK-0450",
        "TASK-0451",
        "TASK-0452",
        "TASK-0453",
        "TASK-0454",
        "TASK-0474",
        "TASK-0475",
        "TASK-0476",
        "TASK-0477",
        "TASK-0478",
        "TASK-0479",
        "TASK-0480",
        "TASK-0481",
        "TASK-0482",
        "TASK-0483",
        "TASK-0484",
        "TASK-0485",
        "TASK-0486",
        "TASK-0487",
        "TASK-0488",
        "TASK-0489",
        "TASK-0490",
        "TASK-0491",
        "TASK-0492",
        "TASK-0493",
    }
    if rendered["live_task_candidates"]:
        assert (
            rendered["live_task_candidates"][0]["task_id"]
            in nuclear_validation_queue_ids
        )
        assert rendered["live_task_candidates"][0]["mode"] in {"research", "support"}
    else:
        assert rendered["task_visibility_policy"]["executor_modes"].startswith(
            "Only READY tasks"
        )
