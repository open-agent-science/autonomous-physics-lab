"""TASK-0536 coverage for Exoplanet second-snapshot ingestion dry-run guards."""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

from physics_lab.datasets.exoplanets import (
    apply_inclusion_filters,
    load_exoplanet_snapshot,
    normalized_snapshot_checksum,
)

ROOT = Path(__file__).resolve().parents[1]
TARGET_FREEZE_PATH = (
    ROOT / "data" / "exoplanets" / "second_snapshot_target_freeze.yaml"
)
SECOND_SNAPSHOT_MANIFEST = (
    ROOT / "data" / "exoplanets" / "second_snapshot_manifest.yaml"
)
SYNTHETIC_FIXTURE = (
    ROOT / "tests" / "fixtures" / "exoplanets" / "synthetic_pscomppars_snapshot.yaml"
)


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        payload = yaml.safe_load(fh)
    assert isinstance(payload, dict)
    return payload


def _single_line(text: str) -> str:
    return " ".join(text.split())


def test_second_snapshot_target_freeze_is_no_live_fetch_no_peek_metadata() -> None:
    freeze = _load_yaml(TARGET_FREEZE_PATH)

    assert freeze["status"] == "rule_frozen_no_future_values"
    assert freeze["scope"]["future_data_values_included"] is False
    assert freeze["scope"]["live_fetch_allowed"] is False
    assert freeze["scope"]["prediction_registry_allowed"] is False
    assert freeze["scope"]["claim_promotion_allowed"] is False

    promotion = freeze["promotion_boundary"]
    assert promotion["writes_prediction_registry"] is False
    assert promotion["writes_canonical_result"] is False
    assert promotion["claim_promotion_allowed"] is False
    assert promotion["knowledge_promotion_allowed"] is False


def test_second_snapshot_target_freeze_keeps_mass_axes_separate() -> None:
    freeze = _load_yaml(TARGET_FREEZE_PATH)
    axes = freeze["target_axes"]

    assert set(axes) == {"true_mass_transit_radius", "minimum_mass_transit_radius"}
    assert "true-mass class" in axes["true_mass_transit_radius"]["mass_provenance_rule"]
    assert (
        "minimum-mass class"
        in axes["minimum_mass_transit_radius"]["mass_provenance_rule"]
    )
    assert "True-mass and minimum-mass axes remain separate" in "\n".join(
        freeze["reveal_conditions"]
    )


def test_second_snapshot_target_freeze_declares_blockers_before_real_reveal() -> None:
    freeze = _load_yaml(TARGET_FREEZE_PATH)
    blockers = "\n".join(freeze["blocker_conditions"])
    required_next_step = _single_line(
        freeze["promotion_boundary"]["required_next_step"]
    )

    assert "Future snapshot retrieval lacks timestamp, checksum, row count" in blockers
    assert "future query differs from the frozen query" in blockers
    assert "mix true-mass and minimum-mass rows" in blockers
    assert "does not authorize acquisition or scoring" in required_next_step


def test_synthetic_fixture_exercises_second_snapshot_row_class_separation() -> None:
    snapshot = load_exoplanet_snapshot(SYNTHETIC_FIXTURE)
    filtered = apply_inclusion_filters(snapshot)

    assert snapshot["snapshot_provenance"]["snapshot_kind"] == "synthetic_dry_run"
    assert snapshot["snapshot_provenance"]["live_external_fetch_allowed"] is False
    assert snapshot["snapshot_provenance"]["raw_checksum_sha256"] is None

    assert filtered.mass_class_counts["true_mass"] >= 1
    assert filtered.mass_class_counts["minimum_mass_msini"] == 1
    assert filtered.mass_class_counts["model_inferred"] == 1
    assert filtered.row_class_counts["model_inferred"] == 2
    assert any(row["inclusion_status"] == "excluded" for row in filtered.excluded_rows)


def test_synthetic_fixture_checksum_replay_is_deterministic_for_dry_run() -> None:
    snapshot = load_exoplanet_snapshot(SYNTHETIC_FIXTURE)
    first = normalized_snapshot_checksum(snapshot)
    second = normalized_snapshot_checksum(copy.deepcopy(snapshot))

    assert first == second
    assert len(first) == 64
    assert all(char in "0123456789abcdef" for char in first)


def test_second_snapshot_manifest_is_metadata_only_acquisition_shape() -> None:
    manifest = _load_yaml(SECOND_SNAPSHOT_MANIFEST)

    assert manifest["status"] == "metadata_only_acquisition_package"
    assert manifest["scope"]["live_fetch_performed"] is False
    assert manifest["scope"]["future_data_values_included"] is False
    assert manifest["scope"]["raw_snapshot_committed"] is False
    assert manifest["scope"]["normalized_snapshot_committed"] is False
    assert manifest["scope"]["benchmark_allowed"] is False
    assert manifest["source"]["query_contract_sha256"] == (
        "4364d83855a19cfc638f733b4aea32c1873af9b78338f0b84a9b25f51e0de3e4"
    )
    assert manifest["checksum_policy"]["raw_checksum_sha256"] is None
    assert manifest["planned_acquisition"]["retrieval_timestamp_utc"] is None
    assert set(manifest["row_class_rules"]["preserve_separate_states"]) == {
        "true_mass_transit_radius",
        "minimum_mass_transit_radius",
        "model_inferred",
        "excluded",
        "radius_only_or_mass_only_context",
    }
