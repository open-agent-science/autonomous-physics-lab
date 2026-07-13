from __future__ import annotations

from pathlib import Path

from physics_lab.registry.scientific_memory_index import (
    collect_scientific_memory_artifacts,
    render_historical_scientific_memory_ledger,
    render_scientific_memory_index,
    write_scientific_memory_index,
)


def test_historical_ledger_lists_pre_tier_artifacts(tmp_path: Path) -> None:
    _write(
        tmp_path / "results/EXP-0001/RUN-0001/result.yaml",
        """
result_id: RESULT-0001
title: Tiered result
best_verdict: VALID
review_tier: AGENT_VALIDATED
""",
    )
    _write(
        tmp_path / "prediction_registry/domain/PRED-0001.yaml",
        """
prediction_id: PRED-0001
title: Legacy prediction
registry_status: REGISTERED
""",
    )

    ledger = render_historical_scientific_memory_ledger(tmp_path)

    assert "Historical Scientific Memory (Pre-Tier Ledger)" in ledger
    assert "must not be read as reviewed or endorsed" in ledger
    assert "`PRED-0001` - Legacy prediction" in ledger
    # Tiered artifacts belong to the review-tier index, not the ledger.
    assert "RESULT-0001" not in ledger


def test_collects_review_tiers_and_legacy_artifacts(tmp_path: Path) -> None:
    _write(
        tmp_path / "results/EXP-0001/RUN-0001/result.yaml",
        """
result_id: RESULT-0001
title: Agent result
best_verdict: VALID_IN_RANGE
review_tier: AGENT_PUBLISHED
""",
    )
    _write(
        tmp_path / "prediction_registry/domain/PRED-0001.yaml",
        """
prediction_id: PRED-0001
title: Future reveal
registry_status: REGISTERED
review_tier: MAINTAINER_REVIEWED
""",
    )
    _write(
        tmp_path / "claims/CLAIM-0001-test.md",
        """---
id: CLAIM-0001
title: Legacy claim
status: DRAFT
---

# Legacy claim
""",
    )
    _write(
        tmp_path / "knowledge/topic/item.md",
        """---
id: KNOW-0001
title: Knowledge item
review_tier: AGENT_VALIDATED
---

# Knowledge item
""",
    )

    artifacts = collect_scientific_memory_artifacts(tmp_path)
    by_id = {artifact.artifact_id: artifact for artifact in artifacts}

    assert by_id["RESULT-0001"].review_tier == "AGENT_PUBLISHED"
    assert by_id["RESULT-0001"].next_action == "replay-needed"
    assert by_id["RESULT-0001"].historical_classification is None
    assert by_id["PRED-0001"].next_action == "external-reveal-needed"
    assert by_id["CLAIM-0001"].review_tier is None
    assert by_id["CLAIM-0001"].is_historical
    assert by_id["CLAIM-0001"].historical_classification == "PRE_TIER_PROTOCOL"
    assert by_id["CLAIM-0001"].next_action == "legacy-triage-only"
    assert by_id["KNOW-0001"].review_tier == "AGENT_VALIDATED"
    assert by_id["KNOW-0001"].next_action == "maintainer-review-needed"


def test_render_includes_counts_and_class_tables(tmp_path: Path) -> None:
    _write(
        tmp_path / "results/EXP-0001/RUN-0001/result.yaml",
        """
result_id: RESULT-0001
title: Agent result
best_verdict: VALID_IN_RANGE
review_tier: AGENT_PUBLISHED
""",
    )
    _write(
        tmp_path / "prediction_registry/domain/PRED-TEMPLATE.yaml",
        """
prediction_id: PRED-TEMPLATE
title: Template must be ignored
""",
    )
    _write(
        tmp_path / "prediction_registry/domain/PRED-0001.yaml",
        """
prediction_id: PRED-0001
title: Legacy prediction
registry_status: REGISTERED
""",
    )

    rendered = render_scientific_memory_index(tmp_path)

    assert "| `AGENT_PUBLISHED` | 1 | 0 | 0 | 0 | 1 |" in rendered
    # Historical artifacts stay out of the trust-ladder counts and sections;
    # they appear only in the compact historical summary.
    assert "LEGACY_UNTIERED" not in rendered
    assert "## Historical Pre-Tier Artifacts" in rendered
    assert "1 canonical artifacts predate the explicit review-tier" in rendered
    assert "| `PRED` | 1 |" in rendered
    assert "`PRED-0001`" not in rendered
    assert "(historical-scientific-memory.md)" in rendered
    assert "`RESULT-0001` - Agent result" in rendered
    assert "`PRED-TEMPLATE`" not in rendered
    assert "[`results/EXP-0001/RUN-0001/result.yaml`](../results/EXP-0001/RUN-0001/result.yaml)" in rendered


def test_write_index_creates_output_file(tmp_path: Path) -> None:
    _write(
        tmp_path / "results/EXP-0001/RUN-0001/result.yaml",
        """
result_id: RESULT-0001
title: Agent result
review_tier: AGENT_PUBLISHED
""",
    )

    output = write_scientific_memory_index(tmp_path)

    assert output == tmp_path / "docs/scientific-memory-review-tiers.md"
    assert output.exists()
    assert "Scientific Memory Review Tiers" in output.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")
