"""Tests for PRED-0029 and PRED-0030 isotope-chain extrapolation registry entries (TASK-0232)."""

from __future__ import annotations

import math
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
PRED_DIR = REPO_ROOT / "prediction_registry" / "nuclear_masses"
NMD_0002_PATH = REPO_ROOT / "data" / "nuclear_masses" / "nmd-0002-curated-measured-slice.yaml"
HOLDOUT_PATH = REPO_ROOT / "data" / "nuclear_masses" / "post_ame2020_holdout.yaml"

PRED_IDS = ["PRED-0029", "PRED-0030"]

# Frozen baseline coefficients from RESULT-0015::model_fitted_semi_empirical
_AV = 15.51423612106804
_AS = 17.2931812095177
_AC = 0.6878156091568888
_AA_BASE = 23.846557883948485
_AA_PLUS_15 = _AA_BASE * 1.15
_AP = 15.990845113398912

# Physical constants matching physics_lab/engines/nuclear_masses.py
_M_H = 1.00782503223   # u
_M_N = 1.00866491595   # u
_U_TO_MEV = 931.49410242  # MeV/u


def _pairing_delta(Z: int, N: int, aP: float) -> float:
    A = Z + N
    if Z % 2 == 0 and N % 2 == 0:
        return +aP / math.sqrt(A)
    elif Z % 2 == 1 and N % 2 == 1:
        return -aP / math.sqrt(A)
    return 0.0


def _mass_excess_mev(Z: int, N: int, aA: float) -> float:
    A = Z + N
    B = (
        _AV * A
        - _AS * A ** (2 / 3)
        - _AC * Z * (Z - 1) / A ** (1 / 3)
        - aA * (N - Z) ** 2 / A
        + _pairing_delta(Z, N, _AP)
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
def test_task_id_is_task_0232(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    assert entry["task_id"] == "TASK-0232"


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


@pytest.mark.parametrize("pred_id", PRED_IDS)
def test_all_targets_are_even_even(pred_id: str) -> None:
    """Both batches contain only even-even nuclei."""
    entry = _load_pred(pred_id)
    for nuc in entry["target_set"]["target_nuclides"]:
        Z, N = nuc["Z"], nuc["N"]
        assert Z % 2 == 0 and N % 2 == 0, (
            f"{pred_id}: {nuc['nuclide_id']} is not even-even (Z={Z}, N={N})"
        )


# --- chain structure ---

def test_pred_0029_is_sn_chain_z50() -> None:
    """PRED-0029 targets must all have Z=50 (Tin chain)."""
    entry = _load_pred("PRED-0029")
    for nuc in entry["target_set"]["target_nuclides"]:
        assert nuc["Z"] == 50, (
            f"PRED-0029: {nuc['nuclide_id']} has Z={nuc['Z']}, expected Z=50 for Sn chain"
        )


def test_pred_0030_is_zn_chain_z30() -> None:
    """PRED-0030 targets must all have Z=30 (Zinc chain)."""
    entry = _load_pred("PRED-0030")
    for nuc in entry["target_set"]["target_nuclides"]:
        assert nuc["Z"] == 30, (
            f"PRED-0030: {nuc['nuclide_id']} has Z={nuc['Z']}, expected Z=30 for Zn chain"
        )


def test_pred_0029_neutron_numbers_increase_monotonically() -> None:
    """PRED-0029 targets must be ordered by increasing N."""
    entry = _load_pred("PRED-0029")
    neutron_numbers = [nuc["N"] for nuc in entry["target_set"]["target_nuclides"]]
    assert neutron_numbers == sorted(neutron_numbers), (
        f"PRED-0029: neutron numbers are not monotonically increasing: {neutron_numbers}"
    )


def test_pred_0030_neutron_numbers_increase_monotonically() -> None:
    """PRED-0030 targets must be ordered by increasing N."""
    entry = _load_pred("PRED-0030")
    neutron_numbers = [nuc["N"] for nuc in entry["target_set"]["target_nuclides"]]
    assert neutron_numbers == sorted(neutron_numbers), (
        f"PRED-0030: neutron numbers are not monotonically increasing: {neutron_numbers}"
    )


# --- deterministic value reproduction ---

def test_pred_0029_values_reproduce() -> None:
    """PRED-0029: base fitted model (aA = base, no asymmetry perturbation)."""
    entry = _load_pred("PRED-0029")
    for nuc in entry["target_set"]["target_nuclides"]:
        expected = _mass_excess_mev(nuc["Z"], nuc["N"], _AA_BASE)
        stored = float(nuc["predicted_value_mev"])
        assert abs(expected - stored) < 1e-4, (
            f"PRED-0029 {nuc['nuclide_id']}: recomputed {expected:.6f} != stored {stored:.6f}"
        )


def test_pred_0030_values_reproduce() -> None:
    """PRED-0030: asymmetry-enhanced model (aA = base * 1.15)."""
    entry = _load_pred("PRED-0030")
    for nuc in entry["target_set"]["target_nuclides"]:
        expected = _mass_excess_mev(nuc["Z"], nuc["N"], _AA_PLUS_15)
        stored = float(nuc["predicted_value_mev"])
        assert abs(expected - stored) < 1e-4, (
            f"PRED-0030 {nuc['nuclide_id']}: recomputed {expected:.6f} != stored {stored:.6f}"
        )


def test_pred_0030_mass_excess_higher_than_base_model() -> None:
    """Enhanced asymmetry must raise mass excess (reduce binding) for all even-even Zn targets."""
    entry = _load_pred("PRED-0030")
    for nuc in entry["target_set"]["target_nuclides"]:
        base_me = _mass_excess_mev(nuc["Z"], nuc["N"], _AA_BASE)
        stored = float(nuc["predicted_value_mev"])
        assert stored > base_me, (
            f"PRED-0030 {nuc['nuclide_id']}: asym+15% mass_excess={stored:.6f} should be "
            f"> base model {base_me:.6f} (higher asymmetry penalty → less binding)"
        )


def test_pred_0030_asymmetry_delta_grows_with_neutron_excess() -> None:
    """The asymmetry perturbation delta must increase as N-Z increases along the Zn chain."""
    entry = _load_pred("PRED-0030")
    deltas = []
    for nuc in entry["target_set"]["target_nuclides"]:
        base_me = _mass_excess_mev(nuc["Z"], nuc["N"], _AA_BASE)
        asym_me = float(nuc["predicted_value_mev"])
        deltas.append(asym_me - base_me)
    for i in range(len(deltas) - 1):
        assert deltas[i] < deltas[i + 1], (
            f"PRED-0030: asymmetry delta at step {i} ({deltas[i]:.4f}) should be < "
            f"delta at step {i+1} ({deltas[i+1]:.4f})"
        )
