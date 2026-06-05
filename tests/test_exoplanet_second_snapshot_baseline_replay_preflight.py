from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_exoplanet_second_snapshot_baseline_replay_preflight as preflight  # noqa: E402

pytestmark = [
    pytest.mark.resource_sensitive,
    pytest.mark.xdist_group(name="exoplanet_snapshot"),
]


def test_committed_exo0002_gate_blocks_baseline_replay(tmp_path: Path) -> None:
    metrics_path = tmp_path / "metrics.json"
    report_path = tmp_path / "report.md"
    review_path = tmp_path / "review.md"

    exit_code = preflight.main(
        [
            "--out",
            str(metrics_path),
            "--report",
            str(report_path),
            "--review",
            str(review_path),
        ]
    )

    assert exit_code == 0
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert metrics["task_id"] == "TASK-0582"
    assert metrics["agent_run_id"] == "AGENT-RUN-0059"
    assert metrics["verdict"] == "BLOCKED_BY_REOPEN_COVERAGE_GATE"
    assert metrics["baseline_replay_status"] == "not_run_gate_failed"

    gate = metrics["gate_evaluation"]
    assert gate["gate_clears"] is False
    assert gate["reopening_lanes"] == []

    true_axis = gate["lanes"]["true_mass_with_transit_radius"]
    assert true_axis["exo_0001_axis_rows"] == 1207
    assert true_axis["exo_0002_axis_rows"] == 1208

    compact = true_axis["slices"]["compact_radius_lt1p5Re"]
    assert compact["exo_0001_eligible_rows"] == 92
    assert compact["exo_0002_eligible_rows"] == 92
    assert compact["lane_reopens"] is False
    assert "gate_2_per_axis_slice_floor" in compact["blockers"]
    assert "gate_3_material_growth" in compact["blockers"]

    jovian = true_axis["slices"]["jovian_radius_8_16Re"]
    assert jovian["exo_0001_eligible_rows"] == 567
    assert jovian["exo_0002_eligible_rows"] == 568
    assert jovian["gate_2_passes"] is True
    assert jovian["gate_3"]["fractional_growth_vs_exo_0001"] == pytest.approx(
        1.0 / 567.0
    )
    assert "gate_3_material_growth" in jovian["blockers"]

    minimum_axis = gate["lanes"]["minimum_mass_with_transit_radius"]
    assert minimum_axis["exo_0002_axis_rows"] == 2
    assert all(
        not payload["lane_reopens"]
        for payload in minimum_axis["slices"].values()
    )

    report = report_path.read_text(encoding="utf-8")
    review = review_path.read_text(encoding="utf-8")
    assert report == review
    assert "frozen CK17 baseline replay" in report
    assert "not run on `EXO-0002`" in report


def test_growth_gate_handles_zero_first_snapshot_count() -> None:
    growth = preflight._growth_gate(
        first_count=0,
        second_count=12,
        min_fractional_growth=0.5,
    )

    assert growth["fractional_growth_vs_exo_0001"] is None
    assert growth["passes"] is True
