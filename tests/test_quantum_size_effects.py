from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from physics_lab.engines.quantum_size_effects import (
    load_direct_inp_absorption_rows,
    run_quantum_size_baseline,
)
from physics_lab.registry.examples import load_example_config


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml"
HOLDOUT_ID = "almeida-2023-inp-620nm"
KIM_LEDGER = (
    ROOT
    / "data/quantum_dots/digitization/kim-2020-nanomaterials-cdse-optical/extraction_ledger.yaml"
)
KIM_REVIEW_PATH = "docs/reviews/quantum/kim-2020-cdse-size-optical-extraction.md"
KIM_LEDGER_PATH = (
    "data/quantum_dots/digitization/kim-2020-nanomaterials-cdse-optical/"
    "extraction_ledger.yaml"
)
KIM_ABSORPTION_PATH = "data/quantum_dots/qd-0005-kim-2020-cdse-absorption.yaml"
KIM_EMISSION_PATH = "data/quantum_dots/qd-0006-kim-2020-cdse-emission.yaml"


def test_loader_keeps_only_six_direct_inp_absorption_rows() -> None:
    rows = load_direct_inp_absorption_rows(DATASET)
    assert len(rows) == 6
    assert {row.material for row in rows} == {"InP"}
    assert rows[-1].entry_id == HOLDOUT_ID
    assert all(row.size_sigma_nm > 0 for row in rows)


def test_frozen_benchmark_selects_fixed_reference_and_beats_controls() -> None:
    metrics = run_quantum_size_baseline(dataset_path=DATASET, holdout_id=HOLDOUT_ID)
    assert metrics["selected_model_id"] == "almeida_fixed_reference"
    assert metrics["selected_holdout_mae_ev"] == 0.04839501
    assert metrics["constant_null_holdout_mae_ev"] == 0.4202
    assert metrics["shuffled_control_holdout_mae_ev"] == 0.375675554
    assert metrics["holdout_improvement_vs_null_ev"] == 0.37180499
    assert metrics["scientific_verdict"] == "VALID_IN_RANGE"
    assert metrics["agent_verdict"] == "SANDBOX_PASS"


def test_property_and_split_boundaries_are_explicit() -> None:
    metrics = run_quantum_size_baseline(dataset_path=DATASET, holdout_id=HOLDOUT_ID)
    assert metrics["property_kind"] == "absorption_peak_eV"
    assert metrics["size_axis"] == "edge_length_nm"
    assert metrics["train_count"] == 5
    assert metrics["holdout_count"] == 1
    selected = next(
        model for model in metrics["models"] if model["model_id"] == metrics["selected_model_id"]
    )
    assert [row["split"] for row in selected["predictions"]].count("holdout") == 1


def test_row_order_and_metrics_are_deterministic() -> None:
    first = run_quantum_size_baseline(dataset_path=DATASET, holdout_id=HOLDOUT_ID)
    second = run_quantum_size_baseline(dataset_path=DATASET, holdout_id=HOLDOUT_ID)
    assert first == second


def test_runner_writes_valid_sandbox_layout(tmp_path: Path) -> None:
    config = ROOT / "examples/quantum_size_effects.yaml"
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/run_quantum_size_effects_baseline.py"),
            "--config",
            str(config),
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    payload = json.loads(completed.stdout)
    assert payload["scientific_verdict"] == "VALID_IN_RANGE"


def test_example_config_is_registered_without_canonical_result_placeholder() -> None:
    config = load_example_config(ROOT / "examples/quantum_size_effects.yaml")
    assert config["config_kind"] == "quantum_size_effects_baseline"
    assert config["task_id"] == "TASK-0225"
    assert "result_id" not in config


def test_example_config_rejects_missing_frozen_boundary(tmp_path: Path) -> None:
    source = ROOT / "examples/quantum_size_effects.yaml"
    data = yaml.safe_load(source.read_text(encoding="utf-8"))
    del data["holdout_entry_id"]
    invalid = tmp_path / "invalid-quantum-size-effects.yaml"
    invalid.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="holdout_entry_id"):
        load_example_config(invalid)


def _load_kim_ledger() -> dict:
    return yaml.safe_load(KIM_LEDGER.read_text(encoding="utf-8"))


