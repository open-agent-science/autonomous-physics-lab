#!/usr/bin/env python3
"""Run TASK-0595 NMD-0003 isotope-chain transfer residual sprint."""

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

TASK_ID = "TASK-0595"
AGENT_RUN_ID = "AGENT-RUN-0063"
DATASET_PATH = REPO_ROOT / "data" / "nuclear_masses" / "nmd-0003-ame2020-measured-training.yaml"
GATE_PATH = REPO_ROOT / "data" / "nuclear_masses" / "nmd-0003-stratified-baseline-gate.yaml"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
DEFAULT_REVIEW_PATH = (
    REPO_ROOT / "docs" / "reviews" / "nmd0003-isotope-chain-transfer-sprint.md"
)

CHAIN_MIN_ROWS = 3
SURVIVAL_MARGIN_MEV = 0.25
RANDOM_SEED = 595


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

    metrics = run_isotope_transfer_sprint()
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "report.md").write_text(render_report(metrics), encoding="utf-8")
    review_path.write_text(render_review(metrics), encoding="utf-8")
    print(f"NMD-0003 isotope-transfer sprint complete: {output_dir / 'metrics.json'}")
    print(f"Verdict: {metrics['verdict']}")
    return 0


def run_isotope_transfer_sprint() -> dict[str, Any]:
    dataset = load_nuclear_mass_dataset(DATASET_PATH)
    entries = sorted(
        dataset.entries, key=lambda entry: (entry.A, entry.Z, entry.N, entry.nuclide_id)
    )
    gate = yaml.safe_load(GATE_PATH.read_text(encoding="utf-8"))
    _assert_contract(gate, entries)

    train_entries, validation_entries = _stratified_split(entries)
    rows_by_id = {
        row.nuclide_id: row for row in _region_stratified_baseline_rows(entries, gate)
    }
    feature_builders: dict[str, Callable[[list[NuclearMassEntry]], dict[str, float]]] = {
        "candidate_neutron_excess_curvature_transfer": _neutron_excess_curvature_feature,
        "matched_random_chain": _matched_random_chain_feature,
        "sign_inverted": _sign_inverted_feature,
        "label_shuffle": _label_shuffle_feature,
    }
    lanes = {
        lane_id: _score_feature_lane(
            entries=entries,
            train_entries=train_entries,
            validation_entries=validation_entries,
            rows_by_id=rows_by_id,
            feature_builder=builder,
        )
        for lane_id, builder in feature_builders.items()
    }
    candidate = lanes["candidate_neutron_excess_curvature_transfer"]
    controls = {
        key: value
        for key, value in lanes.items()
        if key != "candidate_neutron_excess_curvature_transfer"
    }
    chain_panels = _chain_panels(
        validation_entries=validation_entries,
        rows_by_id=rows_by_id,
        lanes=lanes,
    )
    transfer = _transfer_summary(chain_panels)
    best_control_validation = max(
        control["improvement_vs_baseline"]["validation_holdout"]["mae_improvement_mev"]
        for control in controls.values()
    )
    candidate_validation = candidate["improvement_vs_baseline"]["validation_holdout"][
        "mae_improvement_mev"
    ]
    validation_margin = round(float(candidate_validation - best_control_validation), 6)
    verdict = _verdict(
        candidate_validation=candidate_validation,
        validation_margin=validation_margin,
        transfer=transfer,
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
            "validation_isotope_chain_count": len(_group_by_chain(validation_entries)),
            "interpretable_validation_chain_min_rows": CHAIN_MIN_ROWS,
        },
        "input_references": {
            "stratified_gate": _rel(GATE_PATH),
            "task0583_replay": "docs/reviews/nmd0003-stratified-gate-independent-replay.md",
            "high_error_cluster_review": (
                "docs/reviews/nuclear-high-error-cluster-adversarial-stability.md"
            ),
            "gauntlet": "docs/notes/nuclear-controls-first-hypothesis-gauntlet.md",
        },
        "selected_feature_family": {
            "family_id": "neutron_excess_curvature_transfer",
            "feature": "((N-Z)/A)^2 * A^(1/3), standardized on frozen train split",
            "expected_transfer_mechanism": (
                "Neutron-excess curvature is a smooth row-local structural term "
                "defined only from Z, N, and A, so any real residual signal should "
                "show up across multiple isotope chains rather than only one chain."
            ),
            "coefficient_policy": (
                "single non-negative least-squares coefficient on the frozen "
                "stratified train split; sign-inverted control tests the opposite "
                "direction under the same non-negative policy"
            ),
            "forbidden_inputs_excluded": [
                "source_status",
                "measured_or_extrapolated_flags",
                "target_row_labels",
                "post_ame2020_values",
                "baseline_residual_quantile_labels",
            ],
        },
        "baseline_contract": {
            "primary_readiness_baseline": gate["baseline_contract"][
                "primary_readiness_baseline"
            ]["baseline_id"],
            "split_id": gate["split_contract"]["primary_readiness_split_id"],
            "post_ame2020_holdout_scoring_allowed": False,
        },
        "lanes_primary_readiness_baseline": _strip_feature_values(lanes),
        "isotope_chain_transfer": {
            "summary": transfer,
            "chain_panels": chain_panels,
        },
        "decision": {
            "candidate_validation_mae_improvement_mev": round(float(candidate_validation), 6),
            "best_control_validation_mae_improvement_mev": round(
                float(best_control_validation), 6
            ),
            "candidate_minus_best_control_validation_mae_improvement_mev": validation_margin,
            "survival_margin_mev": SURVIVAL_MARGIN_MEV,
            "validation_margin_clears": validation_margin >= SURVIVAL_MARGIN_MEV,
            "validation_holdout_regresses": candidate_validation < 0.0,
        },
        "verdict": verdict,
        "limitations": [
            "One bounded transfer feature family only; no broad factory search.",
            "Transfer panels use committed AME2020 measured rows under the frozen split only.",
            "No source-status, row-role, target-label, or post-AME2020 values are features.",
            "No PRED, RESULT, CLAIM, KNOW, or discovery artifact is created.",
        ],
        "output_routing": {
            "task_verdict": verdict,
            "canonical_destination": [
                f"agent_runs/{AGENT_RUN_ID}/metrics.json",
                f"agent_runs/{AGENT_RUN_ID}/report.md",
                "docs/reviews/nmd0003-isotope-chain-transfer-sprint.md",
            ],
            "review_tier": "none",
            "gate_a_status": "not_attempted",
            "gate_b_status": "not_applicable",
            "claim_impact": "none",
            "knowledge_impact": "none",
            "result_impact": "no RESULT artifact created",
        },
    }


