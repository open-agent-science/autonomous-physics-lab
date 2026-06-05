"""TASK-0581 tests for the EXO-0001/EXO-0002 snapshot delta audit."""

from __future__ import annotations

from pathlib import Path

from scripts.run_exoplanet_snapshot_delta_audit import compare_snapshots

ROOT = Path(__file__).resolve().parents[1]


def test_snapshot_delta_reports_committed_snapshot_counts() -> None:
    delta = compare_snapshots(
        ROOT / "data/exoplanets/exo-0001-pscomppars-snapshot.yaml",
        ROOT / "data/exoplanets/exo-0002-pscomppars-snapshot.yaml",
    )

    exo1 = delta["snapshot_summaries"]["exo0001"]
    exo2 = delta["snapshot_summaries"]["exo0002"]

    assert exo1["total_rows"] == 6291
    assert exo1["post_filter_included_count"] == 4301
    assert exo2["total_rows"] == 6298
    assert exo2["post_filter_included_count"] == 4308
    assert delta["interpretation_boundary"] == {
        "baseline_refit_performed": False,
        "claim_or_prediction_promotion": False,
        "live_fetch_performed": False,
        "residual_metrics_computed": False,
    }


def test_snapshot_delta_preserves_mass_axis_boundaries() -> None:
    delta = compare_snapshots(
        ROOT / "data/exoplanets/exo-0001-pscomppars-snapshot.yaml",
        ROOT / "data/exoplanets/exo-0002-pscomppars-snapshot.yaml",
    )

    exo1_mass = delta["snapshot_summaries"]["exo0001"]["mass_class_counts"]
    exo2_mass = delta["snapshot_summaries"]["exo0002"]["mass_class_counts"]

    assert exo1_mass["true_mass"] == 2103
    assert exo1_mass["minimum_mass_msini"] == 986
    assert exo2_mass["true_mass"] == 2110
    assert exo2_mass["minimum_mass_msini"] == 985
    assert "minimum_mass_transit_radius_axis" in delta["previous_audit_slice_overlap"]


def test_snapshot_delta_reports_identifier_and_slice_overlap() -> None:
    delta = compare_snapshots(
        ROOT / "data/exoplanets/exo-0001-pscomppars-snapshot.yaml",
        ROOT / "data/exoplanets/exo-0002-pscomppars-snapshot.yaml",
    )

    identifiers = delta["planet_identifier_delta"]
    slices = delta["previous_audit_slice_overlap"]

    assert identifiers["exo0001_planet_names"] == 6291
    assert identifiers["exo0002_planet_names"] == 6298
    assert identifiers["overlap_planet_names"] == 6291
    assert identifiers["new_planet_names_in_exo0002"] == 7
    assert identifiers["removed_planet_names_from_exo0001"] == 0

    assert slices["compact_radius_lt1p5Re_true_mass"]["exo0001_count"] == 92
    assert slices["compact_radius_lt1p5Re_true_mass"]["exo0002_count"] == 92
    assert slices["sub_neptune_radius_1p5_4Re_true_mass"]["overlap_count"] == 340
    assert slices["hot_jupiter_period_lt10d_radius_8_16Re_true_mass"][
        "overlap_count"
    ] == 445
