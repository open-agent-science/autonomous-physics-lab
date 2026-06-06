#!/usr/bin/env python3
"""Run TASK-0626 Materials MD-0001 formation-energy factory smoke sprint."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import random
import sys
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab._runtime import enforce as _enforce_python_runtime  # noqa: E402

_enforce_python_runtime()

from physics_lab.engines.materials_md0001_baseline import (  # noqa: E402
    MaterialsRow,
    _fit_baselines,
    _included_rows,
    _load_axis_rows,
    _residual_metrics,
    _split_rows,
    cation_group,
    formula_family,
)

TASK_ID = "TASK-0626"
AGENT_RUN_ID = "AGENT-RUN-0069"
CONFIG_PATH = REPO_ROOT / "examples" / "benchmarks" / "materials_md0001_baseline.yaml"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
DEFAULT_REVIEW_PATH = (
    REPO_ROOT / "docs" / "reviews" / "materials-md0001-formation-energy-factory-smoke-sprint.md"
)
FORMATION_ENERGY_PROPERTY = "formation_energy_per_atom"
SURVIVAL_MARGIN_EV_PER_ATOM = 0.05
RANDOM_SEED = 626

Labeler = Callable[[list[MaterialsRow]], dict[str, str]]


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

    metrics = run_materials_factory_smoke_sprint()
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "report.md").write_text(render_report(metrics), encoding="utf-8")
    review_path.write_text(render_review(metrics), encoding="utf-8")
    print(f"Materials factory smoke sprint complete: {output_dir / 'metrics.json'}")
    print(f"Outcome: {metrics['outcome']['classification']}")
    return 0


def run_materials_factory_smoke_sprint() -> dict[str, Any]:
    rows = _formation_energy_rows()
    splits = _split_rows(rows)
    baseline_predictor = _fit_baselines(splits["train"])["cation_group_mean"]
    baseline_metrics = {
        split_id: _residual_metrics(split_rows, baseline_predictor)
        for split_id, split_rows in splits.items()
    }
    baseline_metrics["full_md0001_axis"] = _residual_metrics(rows, baseline_predictor)

    candidate_labelers: dict[str, Labeler] = {
        "cation_group_residual_offsets": _cation_group_labels,
        "formula_family_residual_offsets": _formula_family_labels,
        "oxygen_stoichiometry_residual_offsets": _oxygen_stoichiometry_labels,
        "formula_family_x_cation_group_offsets": _formula_family_x_cation_group_labels,
    }
    control_labelers: dict[str, Labeler] = {
        "label_shuffle_control": _label_shuffle_labels,
        "cation_group_shuffle_control": _cation_group_shuffle_labels,
        "matched_random_formula_family_control": _matched_random_formula_family_labels,
    }
    candidates = {
        candidate_id: _score_offset_lane(rows, splits, baseline_predictor, labeler)
        for candidate_id, labeler in candidate_labelers.items()
    }
    controls = {
        control_id: _score_offset_lane(rows, splits, baseline_predictor, labeler)
        for control_id, labeler in control_labelers.items()
    }
    split_sensitivity = _split_sensitivity(rows, candidate_labelers)
    outcome = _classify(candidates, controls, split_sensitivity)
    return {
        "task_id": TASK_ID,
        "agent_run_id": AGENT_RUN_ID,
        "dataset": {
            "dataset_id": "MD-0001-materials-project-formation-energy",
            "path": "data/materials/md-0001-materials-project-formation-energy.yaml",
            "axis": FORMATION_ENERGY_PROPERTY,
            "row_count": len(rows),
            "split_counts": {key: len(value) for key, value in splits.items()},
        },
        "input_references": {
            "config": _rel(CONFIG_PATH),
            "baseline_review": "docs/reviews/materials-md0001-baseline-residual-benchmark.md",
            "null_control_review": "docs/reviews/materials-md0001-formation-energy-null-control-audit.md",
            "split_sensitivity_review": "docs/reviews/materials-md0001-split-sensitivity-audit.md",
            "adapter_fit_review": "docs/reviews/materials-research-factory-adapter-fit-review.md",
        },
        "factory_contract": {
            "candidate_cap": 12,
            "executed_candidate_count": len(candidates),
            "target_axis": FORMATION_ENERGY_PROPERTY,
            "excluded_axis": "band_gap",
            "baseline_id": "cation_group_mean",
            "survival_margin_ev_per_atom": SURVIVAL_MARGIN_EV_PER_ATOM,
            "complexity_penalty_ev_per_parameter": 0.01,
            "live_external_fetch": False,
        },
        "baseline": baseline_metrics,
        "candidates": candidates,
        "controls": controls,
        "split_sensitivity": split_sensitivity,
        "outcome": outcome,
        "limitations": [
            "Computed-DFT stable binary oxides only; no experimental formation energies.",
            "Formation energy only; band-gap rows and residuals are not loaded or pooled.",
            "Small MD-0001 holdout; smoke-sprint outputs are diagnostic-only.",
            "No live Materials Project fetch, row addition, prediction, claim, knowledge, or result promotion.",
        ],
        "output_routing": {
            "task_verdict": outcome["classification"],
            "canonical_destination": [
                f"agent_runs/{AGENT_RUN_ID}/metrics.json",
                f"agent_runs/{AGENT_RUN_ID}/report.md",
                "docs/reviews/materials-md0001-formation-energy-factory-smoke-sprint.md",
            ],
            "review_tier": "none",
            "gate_a_status": "not_attempted",
            "gate_b_status": "not_applicable",
            "claim_impact": "none",
            "knowledge_impact": "none",
            "result_impact": "no RESULT artifact created",
            "publication_blocker": "diagnostic-only factory smoke sprint; no canonical result promotion in task scope",
        },
    }


def _formation_energy_rows() -> list[MaterialsRow]:
    import yaml

    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    axis = next(
        axis
        for axis in config["dataset"]["axes"]
        if axis["property_kind"] == FORMATION_ENERGY_PROPERTY
    )
    return _included_rows(
        _load_axis_rows(REPO_ROOT / axis["dataset_file"]),
        expected_property_kind=FORMATION_ENERGY_PROPERTY,
    )


def _score_offset_lane(
    rows: list[MaterialsRow],
    splits: dict[str, list[MaterialsRow]],
    baseline_predictor: Callable[[MaterialsRow], float],
    labeler: Labeler,
) -> dict[str, Any]:
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
            float(baseline_metrics[split_id]["mae"]) - float(corrected_metrics[split_id]["mae"]),
            6,
        )
        for split_id in baseline_metrics
    }
    parameter_count = len(train_offsets)
    complexity_penalty = round(0.01 * parameter_count, 6)
    return {
        "label_counts": _label_counts(labels),
        "parameter_count": parameter_count,
        "complexity_penalty_ev_per_atom": complexity_penalty,
        "training_offsets_ev_per_atom": {
            key: round(value, 6) for key, value in sorted(train_offsets.items())
        },
        "corrected": corrected_metrics,
        "improvement_vs_baseline_mae": improvement,
        "penalized_holdout_improvement": round(improvement["holdout"] - complexity_penalty, 6),
        "verdict": _lane_verdict(improvement, complexity_penalty),
    }


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


def _split_sensitivity(
    rows: list[MaterialsRow],
    candidate_labelers: dict[str, Labeler],
) -> dict[str, Any]:
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
            scored = _score_offset_lane(shuffled, splits, baseline_predictor, labeler)
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


def _classify(
    candidates: dict[str, Any],
    controls: dict[str, Any],
    split_sensitivity: dict[str, Any],
) -> dict[str, Any]:
    best_candidate_id, best_candidate = max(
        candidates.items(), key=lambda item: item[1]["penalized_holdout_improvement"]
    )
    best_control_id, best_control = max(
        controls.items(), key=lambda item: item[1]["penalized_holdout_improvement"]
    )
    margin = round(
        best_candidate["penalized_holdout_improvement"]
        - best_control["penalized_holdout_improvement"],
        6,
    )
    stable = split_sensitivity[best_candidate_id]["stable_positive"]
    if best_candidate["verdict"] == "negative":
        classification = "NEGATIVE"
    elif margin >= SURVIVAL_MARGIN_EV_PER_ATOM and stable:
        classification = "REPLAY_NEEDED"
    elif best_candidate["improvement_vs_baseline_mae"]["holdout"] > 0.0:
        classification = "DIAGNOSTIC_ONLY"
    else:
        classification = "NEGATIVE"
    return {
        "classification": classification,
        "best_candidate_id": best_candidate_id,
        "best_control_id": best_control_id,
        "candidate_minus_best_control_penalized_holdout_improvement": margin,
        "best_candidate_holdout_improvement": best_candidate["improvement_vs_baseline_mae"][
            "holdout"
        ],
        "best_candidate_penalized_holdout_improvement": best_candidate[
            "penalized_holdout_improvement"
        ],
        "best_candidate_split_stable_positive": stable,
        "interpretation": _interpretation(classification, best_candidate_id),
    }


def _interpretation(classification: str, best_candidate_id: str) -> str:
    if classification == "REPLAY_NEEDED":
        return (
            f"{best_candidate_id} beats the matched controls after complexity penalty "
            "and remains positive under seeded split sensitivity; keep it diagnostic-only "
            "pending an independent replay task."
        )
    if classification == "DIAGNOSTIC_ONLY":
        return (
            f"{best_candidate_id} has useful diagnostic signal, but the smoke sprint "
            "does not clear the controls/split-stability threshold for promotion."
        )
    return "No candidate clears the frozen baseline plus controls in this smoke sprint."


def _cation_group_labels(rows: list[MaterialsRow]) -> dict[str, str]:
    return {row.row_id: cation_group(row) for row in rows}


def _formula_family_labels(rows: list[MaterialsRow]) -> dict[str, str]:
    return {row.row_id: formula_family(row) for row in rows}


def _oxygen_stoichiometry_labels(rows: list[MaterialsRow]) -> dict[str, str]:
    labels: dict[str, str] = {}
    for row in rows:
        oxygen = row.composition.get("O", 0.0)
        cation_total = sum(amount for element, amount in row.composition.items() if element != "O")
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


def _label_counts(labels: dict[str, str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for label in labels.values():
        counts[label] = counts.get(label, 0) + 1
    return dict(sorted(counts.items()))


def render_report(metrics: dict[str, Any]) -> str:
    outcome = metrics["outcome"]
    lines = [
        f"# {AGENT_RUN_ID} - Materials MD-0001 Formation-Energy Factory Smoke Sprint",
        "",
        f"**Task:** `{TASK_ID}`",
        f"**Outcome:** `{outcome['classification']}`",
        "",
        "## Summary",
        "",
        "This smoke sprint runs bounded residual-offset candidates on committed "
        "MD-0001 formation-energy rows only. It keeps the frozen cation-group "
        "baseline and split, runs deterministic controls, excludes band gap, and "
        "creates no result, prediction, claim, knowledge, or materials guidance.",
        "",
        "## Decision",
        "",
        f"- Best candidate: `{outcome['best_candidate_id']}`.",
        f"- Best control: `{outcome['best_control_id']}`.",
        f"- Candidate minus best-control penalized holdout improvement: "
        f"`{outcome['candidate_minus_best_control_penalized_holdout_improvement']}` eV/atom.",
        f"- Interpretation: {outcome['interpretation']}",
        "",
        "## Candidate Slate",
        "",
        "| lane | validation improvement | holdout improvement | penalized holdout | verdict |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for lane_id, lane in metrics["candidates"].items():
        improvements = lane["improvement_vs_baseline_mae"]
        lines.append(
            f"| `{lane_id}` | `{improvements['validation']}` | `{improvements['holdout']}` | "
            f"`{lane['penalized_holdout_improvement']}` | `{lane['verdict']}` |"
        )
    lines.extend(["", "## Controls", "", "| control | holdout improvement | penalized holdout |", "| --- | ---: | ---: |"])
    for control_id, control in metrics["controls"].items():
        lines.append(
            f"| `{control_id}` | `{control['improvement_vs_baseline_mae']['holdout']}` | "
            f"`{control['penalized_holdout_improvement']}` |"
        )
    lines.extend(["", _routing_text(metrics), ""])
    return "\n".join(lines)


def render_review(metrics: dict[str, Any]) -> str:
    return render_report(metrics).replace(
        f"# {AGENT_RUN_ID} - Materials MD-0001 Formation-Energy Factory Smoke Sprint",
        "# Materials MD-0001 Formation-Energy Factory Smoke Sprint",
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
            f"- Publication blocker: `{routing['publication_blocker']}`.",
        ]
    )


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
