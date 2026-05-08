"""Tests for the muon g-2 anomaly formula search engine and workflow."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from physics_lab.cli import app
from physics_lab.engines.g2_formula_search import (
    DELTA_AMU,
    SIGMA_COMBINED,
    run_formula_search,
    search_f3,
)


# ── Engine unit tests ─────────────────────────────────────────────────────

def test_run_formula_search_returns_expected_keys() -> None:
    result = run_formula_search()
    assert "families" in result
    assert "summary" in result
    assert "global_verdict" in result
    assert len(result["families"]) == 6


def test_summary_has_no_inf_values() -> None:
    """best_z_score must be None (not inf) when there are no hits."""
    result = run_formula_search()
    s = result["summary"]
    assert s["best_z_score"] is None or isinstance(s["best_z_score"], float)
    if s["best_z_score"] is not None:
        assert s["best_z_score"] != float("inf")
        assert s["best_z_score"] != float("-inf")


def test_summary_best_value_matches_formula() -> None:
    """best_value must be the actual formula value, not a signed approximation."""
    result = run_formula_search()
    s = result["summary"]
    if s["best_z_score"] is not None and s["best_value"] is not None:
        z_recomputed = abs(s["best_value"] - DELTA_AMU) / SIGMA_COMBINED
        assert abs(z_recomputed - s["best_z_score"]) < 1e-10


def test_global_verdict_is_valid_empirical() -> None:
    result = run_formula_search()
    assert result["global_verdict"] == "VALID_EMPIRICAL"


def test_f4_credible_hit_present() -> None:
    """α³(mμ/me)⁻²(mμ/mτ)⁻² must be within 1σ and pass the P<1% guardrail."""
    result = run_formula_search()
    f4 = next(fr for fr in result["families"] if fr["family_id"] == "F4")
    assert f4["random_baseline"]["guardrail_passed"], "F4 random baseline must pass P<1%"
    hit_formulas = [h["formula"] for h in f4["hits"]]
    assert any("mμ/me)^-2" in f and "mμ/mτ)^-2" in f for f in hit_formulas), (
        "Expected α³(mμ/me)⁻²(mμ/mτ)⁻² in F4 hits"
    )


def test_f3_rational_candidate_one_third() -> None:
    """(1/3)(α/π)³(mμ/mπ⁰)² should be within 1σ."""
    fr = search_f3()
    predicted = [h for h in fr.hits if not h.is_reference]
    one_third = next((h for h in predicted if "1/3" in h.formula_str), None)
    assert one_third is not None, "F3 c=1/3 must appear as a hit"
    assert one_third.z_score < 1.0


def test_f3_optimal_hit_marked_as_reference() -> None:
    """The optimal-fit hit must be marked is_reference=True."""
    fr = search_f3()
    ref_hits = [h for h in fr.hits if h.is_reference]
    assert len(ref_hits) == 1
    assert ref_hits[0].z_score == pytest.approx(0.0, abs=1e-12)


def test_f3_verdict_based_on_predicted_hits_only() -> None:
    """F3 verdict must reflect rational-candidate hits, not the always-present optimal fit."""
    fr = search_f3()
    predicted = [h for h in fr.hits if not h.is_reference]
    if predicted:
        assert fr.verdict == "HIT"
    else:
        assert fr.verdict == "NULL"


def test_null_verdict_path_no_json_crash(tmp_path: Path) -> None:
    """Simulate the NULL verdict path: best_z_score=None must not crash JSON serialization."""
    import json
    result = run_formula_search()
    # Patch summary to simulate no hits
    result["summary"]["best_z_score"] = None
    result["summary"]["best_formula"] = None
    result["summary"]["best_value"] = None
    # JSON serialization must succeed (no float("inf") or float("-inf"))
    serialized = json.dumps(result)
    assert '"best_z_score": null' in serialized


def test_all_family_ids_unique() -> None:
    result = run_formula_search()
    ids = [fr["family_id"] for fr in result["families"]]
    assert len(ids) == len(set(ids))


def test_n_hits_1sigma_excludes_reference() -> None:
    """n_hits_1sigma in each family must not count reference (fitted) hits."""
    result = run_formula_search()
    f3 = next(fr for fr in result["families"] if fr["family_id"] == "F3")
    predicted_hits = [h for h in f3["hits"] if not h["is_reference"]]
    assert f3["n_hits_1sigma"] == len(predicted_hits)


# ── CLI integration test ─────────────────────────────────────────────────────

def test_cli_run_g2_formula_search(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["run", "examples/g2_formula_search.yaml", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    run_dir = tmp_path / "EXP-0010" / "RUN-0001"
    assert (run_dir / "result.yaml").exists()
    assert (run_dir / "report.md").exists()
    assert (run_dir / "metrics.json").exists()
    assert (run_dir / "review_metadata.yaml").exists()


def test_cli_run_report_contains_experiment_id(tmp_path: Path) -> None:
    runner = CliRunner()
    runner.invoke(
        app,
        ["run", "examples/g2_formula_search.yaml", "--output-dir", str(tmp_path)],
    )
    report = (tmp_path / "EXP-0010" / "RUN-0001" / "report.md").read_text()
    assert "EXP-0010" in report
    assert "HYP-0010" in report
    assert "TASK-0089" in report
