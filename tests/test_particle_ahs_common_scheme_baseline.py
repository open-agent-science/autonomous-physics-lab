from __future__ import annotations

import json
import math
from pathlib import Path

import yaml

from physics_lab.engines.particle_common_scheme_baseline import run_from_config
from physics_lab.registry.agent_runs import load_agent_run
from scripts.run_particle_ahs_common_scheme_baseline import write_outputs


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "examples" / "benchmarks" / "particle_ahs_common_scheme_baseline.yaml"
COMMITTED_RUN = ROOT / "agent_runs" / "AGENT-RUN-0091"


def test_metric_contract_and_common_scheme_source_are_frozen() -> None:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert config["metric_contract"] == {
        "frozen_before_scoring": True,
        "procedural_not_blind": True,
        "metric_id": "geometric_midpoint_log10_residual_dex",
        "baseline": "middle_yukawa_predicted_as_sqrt_light_times_heavy",
        "signed_residual": "log10(observed_middle_yukawa / predicted_middle_yukawa)",
        "aggregate_metrics": [
            "mean_absolute_residual_dex",
            "root_mean_square_residual_dex",
            "maximum_absolute_residual_dex",
        ],
        "success_threshold": None,
        "verdict_rule": "INCONCLUSIVE_DIAGNOSTIC_WITHOUT_PREDECLARED_QUALITY_THRESHOLD",
    }
    assert config["sectors"] == [
        {"id": "up_type", "ordered_parameters": ["y_u", "y_c", "y_t"]},
        {"id": "down_type", "ordered_parameters": ["y_d", "y_s", "y_b"]},
    ]


def test_engine_recomputes_predeclared_residuals() -> None:
    metrics = run_from_config(CONFIG, root=ROOT)
    assert metrics["source"]["sha256"] == (
        "b96709627e13542c6c047ca565713028321bba98fcb070d1a016ab774e29b480"
    )
    assert metrics["source"]["entry_count"] == 6
    assert metrics["verdict"] == "INCONCLUSIVE"
    assert len(metrics["sectors"]) == 2
    for sector in metrics["sectors"]:
        expected = math.log10(
            sector["observed_middle_yukawa"]
            / math.sqrt(sector["light_yukawa"] * sector["heavy_yukawa"])
        )
        assert sector["signed_residual_dex"] == expected


def test_runner_is_byte_stable_and_manifest_valid(tmp_path: Path) -> None:
    metrics = run_from_config(CONFIG, root=ROOT)
    first = tmp_path / "first" / "AGENT-RUN-0091"
    second = tmp_path / "second" / "AGENT-RUN-0091"
    write_outputs(metrics, first)
    write_outputs(metrics, second)
    first_files = {path.name: path.read_bytes() for path in first.iterdir()}
    second_files = {path.name: path.read_bytes() for path in second.iterdir()}
    assert first_files == second_files


def test_committed_agent_run_matches_fresh_engine_output() -> None:
    committed = json.loads((COMMITTED_RUN / "metrics.json").read_text(encoding="utf-8"))
    assert committed == run_from_config(CONFIG, root=ROOT)
    manifest = load_agent_run(COMMITTED_RUN / "agent_run.yaml", root=ROOT)
    assert manifest["verdict"] == "INCONCLUSIVE"
    assert manifest["promotion_boundary"]["writes_canonical_result"] is False
