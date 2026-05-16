"""Tests for PRED-0027 and PRED-0028 neutron-excess/asymmetry control registry entries (TASK-0231)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from physics_lab.engines.nuclear_mass_baselines import (
    SemiEmpiricalCoefficients,
    semi_empirical_binding_energy,
)
from physics_lab.engines.nuclear_masses import (
    ATOMIC_MASS_UNIT_MEV,
    HYDROGEN_ATOM_MASS_U,
    NEUTRON_MASS_U,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
PRED_DIR = REPO_ROOT / "prediction_registry" / "nuclear_masses"
NMD_0002_PATH = REPO_ROOT / "data" / "nuclear_masses" / "nmd-0002-curated-measured-slice.yaml"
HOLDOUT_PATH = REPO_ROOT / "data" / "nuclear_masses" / "post_ame2020_holdout.yaml"

PRED_IDS = ["PRED-0027", "PRED-0028"]

# Frozen baseline coefficients from RESULT-0015::model_fitted_semi_empirical
_AV = 15.51423612106804
_AS = 17.2931812095177
_AC = 0.6878156091568888
_AA = 23.846557883948485
_AP = 15.990845113398912

_PRED_COEFFS = {
    "PRED-0027": {"i_sq": 82.66196399343987, "i_quartic": -1777.7853009092412},
    "PRED-0028": {"neutron_excess_sq_over_a": 3.4709894797642375e-13},
}

_BASE_COEFFS = SemiEmpiricalCoefficients(
    volume=_AV,
    surface=_AS,
    coulomb=_AC,
    asymmetry=_AA,
    pairing=_AP,
)


def _semi_empirical_binding_energy_mev(Z: int, N: int) -> float:
    return semi_empirical_binding_energy(z=Z, n=N, coefficients=_BASE_COEFFS)


def _mass_excess_mev(pred_id: str, Z: int, N: int) -> float:
    A = Z + N
    coeffs = _PRED_COEFFS[pred_id]
    if pred_id == "PRED-0027":
        asymmetry = (N - Z) / A
        correction = coeffs["i_sq"] * asymmetry**2 + coeffs["i_quartic"] * asymmetry**4
    else:
        correction = coeffs["neutron_excess_sq_over_a"] * (max(N - Z, 0) ** 2 / A)
    binding_energy_mev = _semi_empirical_binding_energy_mev(Z, N) + correction
    atomic_mass_u = (
        Z * HYDROGEN_ATOM_MASS_U + N * NEUTRON_MASS_U - binding_energy_mev / ATOMIC_MASS_UNIT_MEV
    )
    return (atomic_mass_u - A) * ATOMIC_MASS_UNIT_MEV


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
    assert entry["task_id"] == "TASK-0231"
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
def test_neutron_excess_control_values_reproduce(pred_id: str) -> None:
    entry = _load_pred(pred_id)
    for nuclide in entry["target_set"]["target_nuclides"]:
        expected = _mass_excess_mev(pred_id, nuclide["Z"], nuclide["N"])
        stored = float(nuclide["predicted_value_mev"])
        assert round(expected, 6) == stored, (
            f"{pred_id} {nuclide['nuclide_id']}: recomputed {expected:.6f} != stored {stored:.6f}"
        )


def test_pred_0027_is_less_bound_than_pred_0028_for_all_targets() -> None:
    p027 = {n["nuclide_id"]: n for n in _load_pred("PRED-0027")["target_set"]["target_nuclides"]}
    p028 = {n["nuclide_id"]: n for n in _load_pred("PRED-0028")["target_set"]["target_nuclides"]}
    assert p027.keys() == p028.keys()
    for nuclide_id in p027:
        value_027 = float(p027[nuclide_id]["predicted_value_mev"])
        value_028 = float(p028[nuclide_id]["predicted_value_mev"])
        assert value_027 > value_028, (
            f"{nuclide_id}: expected PRED-0027 ({value_027}) to be less bound than "
            f"PRED-0028 ({value_028}) on this neutron-excess probe batch"
        )


def test_pred_0028_remains_practically_baseline_identical() -> None:
    entry = _load_pred("PRED-0028")
    for nuclide in entry["target_set"]["target_nuclides"]:
        A = nuclide["A"]
        Z = nuclide["Z"]
        N = nuclide["N"]
        baseline_binding_energy = _semi_empirical_binding_energy_mev(Z, N)
        baseline_atomic_mass_u = (
            Z * HYDROGEN_ATOM_MASS_U
            + N * NEUTRON_MASS_U
            - baseline_binding_energy / ATOMIC_MASS_UNIT_MEV
        )
        baseline_mass_excess_mev = (baseline_atomic_mass_u - A) * ATOMIC_MASS_UNIT_MEV
        stored = float(nuclide["predicted_value_mev"])
        assert abs(baseline_mass_excess_mev - stored) < 1.0e-5, (
            f"{nuclide['nuclide_id']}: expected near-baseline value {baseline_mass_excess_mev:.6f} "
            f"!= stored {stored:.6f}"
        )
