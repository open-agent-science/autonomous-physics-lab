"""Tests for the Stellar M-L high-mass DEBCat transfer benchmark (TASK-0837).

Covers: the frozen RESULT-0022 predictor is not refit, determinism / numeric
regression of the transfer metrics, the predeclared controls-first contract,
and the standalone sandbox runner that emits AGENT-RUN-0082.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from physics_lab.engines import stellar_ml_high_mass_transfer as eng
from physics_lab.engines.stellar_ml_high_mass_transfer import (
    ALPHA_FROZEN,
    HIGH_MASS_THRESHOLD_SOLAR,
    SURVIVAL_MARGIN_DEX,
    compute_transfer_metrics,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_stellar_ml_high_mass_transfer.py"


def test_frozen_predictor_matches_result_0022_and_is_not_refit() -> None:
    m = compute_transfer_metrics()
    fp = m["frozen_predictor"]
    # The predictor is the RESULT-0022 train-fitted alpha, frozen, not refit.
    assert ALPHA_FROZEN == 4.526004
    assert fp["alpha_frozen"] == 4.526004
    assert fp["source_result_id"] == "RESULT-0022"
    assert fp["refit_on_holdout"] is False
    assert fp["fixed_intercept_log_l0"] == 0.0
    # It must re-derive exactly from the committed main-sequence train lane.
    assert fp["alpha_rederived_from_committed_main_sequence_train"] == 4.526004


def test_engine_is_deterministic_and_regression_pinned() -> None:
    a = compute_transfer_metrics()
    b = compute_transfer_metrics()
    assert a == b, "transfer engine is not deterministic"

    prim = a["primary_high_mass_main_sequence_holdout"]
    # Disjoint high-mass regime composition (matches the TASK-0819 scout feasibility check).
    hm = a["regime_composition"]["high_mass_all_stage"]
    assert hm["component_rows"] == 217
    assert hm["distinct_systems"] == 121

    # Primary stage-matched high-mass holdout: frozen-relation transfer error and controls.
    assert prim["train_count"] == 43
    assert prim["holdout_count"] == 24
    assert prim["holdout_systems"] == 15
    assert prim["frozen_relation_holdout_mae_dex"] == 0.334564
    assert prim["controls_holdout_mae_dex"]["null_massband_median"] == 0.522176
    assert prim["controls_holdout_mae_dex"]["mass_matched_massband_mean"] == 0.483879
    assert prim["best_control_name"] == "mass_matched_massband_mean"
    assert prim["frozen_minus_best_control_dex"] == 0.149315
    assert prim["clears_survival_margin"] is True
    assert prim["beats_all_shuffle_seeds"] is True

    assert a["transfers_to_high_mass"] is True
    assert a["verdict"] == "TRANSFERS_TO_HIGH_MASS_UNDER_CONTROLS"


def test_predeclared_controls_first_contract() -> None:
    m = compute_transfer_metrics()
    pc = m["predeclared_contract"]
    assert HIGH_MASS_THRESHOLD_SOLAR == 2.0
    assert pc["high_mass_threshold_solar"] == 2.0
    assert pc["split_key"] == "system_id"
    assert pc["survival_margin_dex"] == SURVIVAL_MARGIN_DEX == 0.04
    assert pc["frozen_before_holdout_read"] is True
    # Null, shuffled, and mass-matched controls are all present.
    assert set(pc["controls"]) == {
        "null_massband_median",
        "mass_matched_massband_mean",
        "shuffled_target_best",
    }
    # Experimental judge (DEBCat dynamical masses).
    assert "DEBCat dynamical masses" in pc["judge"]
    # The survival rule is "frozen minus best control >= margin" AND beats every shuffle.
    prim = m["primary_high_mass_main_sequence_holdout"]
    expected_clears = prim["frozen_minus_best_control_dex"] >= SURVIVAL_MARGIN_DEX
    assert prim["clears_survival_margin"] is expected_clears


def test_secondary_all_stage_stratum_is_reported() -> None:
    m = compute_transfer_metrics()
    sec = m["secondary_all_stage_high_mass_holdout"]
    assert sec["holdout_count"] == 56
    # All four stages appear in the by-stage high-mass holdout diagnostic.
    by_stage = m["by_stage_high_mass_holdout_mae_dex"]
    assert set(by_stage) == {"main_sequence_compatible", "subgiant", "evolved", "unknown"}
    # Luminosity provenance sensitivity stratifies catalogue vs Stefan-Boltzmann rows.
    prov = m["luminosity_provenance_sensitivity_primary_holdout"]
    assert "debcat_catalogue_reported_logL" in prov


def test_frozen_alpha_drift_guard_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    # If the committed rows ever stop reproducing the frozen alpha, the engine
    # must refuse to transfer a drifted relation rather than silently proceeding.
    monkeypatch.setattr(eng, "ALPHA_FROZEN", 3.5, raising=True)
    with pytest.raises(ValueError, match="does not reproduce"):
        compute_transfer_metrics()


def test_runner_emits_sandbox_agent_run(tmp_path: Path) -> None:
    out_dir = tmp_path / "AGENT-RUN-0082"
    subprocess.run(
        [sys.executable, str(SCRIPT), "--out-dir", str(out_dir)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    metrics = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))
    assert (out_dir / "report.md").exists()
    assert metrics["agent_run_id"] == "AGENT-RUN-0082"
    assert metrics["task_id"] == "TASK-0837"
    assert metrics["code_reference"] == "physics_lab/engines/stellar_ml_high_mass_transfer.py"
    # Gate-B-replayable provenance is recorded.
    assert metrics["engine_version"]
    assert metrics["command"].startswith("python3 scripts/run_stellar_ml_high_mass_transfer.py")
    for entry in metrics["input_file_hashes"].values():
        assert "path" in entry and len(entry["sha256"]) == 64
    # Sandbox boundary: no canonical result or claim promotion.
    assert metrics["promotion_boundary"]["writes_canonical_result"] is False
    assert metrics["promotion_boundary"]["claim_promotion_allowed"] is False
    assert metrics["verdict"] == "TRANSFERS_TO_HIGH_MASS_UNDER_CONTROLS"


def test_runner_emits_gate_a_result_package(tmp_path: Path) -> None:
    out_dir = tmp_path / "AGENT-RUN-0085"
    result_dir = tmp_path / "RESULT-0024"
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--skip-sandbox-output",
            "--out-dir",
            str(out_dir),
            "--result-out-dir",
            str(result_dir),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result = yaml.safe_load((result_dir / "result.yaml").read_text(encoding="utf-8"))
    metrics = json.loads((result_dir / "metrics.json").read_text(encoding="utf-8"))

    assert result["result_id"] == "RESULT-0024"
    assert result["task_id"] == "TASK-0849"
    assert result["experiment_id"] == "EXP-0017"
    assert result["hypothesis_id"] == "HYP-0017"
    assert result["review_tier"] == "AGENT_PUBLISHED"
    assert result["best_verdict"] == "VALID_IN_RANGE"
    assert result["verification"]["passed"] is True
    assert result["verification"]["checks"][0]["status"] == "PASS"
    assert result["agent_proposal_evaluation"]["gates_checked"]["no_protected_artifact_rewrite"] is True
    assert result["comparison_summary"][0]["absolute_difference"] == 0.149315
    assert metrics["publication_boundary"]["refit_on_high_mass_holdout"] is False
    assert metrics["publication_boundary"]["claim_promotion_allowed"] is False

    for name in (
        "report.md",
        "metrics.json",
        "gate_a_report.md",
        "claim_update.md",
        "claim_update.patch.md",
        "knowledge_update.md",
        "knowledge_update.patch.md",
        "review_summary.md",
        "review_metadata.yaml",
    ):
        assert (result_dir / name).exists()
    for entry in result["input_file_hashes"].values():
        assert "path" in entry and len(entry["sha256"]) == 64


def test_runner_is_deterministic(tmp_path: Path) -> None:
    def run(target: Path) -> str:
        subprocess.run(
            [sys.executable, str(SCRIPT), "--out-dir", str(target)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return (target / "metrics.json").read_text(encoding="utf-8")

    first = run(tmp_path / "a")
    second = run(tmp_path / "b")
    assert first == second, "runner metrics.json is not reproducible"
