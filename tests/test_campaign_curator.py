from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from physics_lab.registry.campaign_curator import (
    build_campaign_brief,
    build_campaign_scope_brief,
    campaign_brief_json,
    campaign_scope_brief_json,
    render_campaign_agent_prompt,
    render_campaign_brief,
)
from physics_lab.registry.mission_control import load_current_missions


ROOT = Path(__file__).resolve().parents[1]


def test_campaign_curator_defaults_to_top_campaign() -> None:
    brief = build_campaign_brief(ROOT)
    missions = load_current_missions(ROOT)["missions"]
    expected_campaign = sorted(
        missions,
        key=lambda item: int(item.get("rank", 999)),
    )[0]["id"]

    assert brief.campaign_id == expected_campaign
    assert brief.maintainer_facing is True
    assert brief.advisory_only is True
    assert "Do not execute experiments from this mode." in brief.guardrails
    # The curator should avoid REVIEW_READY closeout/review items in
    # executor-facing recommendations. When no fresh READY campaign task exists,
    # it falls back to configured mission actions instead of recommending
    # review-ready work as executable.
    assert brief.recommended_next_tasks
    assert all(
        item.status != "REVIEW_READY" for item in brief.recommended_next_tasks
    )
    assert all(item.task_id != "TASK-0251" for item in brief.recommended_next_tasks)
    assert all(item.task_id != "TASK-0417" for item in brief.recommended_next_tasks)
    live_ready = [
        item
        for item in brief.recommended_next_tasks
        if item.reason == "live READY task aligned with this campaign"
    ]
    configured_actions = [
        item
        for item in brief.recommended_next_tasks
        if item.reason == "configured mission action; confirm against live task board"
    ]
    assert live_ready or configured_actions
    assert all(item.status == "READY" for item in live_ready)
    assert all(item.task_id is None for item in configured_actions)
    assert not any(
        item.reason == "live READY task aligned with this campaign"
        and item.task_id in {"TASK-0264", "TASK-0266"}
        for item in brief.recommended_next_tasks
    )


def test_campaign_curator_json_is_agent_readable() -> None:
    brief = build_campaign_brief(ROOT, campaign_id="nuclear-mass-surface")
    payload = json.loads(campaign_brief_json(brief))

    assert payload["campaign_id"] == "nuclear-mass-surface"
    assert payload["maintainer_facing"] is True
    assert payload["advisory_only"] is True
    assert payload["recommended_next_tasks"]
    assert "recent_evidence" in payload
    assert any(
        evidence["identifier"].startswith("AGENT-RUN-")
        for evidence in payload["recent_evidence"]
    )


def test_campaign_curator_scope_filters_by_primary_pool() -> None:
    brief = build_campaign_scope_brief(
        ROOT,
        pool="source_data_benchmark",
        active_only=True,
    )

    ids = {item.campaign_id for item in brief.matching_campaigns}
    assert {
        "atomic-clock-residuals",
        "materials-property-residuals",
        "quantum-size-effects",
    } <= ids
    assert "nuclear-mass-surface" not in ids
    assert all(
        item.primary_pool == "source_data_benchmark"
        for item in brief.matching_campaigns
    )
    assert any(
        "secondary_pools are context" in item for item in brief.session_guidance
    )


def test_campaign_curator_scope_json_is_agent_readable() -> None:
    brief = build_campaign_scope_brief(ROOT, domain="classical_mechanics")
    payload = json.loads(campaign_scope_brief_json(brief))

    assert payload["scope_kind"] == "campaign_scope"
    assert payload["filters"]["domain"] == "classical_mechanics"
    ids = {campaign["campaign_id"] for campaign in payload["matching_campaigns"]}
    assert "pendulum-formula-falsification" in ids
    assert "anharmonic-oscillator" in ids
    assert any(
        "Do not create letter-coded groups" in item
        for item in payload["guardrails"]
    )


def test_campaign_curator_scope_rejects_unknown_domain() -> None:
    with pytest.raises(ValueError, match="Unsupported campaign scope domain"):
        build_campaign_scope_brief(ROOT, domain="typo_domain")


def test_campaign_curator_prompt_preserves_authority_boundary() -> None:
    brief = build_campaign_brief(ROOT, campaign_id="nuclear-mass-surface")
    prompt = render_campaign_agent_prompt(brief)

    assert "You are the APL Scientific Campaign Director." in prompt
    assert "campaign-curator" in prompt
    assert "any language" in prompt
    assert "literal phrase matching" in prompt
    assert "Natural-language requests" in prompt
    assert "not a task runner" in prompt
    assert "Do not:" in prompt
    assert "run experiments" in prompt
    assert "promote claims" in prompt
    assert "busywork" in prompt
    assert "nuclear-mass-surface" in prompt


def test_campaign_curator_markdown_contains_expected_sections() -> None:
    brief = build_campaign_brief(ROOT, campaign_id="nuclear-mass-surface")
    rendered = render_campaign_brief(brief)

    assert "# Scientific Campaign Director Brief" in rendered
    assert "## Director Objective" in rendered
    assert "## Portfolio Health / Agent Capacity" in rendered
    assert "## Current Campaign Verdict" in rendered
    assert "## Recommended Next Tasks" in rendered
    assert "## Overclaim / Public Wording Notes" in rendered


def test_campaign_curator_script_json_smoke() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_campaign_curator.py",
            "--campaign",
            "nuclear-mass-surface",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)

    assert payload["campaign_id"] == "nuclear-mass-surface"
    assert payload["role_name"] == "Scientific Campaign Director"
    assert "campaign-curator" in payload["accepted_aliases"]
    assert payload["recommended_next_tasks"]


def test_campaign_curator_script_scope_json_smoke() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_campaign_curator.py",
            "--pool",
            "source_data_benchmark",
            "--active-only",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)

    assert payload["scope_kind"] == "campaign_scope"
    assert payload["filters"]["pool"] == "source_data_benchmark"
    assert payload["filters"]["active_only"] is True
    assert payload["matching_campaigns"]
    assert all(
        campaign["primary_pool"] == "source_data_benchmark"
        for campaign in payload["matching_campaigns"]
    )


def test_campaign_curator_script_rejects_campaign_plus_scope_filter() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_campaign_curator.py",
            "--campaign",
            "nuclear-mass-surface",
            "--pool",
            "prediction_reveal",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "--campaign cannot be combined" in result.stderr


def test_campaign_curator_script_rejects_unknown_pool() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_campaign_curator.py",
            "--pool",
            "group_b",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "invalid choice: 'group_b'" in result.stderr


def test_campaign_curator_script_role_director_prompt_smoke() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_campaign_curator.py",
            "--role",
            "director",
            "--campaign",
            "nuclear-mass-surface",
            "--output",
            "agent",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    assert "Scientific Campaign Director" in result.stdout
    assert "This is not the normal researcher prompt" not in result.stdout
    assert "campaign-curator" in result.stdout
    assert "work-for-work loops" in result.stdout


def test_campaign_curator_script_legacy_agent_prompt_alias_still_works() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_campaign_curator.py",
            "--role",
            "director",
            "--campaign",
            "nuclear-mass-surface",
            "--agent-prompt",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    assert "Scientific Campaign Director" in result.stdout
    assert "campaign-curator" in result.stdout


def test_campaign_curator_script_role_curator_json_smoke() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_campaign_curator.py",
            "--role",
            "curator",
            "--campaign",
            "nuclear-mass-surface",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)

    assert payload["role_name"] == "Scientific Campaign Curator"
    assert "Summarize campaign evidence" in payload["director_objective"][0]
