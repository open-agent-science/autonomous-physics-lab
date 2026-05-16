"""Tests for PRED-0037 and PRED-0038 minimal-complexity form-variant registry entries (TASK-0236)."""

from __future__ import annotations

import math
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
PRED_DIR = REPO_ROOT / "prediction_registry" / "nuclear_masses"
NMD_0002_PATH = REPO_ROOT / "data" / "nuclear_masses" / "nmd-0002-curated-measured-slice.yaml"
HOLDOUT_PATH = REPO_ROOT / "data" / "nuclear_masses" / "post_ame2020_holdout.yaml"

PRED_IDS = ["PRED-0037", "PRED-0038"]

# Frozen baseline coefficients from RESULT-0015::model_fitted_semi_empirical.
_AV = 15.51423612106804
_AS = 17.2931812095177
_AC = 0.6878156091568888
_AA = 23.846557883948485
_AP = 15.990845113398912

# physics_lab.engines.nuclear_masses constants.
_M_H = 1.00782503223
_M_N = 1.00866491595
_U_TO_MEV = 931.49410242


def _pairing_sign(z: int, n: int) -> int:
    if z % 2 == 0 and n % 2 == 0:
        return 1
    if z % 2 == 1 and n % 2 == 1:
        return -1
    return 0


def _binding_coulomb_z_squared(z: int, n: int) -> float:
    """PRED-0037 form: Coulomb term uses Z^2 instead of Z*(Z-1); standard 1/sqrt(A) pairing."""
    a = z + n
    af = float(a)
    return (
        _AV * af
        - _AS * af ** (2 / 3)
        - _AC * (z * z) / af ** (1 / 3)
        - _AA * (n - z) ** 2 / af
        + _pairing_sign(z, n) * _AP / math.sqrt(af)
    )


def _binding_pairing_inverse_a(z: int, n: int) -> float:
    """PRED-0038 form: pairing scales as aP/A instead of aP/sqrt(A); standard Z*(Z-1) Coulomb."""
    a = z + n
    af = float(a)
    return (
        _AV * af
        - _AS * af ** (2 / 3)
        - _AC * z * (z - 1) / af ** (1 / 3)
        - _AA * (n - z) ** 2 / af
        + _pairing_sign(z, n) * _AP / af
    )


def _mass_excess_mev(z: int, n: int, binding_mev: float) -> float:
    a = z + n
    atomic_mass_u = z * _M_H + n * _M_N - binding_mev / _U_TO_MEV
    return (atomic_mass_u - a) * _U_TO_MEV


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
        "prediction_id",
        "title",
        "registry_status",
        "campaign_profile_id",
        "task_id",
        "evidence_class",
        "claim_ceiling",
        "registered_by",
        "registered_at_utc",
        "source_state",
        "target_set",
        "uncertainty_semantics",
        "reveal_conditions",
        "limitations",
        "review_boundary",
    ]
    for field in required:
        assert field in entry, f"{pred_id} missing required field: {field}"


