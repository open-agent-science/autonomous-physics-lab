#!/usr/bin/env python3
"""Run the TASK-0899 no-peek NMD-0003 GP uncertainty-calibration metric audit.

Freezes a calibration config from train/leave-one-out diagnostics only, using the
three TASK-0865 route families (global robust tail, region-quantile with
predeclared minimum counts, global conformal baseline), then scores the
post-AME2020 holdout *after* the config is frozen. Emits a deterministic sandbox
``agent_runs/AGENT-RUN-0089`` package (metrics + report) and a review note. No
PRED/RESULT/CLAIM/KNOW artifact is created and RESULT-0025 is not modified.
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

from physics_lab import __version__  # noqa: E402
from physics_lab._runtime import enforce as _enforce_python_runtime  # noqa: E402

_enforce_python_runtime()

from physics_lab.engines.nmd0003_gp_calibration_audit import (  # noqa: E402
    BENCHMARK_ID,
    DEFAULT_DATASET_PATH,
    DEFAULT_GATE_PATH,
    DEFAULT_HOLDOUT_PATH,
    ENGINE_VERSION,
    TASK_ID,
    run_nmd0003_gp_calibration_audit,
)
from physics_lab.workflows.artifacts import git_commit, hash_file  # noqa: E402

AGENT_RUN_ID = "AGENT-RUN-0089"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
DEFAULT_REVIEW_PATH = (
    REPO_ROOT / "docs" / "reviews" / "nmd0003-gp-uncertainty-calibration-audit.md"
)
PINNED_COMMAND = "python3 scripts/run_nmd0003_gp_calibration_audit.py"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--review-path", default=str(DEFAULT_REVIEW_PATH))
    parser.add_argument(
        "--no-review", action="store_true", help="Skip writing the review note."
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Print metrics JSON to stdout and write no files (determinism check).",
    )
    return parser


def _provenance() -> dict[str, Any]:
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "benchmark_id": BENCHMARK_ID,
        "engine_version": ENGINE_VERSION,
        "physics_lab_version": __version__,
        "git_commit": git_commit(REPO_ROOT),
        "command": PINNED_COMMAND,
        "code_reference": "physics_lab/engines/nmd0003_gp_calibration_audit.py",
        "input_file_hashes": {
            "dataset": hash_file(REPO_ROOT / DEFAULT_DATASET_PATH, REPO_ROOT),
            "frozen_gate": hash_file(REPO_ROOT / DEFAULT_GATE_PATH, REPO_ROOT),
            "post_ame2020_holdout": hash_file(REPO_ROOT / DEFAULT_HOLDOUT_PATH, REPO_ROOT),
        },
        "determinism": "no random seed consumed; closed-form GP fit and LOO identities",
    }


def main() -> int:
    args = build_parser().parse_args()

    metrics = run_nmd0003_gp_calibration_audit(
        dataset_path=REPO_ROOT / DEFAULT_DATASET_PATH,
        gate_path=REPO_ROOT / DEFAULT_GATE_PATH,
        holdout_path=REPO_ROOT / DEFAULT_HOLDOUT_PATH,
    )
    metrics["agent_run_id"] = AGENT_RUN_ID
    metrics["provenance"] = _provenance()

    if args.print_only:
        print(json.dumps(metrics, indent=2, sort_keys=True))
        return 0

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "report.md").write_text(render_report(metrics), encoding="utf-8")

    if not args.no_review:
        review_path = Path(args.review_path)
        review_path.parent.mkdir(parents=True, exist_ok=True)
        review_path.write_text(render_review(metrics), encoding="utf-8")

    print(f"NMD-0003 GP calibration audit complete: {output_dir / 'metrics.json'}")
    print(f"Verdict: {metrics['verdict']}")
    print(f"Prediction-freeze impact: {metrics['prediction_freeze_impact']}")
    return 0


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #


def _family_row(name: str, result: dict[str, Any]) -> str:
    metrics = result["holdout_metrics"]
    success = result["success"]
    return (
        f"| `{name}` | `{metrics['empirical_coverage_1sigma']}` | "
        f"`{metrics['empirical_coverage_2sigma']}` | "
        f"`{metrics['rms_standardized_residual']}` | "
        f"`{metrics['median_width_inflation']}` | "
        f"`{metrics['p90_width_inflation']}` | "
        f"`{success['all_conditions_pass']}` |"
    )


def _frozen_config_lines(metrics: dict[str, Any]) -> list[str]:
    config = metrics["frozen_config"]
    families = config["families"]
    grt = families["global_robust_tail"]
    conf = families["conformal_global"]
    region = families["region_quantile_min_count"]
    loo = metrics["train_only_loo_diagnostics"]
    lines = [
        "## Frozen config (set from train/LOO diagnostics BEFORE holdout scoring)",
        "",
        f"- `frozen_before_holdout_scoring`: `{config['frozen_before_holdout_scoring']}`.",
        f"- Route preflight: `{config['route_preflight_task']}`; region partition: "
        f"`{config['region_partition']}`; minimum region LOO count: "
        f"`{config['region_min_loo_count']}`.",
        f"- Train-only LOO standardized residual: RMS `{loo['rms_standardized_residual']}`, "
        f"abs p68 `{loo['abs_p68']}`, abs p95 `{loo['abs_p95']}`, abs p99 "
        f"`{loo['abs_p99']}`, abs max `{loo['abs_max']}` over `{loo['count']}` rows.",
        "",
        "### Family 1 - `global_robust_tail` (Student-t on LOO standardized residuals)",
        "",
        f"- Student-t `nu` = `{grt['student_t_nu']}` (LOO abs p95/p68 ratio "
        f"`{grt['loo_abs_p95_over_p68_ratio']}` matched to the Student-t ratio); "
        f"scale `{grt['scale']}`.",
        f"- Frozen interval multipliers: 1-sigma `{grt['interval_multiplier_1sigma']}`, "
        f"2-sigma `{grt['interval_multiplier_2sigma']}` (multipliers on the raw GP 1-sigma).",
        "",
        "### Family 2 - `region_quantile_min_count` (per-`a_band` LOO quantiles)",
        "",
        f"- Partition `{region['partition']}`; minimum LOO count "
        f"`{region['min_loo_count']}`; fallback family `{region['fallback_family']}`.",
        "",
        "| region | LOO count | uses fallback | 1-sigma mult | 2-sigma mult |",
        "| --- | ---: | --- | ---: | ---: |",
    ]
    for region_name, spec in region["regions"].items():
        lines.append(
            f"| `{region_name}` | `{spec['loo_count']}` | `{spec['uses_fallback']}` | "
            f"`{spec['interval_multiplier_1sigma']}` | "
            f"`{spec['interval_multiplier_2sigma']}` |"
        )
    lines.extend(
        [
            "",
            "### Family 3 - `conformal_global` (global LOO absolute-standardized quantiles)",
            "",
            f"- Frozen interval multipliers: 1-sigma `{conf['interval_multiplier_1sigma']}`, "
            f"2-sigma `{conf['interval_multiplier_2sigma']}`.",
            "",
            "### Predeclared success conditions (fixed before scoring)",
            "",
            f"- Central calibration: |1-sigma coverage - {config['nominal_coverage']['central_1sigma']}| "
            f"<= `{config['predeclared_success_thresholds']['coverage_1sigma_tol']}` AND "
            f"|2-sigma coverage - {config['nominal_coverage']['central_2sigma']}| <= "
            f"`{config['predeclared_success_thresholds']['coverage_2sigma_tol']}`.",
            f"- Tail control: `{config['predeclared_success_thresholds']['rms_z_low']}` <= "
            f"RMS standardized residual <= "
            f"`{config['predeclared_success_thresholds']['rms_z_high']}`.",
            f"- Sharpness: median width inflation <= "
            f"`{config['predeclared_success_thresholds']['max_median_width_inflation']}` "
            f"AND p90 width inflation <= "
            f"`{config['predeclared_success_thresholds']['max_p90_width_inflation']}`.",
            "- Coverage surface: every fallback/abstained region reported explicitly; "
            "no holdout target silently dropped.",
            "- Scope: calibration audit only; TASK-0827 stays blocked unless all "
            "conditions pass.",
        ]
    )
    return lines


def _body_lines(metrics: dict[str, Any]) -> list[str]:
    provenance = metrics["provenance"]
    dataset = metrics["dataset_summary"]
    uncal = metrics["holdout_uncalibrated_reference"]["interval_metrics"]
    uncal_std = metrics["holdout_uncalibrated_reference"]["standardized_summary"]
    decision = metrics["audit_decision"]
    lines = [
        f"**Task:** `{metrics['task_id']}`",
        f"**Benchmark:** `{metrics['benchmark_id']}`",
        f"**Source:** `{metrics['source_task_id']}` / `{metrics['source_agent_run_id']}` "
        f"(merged GP engine `physics_lab/engines/nmd0003_residual_gp.py`)",
        f"**Verdict:** `{metrics['verdict']}`",
        f"**Prediction-freeze impact:** `{metrics['prediction_freeze_impact']}`",
        "",
        "## Summary",
        "",
        "This is a *no-peek* calibration audit of the merged NMD-0003 residual GP "
        "predictive uncertainty. The calibration config is frozen from train / "
        "leave-one-out (LOO) diagnostics only, using exactly the three "
        f"`{metrics['route_preflight_task']}` route families. The post-AME2020 "
        f"holdout (`{dataset['holdout_primary_row_count']}` rows; "
        f"`{dataset['post_ame2020_rows_used_for_calibration']}` used for "
        "calibration) is scored only after the config is frozen. The merged GP is "
        "not re-fit or modified. No PRED/RESULT/CLAIM/KNOW artifact is created and "
        "RESULT-0025 is unchanged.",
        "",
        "## Provenance (Gate-B-replayable)",
        "",
        f"- Pinned command: `{provenance['command']}`.",
        f"- Code reference: `{provenance['code_reference']}`; engine version "
        f"`{provenance['engine_version']}`; physics_lab `{provenance['physics_lab_version']}`.",
        f"- git commit: `{provenance['git_commit']}`.",
        f"- Determinism: {provenance['determinism']}. Re-running in the same checkout "
        "reproduces identical non-provenance metrics; `git_commit` records the "
        "checkout used for the run.",
        "- Input file hashes (sha256):",
        f"  - dataset `{provenance['input_file_hashes']['dataset']['sha256']}`",
        f"  - frozen gate `{provenance['input_file_hashes']['frozen_gate']['sha256']}`",
        f"  - post-AME2020 holdout `{provenance['input_file_hashes']['post_ame2020_holdout']['sha256']}`",
        "",
        *_frozen_config_lines(metrics),
        "",
        "## Holdout scoring (AFTER freeze)",
        "",
        "Uncalibrated raw-GP reference: 1-sigma coverage "
        f"`{uncal['empirical_coverage_1sigma']}` (nominal "
        f"`{metrics['frozen_config']['nominal_coverage']['central_1sigma']}`), 2-sigma "
        f"`{uncal['empirical_coverage_2sigma']}` (nominal "
        f"`{metrics['frozen_config']['nominal_coverage']['central_2sigma']}`), RMS "
        f"standardized residual `{uncal_std['rms_standardized_residual']}`, "
        f"abs max `{uncal_std['abs_max']}`.",
        "",
        "| family | 1-sigma cov | 2-sigma cov | RMS z | median width infl | p90 width infl | all pass |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
        _family_row("global_robust_tail", metrics["family_results"]["global_robust_tail"]),
        _family_row(
            "region_quantile_min_count",
            metrics["family_results"]["region_quantile_min_count"],
        ),
        _family_row("conformal_global", metrics["family_results"]["conformal_global"]),
        "",
        f"- Any family passes the predeclared success conditions: "
        f"`{decision['any_family_passes']}`.",
        f"- Passing families: "
        f"`{decision['passing_families'] if decision['passing_families'] else 'none'}`.",
        f"- Tripped stop conditions: "
        f"`{decision['tripped_stop_conditions'] if decision['tripped_stop_conditions'] else 'none'}`.",
        "",
        "### Holdout tail outlier ledger (top 5 by |standardized residual|)",
        "",
        "| nuclide | Z | N | A | corrected residual (MeV) | raw sigma (MeV) | z | a_band | eta band | magic |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in metrics["outlier_ledger"]:
        lines.append(
            f"| `{row['nuclide_id']}` | `{row['Z']}` | `{row['N']}` | `{row['A']}` | "
            f"`{row['corrected_residual_mev']}` | `{row['raw_sigma_mev']}` | "
            f"`{row['standardized_residual']}` | `{row['a_band']}` | "
            f"`{row['neutron_excess_band']}` | `{row['magic_neighborhood']}` |"
        )
    lines.extend(
        [
            "",
            "## Verdict and prediction-freeze impact",
            "",
            f"- Audit verdict: `{metrics['verdict']}`.",
            f"- Prediction-freeze impact: `{metrics['prediction_freeze_impact']}`.",
        ]
    )
    if not decision["any_family_passes"]:
        lines.extend(
            [
                f"- No frozen route family meets the predeclared success conditions, "
                f"so `{metrics['prediction_freeze_task']}` stays blocked. This is "
                "preserved as honest negative/blocker memory; the config was not "
                "tuned to the holdout.",
            ]
        )
    lines.extend(
        [
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in metrics["limitations"])
    routing = metrics["output_routing"]
    lines.extend(
        [
            "",
            "## Output-routing summary",
            "",
            f"- Task verdict: `{routing['task_verdict']}`.",
            "- Scope: calibration audit only.",
            f"- Canonical destination: `{routing['canonical_destination']}` "
            f"(`agent_runs/{AGENT_RUN_ID}/` plus this review note).",
            "- Review tier: none; sandbox blocker/calibration memory.",
            "- Gate A status: not attempted (no RESULT/PRED artifact). Gate B: not "
            "attempted; the run is deterministic and replayable from committed inputs.",
            f"- Claim impact: `{routing['claim_impact']}`. Knowledge impact: "
            f"`{routing['knowledge_impact']}`. Result impact: `{routing['result_impact']}` "
            "(RESULT-0025 unchanged). Prediction impact: "
            f"`{routing['prediction_impact']}`.",
            f"- Prediction-freeze impact: `{metrics['prediction_freeze_impact']}`; "
            f"`{metrics['prediction_freeze_task']}` stays blocked unless the "
            "predeclared success conditions pass.",
            "",
        ]
    )
    return lines


def render_report(metrics: dict[str, Any]) -> str:
    header = [f"# {metrics['agent_run_id']} - NMD-0003 GP Uncertainty Calibration Audit", ""]
    return "\n".join([*header, *_body_lines(metrics)])


def render_review(metrics: dict[str, Any]) -> str:
    header = ["# NMD-0003 GP No-Peek Uncertainty Calibration Audit", ""]
    return "\n".join([*header, *_body_lines(metrics)])


if __name__ == "__main__":
    raise SystemExit(main())
