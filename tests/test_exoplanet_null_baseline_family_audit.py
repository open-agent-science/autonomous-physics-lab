from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_exoplanet_null_baseline_family_audit as audit  # noqa: E402
from physics_lab.engines.exoplanet_mass_radius import chen_kipping_predict_radius  # noqa: E402


def _entry(idx: int, *, mass: float, residual: float, radius: float | None = None) -> dict:
    predicted = chen_kipping_predict_radius(mass)
    actual_radius = radius if radius is not None else predicted * (10.0**residual)
    return {
        "row_id": f"SYN-{idx:04d}",
        "mass": {
            "value": mass,
            "mass_class": "true_mass",
            "uncertainty_upper": mass * 0.1,
            "uncertainty_lower": -mass * 0.1,
        },
        "radius": {
            "value": actual_radius,
            "radius_class": "transit_radius",
            "uncertainty_upper": actual_radius * 0.05,
            "uncertainty_lower": -actual_radius * 0.05,
        },
        "orbital_period_days": 3.0,
    }


def test_nearest_other_predictions_skip_self() -> None:
    rows = [_entry(1, mass=1.0, residual=0.0), _entry(2, mass=2.0, residual=0.1)]

    predictions = audit._nearest_other_predictions(rows, key=audit._log_mass)

    assert predictions["SYN-0001"] == audit._log_radius(rows[1])
    assert predictions["SYN-0002"] == audit._log_radius(rows[0])


def test_baseline_predictions_include_required_family_ids() -> None:
    rows = [_entry(i, mass=1.0 + i, residual=0.01 * i) for i in range(1, 5)]

    predictions = audit._baseline_predictions(rows)

    assert set(predictions) == {
        "ck17_frozen",
        "per_class_median",
        "nearest_mass_neighbor",
        "nearest_radius_neighbor",
        "uncertainty_band_median",
    }


def test_main_writes_metrics_and_report(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "snapshot.yaml"
    payload = {
        "dataset_id": "synthetic-null-baselines",
        "title": "Synthetic null baseline fixture",
        "status": "draft",
        "description": "Synthetic rows for TASK-0483 tests.",
        "source_policy": "Synthetic; no live fetch.",
        "snapshot_provenance": {
            "source_family_id": "EXO-SRC-CLASS-001",
            "source_locator": "synthetic://null-baselines",
            "retrieval_date_utc": "2026-05-31T00:00:00Z",
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
        "entries": [
            {
                **_entry(i, mass=1.0 + i * 0.2, residual=0.02),
                "row_class": "direct_mass_radius_measurement",
                "planet_name": f"SYN-{i} b",
                "planet_alt_names": [],
                "host_star": {"name": "SYN", "effective_temperature_K": 5000.0},
                "detection_method": "transit",
                "source_id": "EXO-SRC-CLASS-001",
                "source_table_ref": "synthetic",
                "inclusion_status": "included",
                "inclusion_reason": "synthetic",
                "provenance_notes": "synthetic",
            }
            for i in range(40)
        ],
        "limitations": ["Synthetic fixture."],
    }
    snapshot_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    metrics_path = tmp_path / "metrics.json"
    audit.main(
        [
            "--snapshot",
            str(snapshot_path),
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

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert metrics["task_id"] == "TASK-0483"
    assert metrics["audit_class"] == "BENCHMARK_CONTROL_PANEL"
    assert metrics["verdict"] == "INCONCLUSIVE"
    assert math.isfinite(
        metrics["axes"]["true_mass_with_transit_radius"]["axis_stats"]["ck17_frozen"]["log10_rmse"]
    )
