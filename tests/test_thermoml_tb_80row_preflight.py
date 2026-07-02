"""Tests for the TASK-0906 ThermoML 80-row count-only preflight helper."""

from __future__ import annotations

from collections import Counter
import json

from scripts.preflight_thermoml_tb_80row_identity_counts import (
    SELECTED_FAMILIES,
    TARGET_ROWS_PER_FAMILY,
    ArchiveMetadata,
    Observation,
    assert_value_free_payload,
    summarize_observations,
)


ARCHIVE = ArchiveMetadata(
    filename="ThermoML.v2020-09-30.tgz",
    size_bytes=189_433_115,
    sha256="231161b5e443dc1ae0e5da8429d86a88474cb722016e5b790817bb31c58d7ec2",
)
FAMILY_ATOMS = {
    "acids": (1, 6, 8),
    "esters/lactones": (1, 6, 8),
    "ketones": (1, 6, 8),
    "alcohols/phenols": (1, 6, 8),
    "ethers": (1, 6, 8),
    "halocarbons": (1, 6, 17),
    "aromatic hydrocarbons": (1, 6),
    "alkanes/cycloalkanes": (1, 6),
}


def _observation(
    family: str,
    index: int,
    *,
    identity: str | None = None,
    tb_k: float = 300.0,
    uncertainty_k: float | None = 0.1,
) -> Observation:
    return Observation(
        inchi_key=identity or f"{family}-{index}",
        family=family,
        atomic_numbers=FAMILY_ATOMS[family],
        molecular_weight_g_mol=50.0 + index,
        experimental_tb_k=tb_k,
        expanded_uncertainty_k=uncertainty_k,
        source_doi=f"10.example/{family}/{index}",
        source_member=f"10.example/{family}/{index}.json",
    )


def _balanced_observations() -> list[Observation]:
    return [
        _observation(family, index, tb_k=300.0 + index)
        for family in SELECTED_FAMILIES
        for index in range(TARGET_ROWS_PER_FAMILY)
    ]


def test_summarize_observations_reports_rights_blocker_when_counts_are_feasible() -> None:
    observations = _balanced_observations()
    observations.extend(
        [
            _observation("acids", 99, identity="conflict", tb_k=300.0),
            _observation("acids", 100, identity="conflict", tb_k=302.0),
            _observation("ethers", 99, identity="missing-uncertainty", uncertainty_k=None),
        ]
    )

    payload = summarize_observations(
        observations,
        Counter({"archive_json_files": 1}),
        ARCHIVE,
        rdkit_version="test-rdkit",
        thermo_version="test-thermo",
    )

    assert payload["count_feasibility"] == "80_ROW_EXPANSION_FEASIBLE"
    assert payload["verdict"] == "RIGHTS_DECISION_STILL_BLOCKS"
    assert payload["counts"]["conflict_flagged_identity_counts_by_family"]["acids"] == 1
    assert payload["counts"]["missing_uncertainty_identity_counts_by_family"]["ethers"] == 1
    assert payload["counts"]["underpopulated_families"] == {}
    assert_value_free_payload(payload)
    serialized = json.dumps(payload)
    assert "experimental_tb_k" not in serialized
    assert "source_member" not in serialized
    assert '"rows"' not in serialized


def test_summarize_observations_reports_underpopulated_families() -> None:
    observations = [
        _observation(family, index, tb_k=300.0 + index)
        for family in SELECTED_FAMILIES
        for index in range(TARGET_ROWS_PER_FAMILY)
        if not (family == "ketones" and index == TARGET_ROWS_PER_FAMILY - 1)
    ]

    payload = summarize_observations(
        observations,
        Counter(),
        ARCHIVE,
        rdkit_version="test-rdkit",
        thermo_version="test-thermo",
    )

    underpopulated = payload["counts"]["underpopulated_families"]
    assert payload["verdict"] == "FAMILY_UNDERPOPULATED"
    assert underpopulated == {
        "ketones": {
            "admissible_count": TARGET_ROWS_PER_FAMILY - 1,
            "needed": TARGET_ROWS_PER_FAMILY,
            "shortfall": 1,
        }
    }