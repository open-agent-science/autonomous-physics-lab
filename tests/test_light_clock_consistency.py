from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from physics_lab.engines.light_clock import (
    VALID_BETAS,
    evaluate_light_clock,
    lorentz_factor,
    run_light_clock_benchmark,
)

ROOT = Path(__file__).resolve().parents[1]


def test_lorentz_factor_rejects_out_of_domain_beta() -> None:
    assert lorentz_factor(0.0) == pytest.approx(1.0)
    assert lorentz_factor(0.5) == pytest.approx(1.1547005383792517)
    with pytest.raises(ValueError):
        lorentz_factor(1.0)


def test_reference_candidate_passes_all_declared_beta_cases() -> None:
    payload = run_light_clock_benchmark()
    assert payload["verdict"] == "CONSISTENT"
    assert [case["beta"] for case in payload["valid_beta_sweep"]] == list(VALID_BETAS)
    assert all(case["verdict"] == "CONSISTENT" for case in payload["valid_beta_sweep"])
    assert payload["low_velocity_check"]["status"] == "PASS"


@pytest.mark.parametrize("beta", [1.0, 1.01])
def test_superluminal_or_light_speed_input_is_undefined(beta: float) -> None:
    result = evaluate_light_clock(beta)
    assert result["verdict"] == "UNDEFINED"
    assert result["checks"] == []
    assert "gamma" not in result


def test_newtonian_candidate_is_rejected_by_lc001() -> None:
    result = evaluate_light_clock(0.5, candidate="newtonian")
    checks = {check["id"]: check for check in result["checks"]}
    assert result["verdict"] == "INCONSISTENT"
    assert checks["LC-001"]["status"] == "FAIL"


def test_benchmark_is_deterministic() -> None:
    assert run_light_clock_benchmark() == run_light_clock_benchmark()


def test_runner_writes_metrics_and_report(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_light_clock_consistency_benchmark.py",
            "--out-dir",
            str(tmp_path),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stderr
    metrics = json.loads((tmp_path / "metrics.json").read_text(encoding="utf-8"))
    report = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert metrics["verdict"] == "CONSISTENT"
    assert metrics["summary"]["newtonian_lc001_status"] == "FAIL"
    assert "Gate A: not attempted" in report
