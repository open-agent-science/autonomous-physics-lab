"""Tests for PRED-0023 and PRED-0024 pairing/odd-even control registry entries (TASK-0229)."""

from __future__ import annotations

import math
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
PRED_DIR = REPO_ROOT / "prediction_registry" / "nuclear_masses"
NMD_0002_PATH = REPO_ROOT / "data" / "nuclear_masses" / "nmd-0002-curated-measured-slice.yaml"
HOLDOUT_PATH = REPO_ROOT / "data" / "nuclear_masses" / "post_ame2020_holdout.yaml"

PRED_IDS = ["PRED-0023", "PRED-0024"]

# Frozen baseline coefficients from RESULT-0015::model_fitted_semi_empirical
_AV = 15.51423612106804
_AS = 17.2931812095177
_AC = 0.6878156091568888
_AA = 23.846557883948485
_AP_BASE = 15.990845113398912

# Physical constants
_M_H = 1.00782503207   # u
_M_N = 1.00866491600   # u
_U_TO_MEV = 931.494013  # MeV/u


def _pairing_delta(Z: int, N: int, aP: float) -> float:
    A = Z + N
    if Z % 2 == 0 and N % 2 == 0:
        return +aP / math.sqrt(A)
    elif Z % 2 == 1 and N % 2 == 1:
        return -aP / math.sqrt(A)
    return 0.0


def _mass_excess_mev(Z: int, N: int, aP: float) -> float:
    A = Z + N
    B = (
        _AV * A
        - _AS * A ** (2 / 3)
        - _AC * Z * (Z - 1) / A ** (1 / 3)
        - _AA * (N - Z) ** 2 / A
        + _pairing_delta(Z, N, aP)
    )
    atomic_mass_u = Z * _M_H + N * _M_N - B / _U_TO_MEV
    return (atomic_mass_u - A) * _U_TO_MEV


def _load_pred(pred_id: str) -> dict:
    path = PRED_DIR / f"{pred_id}.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_nmd_0002_ids() -> set[str]:
    data = yaml.safe_load(NMD_0002_PATH.read_text(encoding="utf-8"))
    return {e["nuclide_id"] for e in data.get("entries", [])}


def _load_holdout_ids() -> set[str]:
    data = yaml.safe_load(HOLDOUT_PATH.read_text(encoding="utf-8"))
    return {e["nuclide_id"] for e in data.get("entries", [])}


# --- schema validity ---

