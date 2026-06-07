"""Tests for the Pizzocaro VLBI per-window diagnostic ledger (TASK-0636)."""

from __future__ import annotations

import hashlib

import yaml

from scripts.build_atomic_pizzocaro_vlbi_window_ledger import (
    DEFAULT_CSV,
    DEFAULT_LEDGER,
    build_vlbi_window_ledger,
)


def _committed_ledger() -> dict:
    return yaml.safe_load(DEFAULT_LEDGER.read_text(encoding="utf-8"))


def test_committed_ledger_matches_fresh_build_from_source_csv() -> None:
    # Regeneration guard: the committed ledger must equal a deterministic rebuild
    # from the committed source CSV, so the ledger cannot drift from its source.
    assert _committed_ledger() == build_vlbi_window_ledger()


def test_ledger_records_actual_source_csv_checksum() -> None:
    ledger = _committed_ledger()
    expected_sha256 = hashlib.sha256(DEFAULT_CSV.read_bytes()).hexdigest()

    assert ledger["source"]["source_csv_sha256"] == expected_sha256


def test_ledger_has_ten_vlbi_windows_with_stable_ids_and_mjd_fields() -> None:
    ledger = _committed_ledger()
    windows = ledger["windows"]

    assert ledger["window_count"] == 10
    assert len(windows) == 10
    assert [w["window_id"] for w in windows] == [
        f"PIZZOCARO-VLBI-W{i:02d}" for i in range(1, 11)
    ]
    for window in windows:
        for field in ("mjd_start", "mjd_stop", "mjd_med"):
            assert isinstance(window[field], float)
        assert window["mjd_start"] < window["mjd_stop"]
        assert window["ratio_orientation"] == "Yb/Sr"
        assert isinstance(window["value_yb_sr_relative"], float)
        assert isinstance(window["final_uncertainty"], float)
        assert set(window["statistical_components"]) == {"uA1", "uA2", "uA3", "uA4"}
        assert set(window["systematic_components"]) == {
            "uB1_comb",
            "uB1_clock",
            "uB2",
            "uB4_comb",
            "uB4_clock",
        }


def test_ledger_is_diagnostic_only_and_covariance_blocked() -> None:
    ledger = _committed_ledger()

    assert ledger["diagnostic_only"] is True
    assert ledger["covariance"]["state"] == "COV_BLOCKED_SHARED_SYSTEMATICS"
    assert all(
        window["covariance_state"] == "COV_BLOCKED_SHARED_SYSTEMATICS"
        for window in ledger["windows"]
    )
    assert ledger["promotion_boundary"] == {
        "writes_acr_benchmark_rows": False,
        "writes_cross_window_aggregate_metric": False,
        "writes_benchmark_metrics": False,
        "writes_prediction_registry": False,
        "writes_canonical_result": False,
        "claim_promotion_allowed": False,
        "knowledge_promotion_allowed": False,
    }


def test_shared_systematics_are_window_invariant_components() -> None:
    ledger = _committed_ledger()
    shared = ledger["covariance"]["shared_systematic_components"]

    # The comb and link systematics are constant across windows, which is why
    # they are load-bearing for any cross-window covariance.
    assert "uB1_comb" in shared
    assert "uB4_comb" in shared
    for field in shared:
        values = {
            window["systematic_components"][field] for window in ledger["windows"]
        }
        assert len(values) == 1


def test_ledger_lives_under_source_artifacts_path() -> None:
    assert DEFAULT_LEDGER.name == "vlbi_per_window_diagnostic_ledger.yaml"
    assert "source_artifacts" in DEFAULT_LEDGER.parts
    assert DEFAULT_LEDGER.exists()
