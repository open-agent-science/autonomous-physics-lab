from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
import yaml

from physics_lab.engines.nuclear_mass_baselines import (
    REFERENCE_SEMI_EMPIRICAL_COEFFICIENTS,
    SemiEmpiricalCoefficients,
    semi_empirical_atomic_mass_u,
)
from physics_lab.engines.nuclear_masses import mass_excess_keV_from_atomic_mass_u
from physics_lab.registry.nuclear_mass_predictions import load_nuclear_mass_prediction
from physics_lab.registry.validation import infer_kind_from_path


FITTED_SEMI_EMPIRICAL_COEFFICIENTS = SemiEmpiricalCoefficients(
    volume=15.51423612106804,
    surface=17.2931812095177,
    coulomb=0.6878156091568888,
    asymmetry=23.846557883948485,
    pairing=15.990845113398912,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _template_path() -> Path:
    return _repo_root() / "prediction_registry" / "nuclear_masses" / "PRED-TEMPLATE.yaml"


def _template_payload() -> dict[str, object]:
    raw_text = _template_path().read_text(encoding="utf-8")
    normalized = (
        raw_text.replace("PRED-XXXX", "PRED-0000")
        .replace("TASK-XXXX", "TASK-0000")
        .replace("REPLACE_WITH_COMMIT_SHA", "abcdef0")
    )
    payload = yaml.safe_load(normalized)
    assert isinstance(payload, dict)
    return payload


def _prediction_paths() -> list[Path]:
    return sorted((_repo_root() / "prediction_registry" / "nuclear_masses").glob("PRED-[0-9][0-9][0-9][0-9].yaml"))


def _committed_measured_nuclide_ids() -> set[str]:
    repo_root = _repo_root()
    dataset_paths = [
        repo_root / "data" / "nuclear_masses" / "nmd-0002-curated-measured-slice.yaml",
        repo_root / "data" / "nuclear_masses" / "post_ame2020_holdout.yaml",
    ]
    nuclide_ids: set[str] = set()
    for path in dataset_paths:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict)
        for entry in payload["entries"]:
            nuclide_ids.add(str(entry["nuclide_id"]))
    return nuclide_ids


def test_prediction_template_matches_schema() -> None:
    repo_root = _repo_root()
    schema_path = repo_root / "physics_lab" / "schemas" / "nuclear_mass_prediction.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    payload = _template_payload()

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.absolute_path))

    assert errors == []


def test_prediction_template_preserves_claim_and_reveal_boundary() -> None:
    payload = _template_payload()

    assert payload["campaign_profile_id"] == "nuclear-mass-surface"
    assert payload["evidence_class"] == "prospective_prediction_registry"
    assert payload["source_state"]["live_external_fetch_allowed"] is False
    assert payload["review_boundary"]["retrospective_equivalence_forbidden"] is True
    assert payload["review_boundary"]["pre_reveal_claim_promotion_allowed"] is False
    assert payload["review_boundary"]["canonical_result_allowed_pre_reveal"] is False
    assert "no claim" in payload["claim_ceiling"].lower()
    assert "before later maintainer-reviewed comparison" in payload["claim_ceiling"]


def test_prediction_template_target_rows_are_structurally_consistent() -> None:
    payload = _template_payload()
    targets = payload["target_set"]["target_nuclides"]

    assert len(targets) == 1
    target = targets[0]
    assert target["A"] == target["Z"] + target["N"]
    assert target["uncertainty_mev"] is None
    assert payload["uncertainty_semantics"]["type"] == "point_estimate_only"


def test_prediction_registry_kind_inference_supports_template_and_entries() -> None:
    assert (
        infer_kind_from_path("prediction_registry/nuclear_masses/PRED-TEMPLATE.yaml")
        == "nuclear_mass_prediction"
    )
    assert (
        infer_kind_from_path("prediction_registry/nuclear_masses/PRED-0001.yaml")
        == "nuclear_mass_prediction"
    )


