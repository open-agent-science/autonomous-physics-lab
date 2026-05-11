from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import yaml

from physics_lab.engines.nuclear_mass_baselines import SemiEmpiricalCoefficients, evaluate_baseline
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset
from physics_lab.registry.agent_runs import load_agent_run


HOLDOUTS = {
    "random_stratified": ("He-4", "Fe-57", "Pb-208"),
    "oxygen_chain": ("O-16", "O-17"),
    "magic_heavy_region": ("Sn-120", "Pb-208"),
    "neutron_rich_edge": ("Sn-120", "Pb-208", "U-238"),
}


def _build_feature_columns(rows: list) -> dict[str, np.ndarray]:
    a = np.asarray([row.A for row in rows], dtype=float)
    n = np.asarray([row.N for row in rows], dtype=float)
    z = np.asarray([row.Z for row in rows], dtype=float)
    return {
        "magic_both": np.asarray(
            [1.0 if row.is_magic_z and row.is_magic_n else 0.0 for row in rows],
            dtype=float,
        ),
        "heavy_double_magic": np.asarray(
            [1.0 if row.is_magic_z and row.is_magic_n and row.A >= 100 else 0.0 for row in rows],
            dtype=float,
        ),
        "odd_a": np.asarray(
            [1.0 if row.pairing_class == "odd_a" else 0.0 for row in rows],
            dtype=float,
        ),
        "isospin_asymmetry": (n - z) / a,
        "isospin_asymmetry_sq": ((n - z) / a) ** 2,
    }


def _classify_candidate(*, improved: int, regressed: int, worst_regression: float) -> str:
    if improved >= 4 and worst_regression <= 0.0:
        return "VALID_IN_RANGE"
    if improved >= 2 and regressed <= 1 and worst_regression <= 0.25:
        return "PARTIALLY_VALID"
    if regressed >= 2 or worst_regression >= 1.0:
        return "OVERFITTED"
    return "INCONCLUSIVE"


def test_nuclear_mass_autonomous_pilot_metrics_recompute() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    metrics_path = repo_root / "agent_runs" / "AGENT-RUN-0005" / "metrics.json"
    agent_run_path = repo_root / "agent_runs" / "AGENT-RUN-0005" / "agent_run.yaml"
    result_path = repo_root / "results" / "EXP-0012" / "RUN-0001" / "result.yaml"
    dataset_path = repo_root / "data" / "nuclear_masses" / "nmd-0002-curated-measured-slice.yaml"

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    agent_run = load_agent_run(agent_run_path, root=repo_root)
    result_payload = yaml.safe_load(result_path.read_text(encoding="utf-8"))
    dataset = load_nuclear_mass_dataset(dataset_path)

    fitted_model = next(
        score for score in result_payload["scores"] if score["model_id"] == "model_fitted_semi_empirical"
    )
    coefficients = SemiEmpiricalCoefficients(**fitted_model["coefficients"])
    rows = evaluate_baseline(entries=dataset.entries, model_id="model_fitted_semi_empirical", coefficients=coefficients)
    residuals = np.asarray([row.residual_mev for row in rows], dtype=float)
    nuclides = [row.nuclide_id for row in rows]
    feature_columns = _build_feature_columns(rows)

    families = {
        "shell_dual_heavy_anchor": ("magic_both", "heavy_double_magic"),
        "shell_dual_heavy_anchor_odd_a": ("magic_both", "heavy_double_magic", "odd_a"),
        "quadratic_asymmetry_refinement": ("isospin_asymmetry", "isospin_asymmetry_sq"),
    }

    assert agent_run["campaign_profile_id"] == "nuclear-mass-surface"
    assert metrics["summary"]["generated_proposal_count"] == 8
    assert metrics["summary"]["executed_candidate_count"] == 3
    assert metrics["summary"]["rejected_before_execution_count"] == 5
    assert len(metrics["executed_items"]) == 3
    assert metrics["reference_comparison"]["canonical_result"] == "RESULT-0015"

    for item in metrics["executed_items"]:
        columns = families[item["family"]]
        x = np.column_stack([feature_columns[column] for column in columns])
        improved = 0
        regressed = 0
        deltas: list[float] = []

        for holdout in item["holdout_results"]:
            holdout_id = holdout["holdout_id"]
            holdout_set = set(HOLDOUTS[holdout_id])
            mask = np.asarray([nuclide in holdout_set for nuclide in nuclides], dtype=bool)
            beta, *_ = np.linalg.lstsq(x[~mask], residuals[~mask], rcond=None)
            correction = x[mask] @ beta
            baseline_residuals = residuals[mask]
            candidate_residuals = baseline_residuals - correction

            expected_coefficients = {name: float(value) for name, value in zip(columns, beta)}
            for key, value in expected_coefficients.items():
                assert abs(holdout["coefficients"][key] - value) <= 1.0e-12

            baseline_mae = float(np.mean(np.abs(baseline_residuals)))
            baseline_rmse = float(np.sqrt(np.mean(baseline_residuals**2)))
            candidate_mae = float(np.mean(np.abs(candidate_residuals)))
            candidate_rmse = float(np.sqrt(np.mean(candidate_residuals**2)))
            delta_mae = candidate_mae - baseline_mae
            delta_rmse = candidate_rmse - baseline_rmse

            assert abs(holdout["baseline_metrics"]["mae_mev"] - baseline_mae) <= 1.0e-12
            assert abs(holdout["baseline_metrics"]["rmse_mev"] - baseline_rmse) <= 1.0e-12
            assert abs(holdout["candidate_metrics"]["mae_mev"] - candidate_mae) <= 1.0e-12
            assert abs(holdout["candidate_metrics"]["rmse_mev"] - candidate_rmse) <= 1.0e-12
            assert abs(holdout["delta_mae_mev"] - delta_mae) <= 1.0e-12
            assert abs(holdout["delta_rmse_mev"] - delta_rmse) <= 1.0e-12

            deltas.append(delta_mae)
            if delta_mae < -1.0e-12:
                improved += 1
            elif delta_mae > 1.0e-12:
                regressed += 1

        unchanged = len(deltas) - improved - regressed
        worst_regression = max(0.0, max(deltas))
        expected_verdict = _classify_candidate(
            improved=improved,
            regressed=regressed,
            worst_regression=worst_regression,
        )

        assert item["summary"]["improved_holdout_count"] == improved
        assert item["summary"]["regressed_holdout_count"] == regressed
        assert item["summary"]["unchanged_holdout_count"] == unchanged
        assert abs(item["summary"]["mean_delta_mae_mev"] - float(np.mean(deltas))) <= 1.0e-12
        assert abs(item["summary"]["worst_regression_mev"] - worst_regression) <= 1.0e-12
        assert item["expected_verdict"] == expected_verdict
        assert item["observed_verdict"] == expected_verdict
        assert item["agrees"] is True
