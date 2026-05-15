"""Tests for nuclear_prediction_variant_review ranking helper."""

from __future__ import annotations

from physics_lab.engines.nuclear_prediction_variant_review import (
    EXTREME_SENSITIVITY_THRESHOLD_MEV,
    NEAR_DUPLICATE_THRESHOLD_MEV,
    SlateRankingReport,
    rank_slate,
)


def _minimal_candidate(
    variant_id: str = "v1",
    prediction_id: str = "PRED-0001",
    target_batch: str = "batch-a",
    model_id: str = "MODEL::variant",
    deltas: list[float] | None = None,
    review_notes: list[str] | None = None,
) -> dict:
    if deltas is None:
        deltas = [0.5, -0.3]
    nuclides = [
        {
            "nuclide_id": f"X-{i}",
            "Z": i + 1,
            "N": i + 1,
            "A": 2 * (i + 1),
            "pairing_class": "even_even",
            "predicted_value_mev": -10.0 + d,
            "baseline_value_mev": -10.0,
            "delta_from_baseline_mev": d,
            "uncertainty_mev": None,
            "confidence_note": "test",
        }
        for i, d in enumerate(deltas)
    ]
    return {
        "variant_id": variant_id,
        "prediction_id": prediction_id,
        "target_batch": target_batch,
        "model_id": model_id,
        "title": f"Draft variant {variant_id}",
        "model_control_label": "test control",
        "coefficients": {},
        "coefficient_delta_from_base": {},
        "transform": {},
        "target_nuclides": nuclides,
        "review_notes": review_notes if review_notes is not None else ["A note."],
        "limitations": [],
    }


def _minimal_summary(candidates: list[dict]) -> dict:
    return {
        "factory_id": "test-factory",
        "task_id": "TASK-0253",
        "campaign_profile_id": "nuclear-mass-surface",
        "quantity": "mass_excess_mev",
        "unit": "MeV",
        "live_external_fetch_allowed": False,
        "candidate_count": len(candidates),
        "candidates": candidates,
    }


# --- basic contract ---

def test_rank_slate_returns_report() -> None:
    summary = _minimal_summary([_minimal_candidate()])
    report = rank_slate(summary)
    assert isinstance(report, SlateRankingReport)
    assert report.candidate_count == 1
    assert report.factory_id == "test-factory"
    assert report.task_id == "TASK-0253"


def test_candidate_count_matches() -> None:
    candidates = [_minimal_candidate(f"v{i}", f"PRED-{i:04d}") for i in range(5)]
    report = rank_slate(_minimal_summary(candidates))
    assert report.candidate_count == 5


# --- duplicate prediction id detection ---

def test_no_duplicates_clean_slate() -> None:
    candidates = [
        _minimal_candidate("v1", "PRED-0001"),
        _minimal_candidate("v2", "PRED-0002"),
    ]
    report = rank_slate(_minimal_summary(candidates))
    assert report.duplicate_prediction_ids == []


def test_duplicate_prediction_id_detected() -> None:
    candidates = [
        _minimal_candidate("v1", "PRED-0001"),
        _minimal_candidate("v2", "PRED-0001"),
    ]
    report = rank_slate(_minimal_summary(candidates))
    assert "PRED-0001" in report.duplicate_prediction_ids


def test_duplicate_prediction_id_raises_flag() -> None:
    candidates = [
        _minimal_candidate("v1", "PRED-0001"),
        _minimal_candidate("v2", "PRED-0001"),
    ]
    report = rank_slate(_minimal_summary(candidates))
    codes = [f.code for f in report.flags]
    assert "DUPLICATE_PREDICTION_ID" in codes


# --- near-duplicate value vector detection ---

def test_near_duplicate_vectors_detected() -> None:
    deltas = [0.5, -0.3]
    candidates = [
        _minimal_candidate("v1", "PRED-0001", deltas=deltas),
        _minimal_candidate("v2", "PRED-0002", deltas=deltas),
    ]
    report = rank_slate(_minimal_summary(candidates))
    assert len(report.near_duplicate_pairs) == 1
    assert ("v1", "v2") in report.near_duplicate_pairs


def test_distinct_vectors_not_flagged_as_near_duplicate() -> None:
    candidates = [
        _minimal_candidate("v1", "PRED-0001", deltas=[0.5, -0.3]),
        _minimal_candidate("v2", "PRED-0002", deltas=[5.0, 3.0]),
    ]
    report = rank_slate(_minimal_summary(candidates))
    assert report.near_duplicate_pairs == []


def test_near_duplicate_below_threshold_not_flagged() -> None:
    delta = NEAR_DUPLICATE_THRESHOLD_MEV * 2
    candidates = [
        _minimal_candidate("v1", "PRED-0001", deltas=[0.5, 0.3]),
        _minimal_candidate("v2", "PRED-0002", deltas=[0.5 + delta, 0.3 + delta]),
    ]
    report = rank_slate(_minimal_summary(candidates))
    assert report.near_duplicate_pairs == []


# --- delta sensitivity table ---

