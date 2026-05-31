from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from physics_lab.engines.atomic_clock_residuals import load_atomic_clock_synthetic_cross_source_dataset


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data/atomic_clocks/synthetic_cross_source_dry_run.yaml"


def test_loads_synthetic_cross_source_fixture() -> None:
    dataset = load_atomic_clock_synthetic_cross_source_dataset(FIXTURE)

    assert dataset.dataset_id == "ACLOCK-SYNTHETIC-CROSS-SOURCE-0001"
    assert dataset.task_id == "TASK-0488"
    assert dataset.row_class_counts == {"synthetic_dry_run": 3}
    assert dataset.value_kind_counts == {"frequency_ratio": 3}
    assert dataset.covariance_states["synthetic_cross_source_pair"] == "COV_SYNTHETIC_SENSITIVITY_ONLY"
    assert set(dataset.row_roles) == {
        "ACLOCK-XSR-SYN-ROW-0001",
        "ACLOCK-XSR-SYN-ROW-0002",
        "ACLOCK-XSR-SYN-ROW-0003",
    }


def test_rejects_real_source_role_label(tmp_path: Path) -> None:
    payload = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    mutated = deepcopy(payload)
    mutated["cross_source_dry_run"]["row_roles"]["ACLOCK-XSR-SYN-ROW-0001"] = "beloy_like_real_source"
    path = tmp_path / "bad-cross-source.yaml"
    path.write_text(yaml.safe_dump(mutated, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="not name real sources"):
        load_atomic_clock_synthetic_cross_source_dataset(path)


def test_rejects_non_synthetic_covariance_state(tmp_path: Path) -> None:
    payload = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    mutated = deepcopy(payload)
    mutated["cross_source_dry_run"]["covariance_states"]["synthetic_cross_source_pair"] = "COV_EXACT_COMMITTED"
    path = tmp_path / "bad-cross-source.yaml"
    path.write_text(yaml.safe_dump(mutated, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="COV_SYNTHETIC"):
        load_atomic_clock_synthetic_cross_source_dataset(path)