@pytest.mark.parametrize("pred_id", PRED_IDS)
def test_required_fields_present(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    required = [
        "prediction_id", "title", "registry_status", "campaign_profile_id",
        "task_id", "evidence_class", "claim_ceiling", "registered_by",
        "registered_at_utc", "source_state", "target_set",
        "uncertainty_semantics", "reveal_conditions", "limitations",
        "review_boundary",
    ]
    for field in required:
        assert field in entry, f"{pred_id} missing required field: {field}"


@pytest.mark.parametrize("pred_id", PRED_IDS)
def test_registry_status_is_registered(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    assert entry["registry_status"] == "REGISTERED"


@pytest.mark.parametrize("pred_id", PRED_IDS)
def test_task_id_is_task_0229(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    assert entry["task_id"] == "TASK-0229"


@pytest.mark.parametrize("pred_id", PRED_IDS)
def test_live_fetch_not_allowed(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    assert entry["source_state"]["live_external_fetch_allowed"] is False


@pytest.mark.parametrize("pred_id", PRED_IDS)
def test_no_claim_promotion_pre_reveal(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    rb = entry["review_boundary"]
    assert rb["pre_reveal_claim_promotion_allowed"] is False
    assert rb["canonical_result_allowed_pre_reveal"] is False
    assert rb["retrospective_equivalence_forbidden"] is True


@pytest.mark.parametrize("pred_id", PRED_IDS)
def test_quantity_is_mass_excess_mev(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    ts = entry["target_set"]
    assert ts["quantity"] == "mass_excess_mev"
    assert ts["unit"] == "MeV"


# --- target consistency ---

@pytest.mark.parametrize("pred_id", PRED_IDS)
def test_a_equals_z_plus_n(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    for nuc in entry["target_set"]["target_nuclides"]:
        assert nuc["A"] == nuc["Z"] + nuc["N"], (
            f"{pred_id}: {nuc['nuclide_id']} A={nuc['A']} != Z+N={nuc['Z']+nuc['N']}"
        )


@pytest.mark.parametrize("pred_id", PRED_IDS)
def test_targets_absent_from_nmd_0002(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    nmd_ids = _load_nmd_0002_ids()
    for nuc in entry["target_set"]["target_nuclides"]:
        assert nuc["nuclide_id"] not in nmd_ids, (
            f"{pred_id}: target {nuc['nuclide_id']} is in training dataset NMD-0002"
        )


@pytest.mark.parametrize("pred_id", PRED_IDS)
def test_targets_absent_from_post_ame2020_holdout(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    holdout_ids = _load_holdout_ids()
    for nuc in entry["target_set"]["target_nuclides"]:
        assert nuc["nuclide_id"] not in holdout_ids, (
            f"{pred_id}: target {nuc['nuclide_id']} is in post-AME2020 holdout"
        )


# --- deterministic value reproduction ---

def test_pred_0023_values_reproduce() -> None:
    """PRED-0023: pairing +10% (aP = base * 1.10)."""
    aP = _AP_BASE * 1.10
    entry = _load_pred("PRED-0023")
    for nuc in entry["target_set"]["target_nuclides"]:
        expected = _mass_excess_mev(nuc["Z"], nuc["N"], aP)
        stored = float(nuc["predicted_value_mev"])
        assert abs(expected - stored) < 1e-5, (
            f"PRED-0023 {nuc['nuclide_id']}: recomputed {expected:.6f} != stored {stored:.6f}"
        )


def test_pred_0024_values_reproduce() -> None:
    """PRED-0024: null pairing (aP = 0.0)."""
    aP = 0.0
    entry = _load_pred("PRED-0024")
    for nuc in entry["target_set"]["target_nuclides"]:
        expected = _mass_excess_mev(nuc["Z"], nuc["N"], aP)
        stored = float(nuc["predicted_value_mev"])
        assert abs(expected - stored) < 1e-5, (
            f"PRED-0024 {nuc['nuclide_id']}: recomputed {expected:.6f} != stored {stored:.6f}"
        )


def test_odd_a_targets_identical_in_both_entries() -> None:
    """Odd-A nuclides must have identical predictions in PRED-0023 and PRED-0024."""
    p023 = {n["nuclide_id"]: n for n in _load_pred("PRED-0023")["target_set"]["target_nuclides"]}
    p024 = {n["nuclide_id"]: n for n in _load_pred("PRED-0024")["target_set"]["target_nuclides"]}
    for nid, nuc in p023.items():
        if nid not in p024:
            continue
        Z, N = nuc["Z"], nuc["N"]
        if (Z + N) % 2 == 1:  # odd-A
            v023 = float(nuc["predicted_value_mev"])
            v024 = float(p024[nid]["predicted_value_mev"])
            assert abs(v023 - v024) < 1e-9, (
                f"Odd-A {nid}: PRED-0023={v023} != PRED-0024={v024}; "
                "pairing delta must be zero for odd-A regardless of aP"
            )


def test_even_even_more_bound_in_pred_0023_than_pred_0024() -> None:
    """Even-even targets must have lower mass excess (more binding) in PRED-0023."""
    p023 = {n["nuclide_id"]: n for n in _load_pred("PRED-0023")["target_set"]["target_nuclides"]}
    p024 = {n["nuclide_id"]: n for n in _load_pred("PRED-0024")["target_set"]["target_nuclides"]}
    for nid, nuc in p023.items():
        if nid not in p024:
            continue
        Z, N = nuc["Z"], nuc["N"]
        if Z % 2 == 0 and N % 2 == 0:  # even-even
            v023 = float(nuc["predicted_value_mev"])
            v024 = float(p024[nid]["predicted_value_mev"])
            assert v023 < v024, (
                f"Even-even {nid}: PRED-0023={v023} should be < PRED-0024={v024} "
                "(higher pairing → more binding → lower mass excess)"
            )


def test_odd_odd_less_bound_in_pred_0023_than_pred_0024() -> None:
    """Odd-odd targets must have higher mass excess (less binding) in PRED-0023."""
    p023 = {n["nuclide_id"]: n for n in _load_pred("PRED-0023")["target_set"]["target_nuclides"]}
    p024 = {n["nuclide_id"]: n for n in _load_pred("PRED-0024")["target_set"]["target_nuclides"]}
    for nid, nuc in p023.items():
        if nid not in p024:
            continue
        Z, N = nuc["Z"], nuc["N"]
        if Z % 2 == 1 and N % 2 == 1:  # odd-odd
            v023 = float(nuc["predicted_value_mev"])
            v024 = float(p024[nid]["predicted_value_mev"])
            assert v023 > v024, (
                f"Odd-odd {nid}: PRED-0023={v023} should be > PRED-0024={v024} "
                "(higher pairing penalty → less binding → higher mass excess)"
            )
