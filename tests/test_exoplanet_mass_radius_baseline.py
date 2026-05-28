"""Tests for the TASK-0361 exoplanet mass-radius frozen-baseline benchmark.

Coverage focuses on three surfaces:

1. the frozen Chen-Kipping baseline (segment selection, continuity, and
   sanity values that should not drift if the segmentation is preserved);
2. the residual-summary metric and the per-class null baseline;
3. the runner script orchestration on the synthetic fixture under
   ``tests/fixtures/exoplanets/`` — the runner must produce deterministic
   metrics, agent_run.yaml, report, and review note artifacts and must not
   reach for any live data source.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_exoplanet_mass_radius_baseline as runner  # noqa: E402
from physics_lab.engines.exoplanet_mass_radius import (  # noqa: E402
    CHEN_KIPPING_SEGMENTS,
    ResidualSummary,
    benchmark_result_to_dict,
    chen_kipping_baseline_metadata,
    chen_kipping_predict_radius,
    chen_kipping_segment_for_mass,
    null_baseline_predict_radius,
    per_class_median_log_radius,
    planet_class_for_mass,
    residual_summary_to_dict,
    run_benchmark,
    summarize_log_residuals,
)

SYNTHETIC_FIXTURE = (
    ROOT / "tests" / "fixtures" / "exoplanets" / "synthetic_pscomppars_snapshot.yaml"
)


# ---------------------------------------------------------------------------
# Frozen Chen-Kipping baseline
# ---------------------------------------------------------------------------


def test_chen_kipping_has_four_segments_in_published_order():
    names = [segment.name for segment in CHEN_KIPPING_SEGMENTS]
    assert names == ["terran", "neptunian", "jovian", "stellar"]


def test_chen_kipping_segment_for_mass_picks_correct_bucket():
    assert chen_kipping_segment_for_mass(1.0).name == "terran"
    assert chen_kipping_segment_for_mass(2.04).name == "terran"
    assert chen_kipping_segment_for_mass(10.0).name == "neptunian"
    # Jovian transition is 0.414 M_jup = ~131.58 M_earth.
    assert chen_kipping_segment_for_mass(150.0).name == "jovian"
    # Stellar transition is 0.0800 M_sun = ~26635.68 M_earth.
    assert chen_kipping_segment_for_mass(50000.0).name == "stellar"


def test_chen_kipping_predicts_unit_anchor_at_one_earth_mass():
    # The CK17 anchor is R = 1.008 R_earth at M = 1 M_earth.
    assert chen_kipping_predict_radius(1.0) == pytest.approx(1.008, rel=1e-9)


def test_chen_kipping_is_continuous_across_changepoints():
    for left, right in zip(CHEN_KIPPING_SEGMENTS, CHEN_KIPPING_SEGMENTS[1:]):
        boundary = left.mass_upper_mearth
        left_radius = left.prefactor_r_earth_per_mass_unit_pow_slope * (
            boundary ** left.slope_log_r_per_log_m
        )
        right_radius = right.prefactor_r_earth_per_mass_unit_pow_slope * (
            boundary ** right.slope_log_r_per_log_m
        )
        assert left_radius == pytest.approx(right_radius, rel=1e-9)


def test_chen_kipping_predict_radius_rejects_nonpositive_mass():
    assert math.isnan(chen_kipping_predict_radius(-1.0))
    assert math.isnan(chen_kipping_predict_radius(0.0))


def test_planet_class_for_mass_matches_segment_names():
    assert planet_class_for_mass(0.5) == "terran"
    assert planet_class_for_mass(10.0) == "neptunian"
    assert planet_class_for_mass(500.0) == "jovian"
    assert planet_class_for_mass(40000.0) == "stellar"


def test_chen_kipping_baseline_metadata_is_serialisable_and_frozen():
    metadata = chen_kipping_baseline_metadata()
    assert metadata["no_new_parameters_fit"] is True
    assert len(metadata["segments"]) == 4
    json.dumps(metadata)  # should not raise
    # The stellar segment's upper bound is the only unbounded one and is
    # serialised as None to remain JSON-friendly.
    assert metadata["segments"][-1]["mass_upper_mearth"] is None


# ---------------------------------------------------------------------------
# Null baseline + residual summaries
# ---------------------------------------------------------------------------


def test_per_class_median_log_radius_groups_by_planet_class():
    pairs = [
        (1.0, 1.1),    # terran
        (1.5, 1.3),    # terran
        (10.0, 3.0),   # neptunian
        (100.0, 5.0),  # neptunian (still < 131.58 changepoint)
    ]
    medians = per_class_median_log_radius(pairs)
    assert set(medians) == {"terran", "neptunian"}
    # Terran median is between log10(1.1) and log10(1.3).
    assert math.log10(1.1) <= medians["terran"] <= math.log10(1.3)


def test_null_baseline_returns_nan_for_unseen_class():
    medians = {"terran": math.log10(1.0)}
    assert math.isnan(
        null_baseline_predict_radius(100.0, per_class_medians=medians)
    )


def test_summarize_log_residuals_handles_empty_input():
    summary = summarize_log_residuals([])
    assert isinstance(summary, ResidualSummary)
    assert summary.count == 0
    assert summary.log10_mae is None


def test_summarize_log_residuals_computes_factor_coverage():
    # Three residuals: 0.0 (within factor 1.5), 0.2 (within factor 2),
    # 0.4 (outside factor 2).
    summary = summarize_log_residuals([0.0, 0.2, 0.4])
    assert summary.count == 3
    assert summary.fraction_within_factor_2 == pytest.approx(2.0 / 3.0)
    # Within factor 1.5 (log10 ~ 0.176): only the 0.0 residual.
    assert summary.interval_68_coverage == pytest.approx(1.0 / 3.0)


def test_residual_summary_to_dict_round_trips():
    summary = summarize_log_residuals([-0.1, 0.0, 0.1])
    payload = residual_summary_to_dict(summary)
    json.dumps(payload)  # should not raise
    assert payload["count"] == 3
    assert payload["log10_mae"] == pytest.approx(2.0 / 30.0, rel=1e-9)


# ---------------------------------------------------------------------------
# Benchmark execution on the synthetic fixture
# ---------------------------------------------------------------------------


def _load_synthetic_entries():
    with SYNTHETIC_FIXTURE.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)["entries"]


def test_run_benchmark_on_synthetic_fixture_returns_both_axes():
    benchmark = run_benchmark(_load_synthetic_entries())
    assert set(benchmark) == {
        "true_mass_with_transit_radius",
        "minimum_mass_with_transit_radius",
    }


def test_run_benchmark_includes_only_eligible_rows():
    benchmark = run_benchmark(_load_synthetic_entries())
    true_mass = benchmark["true_mass_with_transit_radius"]
    # The fixture has Earth-like, sub-Neptune, and hot-Jupiter rows plus
    # two high-sigma rows. Even before the loader-level quality filter,
    # the high-sigma rows have valid mass and radius so they appear in
    # this engine-level eligibility predicate. The model-inferred rows
    # and the snapshot-excluded row do not satisfy the predicate.
    eligible_ids = {row.row_id for row in true_mass.rows}
    assert "SYN-001-EARTH-LIKE" in eligible_ids
    assert "SYN-002-SUB-NEPTUNE" in eligible_ids
    assert "SYN-003-HOT-JUPITER" in eligible_ids
    assert "SYN-005-MODEL-INFERRED-MASS" not in eligible_ids
    assert "SYN-006-MODEL-INFERRED-RADIUS" not in eligible_ids


def test_benchmark_result_to_dict_is_json_safe():
    benchmark = run_benchmark(_load_synthetic_entries())
    payload = benchmark_result_to_dict(benchmark["true_mass_with_transit_radius"])
    json.dumps(payload)  # should not raise
    assert payload["axis_name"] == "true_mass_with_transit_radius"


# ---------------------------------------------------------------------------
# Runner orchestration
# ---------------------------------------------------------------------------


def test_runner_produces_full_artifact_bundle_on_synthetic_fixture(tmp_path):
    metrics_path = tmp_path / "metrics.json"
    report_path = tmp_path / "report.md"
    agent_run_path = tmp_path / "agent_run.yaml"
    limitations_path = tmp_path / "limitations.md"
    preflight_path = tmp_path / "preflight.md"
    review_summary_path = tmp_path / "review_summary.md"
    review_path = tmp_path / "review.md"

    exit_code = runner.main(
        [
            "--snapshot",
            str(SYNTHETIC_FIXTURE),
            "--out",
            str(metrics_path),
            "--report",
            str(report_path),
            "--agent-run",
            str(agent_run_path),
            "--limitations",
            str(limitations_path),
            "--preflight",
            str(preflight_path),
            "--review-summary",
            str(review_summary_path),
            "--review",
            str(review_path),
        ]
    )
    assert exit_code == 0

    for path in (
        metrics_path,
        report_path,
        agent_run_path,
        limitations_path,
        preflight_path,
        review_summary_path,
        review_path,
    ):
        assert path.exists(), f"Missing artifact: {path}"
        assert path.stat().st_size > 0

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert metrics["task_id"] == "TASK-0361"
    assert metrics["agent_run_id"] == "AGENT-RUN-0032"
    assert metrics["campaign_profile_id"] == "exoplanet-mass-radius"
    assert metrics["baseline"]["no_new_parameters_fit"] is True
    assert set(metrics["axes"]) == {
        "true_mass_with_transit_radius",
        "minimum_mass_with_transit_radius",
    }
    assert "verdict" in metrics
    assert metrics["verdict"] in {
        "SANDBOX_PASS",
        "SANDBOX_FAIL",
        "FALSIFIED",
        "INCONCLUSIVE",
        "OVERFITTED",
        "REVIEW_NEEDED",
    }


def test_runner_agent_run_yaml_matches_schema_required_shape(tmp_path):
    metrics_path = tmp_path / "metrics.json"
    agent_run_path = tmp_path / "agent_run.yaml"
    runner.main(
        [
            "--snapshot",
            str(SYNTHETIC_FIXTURE),
            "--out",
            str(metrics_path),
            "--report",
            str(tmp_path / "report.md"),
            "--agent-run",
            str(agent_run_path),
            "--limitations",
            str(tmp_path / "limitations.md"),
            "--preflight",
            str(tmp_path / "preflight.md"),
            "--review-summary",
            str(tmp_path / "review_summary.md"),
            "--review",
            str(tmp_path / "review.md"),
        ]
    )
    payload = yaml.safe_load(agent_run_path.read_text(encoding="utf-8"))
    assert payload["sandbox_only"] is True
    assert payload["promotion_boundary"]["writes_canonical_result"] is False
    assert payload["promotion_boundary"]["claim_promotion_allowed"] is False
    assert (
        payload["proposal_paths"]["hypothesis"]
        == "hypothesis_proposals/exoplanet-mass/HYP-PROPOSAL-0049-frozen-baseline-benchmark.yaml"
    )
    assert (
        payload["proposal_paths"]["experiment"]
        == "experiment_proposals/exoplanet-mass/EXP-PROPOSAL-0015-frozen-baseline-benchmark.yaml"
    )


def test_runner_is_deterministic_on_repeated_invocation(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    for path in (first, second):
        runner.main(
            [
                "--snapshot",
                str(SYNTHETIC_FIXTURE),
                "--out",
                str(path),
                "--report",
                str(tmp_path / "report.md"),
                "--agent-run",
                str(tmp_path / "agent_run.yaml"),
                "--limitations",
                str(tmp_path / "limitations.md"),
                "--preflight",
                str(tmp_path / "preflight.md"),
                "--review-summary",
                str(tmp_path / "review_summary.md"),
                "--review",
                str(tmp_path / "review.md"),
            ]
        )
    assert first.read_text(encoding="utf-8") == second.read_text(encoding="utf-8")


def test_runner_verdict_decision_matrix():
    decide = runner._decide_verdict
    assert (
        decide(
            {
                "a": {"ck_beats_null": True},
                "b": {"ck_beats_null": True},
            }
        )
        == "SANDBOX_PASS"
    )
    assert (
        decide(
            {
                "a": {"ck_beats_null": False},
                "b": {"ck_beats_null": False},
            }
        )
        == "FALSIFIED"
    )
    assert (
        decide(
            {
                "a": {"ck_beats_null": True},
                "b": {"ck_beats_null": False},
            }
        )
        == "INCONCLUSIVE"
    )
    assert decide({"a": {"ck_beats_null": None}}) == "INCONCLUSIVE"
