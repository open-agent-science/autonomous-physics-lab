from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

from physics_lab.engines.quantum_effective_mass_transfer import (
    load_effective_mass_inputs,
    reduced_mass,
    run_effective_mass_transfer,
)

ROOT = Path(__file__).resolve().parents[1]
INP = ROOT / "data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml"
ZNSE = ROOT / "data/quantum_dots/qd-0004-toufanian-2021-znse-absorption.yaml"
MASSES = ROOT / "data/quantum_dots/effective_mass_inputs.yaml"


def _run() -> dict:
    return run_effective_mass_transfer(
        inp_dataset_path=INP,
        znse_dataset_path=ZNSE,
        effective_mass_path=MASSES,
    )


def test_literature_masses_and_reduced_mass_are_frozen() -> None:
    masses = load_effective_mass_inputs(MASSES)
    assert masses["InP"]["electron_effective_mass"] == 0.08
    assert masses["InP"]["hole_effective_mass"] == 0.64
    assert masses["ZnSe"]["electron_effective_mass"] == 0.16
    assert masses["ZnSe"]["hole_effective_mass"] == 0.75
    assert reduced_mass(0.08, 0.64) == pytest.approx(0.071111111111)
    assert reduced_mass(0.16, 0.75) == pytest.approx(0.131868131868)


def test_effective_mass_transfer_is_honest_negative_both_directions() -> None:
    metrics = _run()
    primary = metrics["framings"]["equivalent_diameter"]
    forward = primary["forward_inp_to_znse"]
    reverse = primary["reverse_znse_to_inp"]
    assert forward["no_holdout_fit"] is True
    assert reverse["no_holdout_fit"] is True
    assert forward["mass_scaled_transfer"]["mae_ev"] == pytest.approx(0.161570459)
    assert reverse["mass_scaled_transfer"]["mae_ev"] == pytest.approx(0.991542397)
    assert forward["mass_scaled_improvement_vs_bulk_gap_only_ev"] < 0.0
    assert reverse["mass_scaled_improvement_vs_bulk_gap_only_ev"] < 0.0
    assert forward["clears_predeclared_margin"] is False
    assert reverse["clears_predeclared_margin"] is False
    assert metrics["scientific_verdict"] == "MATERIAL_SPECIFIC_AFTER_EFFECTIVE_MASS_SCALING"


def test_controls_are_predeclared_and_separate() -> None:
    for item in _run()["framings"]["equivalent_diameter"].values():
        assert set(item["controls"]) == {
            "calibration_mean_null",
            "per_material_mean",
            "shuffled_size",
        }
        assert item["required_margin_ev"] == 0.05


def test_runner_is_deterministic() -> None:
    script = ROOT / "scripts/run_quantum_effective_mass_transfer.py"
    command = [sys.executable, str(script)]
    first = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    second = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    assert first.stdout == second.stdout
    assert json.loads(first.stdout)["scientific_verdict"] == "MATERIAL_SPECIFIC_AFTER_EFFECTIVE_MASS_SCALING"
