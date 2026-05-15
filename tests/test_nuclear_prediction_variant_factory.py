from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from physics_lab.engines.nuclear_mass_baselines import (
    SemiEmpiricalCoefficients,
    semi_empirical_atomic_mass_u,
)
from physics_lab.engines.nuclear_masses import mass_excess_keV_from_atomic_mass_u
from physics_lab.engines.nuclear_prediction_variants import (
    apply_coefficient_transform,
    generate_variant_slate,
)
from physics_lab.registry.examples import load_example_config
from physics_lab.registry.nuclear_mass_predictions import load_nuclear_mass_prediction


FITTED_SEMI_EMPIRICAL_COEFFICIENTS = SemiEmpiricalCoefficients(
    volume=15.51423612106804,
    surface=17.2931812095177,
    coulomb=0.6878156091568888,
    asymmetry=23.846557883948485,
    pairing=15.990845113398912,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _base_config() -> dict[str, object]:
    return {
        "factory_id": "test-nuclear-prediction-variant-factory",
        "task_id": "TASK-0249",
        "campaign_profile_id": "nuclear-mass-surface",
        "quantity": "mass_excess_mev",
        "registered_by": {
            "contributor_id": "roman",
            "agent_id": "codex",
        },
        "registered_at_utc": "2026-05-15T00:00:00Z",
        "baseline_model": {
            "result_id": "RESULT-0015",
            "source_path": "results/EXP-0012/RUN-0001/result.yaml",
            "score_model_id": "model_fitted_semi_empirical",
            "registry_model_id": "RESULT-0015::model_fitted_semi_empirical",
            "frozen_parameters_note": "Frozen coefficient source is RESULT-0015.",
        },
        "source_state": {
            "git_commit": "abcdef0",
            "training_data_references": [
                "data/nuclear_masses/nmd-0002-curated-measured-slice.yaml"
            ],
            "holdout_protocol_references": [
                "docs/blind-holdout-benchmark-protocol.md",
                "docs/nuclear-mass-holdout-protocol.md",
                "docs/prediction-registry-policy.md",
            ],
            "live_external_fetch_allowed": False,
            "source_data_state_note": (
                "Test factory run uses only committed repository state and does not fetch "
                "live external measurements."
            ),
        },
        "reveal_conditions": {
            "reveal_trigger": (
                "A future maintainer-reviewed nuclear mass dataset or source manifest "
                "contains measured values for one or more target nuclides."
            ),
            "comparison_data_reference": (
                "future data/nuclear_masses/<reviewed-future-source>.yaml"
            ),
            "reveal_owner": "maintainer or maintainer-authorized review agent",
            "no_peek_rule": (
                "After registration, do not alter frozen model id, target nuclides, "
                "predicted values, or reveal rule."
            ),
        },
        "output": {
            "write_draft_predictions": False,
        },
        "target_batches": {
            "odd-even-probe": [
                {"nuclide_id": "Ni-60", "Z": 28, "N": 32},
                {"nuclide_id": "Cu-64", "Z": 29, "N": 35},
            ]
        },
        "variants": [
            {
                "prediction_id": "PRED-9001",
                "variant_id": "pairing-zero-ablation",
                "model_id": "RESULT-0015::model_fitted_semi_empirical::pairing_zero",
                "title": "Draft nuclear mass variant: pairing zero on odd-even probe",
                "target_batch": "odd-even-probe",
                "model_control_label": "pairing ablation control",
                "transform": {"set": {"pairing": 0.0}},
                "review_notes": ["Ablation candidate for factory tests."],
            }
        ],
    }


def _mass_excess_mev(z: int, n: int, coefficients: SemiEmpiricalCoefficients) -> float:
    atomic_mass_u = semi_empirical_atomic_mass_u(z=z, n=n, coefficients=coefficients)
    return mass_excess_keV_from_atomic_mass_u(a=z + n, atomic_mass_u=atomic_mass_u) / 1000.0


def test_variant_factory_generates_deterministic_mass_excess_values() -> None:
    config = _base_config()

    summary = generate_variant_slate(config, repo_root=_repo_root())

    assert summary["candidate_count"] == 1
    candidate = summary["candidates"][0]
    coefficients = apply_coefficient_transform(
        FITTED_SEMI_EMPIRICAL_COEFFICIENTS,
        {"set": {"pairing": 0.0}},
    )
    ni60 = candidate["target_nuclides"][0]
    cu64 = candidate["target_nuclides"][1]

    assert candidate["prediction_id"] == "PRED-9001"
    assert candidate["target_batch"] == "odd-even-probe"
    assert candidate["coefficient_delta_from_base"]["pairing"] == pytest.approx(
        -FITTED_SEMI_EMPIRICAL_COEFFICIENTS.pairing
    )
    assert ni60["predicted_value_mev"] == round(_mass_excess_mev(28, 32, coefficients), 6)
    assert cu64["predicted_value_mev"] == round(_mass_excess_mev(29, 35, coefficients), 6)
    assert ni60["delta_from_baseline_mev"] > 0
    assert cu64["delta_from_baseline_mev"] < 0


def test_variant_factory_rejects_duplicate_prediction_ids() -> None:
    config = deepcopy(_base_config())
    config["variants"].append(deepcopy(config["variants"][0]))
    config["variants"][1]["variant_id"] = "duplicate-request"

    with pytest.raises(ValueError, match="Duplicate requested prediction_id"):
        generate_variant_slate(config, repo_root=_repo_root())


def test_variant_factory_writes_schema_compatible_draft_without_mutating_registry(
    tmp_path: Path,
) -> None:
    config = _base_config()
    registry_dir = _repo_root() / "prediction_registry" / "nuclear_masses"
    before_registry_files = sorted(path.name for path in registry_dir.glob("PRED-*.yaml"))

    summary = generate_variant_slate(
        config,
        repo_root=_repo_root(),
        output_dir=tmp_path,
        write_drafts=True,
    )

    draft_path = tmp_path / "PRED-9001.yaml"
    assert summary["written_prediction_files"] == [str(draft_path)]
    payload = load_nuclear_mass_prediction(draft_path)

    assert payload["prediction_id"] == "PRED-9001"
    assert payload["task_id"] == "TASK-0249"
    assert payload["source_state"]["live_external_fetch_allowed"] is False
    assert payload["target_set"]["quantity"] == "mass_excess_mev"
    assert payload["review_boundary"]["pre_reveal_claim_promotion_allowed"] is False

    after_registry_files = sorted(path.name for path in registry_dir.glob("PRED-*.yaml"))
    assert after_registry_files == before_registry_files


def test_variant_factory_refuses_committed_registry_output_by_default() -> None:
    config = _base_config()
    registry_dir = _repo_root() / "prediction_registry" / "nuclear_masses"

    with pytest.raises(ValueError, match="Refusing to write draft predictions"):
        generate_variant_slate(
            config,
            repo_root=_repo_root(),
            output_dir=registry_dir,
            write_drafts=True,
        )


def test_variant_factory_requires_no_live_external_fetch() -> None:
    config = deepcopy(_base_config())
    config["source_state"]["live_external_fetch_allowed"] = True

    with pytest.raises(ValueError, match="live_external_fetch_allowed must be false"):
        generate_variant_slate(config, repo_root=_repo_root())


def test_factory_example_is_validated_as_factory_config() -> None:
    payload = load_example_config(_repo_root() / "examples" / "nuclear_prediction_variant_factory.yaml")

    assert payload["config_kind"] == "nuclear_prediction_variant_factory"
    assert payload["factory_id"] == "nuclear-prediction-variant-factory-example"
