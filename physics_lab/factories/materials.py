"""Materials formation-energy campaign adapter for the Research Factory core.

Second real campaign adapter after ``physics_lab/factories/nuclear.py``: it
proves the campaign-agnostic core (``physics_lab/factories/core.py``,
TASK-0506) generalizes to a genuinely different campaign - residual-offset
correction of MD-0001 computed formation energies - by producing bounded
``Candidate`` objects the shared ``run_factory`` assembles into a schema-valid
``factory_summary``.

The science (frozen cation-group baseline, per-label residual-offset lanes,
matched null controls, seeded split-sensitivity) is the same bounded pipeline
the TASK-0626 smoke sprint exercises; here it is expressed through the shared
``CampaignAdapter`` interface so no campaign-specific logic lives in the core.
Diagnostic-only: no claim, prediction, knowledge, or result promotion.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import random
from typing import Any, Callable

from physics_lab.engines.materials_md0001_baseline import (
    MaterialsRow,
    _fit_baselines,
    _included_rows,
    _load_axis_rows,
    _residual_metrics,
    _split_rows,
    cation_group,
    formula_family,
)
from physics_lab.factories.core import (
    Candidate,
    FactoryRun,
    FactorySpec,
    register_adapter,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

SURVIVAL_MARGIN_EV_PER_ATOM = 0.05
COMPLEXITY_PENALTY_EV_PER_PARAMETER = 0.01
RANDOM_SEED = 626
FORMATION_ENERGY_PROPERTY = "formation_energy_per_atom"

Labeler = Callable[[list[MaterialsRow]], dict[str, str]]

# The frozen candidate and control label lanes (identical to the TASK-0626
# smoke sprint), keyed by the ids the FactorySpec references in families/controls.
CANDIDATE_LABELERS: dict[str, Labeler] = {}
CONTROL_LABELERS: dict[str, Labeler] = {}


# --- Label lanes -----------------------------------------------------------


def _cation_group_labels(rows: list[MaterialsRow]) -> dict[str, str]:
    return {row.row_id: cation_group(row) for row in rows}


def _formula_family_labels(rows: list[MaterialsRow]) -> dict[str, str]:
    return {row.row_id: formula_family(row) for row in rows}


def _oxygen_stoichiometry_labels(rows: list[MaterialsRow]) -> dict[str, str]:
    labels: dict[str, str] = {}
    for row in rows:
        oxygen = row.composition.get("O", 0.0)
        cation_total = sum(
            amount for element, amount in row.composition.items() if element != "O"
        )
        ratio = oxygen / cation_total if cation_total else 0.0
        if ratio < 1.25:
            label = "oxygen_low"
        elif ratio < 1.75:
            label = "oxygen_mid"
        else:
            label = "oxygen_high"
        labels[row.row_id] = label
    return labels


def _formula_family_x_cation_group_labels(rows: list[MaterialsRow]) -> dict[str, str]:
    return {row.row_id: f"{formula_family(row)}__{cation_group(row)}" for row in rows}


def _label_shuffle_labels(rows: list[MaterialsRow]) -> dict[str, str]:
    base = list(_formula_family_x_cation_group_labels(rows).values())
    random.Random(RANDOM_SEED).shuffle(base)
    return {row.row_id: label for row, label in zip(rows, base, strict=True)}


def _cation_group_shuffle_labels(rows: list[MaterialsRow]) -> dict[str, str]:
    groups = [cation_group(row) for row in rows]
    random.Random(RANDOM_SEED + 1).shuffle(groups)
    return {row.row_id: group for row, group in zip(rows, groups, strict=True)}


def _matched_random_formula_family_labels(rows: list[MaterialsRow]) -> dict[str, str]:
    labels = list(_formula_family_labels(rows).values())
    random.Random(RANDOM_SEED + 2).shuffle(labels)
    return {row.row_id: label for row, label in zip(rows, labels, strict=True)}


CANDIDATE_LABELERS.update(
    {
        "cation_group_residual_offsets": _cation_group_labels,
        "formula_family_residual_offsets": _formula_family_labels,
        "oxygen_stoichiometry_residual_offsets": _oxygen_stoichiometry_labels,
        "formula_family_x_cation_group_offsets": _formula_family_x_cation_group_labels,
    }
)
CONTROL_LABELERS.update(
    {
        "label_shuffle_control": _label_shuffle_labels,
        "cation_group_shuffle_control": _cation_group_shuffle_labels,
        "matched_random_formula_family_control": _matched_random_formula_family_labels,
    }
)
REQUIRED_CONTROL_IDS = tuple(CONTROL_LABELERS)


def _validate_spec_contract(spec: FactorySpec) -> None:
    """Reject configs that could bypass the adapter's bounded control contract."""
    if spec.candidate_cap < 1:
        raise ValueError("Materials factory candidate_cap must be at least 1")

    unknown_families = sorted(set(spec.families) - set(CANDIDATE_LABELERS))
    if unknown_families:
        raise ValueError(
            "Unsupported materials factory families: " + ", ".join(unknown_families)
        )

    unknown_controls = sorted(set(spec.controls) - set(CONTROL_LABELERS))
    if unknown_controls:
        raise ValueError(
            "Unsupported materials factory controls: " + ", ".join(unknown_controls)
        )

    missing_controls = [
        control_id for control_id in REQUIRED_CONTROL_IDS if control_id not in spec.controls
    ]
    if missing_controls:
        raise ValueError(
            "Missing required materials factory controls: " + ", ".join(missing_controls)
        )


