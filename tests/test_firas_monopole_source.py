from __future__ import annotations

from pathlib import Path

import yaml

from scripts.normalize_firas_monopole_source import (
    EXPECTED_ROW_COUNT,
    EXPECTED_SHA256,
    build_dataset,
    parse_rows,
    sha256_file,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = (
    ROOT
    / "data"
    / "textbook_formula_audit"
    / "wien_firas"
    / "source_artifacts"
    / "cobe-firas-monopole"
)
SOURCE = PACKAGE / "firas_monopole_spec_v1.txt"
ROWS = ROOT / "data" / "textbook_formula_audit" / "wien_firas" / "firas_monopole_rows.yaml"


def test_firas_source_checksum_and_row_count_are_pinned() -> None:
    assert sha256_file(SOURCE) == EXPECTED_SHA256
    assert len(parse_rows(SOURCE)) == EXPECTED_ROW_COUNT


def test_firas_rows_preserve_source_and_derived_classes() -> None:
    rows = parse_rows(SOURCE)

    assert rows[0]["spectral_axis_class"] == "source_reported_direct"
    assert rows[0]["monopole_intensity_class"] == "source_derived_absolute"
    assert rows[0]["residual_class"] == "source_reported_residual"
    assert rows[0]["uncertainty_class"] == "source_reported_1sigma"
    assert rows[0]["galaxy_model_class"] == "source_modeled"
    assert rows[0]["spectral_axis_cm_inverse"] == 2.27
    assert rows[-1]["spectral_axis_cm_inverse"] == 21.33


def test_committed_firas_rows_match_deterministic_normalization() -> None:
    committed = yaml.safe_load(ROWS.read_text(encoding="utf-8"))

    assert committed == build_dataset(SOURCE.relative_to(ROOT))
    assert committed["scope"]["metric_run_performed"] is False
    assert committed["scope"]["wien_peak_computed"] is False
    assert committed["counts"] == {
        "rows_total": EXPECTED_ROW_COUNT,
        "rows_admitted": EXPECTED_ROW_COUNT,
        "rows_excluded": 0,
    }
