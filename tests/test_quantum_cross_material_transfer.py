"""Tests for the TASK-0842 cross-material confinement transfer benchmark."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

from physics_lab.engines.quantum_cross_material_transfer import (
    BULK_GAP_EV,
    REQUIRED_MARGIN_EV,
    load_inp_rows,
    load_znse_rows,
    run_cross_material_transfer,
)

ROOT = Path(__file__).resolve().parents[1]
INP_DATASET = ROOT / "data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml"
ZNSE_DATASET = ROOT / "data/quantum_dots/qd-0004-toufanian-2021-znse-absorption.yaml"


def _run() -> dict:
    return run_cross_material_transfer(
        inp_dataset_path=INP_DATASET, znse_dataset_path=ZNSE_DATASET
    )


def test_loaders_admit_only_direct_size_rows_per_material() -> None:
    inp = load_inp_rows(INP_DATASET)
    znse = load_znse_rows(ZNSE_DATASET)
    assert len(inp) == 6
    assert len(znse) == 10
    assert {row.material for row in inp} == {"InP"}
    assert {row.material for row in znse} == {"ZnSe"}
    # ZnSe diameter is used verbatim as the equivalent diameter; InP tetrahedral
    # edge is converted to a smaller equal-volume sphere diameter.
    assert all(row.equiv_diameter_nm == row.size_nm for row in znse)
    assert all(row.equiv_diameter_nm < row.size_nm for row in inp)


def test_confinement_axis_uses_explicit_bulk_gaps_not_fitted() -> None:
    inp = load_inp_rows(INP_DATASET)
    assert BULK_GAP_EV["InP"] == 1.34
    assert BULK_GAP_EV["ZnSe"] == 2.70
    # Confinement is the observed E1s minus the explicit bulk-gap input.
    row = inp[0]
    assert row.confinement_ev == pytest.approx(row.value_ev - 1.34)


def test_wrong_material_rows_are_rejected() -> None:
    with pytest.raises(ValueError):
        load_inp_rows(ZNSE_DATASET)
    with pytest.raises(ValueError):
        load_znse_rows(INP_DATASET)


def test_primary_forward_transfer_is_inconclusive_under_predeclared_margin() -> None:
    metrics = _run()
    # Frozen reveal: the InP-calibrated curve beats the best control on ZnSe but
    # does not clear the predeclared 0.05 eV survival margin -> INCONCLUSIVE.
    assert metrics["primary_framing"] == "equivalent_diameter"
    assert metrics["primary_direction"] == "forward_inp_to_znse"
    assert metrics["required_margin_ev"] == REQUIRED_MARGIN_EV
    assert metrics["primary_transfer_mae_ev"] == pytest.approx(0.09921632, abs=1e-6)
    assert metrics["primary_best_control_id"] == "per_material_mean"
    assert metrics["primary_best_control_mae_ev"] == pytest.approx(0.1458, abs=1e-6)
    margin = metrics["primary_transfer_margin_vs_best_control_ev"]
    assert margin == pytest.approx(0.04658368, abs=1e-6)
    assert 0.0 < margin < REQUIRED_MARGIN_EV
    assert metrics["primary_clears_predeclared_margin"] is False
    assert metrics["scientific_verdict"] == "INCONCLUSIVE"
    assert metrics["agent_verdict"] == "REVIEW_NEEDED"


def test_transferred_model_beats_shuffled_size_control_both_directions() -> None:
    metrics = _run()
    equiv = metrics["framings"]["equivalent_diameter"]
    for direction in ("forward_inp_to_znse", "reverse_znse_to_inp"):
        transfer = equiv[direction]["transfer"]
        transferred = transfer["transferred"]["mae_ev"]
        shuffled = transfer["controls"]["shuffled_size"]["mae_ev"]
        assert transferred < shuffled


def test_reverse_direction_clears_margin_and_is_reported() -> None:
    metrics = _run()
    reverse = metrics["framings"]["equivalent_diameter"]["reverse_znse_to_inp"]
    assert reverse["calibration_material"] == "ZnSe"
    assert reverse["holdout_material"] == "InP"
    assert reverse["transfer"]["clears_predeclared_margin"] is True


def test_characteristic_length_framing_fails_to_beat_controls() -> None:
    metrics = _run()
    forward = metrics["framings"]["characteristic_length"]["forward_inp_to_znse"]
    # Without the morphology conversion the raw-edge model misses the ZnSe
    # diameter regime and does not clear the margin.
    assert forward["transfer"]["clears_predeclared_margin"] is False


def test_no_refit_models_are_frozen_from_calibration_material() -> None:
    metrics = _run()
    equiv = metrics["framings"]["equivalent_diameter"]
    forward_model = equiv["forward_inp_to_znse"]["frozen_model"]
    reverse_model = equiv["reverse_znse_to_inp"]["frozen_model"]
    # The two directions calibrate on different materials, so the frozen
    # coefficients differ; neither is fitted on its holdout.
    assert forward_model["exponent_n"] != reverse_model["exponent_n"]
    assert forward_model["coefficient_C"] != reverse_model["coefficient_C"]


def test_run_is_deterministic() -> None:
    assert json.dumps(_run(), sort_keys=True) == json.dumps(_run(), sort_keys=True)


def test_runner_writes_sandbox_run_and_is_replayable(tmp_path: Path) -> None:
    script = ROOT / "scripts/run_quantum_cross_material_transfer.py"
    first = subprocess.run(
        [sys.executable, str(script)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    second = subprocess.run(
        [sys.executable, str(script)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    # Cross-process determinism: identical stdout summaries.
    assert first.stdout == second.stdout
    payload = json.loads(first.stdout)
    assert payload["scientific_verdict"] == "INCONCLUSIVE"
    assert payload["primary_clears_predeclared_margin"] is False
