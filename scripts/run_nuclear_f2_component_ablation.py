#!/usr/bin/env python3
"""Run TASK-0625 Nuclear F2 survival-margin component ablation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab._runtime import enforce as _enforce_python_runtime  # noqa: E402

_enforce_python_runtime()

from scripts.run_nuclear_f2_controls_first_scoring import (  # noqa: E402
    DATASET_PATH,
    GATE_PATH,
    MANIFEST_PATH,
    SURVIVAL_MARGIN_MEV,
    _assert_gate_contract,
    _f2_labels,
    _fit_offsets,
    _improvement,
    _region_stratified_baseline_rows,
    _rel,
    _stratified_split,
    _summary,
)
from physics_lab.engines.nuclear_f2_coverage import F2_TAXONOMY  # noqa: E402
from physics_lab.engines.nuclear_masses import (  # noqa: E402
    NuclearMassEntry,
    load_nuclear_mass_dataset,
)

TASK_ID = "TASK-0625"
AGENT_RUN_ID = "AGENT-RUN-0068"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
DEFAULT_REVIEW_PATH = (
    REPO_ROOT / "docs" / "reviews" / "nuclear-f2-survival-margin-component-ablation.md"
)


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

    metrics = run_f2_component_ablation()
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "report.md").write_text(render_report(metrics), encoding="utf-8")
    review_path.write_text(render_review(metrics), encoding="utf-8")
    print(f"F2 component ablation complete: {output_dir / 'metrics.json'}")
    print(f"Outcome: {metrics['outcome']['classification']}")
    return 0


def run_f2_component_ablation() -> dict[str, Any]:
    import yaml

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
    labels = _f2_labels(entries)
    train_rows = [rows_by_id[entry.nuclide_id] for entry in train_entries]
    offsets = _fit_offsets(train_rows, labels)

    full_components = set(F2_TAXONOMY)
    slate = _component_slate(full_components)
    variants = {
        variant_id: _score_component_variant(
            entries=entries,
            train_entries=train_entries,
            validation_entries=validation_entries,
            rows_by_id=rows_by_id,
            labels=labels,
            offsets=offsets,
            active_components=active_components,
        )
        for variant_id, active_components in slate.items()
    }
    controls = _unchanged_control_ledger()
    best_control = controls["best_control_full_known_mae_improvement_mev"]
    for variant in variants.values():
        variant["decision"] = _variant_decision(variant, best_control)

    outcome = _classify_outcome(variants)
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
            "controls_first_scoring": "agent_runs/AGENT-RUN-0060/metrics.json",
            "independent_replay": "agent_runs/AGENT-RUN-0067/metrics.json",
            "promotion_or_stop_decision": (
                "docs/reviews/nuclear-f2-promotion-or-stop-decision.md"
            ),
        },
        "ablation_contract": {
            "predeclared_components": list(F2_TAXONOMY),
            "variant_rule": (
                "Apply the frozen F2 per-bin residual offsets only for the active "
                "component set; inactive component offsets are fixed to zero."
            ),
            "variant_count": len(variants),
            "controls_reuse": (
                "The matched_random, smooth_a, asymmetry_only, and cluster_label_shuffle "
                "controls are mathematically unchanged from AGENT-RUN-0067 because the "
                "dataset, split, baseline, labels, and control labelers are unchanged."
            ),
            "survival_margin_mev": SURVIVAL_MARGIN_MEV,
        },
        "controls": controls,
        "variants": variants,
        "outcome": outcome,
        "limitations": [
            "Retrospective AME2020 measured-row component ablation only; no post-AME2020 reveal scoring.",
            "The ablation zeroes F2 component offsets but does not define a new feature family.",
            "Controls are reused because their mathematical inputs are unchanged; no promotion is authorized.",
            "Sandbox diagnostic evidence only; no PRED, reveal score, RESULT, CLAIM, KNOW, or discovery wording is created.",
        ],
        "output_routing": {
            "task_verdict": outcome["classification"],
            "canonical_destination": [
                f"agent_runs/{AGENT_RUN_ID}/metrics.json",
                f"agent_runs/{AGENT_RUN_ID}/report.md",
                "docs/reviews/nuclear-f2-survival-margin-component-ablation.md",
            ],
            "review_tier": "none",
            "gate_a_status": "not_attempted",
            "gate_b_status": "not_applicable",
            "claim_impact": "none",
            "knowledge_impact": "none",
            "result_impact": "no RESULT artifact created",
            "publication_blocker": "diagnostic-only ablation; no canonical result promotion in task scope",
        },
    }


def _component_slate(components: set[str]) -> dict[str, set[str]]:
    slate: dict[str, set[str]] = {"full_f2_reference": set(components)}
    for component in F2_TAXONOMY:
        slate[f"without_{component}"] = set(components) - {component}
    for component in F2_TAXONOMY:
        slate[f"only_{component}"] = {component}
    return slate


def _score_component_variant(
    *,
    entries: list[NuclearMassEntry],
    train_entries: list[NuclearMassEntry],
    validation_entries: list[NuclearMassEntry],
    rows_by_id: dict[str, Any],
    labels: dict[str, str],
    offsets: dict[str, float],
    active_components: set[str],
) -> dict[str, Any]:
    train_ids = {entry.nuclide_id for entry in train_entries}
    validation_ids = {entry.nuclide_id for entry in validation_entries}
    train_rows = [rows_by_id[entry.nuclide_id] for entry in train_entries]
    validation_rows = [rows_by_id[entry.nuclide_id] for entry in validation_entries]

    def correction_for(nuclide_id: str) -> float:
        label = labels[nuclide_id]
        if label not in active_components:
            return 0.0
        return offsets[label]

    grouped_train: dict[str, list[Any]] = {}
    for row in train_rows:
        grouped_train.setdefault(labels[row.nuclide_id], []).append(row)

    train_corrected = {}
    for row in train_rows:
        label = labels[row.nuclide_id]
        if label not in active_components:
            offset = 0.0
        else:
            peers = [peer.residual_mev for peer in grouped_train[label] if peer != row]
            offset = 0.0 if not peers else sum(peers) / len(peers)
        train_corrected[row.nuclide_id] = row.residual_mev - offset
    validation_corrected = [
        row.residual_mev - correction_for(row.nuclide_id) for row in validation_rows
    ]
    all_corrected = []
    for entry in entries:
        row = rows_by_id[entry.nuclide_id]
        if entry.nuclide_id in train_ids:
            all_corrected.append(train_corrected[entry.nuclide_id])
        elif entry.nuclide_id in validation_ids:
            all_corrected.append(row.residual_mev - correction_for(row.nuclide_id))
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
        "active_components": sorted(active_components),
        "inactive_components": [component for component in F2_TAXONOMY if component not in active_components],
        "baseline": baseline,
        "corrected": corrected,
        "improvement_vs_baseline": {
            key: _improvement(baseline[key], corrected[key]) for key in baseline
        },
    }


def _variant_decision(variant: dict[str, Any], best_control: float) -> dict[str, Any]:
    full = variant["improvement_vs_baseline"]["full_known"]["mae_improvement_mev"]
    validation = variant["improvement_vs_baseline"]["validation_holdout"]["mae_improvement_mev"]
    margin = round(float(full - best_control), 6)
    return {
        "candidate_full_known_mae_improvement_mev": full,
        "candidate_validation_holdout_mae_improvement_mev": validation,
        "candidate_minus_best_control_full_known_mae_improvement_mev": margin,
        "survival_margin_clears": margin >= SURVIVAL_MARGIN_MEV,
        "validation_holdout_regresses": validation < 0.0,
    }


def _unchanged_control_ledger() -> dict[str, Any]:
    metrics_path = REPO_ROOT / "agent_runs" / "AGENT-RUN-0067" / "metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    ledger = metrics["control_ledger"]
    return {
        "source": "agent_runs/AGENT-RUN-0067/metrics.json",
        "controls_reused_because_inputs_unchanged": True,
        "best_control_id": ledger["best_control_id"],
        "best_control_full_known_mae_improvement_mev": ledger[
            "best_control_full_known_mae_improvement_mev"
        ],
        "control_full_known_improvements_mev": {
            key: value["full_known_mae_improvement_mev"]
            for key, value in ledger["control_full_known_improvements_mev"].items()
        },
    }


def _classify_outcome(variants: dict[str, Any]) -> dict[str, Any]:
    clearing = [
        variant_id
        for variant_id, variant in variants.items()
        if variant["decision"]["survival_margin_clears"]
        and not variant["decision"]["validation_holdout_regresses"]
    ]
    only_variants = {
        key: value for key, value in variants.items() if key.startswith("only_")
    }
    best_only_id, best_only = max(
        only_variants.items(),
        key=lambda item: item[1]["decision"]["candidate_full_known_mae_improvement_mev"],
    )
    full = variants["full_f2_reference"]["decision"]
    if clearing:
        classification = "COMPONENT_SURVIVES_MARGIN"
    elif best_only["decision"]["candidate_full_known_mae_improvement_mev"] > 0.0:
        classification = "COMPONENT_DIAGNOSTIC_ONLY"
    elif full["candidate_full_known_mae_improvement_mev"] > 0.0:
        classification = "AGGREGATE_FRAGILE"
    else:
        classification = "DO_NOT_PROMOTE"

    return {
        "classification": classification,
        "clearing_variants": clearing,
        "best_single_component_variant": best_only_id,
        "best_single_component_full_known_improvement_mev": best_only["decision"][
            "candidate_full_known_mae_improvement_mev"
        ],
        "full_reference_full_known_improvement_mev": full[
            "candidate_full_known_mae_improvement_mev"
        ],
        "interpretation": _interpretation(classification, best_only_id),
    }


def _interpretation(classification: str, best_only_id: str) -> str:
    if classification == "COMPONENT_SURVIVES_MARGIN":
        return "At least one bounded F2 component clears the predeclared survival margin."
    if classification == "COMPONENT_DIAGNOSTIC_ONLY":
        return (
            f"{best_only_id} carries useful diagnostic signal, but no ablation variant "
            "clears the predeclared controls-first survival margin."
        )
    if classification == "AGGREGATE_FRAGILE":
        return (
            "The full aggregate improves MAE, but no isolated component retains a positive "
            "diagnostic contribution."
        )
    return "The ablation slate does not preserve positive diagnostic evidence."


def render_report(metrics: dict[str, Any]) -> str:
    lines = [
        f"# {AGENT_RUN_ID} - Nuclear F2 Survival-Margin Component Ablation",
        "",
        f"**Task:** `{TASK_ID}`",
        f"**Outcome:** `{metrics['outcome']['classification']}`",
        "",
        "## Summary",
        "",
        "This run applies a predeclared component ablation to the frozen F2 finer "
        "taxonomy. It keeps the committed NMD-0003 rows, stratified split, region "
        "baseline, and controls-first survival rule unchanged. No prediction, result, "
        "claim, knowledge, or discovery wording is created.",
        "",
        "## Decision",
        "",
        f"- Classification: `{metrics['outcome']['classification']}`.",
        f"- Best single-component variant: `{metrics['outcome']['best_single_component_variant']}` "
        f"with `{metrics['outcome']['best_single_component_full_known_improvement_mev']}` MeV "
        "full-known MAE improvement.",
        f"- Full F2 reference improvement: "
        f"`{metrics['outcome']['full_reference_full_known_improvement_mev']}` MeV.",
        f"- Interpretation: {metrics['outcome']['interpretation']}",
        "",
        "## Variant Slate",
        "",
        "| variant | active components | validation improvement | full-known improvement | margin clears |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for variant_id, variant in metrics["variants"].items():
        decision = variant["decision"]
        components = ", ".join(variant["active_components"]) or "none"
        lines.append(
            f"| `{variant_id}` | {components} | "
            f"`{decision['candidate_validation_holdout_mae_improvement_mev']}` | "
            f"`{decision['candidate_full_known_mae_improvement_mev']}` | "
            f"`{decision['survival_margin_clears']}` |"
        )
    lines.extend(["", _routing_text(metrics), ""])
    return "\n".join(lines)


def render_review(metrics: dict[str, Any]) -> str:
    return render_report(metrics).replace(
        f"# {AGENT_RUN_ID} - Nuclear F2 Survival-Margin Component Ablation",
        "# Nuclear F2 Survival-Margin Component Ablation",
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


if __name__ == "__main__":
    raise SystemExit(main())
