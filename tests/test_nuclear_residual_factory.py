"""Tests for the Nuclear residual-law factory adapter (TASK-0506)."""

from __future__ import annotations

from pathlib import Path

import yaml

import physics_lab.factories  # noqa: F401  (registers the nuclear adapter)
from physics_lab.factories.core import FactorySpec, get_adapter, run_factory
from physics_lab.registry.validation import validate_document

REPO_ROOT = Path(__file__).resolve().parents[1]
SMOKE_CONFIG = REPO_ROOT / "examples" / "factories" / "nuclear_residual_factory_smoke.yaml"
SPRINT_CONFIG = REPO_ROOT / "examples" / "factories" / "nuclear_residual_factory_sprint.yaml"


def _sprint_summary() -> dict:
    config = yaml.safe_load(SPRINT_CONFIG.read_text(encoding="utf-8"))
    spec = FactorySpec.from_config(config)
    return run_factory(spec, get_adapter(spec.adapter_id))


def test_sprint_generates_bounded_multi_family_sweep() -> None:
    summary = _sprint_summary()
    counts = summary["candidate_counts"]
    assert 50 <= counts["generated"] <= 100
    executed_families = {
        c["family"] for c in summary["candidates"] if c["candidate_state"] != "PREFLIGHT_REJECTED"
    }
    assert len(executed_families) >= 4
    assert validate_document(summary, "factory_summary", "x/factory_summary.yaml") is summary


def test_sprint_produces_no_false_positive_shortlist_on_small_slice() -> None:
    summary = _sprint_summary()
    # The committed slice has only 3 holdout nuclides -> shortlist is impossible.
    assert summary["candidate_counts"]["shortlisted"] == 0
    routes = summary["route_verdict_summary"]
    assert routes.get("NEGATIVE_RESULT", 0) > 0
    # Negative + inconclusive memory dominates the executed candidates.
    assert routes.get("NEGATIVE_RESULT", 0) + routes.get("INCONCLUSIVE", 0) >= 50


def test_sprint_preflight_blocks_leakage_sensitive_family() -> None:
    summary = _sprint_summary()
    blocked = [c for c in summary["candidates"] if c["candidate_state"] == "PREFLIGHT_REJECTED"]
    assert any(c["family"] == "local_curvature" for c in blocked)
    assert all(c["route_verdict"] == "DATA_QUALITY_BLOCKED" for c in blocked)


def _smoke_spec() -> FactorySpec:
    config = yaml.safe_load(SMOKE_CONFIG.read_text(encoding="utf-8"))
    return FactorySpec.from_config(config)


def test_smoke_config_runs_and_is_schema_valid() -> None:
    spec = _smoke_spec()
    adapter = get_adapter(spec.adapter_id)
    summary = run_factory(spec, adapter)

    # Two allowed families -> two candidates, both executed and structurally clean.
    assert summary["candidate_counts"]["generated"] == 2
    families = {c["family"] for c in summary["candidates"]}
    assert families == {"shell_distance", "odd_even_pairing"}
    assert all(c["leakage_status"] == "CHECKED_CLEAN" for c in summary["candidates"])
    # Every candidate carries null + shuffled control outcomes.
    for candidate in summary["candidates"]:
        names = {item["name"] for item in candidate["control_outcomes"]}
        assert {"null_baseline", "shuffled_feature"} <= names
    assert validate_document(summary, "factory_summary", "x/factory_summary.yaml") is summary


def test_smoke_config_uses_committed_frozen_baseline_coefficients() -> None:
    spec = _smoke_spec()
    summary = run_factory(spec, get_adapter(spec.adapter_id))

    assert spec.baseline["coefficients_ref"] == "results/EXP-0012/RUN-0001/result.yaml"
    assert summary["campaign_specific"]["baseline_coefficients_ref"] == (
        "results/EXP-0012/RUN-0001/result.yaml"
    )


def test_route_verdicts_are_canonical() -> None:
    summary = run_factory(_smoke_spec(), get_adapter("nuclear_residual_factory"))
    canonical = {
        "NEGATIVE_RESULT",
        "INCONCLUSIVE",
        "SHORTLIST_CANDIDATE",
        "READY_FOR_REPLAY",
        "READY_FOR_PRED_FREEZE",
        "REJECTED_BY_CONTROL",
        "LOCAL_ONLY",
        "DATA_QUALITY_BLOCKED",
    }
    assert all(c["route_verdict"] in canonical for c in summary["candidates"])


def test_leakage_sensitive_family_is_blocked_without_check() -> None:
    config = yaml.safe_load(SMOKE_CONFIG.read_text(encoding="utf-8"))
    config["families"] = ["local_curvature"]
    spec = FactorySpec.from_config(config)
    summary = run_factory(spec, get_adapter("nuclear_residual_factory"))

    assert len(summary["candidates"]) == 1
    candidate = summary["candidates"][0]
    assert candidate["family"] == "local_curvature"
    assert candidate["leakage_status"] == "NOT_CHECKED"
    assert candidate["candidate_state"] == "PREFLIGHT_REJECTED"
    assert candidate["route_verdict"] == "DATA_QUALITY_BLOCKED"


def test_leakage_sensitive_family_stays_blocked_even_with_generic_flag() -> None:
    config = yaml.safe_load(SMOKE_CONFIG.read_text(encoding="utf-8"))
    config["families"] = ["local_curvature"]
    config["options"] = {"leakage_check_applied": True}
    spec = FactorySpec.from_config(config)
    summary = run_factory(spec, get_adapter("nuclear_residual_factory"))

    assert summary["candidate_counts"]["generated"] == 1
    assert summary["candidates"][0]["candidate_state"] == "PREFLIGHT_REJECTED"
    assert summary["candidates"][0]["route_verdict"] == "DATA_QUALITY_BLOCKED"
