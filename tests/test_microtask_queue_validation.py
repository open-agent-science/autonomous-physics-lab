from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from physics_lab.registry.repository import validate_repository


def _write_queue(
    root: Path,
    *,
    filename: str = "pendulum-formula-falsification.yaml",
    queue_id: str = "pendulum-formula-falsification",
    duplicate_id: bool = False,
) -> Path:
    path = root / "tasks" / "microtasks" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    second_id = "PFF-001" if duplicate_id else "PFF-002"
    path.write_text(
        textwrap.dedent(
            f"""\
            queue_id: {queue_id}
            campaign: pendulum-formula-falsification
            campaign_status: active
            selection_guidance:
              - "Prefer narrow attempts."
            microtasks:
              - id: PFF-001
                campaign: pendulum-formula-falsification
                title: First microtask
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
              - id: {second_id}
                campaign: pendulum-formula-falsification
                title: Second microtask
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
    return path


def test_validate_repository_accepts_consistent_microtask_queue(tmp_path: Path) -> None:
    _write_queue(tmp_path)

    summary = validate_repository(tmp_path)

    assert summary.root == tmp_path.resolve()


def test_validate_repository_rejects_microtask_queue_id_filename_mismatch(
    tmp_path: Path,
) -> None:
    _write_queue(tmp_path, queue_id="wrong-queue")

    with pytest.raises(ValueError, match="declares queue_id wrong-queue"):
        validate_repository(tmp_path)


def test_validate_repository_rejects_duplicate_microtask_ids(tmp_path: Path) -> None:
    _write_queue(tmp_path, duplicate_id=True)

    with pytest.raises(ValueError, match="duplicate microtask id PFF-001"):
        validate_repository(tmp_path)
