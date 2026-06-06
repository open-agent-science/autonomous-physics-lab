#!/usr/bin/env python3
"""Run TASK-0553 Nuclear F2 controls-first scoring on NMD-0003."""

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

from physics_lab._runtime import enforce as _enforce_python_runtime  # noqa: E402

# This script uses 3.10+ runtime features (e.g. zip(strict=True)); fail fast with
# an actionable message rather than a cryptic TypeError on an old interpreter.
_enforce_python_runtime()

from physics_lab.engines.nuclear_f2_coverage import assign_f2_bin  # noqa: E402
from physics_lab.engines.nuclear_mass_baselines import (  # noqa: E402
    BaselineResidualRow,
    SemiEmpiricalCoefficients,
    evaluate_baseline,
)
from physics_lab.engines.nuclear_masses import NuclearMassEntry, load_nuclear_mass_dataset  # noqa: E402

TASK_ID = "TASK-0553"
AGENT_RUN_ID = "AGENT-RUN-0060"
DATASET_PATH = REPO_ROOT / "data" / "nuclear_masses" / "nmd-0003-ame2020-measured-training.yaml"
GATE_PATH = REPO_ROOT / "data" / "nuclear_masses" / "nmd-0003-stratified-baseline-gate.yaml"
MANIFEST_PATH = REPO_ROOT / "data" / "nuclear_masses" / "f2-coverage-selection-manifest.yaml"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
DEFAULT_REVIEW_PATH = REPO_ROOT / "docs" / "reviews" / "nuclear-f2-controls-first-scoring.md"

SURVIVAL_MARGIN_MEV = 0.25
RANDOM_SEED = 553


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

    metrics = run_f2_controls_first_scoring()
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "report.md").write_text(render_report(metrics), encoding="utf-8")
    review_path.write_text(render_review(metrics), encoding="utf-8")
    print(f"F2 controls-first scoring complete: {output_dir / 'metrics.json'}")
    print(f"Verdict: {metrics['verdict']}")
    return 0


