"""Tests for the MD-0002 formation-energy benchmark workflow (RESULT-0021, Gate B replayable)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

from physics_lab.engines.materials_md0002_formation_energy_result import compute_result_metrics
from physics_lab.registry.agent_replay_validation import ReplayIdentity, validate_agent_published_result

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_PATH = ROOT / "examples" / "materials_md0002_formation_energy_benchmark.yaml"


def test_engine_reproduces_committed_frozen_metrics() -> None:
    a = compute_result_metrics()
    b = compute_result_metrics()
    assert a == b, "engine is not deterministic"
    assert a["cation_pair_holdout_mae"] == 0.200606
    assert a["null_holdout_mae"] == 0.506092
    assert a["improvement_abs"] == 0.305485
    assert a["train_count"] == 253
    assert a["holdout_count"] == 54
    assert a["cation_pair_wins"] == 5
    assert a["cation_pair_holdout_mae_min"] == 0.172441
    assert a["cation_pair_holdout_mae_max"] == 0.216158
    assert a["label_shuffle_control_mae_min"] == 0.530919
    assert a["cation_label_shuffle_control_mae_min"] == 0.474316
    assert a["scores"]["cation_pair"]["test_mean_relative_error"] == 0.107392


def test_cli_run_writes_gate_b_replayable_result(tmp_path: Path) -> None:
    subprocess.run(
        [sys.executable, "-m", "physics_lab.cli", "run", str(EXAMPLE_PATH), "--output-dir", str(tmp_path)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result_path = tmp_path / "EXP-0014" / "RUN-0001" / "result.yaml"
    payload = yaml.safe_load(result_path.read_text(encoding="utf-8"))
    assert payload["command"] == "physics-lab run examples/materials_md0002_formation_energy_benchmark.yaml"
    assert payload["review_tier"] == "AGENT_PUBLISHED"
    assert payload["best_verdict"] == "VALID_IN_RANGE"
    assert payload["agent_proposal_evaluation"]["published_by"]["agent_tool"] == "Claude Code"


def test_gate_b_passes_with_independent_agent(tmp_path: Path) -> None:
    committed = ROOT / "results" / "EXP-0014" / "RUN-0001" / "result.yaml"
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
