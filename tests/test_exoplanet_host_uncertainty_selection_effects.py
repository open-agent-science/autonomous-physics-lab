"""Tests for the TASK-0392 exoplanet selection-effects audit."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_exoplanet_host_uncertainty_selection_effects as audit  # noqa: E402
from physics_lab.engines.exoplanet_mass_radius import (  # noqa: E402
    chen_kipping_predict_radius,
)


def _entry(
    *,
    idx: int,
    mass: float,
    residual: float,
    host_teff: float | None,
    stellar_mass: float | None,
    stellar_radius: float | None,
    detection_method: str,
    mass_class: str = "true_mass",
    mass_uncertainty: float | None = 0.10,
    radius_uncertainty: float | None = 0.04,
) -> dict:
    radius = chen_kipping_predict_radius(mass) * (10.0**residual)
    return {
        "row_id": f"SYN-{idx:04d}",
        "row_class": "direct_mass_radius_measurement",
        "planet_name": f"SYNTH-{idx:04d} b",
        "planet_alt_names": [],
        "host_star": {
            "name": f"SYNTH-HOST-{idx:04d}",
            "spectral_type": None,
            "effective_temperature_K": host_teff,
            "stellar_mass_msun": stellar_mass,
            "stellar_radius_rsun": stellar_radius,
            "metallicity_fe_h": None,
            "stellar_age_gyr": None,
            "notes": "synthetic",
        },
        "detection_method": detection_method,
        "mass": {
            "value": mass,
            "unit": "mearth",
            "uncertainty_upper": (
                None if mass_uncertainty is None else mass * mass_uncertainty
            ),
            "uncertainty_lower": (
                None if mass_uncertainty is None else -mass * mass_uncertainty
            ),
            "uncertainty_semantics": "1-sigma",
            "mass_class": mass_class,
            "mass_method_label": "synthetic",
        },
        "radius": {
            "value": radius,
            "unit": "rearth",
            "uncertainty_upper": (
                None if radius_uncertainty is None else radius * radius_uncertainty
            ),
            "uncertainty_lower": (
                None if radius_uncertainty is None else -radius * radius_uncertainty
            ),
            "uncertainty_semantics": "1-sigma",
            "radius_class": "transit_radius",
            "radius_method_label": "synthetic",
        },
        "equilibrium_temperature_K": None,
        "irradiation_flux_earth_units": None,
        "orbital_period_days": None,
        "orbital_semimajor_axis_au": None,
        "discovery_year": 2026,
        "source_id": "EXO-SRC-CLASS-001",
        "source_table_ref": "synthetic",
        "inclusion_status": "included",
        "inclusion_reason": "synthetic",
        "provenance_notes": "synthetic toy row",
    }


def _synthetic_snapshot(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    entries: list[dict] = []
    idx = 1
    for _ in range(40):
        entries.append(
            _entry(
                idx=idx,
                mass=8.0 + (idx % 5) * 0.1,
                residual=0.30,
                host_teff=5000.0,
                stellar_mass=0.85,
                stellar_radius=0.82,
                detection_method="transit",
                mass_uncertainty=0.04,
            )
        )
        idx += 1
    for _ in range(40):
        entries.append(
            _entry(
                idx=idx,
                mass=8.0 + (idx % 5) * 0.1,
                residual=0.28,
                host_teff=6200.0,
                stellar_mass=1.1,
                stellar_radius=1.2,
                detection_method="radial velocity",
                mass_uncertainty=0.04,
            )
        )
        idx += 1
    for _ in range(40):
        entries.append(
            _entry(
                idx=idx,
                mass=20.0 + (idx % 5) * 0.1,
                residual=0.0,
                host_teff=5700.0,
                stellar_mass=1.0,
                stellar_radius=1.0,
                detection_method="transit",
                mass_uncertainty=None,
                radius_uncertainty=None,
            )
        )
        idx += 1
    for _ in range(2):
        entries.append(
            _entry(
                idx=idx,
                mass=15.0,
                residual=0.10,
                host_teff=4800.0,
                stellar_mass=0.8,
                stellar_radius=0.8,
                detection_method="radial_velocity",
                mass_class="minimum_mass_msini",
            )
        )
        idx += 1

    payload = {
        "dataset_id": "synthetic-selection-effects",
        "title": "Synthetic selection-effects fixture",
        "status": "draft",
        "description": "Synthetic rows for TASK-0392 tests.",
        "source_policy": "Synthetic; no live fetch.",
        "snapshot_provenance": {
            "source_family_id": "EXO-SRC-CLASS-001",
            "source_locator": "synthetic://selection-effects",
            "retrieval_date_utc": "2026-05-27T00:00:00Z",
            "release_date_or_publication_date": None,
            "snapshot_kind": "synthetic_dry_run",
            "live_external_fetch_allowed": False,
            "raw_checksum_sha256": None,
            "normalized_checksum_sha256": None,
            "parser_or_normalizer": None,
            "license_or_reuse_notes": "Synthetic test fixture.",
        },
        "row_class_coverage": ["direct_mass_radius_measurement"],
        "fake_source_warning": "Synthetic rows only.",
        "entries": entries,
        "limitations": ["Synthetic fixture."],
    }
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def _run_runner(tmp_path: Path) -> dict:
    metrics_path = tmp_path / "metrics.json"
    audit.main(
        [
            "--snapshot",
            str(_synthetic_snapshot(tmp_path / "snapshot.yaml")),
            "--out",
            str(metrics_path),
            "--report",
            str(tmp_path / "report.md"),
            "--agent-run",
            str(tmp_path / "agent_run.yaml"),
            "--limitations",
            str(tmp_path / "limitations.md"),
            "--preflight",
            str(tmp_path / "preflight.md"),
            "--review-summary",
            str(tmp_path / "review_summary.md"),
            "--review",
            str(tmp_path / "review.md"),
        ]
    )
    return json.loads(metrics_path.read_text(encoding="utf-8"))


def test_uncertainty_band_helpers():
    assert audit._mass_uncertainty_band(None) == "missing_mass_uncertainty"
    assert audit._mass_uncertainty_band(0.05) == "tight_le5pct"
    assert audit._mass_uncertainty_band(0.10) == "moderate_5_15pct"
    assert audit._mass_uncertainty_band(0.25) == "loose_15_30pct"
    assert audit._radius_uncertainty_band(None) == "missing_radius_uncertainty"
    assert audit._radius_uncertainty_band(0.05) == "tight_le5pct"
    assert audit._radius_uncertainty_band(0.08) == "moderate_5_10pct"
    assert audit._radius_uncertainty_band(0.12) == "loose_10_15pct"


def test_classify_control_erases_apparent_signal():
    out = audit._classify_slice(
        slice_stats={"count": 40, "log10_rmse": 0.30},
        control_stats={"count": 40, "log10_rmse": 0.285},
        axis_stats={"count": 120, "log10_rmse": 0.20},
        control_status="matched",
    )
    assert out["outcome"] == "apparent_signal_erased_by_control"


def test_classify_persistent_selection_effect():
    out = audit._classify_slice(
        slice_stats={"count": 40, "log10_rmse": 0.30},
        control_stats={"count": 40, "log10_rmse": 0.20},
        axis_stats={"count": 120, "log10_rmse": 0.20},
        control_status="matched",
    )
    assert out["outcome"] == "selection_effect_persists_vs_control"


def test_runner_produces_selection_effect_bundle(tmp_path):
    metrics = _run_runner(tmp_path)
    assert metrics["task_id"] == "TASK-0392"
    assert metrics["agent_run_id"] == "AGENT-RUN-0038"
    assert metrics["data_boundary"]["live_external_fetch_performed"] is False
    assert metrics["data_boundary"]["minimum_mass_rows_in_headline_metrics"] is False
    assert metrics["verdict"] == "INCONCLUSIVE"

    true_axis = metrics["axis_audits"]["true_mass_with_transit_radius"]
    min_axis = metrics["axis_audits"]["minimum_mass_with_transit_radius"]
    assert true_axis["overall"]["count"] == 120
    assert min_axis["overall"]["count"] == 2
    assert min_axis["underpowered_slice_count"] > 0

    k_slice = true_axis["dimensions"]["host_temperature"]["K_3900_5200K"]
    assert k_slice["sample_size_matched_control"]["status"] == "matched"
    assert k_slice["classification"]["outcome"] == (
        "apparent_signal_erased_by_control"
    )
    assert metrics["limitations_table"]


def test_runner_is_deterministic(tmp_path):
    first = _run_runner(tmp_path / "first")
    second = _run_runner(tmp_path / "second")
    first["snapshot_path"] = "<fixture>"
    second["snapshot_path"] = "<fixture>"
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_agent_run_yaml_preserves_promotion_boundary(tmp_path):
    _run_runner(tmp_path)
    payload = yaml.safe_load((tmp_path / "agent_run.yaml").read_text(encoding="utf-8"))
    assert payload["sandbox_only"] is True
    assert payload["created_by"]["agent_id"] == "codex"
    assert payload["proposal_paths"]["hypothesis"].endswith(
        "HYP-PROPOSAL-0053-exoplanet-selection-effects-audit.yaml"
    )
    assert payload["promotion_boundary"]["writes_canonical_result"] is False
    assert payload["promotion_boundary"]["claim_promotion_allowed"] is False
    assert payload["verdict"] == "INCONCLUSIVE"


def test_relative_uncertainty_uses_largest_absolute_side():
    assert audit._relative_uncertainty({"value": 2.0}) is None
    assert math.isclose(
        audit._relative_uncertainty(
            {"value": 2.0, "uncertainty_upper": 0.1, "uncertainty_lower": -0.4}
        ),
        0.2,
    )