# --- Lane scoring (frozen baseline + per-label residual offsets) ------------


def _fit_residual_offsets(
    train_rows: list[MaterialsRow],
    labels: dict[str, str],
    baseline_predictor: Callable[[MaterialsRow], float],
) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in train_rows:
        grouped[labels[row.row_id]].append(row.value - baseline_predictor(row))
    return {label: sum(values) / len(values) for label, values in grouped.items()}


def _lane_verdict(improvement: dict[str, float], complexity_penalty: float) -> str:
    if improvement["validation"] < 0.0 or improvement["holdout"] < 0.0:
        return "negative"
    if improvement["holdout"] - complexity_penalty >= SURVIVAL_MARGIN_EV_PER_ATOM:
        return "replay_needed"
    if improvement["holdout"] > 0.0:
        return "diagnostic_only"
    return "negative"


def score_offset_lane(
    rows: list[MaterialsRow],
    splits: dict[str, list[MaterialsRow]],
    baseline_predictor: Callable[[MaterialsRow], float],
    labeler: Labeler,
) -> dict[str, Any]:
    """Score one residual-offset lane; identical maths to the TASK-0626 sprint."""
    labels = labeler(rows)
    train_rows = splits["train"]
    train_offsets = _fit_residual_offsets(train_rows, labels, baseline_predictor)

    def corrected_predictor(row: MaterialsRow) -> float:
        return baseline_predictor(row) + train_offsets.get(labels[row.row_id], 0.0)

    corrected_metrics = {
        split_id: _residual_metrics(split_rows, corrected_predictor)
        for split_id, split_rows in splits.items()
    }
    corrected_metrics["full_md0001_axis"] = _residual_metrics(rows, corrected_predictor)
    baseline_metrics = {
        split_id: _residual_metrics(split_rows, baseline_predictor)
        for split_id, split_rows in splits.items()
    }
    baseline_metrics["full_md0001_axis"] = _residual_metrics(rows, baseline_predictor)
    improvement = {
        split_id: round(
            float(baseline_metrics[split_id]["mae"])
            - float(corrected_metrics[split_id]["mae"]),
            6,
        )
        for split_id in baseline_metrics
    }
    parameter_count = len(train_offsets)
    complexity_penalty = round(
        COMPLEXITY_PENALTY_EV_PER_PARAMETER * parameter_count, 6
    )
    return {
        "parameter_count": parameter_count,
        "complexity_penalty_ev_per_atom": complexity_penalty,
        "corrected": corrected_metrics,
        "improvement_vs_baseline_mae": improvement,
        "penalized_holdout_improvement": round(
            improvement["holdout"] - complexity_penalty, 6
        ),
        "verdict": _lane_verdict(improvement, complexity_penalty),
    }


