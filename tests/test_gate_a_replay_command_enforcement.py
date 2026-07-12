"""Tests for Gate A enforcement of Gate B-replayable result commands."""

from __future__ import annotations

from pathlib import Path

from physics_lab.registry.agent_replay_validation import (
    GATE_A_REPLAY_COMMAND_GRANDFATHERED_RESULT_IDS,
    gate_a_replay_command_issues,
)


def _payload(result_id: str, command: str) -> dict[str, str]:
    return {"result_id": result_id, "command": command}


def _fixture_config(root: Path) -> None:
    config = root / "examples" / "fixture.yaml"
    config.parent.mkdir(parents=True)
    config.write_text("fixture: true\n", encoding="utf-8")


def test_gate_a_accepts_gate_b_replayable_command(tmp_path: Path) -> None:
    _fixture_config(tmp_path)

    issues = gate_a_replay_command_issues(
        _payload("RESULT-9999", "physics-lab run examples/fixture.yaml"),
        root=tmp_path,
    )

    assert issues == []


def test_gate_a_rejects_new_unsupported_command_with_bridge_guidance(tmp_path: Path) -> None:
    issues = gate_a_replay_command_issues(
        _payload("RESULT-9999", "python scripts/package_result.py"),
        root=tmp_path,
    )

    assert [issue.code for issue in issues] == ["gate-a-unreplayable-command"]
    assert "workflow bridge" in issues[0].message
    assert "RESULT-0028/TASK-1016" in issues[0].message


def test_gate_a_allows_only_frozen_legacy_unsupported_results(tmp_path: Path) -> None:
    assert GATE_A_REPLAY_COMMAND_GRANDFATHERED_RESULT_IDS == {
        "RESULT-0007",
        "RESULT-0012",
        "RESULT-0018",
        "RESULT-0025",
    }
    legacy_id = next(iter(GATE_A_REPLAY_COMMAND_GRANDFATHERED_RESULT_IDS))

    legacy_issues = gate_a_replay_command_issues(
        _payload(legacy_id, "python scripts/legacy_result.py"),
        root=tmp_path,
    )
    resolved_issues = gate_a_replay_command_issues(
        _payload("RESULT-0028", "python scripts/legacy_result.py"),
        root=tmp_path,
    )

    assert legacy_issues == []
    assert [issue.code for issue in resolved_issues] == ["gate-a-unreplayable-command"]
