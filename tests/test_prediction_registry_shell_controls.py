"""Tests for PRED-0025 and PRED-0026 shell/magic-number control registry entries (TASK-0230)."""

from __future__ import annotations

import math
from pathlib import Path

import pytest
import yaml

from physics_lab.engines.nuclear_mass_baselines import MAGIC_NUMBERS


REPO_ROOT = Path(__file__).resolve().parent.parent
PRED_DIR = REPO_ROOT / "prediction_registry" / "nuclear_masses"
NMD_0002_PATH = REPO_ROOT / "data" / "nuclear_masses" / "nmd-0002-curated-measured-slice.yaml"
HOLDOUT_PATH = REPO_ROOT / "data" / "nuclear_masses" / "post_ame2020_holdout.yaml"

PRED_IDS = ["PRED-0025", "PRED-0026"]

# Frozen baseline coefficients from RESULT-0015::model_fitted_semi_empirical
_AV = 15.51423612106804
_AS = 17.2931812095177
_AC = 0.6878156091568888
_AA = 23.846557883948485
_AP = 15.990845113398912

# Frozen shell-control fit copied from AGENT-RUN-0009 / TASK-0200
_SIGMA = 2.0
_PRED_COEFFS = {
    "PRED-0025": {"s_z_gauss": -1.5599853542897564, "s_n_gauss": 3.2082046765215466},
    "PRED-0026": {"s_n_gauss": 1.6049071729432316},
}

# Physical constants
_M_H = 1.00782503207  # u
_M_N = 1.00866491600  # u
_U_TO_MEV = 931.494013  # MeV/u


def _semi_empirical_binding_energy_mev(Z: int, N: int) -> float:
    A = Z + N
    if Z % 2 == 0 and N % 2 == 0:
        pairing_delta = +_AP / math.sqrt(A)
    elif Z % 2 == 1 and N % 2 == 1:
        pairing_delta = -_AP / math.sqrt(A)
    else:
        pairing_delta = 0.0
    return (
        _AV * A
        - _AS * A ** (2 / 3)
        - _AC * Z * (Z - 1) / A ** (1 / 3)
        - _AA * (N - Z) ** 2 / A
        + pairing_delta
    )


def _nearest_magic_distance(value: int) -> int:
    return min(abs(value - magic) for magic in MAGIC_NUMBERS)


def _shell_proximity(value: int) -> float:
    distance = _nearest_magic_distance(value)
    return math.exp(-(distance**2) / (2.0 * _SIGMA * _SIGMA))


def _mass_excess_mev(pred_id: str, Z: int, N: int) -> float:
    A = Z + N
    coeffs = _PRED_COEFFS[pred_id]
    correction = coeffs.get("s_z_gauss", 0.0) * _shell_proximity(Z) + coeffs.get(
        "s_n_gauss", 0.0
    ) * _shell_proximity(N)
    binding_energy_mev = _semi_empirical_binding_energy_mev(Z, N) + correction
    atomic_mass_u = Z * _M_H + N * _M_N - binding_energy_mev / _U_TO_MEV
    return (atomic_mass_u - A) * _U_TO_MEV


def _load_pred(pred_id: str) -> dict:
    path = PRED_DIR / f"{pred_id}.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_nmd_0002_ids() -> set[str]:
    data = yaml.safe_load(NMD_0002_PATH.read_text(encoding="utf-8"))
    return {entry["nuclide_id"] for entry in data.get("entries", [])}


def _load_holdout_ids() -> set[str]:
    data = yaml.safe_load(HOLDOUT_PATH.read_text(encoding="utf-8"))
    return {entry["nuclide_id"] for entry in data.get("entries", [])}


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
def test_registry_boundary_fields(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    assert entry["registry_status"] == "REGISTERED"
    assert entry["task_id"] == "TASK-0230"
    assert entry["source_state"]["live_external_fetch_allowed"] is False
    assert entry["target_set"]["quantity"] == "mass_excess_mev"
    assert entry["target_set"]["unit"] == "MeV"
    assert entry["review_boundary"]["pre_reveal_claim_promotion_allowed"] is False
    assert entry["review_boundary"]["canonical_result_allowed_pre_reveal"] is False
    assert entry["review_boundary"]["retrospective_equivalence_forbidden"] is True


@pytest.mark.parametrize("pred_id", PRED_IDS)
def test_targets_are_repo_prospective_and_structurally_consistent(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    nmd_ids = _load_nmd_0002_ids()
    holdout_ids = _load_holdout_ids()
    for nuclide in entry["target_set"]["target_nuclides"]:
        assert nuclide["A"] == nuclide["Z"] + nuclide["N"]
        assert nuclide["uncertainty_mev"] is None
        assert nuclide["nuclide_id"] not in nmd_ids
        assert nuclide["nuclide_id"] not in holdout_ids


@pytest.mark.parametrize("pred_id", PRED_IDS)
def test_shell_control_values_reproduce(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    for nuclide in entry["target_set"]["target_nuclides"]:
        expected = _mass_excess_mev(pred_id, nuclide["Z"], nuclide["N"])
        stored = float(nuclide["predicted_value_mev"])
        assert abs(expected - stored) < 1.0e-5, (
            f"{pred_id} {nuclide['nuclide_id']}: recomputed {expected:.6f} != stored {stored:.6f}"
        )


def test_pred_0025_is_more_bound_than_pred_0026_for_all_targets() -> None:
    p025 = {n["nuclide_id"]: n for n in _load_pred("PRED-0025")["target_set"]["target_nuclides"]}
    p026 = {n["nuclide_id"]: n for n in _load_pred("PRED-0026")["target_set"]["target_nuclides"]}
    assert p025.keys() == p026.keys()
    for nuclide_id in p025:
        value_025 = float(p025[nuclide_id]["predicted_value_mev"])
        value_026 = float(p026[nuclide_id]["predicted_value_mev"])
        assert value_025 < value_026, (
            f"{nuclide_id}: expected PRED-0025 ({value_025}) to be more bound than "
            f"PRED-0026 ({value_026}) on this shell-magic probe batch"
        )


def test_pred_0025_minus_pred_0026_matches_frozen_delta() -> None:
    p025 = {n["nuclide_id"]: n for n in _load_pred("PRED-0025")["target_set"]["target_nuclides"]}
    p026 = {n["nuclide_id"]: n for n in _load_pred("PRED-0026")["target_set"]["target_nuclides"]}
    z_coefficient_delta = _PRED_COEFFS["PRED-0025"]["s_z_gauss"]
    n_coefficient_delta = (
        _PRED_COEFFS["PRED-0025"]["s_n_gauss"] - _PRED_COEFFS["PRED-0026"]["s_n_gauss"]
    )
    for nuclide_id, p025_row in p025.items():
        p026_row = p026[nuclide_id]
        Z = int(p025_row["Z"])
        N = int(p025_row["N"])
        expected_delta = -(
            z_coefficient_delta * _shell_proximity(Z) + n_coefficient_delta * _shell_proximity(N)
        )
        observed_delta = float(p025_row["predicted_value_mev"]) - float(
            p026_row["predicted_value_mev"]
        )
        assert abs(expected_delta - observed_delta) < 1.0e-5, (
            f"{nuclide_id}: expected delta {expected_delta:.6f} != observed {observed_delta:.6f}"
        )
