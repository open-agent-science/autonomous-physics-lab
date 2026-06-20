from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from physics_lab.engines.quantum_size_effects import (
    load_direct_inp_absorption_rows,
    run_quantum_size_baseline,
)
from physics_lab.registry.examples import load_example_config


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml"
HOLDOUT_ID = "almeida-2023-inp-620nm"


def test_loader_keeps_only_six_direct_inp_absorption_rows() -> None:
    rows = load_direct_inp_absorption_rows(DATASET)
    assert len(rows) == 6
    assert {row.material for row in rows} == {"InP"}
    assert rows[-1].entry_id == HOLDOUT_ID
    assert all(row.size_sigma_nm > 0 for row in rows)


def test_frozen_benchmark_selects_fixed_reference_and_beats_controls() -> None:
    metrics = run_quantum_size_baseline(dataset_path=DATASET, holdout_id=HOLDOUT_ID)
    assert metrics["selected_model_id"] == "almeida_fixed_reference"
    assert metrics["selected_holdout_mae_ev"] == 0.04839501
    assert metrics["constant_null_holdout_mae_ev"] == 0.4202
    assert metrics["shuffled_control_holdout_mae_ev"] == 0.375675554
    assert metrics["holdout_improvement_vs_null_ev"] == 0.37180499
    assert metrics["scientific_verdict"] == "VALID_IN_RANGE"
    assert metrics["agent_verdict"] == "SANDBOX_PASS"


def test_property_and_split_boundaries_are_explicit() -> None:
    metrics = run_quantum_size_baseline(dataset_path=DATASET, holdout_id=HOLDOUT_ID)
    assert metrics["property_kind"] == "absorption_peak_eV"
    assert metrics["size_axis"] == "edge_length_nm"
    assert metrics["train_count"] == 5
    assert metrics["holdout_count"] == 1
    selected = next(
        model for model in metrics["models"] if model["model_id"] == metrics["selected_model_id"]
    )
    assert [row["split"] for row in selected["predictions"]].count("holdout") == 1


def test_row_order_and_metrics_are_deterministic() -> None:
    first = run_quantum_size_baseline(dataset_path=DATASET, holdout_id=HOLDOUT_ID)
    second = run_quantum_size_baseline(dataset_path=DATASET, holdout_id=HOLDOUT_ID)
    assert first == second


def test_runner_writes_valid_sandbox_layout(tmp_path: Path) -> None:
    config = ROOT / "examples/quantum_size_effects.yaml"
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/run_quantum_size_effects_baseline.py"),
            "--config",
            str(config),
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    payload = json.loads(completed.stdout)
    assert payload["scientific_verdict"] == "VALID_IN_RANGE"


def test_example_config_is_registered_without_canonical_result_placeholder() -> None:
    config = load_example_config(ROOT / "examples/quantum_size_effects.yaml")
    assert config["config_kind"] == "quantum_size_effects_baseline"
    assert config["task_id"] == "TASK-0225"
    assert "result_id" not in config


def test_example_config_rejects_missing_frozen_boundary(tmp_path: Path) -> None:
    source = ROOT / "examples/quantum_size_effects.yaml"
    data = yaml.safe_load(source.read_text(encoding="utf-8"))
    del data["holdout_entry_id"]
    invalid = tmp_path / "invalid-quantum-size-effects.yaml"
    invalid.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="holdout_entry_id"):
        load_example_config(invalid)
