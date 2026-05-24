from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_comparison_module():
    module_path = _repo_root() / "scripts" / "compare_nuclear_agent_vs_factory_scouts.py"
    spec = importlib.util.spec_from_file_location(
        "compare_nuclear_agent_vs_factory_scouts", module_path
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_agent_vs_factory_comparison_summarizes_committed_artifacts() -> None:
    module = _load_comparison_module()
    agent = module.summarize_agent_runs(_repo_root())
    factory = module.summarize_factory_slates(_repo_root())

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
    module = _load_comparison_module()
    markdown = module.render_markdown(
        module.summarize_agent_runs(_repo_root()),
        module.summarize_factory_slates(_repo_root()),
    )

    assert "MIXED" in markdown
    assert "does not fetch live measurements" in markdown
    assert "No claim, canonical result" in markdown
    assert "does not support a claim" in markdown
    assert "future-measurement reveal" in markdown
