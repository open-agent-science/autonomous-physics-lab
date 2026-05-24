"""Tests for the Exoplanet Mass-Radius dataset loader (TASK-0354).

The synthetic fixture under tests/fixtures/exoplanets/ is constructed so
each filter branch in `physics_lab.datasets.exoplanets` is exercised at
least once. Counts in this test file are tied to that fixture; updating
the fixture requires updating the assertions here.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import yaml

from physics_lab.datasets.exoplanets import (
    DEFAULT_MASS_SIGMA_THRESHOLD,
    DEFAULT_RADIUS_SIGMA_THRESHOLD,
    KNOWN_MASS_CLASSES,
    KNOWN_RADIUS_CLASSES,
    KNOWN_ROW_CLASSES,
    REASON_DUPLICATE_PLANET_NAME,
    REASON_MASS_INFERRED_FROM_MR_RELATION,
    REASON_MASS_RELATIVE_UNCERTAINTY_ABOVE_THRESHOLD,
    REASON_RADIUS_INFERRED_FROM_NON_TRANSIT,
    REASON_RADIUS_RELATIVE_UNCERTAINTY_ABOVE_THRESHOLD,
    REASON_UNKNOWN_MASS_CLASS,
    apply_inclusion_filters,
    load_and_filter,
    load_exoplanet_snapshot,
    summarize,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "exoplanets"
SYNTHETIC_FIXTURE = FIXTURE_DIR / "synthetic_pscomppars_snapshot.yaml"


# ---------------------------------------------------------------------------
# Fixture-level invariants
# ---------------------------------------------------------------------------


def test_synthetic_fixture_loads_and_advertises_synthetic_dry_run():
    payload = load_exoplanet_snapshot(SYNTHETIC_FIXTURE)

    assert payload["dataset_id"] == "synthetic-pscomppars-snapshot-001"
    assert payload["snapshot_provenance"]["snapshot_kind"] == "synthetic_dry_run"
    assert payload["snapshot_provenance"]["live_external_fetch_allowed"] is False
    assert "fabricated" in payload["fake_source_warning"].lower()
    assert len(payload["entries"]) == 10


def test_loader_rejects_synthetic_kind_without_fake_source_warning(tmp_path: Path):
    payload = yaml.safe_load(SYNTHETIC_FIXTURE.read_text(encoding="utf-8"))
    payload.pop("fake_source_warning")
    bad = tmp_path / "bad-synthetic.yaml"
    bad.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="fake_source_warning"):
        load_exoplanet_snapshot(bad)


def test_loader_rejects_non_synthetic_kind_that_allows_live_external_fetch(
    tmp_path: Path,
):
    payload = yaml.safe_load(SYNTHETIC_FIXTURE.read_text(encoding="utf-8"))
    payload["snapshot_provenance"]["snapshot_kind"] = "composite_catalog_snapshot"
    payload["snapshot_provenance"]["live_external_fetch_allowed"] = True
    payload.pop("fake_source_warning")
    bad = tmp_path / "bad-live-fetch.yaml"
    bad.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="live_external_fetch_allowed"):
        load_exoplanet_snapshot(bad)


def test_loader_rejects_empty_entries(tmp_path: Path):
    payload = yaml.safe_load(SYNTHETIC_FIXTURE.read_text(encoding="utf-8"))
    payload["entries"] = []
    bad = tmp_path / "bad-empty.yaml"
    bad.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="entries"):
        load_exoplanet_snapshot(bad)


# ---------------------------------------------------------------------------
# Filter-chain behavior
# ---------------------------------------------------------------------------


def test_filter_chain_keeps_only_clean_true_mass_rows_post_filter():
    """Per the synthetic fixture:

    - 10 total rows
    - SYN-001, SYN-002, SYN-003 are clean true-mass + transit-radius (kept).
    - SYN-004 is M sin i (kept on minimum-mass axis; not excluded by loader).
    - SYN-005 is model_inferred mass (excluded; circular-validation guard).
    - SYN-006 is model_inferred radius (excluded; non-transit guard).
    - SYN-007 has sigma_M/M = 0.40 > 0.30 (excluded post-filter).
    - SYN-008 has sigma_R/R = 0.25 > 0.15 (excluded post-filter).
    - SYN-009 is microlensing mass (kept on alternate axis).
    - SYN-010 is snapshot-excluded (preserved with its reason).
    """

    filtered = load_and_filter(SYNTHETIC_FIXTURE)

    assert filtered.total_rows == 10
    # Pre-filter included = SYN-001, 002, 003, 004, 007, 008, 009 = 7
    assert filtered.pre_filter_included_count == 7
    # Post-filter included = drop SYN-007 and SYN-008 = 5
    assert filtered.post_filter_included_count == 5

    included_ids = {row["row_id"] for row in filtered.included_rows}
    assert included_ids == {
        "SYN-001-EARTH-LIKE",
        "SYN-002-SUB-NEPTUNE",
        "SYN-003-HOT-JUPITER",
        "SYN-004-MSINI-ONLY",
        "SYN-009-MICROLENSING",
    }

    excluded_ids = {row["row_id"] for row in filtered.excluded_rows}
    assert excluded_ids == {
        "SYN-005-MODEL-INFERRED-MASS",
        "SYN-006-MODEL-INFERRED-RADIUS",
        "SYN-007-HIGH-MASS-SIGMA",
        "SYN-008-HIGH-RADIUS-SIGMA",
        "SYN-010-SNAPSHOT-EXCLUDED",
    }


def test_filter_chain_emits_per_reason_exclusion_counts():
    filtered = load_and_filter(SYNTHETIC_FIXTURE)

    assert (
        filtered.exclusion_reason_counts[REASON_MASS_INFERRED_FROM_MR_RELATION] == 1
    )
    assert (
        filtered.exclusion_reason_counts[REASON_RADIUS_INFERRED_FROM_NON_TRANSIT] == 1
    )
    assert (
        filtered.exclusion_reason_counts[
            REASON_MASS_RELATIVE_UNCERTAINTY_ABOVE_THRESHOLD
        ]
        == 1
    )
    assert (
        filtered.exclusion_reason_counts[
            REASON_RADIUS_RELATIVE_UNCERTAINTY_ABOVE_THRESHOLD
        ]
        == 1
    )
    # Snapshot-marked exclusion preserves its inclusion_reason.
    assert filtered.exclusion_reason_counts["solution_type_not_confirmed"] == 1


def test_filter_chain_reports_class_and_method_histograms():
    filtered = load_and_filter(SYNTHETIC_FIXTURE)

    # Row-class histogram covers the fixture's spread.
    assert filtered.row_class_counts.get("direct_mass_radius_measurement", 0) >= 5
    assert filtered.row_class_counts.get("rv_minimum_mass_only", 0) == 1
    assert filtered.row_class_counts.get("microlensing_or_astrometry_mass", 0) == 1
    assert filtered.row_class_counts.get("model_inferred", 0) == 2

    # Mass-class histogram separates true_mass from minimum_mass_msini.
    assert filtered.mass_class_counts["true_mass"] >= 5
    assert filtered.mass_class_counts["minimum_mass_msini"] == 1
    assert filtered.mass_class_counts["microlensing_mass"] == 1
    assert filtered.mass_class_counts["model_inferred"] == 1

    # Radius-class histogram separates transit_radius from model_inferred /
    # not_measured.
    assert filtered.radius_class_counts["transit_radius"] >= 5
    assert filtered.radius_class_counts["model_inferred"] == 1
    assert filtered.radius_class_counts["not_measured"] == 2

    # Detection-method histogram includes both transit_and_RV and pure RV.
    assert filtered.detection_method_counts["transit_and_radial_velocity"] >= 5
    assert filtered.detection_method_counts["radial_velocity"] == 2
    assert filtered.detection_method_counts["microlensing"] == 1


# ---------------------------------------------------------------------------
# Threshold overrides
# ---------------------------------------------------------------------------


def test_relaxed_thresholds_keep_high_uncertainty_rows():
    """Pushing thresholds above the synthetic relative uncertainties
    (0.40 for mass and 0.25 for radius) keeps SYN-007 and SYN-008
    inside the post-filter included set."""

    filtered = load_and_filter(
        SYNTHETIC_FIXTURE,
        mass_sigma_threshold=0.50,
        radius_sigma_threshold=0.30,
    )

    included_ids = {row["row_id"] for row in filtered.included_rows}
    assert "SYN-007-HIGH-MASS-SIGMA" in included_ids
    assert "SYN-008-HIGH-RADIUS-SIGMA" in included_ids
    # Pre-filter is unchanged; post-filter now equals pre-filter.
    assert (
        filtered.post_filter_included_count == filtered.pre_filter_included_count == 7
    )


def test_strict_thresholds_drop_more_rows():
    """Tightening mass threshold to 0.04 drops SYN-001 too (sigma_M/M = 0.05)."""

    filtered = load_and_filter(
        SYNTHETIC_FIXTURE,
        mass_sigma_threshold=0.04,
        radius_sigma_threshold=DEFAULT_RADIUS_SIGMA_THRESHOLD,
    )

    included_ids = {row["row_id"] for row in filtered.included_rows}
    assert "SYN-001-EARTH-LIKE" not in included_ids
    # Mass-threshold exclusion counter grows.
    assert (
        filtered.exclusion_reason_counts[
            REASON_MASS_RELATIVE_UNCERTAINTY_ABOVE_THRESHOLD
        ]
        >= 2
    )


# ---------------------------------------------------------------------------
# Duplicate-name and unknown-class guards
# ---------------------------------------------------------------------------


def test_duplicate_planet_name_is_excluded(tmp_path: Path):
    payload = yaml.safe_load(SYNTHETIC_FIXTURE.read_text(encoding="utf-8"))
    duplicate = copy.deepcopy(payload["entries"][0])
    duplicate["row_id"] = "SYN-001-DUP"
    payload["entries"].append(duplicate)
    duplicated = tmp_path / "duplicated.yaml"
    duplicated.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    snapshot = load_exoplanet_snapshot(duplicated)
    filtered = apply_inclusion_filters(snapshot)

    assert filtered.exclusion_reason_counts[REASON_DUPLICATE_PLANET_NAME] == 1
    excluded_ids = {row["row_id"] for row in filtered.excluded_rows}
    assert "SYN-001-DUP" in excluded_ids


def test_unknown_mass_class_is_excluded_with_dedicated_reason(tmp_path: Path):
    payload = yaml.safe_load(SYNTHETIC_FIXTURE.read_text(encoding="utf-8"))
    payload["entries"][0]["mass"]["mass_class"] = "totally_made_up_class"
    bad = tmp_path / "bad-mass-class.yaml"
    bad.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    snapshot = load_exoplanet_snapshot(bad)
    filtered = apply_inclusion_filters(snapshot)

    assert filtered.exclusion_reason_counts[REASON_UNKNOWN_MASS_CLASS] == 1


def test_known_class_buckets_match_schema_enums():
    """Loader class buckets stay in sync with the schema enums."""

    schema_path = (
        ROOT / "physics_lab" / "schemas" / "exoplanet_mass_radius.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    entries_schema = schema["properties"]["entries"]["items"]
    mass_enum = set(entries_schema["properties"]["mass"]["properties"]["mass_class"]["enum"])
    radius_enum = set(entries_schema["properties"]["radius"]["properties"]["radius_class"]["enum"])
    row_enum = set(entries_schema["properties"]["row_class"]["enum"])

    assert KNOWN_MASS_CLASSES == mass_enum
    assert KNOWN_RADIUS_CLASSES == radius_enum
    assert KNOWN_ROW_CLASSES == row_enum


# ---------------------------------------------------------------------------
# Output shape
# ---------------------------------------------------------------------------


def test_summarize_is_json_serializable_and_includes_thresholds():
    filtered = load_and_filter(SYNTHETIC_FIXTURE)
    summary = summarize(filtered)

    serialized = json.dumps(summary, sort_keys=True)
    parsed = json.loads(serialized)

    assert parsed["dataset_id"] == "synthetic-pscomppars-snapshot-001"
    assert parsed["snapshot_kind"] == "synthetic_dry_run"
    assert parsed["thresholds"]["mass_sigma_threshold"] == DEFAULT_MASS_SIGMA_THRESHOLD
    assert (
        parsed["thresholds"]["radius_sigma_threshold"]
        == DEFAULT_RADIUS_SIGMA_THRESHOLD
    )
    # Ordered keys for review-friendly output.
    assert list(parsed["exclusion_reason_counts"].keys()) == sorted(
        parsed["exclusion_reason_counts"].keys()
    )


def test_filtered_snapshot_does_not_mutate_input_snapshot():
    snapshot = load_exoplanet_snapshot(SYNTHETIC_FIXTURE)
    before = copy.deepcopy(snapshot)

    apply_inclusion_filters(snapshot)
    apply_inclusion_filters(
        snapshot,
        mass_sigma_threshold=0.05,
        radius_sigma_threshold=0.05,
    )

    assert snapshot == before, "Filter must not mutate the loaded snapshot"