def test_kim_source_and_panel_checksums_are_frozen_without_source_bytes() -> None:
    ledger = _load_kim_ledger()
    pins = ledger["source_pins"]

    assert pins["version_of_record_pdf"] == {
        "locator": (
            "https://mdpi-res.com/d_attachment/nanomaterials/"
            "nanomaterials-10-01589/article_deploy/nanomaterials-10-01589.pdf"
        ),
        "retrieved_utc": "2026-07-15",
        "bytes": 1368239,
        "sha256": "2dab8a6b4db18af88f7175ac0773747fe1aeb15d88f951a4a8536cdc2dd73edb",
        "matches_task_1043": True,
    }
    assert pins["europe_pmc_jats"]["sha256"] == (
        "6642fed609ad6540b61ca856d293d2b469c5ed7be9323479c9b76b023f668244"
    )
    assert pins["crossref_snapshot"]["sha256"] == (
        "6b3a36ba7160d7c3d12a54bc64b846ec358d569ee562e778e8ac64eca6526e9c"
    )
    assert ledger["figure_raster"]["panel_crop"] == {
        "geometry": "650x913+0+0",
        "dimensions_px": [650, 913],
        "sha256": "975fd9d33a14106dc7b42c8917aeeba86c591ca4c4c49087cd3c99dc54585c12",
        "committed": False,
    }
    forbidden_suffixes = {".pdf", ".png", ".jpg", ".jpeg"}
    assert not {
        path.suffix.lower()
        for path in KIM_LEDGER.parent.iterdir()
        if path.is_file()
    } & forbidden_suffixes


def test_kim_blocker_ledger_has_exactly_twelve_paired_observations() -> None:
    ledger = _load_kim_ledger()
    sizes = ledger["text_size_summaries"]
    optical = ledger["optical_observations"]
    samples = {f"CdSe-{index}" for index in range(1, 5)}

    assert ledger["schema_version"] == "1"
    assert len(sizes) == 4
    assert len(optical) == 8
    assert len(sizes) + len(optical) == 12
    assert {row["sample_id"] for row in sizes} == samples
    assert {row["sample_id"] for row in optical} == samples
    assert {row["property_kind"] for row in optical} == {
        "absorption_peak_eV",
        "emission_peak_eV",
    }
    assert {
        (row["sample_id"], row["property_kind"])
        for row in optical
    } == {
        (sample, property_kind)
        for sample in samples
        for property_kind in ("absorption_peak_eV", "emission_peak_eV")
    }
    assert {
        row["sample_id"]: (
            row["reported_hrtem_gaussian_fit_mean_diameter_nm"],
            row["reported_size_dispersion_nm"],
            row["reported_relative_dispersion_percent"],
        )
        for row in sizes
    } == {
        "CdSe-1": (2.7, 0.5, 20),
        "CdSe-2": (3.5, 0.6, 19),
        "CdSe-3": (3.7, 0.9, 26),
        "CdSe-4": (4.5, 0.5, 11),
    }
    assert all(row["morphology"] == "unknown_non_spherical" for row in sizes + optical)
    assert all(row["instrument_uncertainty"] == "not_reported" for row in sizes)
    assert all(row["source_locator"] for row in sizes + optical)


def test_kim_two_pass_points_preserve_required_provenance_and_axis_failure() -> None:
    ledger = _load_kim_ledger()
    passes = ledger["digitization"]["passes"]
    uncertainty_policy = ledger["digitization"]["coordinate_uncertainty_policy"]
    required_point_fields = {
        "point_id",
        "sample_id",
        "source_id",
        "source_artifact_sha256",
        "source_figure_ref",
        "curve_role",
        "raw_pixel_x",
        "raw_pixel_y",
        "axis_calibration_ref",
        "extraction_tool",
        "extraction_tool_version",
        "extraction_pass_id",
        "operator_or_runner_id",
        "native_x_value",
        "native_x_unit",
        "native_y_value",
        "native_y_unit",
        "coordinate_uncertainty",
        "inclusion_status",
        "exclusion_reason",
    }

    assert len(passes) == 2
    assert {run["session_id"] for run in passes} == {
        "TASK-1052-20260715-A",
        "TASK-1052-20260715-B",
    }
    assert uncertainty_policy["adopted_x_coordinate_uncertainty_eV"] == 0.0045
    assert uncertainty_policy["adopted_y_coordinate_uncertainty_fraction"] == 0.0023
    for run in passes:
        anchors = run["axis_calibration"]["anchors"]
        points = run["points"]
        x_anchors = [anchor for anchor in anchors if anchor["axis"] == "x"]
        y_anchors = [anchor for anchor in anchors if anchor["axis"] == "y"]

        assert run["panel_raster_sha256"] == (
            "100e9f4cb1cd82aa18033523edd382e146115f6b60be4317e441ccd6b09567e7"
        )
        assert len(anchors) == 4
        assert len(x_anchors) == 2
        assert all(anchor["anchor_kind"] == "printed_tick_mark" for anchor in x_anchors)
        assert all(anchor["contract_valid"] is True for anchor in x_anchors)
        assert len(y_anchors) == 2
        assert all(anchor["printed_value"] is None for anchor in y_anchors)
        assert all(anchor["anchor_kind"] == "panel_frame_endpoint" for anchor in y_anchors)
        assert all(anchor["contract_valid"] is False for anchor in y_anchors)
        assert len(points) == 8
        assert {point["curve_role"] for point in points} == {"absorption", "emission"}
        assert all(required_point_fields <= point.keys() for point in points)
        assert all(point["extraction_tool"] == "WebPlotDigitizer" for point in points)
        assert all(point["extraction_tool_version"] == "4.8" for point in points)
        assert all(
            point["source_artifact_sha256"]
            == "2dab8a6b4db18af88f7175ac0773747fe1aeb15d88f951a4a8536cdc2dd73edb"
            for point in points
        )
        assert all(point["inclusion_status"] == "excluded" for point in points)
        assert all(point["exclusion_reason"] for point in points)
        assert all(
            point["coordinate_uncertainty"]["instrument_uncertainty"] == "not_reported"
            for point in points
        )
        assert all(
            point["coordinate_uncertainty"]["x_eV"]
            == uncertainty_policy["adopted_x_coordinate_uncertainty_eV"]
            for point in points
        )
        assert all(
            point["coordinate_uncertainty"]["y_axis_fraction"]
            == uncertainty_policy["adopted_y_coordinate_uncertainty_fraction"]
            for point in points
        )


