"""Guards for the TASK-0995 FRB reveal-source admissibility contract."""

from __future__ import annotations

from pathlib import Path

import yaml

from physics_lab.registry.task_discovery import find_task_file

ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "docs" / "reviews" / "frb-reveal-source-admissibility-contract.md"


def _note_text() -> str:
    return NOTE.read_text(encoding="utf-8")


def test_frb_reveal_contract_records_single_ready_verdict_and_no_label_boundary() -> None:
    text = _note_text()
    assert text.count("REVEAL_CONTRACT_READY") == 1
    assert "REVEAL_CONTRACT_NEEDS_DECISION" not in text
    assert "REVEAL_CONTRACT_BLOCKED" not in text
    assert "does not fetch a later catalog" in text
    assert "read repeat status" in text
    assert "score frozen ranks" in text
    assert "register a `PRED-*` entry" in text
    assert "target count: `479`" in text
    assert "score_pre_t = log1p(E_upper_hours + E_lower_hours)" in text


def test_frb_reveal_contract_declares_manifest_fields_and_source_classes() -> None:
    text = _note_text()
    for section in (
        "## Admissible Reveal-Source Classes",
        "## Inadmissible Reveal-Source Classes",
        "## Required Future Manifest Fields",
        "## Source-ID Matching Policy",
        "## Row-Loss, Duplicate, And Ambiguity Handling",
        "## Frozen Comparison Outputs And Comparators",
        "## Stop Conditions",
    ):
        assert section in text

    required_fields = [
        "source title, version, issuing body, publication/release date, and citation",
        "source locator, access timestamp, byte size, SHA-256, and archive route",
        "parser/normalizer command, code reference, and normalized artifact checksum",
        "repeat-label field names and repeat-evidence timestamp field names",
        "no-peek attestation naming who froze the manifest before label inspection",
    ]
    for field in required_fields:
        assert field in text


def test_frb_reveal_contract_label_enum_and_matching_policy_are_explicit() -> None:
    text = _note_text()
    for label in (
        "POSITIVE_POST_T_REPEAT",
        "NO_POST_T_REPEAT_EVIDENCE_AS_OF_SOURCE",
        "UNREVEALED_MISSING",
        "AMBIGUOUS_STOP",
        "PRE_T_REPEAT_EXCLUDED",
    ):
        assert label in text

    assert "Exact source id match after whitespace trimming only." in text
    assert "Case-normalized exact match" in text
    assert "Maintainer-approved alias-table match" in text
    assert "using `repeater_name` as a pre-T feature" in text
    assert "dropping a target silently" in text


def test_frb_reveal_contract_freezes_comparators_without_refit() -> None:
    text = _note_text()
    for score in (
        "log1p(E_upper_hours + E_lower_hours)",
        "log1p(E_upper_hours)",
        "log1p(E_lower_hours)",
        "`0.0`",
    ):
        assert score in text
    assert "No feature may be refit, retuned, or added after labels are visible." in text
    assert "rank AUC" in text
    assert "average precision" in text
    assert "top-k positive counts for `k in {10, 25, 50}`" in text


def test_task_0995_is_reviewed_or_closed_out() -> None:
    task_path = find_task_file(ROOT, "TASK-0995")
    assert task_path is not None
    assert task_path.exists()
    with task_path.open("r", encoding="utf-8") as handle:
        task = yaml.safe_load(handle)
    assert task["status"] in {"REVIEW_READY", "DONE"}
    assert task["closeout"] == "review"
