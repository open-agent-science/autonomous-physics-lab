"""Tests for the lepton g-2 cross-observable falsifier (TASK-0227)."""

from __future__ import annotations

from pathlib import Path

import pytest

from physics_lab.engines.lepton_g2_cross_check import (
    CANDIDATES,
    CONSISTENT_SIGMA_THRESHOLD,
    DEFAULT_DATA_PATH,
    ElectronResidual,
    INCONSISTENT_SIGMA_THRESHOLD,
    NULL_SIGMA_THRESHOLD,
    _classify,
    load_electron_g2_data,
    run_cross_check,
)


# ── Data file ─────────────────────────────────────────────────────────────

def test_default_data_path_exists() -> None:
    assert DEFAULT_DATA_PATH.exists(), (
        f"Electron g-2 data file missing at {DEFAULT_DATA_PATH}"
    )


def test_load_electron_g2_data_returns_both_alpha_sources() -> None:
    residuals = load_electron_g2_data()
    ids = {r.residual_id for r in residuals}
    assert "delta_a_e_cs" in ids
    assert "delta_a_e_rb" in ids


def test_residuals_have_opposite_signs() -> None:
    """The two α-source residuals must flip sign — that is the entire reason
    the cross-check looks at both rather than aggregating them."""
    residuals = {r.residual_id: r for r in load_electron_g2_data()}
    assert residuals["delta_a_e_cs"].delta_ae < 0
    assert residuals["delta_a_e_rb"].delta_ae > 0


def test_load_rejects_empty_file(tmp_path: Path) -> None:
    bad = tmp_path / "empty.yaml"
    bad.write_text("derived_residuals: []\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_electron_g2_data(bad)


# ── Classification thresholds ─────────────────────────────────────────────

def _residual(rid: str, value: float, sigma: float) -> ElectronResidual:
    return ElectronResidual(
        residual_id=rid,
        label=rid,
        delta_ae=value,
        sigma=sigma,
        alpha_source="test",
    )


def test_classify_null_when_prediction_below_measurement_noise() -> None:
    residuals = [_residual("a", -1.0e-12, 0.3e-12), _residual("b", 0.3e-12, 0.15e-12)]
    # |1e-14| / 3e-13 = 0.033, |1e-14| / 1.5e-13 = 0.067 → both below 0.5σ
    assert _classify(1.0e-14, residuals) == "null"


def test_classify_inconsistent_when_far_from_every_residual() -> None:
    residuals = [_residual("a", -1.0e-12, 0.3e-12), _residual("b", 0.3e-12, 0.15e-12)]
    # 1.0 is huge compared to residuals; both z-scores blow up
    assert _classify(1.0, residuals) == "inconsistent"


def test_classify_overfit_when_only_one_alpha_source_agrees() -> None:
    residuals = [
        _residual("a", -1.0e-12, 0.3e-12),   # z(+0.3e-12) = 4.3σ → inconsistent
        _residual("b", 0.3e-12, 0.15e-12),   # z(+0.3e-12) = 0σ  → consistent
    ]
    assert _classify(0.3e-12, residuals) == "overfit"


def test_classify_review_needed_for_mixed_marginal() -> None:
    # consistent-with-one (z=2), not-quite-inconsistent-with-other (z=2.5)
    residuals = [_residual("a", 0.0, 1.0e-13), _residual("b", 2.5e-13, 1.0e-13)]
    assert _classify(2.0e-13, residuals) == "review_needed"


def test_threshold_constants_are_ordered() -> None:
    assert 0 < NULL_SIGMA_THRESHOLD < CONSISTENT_SIGMA_THRESHOLD
    assert CONSISTENT_SIGMA_THRESHOLD < INCONSISTENT_SIGMA_THRESHOLD


# ── Candidate registry ────────────────────────────────────────────────────

def test_candidate_registry_is_small() -> None:
    """The cross-check is intentionally narrow; do not let the registry sprawl."""
    assert len(CANDIDATES) <= 5, (
        "Expanding the candidate registry requires a new maintainer-approved task."
    )


def test_each_candidate_has_required_fields() -> None:
    required = {"candidate_id", "muon_formula", "electron_formula", "value_fn", "notes"}
    for cand in CANDIDATES:
        missing = required - cand.keys()
        assert not missing, f"candidate {cand.get('candidate_id')!r} missing fields {missing}"


# ── Engine output ─────────────────────────────────────────────────────────

def test_run_cross_check_basic_shape() -> None:
    result = run_cross_check()
    assert result["task_id"] == "TASK-0227"
    assert "global_verdict" in result
    assert "candidates" in result
    assert len(result["candidates"]) == len(CANDIDATES)
    assert "guardrails" in result


def test_run_cross_check_includes_both_residual_comparisons() -> None:
    result = run_cross_check()
    for cand in result["candidates"]:
        ids = {comp["residual_id"] for comp in cand["comparisons"]}
        assert "delta_a_e_cs" in ids
        assert "delta_a_e_rb" in ids


def test_f4_hit_is_inconsistent_at_electron() -> None:
    """The F4 guardrail-screened muon hit must fail the electron cross-check.

    After m_mu → m_e the (m_mu/m_e)^-2 factor collapses to 1 and the analog
    is α^3 × (m_e/m_tau)^-2 ≈ 4.7 — orders of magnitude away from any plausible
    Δa_e. This is the headline negative result of the falsifier.
    """
    result = run_cross_check()
    f4 = next(c for c in result["candidates"] if c["candidate_id"] == "F4_hit")
    assert f4["verdict"] == "inconsistent"
    assert f4["electron_value"] > 1.0
    for comp in f4["comparisons"]:
        assert comp["z_score"] > INCONSISTENT_SIGMA_THRESHOLD


def test_f3_one_third_is_null_at_electron() -> None:
    """The F3 c=1/3 hadronic-style candidate produces an electron analog that
    sits below current Δa_e uncertainty, so the cross-check is uninformative."""
    result = run_cross_check()
    f3 = next(c for c in result["candidates"] if c["candidate_id"] == "F3_one_third")
    assert f3["verdict"] == "null"
    for comp in f3["comparisons"]:
        assert comp["relative_magnitude"] < NULL_SIGMA_THRESHOLD


def test_naive_scaling_is_null_at_electron() -> None:
    result = run_cross_check()
    naive = next(c for c in result["candidates"] if c["candidate_id"] == "naive_msq_scaling")
    assert naive["verdict"] == "null"


def test_global_verdict_is_inconsistent_at_electron() -> None:
    """Headline outcome: at least one EXP-0010 candidate is ruled out by the
    cross-check, so the global verdict should reflect the negative result."""
    result = run_cross_check()
    assert result["global_verdict"] == "INCONSISTENT_AT_ELECTRON"


def test_no_discovery_or_bsm_wording_in_result() -> None:
    """Guardrail: result payload must not slip into discovery-style framing."""
    import json
    blob = json.dumps(run_cross_check()).lower()
    for forbidden in [
        "discovery",
        "bsm signal",
        "anomaly solved",
        "electron g-2 formula",
        "breakthrough",
    ]:
        assert forbidden not in blob, f"unexpected promotion wording: {forbidden!r}"
