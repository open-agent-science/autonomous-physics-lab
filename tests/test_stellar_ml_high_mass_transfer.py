"""Regression tests for TASK-0837 Stellar M-L high-mass transfer benchmark."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_stellar_ml_high_mass_transfer.py"

_SPEC = importlib.util.spec_from_file_location("run_stellar_ml_high_mass_transfer", SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)


def test_high_mass_transfer_metrics_are_frozen() -> None:
    metrics = _MODULE.build_metrics()

    assert metrics["frozen_relation"]["alpha_hat"] == 4.526004
    assert metrics["frozen_relation"]["no_refit_performed"] is True
    assert metrics["transfer_slice"]["row_count"] == 217
    assert metrics["transfer_slice"]["system_count"] == 121
    assert metrics["transfer_slice"]["lane_counts"] == {
        "train": 110,
        "validation": 51,
        "holdout": 56,
    }
    assert metrics["high_mass_holdout"]["frozen_relation"]["mae_dex"] == 0.409289
    assert metrics["controls"]["null_high_mass_train_massband_median"]["mae_dex"] == 0.457384
    assert metrics["controls"]["mass_matched_high_mass_train_nearest"]["mae_dex"] == 0.306352
    assert metrics["survival_margin"]["best_control_id"] == (
        "mass_matched_high_mass_train_nearest"
    )
    assert metrics["survival_margin"]["best_control_minus_relation_mae_dex"] == -0.102937
    assert metrics["survival_margin"]["clears_threshold"] is False
    assert metrics["verdict"] == "TRANSFER_NOT_SUPPORTED_BEST_CONTROL"
    assert metrics["output_routing"]["result_artifact_created"] is False


def test_cli_writes_replayable_sandbox_outputs(tmp_path: Path) -> None:
    out_dir = tmp_path / "run"
    review_note = tmp_path / "review.md"
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--output-dir",
            str(out_dir),
            "--review-note",
            str(review_note),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    metrics = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))
    assert metrics["agent_run_id"] == "AGENT-RUN-0085"
    assert metrics["task_id"] == "TASK-0837"
    assert "input_file_hashes" in metrics["replay"]
    assert (out_dir / "report.md").exists()
    assert review_note.read_text(encoding="utf-8").startswith(
        "# Stellar M-L High-Mass DEBCat Transfer Benchmark"
    )
