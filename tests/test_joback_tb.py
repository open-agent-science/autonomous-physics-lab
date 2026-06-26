"""Tests for the frozen Joback Tb estimator and the bounded transfer runner.

The implementation-fidelity gate (the frozen 25-compound fixture reproducing
published predicted Tb with zero mismatches) is the load-bearing assertion: an
off-by-one group assignment must fail here before any benchmark is allowed to
read transfer error (TASK-0841).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from physics_lab.engines.joback_tb import (
    FIDELITY_TOLERANCE_K,
    JOBACK_BASE_JR1987,
    JOBACK_BASE_MOLECULARKNOWLEDGE,
    JOBACK_FIDELITY_FIXTURE,
    JOBACK_TB_GROUPS,
    GroupCoverageError,
    evaluate_fidelity_fixture,
    joback_group_sum,
    joback_tb,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_thermoml_tb_transfer.py"
SOURCE_MANIFEST = ROOT / "data" / "thermophysical" / "source_manifest.yaml"


def test_canonical_intercept_and_table_anchors() -> None:
    # Canonical Joback & Reid (1987) intercept and the acetone worked example.
    assert JOBACK_BASE_JR1987 == 198.2
    assert JOBACK_BASE_MOLECULARKNOWLEDGE == 198.12
    acetone = joback_tb({"-CH3": 2, ">C=O (non-ring)": 1}, base=JOBACK_BASE_JR1987)
    assert acetone == pytest.approx(322.11, abs=1e-9)
    # A couple of frozen table values used widely.
    assert JOBACK_TB_GROUPS["-CH3"] == 23.58
    assert JOBACK_TB_GROUPS["-COOH (acid)"] == 169.09
    assert JOBACK_TB_GROUPS["ring =CH-"] == 26.73


def test_group_sum_excludes_intercept() -> None:
    counts = {"-CH3": 2, ">C=O (non-ring)": 1}
    assert joback_group_sum(counts) == pytest.approx(2 * 23.58 + 76.75, abs=1e-9)
    assert joback_tb(counts, base=0.0) == pytest.approx(joback_group_sum(counts), abs=1e-9)


def test_out_of_coverage_group_raises() -> None:
    # An untabulated group means the molecule is out of Joback coverage.
    with pytest.raises(GroupCoverageError):
        joback_tb({"-CH3": 1, ">Si<": 1})
    with pytest.raises(ValueError):
        joback_tb({})
    with pytest.raises(ValueError):
        joback_tb({"-CH3": 0})


def test_fidelity_fixture_has_25_compounds_zero_mismatch() -> None:
    """THE GATE: frozen fixture reproduces published predicted Tb, 0 mismatches."""
    report = evaluate_fidelity_fixture()
    assert report.compound_count == 25
    assert report.mismatch_count == 0
    assert report.passed is True
    assert report.max_abs_error_k <= FIDELITY_TOLERANCE_K
    # Every row matches within tolerance against its own source intercept.
    for row in report.rows:
        assert row.match is True, f"{row.name} mismatched: {row.abs_error_k} K"


def test_each_fixture_compound_reproduces_its_published_value() -> None:
    for compound in JOBACK_FIDELITY_FIXTURE:
        assert compound.matches(), (
            f"{compound.name}: computed {compound.computed_tb_k():.4f} K vs "
            f"published {compound.published_tb_k} K (err {compound.abs_error_k():.4f} K)"
        )


def test_ethyl_thioacetate_decomposition_regression() -> None:
    # Retained regression: the correct grouping (with -CH2-) matches; a missing
    # -CH2- once manufactured a ~23 K outlier in the TASK-0833 scout.
    correct = joback_tb(
        {"-CH3": 2, "-CH2-": 1, ">C=O (non-ring)": 1, "-S- (non-ring)": 1},
        base=JOBACK_BASE_MOLECULARKNOWLEDGE,
    )
    assert correct == pytest.approx(413.69, abs=0.05)
    missing_ch2 = joback_tb(
        {"-CH3": 2, ">C=O (non-ring)": 1, "-S- (non-ring)": 1},
        base=JOBACK_BASE_MOLECULARKNOWLEDGE,
    )
    assert abs(missing_ch2 - 413.69) > 20.0  # the artifact the fixture catches


def test_source_manifest_is_metadata_only_with_pinned_sha() -> None:
    import yaml

    manifest = yaml.safe_load(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["no_values_recorded_here"] is True
    assert manifest["no_corpus_committed"] is True
    assert manifest["live_external_fetch_allowed"] is False
    source = manifest["sources"][0]
    assert source["doi"] == "10.18434/mds2-2422"
    assert source["official_published_sha256"] == (
        "231161b5e443dc1ae0e5da8429d86a88474cb722016e5b790817bb31c58d7ec2"
    )
    assert source["apl_computed_sha256"] == "PENDING_FIRST_FETCH"
    rights = source["rights_framework"]
    assert rights["local_analysis_allowed"] is True
    assert rights["source_bytes_redistribution"] is False
    assert rights["covered_by_repo_license"] is False
    # Tb only; Tc must not appear as an in-scope property.
    assert source["properties"] == ["normal_boiling_point_Tb"]


def test_runner_writes_inconclusive_bounded_outcome(tmp_path: Path) -> None:
    output_dir = tmp_path / "thermoml-tb"
    completed = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--output-dir", str(output_dir)],
        check=True,
        capture_output=True,
        text=True,
    )
    metrics = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))
    report = (output_dir / "report.md").read_text(encoding="utf-8")
    stdout_metrics = json.loads(completed.stdout)

    assert metrics == stdout_metrics
    # Default (no fetch) -> bounded IMPLEMENTATION_INCONCLUSIVE, fidelity clean.
    assert metrics["verdict"] == "IMPLEMENTATION_INCONCLUSIVE"
    assert metrics["fetch_executed"] == "no"
    assert metrics["fidelity_gate"]["passed"] is True
    assert metrics["fidelity_gate"]["mismatch_count"] == 0
    assert metrics["fidelity_gate"]["compound_count"] == 25
    assert metrics["transfer"]["executed"] is False
    assert metrics["property_in_scope"] == "normal_boiling_point_Tb_only"
    # Gate-B replay metadata present.
    replay = metrics["replay"]
    assert replay["engine_version"] == "0.1.0"
    assert replay["git_commit"]
    assert "physics_lab/engines/joback_tb.py" in replay["input_file_hashes"]
    assert replay["input_file_hashes"]["physics_lab/engines/joback_tb.py"].startswith(
        "sha256:"
    )
    # Rights determination recorded; no claim impact.
    assert metrics["rights_determination"]["source_bytes_redistribution"] == "no"
    assert metrics["output_routing"]["claim_impact"] == "none"
    assert "IMPLEMENTATION_INCONCLUSIVE" in report
    assert "fetch executed: " not in report.lower() or "Fetch executed" in report
