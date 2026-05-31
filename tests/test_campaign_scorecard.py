"""Tests for the campaign output scorecard (TASK-0498)."""

from __future__ import annotations

from pathlib import Path

from physics_lab.registry.campaign_scorecard import (
    ScorecardReport,
    _count_results,
    _repo_claim_statuses,
    build_scorecard,
)


def _write_result(path: Path, *, verdict: str, tier: str | None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"best_verdict: {verdict}"]
    if tier is not None:
        lines.append(f"review_tier: {tier}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_count_results_groups_verdicts_and_tiers(tmp_path: Path) -> None:
    _write_result(tmp_path / "a" / "result.yaml", verdict="VALID", tier="AGENT_PUBLISHED")
    _write_result(tmp_path / "b" / "result.yaml", verdict="FALSIFIED", tier=None)
    count, verdicts, tiers = _count_results(
        [tmp_path / "a" / "result.yaml", tmp_path / "b" / "result.yaml", tmp_path / "missing.yaml"]
    )
    assert count == 2
    assert verdicts == {"VALID": 1, "FALSIFIED": 1}
    # missing review_tier defaults to LEGACY_UNTIERED
    assert tiers == {"AGENT_PUBLISHED": 1, "LEGACY_UNTIERED": 1}


def test_repo_claim_statuses_counts_status_lines(tmp_path: Path) -> None:
    claims = tmp_path / "claims"
    claims.mkdir()
    (claims / "CLAIM-0001-x.md").write_text("# Claim\n\nstatus: DRAFT\n", encoding="utf-8")
    (claims / "CLAIM-0002-y.md").write_text("# Claim\n\nstatus: SUPPORTED\n", encoding="utf-8")
    (claims / "CLAIM-0003-z.md").write_text("# Claim\n\nstatus: DRAFT\n", encoding="utf-8")
    counts = _repo_claim_statuses(tmp_path)
    assert counts == {"DRAFT": 2, "SUPPORTED": 1}


def test_build_scorecard_empty_repo_is_safe(tmp_path: Path) -> None:
    report = build_scorecard(tmp_path)
    assert isinstance(report, ScorecardReport)
    assert report.campaigns == ()
    assert report.totals()["results_total"] == 0


def test_build_scorecard_runs_on_live_repo() -> None:
    report = build_scorecard(".")
    totals = report.totals()
    # The live repo has predictions and claims; scorecard must compute totals.
    assert totals["results_total"] >= 0
    assert set(totals) >= {"results_total", "predictions", "claims", "knowledge"}
    # repo-wide result verdict/tier dicts are populated structures
    assert isinstance(report.repo_result_verdicts, dict)