@pytest.mark.parametrize("pred_id", PRED_IDS)
def test_prediction_id_matches_filename(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    assert entry["prediction_id"] == pred_id


@pytest.mark.parametrize("pred_id", PRED_IDS)
def test_registry_status_is_registered(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    assert entry["registry_status"] == "REGISTERED"


@pytest.mark.parametrize("pred_id", PRED_IDS)
def test_task_id_is_task_0236(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    assert entry["task_id"] == "TASK-0236"


@pytest.mark.parametrize("pred_id", PRED_IDS)
def test_evidence_class_is_prospective(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    assert entry["evidence_class"] == "prospective_prediction_registry"


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
    assert rb["post_reveal_claim_promotion_requires_review"] is True
    assert rb["retrospective_equivalence_forbidden"] is True


@pytest.mark.parametrize("pred_id", PRED_IDS)
def test_quantity_is_mass_excess_mev(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    ts = entry["target_set"]
    assert ts["quantity"] == "mass_excess_mev"
    assert ts["unit"] == "MeV"


@pytest.mark.parametrize("pred_id", PRED_IDS)
def test_uncertainty_is_point_estimate_only(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    assert entry["uncertainty_semantics"]["type"] == "point_estimate_only"
    for nuc in entry["target_set"]["target_nuclides"]:
        assert nuc["uncertainty_mev"] is None


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
def test_target_batch_is_frontier_next_row(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    assert entry["target_set"]["label"] == "frontier-next-row"
    ids = [n["nuclide_id"] for n in entry["target_set"]["target_nuclides"]]
    assert ids == ["Ca-55", "Ni-76", "Zn-80", "Ga-85"]


# --- deterministic value reproduction ---


def test_pred_0037_values_reproduce() -> None:
    """PRED-0037: Coulomb Z^2 form, standard 1/sqrt(A) pairing."""
    entry = _load_pred("PRED-0037")
    assert entry["source_state"]["model_reference"]["model_id"] == (
        "RESULT-0015::model_fitted_semi_empirical::coulomb_z_squared_form"
    )
    for nuc in entry["target_set"]["target_nuclides"]:
        binding = _binding_coulomb_z_squared(nuc["Z"], nuc["N"])
        expected = round(_mass_excess_mev(nuc["Z"], nuc["N"], binding), 6)
        stored = float(nuc["predicted_value_mev"])
        assert abs(expected - stored) < 1e-6, (
            f"PRED-0037 {nuc['nuclide_id']}: recomputed {expected:.6f} != stored {stored:.6f}"
        )


def test_pred_0038_values_reproduce() -> None:
    """PRED-0038: standard Z*(Z-1) Coulomb, pairing 1/A scaling."""
    entry = _load_pred("PRED-0038")
    assert entry["source_state"]["model_reference"]["model_id"] == (
        "RESULT-0015::model_fitted_semi_empirical::pairing_inverse_a_scaling"
    )
    for nuc in entry["target_set"]["target_nuclides"]:
        binding = _binding_pairing_inverse_a(nuc["Z"], nuc["N"])
        expected = round(_mass_excess_mev(nuc["Z"], nuc["N"], binding), 6)
        stored = float(nuc["predicted_value_mev"])
        assert abs(expected - stored) < 1e-6, (
            f"PRED-0038 {nuc['nuclide_id']}: recomputed {expected:.6f} != stored {stored:.6f}"
        )


def test_pred_0038_odd_a_targets_equal_pred_0001() -> None:
    """Odd-A targets in PRED-0038 must equal PRED-0001 by construction (pairing zero)."""
    p001 = {n["nuclide_id"]: n for n in _load_pred("PRED-0001")["target_set"]["target_nuclides"]}
    p038 = {n["nuclide_id"]: n for n in _load_pred("PRED-0038")["target_set"]["target_nuclides"]}
    for nid, nuc in p038.items():
        if nid not in p001:
            continue
        z, n = nuc["Z"], nuc["N"]
        if (z + n) % 2 == 1:  # odd-A
            v001 = float(p001[nid]["predicted_value_mev"])
            v038 = float(nuc["predicted_value_mev"])
            assert abs(v001 - v038) < 1e-6, (
                f"Odd-A {nid}: PRED-0001={v001} != PRED-0038={v038}; "
                "pairing 1/A vs 1/sqrt(A) must coincide for odd-A targets"
            )


def test_pred_0037_uniform_coulomb_shift_vs_pred_0001() -> None:
    """PRED-0037 minus PRED-0001 must equal +aC * Z / A^(1/3) for every target."""
    p001 = {n["nuclide_id"]: n for n in _load_pred("PRED-0001")["target_set"]["target_nuclides"]}
    p037 = {n["nuclide_id"]: n for n in _load_pred("PRED-0037")["target_set"]["target_nuclides"]}
    for nid, nuc in p037.items():
        if nid not in p001:
            continue
        z, n = nuc["Z"], nuc["N"]
        a = z + n
        expected_shift = _AC * z / a ** (1 / 3)
        observed_shift = float(nuc["predicted_value_mev"]) - float(p001[nid]["predicted_value_mev"])
        assert abs(observed_shift - expected_shift) < 1e-4, (
            f"{nid}: PRED-0037 vs PRED-0001 shift {observed_shift:.6f} != expected {expected_shift:.6f}"
        )


def test_pred_0038_even_even_shift_matches_pairing_scaling_delta() -> None:
    """For even-even targets, PRED-0038 minus PRED-0001 must equal +aP*(1/sqrt(A) - 1/A) MeV in mass excess."""
    p001 = {n["nuclide_id"]: n for n in _load_pred("PRED-0001")["target_set"]["target_nuclides"]}
    p038 = {n["nuclide_id"]: n for n in _load_pred("PRED-0038")["target_set"]["target_nuclides"]}
    for nid, nuc in p038.items():
        if nid not in p001:
            continue
        z, n = nuc["Z"], nuc["N"]
        if not (z % 2 == 0 and n % 2 == 0):
            continue
        a = z + n
        expected_shift = _AP * (1.0 / math.sqrt(a) - 1.0 / a)
        observed_shift = float(nuc["predicted_value_mev"]) - float(p001[nid]["predicted_value_mev"])
        assert abs(observed_shift - expected_shift) < 1e-4, (
            f"Even-even {nid}: PRED-0038 vs PRED-0001 shift {observed_shift:.6f} != expected {expected_shift:.6f}"
        )
