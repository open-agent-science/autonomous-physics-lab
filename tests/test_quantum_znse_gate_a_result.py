"""Tests for the TASK-0957 ZnSe no-refit transfer Gate A RESULT workflow."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

from physics_lab.registry.agent_replay_validation import (
    ReplayIdentity,
    validate_agent_published_result,
)
from physics_lab.registry.result_publication_gate import check_artifact

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_PATH = ROOT / "examples" / "quantum_znse_contract_transfer_result.yaml"
COMMITTED_RESULT = ROOT / "results" / "EXP-0022" / "RUN-0001" / "result.yaml"


def _run_cli(output_dir: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "physics_lab.cli",
            "run",
            str(EXAMPLE_PATH),
            "--output-dir",
            str(output_dir),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def test_cli_run_writes_gate_a_result(tmp_path: Path) -> None:
    _run_cli(tmp_path)

    result_path = tmp_path / "EXP-0022" / "RUN-0001" / "result.yaml"
    payload = yaml.safe_load(result_path.read_text(encoding="utf-8"))

    assert payload["result_id"] == "RESULT-0029"
    assert payload["experiment_id"] == "EXP-0022"
    assert payload["hypothesis_id"] == "HYP-0022"
    assert payload["task_id"] == "TASK-0957"
    assert payload["command"] == (
        "python -m physics_lab.cli run "
        "examples/quantum_znse_contract_transfer_result.yaml"
    )
    assert payload["review_tier"] == "AGENT_PUBLISHED"
    assert payload["best_verdict"] == "INCONCLUSIVE"
    assert payload["best_model_id"] == "model_inp_no_refit_confinement_power_law"
    assert payload["agent_proposal_evaluation"]["published_by"]["agent_tool"] == "Codex"

    checks = {check["name"]: check for check in payload["verification"]["checks"]}
    assert checks["agent_run_0090_metric_reproduction"]["metrics"][
        "primary_transfer_mae_ev"
    ] == 0.09921632
    assert checks["frozen_margin_outcome"]["metrics"]["margin_shortfall_ev"] == 0.00341632


def test_cli_result_is_byte_stable_in_same_output_dir(tmp_path: Path) -> None:
    _run_cli(tmp_path)
    result_path = tmp_path / "EXP-0022" / "RUN-0001" / "result.yaml"
    first = result_path.read_bytes()

    _run_cli(tmp_path)
    second = result_path.read_bytes()

    assert first == second


def test_committed_result_passes_gate_a() -> None:
    report = check_artifact(COMMITTED_RESULT, root=ROOT)
    assert report.ok, [issue.message for issue in report.issues]


def test_gate_b_replay_helper_accepts_committed_result(tmp_path: Path) -> None:
    replay = validate_agent_published_result(
        COMMITTED_RESULT,
        root=ROOT,
        replayed_by=ReplayIdentity(
            contributor_id="independent-reviewer",
            github_username="independent-reviewer",
            agent_tool="Claude Code",
            model_version="Claude Opus 4.8",
        ),
        output_dir=tmp_path / "replay",
    )

    assert replay.ok, [issue.message for issue in replay.issues]
    assert replay.status == "PASS"
    assert max((delta.abs_delta for delta in replay.metric_deltas), default=0.0) == 0.0
