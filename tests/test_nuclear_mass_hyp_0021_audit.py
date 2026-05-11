from __future__ import annotations

from itertools import product
from pathlib import Path
import json
import statistics

import numpy as np
import yaml

from physics_lab.engines.nuclear_mass_baselines import SemiEmpiricalCoefficients, evaluate_baseline
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset


LIGHT_NUCLIDES = ("He-4", "N-14", "O-16", "O-17")
MEDIUM_NUCLIDES = ("Ca-40", "Ca-48", "Fe-56", "Fe-57")
HEAVY_NUCLIDES = ("Sn-120", "Pb-208", "U-238")
PILOT_RANDOM_SPLIT = ("He-4", "Fe-57", "Pb-208")


def _load_residual_surface() -> tuple[list[str], np.ndarray, np.ndarray, np.ndarray]:
    repo_root = Path(__file__).resolve().parent.parent
    result_path = repo_root / "results" / "EXP-0012" / "RUN-0001" / "result.yaml"
    dataset_path = repo_root / "data" / "nuclear_masses" / "nmd-0002-curated-measured-slice.yaml"

    result_payload = yaml.safe_load(result_path.read_text(encoding="utf-8"))
    fitted_model = next(
        score for score in result_payload["scores"] if score["model_id"] == "model_fitted_semi_empirical"
    )
    coefficients = SemiEmpiricalCoefficients(**fitted_model["coefficients"])
    dataset = load_nuclear_mass_dataset(dataset_path)
    rows = evaluate_baseline(entries=dataset.entries, model_id="model_fitted_semi_empirical", coefficients=coefficients)

    nuclides = [row.nuclide_id for row in rows]
    residuals = np.asarray([row.residual_mev for row in rows], dtype=float)
    x20 = np.column_stack(
        [
            np.asarray([1.0 if row.is_magic_z and row.is_magic_n else 0.0 for row in rows], dtype=float),
            np.asarray(
                [1.0 if row.is_magic_z and row.is_magic_n and row.A >= 100 else 0.0 for row in rows],
                dtype=float,
            ),
        ]
    )
    x21 = np.column_stack(
        [
            x20[:, 0],
            x20[:, 1],
            np.asarray([1.0 if row.pairing_class == "odd_a" else 0.0 for row in rows], dtype=float),
        ]
    )
    return nuclides, residuals, x20, x21


def _delta_mae_for_holdout(
    *,
    holdout: tuple[str, ...],
    nuclides: list[str],
    residuals: np.ndarray,
    design_matrix: np.ndarray,
) -> float:
    holdout_set = set(holdout)
    mask = np.asarray([nuclide in holdout_set for nuclide in nuclides], dtype=bool)
    beta, *_ = np.linalg.lstsq(design_matrix[~mask], residuals[~mask], rcond=None)
    corrected = residuals[mask] - (design_matrix[mask] @ beta)
    return float(np.mean(np.abs(corrected)) - np.mean(np.abs(residuals[mask])))


def test_hyp_0021_replay_matches_stored_metrics() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    metrics_path = repo_root / "agent_runs" / "AGENT-RUN-0005" / "metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

    nuclides, residuals, _, x21 = _load_residual_surface()
    proposal = next(item for item in metrics["executed_items"] if item["proposal_id"] == "HYP-PROPOSAL-0021")

    for holdout_result in proposal["holdout_results"]:
        holdout = tuple(metrics["holdout_definition"][holdout_result["holdout_id"]])
        replayed_delta = _delta_mae_for_holdout(
            holdout=holdout,
            nuclides=nuclides,
            residuals=residuals,
            design_matrix=x21,
        )
        assert abs(replayed_delta - holdout_result["delta_mae_mev"]) <= 1.0e-12

    summary = proposal["summary"]
    assert proposal["observed_verdict"] == "VALID_IN_RANGE"
    assert summary["improved_holdout_count"] == 4
    assert summary["regressed_holdout_count"] == 0
    assert abs(summary["mean_delta_mae_mev"] - (-0.33501713070505423)) <= 1.0e-12
    assert abs(summary["worst_regression_mev"] - 0.0) <= 1.0e-12


