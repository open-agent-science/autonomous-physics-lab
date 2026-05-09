from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from physics_lab.registry.microtask_runs import load_microtask_run
from physics_lab.registry.repository import validate_repository
from physics_lab.registry.validation import infer_kind_from_path


def _write_queue(root: Path) -> None:
    queue_path = root / "tasks" / "microtasks" / "pendulum-formula-falsification.yaml"
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(
        textwrap.dedent(
            """\
            queue_id: pendulum-formula-falsification
            campaign: pendulum-formula-falsification
            campaign_status: active
            selection_guidance:
              - "Prefer narrow attempts."
            microtasks:
              - id: PFF-001
                campaign: pendulum-formula-falsification
                title: Propose one candidate family
                type: formula-family-proposal
                estimated_effort: 15-30 minutes
                recommended_for:
                  - codex
                autonomy_level:
                  - agent_can_complete
                  - human_review_required
                expected_output: "One note."
                validation:
                  - "State limits."
                risk_level: low
                forbidden_claims:
                  - "discovery-level result"
            """
        ),
        encoding="utf-8",
    )


def _write_microtask_run(root: Path, *, microtask_id: str = "PFF-001") -> Path:
    _write_queue(root)
    note_path = root / "docs" / "notes" / "pff-001-attempt.md"
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text("sandbox note\n", encoding="utf-8")

    run_path = root / "microtask_runs" / "pendulum-formula-falsification" / "MICROTASK-RUN-0001.yaml"
    run_path.parent.mkdir(parents=True, exist_ok=True)
    run_path.write_text(
        textwrap.dedent(
            f"""\
            id: MICROTASK-RUN-0001
            queue_id: pendulum-formula-falsification
            microtask_id: {microtask_id}
            status: COMPLETED
            claimant:
              contributor_id: roman
              agent_id: codex
            branch: agent/roman/codex/microtask-PFF-001-candidate-family
            pull_request: "https://github.com/gladunrv/autonomous-physics-lab/pull/999"
            result_note: docs/notes/pff-001-attempt.md
            verdict: REVIEW_NEEDED
            review_state: REVIEW_READY
            metadata:
              inputs:
                - tasks/microtasks/pendulum-formula-falsification.yaml
              method: "Drafted one bounded candidate-family note."
              code_references:
                - docs/scientific-micro-task-protocol.md
              metrics:
                - qualitative_review_only
              failure_mode: "Reject if the family is not even in theta."
              limitations:
                - "No canonical result artifact was produced."
              novelty_check:
                checked_paths:
                  - microtask_runs/
                  - docs/notes/
                summary: "No duplicate run found."
            """
        ),
        encoding="utf-8",
    )
    return run_path


def test_microtask_run_validates_and_counts(tmp_path: Path) -> None:
    run_path = _write_microtask_run(tmp_path)

    payload = load_microtask_run(run_path, root=tmp_path)
    summary = validate_repository(tmp_path)

    assert payload["id"] == "MICROTASK-RUN-0001"
    assert summary.counts["microtask_runs"] == 1


def test_microtask_run_rejects_unknown_microtask_id(tmp_path: Path) -> None:
    run_path = _write_microtask_run(tmp_path, microtask_id="PFF-999")

    with pytest.raises(ValueError, match="unknown microtask id"):
        load_microtask_run(run_path, root=tmp_path)


def test_microtask_run_rejects_absolute_result_note(tmp_path: Path) -> None:
    run_path = _write_microtask_run(tmp_path)
    text = run_path.read_text(encoding="utf-8")
    run_path.write_text(text.replace("docs/notes/pff-001-attempt.md", str(tmp_path / "note.md")), encoding="utf-8")

    with pytest.raises(ValueError, match="repository-relative paths"):
        load_microtask_run(run_path, root=tmp_path)


def test_microtask_run_rejects_wrong_queue_folder(tmp_path: Path) -> None:
    run_path = _write_microtask_run(tmp_path)
    wrong_path = tmp_path / "microtask_runs" / "other-queue" / run_path.name
    wrong_path.parent.mkdir(parents=True, exist_ok=True)
    run_path.replace(wrong_path)

    with pytest.raises(ValueError, match="microtask_runs/pendulum-formula-falsification/"):
        load_microtask_run(wrong_path, root=tmp_path)


def test_repository_rejects_duplicate_active_microtask_runs(tmp_path: Path) -> None:
    first_path = _write_microtask_run(tmp_path)
    first_text = first_path.read_text(encoding="utf-8").replace("status: COMPLETED", "status: CLAIMED")
    first_path.write_text(first_text, encoding="utf-8")
    second_path = first_path.with_name("MICROTASK-RUN-0002.yaml")
    second_path.write_text(
        first_text.replace("MICROTASK-RUN-0001", "MICROTASK-RUN-0002"),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate active microtask run"):
        validate_repository(tmp_path)


def test_repository_rejects_duplicate_completed_microtask_runs(tmp_path: Path) -> None:
    first_path = _write_microtask_run(tmp_path)
    first_text = first_path.read_text(encoding="utf-8")
    first_path.write_text(first_text, encoding="utf-8")
    second_path = first_path.with_name("MICROTASK-RUN-0002.yaml")
    second_path.write_text(
        first_text.replace("MICROTASK-RUN-0001", "MICROTASK-RUN-0002"),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate completed microtask run"):
        validate_repository(tmp_path)


def test_infer_kind_from_microtask_run_path() -> None:
    assert infer_kind_from_path("microtask_runs/pendulum/MICROTASK-RUN-0001.yaml") == "microtask_run"