def _assert_contract(gate: dict[str, Any], entries: list[NuclearMassEntry]) -> None:
    if gate["status"] != "frozen_readiness_gate":
        raise ValueError("NMD-0003 stratified baseline gate is not frozen.")
    if gate["source_dataset"] != _rel(DATASET_PATH):
        raise ValueError("Gate source dataset does not match TASK-0595 dataset.")
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
    beta = _fit_nonnegative_beta(train_rows, features)
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
        "standardized_features": {key: round(float(value), 12) for key, value in features.items()},
        "baseline": baseline,
        "corrected": corrected_summary,
        "improvement_vs_baseline": {
            key: _improvement(baseline[key], corrected_summary[key]) for key in baseline
        },
    }


def _strip_feature_values(lanes: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        lane_id: {key: value for key, value in lane.items() if key != "standardized_features"}
        for lane_id, lane in lanes.items()
    }


def _fit_nonnegative_beta(
    rows: list[BaselineResidualRow], features: dict[str, float]
) -> float:
    x = np.asarray([features[row.nuclide_id] for row in rows], dtype=float)
    y = np.asarray([row.residual_mev for row in rows], dtype=float)
    denom = float(np.dot(x, x))
    if denom == 0.0:
        return 0.0
    return max(0.0, float(np.dot(x, y) / denom))


def _standardize_features(
    raw: dict[str, float], train_entries: list[NuclearMassEntry]
) -> dict[str, float]:
    train_values = np.asarray([raw[entry.nuclide_id] for entry in train_entries], dtype=float)
    mean = float(np.mean(train_values))
    std = float(np.std(train_values))
    if std == 0.0:
        return {key: 0.0 for key in raw}
    return {key: (float(value) - mean) / std for key, value in raw.items()}


def _neutron_excess_curvature_feature(
    entries: list[NuclearMassEntry],
) -> dict[str, float]:
    return {
        entry.nuclide_id: (((entry.N - entry.Z) / float(entry.A)) ** 2)
        * (float(entry.A) ** (1.0 / 3.0))
        for entry in entries
    }


def _matched_random_chain_feature(entries: list[NuclearMassEntry]) -> dict[str, float]:
    base = _neutron_excess_curvature_feature(entries)
    rng = random.Random(RANDOM_SEED)
    out: dict[str, float] = {}
    for chain_entries in _group_by_chain(entries).values():
        values = [base[entry.nuclide_id] for entry in chain_entries]
        rng.shuffle(values)
        for entry, value in zip(chain_entries, values, strict=True):
            out[entry.nuclide_id] = value
    return out


