"""Tests for the task-proposal PR helper (TASK-0467, P1/P3/P4)."""

from __future__ import annotations

from pathlib import Path

from physics_lab.registry.proposal_pr_helper import (
    preflight_proposal_pr,
    proposal_branch,
    proposal_filename,
    proposal_title,
    proposal_yaml,
)
from physics_lab.registry.validation import validate_document
import yaml


def _scaffold_kwargs() -> dict:
    return dict(
        date_str="20260530",
        contributor_id="roman",
        agent_id="claude",
        slug="demo-finding",
        title="Demo finding",
        proposal_type="maintainer_workflow",
        summary="A demo proposal.",
        rationale="Because demos help.",
        related_domain="cross_campaign_quality",
        planning_context="Demo planning context.",
    )


def test_canonical_names() -> None:
    assert proposal_branch("roman", "claude", "demo") == "agent/roman/claude/propose-task-demo"
    assert proposal_title("Demo") == "TASK-PROPOSAL: Demo"
    assert proposal_filename("20260530", "roman", "demo") == "20260530-roman-demo.yaml"


def test_scaffold_is_schema_valid() -> None:
    document = yaml.safe_load(proposal_yaml(**_scaffold_kwargs()))
    # Should not raise; includes the required planning_context field.
    validate_document(document, kind="task_proposal", source="scaffold.yaml")
    assert document["input"]["planning_context"] == "Demo planning context."
    assert document["proposal_id"] == "20260530-roman-demo-finding"


def _write_scaffold(root: Path) -> str:
    rel = f"tasks/proposals/{proposal_filename('20260530', 'roman', 'demo-finding')}"
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(proposal_yaml(**_scaffold_kwargs()), encoding="utf-8")
    return rel


def test_preflight_accepts_clean_proposal(tmp_path: Path) -> None:
    rel = _write_scaffold(tmp_path)
    report = preflight_proposal_pr(
        tmp_path,
        branch="agent/roman/claude/propose-task-demo-finding",
        title="TASK-PROPOSAL: Demo finding",
        proposal_path=rel,
    )
    assert report.ok
    assert report.warnings == ()


def test_preflight_flags_bad_branch_and_title(tmp_path: Path) -> None:
    rel = _write_scaffold(tmp_path)
    report = preflight_proposal_pr(
        tmp_path,
        branch="agent/roman/claude/task-0001-demo-finding",  # wrong: task branch
        title="TASK-0001: Demo finding",  # wrong: task title
        proposal_path=rel,
    )
    assert not report.ok
    assert any("proposal branch format" in e for e in report.errors)
    assert any("proposal PR title format" in e for e in report.errors)


def test_preflight_flags_bad_filename(tmp_path: Path) -> None:
    bad_rel = "tasks/proposals/decouple-board.yaml"  # missing date+contributor
    target = tmp_path / bad_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(proposal_yaml(**_scaffold_kwargs()), encoding="utf-8")
    report = preflight_proposal_pr(
        tmp_path,
        branch="agent/roman/claude/propose-task-demo-finding",
        title="TASK-PROPOSAL: Demo finding",
        proposal_path=bad_rel,
    )
    assert not report.ok
    assert any("filename" in e for e in report.errors)


def test_preflight_surfaces_schema_error(tmp_path: Path) -> None:
    rel = f"tasks/proposals/{proposal_filename('20260530', 'roman', 'demo-finding')}"
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    document = yaml.safe_load(proposal_yaml(**_scaffold_kwargs()))
    del document["input"]["planning_context"]  # break the schema
    target.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    report = preflight_proposal_pr(
        tmp_path,
        branch="agent/roman/claude/propose-task-demo-finding",
        title="TASK-PROPOSAL: Demo finding",
        proposal_path=rel,
    )
    assert not report.ok
    assert any("planning_context" in e for e in report.errors)
