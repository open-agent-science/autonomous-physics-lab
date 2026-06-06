"""Tests for the sandbox-only Stefan-Boltzmann exact-reference fixture."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from physics_lab.engines.stefan_boltzmann import (
    STEFAN_BOLTZMANN_CONSTANT_W_M2_K4,
    audit_exact_reference_fixture,
    radiated_power_w,
    sphere_area_m2,
    spherical_luminosity_w,
)
from physics_lab.registry.agent_replay_validation import (
    ReplayIdentity,
    validate_agent_published_result,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = (
    ROOT
    / "data"
    / "textbook_formula_audit"
    / "textbook_stefan_boltzmann_exact_reference.yaml"
)
SCRIPT_PATH = ROOT / "scripts" / "run_textbook_stefan_boltzmann_exact_reference.py"
EXAMPLE_PATH = ROOT / "examples" / "textbook_stefan_boltzmann_exact_reference.yaml"


def _load_config() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def test_frozen_codata_2022_constant_is_pinned() -> None:
    config = _load_config()

    assert STEFAN_BOLTZMANN_CONSTANT_W_M2_K4 == 5.670374419e-8
    assert config["constant"]["value_w_m2_k4"] == STEFAN_BOLTZMANN_CONSTANT_W_M2_K4
    assert "CODATA 2022" in config["constant"]["source_convention"]


def test_si_area_and_temperature_scaling() -> None:
    area_m2 = 2.5
    temperature_k = 300.0

    assert sphere_area_m2(2.0) == 4.0 * sphere_area_m2(1.0)
    assert radiated_power_w(area_m2 * 3.0, temperature_k) == pytest.approx(
        3.0 * radiated_power_w(area_m2, temperature_k)
    )
    assert radiated_power_w(area_m2, temperature_k * 2.0) == pytest.approx(
        16.0 * radiated_power_w(area_m2, temperature_k)
    )
    assert spherical_luminosity_w(2.0, temperature_k) == pytest.approx(
        4.0 * spherical_luminosity_w(1.0, temperature_k)
    )


def test_exact_reference_fixture_passes_software_gates_and_rejects_controls() -> None:
    metrics = audit_exact_reference_fixture(_load_config())

    assert metrics["verdict"] == "VALID_IN_RANGE"
    assert metrics["scope"]["software_fixture_only"] is True
    assert metrics["scope"]["row_count"] == 16
    assert metrics["scope"]["reference_row_count"] == 8
    assert metrics["scope"]["holdout_row_count"] == 8
    assert all(gate["status"] == "PASS" for gate in metrics["gates"].values())
    assert metrics["gates"]["dimensional_consistency"]["computed_verdict"] == "VALID"
    assert metrics["gates"]["wrong_temperature_exponent_control"]["control_rejected"] is True
    assert metrics["gates"]["wrong_area_control"]["control_rejected"] is True
    # TASK-0634 changed the manifest route to scoped software-result packaging
    # for the EXP-0013 / HYP-0013 identity; the engine now echoes that boundary.
    assert metrics["promotion_boundary"]["sandbox_only"] is False
    assert metrics["promotion_boundary"]["writes_canonical_result"] is True
    assert metrics["promotion_boundary"]["claim_promotion_allowed"] is False
    assert metrics["promotion_boundary"]["empirical_audit_performed"] is False


def test_runner_writes_sandbox_metrics_and_report(tmp_path: Path) -> None:
    output_dir = tmp_path / "stefan-boltzmann"
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--config",
            str(CONFIG_PATH),
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    metrics = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))
    report = (output_dir / "report.md").read_text(encoding="utf-8")
    stdout_metrics = json.loads(completed.stdout)

    assert metrics == stdout_metrics
    assert metrics["verdict"] == "VALID_IN_RANGE"
    assert "synthetic software/gate fixture only" in report
    assert "no empirical audit" in report
    assert "scoped software-result packaging route" in report
    assert "Gate A: evaluated by the result-publication gate" in report


def test_cli_workflow_writes_gate_b_replayable_result(tmp_path: Path) -> None:
    output_dir = tmp_path / "canonical"
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

    result_path = output_dir / "EXP-0013" / "RUN-0001" / "result.yaml"
    result_payload = yaml.safe_load(result_path.read_text(encoding="utf-8"))

    assert result_payload["command"] == "physics-lab run examples/textbook_stefan_boltzmann_exact_reference.yaml"
    assert result_payload["review_tier"] == "AGENT_PUBLISHED"
    assert result_payload["agent_proposal_evaluation"]["published_by"]["agent_tool"] == "Claude Code"

    replay = validate_agent_published_result(
        ROOT / "results" / "EXP-0013" / "RUN-0001" / "result.yaml",
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
