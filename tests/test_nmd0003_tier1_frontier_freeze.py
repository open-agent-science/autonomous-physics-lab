"""Guards for the TASK-0933 tier-1 point-only NMD-0003 frontier freeze artifacts.

Fast tests verify the frozen PRED entries structurally (point-only payloads,
mandatory caveat, disjointness requirement, re-verified no-peek target set) and
recompute the two closed-form comparator surfaces exactly. The full-surface GP
recompute is a ``full_repo`` smoke test because the deterministic GP refit on
the committed training surface takes tens of seconds.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path

import pytest

from physics_lab.engines.nmd0003_duflo_zuker_baseline import (
    FEATURE_NAMES,
    predict_duflo_zuker_binding_energy,
)
from physics_lab.engines.nmd0003_residual_gp import _frozen_baseline_coefficients
from physics_lab.engines.nuclear_mass_baselines import semi_empirical_binding_energy
from physics_lab.registry.nuclear_mass_predictions import load_nuclear_mass_prediction
from scripts.freeze_nmd0003_tier1_point_only_frontier import (
    AGENT_RUN_0078_METRICS_PATH,
    DISJOINTNESS_REQUIREMENT,
    GATE_PATH,
    HOLDOUT_PATH,
    MANDATORY_CAVEAT,
    NMD0002_SLICE_PATH,
    PREDICTION_IDS,
    TARGET_SET_LABEL,
    TASK_ID,
    TRAINING_PATH,
    _committed_identity_screens,
    _load_yaml,
    load_manifest_targets,
    reverify_source_state,
)
from scripts.freeze_nmd0003_tier1_point_only_frontier import (
    MANIFEST_PATH as FREEZE_MANIFEST_PATH,
)

ROOT = Path(__file__).resolve().parents[1]
REVIEW_NOTE_PATH = ROOT / "docs" / "reviews" / "nmd0003-tier1-point-only-frontier-freeze.md"


@lru_cache(maxsize=1)
def _entries() -> dict[str, dict[str, object]]:
    return {
        prediction_id: load_nuclear_mass_prediction(
            ROOT / "prediction_registry" / "nuclear_masses" / f"{prediction_id}.yaml"
        )
        for prediction_id in PREDICTION_IDS.values()
    }


@lru_cache(maxsize=1)
def _reverified_survivors() -> tuple[tuple[str, int, int, int], ...]:
    targets, manifest_payload = load_manifest_targets(ROOT / FREEZE_MANIFEST_PATH)
    screens = _committed_identity_screens(
        training_path=ROOT / TRAINING_PATH,
        holdout_path=ROOT / HOLDOUT_PATH,
        nmd0002_slice_path=ROOT / NMD0002_SLICE_PATH,
    )
    surviving, dropped = reverify_source_state(targets, manifest_payload, screens)
    assert not dropped, "committed freeze recorded 0 dropped targets"
    return tuple((target.nuclide_id, target.z, target.n, target.a) for target in surviving)


def _normalized(text: str) -> str:
    """Collapse blockquote markers, line wraps, and wrapped hyphenation for comparison."""
    joined = " ".join(line.lstrip("> ") for line in text.splitlines())
    return " ".join(joined.split()).replace("- ", "-")


def test_tier1_freeze_entries_are_point_only_and_registered() -> None:
    for prediction_id, payload in _entries().items():
        assert payload["prediction_id"] == prediction_id
        assert payload["freeze_tier"] == "point_only"
        assert payload["registry_status"] == "REGISTERED"
        assert payload["task_id"] == TASK_ID
        assert payload["registered_by"] == {"contributor_id": "gladunrv", "agent_id": "claude"}
        assert payload["target_set"]["label"] == TARGET_SET_LABEL
        assert payload["target_set"]["quantity"] == "binding_energy_mev"
        assert payload["target_set"]["unit"] == "MeV"
        assert payload["uncertainty_semantics"]["type"] == "point_estimate_only"
        targets = payload["target_set"]["target_nuclides"]
        assert len(targets) == 37
        for target in targets:
            assert target["uncertainty_mev"] is None
            assert target["A"] == target["Z"] + target["N"]


def test_tier1_freeze_targets_match_reverified_no_peek_survivors() -> None:
    survivors = _reverified_survivors()
    assert len(survivors) == 37
    for payload in _entries().values():
        frozen = tuple(
            (str(t["nuclide_id"]), int(t["Z"]), int(t["N"]), int(t["A"]))
            for t in payload["target_set"]["target_nuclides"]
        )
        assert frozen == survivors


def test_tier1_freeze_excludes_committed_neighbors() -> None:
    _, manifest_payload = load_manifest_targets(ROOT / FREEZE_MANIFEST_PATH)
    excluded = manifest_payload["excluded_committed_neighbors"]
    excluded_zn = {
        (int(row["Z"]), int(row["N"]))
        for key in ("in_nmd0003_training", "in_post_ame2020_holdout")
        for row in excluded[key]
    }
    for payload in _entries().values():
        frozen_zn = {
            (int(t["Z"]), int(t["N"])) for t in payload["target_set"]["target_nuclides"]
        }
        assert not (frozen_zn & excluded_zn)


def test_tier1_freeze_carries_mandatory_caveat_and_disjointness() -> None:
    for payload in _entries().values():
        limitations = list(payload["limitations"])
        assert MANDATORY_CAVEAT in limitations
        assert DISJOINTNESS_REQUIREMENT in limitations
        assert "no claim" in str(payload["claim_ceiling"]).lower()
        assert "TASK-0827" in MANDATORY_CAVEAT


def test_tier1_freeze_review_note_carries_caveat_verbatim() -> None:
    note_text = REVIEW_NOTE_PATH.read_text(encoding="utf-8")
    assert _normalized(MANDATORY_CAVEAT) in _normalized(note_text)
    assert "TASK-0925" in note_text
    assert "dropped" in note_text.lower()


def test_tier1_frozen_closed_form_comparators_recompute_exactly() -> None:
    entries = _entries()
    gate = _load_yaml(ROOT / GATE_PATH)
    coefficients = _frozen_baseline_coefficients(gate)
    committed_metrics = json.loads(
        (ROOT / AGENT_RUN_0078_METRICS_PATH).read_text(encoding="utf-8")
    )
    dz10_coefficients = {
        name: float(committed_metrics["coefficients"][name]) for name in FEATURE_NAMES
    }

    for target in entries[PREDICTION_IDS["liquid_drop"]]["target_set"]["target_nuclides"]:
        expected = round(
            semi_empirical_binding_energy(
                z=int(target["Z"]), n=int(target["N"]), coefficients=coefficients
            ),
            6,
        )
        assert expected == float(target["predicted_value_mev"])

    for target in entries[PREDICTION_IDS["dz10"]]["target_set"]["target_nuclides"]:
        expected = round(
            predict_duflo_zuker_binding_energy(
                z=int(target["Z"]), n=int(target["N"]), coefficients=dz10_coefficients
            ),
            6,
        )
        assert expected == float(target["predicted_value_mev"])


@pytest.mark.full_repo
@pytest.mark.timeout(300)
def test_tier1_full_surface_recompute_matches_frozen_values() -> None:
    """Full deterministic refit of the GP and smooth-A surfaces matches the freeze.

    ``compute_freeze`` also re-runs every frozen-surface identity check against
    the committed RESULT-0025 / AGENT-RUN-0078 metrics and raises on any drift.
    """
    from scripts.freeze_nmd0003_tier1_point_only_frontier import compute_freeze

    freeze = compute_freeze(ROOT)
    assert not freeze["dropped"]
    entries = _entries()
    for model_key, prediction_id in PREDICTION_IDS.items():
        frozen_values = [
            float(t["predicted_value_mev"])
            for t in entries[prediction_id]["target_set"]["target_nuclides"]
        ]
        assert frozen_values == freeze["forecasts"][model_key]
