"""Tests for the synthetic-only atomic-clock loader dry run."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from physics_lab.engines.atomic_clock_residuals import load_atomic_clock_synthetic_dataset


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_PATH = REPO_ROOT / "data" / "atomic_clocks" / "synthetic_loader_dry_run.yaml"


def test_atomic_clock_synthetic_loader_accepts_fixture() -> None:
    dataset = load_atomic_clock_synthetic_dataset(EXAMPLE_PATH)

    assert dataset.dataset_id == "ACLOCK-SYNTHETIC-0001"
    assert dataset.task_id == "TASK-0328"
    assert len(dataset.rows) == 3
    assert dataset.row_class_counts == {"synthetic_dry_run": 3}
    assert dataset.value_kind_counts == {
        "derived_constraint": 1,
        "frequency_ratio": 1,
        "repeated_frequency_ratio": 1,
    }


def test_atomic_clock_synthetic_fixture_keeps_rows_synthetic() -> None:
    dataset = load_atomic_clock_synthetic_dataset(EXAMPLE_PATH)

    assert all(row.synthetic for row in dataset.rows)
    assert {row.split for row in dataset.rows} == {"synthetic_only"}
    assert sum(1 for row in dataset.rows if row.derived_constraint) == 1


def test_atomic_clock_synthetic_loader_rejects_real_measurement_flag(tmp_path: Path) -> None:
    payload = yaml.safe_load(EXAMPLE_PATH.read_text(encoding="utf-8"))
    payload["rows"][0]["classification"]["direct_measurement"] = True
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="must not be direct measurements"):
        load_atomic_clock_synthetic_dataset(path)


def test_atomic_clock_synthetic_loader_rejects_non_synthetic_dataset(tmp_path: Path) -> None:
    payload = yaml.safe_load(EXAMPLE_PATH.read_text(encoding="utf-8"))
    payload["synthetic"] = False
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="must be explicitly synthetic"):
        load_atomic_clock_synthetic_dataset(path)


def test_atomic_clock_synthetic_loader_rejects_missing_derived_metadata(tmp_path: Path) -> None:
    payload = yaml.safe_load(EXAMPLE_PATH.read_text(encoding="utf-8"))
    del payload["rows"][2]["derived_constraint"]
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="need derived_constraint metadata"):
        load_atomic_clock_synthetic_dataset(path)
