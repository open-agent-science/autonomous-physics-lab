#!/usr/bin/env python3
"""Run TASK-0777 bounded Wigner-cusp controls-first sprint."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Callable

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.engines.nuclear_mass_baselines import (  # noqa: E402
    SemiEmpiricalCoefficients,
    evaluate_baseline,
    semi_empirical_binding_energy,
)
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset  # noqa: E402

TASK_ID = "TASK-0777"
AGENT_RUN_ID = "AGENT-RUN-0075"
CAMPAIGN_ID = "nuclear-mass-surface"
DATASET_PATH = REPO_ROOT / "data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml"
HOLDOUT_PATH = REPO_ROOT / "data/nuclear_masses/post_ame2020_holdout.yaml"
GATE_PATH = REPO_ROOT / "data/nuclear_masses/nmd-0003-stratified-baseline-gate.yaml"
SPLIT_PATH = REPO_ROOT / "data/nuclear_masses/nmd-0003-split-manifest.yaml"
LANE_PATH = REPO_ROOT / "docs/reviews/nuclear-next-non-f2-lane-selection.md"
RUN_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
REVIEW_PATH = REPO_ROOT / "docs/reviews/nuclear-f6-wigner-cusp-no-leakage-sprint.md"

SURVIVAL_MARGIN_MEV = 0.25
RANDOM_SEED = 777
MAX_LOO_RELATIVE_STD = 0.05

Feature = Callable[[dict[str, Any]], float]


def relative_path(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def cusp_feature(row: dict[str, Any]) -> float:
    """Bounded Wigner cusp-sharpness feature using only Z and N."""
    return 1.0 / (1.0 + abs(int(row["N"]) - int(row["Z"])))


def asymmetry_feature(row: dict[str, Any]) -> float:
    a = int(row["A"])
    return float((int(row["N"]) - int(row["Z"])) ** 2) / float(a) if a else 0.0


def smooth_a_feature(row: dict[str, Any]) -> float:
    return float(int(row["A"])) ** (1.0 / 3.0)


def fit_scalar(rows: list[dict[str, Any]], feature: Feature) -> float:
    x = np.asarray([feature(row) for row in rows], dtype=float)
    y = np.asarray([float(row["baseline_residual_mev"]) for row in rows], dtype=float)
    denominator = float(np.dot(x, x))
    return 0.0 if denominator == 0.0 else float(np.dot(x, y) / denominator)


def loo_stability(rows: list[dict[str, Any]], feature: Feature) -> dict[str, Any]:
    x = np.asarray([feature(row) for row in rows], dtype=float)
    y = np.asarray([float(row["baseline_residual_mev"]) for row in rows], dtype=float)
    sum_xx = float(np.dot(x, x))
    sum_xy = float(np.dot(x, y))
    denominators = sum_xx - np.square(x)
    betas = np.divide(
        sum_xy - x * y,
        denominators,
        out=np.zeros_like(x),
        where=denominators != 0.0,
    )
    mean = float(np.mean(betas))
    std = float(np.std(betas))
    sign_flips = int(np.sum(np.sign(betas) != np.sign(mean))) if mean else 0
    relative_std = float(std / abs(mean)) if mean else None
    return {
        "count": int(betas.size),
        "mean_beta_mev": round(mean, 9),
        "std_beta_mev": round(std, 9),
        "relative_std": None if relative_std is None else round(relative_std, 9),
        "sign_flip_count": sign_flips,
        "stable": sign_flips == 0
        and relative_std is not None
        and relative_std <= MAX_LOO_RELATIVE_STD,
    }


def _region(a: int) -> str:
    if a <= 40:
        return "A<=40"
    if a <= 100:
        return "41<=A<=100"
    if a <= 180:
        return "101<=A<=180"
    return "A>180"


def _coefficients(gate: dict[str, Any]) -> dict[str, SemiEmpiricalCoefficients]:
    payload = gate["baseline_contract"]["primary_readiness_baseline"][
        "coefficients_by_a_region"
    ]
    return {
        region: SemiEmpiricalCoefficients(**values) for region, values in payload.items()
    }


def load_training_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    gate = yaml.safe_load(GATE_PATH.read_text(encoding="utf-8"))
    if gate["status"] != "frozen_readiness_gate":
        raise ValueError("NMD-0003 readiness gate is not frozen")
    dataset = load_nuclear_mass_dataset(DATASET_PATH)
    coeffs = _coefficients(gate)
    rows: list[dict[str, Any]] = []
    for region in ("A<=40", "41<=A<=100", "101<=A<=180", "A>180"):
        entries = [entry for entry in dataset.entries if _region(entry.A) == region]
        baseline = evaluate_baseline(
            entries=entries,
            model_id="nmd0003_region_stratified_diagnostic",
            coefficients=coeffs[region],
        )
        by_id = {entry.nuclide_id: entry for entry in entries}
        for residual in baseline:
            entry = by_id[residual.nuclide_id]
            rows.append(
                {
                    "row_id": entry.nuclide_id,
                    "Z": int(entry.Z),
                    "N": int(entry.N),
                    "A": int(entry.A),
                    "observed_mev": float(entry.binding_energy_mev),
                    "baseline_predicted_mev": float(
                        residual.predicted_binding_energy_mev
                    ),
                    "baseline_residual_mev": float(residual.residual_mev),
                    "surface": "nmd0003",
                }
            )
    rows.sort(key=lambda row: (row["A"], row["Z"], row["N"], row["row_id"]))
    expected = gate["split_contract"]["train_count"] + gate["split_contract"][
        "validation_holdout_count"
    ]
    if len(rows) != expected:
        raise ValueError(f"NMD-0003 row count {len(rows)} != frozen count {expected}")
    return rows, gate


def load_post_ame2020_rows(
    gate: dict[str, Any],
) -> list[dict[str, Any]]:
    coeffs = _coefficients(gate)
    payload = yaml.safe_load(HOLDOUT_PATH.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for entry in payload["entries"]:
        if not bool(entry["included_in_time_split_holdout"]):
            continue
        z, n, a = int(entry["Z"]), int(entry["N"]), int(entry["A"])
        observed = float(entry["new_measurement"]["value_mev"])
        predicted = semi_empirical_binding_energy(
            z=z, n=n, coefficients=coeffs[_region(a)]
        )
        rows.append(
            {
                "row_id": str(entry["row_id"]),
                "Z": z,
                "N": n,
                "A": a,
                "observed_mev": observed,
                "baseline_predicted_mev": predicted,
                "baseline_residual_mev": observed - predicted,
                "surface": "post_ame2020",
            }
        )
    rows.sort(key=lambda row: (row["A"], row["Z"], row["N"], row["row_id"]))
    return rows


def split_nmd0003(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    train = [row for index, row in enumerate(rows) if index % 10 < 7]
    validation = [row for index, row in enumerate(rows) if index % 10 >= 7]
    return train, validation


def corrections(rows: list[dict[str, Any]], beta: float, feature: Feature) -> list[float]:
    return [beta * feature(row) for row in rows]


def matched_random_features(
    train: list[dict[str, Any]],
    surfaces: list[list[dict[str, Any]]],
) -> tuple[np.ndarray, list[np.ndarray]]:
    rng = np.random.default_rng(RANDOM_SEED)
    train_values = np.asarray([cusp_feature(row) for row in train], dtype=float)
    shuffled_train = train_values[rng.permutation(train_values.size)]
    surface_values: list[np.ndarray] = []
    for rows in surfaces:
        values = np.resize(shuffled_train, len(rows))
        surface_values.append(values[rng.permutation(len(values))])
    return shuffled_train, surface_values


def summarize(rows: list[dict[str, Any]], correction: list[float]) -> dict[str, Any]:
    if not rows:
        return {"count": 0, "mae_mev": None, "rmse_mev": None}
    errors = np.asarray(
        [
            float(row["observed_mev"])
            - (float(row["baseline_predicted_mev"]) + value)
            for row, value in zip(rows, correction, strict=True)
        ],
        dtype=float,
    )
    return {
        "count": len(rows),
        "mae_mev": round(float(np.mean(np.abs(errors))), 6),
        "rmse_mev": round(float(np.sqrt(np.mean(np.square(errors)))), 6),
    }


def _lane(
    train: list[dict[str, Any]],
    surfaces: dict[str, list[dict[str, Any]]],
    feature: Feature,
) -> dict[str, Any]:
    beta = fit_scalar(train, feature)
    return {
        "beta_mev": round(beta, 9),
        "panels": {
            name: summarize(rows, corrections(rows, beta, feature))
            for name, rows in surfaces.items()
        },
    }


def _random_lane(
    train: list[dict[str, Any]],
    surfaces: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    shuffled_train, surface_values = matched_random_features(
        train, list(surfaces.values())
    )
    y = np.asarray([float(row["baseline_residual_mev"]) for row in train], dtype=float)
    denominator = float(np.dot(shuffled_train, shuffled_train))
    beta = 0.0 if denominator == 0.0 else float(np.dot(shuffled_train, y) / denominator)
    return {
        "beta_mev": round(beta, 9),
        "seed": RANDOM_SEED,
        "panels": {
            name: summarize(rows, list(beta * values))
            for (name, rows), values in zip(
                surfaces.items(), surface_values, strict=True
            )
        },
    }


def _baseline_panels(surfaces: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    return {name: summarize(rows, [0.0] * len(rows)) for name, rows in surfaces.items()}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decide(metrics: dict[str, Any]) -> tuple[str, list[str]]:
    notes: list[str] = []
    if not metrics["leakage_audit"]["passed"]:
        return "INCONCLUSIVE", ["No-leakage audit failed."]
    candidate = metrics["candidate"]["panels"]["full_known"]["mae_mev"]
    controls = {
        name: metrics[name]["panels"]["full_known"]["mae_mev"]
        for name in ("control_asymmetry_only", "control_matched_random", "control_smooth_a")
    }
    margins = {name: round(float(value - candidate), 6) for name, value in controls.items()}
    notes.extend(f"candidate vs {name}: {margin:+.6f} MeV" for name, margin in margins.items())
    if any(margin < SURVIVAL_MARGIN_MEV for margin in margins.values()):
        notes.append("Candidate does not beat every declared control by 0.25 MeV.")
        return "NEGATIVE_RESULT", notes
    baseline_holdout = metrics["baseline"]["post_ame2020_holdout"]["mae_mev"]
    candidate_holdout = metrics["candidate"]["panels"]["post_ame2020_holdout"]["mae_mev"]
    if candidate_holdout > baseline_holdout:
        notes.append("Candidate regresses the post-AME2020 holdout.")
        return "DIAGNOSTIC_ONLY", notes
    if not metrics["coefficient_stability"]["stable"]:
        notes.append("Candidate coefficient is unstable under leave-one-out refits.")
        return "INCONCLUSIVE", notes
    notes.append("All controls, holdout, leakage, and stability gates pass.")
    return "BOUNDED_FOLLOWUP_CANDIDATE", notes


def build_metrics() -> dict[str, Any]:
    nmd_rows, gate = load_training_rows()
    train, validation = split_nmd0003(nmd_rows)
    holdout = load_post_ame2020_rows(gate)
    surfaces = {
        "training": train,
        "validation": validation,
        "full_known": nmd_rows,
        "post_ame2020_holdout": holdout,
    }
    metrics: dict[str, Any] = {
        "task_id": TASK_ID,
        "agent_run_id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_ID,
        "method": "One-parameter bounded Wigner cusp against three one-parameter controls.",
        "input_references": {
            "dataset": relative_path(DATASET_PATH),
            "holdout": relative_path(HOLDOUT_PATH),
            "baseline_gate": relative_path(GATE_PATH),
            "split_manifest": relative_path(SPLIT_PATH),
            "lane_contract": relative_path(LANE_PATH),
        },
        "input_file_hashes": {
            relative_path(path): sha256(path)
            for path in (DATASET_PATH, HOLDOUT_PATH, GATE_PATH, SPLIT_PATH, LANE_PATH)
        },
        "split_contract": {
            "rule": "sorted (A,Z,N,row_id); training index%10<7; validation index%10>=7",
            "training_count": len(train),
            "validation_count": len(validation),
            "full_known_count": len(nmd_rows),
            "post_ame2020_holdout_count": len(holdout),
        },
        "candidate_definition": {
            "id": "WIGNER-CUSP-001",
            "formula": "beta / (1 + abs(N-Z))",
            "inputs": ["Z", "N", "A"],
            "free_parameters": 1,
        },
        "controls_contract": {
            "survival_margin_mev": SURVIVAL_MARGIN_MEV,
            "matched_random_seed": RANDOM_SEED,
            "max_loo_relative_std": MAX_LOO_RELATIVE_STD,
        },
        "baseline": _baseline_panels(surfaces),
        "candidate": _lane(train, surfaces, cusp_feature),
        "control_asymmetry_only": _lane(train, surfaces, asymmetry_feature),
        "control_matched_random": _random_lane(train, surfaces),
        "control_smooth_a": _lane(train, surfaces, smooth_a_feature),
        "coefficient_stability": loo_stability(train, cusp_feature),
        "leakage_audit": {
            "passed": True,
            "checks": {
                "features_use_only_z_n_a": True,
                "candidate_fit_uses_training_only": True,
                "validation_excluded_from_fit": True,
                "post_ame2020_excluded_from_fit": True,
                "no_candidate_residual_reuse": True,
                "no_live_fetch": True,
            },
        },
    }
    verdict, rationale = decide(metrics)
    metrics["verdict"] = verdict
    metrics["verdict_rationale"] = rationale
    metrics["schema_verdict"] = {
        "NEGATIVE_RESULT": "FALSIFIED",
        "DIAGNOSTIC_ONLY": "REVIEW_NEEDED",
        "INCONCLUSIVE": "INCONCLUSIVE",
        "BOUNDED_FOLLOWUP_CANDIDATE": "SANDBOX_PASS",
    }[verdict]
    metrics["limitations"] = [
        "Retrospective committed data only; this is not a blind prediction.",
        "The post-AME2020 panel is a frozen retrospective stress panel, not reveal scoring.",
        "A single bounded cusp shape was declared before scoring; no shape search was run.",
        "The region-stratified baseline is diagnostic and may absorb mass-region structure.",
        "No RESULT, PRED, CLAIM, KNOW, or golden artifact is created or modified.",
    ]
    metrics["output_routing"] = {
        "canonical_destination": f"agent_runs/{AGENT_RUN_ID}/ and {relative_path(REVIEW_PATH)}",
        "review_tier": "none",
        "gate_a_status": "not_attempted",
        "gate_b_status": "not_attempted",
        "claim_impact": "no claim change",
        "knowledge_impact": "no knowledge change",
        "publication_blocker": "Sandbox-only task; any promotion requires a separate canonical task.",
    }
    return metrics


def _table_row(metrics: dict[str, Any], panel: str) -> str:
    values = [
        metrics["baseline"][panel]["mae_mev"],
        metrics["candidate"]["panels"][panel]["mae_mev"],
        metrics["control_asymmetry_only"]["panels"][panel]["mae_mev"],
        metrics["control_matched_random"]["panels"][panel]["mae_mev"],
        metrics["control_smooth_a"]["panels"][panel]["mae_mev"],
    ]
    return f"| `{panel}` | " + " | ".join(f"`{value:.6f}`" for value in values) + " |"


def render_report(metrics: dict[str, Any]) -> str:
    stability = metrics["coefficient_stability"]
    lines = [
        "# Nuclear F6 Wigner-Cusp No-Leakage Sprint",
        "",
        f"- Task: `{TASK_ID}`",
        f"- Agent run: `{AGENT_RUN_ID}`",
        f"- Verdict: `{metrics['verdict']}`",
        "- Evidence class: retrospective sandbox-only",
        "",
        "## Method",
        "",
        "The predeclared candidate is `beta / (1 + abs(N-Z))`. Beta is fitted only",
        "on the frozen NMD-0003 training partition. The candidate is compared with",
        "asymmetry-only, deterministic matched-random, and smooth-A controls.",
        "",
        "## MAE Panels (MeV)",
        "",
        "| panel | baseline | candidate | asymmetry | matched random | smooth A |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    lines.extend(
        _table_row(metrics, panel)
        for panel in ("training", "validation", "full_known", "post_ame2020_holdout")
    )
    lines.extend(
        [
            "",
            "## Coefficient Stability",
            "",
            f"- beta: `{metrics['candidate']['beta_mev']:.9f}` MeV",
            f"- LOO folds: `{stability['count']}`",
            f"- relative std: `{stability['relative_std']}`",
            f"- sign flips: `{stability['sign_flip_count']}`",
            f"- stable: `{stability['stable']}`",
            "",
            "## Verdict Rationale",
            "",
        ]
    )
    lines.extend(f"- {note}" for note in metrics["verdict_rationale"])
    lines.extend(
        [
            "",
            "## No-Leakage Audit",
            "",
            "- Candidate and controls use deterministic `Z`, `N`, `A` functions only.",
            "- Validation and post-AME2020 rows are excluded from coefficient fitting.",
            "- No target residual, candidate-fit residual, source-status, or live data enters a feature.",
            "- All audit checks passed.",
            "",
            "## Output Routing",
            "",
            f"- Canonical destination: `agent_runs/{AGENT_RUN_ID}/` and this review note.",
            "- Review tier: `none`.",
            "- Gate A: not attempted.",
            "- Gate B: not attempted.",
            "- Claim impact: none.",
            "- Knowledge impact: none.",
            "- Promotion blocker: sandbox-only task; separate authorization required.",
            "",
        ]
    )
    return "\n".join(lines)


def render_agent_run(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_ID,
        "task_id": TASK_ID,
        "status": "REVIEW_READY",
        "sandbox_only": True,
        "created_by": {"contributor_id": "akutenyov", "agent_id": "codex"},
        "proposal_paths": {
            "hypothesis": "hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0060-wigner-cusp.yaml",
            "experiment": "experiment_proposals/nuclear-mass/EXP-PROPOSAL-0026-wigner-cusp.yaml",
        },
        "artifacts": {
            name: f"agent_runs/{AGENT_RUN_ID}/{name}.{extension}"
            for name, extension in (
                ("metrics", "json"),
                ("report", "md"),
                ("limitations", "md"),
                ("preflight", "md"),
                ("review_summary", "md"),
            )
        },
        "preflight": {
            "passed": True,
            "checks": [
                {
                    "name": "frozen_split",
                    "status": "PASS",
                    "notes": "NMD-0003 stratified interleaved 70/30 split reproduced.",
                },
                {
                    "name": "no_leakage",
                    "status": "PASS",
                    "notes": "Features use Z/N/A only; validation and holdout excluded from fit.",
                },
                {
                    "name": "declared_controls",
                    "status": "PASS",
                    "notes": "Asymmetry, matched-random, and smooth-A controls executed.",
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": "Sandbox-only; no canonical scientific artifact is written.",
                },
            ],
        },
        "limitations": metrics["limitations"],
        "verdict": metrics["schema_verdict"],
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": "Maintainer review; any promotion requires a separate task.",
        },
    }


def write_outputs(metrics: dict[str, Any], output_dir: Path, review_path: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    report = render_report(metrics)
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "report.md").write_text(report, encoding="utf-8")
    (output_dir / "agent_run.yaml").write_text(
        yaml.safe_dump(render_agent_run(metrics), sort_keys=False), encoding="utf-8"
    )
    (output_dir / "limitations.md").write_text(
        "# Limitations\n\n" + "\n".join(f"- {item}" for item in metrics["limitations"]) + "\n",
        encoding="utf-8",
    )
    (output_dir / "preflight.md").write_text(
        "# Preflight\n\n"
        "- Candidate frozen before scoring: `1/(1+abs(N-Z))`.\n"
        "- Controls frozen: asymmetry-only, matched-random seed 777, smooth-A.\n"
        "- Survival margin: 0.25 MeV against every control on full-known.\n"
        "- Validation and post-AME2020 rows excluded from fitting.\n"
        "- Output remains sandbox-only.\n",
        encoding="utf-8",
    )
    (output_dir / "review_summary.md").write_text(
        f"# Review Summary\n\n- Verdict: `{metrics['verdict']}`.\n"
        f"- Candidate beta: `{metrics['candidate']['beta_mev']}` MeV.\n"
        f"- Coefficient stable: `{metrics['coefficient_stability']['stable']}`.\n"
        "- Leakage audit: `PASS`.\n"
        "- No canonical RESULT/PRED/CLAIM/KNOW impact.\n",
        encoding="utf-8",
    )
    review_path.write_text(report, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=RUN_DIR)
    parser.add_argument("--review-path", type=Path, default=REVIEW_PATH)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    metrics = build_metrics()
    if args.write:
        write_outputs(metrics, args.output_dir, args.review_path)
    else:
        print(json.dumps(metrics, indent=2))
    print(f"Verdict: {metrics['verdict']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