def split_sensitivity(
    rows: list[MaterialsRow],
    candidate_labelers: dict[str, Labeler],
) -> dict[str, Any]:
    """Seeded 70/30 holdout stability for each candidate lane."""
    summaries: dict[str, Any] = {}
    for candidate_id, labeler in candidate_labelers.items():
        seed_improvements: list[float] = []
        for seed in range(5):
            shuffled = rows[:]
            random.Random(seed).shuffle(shuffled)
            train_count = int(len(shuffled) * 0.7)
            splits = {
                "train": shuffled[:train_count],
                "validation": [],
                "holdout": shuffled[train_count:],
            }
            baseline_predictor = _fit_baselines(splits["train"])["cation_group_mean"]
            scored = score_offset_lane(shuffled, splits, baseline_predictor, labeler)
            seed_improvements.append(scored["improvement_vs_baseline_mae"]["holdout"])
        positive = sum(1 for value in seed_improvements if value > 0.0)
        summaries[candidate_id] = {
            "seeded_random_70_30_holdout_improvements": [
                round(value, 6) for value in seed_improvements
            ],
            "positive_seed_count": positive,
            "stable_positive": positive >= 4,
        }
    return summaries


def load_formation_energy_rows(dataset_file: str | Path) -> list[MaterialsRow]:
    """Load the MD-0001 formation-energy rows referenced by the spec dataset."""
    path = Path(dataset_file)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return _included_rows(
        _load_axis_rows(path),
        expected_property_kind=FORMATION_ENERGY_PROPERTY,
    )


# --- Candidate routing (lane outcome -> core verdict/state) -----------------


def _route_lane(
    lane: dict[str, Any],
    *,
    best_control_penalized: float,
    stable: bool,
) -> tuple[str, str]:
    """Map a scored lane to (candidate_state, route_verdict) in the core vocabulary."""
    improvement = lane["improvement_vs_baseline_mae"]
    if lane["verdict"] == "negative":
        return "EXECUTED", "NEGATIVE_RESULT"
    margin = round(lane["penalized_holdout_improvement"] - best_control_penalized, 6)
    if margin <= 0.0:
        # A matched null control does at least as well: not a real signal.
        return "REJECTED_BY_CONTROL", "REJECTED_BY_CONTROL"
    if margin >= SURVIVAL_MARGIN_EV_PER_ATOM and stable:
        return "SHORTLISTED", "READY_FOR_REPLAY"
    if improvement["holdout"] > 0.0:
        return "EXECUTED", "INCONCLUSIVE"
    return "EXECUTED", "NEGATIVE_RESULT"