def _sign_inverted_feature(entries: list[NuclearMassEntry]) -> dict[str, float]:
    base = _neutron_excess_curvature_feature(entries)
    return {key: -value for key, value in base.items()}


def _label_shuffle_feature(entries: list[NuclearMassEntry]) -> dict[str, float]:
    base = _neutron_excess_curvature_feature(entries)
    rng = random.Random(RANDOM_SEED + 1)
    out: dict[str, float] = {}
    for region in ("A<=40", "41<=A<=100", "101<=A<=180", "A>180"):
        region_entries = [entry for entry in entries if _a_region(entry.A) == region]
        values = [base[entry.nuclide_id] for entry in region_entries]
        rng.shuffle(values)
        for entry, value in zip(region_entries, values, strict=True):
            out[entry.nuclide_id] = value
    return out


def _chain_panels(
    *,
    validation_entries: list[NuclearMassEntry],
    rows_by_id: dict[str, BaselineResidualRow],
    lanes: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    panels: list[dict[str, Any]] = []
    for chain_id, chain_entries in _group_by_chain(validation_entries).items():
        baseline_residuals = [
            rows_by_id[entry.nuclide_id].residual_mev for entry in chain_entries
        ]
        baseline = _summary(baseline_residuals)
        lane_items = {}
        for lane_id, lane in lanes.items():
            beta = float(lane["coefficient_mev_per_standardized_feature"])
            features = lane["standardized_features"]
            corrected = [
                rows_by_id[entry.nuclide_id].residual_mev
                - beta * float(features[entry.nuclide_id])
                for entry in chain_entries
            ]
            corrected_summary = _summary(corrected)
            lane_items[lane_id] = {
                "corrected_mae_mev": corrected_summary["mae_mev"],
                "corrected_rmse_mev": corrected_summary["rmse_mev"],
                "mae_improvement_mev": _improvement(baseline, corrected_summary)[
                    "mae_improvement_mev"
                ],
            }
        candidate_improvement = lane_items[
            "candidate_neutron_excess_curvature_transfer"
        ]["mae_improvement_mev"]
        best_control = max(
            item["mae_improvement_mev"]
            for key, item in lane_items.items()
            if key != "candidate_neutron_excess_curvature_transfer"
        )
        panels.append(
            {
                "chain_id": chain_id,
                "Z": chain_entries[0].Z,
                "row_count": len(chain_entries),
                "A_min": min(entry.A for entry in chain_entries),
                "A_max": max(entry.A for entry in chain_entries),
                "diagnostic_class": (
                    "interpretable" if len(chain_entries) >= CHAIN_MIN_ROWS else "too_sparse"
                ),
                "baseline_mae_mev": baseline["mae_mev"],
                "baseline_rmse_mev": baseline["rmse_mev"],
                "lanes": lane_items,
                "candidate_minus_best_control_mae_improvement_mev": round(
                    float(candidate_improvement - best_control), 6
                ),
            }
        )
    return panels


def _transfer_summary(chain_panels: list[dict[str, Any]]) -> dict[str, Any]:
    interpretable = [
        panel for panel in chain_panels if panel["diagnostic_class"] == "interpretable"
    ]
    candidate_key = "candidate_neutron_excess_curvature_transfer"
    improved = [
        panel
        for panel in interpretable
        if panel["lanes"][candidate_key]["mae_improvement_mev"] > 0.0
    ]
    regressed = [
        panel
        for panel in interpretable
        if panel["lanes"][candidate_key]["mae_improvement_mev"] < 0.0
    ]
    beat_controls = [
        panel
        for panel in interpretable
        if panel["candidate_minus_best_control_mae_improvement_mev"] > 0.0
    ]
    total = len(interpretable)
    return {
        "interpretable_chain_count": total,
        "too_sparse_chain_count": len(chain_panels) - total,
        "candidate_improved_chain_count": len(improved),
        "candidate_regressed_chain_count": len(regressed),
        "candidate_beat_controls_chain_count": len(beat_controls),
        "candidate_improvement_rate": len(improved) / total if total else None,
        "candidate_control_survival_rate": len(beat_controls) / total if total else None,
        "required_minimum_interpretable_chains": 3,
    }


def _group_by_chain(
    entries: list[NuclearMassEntry],
) -> dict[str, list[NuclearMassEntry]]:
    grouped: dict[str, list[NuclearMassEntry]] = {}
    for entry in entries:
        grouped.setdefault(f"Z_{entry.Z:03d}", []).append(entry)
    return dict(sorted(grouped.items(), key=lambda item: item[0]))


def _summary(residuals: list[float]) -> dict[str, float | int]:
    values = np.asarray(residuals, dtype=float)
    if values.size == 0:
        return {
            "count": 0,
            "mae_mev": 0.0,
            "rmse_mev": 0.0,
            "median_abs_residual_mev": 0.0,
            "p90_abs_residual_mev": 0.0,
            "max_abs_residual_mev": 0.0,
        }
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
    *,
    candidate_validation: float,
    validation_margin: float,
    transfer: dict[str, Any],
) -> str:
    if transfer["interpretable_chain_count"] < 3:
        return "INCONCLUSIVE"
    if candidate_validation < 0.0:
        return "NEGATIVE_RESULT"
    survival_rate = float(transfer["candidate_control_survival_rate"] or 0.0)
    improvement_rate = float(transfer["candidate_improvement_rate"] or 0.0)
    if validation_margin >= SURVIVAL_MARGIN_MEV and survival_rate >= 0.67:
        return "BOUNDED_FOLLOWUP_CANDIDATE"
    if improvement_rate > 0.0:
        return "DIAGNOSTIC_ONLY"
    return "NEGATIVE_RESULT"


