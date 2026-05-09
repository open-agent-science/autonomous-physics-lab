from __future__ import annotations

import json
from pathlib import Path

from physics_lab.engines.dimensions import validate_item


def test_dimensional_validator_pilot_metrics_recompute() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    metrics_path = repo_root / "agent_runs" / "AGENT-RUN-0003" / "metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

    assert metrics["summary"]["generated_proposal_count"] == 8
    assert metrics["summary"]["executed_item_count"] == 5
    assert metrics["summary"]["rejected_before_execution_count"] == 3

    agreements = 0
    for item in metrics["executed_items"]:
        result = validate_item(
            {
                "id": item["item_id"],
                "formula": item["formula"],
                "variables": item["variables"],
                "expected_verdict": item["expected_verdict"],
            }
        )
        assert result.computed_verdict == item["observed_verdict"]
        assert result.agrees is item["agrees"]
        if result.agrees:
            agreements += 1

    assert agreements == metrics["summary"]["agreement_count"]