def test_hyp_0021_stratified_random_split_sensitivity_is_visible() -> None:
    nuclides, residuals, x20, x21 = _load_residual_surface()

    results: list[tuple[tuple[str, ...], float, float, float]] = []
    for holdout in product(LIGHT_NUCLIDES, MEDIUM_NUCLIDES, HEAVY_NUCLIDES):
        delta20 = _delta_mae_for_holdout(
            holdout=holdout,
            nuclides=nuclides,
            residuals=residuals,
            design_matrix=x20,
        )
        delta21 = _delta_mae_for_holdout(
            holdout=holdout,
            nuclides=nuclides,
            residuals=residuals,
            design_matrix=x21,
        )
        results.append((holdout, delta20, delta21, delta21 - delta20))

    deltas21 = [delta21 for _, _, delta21, _ in results]
    pilot_rank = [index + 1 for index, item in enumerate(sorted(results, key=lambda item: item[2])) if item[0] == PILOT_RANDOM_SPLIT][0]

    assert len(results) == 48
    assert sum(1 for _, _, delta21, _ in results if delta21 < -1.0e-12) == 28
    assert sum(1 for _, _, delta21, _ in results if delta21 > 1.0e-12) == 13
    assert sum(1 for _, _, delta21, _ in results if abs(delta21) <= 1.0e-12) == 7
    assert abs(statistics.median(deltas21) - (-0.135265169994792)) <= 1.0e-12
    assert abs(min(deltas21) - (-0.7440386250631548)) <= 1.0e-12
    assert abs(max(deltas21) - 0.9480738911860487) <= 1.0e-12
    assert pilot_rank == 18

    better_than_hyp20 = [item for item in results if item[3] < -1.0e-12]
    worse_than_hyp20 = [item for item in results if item[3] > 1.0e-12]

    assert len(better_than_hyp20) == 18
    assert len(worse_than_hyp20) == 0
    assert all(("O-17" in holdout or "Fe-57" in holdout) for holdout, _, _, _ in better_than_hyp20)


def test_task_0183_agent_run_metrics_match_split_replay() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    metrics_path = repo_root / "agent_runs" / "AGENT-RUN-0006" / "metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

    nuclides, residuals, x20, x21 = _load_residual_surface()
    selected_splits = {
        item["split_id"]: tuple(item["holdout"])
        for item in metrics["selected_split_results"]
    }

    assert metrics["sandbox_only"] is True
    assert metrics["canonical_results_changed"] is False
    assert metrics["canonical_claims_changed"] is False
    assert selected_splits["pilot_random_stratified"] == PILOT_RANDOM_SPLIT
    assert len(selected_splits) >= 4

    for split_result in metrics["selected_split_results"]:
        replayed_delta = _delta_mae_for_holdout(
            holdout=tuple(split_result["holdout"]),
            nuclides=nuclides,
            residuals=residuals,
            design_matrix=x21,
        )
        assert abs(replayed_delta - split_result["delta_mae_mev"]) <= 1.0e-12

    results: list[tuple[tuple[str, ...], float, float, float]] = []
    for holdout in product(LIGHT_NUCLIDES, MEDIUM_NUCLIDES, HEAVY_NUCLIDES):
        delta20 = _delta_mae_for_holdout(
            holdout=holdout,
            nuclides=nuclides,
            residuals=residuals,
            design_matrix=x20,
        )
        delta21 = _delta_mae_for_holdout(
            holdout=holdout,
            nuclides=nuclides,
            residuals=residuals,
            design_matrix=x21,
        )
        results.append((holdout, delta20, delta21, delta21 - delta20))

    summary = metrics["same_shape_stratified_summary"]
    deltas21 = [delta21 for _, _, delta21, _ in results]
    pilot_rank = [
        index + 1
        for index, item in enumerate(sorted(results, key=lambda item: item[2]))
        if item[0] == PILOT_RANDOM_SPLIT
    ][0]

    assert summary["split_count"] == len(results) == 48
    assert summary["improved_count"] == sum(1 for value in deltas21 if value < -1.0e-12)
    assert summary["regressed_count"] == sum(1 for value in deltas21 if value > 1.0e-12)
    assert summary["tied_count"] == sum(1 for value in deltas21 if abs(value) <= 1.0e-12)
    assert abs(summary["median_delta_mae_mev"] - statistics.median(deltas21)) <= 1.0e-12
    assert abs(summary["best_delta_mae_mev"] - min(deltas21)) <= 1.0e-12
    assert abs(summary["worst_delta_mae_mev"] - max(deltas21)) <= 1.0e-12
    assert summary["pilot_rank_by_delta_mae"] == pilot_rank
