from __future__ import annotations

import hashlib
import math
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ROWS_PATH = ROOT / "data/textbook_formula_audit/stellar_ml/chara_component_rows.yaml"
ALIAS_PATH = ROOT / "data/textbook_formula_audit/stellar_ml/chara_alias_audit_ledger.yaml"
DEBCAT_PATH = ROOT / "data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml"


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalize(value: str) -> str:
    value = value.strip().strip("'\"").upper()
    if value.startswith("V* "):
        value = value[3:]
    return value.replace(" ", "").replace("_", "")


def test_surface_freezes_exact_candidate_set_and_source_limit() -> None:
    payload = _load(ROWS_PATH)
    assert payload["verdict"] == "SOURCE_LIMITED"
    assert payload["candidate_policy"] == {
        "candidate_system_count": 13,
        "admitted_system_count": 6,
        "admitted_component_row_count": 12,
        "excluded_system_count": 7,
        "debcat_whole_system_intersection_count": 0,
        "selection_basis": "source_completeness_and_component_mapping_only",
    }
    candidates = {item["queried_id"] for item in _load(ALIAS_PATH)["candidates"]}
    represented = {row["system_id"] for row in payload["rows"]}
    represented |= {item["system_id"] for item in payload["excluded_systems"]}
    assert represented == candidates


def test_frozen_inputs_and_identifier_intersection() -> None:
    payload = _load(ROWS_PATH)
    assert _sha256(ALIAS_PATH) == payload["frozen_inputs"]["alias_ledger"]["sha256"]
    assert _sha256(DEBCAT_PATH) == payload["frozen_inputs"]["debcat_rows"]["sha256"]
    debcat_ids = {_normalize(row["system_id"]) for row in _load(DEBCAT_PATH)["rows"]}
    candidate_ids = {
        _normalize(item["queried_id"]) for item in _load(ALIAS_PATH)["candidates"]
    }
    assert candidate_ids.isdisjoint(debcat_ids)


def test_rows_are_complete_component_pairs_without_split_or_metrics() -> None:
    payload = _load(ROWS_PATH)
    by_system: dict[str, set[str]] = {}
    forbidden = {"split", "lane", "residual", "metric", "prediction", "fit"}
    for row in payload["rows"]:
        by_system.setdefault(row["system_id"], set()).add(row["component_id"])
        assert row["mass_solar"] > 0
        assert row["mass_uncertainty_solar"] > 0
        assert row["luminosity_solar"] > 0
        assert row["luminosity_uncertainty_solar"] > 0
        assert row["source_location"].startswith("Table ")
        assert forbidden.isdisjoint(row)
    assert set(by_system) == {
        "HD 8374", "HD 24546", "HD 61859", "HD 89822", "HD 109510", "HD 191692"
    }
    assert all(components == {"A", "B"} for components in by_system.values())


def test_derived_luminosities_replay_stefan_boltzmann() -> None:
    for row in _load(ROWS_PATH)["rows"]:
        inputs = row.get("luminosity_inputs")
        if inputs is None:
            continue
        radius = inputs["radius_solar"]
        radius_error = inputs["radius_uncertainty_solar"]
        temperature = inputs["teff_k"]
        temperature_error = inputs["teff_uncertainty_k"]
        luminosity = radius**2 * (temperature / 5772.0) ** 4
        relative_error = math.sqrt(
            (2 * radius_error / radius) ** 2
            + (4 * temperature_error / temperature) ** 2
        )
        assert math.isclose(row["luminosity_solar"], luminosity, rel_tol=1e-7)
        assert math.isclose(
            row["luminosity_uncertainty_solar"],
            luminosity * relative_error,
            rel_tol=1e-6,
        )


def test_source_artifacts_are_hash_pinned_or_explicitly_blocked() -> None:
    artifacts = _load(ROWS_PATH)["source_artifacts"]
    assert len(artifacts) == 7
    for artifact in artifacts:
        assert artifact["values_used"] is False or artifact.get("sha256")
        if artifact["source_id"] != "hd284163-supplement":
            assert len(artifact["sha256"]) == 64
            assert artifact["bytes"] > 0
    supplement = next(
        item for item in artifacts if item["source_id"] == "hd284163-supplement"
    )
    assert supplement["pin_status"] == "checksum_unavailable"
    assert supplement["values_used"] is False
