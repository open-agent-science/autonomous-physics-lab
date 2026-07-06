"""Tests for the TASK-0911 DZ10 full-table parity gate.

The full 9311-row AMDC table is external and never vendored, so these tests
exercise the byte-independent check logic on the committed smoke fixture and
verify the gate's clean-skip and contested-identity behaviour without source
bytes. An optional integration test runs the real gate only when a local cache
is supplied through ``APL_DZ10_CACHE_DIR``.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from physics_lab.engines.nmd0003_canonical_dz10_reference import (
    DZ10_SMOKE_FIXTURE,
    format_dz10_fixture_text,
)
from physics_lab.engines.nmd0003_dz10_full_table_parity_gate import (
    EXPECTED_FULL_TABLE_ROW_COUNT,
    VERDICT_CONTESTED,
    VERDICT_PASS,
    VERDICT_SOURCE_BYTES_NOT_AVAILABLE,
    evaluate_parsed_table,
    run_full_table_parity_gate,
    verify_cache_identity,
)


def test_gate_skips_cleanly_without_source_bytes(tmp_path: Path) -> None:
    report = run_full_table_parity_gate(
        tmp_path / "du_zu_10.feb96",
        tmp_path / "du_zu_10.feb96fort",
    )
    assert report["verdict"] == VERDICT_SOURCE_BYTES_NOT_AVAILABLE
    assert report["source_identity"]["all_present"] is False
    assert "checks" not in report


def test_gate_contests_unpinned_bytes(tmp_path: Path) -> None:
    table = tmp_path / "du_zu_10.feb96"
    fortran = tmp_path / "du_zu_10.feb96fort"
    table.write_text(format_dz10_fixture_text(DZ10_SMOKE_FIXTURE), encoding="utf-8")
    fortran.write_text("C not the pinned fortran source\n", encoding="utf-8")
    report = run_full_table_parity_gate(table, fortran)
    assert report["verdict"] == VERDICT_CONTESTED
    assert report["source_identity"]["all_present"] is True
    assert report["source_identity"]["all_match"] is False
    assert "checks" not in report


def test_identity_records_expected_pins(tmp_path: Path) -> None:
    identity = verify_cache_identity(
        tmp_path / "du_zu_10.feb96",
        tmp_path / "du_zu_10.feb96fort",
    )
    table_entry = identity["files"]["table"]
    assert table_entry["expected_bytes"] == 196049
    assert table_entry["expected_sha256"].startswith("b80d64ca")
    fortran_entry = identity["files"]["fortran"]
    assert fortran_entry["expected_bytes"] == 12231
    assert fortran_entry["expected_sha256"].startswith("cccc8406")


def test_evaluate_parsed_table_passes_on_smoke_fixture() -> None:
    checks = evaluate_parsed_table(
        DZ10_SMOKE_FIXTURE,
        expected_row_count=len(DZ10_SMOKE_FIXTURE),
    )
    assert checks["passed"] is True
    assert checks["coverage"]["row_count_matches"] is True
    assert checks["printed_precision"]["passed"] is True
    assert checks["smoke_fixture"]["passed"] is True
    assert checks["lookup"]["passed"] is True


def test_evaluate_parsed_table_flags_row_count_mismatch() -> None:
    checks = evaluate_parsed_table(
        DZ10_SMOKE_FIXTURE,
        expected_row_count=EXPECTED_FULL_TABLE_ROW_COUNT,
    )
    assert checks["passed"] is False
    assert checks["coverage"]["row_count_matches"] is False


@pytest.mark.skipif(
    not os.environ.get("APL_DZ10_CACHE_DIR"),
    reason="APL_DZ10_CACHE_DIR not set; full-table gate needs local AMDC bytes.",
)
def test_full_gate_passes_on_pinned_local_cache() -> None:
    cache_dir = Path(os.environ["APL_DZ10_CACHE_DIR"])
    report = run_full_table_parity_gate(
        cache_dir / "du_zu_10.feb96",
        cache_dir / "du_zu_10.feb96fort",
    )
    assert report["verdict"] == VERDICT_PASS
    assert report["checks"]["coverage"]["row_count"] == EXPECTED_FULL_TABLE_ROW_COUNT
    diagnostic = report["published_variant_diagnostic"]
    assert diagnostic["verdict"] == "diagnostic_only_not_canonical_parity"
    assert diagnostic["comparison_count"] == EXPECTED_FULL_TABLE_ROW_COUNT