def run_f2_controls_first_scoring() -> dict[str, Any]:
    dataset = load_nuclear_mass_dataset(DATASET_PATH)
    entries = sorted(
        dataset.entries, key=lambda entry: (entry.A, entry.Z, entry.N, entry.nuclide_id)
    )
    gate = yaml.safe_load(GATE_PATH.read_text(encoding="utf-8"))
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))

    _assert_gate_contract(gate, manifest, entries)
    train_entries, validation_entries = _stratified_split(entries)
    baseline_rows = _region_stratified_baseline_rows(entries, gate)
    rows_by_id = {row.nuclide_id: row for row in baseline_rows}

    labelers: dict[str, Callable[[list[NuclearMassEntry]], dict[str, str]]] = {
        "candidate_f2_finer_taxonomy": _f2_labels,
        "matched_random": _matched_random_labels,
        "smooth_a": _smooth_a_labels,
        "asymmetry_only": _asymmetry_only_labels,
        "cluster_label_shuffle": _cluster_label_shuffle_labels,
    }
    lanes = {
        lane_id: _score_lane(entries, train_entries, validation_entries, rows_by_id, labeler)
        for lane_id, labeler in labelers.items()
    }
    candidate = lanes["candidate_f2_finer_taxonomy"]
    controls = {k: v for k, v in lanes.items() if k != "candidate_f2_finer_taxonomy"}
    best_control = max(
        control["improvement_vs_baseline"]["full_known"]["mae_improvement_mev"]
        for control in controls.values()
    )
    candidate_full = candidate["improvement_vs_baseline"]["full_known"]["mae_improvement_mev"]
    candidate_validation = candidate["improvement_vs_baseline"]["validation_holdout"][
        "mae_improvement_mev"
    ]
    survival_margin = round(float(candidate_full - best_control), 6)
    margin_clears = survival_margin >= SURVIVAL_MARGIN_MEV
    validation_regresses = candidate_validation < 0.0
    verdict = _verdict(
        margin_clears=margin_clears,
        validation_regresses=validation_regresses,
        candidate_full=candidate_full,
    )

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
            "f2_selection_manifest": _rel(MANIFEST_PATH),
            "f2_preflight_review": "docs/reviews/nuclear-f2-finer-taxonomy-preflight.md",
            "coverage_review": "docs/reviews/nuclear-f2-coverage-clearing-slice.md",
            "no_leakage_contract": "docs/nuclear-residual-feature-no-leakage-contract.md",
        },
        "baseline_contract": {
            "baseline_id": gate["baseline_contract"]["primary_readiness_baseline"][
                "baseline_id"
            ],
            "split_id": gate["split_contract"]["primary_readiness_split_id"],
            "post_ame2020_holdout_scoring_allowed": False,
        },
        "controls_first_contract": {
            "controls": list(controls),
            "survival_margin_mev": SURVIVAL_MARGIN_MEV,
            "f2_eligibility": "diagnostic_only",
            "no_prediction_or_claim_artifacts": True,
        },
        "lanes": lanes,
        "decision": {
            "best_control_full_known_mae_improvement_mev": round(float(best_control), 6),
            "candidate_full_known_mae_improvement_mev": round(float(candidate_full), 6),
            "candidate_minus_best_control_full_known_mae_improvement_mev": survival_margin,
            "survival_margin_clears": margin_clears,
            "validation_holdout_regresses": validation_regresses,
        },
        "verdict": verdict,
        "limitations": [
            "Retrospective AME2020 measured-row scoring only; no post-AME2020 reveal scoring.",
            "F2 remains diagnostic_only regardless of this run's outcome.",
            "The lane fits per-bin residual offsets against the frozen readiness baseline; it does not create PRED, CLAIM, KNOW, or RESULT artifacts.",
        ],
        "output_routing": {
            "task_verdict": verdict,
            "canonical_destination": [
                f"agent_runs/{AGENT_RUN_ID}/metrics.json",
                f"agent_runs/{AGENT_RUN_ID}/report.md",
                "docs/reviews/nuclear-f2-controls-first-scoring.md",
            ],
            "review_tier": "none",
            "gate_a_status": "not_attempted",
            "gate_b_status": "not_applicable",
            "claim_impact": "none",
            "knowledge_impact": "none",
            "result_impact": "no RESULT artifact created",
        },
    }


def _assert_gate_contract(
    gate: dict[str, Any], manifest: dict[str, Any], entries: list[NuclearMassEntry]
) -> None:
    if gate["status"] != "frozen_readiness_gate":
        raise ValueError("NMD-0003 stratified baseline gate is not frozen.")
    if not gate["readiness_decision"]["future_bounded_residual_feature_sprint_allowed"]:
        raise ValueError("Frozen gate does not allow residual-feature scoring.")
    if gate["source_dataset"] != _rel(DATASET_PATH):
        raise ValueError("Gate source dataset does not match TASK-0553 dataset.")
    if not manifest["gate_result"]["gate_clears"]:
        raise ValueError("F2 coverage manifest does not clear the pre-score gate.")
    if manifest["source_dataset"] != _rel(DATASET_PATH):
        raise ValueError("F2 manifest source dataset does not match TASK-0553 dataset.")
    if len(entries) != gate["split_contract"]["train_count"] + gate["split_contract"][
        "validation_holdout_count"
    ]:
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
        region_entries = [entry for entry in entries if _a_region(entry.A) == region]
        rows.extend(
            evaluate_baseline(
                entries=region_entries,
                model_id="nmd0003_region_stratified_diagnostic",
                coefficients=coeffs[region],
            )
        )
    rows.sort(key=lambda row: (row.A, row.Z, row.N, row.nuclide_id))
    return rows


