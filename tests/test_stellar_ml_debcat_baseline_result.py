"""Tests for the Stellar M-L DEBCat benchmark workflow (RESULT-0022, Gate B replayable)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

from physics_lab.engines.stellar_ml_debcat_baseline_result import compute_result_metrics
from physics_lab.registry.agent_replay_validation import ReplayIdentity, validate_agent_published_result

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_PATH = ROOT / "examples" / "stellar_ml_debcat_baseline_benchmark.yaml"


def test_engine_reproduces_committed_frozen_metrics() -> None:
    a = compute_result_metrics()
    b = compute_result_metrics()
    assert a == b, "engine is not deterministic"
    assert a["alpha_3p5_holdout_mae"] == 0.184954
    assert a["alpha_4p0_holdout_mae"] == 0.137608
    assert a["fitted_alpha"] == 4.526004
    assert a["fitted_holdout_mae"] == 0.119925
    assert a["null_holdout_mae"] == 0.331817
    assert a["main_sequence_components"] == 223
    assert a["train_count"] == 102
    assert a["holdout_count"] == 65
    assert a["split_positive_seed_count"] == 5
    assert a["shuffle_real_exceeds_all"] is True
    assert a["by_stage_holdout_mae_dex"]["evolved"] == 1.708908
    assert a["scores"]["fitted"]["train_mean_relative_error"] == 0.24184


def test_cli_run_writes_gate_b_replayable_result(tmp_path: Path) -> None:
    subprocess.run(
        [sys.executable, "-m", "physics_lab.cli", "run", str(EXAMPLE_PATH), "--output-dir", str(tmp_path)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result_path = tmp_path / "EXP-0015" / "RUN-0001" / "result.yaml"
    payload = yaml.safe_load(result_path.read_text(encoding="utf-8"))
    assert payload["command"] == "physics-lab run examples/stellar_ml_debcat_baseline_benchmark.yaml"
    assert payload["review_tier"] == "AGENT_PUBLISHED"
    assert payload["best_verdict"] == "VALID_IN_RANGE"
    assert payload["best_model_id"] == "model_train_fitted_alpha"
    assert payload["agent_proposal_evaluation"]["published_by"]["agent_tool"] == "Claude Code"


def test_gate_b_passes_with_independent_agent(tmp_path: Path) -> None:
    committed = ROOT / "results" / "EXP-0015" / "RUN-0001" / "result.yaml"
    replay = validate_agent_published_result(
        committed,
        root=ROOT,
        replayed_by=ReplayIdentity(
            contributor_id="codex",
            github_username="gladunrv",
            agent_tool="Codex",
            model_version="gpt-5-codex",
        ),
        output_dir=tmp_path / "replay",
    )
    assert replay.ok, [issue.message for issue in replay.issues]
