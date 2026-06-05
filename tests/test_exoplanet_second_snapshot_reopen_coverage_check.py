from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_exoplanet_second_snapshot_reopen_coverage_check as coverage  # noqa: E402

pytestmark = [
    pytest.mark.resource_sensitive,
    pytest.mark.xdist_group(name="exoplanet_snapshot"),
]


def test_committed_exo0002_reopen_coverage_gate_remains_closed(
    tmp_path: Path,
) -> None:
    review_path = tmp_path / "coverage-review.md"
    json_path = tmp_path / "coverage-summary.json"

    exit_code = coverage.main(
        [
            "--review",
            str(review_path),
            "--json",
            str(json_path),
        ]
    )

    assert exit_code == 0
    summary = json.loads(json_path.read_text(encoding="utf-8"))
    assert summary["task_id"] == "TASK-0580"
    assert summary["verdict"] == "RESIDUAL_LANE_REMAINS_CLOSED"

    gate = summary["coverage_gate"]
    assert gate["gate_status"] == "BLOCKED"
    assert gate["reopening_lanes"] == []
    assert gate["gate_6_null_baseline_competition"] == (
        "not_attempted_coverage_gate_failed"
    )

    true_axis = gate["axes"]["true_mass_with_transit_radius"]
    minimum_axis = gate["axes"]["minimum_mass_with_transit_radius"]
    assert true_axis["exo_0001_axis_rows"] == 1207
    assert true_axis["exo_0002_axis_rows"] == 1208
    assert minimum_axis["exo_0001_axis_rows"] == 2
    assert minimum_axis["exo_0002_axis_rows"] == 2

    compact = true_axis["slices"]["compact_radius_lt1p5Re"]
    assert compact["exo_0001_eligible_rows"] == 92
    assert compact["exo_0002_eligible_rows"] == 92
    assert compact["gate_2_passes"] is False
    assert compact["lane_reopens"] is False

    jovian = true_axis["slices"]["jovian_radius_8_16Re"]
    assert jovian["exo_0001_eligible_rows"] == 567
    assert jovian["exo_0002_eligible_rows"] == 568
    assert jovian["gate_2_passes"] is True
    assert jovian["gate_3"]["fractional_growth_vs_exo_0001"] == pytest.approx(
        1.0 / 567.0
    )
    assert "gate_3_material_growth" in jovian["blockers"]

    review = review_path.read_text(encoding="utf-8")
    assert "residual lane therefore remains closed" in review
    assert "Null-baseline competition" in review


def test_growth_status_reports_zero_reference_without_division() -> None:
    growth = coverage._growth_status(
        first_count=0,
        second_count=0,
        min_fractional_growth=0.5,
    )

    assert growth["fractional_growth_vs_exo_0001"] is None
    assert growth["passes"] is False