def test_loader_validates_registered_prediction_slate() -> None:
    prediction_paths = _prediction_paths()

    assert len(prediction_paths) >= 20
    expected_first_slate_task_ids = {f"PRED-{idx:04d}": "TASK-0205" for idx in range(1, 21)}
    for entry_path in prediction_paths:
        payload = load_nuclear_mass_prediction(entry_path)
        assert payload["prediction_id"] == entry_path.stem
        assert payload["registry_status"] == "REGISTERED"
        if payload["prediction_id"] in expected_first_slate_task_ids:
            assert payload["task_id"] == expected_first_slate_task_ids[payload["prediction_id"]]


def test_registered_prediction_slate_preserves_parallel_variant_shape() -> None:
    first_slate_paths = [
        path
        for path in _prediction_paths()
        if path.stem in {f"PRED-{idx:04d}" for idx in range(1, 21)}
    ]
    payloads = [load_nuclear_mass_prediction(path) for path in first_slate_paths]

    model_ids = {
        str(payload["source_state"]["model_reference"]["model_id"]) for payload in payloads
    }
    target_labels = {str(payload["target_set"]["label"]) for payload in payloads}

    assert model_ids == {
        "RESULT-0015::model_fitted_semi_empirical",
        "RESULT-0015::model_reference_semi_empirical",
        "RESULT-0015::model_reference_liquid_drop_no_pairing",
        "RESULT-0015::model_fitted_semi_empirical::pairing_ablation_zero",
    }
    assert target_labels == {
        "frontier-next-row",
        "n50-forward-row",
        "n82-neighborhood-row",
        "heavy-extension-row",
        "odd-even-stress-row",
    }


def _smooth_control_coefficients(model_id: str) -> SemiEmpiricalCoefficients:
    fitted = FITTED_SEMI_EMPIRICAL_COEFFICIENTS
    reference = REFERENCE_SEMI_EMPIRICAL_COEFFICIENTS
    if model_id == "RESULT-0015::model_fitted_reference_blend_50_50":
        return SemiEmpiricalCoefficients(
            volume=(fitted.volume + reference.volume) / 2.0,
            surface=(fitted.surface + reference.surface) / 2.0,
            coulomb=(fitted.coulomb + reference.coulomb) / 2.0,
            asymmetry=(fitted.asymmetry + reference.asymmetry) / 2.0,
            pairing=(fitted.pairing + reference.pairing) / 2.0,
        )
    if model_id == "RESULT-0015::model_fitted_semi_empirical::volume_perturbation_plus_one_percent":
        return SemiEmpiricalCoefficients(
            volume=fitted.volume * 1.01,
            surface=fitted.surface,
            coulomb=fitted.coulomb,
            asymmetry=fitted.asymmetry,
            pairing=fitted.pairing,
        )
    raise AssertionError(f"Unknown smooth control model_id: {model_id}")


def test_smooth_control_predictions_match_deterministic_recompute() -> None:
    smooth_control_ids = ("PRED-0021", "PRED-0022")
    for prediction_id in smooth_control_ids:
        entry_path = (
            _repo_root() / "prediction_registry" / "nuclear_masses" / f"{prediction_id}.yaml"
        )
        payload = load_nuclear_mass_prediction(entry_path)

        assert payload["task_id"] == "TASK-0228"
        assert payload["target_set"]["label"] == "frontier-next-row"

        model_id = str(payload["source_state"]["model_reference"]["model_id"])
        coefficients = _smooth_control_coefficients(model_id)
        for target in payload["target_set"]["target_nuclides"]:
            mass_u = semi_empirical_atomic_mass_u(
                z=int(target["Z"]),
                n=int(target["N"]),
                coefficients=coefficients,
            )
            mass_excess_mev = (
                mass_excess_keV_from_atomic_mass_u(a=int(target["A"]), atomic_mass_u=mass_u)
                / 1000.0
            )
            assert round(mass_excess_mev, 6) == float(target["predicted_value_mev"])


def test_registered_prediction_targets_are_repo_prospective() -> None:
    measured_nuclide_ids = _committed_measured_nuclide_ids()

    for entry_path in _prediction_paths():
        payload = load_nuclear_mass_prediction(entry_path)
        targets = payload["target_set"]["target_nuclides"]
        for target in targets:
            assert target["A"] == target["Z"] + target["N"]
            assert target["nuclide_id"] not in measured_nuclide_ids
            assert target["uncertainty_mev"] is None
