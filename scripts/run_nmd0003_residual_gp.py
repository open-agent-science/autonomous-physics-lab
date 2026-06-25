#!/usr/bin/env python3
"""Run the TASK-0824 calibrated-uncertainty GP residual extrapolation benchmark.

Fits a deterministic Gaussian-process correction on the frozen NMD-0003 baseline
residuals over the training split only, then evaluates extrapolation accuracy and
uncertainty calibration on the post-AME2020 holdout under controls. Emits a
sandbox ``agent_runs`` package (metrics + report) and a review note.
"""

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

from physics_lab.engines.nmd0003_residual_gp import (  # noqa: E402
    BENCHMARK_ID,
    DEFAULT_DATASET_PATH,
    DEFAULT_GATE_PATH,
    DEFAULT_HOLDOUT_PATH,
    TASK_ID,
    run_nmd0003_residual_gp,
)

AGENT_RUN_ID = "AGENT-RUN-0078"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
DEFAULT_REVIEW_PATH = (
    REPO_ROOT / "docs" / "reviews" / "nmd0003-calibrated-uncertainty-gp-extrapolation.md"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--review-path", default=str(DEFAULT_REVIEW_PATH))
    parser.add_argument("--no-review", action="store_true", help="Skip writing the review note.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics = run_nmd0003_residual_gp(
        dataset_path=REPO_ROOT / DEFAULT_DATASET_PATH,
        gate_path=REPO_ROOT / DEFAULT_GATE_PATH,
        holdout_path=REPO_ROOT / DEFAULT_HOLDOUT_PATH,
    )
    metrics["agent_run_id"] = AGENT_RUN_ID

    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "report.md").write_text(render_report(metrics), encoding="utf-8")

    if not args.no_review:
        review_path = Path(args.review_path)
        review_path.parent.mkdir(parents=True, exist_ok=True)
        review_path.write_text(render_review(metrics), encoding="utf-8")

    print(f"NMD-0003 calibrated GP residual benchmark complete: {output_dir / 'metrics.json'}")
    print(f"Verdict: {metrics['verdict']}")
    print(f"Calibration verdict: {metrics['calibration_verdict']}")
    return 0


def _routing_block(metrics: dict[str, Any]) -> list[str]:
    routing = metrics["output_routing"]
    decision = metrics["decision"]
    calibration = metrics["calibration"]
    extrapolation = metrics["extrapolation"]
    return [
        "## Output-routing summary",
        "",
        f"- Task verdict: `{routing['task_verdict']}`.",
        f"- Calibration verdict: `{routing['calibration_verdict']}`.",
        "- Gate A status: mechanical conditions are met (deterministic replay, "
        "verification, input hashes, limitations, pinned engine version/commit, "
        "schema-valid, no protected rewrite, no overclaim, dataset provenance); the "
        "result is routed to SANDBOX (this agent run plus the review note) rather "
        "than a published RESULT, because linking the result into hypothesis "
        "evidence is outside this benchmark task's authorized change surface.",
        f"- Extrapolation: baseline holdout MAE "
        f"`{extrapolation['frozen_baseline_holdout']['mae_mev']}` MeV / RMS "
        f"`{extrapolation['frozen_baseline_holdout']['rms_mev']}` MeV vs GP-corrected MAE "
        f"`{extrapolation['gp_corrected_holdout']['mae_mev']}` MeV / RMS "
        f"`{extrapolation['gp_corrected_holdout']['rms_mev']}` MeV "
        f"(MAE improvement `{extrapolation['gp_mae_improvement_mev']}` MeV).",
        f"- Calibration coverage: 1 sigma "
        f"`{calibration['empirical_coverage_1sigma']}` (expected "
        f"`{calibration['expected_coverage_1sigma']}`), 2 sigma "
        f"`{calibration['empirical_coverage_2sigma']}` (expected "
        f"`{calibration['expected_coverage_2sigma']}`), RMS standardized residual "
        f"`{calibration['rms_standardized_residual']}`.",
        f"- Control-survival margin: GP minus best control "
        f"(`{decision['best_control_id']}`) MAE improvement = "
        f"`{decision['gp_minus_best_control_mae_improvement_mev']}` MeV vs predeclared "
        f"`{decision['predeclared_survival_margin_mev']}` MeV "
        f"(clears: `{decision['survival_margin_clears']}`).",
        "- Claim impact: `none` (methodology contribution; no PRED/CLAIM/KNOW/discovery).",
        "- Limitations: retrospective time-split, single dataset, single model class "
        "(RBF GP on `[Z, N]` residuals), frozen-baseline-dependent residual surface.",
    ]


