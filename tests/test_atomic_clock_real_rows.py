from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from physics_lab.engines.atomic_clock_residuals import (
    load_atomic_clock_direct_dataset,
    load_atomic_clock_synthetic_dataset,
)


ROOT = Path(__file__).resolve().parents[1]
BELOY_DIRECT_ROWS = ROOT / "data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml"
SYNTHETIC_DRY_RUN = ROOT / "data/atomic_clocks/synthetic_loader_dry_run.yaml"
ATOMIC_HOLDOUT_MANIFEST = "data/atomic_clocks/atomic_holdout_manifest.yaml"


def test_loads_committed_beloy_direct_rows() -> None:
    dataset = load_atomic_clock_direct_dataset(BELOY_DIRECT_ROWS)

    assert dataset.dataset_id == "ACR-0001-BELOY-2021-DIRECT-RATIOS"
    assert dataset.row_class_counts == {"direct_measurement": 3}
    assert dataset.value_kind_counts == {"frequency_ratio": 3}
    assert dataset.covariance_group_counts == {"bacon_2018_campaign": 3}
    assert {row.confidence_level_label for row in dataset.rows} == {"1_sigma"}
    assert {row.bound_style for row in dataset.rows} == {"measurement"}
    assert {row.row_id: row.split for row in dataset.rows} == {
        "ACR-0001-ROW-001": "train",
        "ACR-0001-ROW-002": "train",
        "ACR-0001-ROW-003": "cross_source_reference",
    }
    assert {row.row_id: row.row_role for row in dataset.rows} == {
        "ACR-0001-ROW-001": "training_context",
        "ACR-0001-ROW-002": "training_context",
        "ACR-0001-ROW-003": "cross_source_reference",
    }
    assert {row.freeze_manifest for row in dataset.rows} == {ATOMIC_HOLDOUT_MANIFEST}


def test_real_loader_rejects_source_metadata_alias(tmp_path: Path) -> None:
    payload = yaml.safe_load(BELOY_DIRECT_ROWS.read_text(encoding="utf-8"))
    mutated = deepcopy(payload)
    first_row = mutated["rows"][0]
    first_row["source_metadata"] = first_row.pop("source")
    path = tmp_path / "bad-real-row.yaml"
    path.write_text(yaml.safe_dump(mutated, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="must use source, not source_metadata"):
        load_atomic_clock_direct_dataset(path)


def test_real_loader_rejects_missing_covariance_reference(tmp_path: Path) -> None:
    payload = yaml.safe_load(BELOY_DIRECT_ROWS.read_text(encoding="utf-8"))
    mutated = deepcopy(payload)
    del mutated["rows"][0]["uncertainty"]["covariance_reference"]
    path = tmp_path / "bad-real-row.yaml"
    path.write_text(yaml.safe_dump(mutated, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="covariance_reference"):
        load_atomic_clock_direct_dataset(path)


def test_real_loader_rejects_unknown_holdout_split(tmp_path: Path) -> None:
    payload = yaml.safe_load(BELOY_DIRECT_ROWS.read_text(encoding="utf-8"))
    mutated = deepcopy(payload)
    mutated["rows"][0]["holdout"]["split"] = "calibration"
    path = tmp_path / "bad-real-row.yaml"
    path.write_text(yaml.safe_dump(mutated, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="holdout.split"):
        load_atomic_clock_direct_dataset(path)


def test_real_loader_requires_freeze_manifest_for_assigned_rows(tmp_path: Path) -> None:
    payload = yaml.safe_load(BELOY_DIRECT_ROWS.read_text(encoding="utf-8"))
    mutated = deepcopy(payload)
    mutated["rows"][0]["holdout"]["freeze_manifest"] = None
    path = tmp_path / "bad-real-row.yaml"
    path.write_text(yaml.safe_dump(mutated, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="freeze_manifest"):
        load_atomic_clock_direct_dataset(path)


def test_real_loader_rejects_row_role_split_mismatch(tmp_path: Path) -> None:
    payload = yaml.safe_load(BELOY_DIRECT_ROWS.read_text(encoding="utf-8"))
    mutated = deepcopy(payload)
    mutated["rows"][0]["holdout"]["row_role"] = "cross_source_target"
    path = tmp_path / "bad-real-row.yaml"
    path.write_text(yaml.safe_dump(mutated, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="row_role"):
        load_atomic_clock_direct_dataset(path)


def test_synthetic_loader_still_accepts_synthetic_fixture() -> None:
    dataset = load_atomic_clock_synthetic_dataset(SYNTHETIC_DRY_RUN)

    assert dataset.dataset_id == "ACLOCK-SYNTHETIC-0001"
    assert dataset.row_class_counts == {"synthetic_dry_run": 3}
