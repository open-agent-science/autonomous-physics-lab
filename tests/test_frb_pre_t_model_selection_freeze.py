from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_frb_pre_t_model_selection_freeze.py"
CONTRACT = ROOT / "data" / "radio_transients" / "frb_pre_t_model_selection_contract.yaml"
SURFACE = ROOT / "data" / "radio_transients" / "frb_pre_t_repeater_propensity_model_surface.yaml"


def _load_module():
    spec = importlib.util.spec_from_file_location("frb_task0964", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_contract_freezes_no_label_selection() -> None:
    contract = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    assert contract["feature_boundary"]["label_contact_allowed"] is False
    assert contract["feature_boundary"]["label_columns_read"] == []
    assert contract["feature_boundary"]["label_use_for_selection"] == "none"
    assert contract["frozen_scoring_rule"]["score_pre_t"] == (
        "score_pre_t = log1p(E_upper_hours + E_lower_hours)"
    )


def test_committed_surface_is_frozen_and_label_free() -> None:
    payload = yaml.safe_load(SURFACE.read_text(encoding="utf-8"))
    assert payload["surface_id"] == "FRB-PRET-MODEL-SURFACE-0001"
    assert payload["status"] == "frozen_model_surface"
    assert payload["selection"]["selected_model_id"] == "gate_total_exposure_log1p"
    assert payload["feature_boundary"]["label_contact"] is False
    assert payload["feature_boundary"]["columns_read"] == [
        "source_id",
        "E_upper_hours",
        "E_lower_hours",
        "score_pre_t",
    ]
    assert payload["per_source_score_count"] == 479
    assert payload["selection"]["selected_model_nonzero_rows"] == 465
    assert payload["selection"]["constant_null_unique_scores"] == 1
    assert "prediction_registry_entry" in payload["output_routing"]
    assert payload["output_routing"]["prediction_registry_entry"] == "none"


def test_runner_reproduces_committed_surface_digest(tmp_path: Path) -> None:
    module = _load_module()
    output = tmp_path / "surface.yaml"
    review = tmp_path / "review.md"
    replay = module.build_freeze(
        contract_path=CONTRACT,
        output_path=output,
        review_note_path=review,
        generated_at_utc="2026-07-09T00:00:00Z",
    )
    committed = yaml.safe_load(SURFACE.read_text(encoding="utf-8"))
    assert replay["per_source_scores_sha256"] == committed["per_source_scores_sha256"]
    assert replay["per_source_scores"] == committed["per_source_scores"]
    assert review.read_text(encoding="utf-8").startswith("# FRB Pre-T Model Selection Freeze")


def test_runner_blocks_scoring_rule_drift(tmp_path: Path) -> None:
    module = _load_module()
    contract = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    contract["frozen_scoring_rule"]["score_pre_t"] = "score_pre_t = E_upper_hours"
    bad_contract = tmp_path / "bad_contract.yaml"
    bad_contract.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
    with pytest.raises(SystemExit, match="scoring rule drifted"):
        module.build_freeze(
            contract_path=bad_contract,
            output_path=tmp_path / "surface.yaml",
            review_note_path=tmp_path / "review.md",
            generated_at_utc="2026-07-09T00:00:00Z",
        )
