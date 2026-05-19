from __future__ import annotations

from pathlib import Path

from scripts.compare_nuclear_agent_vs_factory_scouts import (
    render_markdown,
    summarize_agent_runs,
    summarize_factory_slates,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_agent_vs_factory_comparison_summarizes_committed_artifacts() -> None:
    agent = summarize_agent_runs(_repo_root())
    factory = summarize_factory_slates(_repo_root())

    assert factory.candidates == 84
    assert factory.advisory_flags == 24
    assert factory.extreme_sensitivity_flags == 13
    assert factory.all_zero_flags == 3
    assert factory.redundant_target_batch_flags == 8

    assert agent.generated == 26
    assert agent.executed == 17
    assert agent.rejected == 9
    assert agent.verdict_counts["PARTIALLY_VALID"] == 6
    assert agent.verdict_counts["OVERFITTED"] == 5
    assert agent.verdict_counts["INCONCLUSIVE"] == 6
    assert agent.negative_primary_count == 6
    assert agent.zero_primary_count == 4
    assert agent.positive_primary_count == 7
    assert agent.best_primary_delta == -0.09150380269033231
    assert agent.worst_primary_delta == 18.63976352053184


def test_agent_vs_factory_markdown_preserves_review_boundaries() -> None:
    markdown = render_markdown(
        summarize_agent_runs(_repo_root()),
        summarize_factory_slates(_repo_root()),
    )

    assert "MIXED" in markdown
    assert "does not fetch live measurements" in markdown
    assert "No claim, canonical result" in markdown
    assert "does not support a claim" in markdown
    assert "future-measurement reveal" in markdown
