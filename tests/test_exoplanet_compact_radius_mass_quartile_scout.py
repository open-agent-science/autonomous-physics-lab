"""Tests for the TASK-0480 compact-radius mass-quartile scout."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_exoplanet_compact_radius_mass_quartile_scout as scout  # noqa: E402

SYNTHETIC_FIXTURE = (
    ROOT / "tests" / "fixtures" / "exoplanets" / "synthetic_pscomppars_snapshot.yaml"
)


def test_quartile_specs_cover_compact_rows_without_overlap() -> None:
    compact_entries = [
        {"row_id": f"row-{index}", "mass": {"value": float(index + 1)}}
        for index in range(10)
    ]

    specs = scout._quartile_specs(compact_entries)

    assert len(specs) == 4
    covered: list[str] = []

    for spec in specs:
        covered.extend(sorted(spec["row_ids"]))
        assert spec["rank_start_inclusive"] < spec["rank_end_exclusive"]
        assert spec["mass_min_Mearth"] <= spec["mass_max_Mearth"]

    assert sorted(covered) == [row["row_id"] for row in compact_entries]
    assert len(covered) == len(set(covered))


def test_classify_underpowered_quartile_blocks_interpretation() -> None:
    result = scout._classify_quartile(
        target_stats={"count": 10, "log10_rmse": 0.30},
        eligible_stats={"count": 100, "log10_rmse": 0.15},
        controls={},
    )

    assert result["verdict"] == "INCONCLUSIVE"
    assert result["outcome"] == "under_minimum_slice"
    assert result["adverse_control"] is None


def test_classify_sandbox_pass_when_quartile_clears_controls() -> None:
    control = {
        "status": "usable_control",
        "kind": "matched_cohort",
        "stats": {"log10_rmse": 0.20},
    }

    result = scout._classify_quartile(
        target_stats={"count": scout.MIN_SLICE_ROW_COUNT, "log10_rmse": 0.30},
        eligible_stats={"count": 100, "log10_rmse": 0.15},
        controls={"nearest_mass_other_compact_quartiles": control},
    )

    assert result["verdict"] == "SANDBOX_PASS"
    assert result["outcome"] == "quartile_residual_stress_above_eligible_and_controls"
    assert result["adverse_control"] == "nearest_mass_other_compact_quartiles"


def test_build_metrics_on_synthetic_fixture_records_boundaries() -> None:
    metrics = scout.build_metrics(SYNTHETIC_FIXTURE)

    assert metrics["task_id"] == "TASK-0480"
    assert metrics["agent_run_id"] == "AGENT-RUN-0049"
    assert metrics["live_fetch_performed"] is False
    assert metrics["baseline_refit_performed"] is False
    assert metrics["predeclared_bins"]["method"] == (
        "rank_balanced_mass_quartiles_within_compact_slice"
    )
    assert len(metrics["quartiles"]) == 4
    assert "claim_promotion" in metrics["forbidden_interpretations"]
    assert "new_mass_radius_law" in metrics["forbidden_interpretations"]


def test_write_outputs_uses_schema_valid_sandbox_agent_run_paths(tmp_path: Path) -> None:
    metrics = scout.build_metrics(SYNTHETIC_FIXTURE)
    metrics_path = tmp_path / "metrics.json"
    report_path = tmp_path / "report.md"
    agent_run_path = tmp_path / "agent_run.yaml"
    review_path = tmp_path / "review.md"

    scout.write_outputs(metrics, metrics_path, report_path, agent_run_path, review_path)

    assert metrics_path.exists()
    assert report_path.exists()
    assert agent_run_path.exists()
    assert review_path.exists()
    assert (tmp_path / "limitations.md").exists()
    assert (tmp_path / "preflight.md").exists()
    assert (tmp_path / "review_summary.md").exists()

    report = report_path.read_text(encoding="utf-8")
    review = review_path.read_text(encoding="utf-8")
    agent_run = agent_run_path.read_text(encoding="utf-8")

    assert "canonical `RESULT-*` created or edited" in report
    assert "canonical `RESULT-*` created or edited" in review
    assert "id: AGENT-RUN-0049" in agent_run
    assert "status: SANDBOX_COMPLETE" in agent_run
    assert "sandbox_only: true" in agent_run
    assert "promotion_boundary:" in agent_run
    assert "writes_canonical_result: false" in agent_run