def render_report(metrics: dict[str, Any]) -> str:
    decision = metrics["decision"]
    candidate = metrics["lanes_primary_readiness_baseline"][
        "candidate_neutron_excess_curvature_transfer"
    ]
    transfer = metrics["isotope_chain_transfer"]["summary"]
    lines = [
        f"# {AGENT_RUN_ID} - NMD-0003 Isotope-Chain Transfer Sprint",
        "",
        f"**Task:** `{TASK_ID}`",
        f"**Verdict:** `{metrics['verdict']}`",
        "",
        "## Summary",
        "",
        "This bounded sprint tests one row-local transfer feature family, "
        "`neutron_excess_curvature_transfer`, under the frozen NMD-0003 "
        "stratified gate. It reports isotope-chain panels separately from "
        "aggregate MAE/RMSE and writes sandbox-only evidence.",
        "",
        "## Aggregate Metrics",
        "",
        "| surface | baseline MAE | corrected MAE | MAE improvement | baseline RMSE | corrected RMSE |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for surface in ("train", "validation_holdout", "full_known"):
        lines.append(
            f"| `{surface}` | `{candidate['baseline'][surface]['mae_mev']}` | "
            f"`{candidate['corrected'][surface]['mae_mev']}` | "
            f"`{candidate['improvement_vs_baseline'][surface]['mae_improvement_mev']}` | "
            f"`{candidate['baseline'][surface]['rmse_mev']}` | "
            f"`{candidate['corrected'][surface]['rmse_mev']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision Metrics",
            "",
            f"- Candidate validation MAE improvement: "
            f"`{decision['candidate_validation_mae_improvement_mev']}` MeV.",
            f"- Best control validation MAE improvement: "
            f"`{decision['best_control_validation_mae_improvement_mev']}` MeV.",
            f"- Candidate minus best control on validation: "
            f"`{decision['candidate_minus_best_control_validation_mae_improvement_mev']}` MeV.",
            f"- Interpretable validation chains: "
            f"`{transfer['interpretable_chain_count']}`.",
            f"- Candidate improved chain count: "
            f"`{transfer['candidate_improved_chain_count']}`.",
            f"- Candidate beat-controls chain count: "
            f"`{transfer['candidate_beat_controls_chain_count']}`.",
            "",
            "## Isotope-Chain Transfer Panels",
            "",
        ]
    )
    lines.extend(_chain_table(metrics["isotope_chain_transfer"]["chain_panels"]))
    lines.extend(["", _routing_text(metrics), ""])
    return "\n".join(lines)


def render_review(metrics: dict[str, Any]) -> str:
    return render_report(metrics).replace(
        f"# {AGENT_RUN_ID} - NMD-0003 Isotope-Chain Transfer Sprint",
        "# NMD-0003 Isotope-Chain Transfer Sprint",
        1,
    )


def _chain_table(chain_panels: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| chain | rows | A range | baseline MAE | candidate improvement | candidate-control margin | class |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for panel in chain_panels:
        candidate = panel["lanes"]["candidate_neutron_excess_curvature_transfer"]
        lines.append(
            f"| `{panel['chain_id']}` | `{panel['row_count']}` | "
            f"`{panel['A_min']}-{panel['A_max']}` | `{panel['baseline_mae_mev']}` | "
            f"`{candidate['mae_improvement_mev']}` | "
            f"`{panel['candidate_minus_best_control_mae_improvement_mev']}` | "
            f"`{panel['diagnostic_class']}` |"
        )
    return lines


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