def test_kim_repeatability_passes_but_full_contract_remains_blocked() -> None:
    ledger = _load_kim_ledger()
    runs = ledger["digitization"]["passes"]
    points_by_run = {
        run["extraction_pass_id"]: {
            (point["sample_id"], point["curve_role"]): point
            for point in run["points"]
        }
        for run in runs
    }
    agreement = ledger["agreement"]
    recomputed_x: list[float] = []
    recomputed_y: list[float] = []

    for pair in agreement["point_pairs"]:
        key = (pair["sample_id"], pair["curve_role"])
        point_a = points_by_run["kim-f3a-pass-a"][key]
        point_b = points_by_run["kim-f3a-pass-b"][key]
        x_difference = abs(point_a["native_x_value"] - point_b["native_x_value"])
        y_difference = abs(point_a["native_y_value"] - point_b["native_y_value"])
        x_fraction = x_difference / agreement["x_axis_span_eV"]

        assert pair["x_difference_eV"] == pytest.approx(x_difference)
        assert pair["x_difference_fraction"] == pytest.approx(x_fraction)
        assert pair["y_difference_fraction"] == pytest.approx(y_difference)
        assert pair["passes"] is True
        recomputed_x.append(x_fraction)
        recomputed_y.append(y_difference)

    assert agreement["max_x_difference_fraction"] == pytest.approx(max(recomputed_x))
    assert agreement["max_y_difference_fraction"] == pytest.approx(max(recomputed_y))
    assert agreement["max_x_difference_fraction"] < 0.005
    assert agreement["max_y_difference_fraction"] < 0.01
    assert agreement["pair_pass_fraction"] == 1.0
    assert agreement["repeatability_gate_pass"] is True
    assert agreement["full_contract_gate_pass"] is False
    assert ledger["verdict"] == "UNCERTAINTY_BLOCKED"


def test_kim_blocker_does_not_authorize_qd_rows_or_property_relabelling() -> None:
    ledger = _load_kim_ledger()
    optical = ledger["optical_observations"]

    assert ledger["qd_yaml_allowed"] is False
    assert ledger["baseline_metrics_allowed"] is False
    assert ledger["claim_promotion_allowed"] is False
    assert ledger["completeness"]["admitted_optical_row_count"] == 0
    assert ledger["completeness"]["excluded_optical_observation_count"] == 8
    assert all(row["inclusion_status"] == "excluded" for row in optical)
    assert all(
        row["coordinate_uncertainty"]["instrument_uncertainty"] == "not_reported"
        for row in optical
    )
    assert "bandgap_eV" not in {row["property_kind"] for row in optical}
    assert "bandgap_eV" in ledger["semantic_boundaries"]["excluded_from_this_ledger"]
    assert ledger["semantic_boundaries"]["equivalent_sphere_conversion"] == "forbidden"


def test_kim_value_bearing_paths_are_registered_for_redistribution() -> None:
    registry = yaml.safe_load((ROOT / "data/DATA_LICENSES.yaml").read_text(encoding="utf-8"))
    entry = next(
        item
        for item in registry["datasets"]
        if item["id"] == "kim-2020-cdse-optical-surface"
    )

    assert entry["license"] == "CC BY 4.0 (version of record)"
    assert entry["raw_artifact_vendored"] is False
    assert set(entry["paths"]) == {
        KIM_LEDGER_PATH,
        KIM_ABSORPTION_PATH,
        KIM_EMISSION_PATH,
        KIM_REVIEW_PATH,
    }
