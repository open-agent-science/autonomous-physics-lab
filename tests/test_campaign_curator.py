from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from physics_lab.registry.campaign_curator import (
    build_campaign_brief,
    campaign_brief_json,
    render_campaign_agent_prompt,
    render_campaign_brief,
)


ROOT = Path(__file__).resolve().parents[1]


def test_campaign_curator_defaults_to_top_campaign() -> None:
    brief = build_campaign_brief(ROOT)

    assert brief.campaign_id == "nuclear-mass-surface"
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
