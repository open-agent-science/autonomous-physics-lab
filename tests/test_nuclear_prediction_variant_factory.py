from __future__ import annotations

import math
from copy import deepcopy
from pathlib import Path

import pytest

from physics_lab.engines.nuclear_mass_baselines import (
    SemiEmpiricalCoefficients,
    semi_empirical_atomic_mass_u,
    semi_empirical_binding_energy,
)
from physics_lab.engines.nuclear_masses import (
    ATOMIC_MASS_UNIT_MEV,
    HYDROGEN_ATOM_MASS_U,
    NEUTRON_MASS_U,
    mass_excess_keV_from_atomic_mass_u,
)
from physics_lab.engines.nuclear_prediction_variants import (
    apply_coefficient_transform,
    collect_target_batch_library_issues,
    feature_term_correction_mev,
    generate_variant_slate,
    load_target_batch_library,
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


def test_target_batch_library_is_valid_and_spans_required_batch_types() -> None:
    library = load_target_batch_library(repo_root=_repo_root())
    batches = library["batches"]

    assert not collect_target_batch_library_issues(library, repo_root=_repo_root())
    assert {
        "frontier_controls",
        "odd_even_pairing_probe",
        "shell_magic_probe",
        "neutron_rich_stress",
        "isotope_chain_probe",
    }.issubset({batch["category"] for batch in batches.values()})
    assert len(batches) >= 5


def test_variant_factory_resolves_targets_from_reusable_library() -> None:
    config = deepcopy(_base_config())
    config.pop("target_batches")
    config["target_batch_library"] = {
        "path": "data/nuclear_masses/factory_target_batches.yaml",
        "include_batches": ["odd-even-pairing-probe"],
    }
    config["variants"][0]["target_batch"] = "odd-even-pairing-probe"

    summary = generate_variant_slate(config, repo_root=_repo_root())
    candidate = summary["candidates"][0]

    assert candidate["target_batch"] == "odd-even-pairing-probe"
    assert [row["nuclide_id"] for row in candidate["target_nuclides"]] == [
        "Co-59",
        "Ni-60",
        "Cu-64",
        "Zn-65",
    ]


def test_target_batch_library_detects_inconsistent_mass_number() -> None:
    library = {
        "source_guardrails": {"live_external_fetch_allowed": False},
        "batches": {
            "bad-batch": {
                "retrospective_control": False,
                "targets": [{"nuclide_id": "Bad-5", "Z": 2, "N": 2, "A": 5}],
            }
        },
    }

    issues = collect_target_batch_library_issues(library, repo_root=_repo_root())

    assert any(issue.code == "invalid_target" for issue in issues)


def test_target_batch_library_detects_duplicate_nuclides_within_batch() -> None:
    library = {
        "source_guardrails": {"live_external_fetch_allowed": False},
        "batches": {
            "duplicate-batch": {
                "retrospective_control": False,
                "targets": [
                    {"nuclide_id": "Ni-76", "Z": 28, "N": 48, "A": 76},
                    {"nuclide_id": "Ni-76", "Z": 28, "N": 48, "A": 76},
                ],
            }
        },
    }

    issues = collect_target_batch_library_issues(library, repo_root=_repo_root())

    assert any(issue.code == "duplicate_nuclide_id" for issue in issues)


def test_target_batch_library_blocks_committed_measurements_unless_retrospective() -> None:
    library = {
        "source_guardrails": {"live_external_fetch_allowed": False},
        "batches": {
            "prospective-batch": {
                "retrospective_control": False,
                "targets": [{"nuclide_id": "He-4", "Z": 2, "N": 2, "A": 4}],
            },
            "retrospective-batch": {
                "retrospective_control": True,
                "targets": [{"nuclide_id": "Ca-40", "Z": 20, "N": 20, "A": 40}],
            },
        },
    }

    issues = collect_target_batch_library_issues(library, repo_root=_repo_root())

    assert any(
        issue.code == "committed_measurement_target"
        and issue.batch_id == "prospective-batch"
        for issue in issues
    )
    assert not any(
        issue.code == "committed_measurement_target"
        and issue.batch_id == "retrospective-batch"
        for issue in issues
    )


def _mass_excess_with_correction(
    z: int,
    n: int,
    coefficients: SemiEmpiricalCoefficients,
    correction_mev: float,
) -> float:
    binding_energy = semi_empirical_binding_energy(z=z, n=n, coefficients=coefficients)
    mass_defect_u = (binding_energy + correction_mev) / ATOMIC_MASS_UNIT_MEV
    atomic_mass_u = (
        z * HYDROGEN_ATOM_MASS_U + n * NEUTRON_MASS_U - mass_defect_u
    )
    return mass_excess_keV_from_atomic_mass_u(a=z + n, atomic_mass_u=atomic_mass_u) / 1000.0


def test_feature_term_shell_proximity_gaussian_matches_manual_computation() -> None:
    # Z+N axis Gaussian shell-proximity, mirroring PRED-0025 review coefficients.
    feature_terms = (
        {
            "type": "shell_proximity_gaussian",
            "axis": "z",
            "coefficient": -1.5599853542897564,
            "sigma": 2.0,
            "magic_numbers": [2, 8, 20, 28, 50, 82, 126],
        },
        {
            "type": "shell_proximity_gaussian",
            "axis": "n",
            "coefficient": 3.2082046765215466,
            "sigma": 2.0,
            "magic_numbers": [2, 8, 20, 28, 50, 82, 126],
        },
    )
    # Cu-79: Z=29 (distance to nearest magic = 1 from 28); N=50 (distance = 0).
    expected = (
        -1.5599853542897564 * math.exp(-(1 ** 2) / (2 * 2.0 ** 2))
        + 3.2082046765215466 * math.exp(-(0 ** 2) / (2 * 2.0 ** 2))
    )
    actual = feature_term_correction_mev(z=29, n=50, feature_terms=feature_terms)
    assert actual == pytest.approx(expected)


def test_feature_term_asymmetry_polynomial_matches_manual_computation() -> None:
    feature_terms = (
        {
            "type": "asymmetry_polynomial",
            "terms": [
                {"power": 2, "coefficient": 82.66196399343987},
                {"power": 4, "coefficient": -1777.7853009092412},
            ],
        },
    )
    z, n = 11, 28  # Na-39
    a = z + n
    isospin = (n - z) / a
    expected = (
        82.66196399343987 * isospin ** 2
        + -1777.7853009092412 * isospin ** 4
    )
    actual = feature_term_correction_mev(z=z, n=n, feature_terms=feature_terms)
    assert actual == pytest.approx(expected)


def test_feature_term_asymmetric_neutron_excess_zero_when_n_le_z() -> None:
    feature_terms = (
        {
            "type": "asymmetric_neutron_excess",
            "coefficient": 1.0,
            "power": 2,
        },
    )
    # Neutron-poor target (N < Z) — correction must be exactly 0.
    assert feature_term_correction_mev(z=29, n=28, feature_terms=feature_terms) == 0.0
    # Symmetric (N = Z) — also 0.
    assert feature_term_correction_mev(z=20, n=20, feature_terms=feature_terms) == 0.0
    # Neutron-rich case computes c * (N-Z)^2 / A.
    z, n = 11, 28
    expected = 1.0 * ((n - z) ** 2) / (z + n)
    assert feature_term_correction_mev(
        z=z, n=n, feature_terms=feature_terms
    ) == pytest.approx(expected)


def _feature_term_variant_config(feature_terms: list[dict[str, object]]) -> dict[str, object]:
    config = deepcopy(_base_config())
    config["target_batches"]["shell-magic-control-probe"] = [
        {"nuclide_id": "Cu-79", "Z": 29, "N": 50},
        {"nuclide_id": "Kr-86", "Z": 36, "N": 50},
    ]
    config["variants"] = [
        {
            "prediction_id": "PRED-9301",
            "variant_id": "shell-proximity-zn-control",
            "model_id": "RESULT-0015::model_fitted_semi_empirical::shell_zn",
            "title": "Draft nuclear mass variant: Z+N shell-proximity feature control",
            "target_batch": "shell-magic-control-probe",
            "model_control_label": "shell-proximity feature control",
            "transform": {"feature_terms": feature_terms},
            "review_notes": ["Feature-term factory test."],
        }
    ]
    return config


def test_variant_factory_applies_feature_term_to_predicted_mass_excess() -> None:
    feature_terms = [
        {
            "type": "shell_proximity_gaussian",
            "axis": "z",
            "coefficient": -1.5599853542897564,
        },
        {
            "type": "shell_proximity_gaussian",
            "axis": "n",
            "coefficient": 3.2082046765215466,
        },
    ]
    config = _feature_term_variant_config(feature_terms)

    summary = generate_variant_slate(config, repo_root=_repo_root())
    candidate = summary["candidates"][0]

    assert candidate["feature_terms"][0]["type"] == "shell_proximity_gaussian"
    assert candidate["feature_term_summary"]["max_abs_correction_mev"] > 0.0
    assert all(name in COEFFICIENT_DELTA_KEYS for name in candidate["coefficient_delta_from_base"])

    cu79_row = candidate["target_nuclides"][0]
    correction = feature_term_correction_mev(
        z=29, n=50, feature_terms=tuple(_normalize_for_eval(feature_terms))
    )
    expected_excess = round(
        _mass_excess_with_correction(29, 50, FITTED_SEMI_EMPIRICAL_COEFFICIENTS, correction),
        6,
    )
    assert cu79_row["predicted_value_mev"] == expected_excess
    assert cu79_row["feature_term_correction_mev"] == round(correction, 6)
    # Baseline must remain a pure semi-empirical recompute (no feature correction).
    baseline_expected = round(
        _mass_excess_with_correction(29, 50, FITTED_SEMI_EMPIRICAL_COEFFICIENTS, 0.0),
        6,
    )
    assert cu79_row["baseline_value_mev"] == baseline_expected


def test_variant_factory_combines_coefficient_and_feature_term_transforms() -> None:
    feature_terms = [
        {
            "type": "asymmetric_neutron_excess",
            "coefficient": 5.0,
            "power": 2,
        }
    ]
    config = _feature_term_variant_config(feature_terms)
    config["variants"][0]["transform"] = {
        "scale": {"asymmetry": 1.01},
        "feature_terms": feature_terms,
    }

    summary = generate_variant_slate(config, repo_root=_repo_root())
    candidate = summary["candidates"][0]

    # Coefficient transform applied: asymmetry coefficient delta is non-zero.
    assert candidate["coefficient_delta_from_base"]["asymmetry"] == pytest.approx(
        FITTED_SEMI_EMPIRICAL_COEFFICIENTS.asymmetry * 0.01
    )
    # Feature-term correction also recorded for each target.
    cu79_row = candidate["target_nuclides"][0]
    expected_correction = 5.0 * ((50 - 29) ** 2) / (29 + 50)
    assert cu79_row["feature_term_correction_mev"] == pytest.approx(
        round(expected_correction, 6)
    )


def test_variant_factory_rejects_unknown_feature_term_type() -> None:
    config = _feature_term_variant_config([{"type": "totally-made-up", "coefficient": 1.0}])
    with pytest.raises(ValueError, match="unknown feature term type"):
        generate_variant_slate(config, repo_root=_repo_root())


def test_variant_factory_rejects_invalid_shell_proximity_axis() -> None:
    config = _feature_term_variant_config(
        [{"type": "shell_proximity_gaussian", "axis": "x", "coefficient": 1.0}]
    )
    with pytest.raises(ValueError, match="axis must be 'z' or 'n'"):
        generate_variant_slate(config, repo_root=_repo_root())


def test_variant_factory_rejects_invalid_shell_proximity_sigma() -> None:
    config = _feature_term_variant_config(
        [
            {
                "type": "shell_proximity_gaussian",
                "axis": "z",
                "coefficient": 1.0,
                "sigma": 0.0,
            }
        ]
    )
    with pytest.raises(ValueError, match="sigma must be > 0"):
        generate_variant_slate(config, repo_root=_repo_root())


def test_variant_factory_rejects_duplicate_polynomial_powers() -> None:
    config = _feature_term_variant_config(
        [
            {
                "type": "asymmetry_polynomial",
                "terms": [
                    {"power": 2, "coefficient": 1.0},
                    {"power": 2, "coefficient": 2.0},
                ],
            }
        ]
    )
    with pytest.raises(ValueError, match="duplicate power"):
        generate_variant_slate(config, repo_root=_repo_root())


def test_variant_factory_rejects_polynomial_power_above_max() -> None:
    config = _feature_term_variant_config(
        [
            {
                "type": "asymmetry_polynomial",
                "terms": [{"power": 7, "coefficient": 1.0}],
            }
        ]
    )
    with pytest.raises(ValueError, match="power must be between 1 and"):
        generate_variant_slate(config, repo_root=_repo_root())


def test_feature_term_factory_writes_schema_compatible_draft(tmp_path: Path) -> None:
    feature_terms = [
        {
            "type": "shell_proximity_gaussian",
            "axis": "n",
            "coefficient": 1.6049071729432316,
        }
    ]
    config = _feature_term_variant_config(feature_terms)

    summary = generate_variant_slate(
        config,
        repo_root=_repo_root(),
        output_dir=tmp_path,
        write_drafts=True,
    )
    draft_path = tmp_path / "PRED-9301.yaml"
    assert summary["written_prediction_files"] == [str(draft_path)]
    payload = load_nuclear_mass_prediction(draft_path)

    assert payload["prediction_id"] == "PRED-9301"
    assert payload["target_set"]["quantity"] == "mass_excess_mev"
    assert payload["source_state"]["live_external_fetch_allowed"] is False


COEFFICIENT_DELTA_KEYS = {"volume", "surface", "coulomb", "asymmetry", "pairing"}


def _normalize_for_eval(feature_terms: list[dict[str, object]]) -> list[dict[str, object]]:
    """Mirror engine defaults so manual feature_term evaluation matches the engine."""
    from physics_lab.engines.nuclear_mass_baselines import MAGIC_NUMBERS

    normalized = []
    for term in feature_terms:
        copy = deepcopy(term)
        if copy["type"] == "shell_proximity_gaussian":
            copy.setdefault("sigma", 2.0)
            copy.setdefault("magic_numbers", list(MAGIC_NUMBERS))
        elif copy["type"] == "asymmetric_neutron_excess":
            copy.setdefault("power", 2)
        normalized.append(copy)
    return normalized
