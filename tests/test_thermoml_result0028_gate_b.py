"""Regression tests for the Gate-B-safe RESULT-0028 workflow bridge."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "thermoml_esters_lactones_negative_result.yaml"
CANONICAL_RUN = ROOT / "results" / "EXP-0020" / "RUN-0002"


def test_gate_b_safe_workflow_reproduces_canonical_result_metrics(tmp_path: Path) -> None:
    output_dir = tmp_path / "result0028-replay"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "physics_lab.cli",
            "run",
            str(EXAMPLE),
            "--output-dir",
            str(output_dir),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    replay_run = output_dir / "EXP-0020" / "RUN-0002"
    expected_metrics = json.loads((CANONICAL_RUN / "metrics.json").read_text(encoding="utf-8"))
    observed_metrics = json.loads((replay_run / "metrics.json").read_text(encoding="utf-8"))
    assert observed_metrics == expected_metrics

    result = yaml.safe_load((replay_run / "result.yaml").read_text(encoding="utf-8"))
    assert result["result_id"] == "RESULT-0028"
    assert result["best_verdict"] == "INVALID"
    assert result["command"] == "physics-lab run examples/thermoml_esters_lactones_negative_result.yaml"
    assert result["code_reference"] == (
        "physics_lab/workflows/thermoml_esters_lactones_negative_result.py"
    )


def test_gate_b_safe_workflow_is_registered() -> None:
    from physics_lab.workflows.runner import WORKFLOW_DISPATCH

    assert "thermoml_esters_lactones_negative_result" in WORKFLOW_DISPATCH
