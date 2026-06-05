#!/usr/bin/env python3
"""Run TASK-0584 bounded NMD-0003 residual-feature sprint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import sys
from typing import Any, Callable

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.engines.nuclear_mass_baselines import (  # noqa: E402
    BaselineResidualRow,
    SemiEmpiricalCoefficients,
    evaluate_baseline,
)
from physics_lab.engines.nuclear_masses import NuclearMassEntry, load_nuclear_mass_dataset  # noqa: E402

TASK_ID = "TASK-0584"
AGENT_RUN_ID = "AGENT-RUN-0061"
DATASET_PATH = REPO_ROOT / "data" / "nuclear_masses" / "nmd-0003-ame2020-measured-training.yaml"
GATE_PATH = REPO_ROOT / "data" / "nuclear_masses" / "nmd-0003-stratified-baseline-gate.yaml"
FACTORY_MEMORY_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0053" / "factory_summary.yaml"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
DEFAULT_REVIEW_PATH = (
    REPO_ROOT / "docs" / "reviews" / "nmd0003-bounded-residual-feature-sprint.md"
)

SURVIVAL_MARGIN_MEV = 0.25
RANDOM_SEED = 584


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--review-path", default=str(DEFAULT_REVIEW_PATH))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    review_path = Path(args.review_path)
    review_path.parent.mkdir(parents=True, exist_ok=True)

    metrics = run_bounded_residual_feature_sprint()
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "report.md").write_text(render_report(metrics), encoding="utf-8")
    review_path.write_text(render_review(metrics), encoding="utf-8")
    print(f"NMD-0003 bounded sprint complete: {output_dir / 'metrics.json'}")
    print(f"Verdict: {metrics['verdict']}")
    return 0


def run_bounded_residual_feature_sprint() -> dict[str, Any]:
    dataset = load_nuclear_mass_dataset(DATASET_PATH)
    entries = sorted(
        dataset.entries, key=lambda entry: (entry.A, entry.Z, entry.N, entry.nuclide_id)
    )
    gate = yaml.safe_load(GATE_PATH.read_text(encoding="utf-8"))
    factory_memory = yaml.safe_load(FACTORY_MEMORY_PATH.read_text(encoding="utf-8"))
    _assert_contract(gate, factory_memory, entries)

    train_entries, validation_entries = _stratified_split(entries)
    primary_rows = _region_stratified_baseline_rows(entries, gate)
    audit_rows = _global_ols_baseline_rows(entries, gate)
    primary_by_id = {row.nuclide_id: row for row in primary_rows}
    audit_by_id = {row.nuclide_id: row for row in audit_rows}

    feature_builders: dict[str, Callable[[list[NuclearMassEntry]], dict[str, float]]] = {
        "candidate_coulomb_surface_interaction": _coulomb_surface_feature,
        "matched_random_slice": _matched_random_feature,
        "label_shuffle": _label_shuffle_feature,
        "smooth_control": _smooth_a_feature,
    }
    lanes = {
        lane_id: _score_feature_lane(
            entries=entries,
            train_entries=train_entries,
            validation_entries=validation_entries,
            rows_by_id=primary_by_id,
            feature_builder=builder,
        )
        for lane_id, builder in feature_builders.items()
    }
    audit_candidate = _score_feature_lane(
        entries=entries,
        train_entries=train_entries,
        validation_entries=validation_entries,
        rows_by_id=audit_by_id,
        feature_builder=_coulomb_surface_feature,
    )
    candidate = lanes["candidate_coulomb_surface_interaction"]
    controls = {k: v for k, v in lanes.items() if k != "candidate_coulomb_surface_interaction"}
    best_control = max(
        control["improvement_vs_baseline"]["validation_holdout"]["mae_improvement_mev"]
        for control in controls.values()
    )
    candidate_validation = candidate["improvement_vs_baseline"]["validation_holdout"][
        "mae_improvement_mev"
    ]
    candidate_full = candidate["improvement_vs_baseline"]["full_known"]["mae_improvement_mev"]
    survival_margin = round(float(candidate_validation - best_control), 6)
    margin_clears = survival_margin >= SURVIVAL_MARGIN_MEV
    validation_regresses = candidate_validation < 0.0
    verdict = _verdict(
        margin_clears=margin_clears,
        validation_regresses=validation_regresses,
        candidate_validation=candidate_validation,
    )

    prior_families = sorted({str(c["family"]) for c in factory_memory["candidates"]})
    return {
        "task_id": TASK_ID,
        "agent_run_id": AGENT_RUN_ID,
        "dataset": {
            "dataset_id": dataset.dataset_id,
            "path": _rel(DATASET_PATH),
            "row_count": len(entries),
            "train_count": len(train_entries),
            "validation_holdout_count": len(validation_entries),
        },
        "input_references": {
            "stratified_gate": _rel(GATE_PATH),
            "prior_factory_memory": _rel(FACTORY_MEMORY_PATH),
            "negative_result_preflight": "docs/reviews/nmd0003-factory-negative-result-promotion-preflight.md",
            "gauntlet": "docs/notes/nuclear-controls-first-hypothesis-gauntlet.md",
        },
        "selected_feature_family": {
            "family_id": "coulomb_surface_interaction",
            "feature": "Z*(Z-1)/A^(2/3), standardized on the frozen train split",
            "coefficient_policy": "single least-squares coefficient fit on primary readiness baseline residuals",
            "disjoint_from_task0517_families": prior_families,
            "disjoint_rationale": (
                "TASK-0517 swept shell_distance, asymmetry, odd_even_pairing, "
                "valence_z, valence_n, and blocked local_curvature families. "
                "This sprint tests a higher-order Coulomb surface coupling term "
                "against the frozen liquid-drop residuals instead of repeating "
                "those families or masks."
            ),
        },
        "baseline_contract": {
            "primary_readiness_baseline": gate["baseline_contract"][
                "primary_readiness_baseline"
            ]["baseline_id"],
            "required_audit_baseline": gate["baseline_contract"]["required_audit_baseline"][
                "baseline_id"
            ],
            "split_id": gate["split_contract"]["primary_readiness_split_id"],
            "post_ame2020_holdout_scoring_allowed": False,
        },
        "lanes_primary_readiness_baseline": lanes,
        "candidate_required_audit_baseline": audit_candidate,
        "decision": {
            "candidate_validation_mae_improvement_mev": round(float(candidate_validation), 6),
            "candidate_full_known_mae_improvement_mev": round(float(candidate_full), 6),
            "best_control_validation_mae_improvement_mev": round(float(best_control), 6),
            "candidate_minus_best_control_validation_mae_improvement_mev": survival_margin,
            "survival_margin_mev": SURVIVAL_MARGIN_MEV,
            "survival_margin_clears": margin_clears,
            "validation_holdout_regresses": validation_regresses,
        },
        "verdict": verdict,
        "limitations": [
            "One bounded residual-feature family only; no follow-up wave or retuning.",
            "Retrospective AME2020 measured-row validation only; no post-AME2020 reveal scoring.",
            "No PRED, CLAIM, KNOW, RESULT, or discovery artifact is created.",
        ],
        "output_routing": {
            "task_verdict": verdict,
            "canonical_destination": [
                f"agent_runs/{AGENT_RUN_ID}/metrics.json",
                f"agent_runs/{AGENT_RUN_ID}/report.md",
                "docs/reviews/nmd0003-bounded-residual-feature-sprint.md",
            ],
            "review_tier": "none",
            "gate_a_status": "not_attempted",
            "gate_b_status": "not_applicable",
            "claim_impact": "none",
            "knowledge_impact": "none",
            "result_impact": "no RESULT artifact created",
        },
    }


def _assert_contract(
    gate: dict[str, Any], factory_memory: dict[str, Any], entries: list[NuclearMassEntry]
) -> None:
    if gate["status"] != "frozen_readiness_gate":
        raise ValueError("NMD-0003 stratified baseline gate is not frozen.")
    if not gate["readiness_decision"]["future_bounded_residual_feature_sprint_allowed"]:
        raise ValueError("Frozen gate does not permit a bounded residual-feature sprint.")
    if gate["source_dataset"] != _rel(DATASET_PATH):
        raise ValueError("Gate source dataset does not match TASK-0584 dataset.")
    if factory_memory["task_id"] != "TASK-0517":
        raise ValueError("Prior factory memory must be TASK-0517.")
    prior_families = {str(c["family"]) for c in factory_memory["candidates"]}
    if "coulomb_surface_interaction" in prior_families:
        raise ValueError("Selected feature family is not disjoint from TASK-0517.")
    expected = gate["split_contract"]["train_count"] + gate["split_contract"][
        "validation_holdout_count"
    ]
    if len(entries) != expected:
        raise ValueError("Gate split counts do not match loaded dataset rows.")


def _stratified_split(
    entries: list[NuclearMassEntry],
) -> tuple[list[NuclearMassEntry], list[NuclearMassEntry]]:
    train = [entry for index, entry in enumerate(entries) if index % 10 < 7]
    validation = [entry for index, entry in enumerate(entries) if index % 10 >= 7]
    return train, validation


def _region_stratified_baseline_rows(
    entries: list[NuclearMassEntry], gate: dict[str, Any]
) -> list[BaselineResidualRow]:
    coeffs = {
        region: SemiEmpiricalCoefficients(**values)
        for region, values in gate["baseline_contract"]["primary_readiness_baseline"][
            "coefficients_by_a_region"
        ].items()
    }
    rows: list[BaselineResidualRow] = []
    for region in ("A<=40", "41<=A<=100", "101<=A<=180", "A>180"):
        rows.extend(
            evaluate_baseline(
                entries=[entry for entry in entries if _a_region(entry.A) == region],
                model_id="nmd0003_region_stratified_diagnostic",
                coefficients=coeffs[region],
            )
        )
    rows.sort(key=lambda row: (row.A, row.Z, row.N, row.nuclide_id))
    return rows


def _global_ols_baseline_rows(
    entries: list[NuclearMassEntry], gate: dict[str, Any]
) -> list[BaselineResidualRow]:
    coefficients = SemiEmpiricalCoefficients(
        **gate["baseline_contract"]["required_audit_baseline"]["coefficients"]
    )
    return evaluate_baseline(
        entries=entries,
        model_id="nmd0003_train_fitted_ols",
        coefficients=coefficients,
    )


def _score_feature_lane(
    *,
    entries: list[NuclearMassEntry],
    train_entries: list[NuclearMassEntry],
    validation_entries: list[NuclearMassEntry],
    rows_by_id: dict[str, BaselineResidualRow],
    feature_builder: Callable[[list[NuclearMassEntry]], dict[str, float]],
) -> dict[str, Any]:
    raw_features = feature_builder(entries)
    features = _standardize_features(raw_features, train_entries)
    train_rows = [rows_by_id[entry.nuclide_id] for entry in train_entries]
    validation_rows = [rows_by_id[entry.nuclide_id] for entry in validation_entries]
    beta = _fit_beta(train_rows, features)
    corrected = {
        "train": [
            row.residual_mev - beta * features[row.nuclide_id] for row in train_rows
        ],
        "validation_holdout": [
            row.residual_mev - beta * features[row.nuclide_id] for row in validation_rows
        ],
        "full_known": [
            rows_by_id[entry.nuclide_id].residual_mev - beta * features[entry.nuclide_id]
            for entry in entries
        ],
    }
    baseline = {
        "train": _summary([row.residual_mev for row in train_rows]),
        "validation_holdout": _summary([row.residual_mev for row in validation_rows]),
        "full_known": _summary([rows_by_id[entry.nuclide_id].residual_mev for entry in entries]),
    }
    corrected_summary = {key: _summary(values) for key, values in corrected.items()}
    return {
        "coefficient_mev_per_standardized_feature": round(float(beta), 6),
        "feature_summary": _feature_summary(features),
        "baseline": baseline,
        "corrected": corrected_summary,
        "improvement_vs_baseline": {
            key: _improvement(baseline[key], corrected_summary[key]) for key in baseline
        },
    }


def _fit_beta(rows: list[BaselineResidualRow], features: dict[str, float]) -> float:
    x = np.asarray([features[row.nuclide_id] for row in rows], dtype=float)
    y = np.asarray([row.residual_mev for row in rows], dtype=float)
    denom = float(np.dot(x, x))
    if denom == 0.0:
        return 0.0
    return float(np.dot(x, y) / denom)


def _standardize_features(
    raw: dict[str, float], train_entries: list[NuclearMassEntry]
) -> dict[str, float]:
    train_values = np.asarray([raw[entry.nuclide_id] for entry in train_entries], dtype=float)
    mean = float(np.mean(train_values))
    std = float(np.std(train_values))
    if std == 0.0:
        return {key: 0.0 for key in raw}
    return {key: (float(value) - mean) / std for key, value in raw.items()}


def _coulomb_surface_feature(entries: list[NuclearMassEntry]) -> dict[str, float]:
    return {
        entry.nuclide_id: float(entry.Z * (entry.Z - 1)) / (float(entry.A) ** (2.0 / 3.0))
        for entry in entries
    }


def _matched_random_feature(entries: list[NuclearMassEntry]) -> dict[str, float]:
    values = list(_coulomb_surface_feature(entries).values())
    random.Random(RANDOM_SEED).shuffle(values)
    return {entry.nuclide_id: value for entry, value in zip(entries, values, strict=True)}


def _label_shuffle_feature(entries: list[NuclearMassEntry]) -> dict[str, float]:
    base = _coulomb_surface_feature(entries)
    rng = random.Random(RANDOM_SEED + 1)
    shuffled: dict[str, float] = {}
    for region in ("A<=40", "41<=A<=100", "101<=A<=180", "A>180"):
        region_entries = [entry for entry in entries if _a_region(entry.A) == region]
        values = [base[entry.nuclide_id] for entry in region_entries]
        rng.shuffle(values)
        for entry, value in zip(region_entries, values, strict=True):
            shuffled[entry.nuclide_id] = value
    return shuffled


def _smooth_a_feature(entries: list[NuclearMassEntry]) -> dict[str, float]:
    return {entry.nuclide_id: float(entry.A) ** (2.0 / 3.0) for entry in entries}


def _summary(residuals: list[float]) -> dict[str, float | int]:
    values = np.asarray(residuals, dtype=float)
    abs_values = np.abs(values)
    return {
        "count": int(values.size),
        "mae_mev": round(float(np.mean(abs_values)), 6),
        "rmse_mev": round(float(np.sqrt(np.mean(values * values))), 6),
        "median_abs_residual_mev": round(float(np.median(abs_values)), 6),
        "p90_abs_residual_mev": round(float(np.percentile(abs_values, 90)), 6),
        "max_abs_residual_mev": round(float(np.max(abs_values)), 6),
    }


def _feature_summary(features: dict[str, float]) -> dict[str, float]:
    values = np.asarray(list(features.values()), dtype=float)
    return {
        "mean": round(float(np.mean(values)), 6),
        "std": round(float(np.std(values)), 6),
        "min": round(float(np.min(values)), 6),
        "max": round(float(np.max(values)), 6),
    }


def _improvement(
    baseline: dict[str, float | int], corrected: dict[str, float | int]
) -> dict[str, float]:
    baseline_mae = float(baseline["mae_mev"])
    corrected_mae = float(corrected["mae_mev"])
    baseline_rmse = float(baseline["rmse_mev"])
    corrected_rmse = float(corrected["rmse_mev"])
    return {
        "mae_improvement_mev": round(baseline_mae - corrected_mae, 6),
        "rmse_improvement_mev": round(baseline_rmse - corrected_rmse, 6),
    }


def _a_region(a: int) -> str:
    if a <= 40:
        return "A<=40"
    if a <= 100:
        return "41<=A<=100"
    if a <= 180:
        return "101<=A<=180"
    return "A>180"


def _verdict(
    *, margin_clears: bool, validation_regresses: bool, candidate_validation: float
) -> str:
    if validation_regresses:
        return "NEGATIVE_RESULT"
    if margin_clears:
        return "BOUNDED_FOLLOWUP_CANDIDATE"
    if candidate_validation > 0.0:
        return "INCONCLUSIVE_CONTROL_DOMINATED"
    return "NEGATIVE_RESULT"


def render_report(metrics: dict[str, Any]) -> str:
    decision = metrics["decision"]
    candidate = metrics["lanes_primary_readiness_baseline"][
        "candidate_coulomb_surface_interaction"
    ]
    lines = [
        f"# {AGENT_RUN_ID} - NMD-0003 Bounded Residual-Feature Sprint",
        "",
        f"**Task:** `{TASK_ID}`",
        f"**Verdict:** `{metrics['verdict']}`",
        "",
        "## Summary",
        "",
        "This bounded sprint tests exactly one disjoint residual-feature family, "
        "`coulomb_surface_interaction`, under the frozen NMD-0003 stratified gate. "
        "It does not score the post-AME2020 holdout and does not create prediction, "
        "claim, knowledge, or result artifacts.",
        "",
        "## Decision Metrics",
        "",
        f"- Candidate validation MAE improvement: "
        f"`{decision['candidate_validation_mae_improvement_mev']}` MeV.",
        f"- Best control validation MAE improvement: "
        f"`{decision['best_control_validation_mae_improvement_mev']}` MeV.",
        f"- Candidate minus best control: "
        f"`{decision['candidate_minus_best_control_validation_mae_improvement_mev']}` MeV.",
        f"- Survival margin clears: `{decision['survival_margin_clears']}`.",
        "",
        "## Candidate Surface Metrics",
        "",
        "| surface | baseline MAE | corrected MAE | MAE improvement |",
        "| --- | ---: | ---: | ---: |",
    ]
    for surface in ("train", "validation_holdout", "full_known"):
        lines.append(
            f"| `{surface}` | `{candidate['baseline'][surface]['mae_mev']}` | "
            f"`{candidate['corrected'][surface]['mae_mev']}` | "
            f"`{candidate['improvement_vs_baseline'][surface]['mae_improvement_mev']}` |"
        )
    lines.extend(["", _routing_text(metrics), ""])
    return "\n".join(lines)


def render_review(metrics: dict[str, Any]) -> str:
    return render_report(metrics).replace(
        f"# {AGENT_RUN_ID} - NMD-0003 Bounded Residual-Feature Sprint",
        "# NMD-0003 Bounded Residual-Feature Sprint",
        1,
    )


def _routing_text(metrics: dict[str, Any]) -> str:
    routing = metrics["output_routing"]
    return "\n".join(
        [
            "## Output Routing Summary",
            "",
            f"- Task verdict: `{routing['task_verdict']}`.",
            "- Canonical destination: "
            + ", ".join(f"`{path}`" for path in routing["canonical_destination"])
            + ".",
            f"- Review tier: `{routing['review_tier']}`.",
            f"- Gate A status: `{routing['gate_a_status']}`.",
            f"- Gate B status: `{routing['gate_b_status']}`.",
            f"- Claim impact: `{routing['claim_impact']}`.",
            f"- Knowledge impact: `{routing['knowledge_impact']}`.",
            f"- Result impact: `{routing['result_impact']}`.",
        ]
    )


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
