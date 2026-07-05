"""Tests for the TASK-0920 contract execution of the ZnSe no-refit transfer.

The runner must execute exactly the TASK-0914 frozen contract: verified frozen
rows, harmonization, controls, and survival threshold; no refit and no metric
drift relative to the committed TASK-0842 engine it wraps.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from physics_lab.engines.quantum_cross_material_transfer import (
    run_cross_material_transfer,
)

ROOT = Path(__file__).resolve().parents[1]
INP_DATASET = ROOT / "data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml"
ZNSE_DATASET = ROOT / "data/quantum_dots/qd-0004-toufanian-2021-znse-absorption.yaml"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_quantum_znse_contract_transfer import (  # noqa: E402
    CONTRACT_INP_ROW_IDS,
    CONTRACT_ZNSE_ROW_IDS,
    ContractViolationError,
    _compute_metrics,
    contract_survival_outcome,
    verify_frozen_contract,
)


def test_frozen_contract_verifies_on_committed_inputs() -> None:
    # The committed datasets and engine constants must match the TASK-0914
    # frozen contract exactly; verification runs before any metric.
    verify_frozen_contract(
        inp_dataset_path=INP_DATASET, znse_dataset_path=ZNSE_DATASET
    )


def test_contract_violation_on_tampered_holdout_rows(tmp_path: Path) -> None:
    payload = yaml.safe_load(ZNSE_DATASET.read_text(encoding="utf-8"))
    # Excluding one frozen ZnSe row must stop the run even though the engine
    # itself would still accept nine direct rows.
    payload["entries"][0]["inclusion_status"] = "excluded"
    tampered = tmp_path / "qd-0004-toufanian-2021-znse-absorption.yaml"
    tampered.write_text(yaml.safe_dump(payload), encoding="utf-8")
    with pytest.raises(ContractViolationError):
        verify_frozen_contract(
            inp_dataset_path=INP_DATASET, znse_dataset_path=tampered
        )


def test_contract_survival_outcome_routing() -> None:
    assert contract_survival_outcome(
        clears_predeclared_margin=True, margin_ev=0.06
    )[0] == "PASS_CLEARS_PREDECLARED_MARGIN"
    assert contract_survival_outcome(
        clears_predeclared_margin=False, margin_ev=0.0466
    )[0] == "FAIL_TO_CLEAR_PREDECLARED_MARGIN"
    assert contract_survival_outcome(
        clears_predeclared_margin=False, margin_ev=-0.01
    )[0] == "NEGATIVE_MEMORY"
    assert contract_survival_outcome(
        clears_predeclared_margin=False, margin_ev=0.0
    )[0] == "NEGATIVE_MEMORY"


def test_metrics_carry_contract_metadata_and_frozen_parameters() -> None:
    metrics = _compute_metrics()
    assert metrics["task_id"] == "TASK-0920"
    contract = metrics["contract"]
    assert contract["contract_task_id"] == "TASK-0914"
    assert contract["engine_origin_task_id"] == "TASK-0842"
    assert (
        contract["contract_reference"]
        == "docs/reviews/quantum-znse-no-refit-transfer-contract.md"
    )
    assert contract["frozen_inp_row_ids"] == list(CONTRACT_INP_ROW_IDS)
    assert contract["frozen_znse_row_ids"] == list(CONTRACT_ZNSE_ROW_IDS)
    assert contract["tetra_edge_to_equiv_diameter_factor"] == 0.608291447
    assert contract["bulk_gap_ev"] == {"InP": 1.34, "ZnSe": 2.70}
    assert contract["required_margin_ev"] == 0.05
    assert contract["shuffle_seed"] == 842
    assert contract["primary_framing"] == "equivalent_diameter"
    assert contract["primary_direction"] == "forward_inp_to_znse"
    assert metrics["run_meta"]["agent_run_id"] == "AGENT-RUN-0090"
    assert len(metrics["run_meta"]["input_file_hashes"]) == 2


def test_contract_execution_reproduces_engine_metrics_exactly() -> None:
    # The runner is an exact workflow wrapper: it must not change any metric
    # produced by the committed TASK-0842 engine.
    wrapped = _compute_metrics()
    direct = run_cross_material_transfer(
        inp_dataset_path=INP_DATASET, znse_dataset_path=ZNSE_DATASET
    )
    assert wrapped["framings"] == direct["framings"]
    assert wrapped["primary_transfer_mae_ev"] == direct["primary_transfer_mae_ev"]
    assert (
        wrapped["primary_transfer_margin_vs_best_control_ev"]
        == direct["primary_transfer_margin_vs_best_control_ev"]
    )
    assert wrapped["scientific_verdict"] == direct["scientific_verdict"]


def test_primary_outcome_fails_to_clear_frozen_margin() -> None:
    metrics = _compute_metrics()
    margin = metrics["primary_transfer_margin_vs_best_control_ev"]
    assert metrics["primary_transfer_mae_ev"] == pytest.approx(0.09921632, abs=1e-6)
    assert metrics["primary_best_control_id"] == "per_material_mean"
    assert margin == pytest.approx(0.04658368, abs=1e-6)
    assert 0.0 < margin < 0.05
    assert metrics["primary_clears_predeclared_margin"] is False
    assert metrics["contract_survival_outcome"] == "FAIL_TO_CLEAR_PREDECLARED_MARGIN"
    assert "inconclusive/borderline" in metrics["contract_outcome_routing"]
    assert metrics["scientific_verdict"] == "INCONCLUSIVE"
    assert metrics["agent_verdict"] == "REVIEW_NEEDED"


def test_contract_run_is_deterministic() -> None:
    assert json.dumps(_compute_metrics(), sort_keys=True) == json.dumps(
        _compute_metrics(), sort_keys=True
    )


def test_runner_stdout_is_replayable_across_processes() -> None:
    script = ROOT / "scripts/run_quantum_znse_contract_transfer.py"
    runs = [
        subprocess.run(
            [sys.executable, str(script)],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        for _ in range(2)
    ]
    assert runs[0].stdout == runs[1].stdout
    payload = json.loads(runs[0].stdout)
    assert payload["contract_survival_outcome"] == "FAIL_TO_CLEAR_PREDECLARED_MARGIN"
    assert payload["primary_clears_predeclared_margin"] is False
