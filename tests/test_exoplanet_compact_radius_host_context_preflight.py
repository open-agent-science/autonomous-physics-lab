"""Tests for the TASK-0481 compact-radius host-context preflight."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.resource_sensitive,
    pytest.mark.xdist_group(name="exoplanet_snapshot"),
]

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_exoplanet_compact_radius_host_context_preflight as preflight  # noqa: E402
from physics_lab.registry.agent_runs import (  # noqa: E402
    validate_agent_run_payload,
)

SNAPSHOT_PATH = (
    ROOT / "data" / "exoplanets" / "exo-0001-pscomppars-snapshot.yaml"
)


def test_number_or_none_accepts_metallicity_zero_and_negative_values():
    assert preflight._number_or_none(0.0) == 0.0
    assert preflight._number_or_none(-0.3) == -0.3
    assert preflight._number_or_none(0.0, positive_only=True) is None
    assert preflight._number_or_none(float("nan")) is None


def test_classification_thresholds():
    assert (
        preflight._classification(denominator=20, present=20, interpretable_bin_count=2)
        == "blocked_by_low_slice_count"
    )
    assert (
        preflight._classification(denominator=100, present=20, interpretable_bin_count=2)
        == "blocked_by_missingness"
    )
    assert (
        preflight._classification(denominator=100, present=90, interpretable_bin_count=1)
        == "coverage_usable_partition_underpowered"
    )
    assert (
        preflight._classification(denominator=100, present=60, interpretable_bin_count=2)
        == "conditionally_usable"
    )
    assert (
        preflight._classification(denominator=100, present=90, interpretable_bin_count=2)
        == "benchmark_usable"
    )


@pytest.fixture(scope="module")
def metrics() -> dict:
    return preflight.build_metrics(SNAPSHOT_PATH)


def _compact_field(metrics: dict, field_id: str) -> dict:
    return next(
        item
        for item in metrics["field_coverage"]["compact_radius"]
        if item["field_id"] == field_id
    )


def test_committed_snapshot_compact_slice_preflight_summary(metrics):
    assert metrics["loader_summary"]["eligible_true_mass_with_transit_radius"] == 1207
    assert metrics["loader_summary"]["compact_slice_count"] == 92
    assert metrics["preflight_status"] == "conditional_only_partition_underpowered"
    assert metrics["verdict"] == "INCONCLUSIVE"
    assert metrics["axis_recommendations"]["benchmark_usable"] == []
    assert set(metrics["axis_recommendations"]["conditional_or_partition_underpowered"]) == {
        "host_effective_temperature_K",
        "host_metallicity_fe_h",
        "stellar_radius_rsun",
        "equilibrium_temperature_K",
        "irradiation_flux_earth_units",
    }
    assert metrics["axis_recommendations"]["blocked_by_missingness"] == []


def test_compact_slice_field_counts_preserve_missingness(metrics):
    teff = _compact_field(metrics, "host_effective_temperature_K")
    metallicity = _compact_field(metrics, "host_metallicity_fe_h")
    stellar_radius = _compact_field(metrics, "stellar_radius_rsun")
    eq_temp = _compact_field(metrics, "equilibrium_temperature_K")
    flux = _compact_field(metrics, "irradiation_flux_earth_units")

    assert teff["present_count"] == 90
    assert teff["missing_count"] == 2
    assert teff["status"] == "coverage_usable_partition_underpowered"
    assert metallicity["present_count"] == 81
    assert metallicity["missing_count"] == 11
    assert stellar_radius["present_count"] == 92
    assert stellar_radius["missing_count"] == 0
    assert eq_temp["present_count"] == 70
    assert eq_temp["missing_count"] == 22
    assert flux["present_count"] == 61
    assert flux["missing_count"] == 31


def test_data_boundary_flags(metrics):
    assert metrics["data_boundary"]["live_external_fetch_performed"] is False
    assert metrics["data_boundary"]["correction_model_fit_performed"] is False
    assert metrics["data_boundary"]["baseline_refit_performed"] is False
    assert metrics["data_boundary"]["canonical_result_written"] is False
    assert metrics["data_boundary"]["claim_or_knowledge_update_performed"] is False


def test_write_outputs_and_validate_agent_run(tmp_path, metrics):
    out = tmp_path / "metrics.json"
    agent_run = tmp_path / "agent_run.yaml"
    preflight.write_outputs(
        metrics,
        out=out,
        report=tmp_path / "report.md",
        agent_run=agent_run,
        limitations=tmp_path / "limitations.md",
        preflight=tmp_path / "preflight.md",
        review_summary=tmp_path / "review_summary.md",
        review=tmp_path / "review.md",
    )
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["preflight_status"] == "conditional_only_partition_underpowered"

    payload = preflight._build_agent_run_payload(metrics)
    validate_agent_run_payload(payload, source=agent_run)
    assert payload["sandbox_only"] is True
    assert payload["promotion_boundary"]["writes_canonical_result"] is False


def test_committed_agent_run_manifest_validates_under_repo_root(metrics):
    payload = preflight._build_agent_run_payload(metrics)
    validate_agent_run_payload(
        payload,
        source=ROOT / "agent_runs" / preflight.AGENT_RUN_ID / "agent_run.yaml",
        root=ROOT,
    )
