from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from physics_lab.engines.nuclear_prediction_reveal import (
    ELIGIBLE_STATUS,
    NON_MEASURED_VALUE_ONLY,
    SOURCE_PREDATES_REGISTRATION,
    TARGET_NOT_REVEALED,
    load_synthetic_reveal_config,
    run_synthetic_reveal_dry_run,
)
from physics_lab.registry.examples import load_example_config


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "examples" / "nuclear_prediction_synthetic_reveal.yaml"
PRED_0041 = ROOT / "prediction_registry" / "nuclear_masses" / "PRED-0041.yaml"


def test_synthetic_reveal_dry_run_labels_source_as_fake() -> None:
    result = run_synthetic_reveal_dry_run(ROOT, CONFIG)

    assert result["mode"] == "synthetic_reveal_dry_run"
    assert result["source"]["synthetic_source"] is True
    assert result["source"]["real_measurement_source"] is False
    assert result["source"]["source_kind"] == "synthetic_toy_measurement"
    assert result["verdict"] == "INCONCLUSIVE_SYNTHETIC_DRY_RUN"


def test_synthetic_reveal_dry_run_reports_partial_coverage_and_exclusions() -> None:
    result = run_synthetic_reveal_dry_run(ROOT, CONFIG)
    rows = {row["nuclide_id"]: row for row in result["comparison_rows"]}

    assert result["registry_snapshot"]["prediction_ids"] == ["PRED-0041"]
    assert result["coverage"]["target_rows"] == 4
    assert result["coverage"]["eligible_rows"] == 1
    assert result["coverage"]["unrevealed_rows"] == 1
    assert result["coverage"]["ineligible_rows"] == 2
    assert rows["Ni-76"]["eligibility_status"] == ELIGIBLE_STATUS
    assert rows["Ca-55"]["eligibility_status"] == TARGET_NOT_REVEALED
    assert rows["Zn-80"]["eligibility_status"] == NON_MEASURED_VALUE_ONLY
    assert rows["Ga-85"]["eligibility_status"] == SOURCE_PREDATES_REGISTRATION


def test_synthetic_reveal_dry_run_scores_only_eligible_synthetic_rows() -> None:
    result = run_synthetic_reveal_dry_run(ROOT, CONFIG)
    rows = {row["nuclide_id"]: row for row in result["comparison_rows"]}

    assert result["metrics"]["eligible_count"] == 1
    assert result["metrics"]["mae_mev"] == pytest.approx(0.201393)
    assert rows["Ni-76"]["signed_error_mev"] == pytest.approx(0.201393)
    assert rows["Zn-80"]["signed_error_mev"] is None
    assert rows["Ga-85"]["absolute_error_mev"] is None


def test_synthetic_reveal_dry_run_does_not_mutate_registry_inputs() -> None:
    before = PRED_0041.read_bytes()

    run_synthetic_reveal_dry_run(ROOT, CONFIG)

    assert PRED_0041.read_bytes() == before


def test_synthetic_reveal_config_rejects_real_source_label(tmp_path: Path) -> None:
    payload = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    payload["synthetic_source"]["real_measurement_source"] = True
    bad_config = tmp_path / "bad-synthetic-reveal.yaml"
    bad_config.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="real_measurement_source"):
        load_synthetic_reveal_config(bad_config)


def test_synthetic_reveal_example_loads_through_repository_examples() -> None:
    payload = load_example_config(CONFIG)

    assert payload["config_kind"] == "nuclear_prediction_synthetic_reveal"
    assert payload["synthetic_source"]["source_kind"] == "synthetic_toy_measurement"
