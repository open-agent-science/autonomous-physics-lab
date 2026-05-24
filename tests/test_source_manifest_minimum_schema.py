from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from physics_lab.registry.validation import validate_document


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / "templates" / "source_manifest_minimum.yaml"


def _load_template() -> dict[str, object]:
    payload = yaml.safe_load(TEMPLATE_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_source_manifest_minimum_template_validates() -> None:
    payload = _load_template()

    result = validate_document(
        payload,
        "source_manifest_minimum",
        TEMPLATE_PATH,
    )

    assert result is payload
    assert payload["claim_promotion_allowed"] is False
    assert payload["benchmark_allowed"] is False
    assert payload["live_fetch_allowed_in_validation"] is False


def test_source_manifest_minimum_rejects_extra_top_level_fields() -> None:
    payload = _load_template()
    payload["measurement_values"] = [1.0, 2.0]

    with pytest.raises(ValueError, match="schema validation"):
        validate_document(payload, "source_manifest_minimum", TEMPLATE_PATH)


def test_source_manifest_minimum_requires_locator_surface() -> None:
    payload = _load_template()
    source = payload["sources"][0]  # type: ignore[index]
    del source["locators"]["citation"]  # type: ignore[index]

    with pytest.raises(ValueError, match="schema validation"):
        validate_document(payload, "source_manifest_minimum", TEMPLATE_PATH)


def test_source_manifest_minimum_rejects_claim_promotion() -> None:
    payload = _load_template()
    payload["claim_promotion_allowed"] = True

    with pytest.raises(ValueError, match="schema validation"):
        validate_document(payload, "source_manifest_minimum", TEMPLATE_PATH)


def test_source_manifest_minimum_accepts_checksum_pinned_artifact() -> None:
    payload = copy.deepcopy(_load_template())
    source = payload["sources"][0]  # type: ignore[index]
    artifact = source["artifact"]  # type: ignore[index]
    artifact["artifact_type"] = "csv_snapshot"  # type: ignore[index]
    artifact["artifact_path_or_locator"] = "data/example/raw/source.csv"  # type: ignore[index]
    artifact["checksum_sha256"] = "a" * 64  # type: ignore[index]
    artifact["checksum_scope"] = "raw_artifact"  # type: ignore[index]
    artifact["value_bearing_artifact"] = True  # type: ignore[index]
    source["row_admissibility"]["inclusion_status"] = "requires_review"  # type: ignore[index]
    source["extraction"]["extraction_method"] = "api_snapshot"  # type: ignore[index]
    source["extraction"]["review_status"] = "needs_source_review"  # type: ignore[index]

    validate_document(payload, "source_manifest_minimum", TEMPLATE_PATH)
