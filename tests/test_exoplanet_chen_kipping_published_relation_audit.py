from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_exoplanet_chen_kipping_published_relation_audit as audit  # noqa: E402
from physics_lab.engines.exoplanet_mass_radius import chen_kipping_predict_radius  # noqa: E402


def _row(index: int, mass: float, radius_scale: float = 1.0) -> dict:
    radius = chen_kipping_predict_radius(mass) * radius_scale
    return {
        "row_id": f"SYN-{index:04d}",
        "row_class": "direct_mass_radius_measurement",
        "planet_name": f"Synthetic Planet {index}",
        "planet_alt_names": [],
        "host_star": {"name": f"Synthetic Star {index}"},
        "detection_method": "transit",
        "mass": {
            "value": mass,
            "unit": "mearth",
            "uncertainty_upper": 0.1 * mass,
            "uncertainty_lower": -0.1 * mass,
            "uncertainty_semantics": "synthetic",
            "mass_class": "true_mass",
            "mass_method_label": "Mass",
        },
        "radius": {
            "value": radius,
            "unit": "rearth",
            "uncertainty_upper": 0.05 * radius,
            "uncertainty_lower": -0.05 * radius,
            "uncertainty_semantics": "synthetic",
            "radius_class": "transit_radius",
            "radius_method_label": "Transit radius",
        },
        "source_id": "EXO-SRC-CLASS-001",
        "source_table_ref": "synthetic",
        "inclusion_status": "included",
        "inclusion_reason": "synthetic",
        "provenance_notes": "synthetic",
    }


def _snapshot(path: Path, dataset_id: str) -> None:
    masses = [0.7 + index * 0.08 for index in range(40)]
    masses += [4.0 + index * 2.0 for index in range(40)]
    masses += [150.0 + index * 25.0 for index in range(40)]
    rows = [_row(index, mass, 1.0 + 0.02 * ((index % 5) - 2)) for index, mass in enumerate(masses)]
    rows.append(_row(500, audit.BROWN_DWARF_CAP_MEARTH + 1.0))
    minimum = _row(501, 30.0)
    minimum["row_class"] = "transit_radius_with_rv_minimum_mass"
    minimum["mass"]["mass_class"] = "minimum_mass_msini"
    rows.append(minimum)
    excluded = _row(502, 10.0)
    excluded["inclusion_status"] = "excluded"
    rows.append(excluded)
    payload = {
        "dataset_id": dataset_id,
        "title": "Synthetic audit snapshot",
        "status": "draft",
        "description": "Synthetic rows for TASK-0866 tests.",
        "source_policy": "Synthetic; no live fetch.",
        "snapshot_provenance": {
            "source_family_id": "EXO-SRC-CLASS-001",
            "source_locator": "synthetic://task-0866",
            "retrieval_date_utc": "2026-06-28T00:00:00Z",
            "release_date_or_publication_date": None,
            "snapshot_kind": "synthetic_dry_run",
            "live_external_fetch_allowed": False,
            "raw_checksum_sha256": None,
            "normalized_checksum_sha256": None,
            "parser_or_normalizer": None,
            "license_or_reuse_notes": "Synthetic fixture.",
        },
        "row_class_coverage": [
            "direct_mass_radius_measurement",
            "transit_radius_with_rv_minimum_mass",
        ],
        "fake_source_warning": "Synthetic rows only.",
        "entries": rows,
        "limitations": ["Synthetic fixture."],
    }
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def test_real_snapshot_counts_match_frozen_readiness_contract() -> None:
    primary = audit._evaluate_snapshot(audit.PRIMARY_SNAPSHOT)
    compatibility = audit._evaluate_snapshot(audit.COMPATIBILITY_SNAPSHOT)

    assert primary["counts"]["all_entries"] == 6298
    assert primary["counts"]["direct_true_mass_transit_radius"] == 1449
    assert primary["counts"]["primary_below_13_mjup"] == 1433
    assert primary["counts"]["primary_with_complete_uncertainty"] == 1294
    assert primary["counts"]["boundary_at_or_above_13_mjup"] == 16
    assert compatibility["counts"]["all_entries"] == 6291
    assert compatibility["counts"]["primary_below_13_mjup"] == 1432


def test_train_fitted_controls_are_not_changed_by_test_radius_edits() -> None:
    rows = [_row(index, 1.0 + index * 0.3) for index in range(80)]
    train, test = audit._split_rows(rows)
    before = audit._freeze_controls(train)
    for row in test:
        row["radius"]["value"] *= 20.0
    after = audit._freeze_controls(train)

    assert before == after
    assert train
    assert test


def test_main_writes_deterministic_sandbox_bundle(tmp_path: Path) -> None:
    primary = tmp_path / "primary.yaml"
    compatibility = tmp_path / "compatibility.yaml"
    _snapshot(primary, "synthetic-primary")
    _snapshot(compatibility, "synthetic-compatibility")
    first = tmp_path / "first"
    second = tmp_path / "second"

    for output in (first, second):
        assert (
            audit.main(
                [
                    "--primary",
                    str(primary),
                    "--compatibility",
                    str(compatibility),
                    "--out-dir",
                    str(output),
                    "--review",
                    str(output / "review.md"),
                ]
            )
            == 0
        )

    assert (first / "metrics.json").read_text(encoding="utf-8") == (
        second / "metrics.json"
    ).read_text(encoding="utf-8")
    metrics = json.loads((first / "metrics.json").read_text(encoding="utf-8"))
    agent_run = yaml.safe_load((first / "agent_run.yaml").read_text(encoding="utf-8"))
    assert set(metrics["frozen_protocol"]["controls"]) == set(audit.CONTROL_IDS)
    assert (
        metrics["snapshots"]["primary_exo_0002"]["probabilistic_calibration"]["status"]
        == "NOT_ATTEMPTED"
    )
    assert metrics["snapshots"]["primary_exo_0002"]["counts"]["boundary_at_or_above_13_mjup"] == 1
    assert (
        metrics["snapshots"]["primary_exo_0002"]["counts"]["minimum_mass_diagnostic_below_13_mjup"]
        == 1
    )
    assert agent_run["id"] == "AGENT-RUN-0088"
    assert agent_run["sandbox_only"] is True
    assert agent_run["status"] == "REVIEW_READY"