def test_delta_table_sorted_descending() -> None:
    candidates = [
        _minimal_candidate("v-small", "PRED-0001", deltas=[0.1, 0.2]),
        _minimal_candidate("v-large", "PRED-0002", deltas=[8.0, 9.0]),
    ]
    report = rank_slate(_minimal_summary(candidates))
    assert report.delta_table[0]["variant_id"] == "v-large"
    assert report.delta_table[1]["variant_id"] == "v-small"


def test_delta_table_ranking_stability() -> None:
    candidates = [_minimal_candidate(f"v{i}", f"PRED-{i:04d}", deltas=[float(i)]) for i in range(10)]
    report1 = rank_slate(_minimal_summary(candidates))
    report2 = rank_slate(_minimal_summary(candidates))
    assert [r["variant_id"] for r in report1.delta_table] == [r["variant_id"] for r in report2.delta_table]


# --- heuristic flags ---

def test_extreme_sensitivity_flagged() -> None:
    large_delta = EXTREME_SENSITIVITY_THRESHOLD_MEV + 1.0
    candidates = [_minimal_candidate("v1", "PRED-0001", deltas=[large_delta])]
    report = rank_slate(_minimal_summary(candidates))
    codes = [f.code for f in report.flags]
    assert "EXTREME_SENSITIVITY" in codes


def test_normal_delta_not_flagged_extreme() -> None:
    candidates = [_minimal_candidate("v1", "PRED-0001", deltas=[0.5])]
    report = rank_slate(_minimal_summary(candidates))
    codes = [f.code for f in report.flags]
    assert "EXTREME_SENSITIVITY" not in codes


def test_all_zero_delta_flagged() -> None:
    candidates = [_minimal_candidate("v1", "PRED-0001", deltas=[0.0, 0.0])]
    report = rank_slate(_minimal_summary(candidates))
    codes = [f.code for f in report.flags]
    assert "ALL_ZERO_DELTA" in codes


def test_nonzero_delta_not_flagged_all_zero() -> None:
    candidates = [_minimal_candidate("v1", "PRED-0001", deltas=[0.0, 0.5])]
    report = rank_slate(_minimal_summary(candidates))
    codes = [f.code for f in report.flags]
    assert "ALL_ZERO_DELTA" not in codes


def test_missing_review_notes_flagged() -> None:
    candidates = [_minimal_candidate("v1", "PRED-0001", review_notes=[])]
    report = rank_slate(_minimal_summary(candidates))
    codes = [f.code for f in report.flags]
    assert "MISSING_REVIEW_NOTES" in codes


def test_present_review_notes_not_flagged() -> None:
    candidates = [_minimal_candidate("v1", "PRED-0001", review_notes=["Some note."])]
    report = rank_slate(_minimal_summary(candidates))
    codes = [f.code for f in report.flags]
    assert "MISSING_REVIEW_NOTES" not in codes


# --- no-claim wording in markdown ---

def test_markdown_no_claim_wording() -> None:
    candidates = [_minimal_candidate()]
    report = rank_slate(_minimal_summary(candidates))
    md = report.to_markdown()
    assert "does not assign" in md or "no scientific claim" in md.lower() or "No scientific claim" in md


def test_markdown_no_success_score_words() -> None:
    candidates = [_minimal_candidate()]
    report = rank_slate(_minimal_summary(candidates))
    md = report.to_markdown()
    lower = md.lower()
    assert "discovery" not in lower
    assert "breakthrough" not in lower
    assert "confirmed" not in lower


def test_markdown_contains_factory_id() -> None:
    candidates = [_minimal_candidate()]
    report = rank_slate(_minimal_summary(candidates))
    md = report.to_markdown()
    assert "test-factory" in md


def test_markdown_contains_delta_table() -> None:
    candidates = [_minimal_candidate()]
    report = rank_slate(_minimal_summary(candidates))
    md = report.to_markdown()
    assert "Delta Sensitivity Table" in md
    assert "variant_id" in md


# --- target-batch and model-family coverage ---

def test_target_batch_coverage_reported() -> None:
    candidates = [
        _minimal_candidate("v1", "PRED-0001", target_batch="batch-a"),
        _minimal_candidate("v2", "PRED-0002", target_batch="batch-b"),
    ]
    report = rank_slate(_minimal_summary(candidates))
    assert set(report.target_batches_covered) == {"batch-a", "batch-b"}
    assert report.candidates_per_batch == {"batch-a": 1, "batch-b": 1}


def test_model_family_prefix_extracted() -> None:
    candidates = [
        _minimal_candidate("v1", "PRED-0001", model_id="RESULT-0015::variant_a"),
        _minimal_candidate("v2", "PRED-0002", model_id="RESULT-0015::variant_b"),
    ]
    report = rank_slate(_minimal_summary(candidates))
    assert report.model_family_prefixes == ["RESULT-0015"]


def test_empty_slate() -> None:
    report = rank_slate(_minimal_summary([]))
    assert report.candidate_count == 0
    assert report.flags == []
    md = report.to_markdown()
    assert "Candidates:** 0" in md