def render_report(metrics: dict[str, Any]) -> str:
    gp = metrics["gp_model"]
    hp = gp["fitted_hyperparameters"]
    extrapolation = metrics["extrapolation"]
    calibration = metrics["calibration"]
    controls = metrics["controls"]
    lines = [
        f"# {metrics.get('agent_run_id', AGENT_RUN_ID)} - NMD-0003 Calibrated GP Residual Extrapolation",
        "",
        f"**Task:** `{TASK_ID}`",
        f"**Benchmark:** `{BENCHMARK_ID}`",
        f"**Verdict:** `{metrics['verdict']}`",
        f"**Calibration verdict:** `{metrics['calibration_verdict']}`",
        "",
        "## Summary",
        "",
        "A deterministic Gaussian-process correction is fit on the frozen NMD-0003 "
        f"audit baseline (`{metrics['frozen_baseline']['baseline_id']}`) residuals over "
        "the training split only (no post-AME2020 holdout leakage), then evaluated on "
        "the post-AME2020 time-split holdout for extrapolation accuracy AND uncertainty "
        "calibration. The deliverable is a calibrated residual model and its diagnostics; "
        "no prediction, claim, knowledge entry, or discovery is promoted.",
        "",
        "## Model",
        "",
        f"- Feature basis: `{', '.join(gp['feature_basis'])}` standardized on the training split.",
        f"- Kernel: `{gp['kernel']}`; hyperparameters by `{gp['hyperparameter_fit']}`.",
        f"- Fitted hyperparameters: sigma_f = `{hp['sigma_f_mev']}` MeV, length-scale = "
        f"`{hp['length_scale_standardized']}` (standardized), sigma_n = `{hp['sigma_n_mev']}` MeV.",
        f"- Training rows: `{metrics['dataset_summary']['training_row_count']}`; "
        f"holdout rows: `{metrics['dataset_summary']['holdout_primary_row_count']}`; "
        f"post-AME2020 rows used for fitting: "
        f"`{metrics['dataset_summary']['post_ame2020_rows_used_for_fitting']}`.",
        "",
        "## Extrapolation Accuracy (post-AME2020 holdout)",
        "",
        "| Model | MAE (MeV) | RMS (MeV) | median abs (MeV) | max abs (MeV) |",
        "| --- | ---: | ---: | ---: | ---: |",
        f"| Frozen baseline | `{extrapolation['frozen_baseline_holdout']['mae_mev']}` | "
        f"`{extrapolation['frozen_baseline_holdout']['rms_mev']}` | "
        f"`{extrapolation['frozen_baseline_holdout']['median_abs_mev']}` | "
        f"`{extrapolation['frozen_baseline_holdout']['max_abs_mev']}` |",
        f"| GP-corrected | `{extrapolation['gp_corrected_holdout']['mae_mev']}` | "
        f"`{extrapolation['gp_corrected_holdout']['rms_mev']}` | "
        f"`{extrapolation['gp_corrected_holdout']['median_abs_mev']}` | "
        f"`{extrapolation['gp_corrected_holdout']['max_abs_mev']}` |",
        "",
        f"GP MAE improvement over baseline: `{extrapolation['gp_mae_improvement_mev']}` MeV; "
        f"RMS improvement: `{extrapolation['gp_rms_improvement_mev']}` MeV.",
        "",
        "## Uncertainty Calibration",
        "",
        f"- Empirical 1 sigma coverage: `{calibration['empirical_coverage_1sigma']}` "
        f"(expected `{calibration['expected_coverage_1sigma']}`).",
        f"- Empirical 2 sigma coverage: `{calibration['empirical_coverage_2sigma']}` "
        f"(expected `{calibration['expected_coverage_2sigma']}`).",
        f"- RMS standardized residual: `{calibration['rms_standardized_residual']}` "
        "(well-calibrated ~ 1.0).",
        f"- Mean predictive sigma: `{calibration['mean_predictive_sigma_mev']}` MeV; "
        f"fraction beyond 2 sigma: `{calibration['fraction_beyond_2sigma']}`.",
        "",
        "## Controls-First Decision",
        "",
        "| Lane | holdout MAE (MeV) | MAE improvement vs baseline (MeV) |",
        "| --- | ---: | ---: |",
        f"| GP correction | `{extrapolation['gp_corrected_holdout']['mae_mev']}` | "
        f"`{extrapolation['gp_mae_improvement_mev']}` |",
    ]
    for control_id, control in controls.items():
        if control_id == "uncorrected_baseline":
            continue
        improvement = round(
            float(
                extrapolation["frozen_baseline_holdout"]["mae_mev"]
                - control["corrected"]["mae_mev"]
            ),
            6,
        )
        lines.append(
            f"| {control_id} | `{control['corrected']['mae_mev']}` | `{improvement}` |"
        )
    decision = metrics["decision"]
    lines.extend(
        [
            "",
            f"- Predeclared survival margin: `{decision['predeclared_survival_margin_mev']}` MeV "
            "(fixed before reading holdout scores; the established NMD-0003 bounded-sprint "
            "convention).",
            f"- Best control: `{decision['best_control_id']}` "
            f"(MAE improvement `{decision['best_control_mae_improvement_mev']}` MeV).",
            f"- GP minus best control: "
            f"`{decision['gp_minus_best_control_mae_improvement_mev']}` MeV; clears margin: "
            f"`{decision['survival_margin_clears']}`.",
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in metrics["limitations"])
    lines.extend(["", *_routing_block(metrics), ""])
    return "\n".join(lines)


def render_review(metrics: dict[str, Any]) -> str:
    return render_report(metrics).replace(
        f"# {metrics.get('agent_run_id', AGENT_RUN_ID)} - NMD-0003 Calibrated GP Residual Extrapolation",
        "# NMD-0003 Calibrated-Uncertainty GP Residual Extrapolation",
        1,
    )


if __name__ == "__main__":
    raise SystemExit(main())
