"""Tests for Gate B agent replay validation."""

from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

from physics_lab.registry.agent_replay_validation import (
    ReplayIdentity,
    validate_agent_published_result,
)


def _identity() -> ReplayIdentity:
    return ReplayIdentity(
        contributor_id="roman",
        github_username="gladunrv",
        agent_tool="Codex",
        model_version="GPT-5 Codex",
    )


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _fixture_result(root: Path, *, review_tier: str = "AGENT_PUBLISHED") -> Path:
    config = root / "examples" / "fixture.yaml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("fixture: true\n", encoding="utf-8")
    digest = hashlib.sha256(config.read_bytes()).hexdigest()
    payload = {
        "result_id": "RESULT-9999",
        "run_id": "RUN-9999",
        "experiment_id": "EXP-9999",
        "title": "Fixture Result",
        "hypothesis_id": "HYP-9999",
        "task_id": "TASK-9999",
        "generated_at": "2026-01-01T00:00:00+00:00",
        "engine_version": "0.1-test",
        "git_commit": "deadbeef",
        "command": "physics-lab run examples/fixture.yaml",
        "input_file_hashes": {
            "config": {"path": "examples/fixture.yaml", "sha256": digest}
        },
        "code_reference": "physics_lab/workflows/fixture.py",
        "limitations": ["Fixture only."],
        "train_range": [0.0, 1.0],
        "test_range": [1.0, 2.0],
        "best_model_id": "model_fixture",
        "best_verdict": "VALID_IN_RANGE",
        "review_tier": review_tier,
        "agent_proposal_evaluation": {
            "review_tier_proposed": "AGENT_PUBLISHED",
            "best_verdict_proposed": "VALID_IN_RANGE",
            "published_by": {
                "contributor_id": "other",
                "github_username": "other-user",
                "agent_tool": "Claude Code",
                "model_version": "claude-opus-4-7",
            },
            "gates_checked": {
                "deterministic_run": True,
                "verification_block_populated": True,
                "input_hashes_recorded": True,
                "limitations_listed": True,
                "engine_version_and_commit_pinned": True,
                "schema_validation_passes": True,
                "no_protected_artifact_rewrite": True,
                "no_forbidden_overclaim_wording": True,
                "dataset_provenance_valid": True,
            },
            "evidence_summary": "Fixture evidence.",
        },
        "verification": {
            "passed": True,
            "checks": [
                {
                    "name": "deterministic_replay",
                    "status": "PASS",
                    "details": "Fixture replay.",
                    "metrics": {"mean_relative_error": 0.001},
                }
            ],
        },
        "scores": [
            {
                "model_id": "model_fixture",
                "formula": "fixture",
                "coefficients": {"a": 1.0},
                "complexity_score": 1,
                "train_metrics": {"mean_relative_error": 0.001},
                "test_metrics": {"mean_relative_error": 0.002},
                "composite_score": 0.003,
                "verdict": "VALID",
            }
        ],
    }
    result = root / "results" / "EXP-9999" / "RUN-9999" / "result.yaml"
    _write_yaml(result, payload)
    return result


def _copy_replay_result(source: Path, replay_root: Path, *, mutate: dict | None = None) -> None:
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    if mutate:
        for path, value in mutate.items():
            target = payload
            parts = path.split(".")
            for part in parts[:-1]:
                target = target[part]
            target[parts[-1]] = value
    replay_result = replay_root / "EXP-9999" / "RUN-9999" / "result.yaml"
    _write_yaml(replay_result, payload)


def test_gate_b_passes_and_emits_validation_record(tmp_path: Path) -> None:
    result = _fixture_result(tmp_path)
    replay_root = tmp_path / "replay"
    _copy_replay_result(result, replay_root)

    report = validate_agent_published_result(
        result,
        root=tmp_path,
        output_dir=replay_root,
        replayed_by=_identity(),
        dry_run=True,
    )

    assert report.ok, report.issues
    assert report.status == "PASS"
    assert report.validation_record is not None
    assert report.validation_record["review_tier_proposed"] == "AGENT_VALIDATED"
    assert report.validation_record["validation_record"]["replayed_by"] == _identity().as_dict()


def test_gate_b_finds_flat_layout_result(tmp_path: Path) -> None:
    # Some workflows (e.g. the dimensional analysis validator) write result.yaml
    # flat under --output-dir instead of nesting it as EXP-XXXX/RUN-XXXX/. Gate B
    # must still locate the replayed result in that flat layout.
    result = _fixture_result(tmp_path)
    replay_root = tmp_path / "replay"
    payload = yaml.safe_load(result.read_text(encoding="utf-8"))
    replay_root.mkdir(parents=True, exist_ok=True)
    _write_yaml(replay_root / "result.yaml", payload)

    report = validate_agent_published_result(
        result,
        root=tmp_path,
        output_dir=replay_root,
        replayed_by=_identity(),
        dry_run=True,
    )

    assert report.ok, report.issues
    assert report.status == "PASS"
    assert report.validation_record is not None
    assert report.validation_record["review_tier_proposed"] == "AGENT_VALIDATED"


def test_gate_b_blocks_wrong_review_tier(tmp_path: Path) -> None:
    result = _fixture_result(tmp_path, review_tier="MAINTAINER_REVIEWED")

    report = validate_agent_published_result(
        result,
        root=tmp_path,
        output_dir=tmp_path / "replay",
        replayed_by=_identity(),
        dry_run=True,
    )

    assert not report.ok
    assert report.status == "BLOCKED"
    assert {issue.code for issue in report.issues} >= {"review-tier"}


def test_gate_b_contests_metric_drift(tmp_path: Path) -> None:
    result = _fixture_result(tmp_path)
    replay_root = tmp_path / "replay"
    _copy_replay_result(
        result,
        replay_root,
        mutate={"verification.checks": [{"name": "deterministic_replay", "status": "PASS", "details": "Fixture replay.", "metrics": {"mean_relative_error": 0.5}}]},
    )

    report = validate_agent_published_result(
        result,
        root=tmp_path,
        output_dir=replay_root,
        replayed_by=_identity(),
        dry_run=True,
    )

    assert not report.ok
    assert report.status == "CONTESTED_RESULT"
    assert "metric-drift" in {issue.code for issue in report.issues}
    assert report.contested_report is not None


def test_gate_b_rejects_unsupported_command(tmp_path: Path) -> None:
    result = _fixture_result(tmp_path)
    payload = yaml.safe_load(result.read_text(encoding="utf-8"))
    payload["command"] = "bash scripts/run-anything.sh"
    _write_yaml(result, payload)

    report = validate_agent_published_result(
        result,
        root=tmp_path,
        output_dir=tmp_path / "replay",
        replayed_by=_identity(),
        dry_run=True,
    )

    assert not report.ok
    assert report.status == "BLOCKED"
    assert "unsupported-command" in {issue.code for issue in report.issues}


def test_gate_b_warns_when_original_publisher_is_unknown(tmp_path: Path) -> None:
    result = _fixture_result(tmp_path)
    payload = yaml.safe_load(result.read_text(encoding="utf-8"))
    del payload["agent_proposal_evaluation"]["published_by"]
    _write_yaml(result, payload)
    replay_root = tmp_path / "replay"
    _copy_replay_result(result, replay_root)

    report = validate_agent_published_result(
        result,
        root=tmp_path,
        output_dir=replay_root,
        replayed_by=_identity(),
        dry_run=True,
    )

    assert report.ok
    assert "original-publisher-unknown" in {issue.code for issue in report.issues}
