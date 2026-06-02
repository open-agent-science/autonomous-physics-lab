"""Tests for the real direct-measurement atomic-clock loader (TASK-0453).

These tests exercise the deterministic loader against the committed Beloy 2021 /
BACON direct-ratio seed fixture. They validate schema reconciliation and the
sandbox boundary only; they never fit drifts, compute residuals, derive
constants constraints, or promote claims.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from physics_lab.engines.atomic_clock_residuals import (
    load_atomic_clock_direct_dataset,
    load_atomic_clock_synthetic_dataset,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
BELOY_SEED_PATH = REPO_ROOT / "data" / "atomic_clocks" / "acr-0001-beloy-2021-direct-ratios.yaml"
SYNTHETIC_PATH = REPO_ROOT / "data" / "atomic_clocks" / "synthetic_loader_dry_run.yaml"


def _load_seed_payload() -> dict:
    return yaml.safe_load(BELOY_SEED_PATH.read_text(encoding="utf-8"))


def _write_payload(tmp_path: Path, payload: dict) -> Path:
    target = tmp_path / "dataset.yaml"
    target.write_text(yaml.safe_dump(payload), encoding="utf-8")
    return target


def test_direct_loader_accepts_committed_beloy_seed() -> None:
    dataset = load_atomic_clock_direct_dataset(BELOY_SEED_PATH)

    assert dataset.dataset_id == "ACR-0001-BELOY-2021-DIRECT-RATIOS"
    assert dataset.campaign_profile_id == "atomic-clock-residuals"
    assert len(dataset.rows) == 3
    assert dataset.row_class_counts == {"direct_measurement": 3}
    assert dataset.value_kind_counts == {"frequency_ratio": 3}
    assert dataset.covariance_groups == ("bacon_2018_campaign",)


def test_direct_loader_surfaces_uncertainty_contract_fields() -> None:
    dataset = load_atomic_clock_direct_dataset(BELOY_SEED_PATH)

    for row in dataset.rows:
        assert row.total_uncertainty > 0
        assert row.confidence_level_label == "1_sigma"
        assert row.bound_style == "measurement"
        assert row.covariance_reference.startswith("diagonal_per_paper")
        assert row.value > 0


def test_direct_loader_row_ids_match_seed() -> None:
    dataset = load_atomic_clock_direct_dataset(BELOY_SEED_PATH)

    assert sorted(row.row_id for row in dataset.rows) == [
        "ACR-0001-ROW-001",
        "ACR-0001-ROW-002",
        "ACR-0001-ROW-003",
    ]


def test_direct_loader_rejects_source_metadata_naming_drift(tmp_path: Path) -> None:
    payload = _load_seed_payload()
    # Inject the synthetic-style key onto a real row.
    payload["rows"][0]["source_metadata"] = {"source_class": "synthetic_rows"}
    with pytest.raises(ValueError, match="source_metadata"):
        load_atomic_clock_direct_dataset(_write_payload(tmp_path, payload))


def test_direct_loader_rejects_missing_uncertainty_field(tmp_path: Path) -> None:
    payload = _load_seed_payload()
    del payload["rows"][0]["uncertainty"]["bound_style"]
    with pytest.raises(ValueError, match="uncertainty missing required keys"):
        load_atomic_clock_direct_dataset(_write_payload(tmp_path, payload))


def test_direct_loader_rejects_synthetic_classification_flag(tmp_path: Path) -> None:
    payload = _load_seed_payload()
    payload["rows"][0]["classification"]["synthetic"] = True
    with pytest.raises(ValueError, match="classification.synthetic false"):
        load_atomic_clock_direct_dataset(_write_payload(tmp_path, payload))


def test_direct_loader_rejects_derived_constraint_mixing(tmp_path: Path) -> None:
    payload = _load_seed_payload()
    payload["rows"][0]["row_class"] = "derived_constraint"
    payload["rows"][0]["classification"]["derived_constraint"] = True
    with pytest.raises(ValueError, match="row_class must be direct_measurement"):
        load_atomic_clock_direct_dataset(_write_payload(tmp_path, payload))


def test_direct_loader_rejects_benchmark_allowed_dataset(tmp_path: Path) -> None:
    payload = _load_seed_payload()
    payload["scope"]["benchmark_allowed"] = True
    with pytest.raises(ValueError, match="benchmark_allowed false"):
        load_atomic_clock_direct_dataset(_write_payload(tmp_path, payload))


def test_direct_loader_rejects_nonpositive_uncertainty(tmp_path: Path) -> None:
    payload = _load_seed_payload()
    payload["rows"][0]["uncertainty"]["total"] = 0.0
    with pytest.raises(ValueError, match="uncertainty.total must be positive"):
        load_atomic_clock_direct_dataset(_write_payload(tmp_path, payload))


def test_synthetic_loader_still_rejects_real_seed() -> None:
    # The two loaders stay disjoint: the synthetic loader must not accept a real
    # direct-measurement dataset.
    with pytest.raises(ValueError):
        load_atomic_clock_synthetic_dataset(BELOY_SEED_PATH)


def test_direct_loader_rejects_synthetic_fixture() -> None:
    # ...and the direct loader must not accept the synthetic dry-run fixture.
    with pytest.raises(ValueError):
        load_atomic_clock_direct_dataset(SYNTHETIC_PATH)


def test_direct_loader_does_not_mutate_seed_file() -> None:
    before = BELOY_SEED_PATH.read_text(encoding="utf-8")
    load_atomic_clock_direct_dataset(BELOY_SEED_PATH)
    after = BELOY_SEED_PATH.read_text(encoding="utf-8")
    assert before == after


def test_helper_payload_roundtrip_is_isolated(tmp_path: Path) -> None:
    # Guard: mutating the working payload copy must not affect the seed on disk.
    payload = _load_seed_payload()
    mutated = copy.deepcopy(payload)
    mutated["rows"] = mutated["rows"][:1]
    load_atomic_clock_direct_dataset(_write_payload(tmp_path, mutated))
    # Original seed still loads with all three rows.
    assert len(load_atomic_clock_direct_dataset(BELOY_SEED_PATH).rows) == 3
