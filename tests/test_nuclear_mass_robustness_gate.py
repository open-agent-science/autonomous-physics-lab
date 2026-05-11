from __future__ import annotations

from pathlib import Path

import yaml


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def test_nuclear_robustness_gate_defines_required_checks() -> None:
    gate = (_repo_root() / "docs" / "nuclear-mass-robustness-gate.md").read_text(
        encoding="utf-8"
    )

    for required in (
        "Primary holdout",
        "Split sensitivity",
        "Leakage review",
        "Complexity penalty",
        "Negative control",
        "Post-AME2020 Time-Split Rule",
        "ALLOW_BOUNDED_SANDBOX_FOLLOWUP",
        "ALLOW_ONLY_AS_NEGATIVE_CONTROL",
        "REQUIRES_TIME_SPLIT_REPLAY",
        "BLOCK_PROMOTION",
    ):
        assert required in gate


def test_second_nuclear_batch_remains_robustness_gated() -> None:
    task_path = _repo_root() / "tasks" / "TASK-0178-run-second-nuclear-mass-sandbox-batch.yaml"
    payload = yaml.safe_load(task_path.read_text(encoding="utf-8"))
    requirements = "\n".join(payload["requirements"])
    accepted_outputs = "\n".join(payload["accepted_outputs"])

    assert payload["status"] == "BLOCKED"
    assert "TASK-0190 is DONE" in requirements
    assert "robustness-gate section" in accepted_outputs
    assert "post-AME2020 status" in requirements


def test_current_mission_keeps_robustness_gate_visible() -> None:
    missions = yaml.safe_load((_repo_root() / "missions" / "current.yaml").read_text(encoding="utf-8"))
    nuclear = next(item for item in missions["missions"] if item["id"] == "nuclear-mass-surface")
    second_batch = next(
        action for action in nuclear["actions"] if action["id"] == "second-bounded-nuclear-batch"
    )

    assert "nuclear-robustness-gate-review" in second_batch["gated_by"]
    assert any("robustness gate" in item for item in nuclear["why_now"])