def _score_lane(
    entries: list[NuclearMassEntry],
    train_entries: list[NuclearMassEntry],
    validation_entries: list[NuclearMassEntry],
    rows_by_id: dict[str, BaselineResidualRow],
    labeler: Callable[[list[NuclearMassEntry]], dict[str, str]],
) -> dict[str, Any]:
    labels = labeler(entries)
    train_ids = {entry.nuclide_id for entry in train_entries}
    validation_ids = {entry.nuclide_id for entry in validation_entries}
    train_rows = [rows_by_id[entry.nuclide_id] for entry in train_entries]
    validation_rows = [rows_by_id[entry.nuclide_id] for entry in validation_entries]
    offsets = _fit_offsets(train_rows, labels)
    train_corrected = _corrected_residuals_train_loo(train_rows, labels)
    validation_corrected = [
        row.residual_mev - offsets.get(labels[row.nuclide_id], 0.0) for row in validation_rows
    ]
    all_corrected = []
    for entry in entries:
        row = rows_by_id[entry.nuclide_id]
        if entry.nuclide_id in train_ids:
            all_corrected.append(train_corrected[entry.nuclide_id])
        elif entry.nuclide_id in validation_ids:
            all_corrected.append(row.residual_mev - offsets.get(labels[row.nuclide_id], 0.0))
        else:
            raise ValueError(f"Row outside split: {entry.nuclide_id}")

    baseline = {
        "train_loo": _summary([row.residual_mev for row in train_rows]),
        "validation_holdout": _summary([row.residual_mev for row in validation_rows]),
        "full_known": _summary([rows_by_id[entry.nuclide_id].residual_mev for entry in entries]),
    }
    corrected = {
        "train_loo": _summary([train_corrected[row.nuclide_id] for row in train_rows]),
        "validation_holdout": _summary(validation_corrected),
        "full_known": _summary(all_corrected),
    }
    return {
        "label_counts": _label_counts(labels),
        "training_offsets_mev": {k: round(float(v), 6) for k, v in sorted(offsets.items())},
        "baseline": baseline,
        "corrected": corrected,
        "improvement_vs_baseline": {
            key: _improvement(baseline[key], corrected[key]) for key in baseline
        },
    }


def _fit_offsets(
    train_rows: list[BaselineResidualRow], labels: dict[str, str]
) -> dict[str, float]:
    grouped: dict[str, list[float]] = {}
    for row in train_rows:
        grouped.setdefault(labels[row.nuclide_id], []).append(row.residual_mev)
    return {label: float(np.mean(values)) for label, values in grouped.items()}


def _corrected_residuals_train_loo(
    train_rows: list[BaselineResidualRow], labels: dict[str, str]
) -> dict[str, float]:
    grouped: dict[str, list[BaselineResidualRow]] = {}
    for row in train_rows:
        grouped.setdefault(labels[row.nuclide_id], []).append(row)
    corrected: dict[str, float] = {}
    for row in train_rows:
        peers = [peer.residual_mev for peer in grouped[labels[row.nuclide_id]] if peer != row]
        offset = 0.0 if not peers else float(np.mean(peers))
        corrected[row.nuclide_id] = row.residual_mev - offset
    return corrected


def _f2_labels(entries: list[NuclearMassEntry]) -> dict[str, str]:
    return {entry.nuclide_id: assign_f2_bin(entry.Z, entry.N, entry.A) for entry in entries}


def _matched_random_labels(entries: list[NuclearMassEntry]) -> dict[str, str]:
    labels = list(_f2_labels(entries).values())
    random.Random(RANDOM_SEED).shuffle(labels)
    return {entry.nuclide_id: label for entry, label in zip(entries, labels, strict=True)}


def _cluster_label_shuffle_labels(entries: list[NuclearMassEntry]) -> dict[str, str]:
    rng = random.Random(RANDOM_SEED + 1)
    base = _f2_labels(entries)
    shuffled: dict[str, str] = {}
    for region in ("A<=40", "41<=A<=100", "101<=A<=180", "A>180"):
        region_entries = [entry for entry in entries if _a_region(entry.A) == region]
        labels = [base[entry.nuclide_id] for entry in region_entries]
        rng.shuffle(labels)
        for entry, label in zip(region_entries, labels, strict=True):
            shuffled[entry.nuclide_id] = label
    return shuffled


