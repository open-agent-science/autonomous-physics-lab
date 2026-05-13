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
    # The curator should surface at least one current follow-up task relevant to
    # the live nuclear campaign, which may be a direct nuclear validation task
    # (`TASK-0189`) or a campaign-adjacent support/doc task (`TASK-0175`) when
    # the stricter nuclear validation lanes are already claimed.
    assert any(
        item.task_id in {"TASK-0175", "TASK-0189", "TASK-0201"}
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

    assert "You are the APL Scientific Campaign Curator." in prompt
    assert "Canonical short command/name: campaign-curator." in prompt
    assert "Natural-language requests" in prompt
    assert "not\na task runner" in prompt
    assert "Do not:" in prompt
    assert "run experiments" in prompt
    assert "promote claims" in prompt
    assert "nuclear-mass-surface" in prompt


def test_campaign_curator_markdown_contains_expected_sections() -> None:
    brief = build_campaign_brief(ROOT, campaign_id="nuclear-mass-surface")
    rendered = render_campaign_brief(brief)

    assert "# Scientific Campaign Curator Brief" in rendered
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
    assert payload["recommended_next_tasks"]
