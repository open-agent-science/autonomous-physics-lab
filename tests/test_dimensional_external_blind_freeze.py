from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks" / "TASK-1071-freeze-external-blind-dimensional-validator-benchmark.yaml"
INTERFACE_PATH = ROOT / "docs" / "dimensional-validator-external-curator-interface.md"
BLOCKER_RECORD_PATH = ROOT / "docs" / "reviews" / "dimensional" / "task1071-external-exposure-blocker.md"


def _task() -> dict:
    return yaml.safe_load(TASK_PATH.read_text(encoding="utf-8"))


def test_external_curator_input_surface_is_answer_free() -> None:
    task = _task()
    assert task["input"]["related_objects"] == [
        "docs/dimensional-validator-external-curator-interface.md"
    ]

    related = "\n".join(task["input"]["related_objects"])
    forbidden = (
        "results/",
        "knowledge/challenge_sets/",
        "physics_lab/engines/",
        "docs/notes/dimensional-analysis-challenge-set.md",
        "TASK-1038",
        "TASK-1039",
    )
    assert all(token not in related for token in forbidden)


def test_external_freeze_validation_is_metadata_only() -> None:
    commands = "\n".join(_task()["validation"]["commands"])
    assert "tests/test_dimensional_external_blind_freeze.py" in commands
    assert "tests/test_docs_links.py" in commands
    assert "tests/test_dimensions.py" not in commands
    assert "tests/test_dimensional_validator_v2_freeze.py" not in commands


def test_curator_interface_contains_no_answer_bearing_paths() -> None:
    text = INTERFACE_PATH.read_text(encoding="utf-8")
    forbidden = (
        "results/EXP-",
        "knowledge/challenge_sets/",
        "physics_lab/engines/dimensions.py",
        "dimensional_analysis_challenge_set_v2.yaml",
    )
    assert all(token not in text for token in forbidden)
    assert "During curation, the curator may read only this document and `TASK-1071`." in text


def test_external_exposure_blocker_is_metadata_only() -> None:
    text = BLOCKER_RECORD_PATH.read_text(encoding="utf-8")
    assert "**`EXTERNAL_EXPOSURE_BLOCKED`**" in text
    assert "No formulas, variable-dimension declarations, native labels" in text
    assert "Codex Desktop` / `GPT-5" in text
    assert "TASK-1071-EXPOSURE-ATTESTATION-20260719-AKUTENYOV-CODEX-GPT5" in text
    assert "docs/campaigns/dimensional-analysis-validator.md" in text
    assert "value-free result-performance discussion" in text
    forbidden = (
        "knowledge/challenge_sets/",
        "physics_lab/engines/",
        "results/EXP-",
    )
    assert all(token not in text for token in forbidden)