def _smooth_a_labels(entries: list[NuclearMassEntry]) -> dict[str, str]:
    return {entry.nuclide_id: _a_region(entry.A) for entry in entries}


def _asymmetry_only_labels(entries: list[NuclearMassEntry]) -> dict[str, str]:
    labels: dict[str, str] = {}
    for entry in entries:
        eta = (entry.N - entry.Z) / entry.A
        if eta < 0.10:
            label = "eta_lt_0p10"
        elif eta < 0.18:
            label = "eta_0p10_to_0p18"
        elif eta < 0.24:
            label = "eta_0p18_to_0p24"
        else:
            label = "eta_gte_0p24"
        labels[entry.nuclide_id] = label
    return labels


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


def _label_counts(labels: dict[str, str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for label in labels.values():
        counts[label] = counts.get(label, 0) + 1
    return dict(sorted(counts.items()))


def _a_region(a: int) -> str:
    if a <= 40:
        return "A<=40"
    if a <= 100:
        return "41<=A<=100"
    if a <= 180:
        return "101<=A<=180"
    return "A>180"


def _verdict(*, margin_clears: bool, validation_regresses: bool, candidate_full: float) -> str:
    if validation_regresses:
        return "NEGATIVE_RESULT"
    if margin_clears:
        return "BOUNDED_FOLLOWUP_CANDIDATE_DIAGNOSTIC_ONLY"
    if candidate_full > 0.0:
        return "DIAGNOSTIC_ONLY_CONTROL_DOMINATED"
    return "NEGATIVE_RESULT"


def render_report(metrics: dict[str, Any]) -> str:
    decision = metrics["decision"]
    candidate = metrics["lanes"]["candidate_f2_finer_taxonomy"]
    lines = [
        f"# {AGENT_RUN_ID} - Nuclear F2 Controls-First Scoring",
        "",
        f"**Task:** `{TASK_ID}`",
        f"**Verdict:** `{metrics['verdict']}`",
        "",
        "## Summary",
        "",
        "This run scores the frozen residual-free F2 finer taxonomy on the committed "
        "NMD-0003 measured-row surface under the frozen stratified readiness gate. "
        "F2 remains diagnostic-only; no prediction, claim, knowledge, or result "
        "artifact is created.",
        "",
        "## Decision Metrics",
        "",
        f"- Candidate full-known MAE improvement: "
        f"`{decision['candidate_full_known_mae_improvement_mev']}` MeV.",
        f"- Best control full-known MAE improvement: "
        f"`{decision['best_control_full_known_mae_improvement_mev']}` MeV.",
        f"- Candidate minus best control: "
        f"`{decision['candidate_minus_best_control_full_known_mae_improvement_mev']}` MeV.",
        f"- Survival margin clears: `{decision['survival_margin_clears']}`.",
        f"- Validation holdout regresses: `{decision['validation_holdout_regresses']}`.",
        "",
        "## F2 Candidate",
        "",
        "| surface | baseline MAE | corrected MAE | MAE improvement |",
        "| --- | ---: | ---: | ---: |",
    ]
    for surface in ("train_loo", "validation_holdout", "full_known"):
        lines.append(
            f"| `{surface}` | `{candidate['baseline'][surface]['mae_mev']}` | "
            f"`{candidate['corrected'][surface]['mae_mev']}` | "
            f"`{candidate['improvement_vs_baseline'][surface]['mae_improvement_mev']}` |"
        )
    lines.extend(["", _routing_text(metrics), ""])
    return "\n".join(lines)


def render_review(metrics: dict[str, Any]) -> str:
    report = render_report(metrics)
    return report.replace(
        f"# {AGENT_RUN_ID} - Nuclear F2 Controls-First Scoring",
        "# Nuclear F2 Controls-First Scoring",
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