class MaterialsFormationEnergyFactoryAdapter:
    """Residual-offset formation-energy adapter over the shared factory core."""

    adapter_id = "materials_formation_energy_factory"
    adapter_version = "0.1"

    def build_run(self, spec: FactorySpec) -> FactoryRun:
        _validate_spec_contract(spec)
        rows = load_formation_energy_rows(spec.dataset["snapshot_ref"])
        splits = _split_rows(rows)
        baseline_predictor = _fit_baselines(splits["train"])[
            str(spec.baseline.get("baseline_id", "cation_group_mean"))
        ]

        selected_families = spec.families[: spec.candidate_cap]
        candidate_labelers = {
            family: CANDIDATE_LABELERS[family] for family in selected_families
        }
        control_labelers = {
            control: CONTROL_LABELERS[control] for control in spec.controls
        }

        scored_candidates = {
            cid: score_offset_lane(rows, splits, baseline_predictor, labeler)
            for cid, labeler in candidate_labelers.items()
        }
        scored_controls = {
            cid: score_offset_lane(rows, splits, baseline_predictor, labeler)
            for cid, labeler in control_labelers.items()
        }
        sensitivity = split_sensitivity(rows, candidate_labelers)

        best_control_penalized = (
            max(c["penalized_holdout_improvement"] for c in scored_controls.values())
            if scored_controls
            else 0.0
        )
        best_control_id = (
            max(
                scored_controls.items(),
                key=lambda item: item[1]["penalized_holdout_improvement"],
            )[0]
            if scored_controls
            else None
        )

        candidates: list[Candidate] = []
        for index, (cid, lane) in enumerate(scored_candidates.items(), start=1):
            if len(candidates) >= spec.candidate_cap:
                break
            stable = sensitivity[cid]["stable_positive"]
            state, verdict = _route_lane(
                lane, best_control_penalized=best_control_penalized, stable=stable
            )
            control_outcomes = tuple(
                {
                    "name": control_id,
                    "outcome": (
                        "candidate_wins"
                        if lane["penalized_holdout_improvement"]
                        > control["penalized_holdout_improvement"]
                        else "control_matches_or_wins"
                    ),
                }
                for control_id, control in scored_controls.items()
            )
            candidates.append(
                Candidate(
                    candidate_id=f"material-lane-{index:02d}",
                    family=cid,
                    complexity=float(lane["parameter_count"]),
                    leakage_status="CHECKED_CLEAN",
                    candidate_state=state,
                    route_verdict=verdict,
                    parameters={
                        "parameter_count": lane["parameter_count"],
                        "complexity_penalty_ev_per_atom": lane[
                            "complexity_penalty_ev_per_atom"
                        ],
                    },
                    metrics={
                        "validation_mae_improvement": lane[
                            "improvement_vs_baseline_mae"
                        ]["validation"],
                        "holdout_mae_improvement": lane["improvement_vs_baseline_mae"][
                            "holdout"
                        ],
                        "penalized_holdout_improvement": lane[
                            "penalized_holdout_improvement"
                        ],
                        "split_stable_positive": stable,
                    },
                    control_outcomes=control_outcomes,
                )
            )

        controls = tuple(
            {
                "name": control_id,
                "outcome": (
                    "matched null label permutation; penalized_holdout_improvement "
                    f"{control['penalized_holdout_improvement']} eV/atom"
                ),
            }
            for control_id, control in scored_controls.items()
        )

        best_candidate = (
            max(
                candidates,
                key=lambda c: float(c.metrics["penalized_holdout_improvement"]),
            )
            if candidates
            else None
        )
        campaign_specific = {
            "target_axis": FORMATION_ENERGY_PROPERTY,
            "excluded_axis": "band_gap",
            "survival_margin_ev_per_atom": SURVIVAL_MARGIN_EV_PER_ATOM,
            "dataset_id": str(spec.dataset.get("source_id", "MD-0001")),
            "row_count": len(rows),
            "best_control_id": best_control_id,
            "best_candidate_id": best_candidate.candidate_id if best_candidate else None,
            "best_candidate_family": best_candidate.family if best_candidate else None,
            "split_counts": {key: len(value) for key, value in splits.items()},
            "split_sensitivity": sensitivity,
        }

        return FactoryRun(
            dataset={
                "snapshot_ref": str(spec.dataset["snapshot_ref"]),
                "source_id": str(spec.dataset.get("source_id", "MD-0001")),
                "retrieval_policy": str(
                    spec.dataset.get("retrieval_policy", "no_live_fetch")
                ),
                "checksum_policy": str(
                    spec.dataset.get("checksum_policy", "recorded in source manifest")
                ),
            },
            baseline={
                "baseline_id": str(
                    spec.baseline.get("baseline_id", "cation_group_mean")
                ),
                "baseline_type": str(spec.baseline.get("baseline_type", "frozen")),
            },
            controls=controls,
            candidates=tuple(candidates),
            campaign_specific=campaign_specific,
        )


register_adapter(MaterialsFormationEnergyFactoryAdapter())
