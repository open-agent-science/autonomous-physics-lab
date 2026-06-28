#!/usr/bin/env python3
"""Adjudicate TASK-0824 NMD-0003 GP uncertainty calibration without holdout tuning."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab._runtime import enforce as _enforce_python_runtime  # noqa: E402

_enforce_python_runtime()

from physics_lab.engines.nmd0003_residual_gp import (  # noqa: E402
    DEFAULT_DATASET_PATH,
    DEFAULT_GATE_PATH,
    DEFAULT_HOLDOUT_PATH,
    FROZEN_BASELINE_ID,
    SURVIVAL_MARGIN_MEV,
    _calibration_summary,
    _calibration_verdict,
    _error_summary,
    _frozen_baseline_coefficients,
    _holdout_arrays,
    _repo_relative_posix,
    _training_residuals,
    fit_residual_gp,
)
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset  # noqa: E402
from physics_lab.registry.post_ame2020_holdout import (  # noqa: E402
    load_post_ame2020_holdout_dataset,
)

TASK_ID = "TASK-0844"
SOURCE_TASK_ID = "TASK-0824"
SOURCE_AGENT_RUN_ID = "AGENT-RUN-0080"
SOURCE_METRICS_PATH = REPO_ROOT / "agent_runs" / SOURCE_AGENT_RUN_ID / "metrics.json"
DEFAULT_JSON_PATH = REPO_ROOT / "docs" / "reviews" / "nmd0003-gp-uncertainty-calibration-diagnostics.json"
DEFAULT_MD_PATH = (
    REPO_ROOT / "docs" / "reviews" / "nmd0003-gp-uncertainty-calibration-adjudication.md"
)
MAGIC_NUMBERS = (2, 8, 20, 28, 50, 82, 126)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", default=str(DEFAULT_JSON_PATH))
    parser.add_argument("--md-out", default=str(DEFAULT_MD_PATH))
    parser.add_argument("--no-write", action="store_true", help="Print JSON only.")
    return parser


def _rounded(value: float) -> float:
    return round(float(value), 6)


def _standardized_summary(values: np.ndarray) -> dict[str, float | int]:
    abs_values = np.abs(values)
    return {
        "count": int(values.size),
        "mean": _rounded(float(np.mean(values))),
        "median": _rounded(float(np.median(values))),
        "rms": _rounded(float(np.sqrt(np.mean(values**2)))),
        "abs_p50": _rounded(float(np.percentile(abs_values, 50))),
        "abs_p68": _rounded(float(np.percentile(abs_values, 68.2689))),
        "abs_p90": _rounded(float(np.percentile(abs_values, 90))),
        "abs_p95": _rounded(float(np.percentile(abs_values, 95))),
        "abs_p9545": _rounded(float(np.percentile(abs_values, 95.45))),
        "abs_p99": _rounded(float(np.percentile(abs_values, 99))),
        "abs_max": _rounded(float(np.max(abs_values))),
        "fraction_beyond_2sigma": _rounded(float(np.mean(abs_values > 2.0))),
        "fraction_beyond_3sigma": _rounded(float(np.mean(abs_values > 3.0))),
    }


def _coverage(corrected_residual: np.ndarray, sigma: np.ndarray, scale: float) -> dict[str, float | int]:
    scaled_sigma = sigma * scale
    standardized = corrected_residual / scaled_sigma
    summary = _calibration_summary(corrected_residual, scaled_sigma)
    return {
        **summary,
        "scale": _rounded(scale),
        "calibration_verdict": _calibration_verdict(summary),
        "mean_scaled_sigma_mev": _rounded(float(np.mean(scaled_sigma))),
        "median_scaled_sigma_mev": _rounded(float(np.median(scaled_sigma))),
        "abs_p95_standardized": _rounded(float(np.percentile(np.abs(standardized), 95))),
        "abs_max_standardized": _rounded(float(np.max(np.abs(standardized)))),
    }


def _a_band(a: int) -> str:
    if a < 60:
        return "light_A_lt_60"
    if a < 140:
        return "medium_60_le_A_lt_140"
    return "heavy_A_ge_140"


def _neutron_excess_band(z: int, n: int, a: int) -> str:
    eta = (n - z) / a
    if eta < 0.15:
        return "low_eta_lt_0_15"
    if eta < 0.25:
        return "mid_0_15_le_eta_lt_0_25"
    return "high_eta_ge_0_25"


def _magic_band(z: int, n: int) -> str:
    min_distance = min(abs(z - magic) for magic in MAGIC_NUMBERS)
    min_distance = min(min_distance, *(abs(n - magic) for magic in MAGIC_NUMBERS))
    if min_distance <= 2:
        return "near_magic_within_2"
    return "not_near_magic"


def _region_summaries(
    rows: list[Mapping[str, Any]],
    corrected_residual: np.ndarray,
    sigma: np.ndarray,
    labels: Iterable[tuple[str, list[str]]],
) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for family, family_labels in labels:
        output[family] = {}
        for label in family_labels:
            mask = np.array([_row_region(row, family) == label for row in rows], dtype=bool)
            if not bool(np.any(mask)):
                continue
            output[family][label] = _coverage(corrected_residual[mask], sigma[mask], scale=1.0)
    return output


def _row_region(row: Mapping[str, Any], family: str) -> str:
    z = int(row["Z"])
    n = int(row["N"])
    a = int(row["A"])
    if family == "a_band":
        return _a_band(a)
    if family == "neutron_excess_band":
        return _neutron_excess_band(z, n, a)
    if family == "magic_neighborhood":
        return _magic_band(z, n)
    raise ValueError(f"unknown region family: {family}")


def _outlier_ledger(
    rows: list[Mapping[str, Any]],
    corrected_residual: np.ndarray,
    sigma: np.ndarray,
    *,
    limit: int = 12,
) -> list[dict[str, Any]]:
    standardized = corrected_residual / sigma
    order = np.argsort(-np.abs(standardized))[:limit]
    ledger: list[dict[str, Any]] = []
    for index in order:
        row = rows[int(index)]
        z = int(row["Z"])
        n = int(row["N"])
        a = int(row["A"])
        ledger.append(
            {
                "rank": len(ledger) + 1,
                "row_id": row["row_id"],
                "nuclide_id": row["nuclide_id"],
                "Z": z,
                "N": n,
                "A": a,
                "corrected_residual_mev": _rounded(corrected_residual[index]),
                "predictive_sigma_mev": _rounded(sigma[index]),
                "standardized_residual": _rounded(standardized[index]),
                "abs_standardized_residual": _rounded(abs(standardized[index])),
                "a_band": _a_band(a),
                "neutron_excess_band": _neutron_excess_band(z, n, a),
                "magic_neighborhood": _magic_band(z, n),
                "measurement_methods": list(row.get("measurement_method_ids", [])),
                "publication_year": row.get("publication_year"),
            }
        )
    return ledger


def _loo_standardized_residuals(fit: Any, residual_train: np.ndarray) -> np.ndarray:
    centered = residual_train - fit.target_mean
    inverse_lower = np.linalg.solve(fit.cholesky_lower, np.eye(fit.cholesky_lower.shape[0]))
    kernel_inverse_diag = np.sum(inverse_lower**2, axis=0)
    alpha = fit.alpha
    # LOO residual = alpha_i / K^-1_ii and LOO sigma = sqrt(1 / K^-1_ii).
    loo_residual = alpha / kernel_inverse_diag
    loo_sigma = np.sqrt(1.0 / kernel_inverse_diag)
    # Keep a defensive check so future refactors do not silently change conventions.
    if not np.isfinite(centered).all() or not np.isfinite(loo_sigma).all():
        raise ValueError("non-finite LOO calibration diagnostic")
    return loo_residual / loo_sigma


def _candidate_scales(loo_standardized: np.ndarray) -> dict[str, float]:
    abs_loo = np.abs(loo_standardized)
    return {
        "none": 1.0,
        "loo_rms_scale": max(1.0, float(np.sqrt(np.mean(loo_standardized**2)))),
        "loo_95_abs_quantile_to_2sigma": max(1.0, float(np.percentile(abs_loo, 95.0) / 2.0)),
        "loo_9545_abs_quantile_to_2sigma": max(
            1.0, float(np.percentile(abs_loo, 95.45) / 2.0)
        ),
        "loo_99_abs_quantile_to_3sigma": max(1.0, float(np.percentile(abs_loo, 99.0) / 3.0)),
    }


def _adjudication_verdict(scaled_holdout: Mapping[str, Mapping[str, Any]]) -> str:
    for name, row in scaled_holdout.items():
        if name == "none":
            continue
        cov1 = float(row["empirical_coverage_1sigma"])
        cov2 = float(row["empirical_coverage_2sigma"])
        rms = float(row["rms_standardized_residual"])
        scale = float(row["scale"])
        if (
            abs(cov1 - 0.682689) <= 0.05
            and abs(cov2 - 0.9545) <= 0.03
            and 0.85 <= rms <= 1.2
            and scale <= 2.0
        ):
            return "CALIBRATION_PATH_READY_FOR_FREEZE"
    return "POINT_GAIN_ONLY_UNCERTAINTY_BLOCKED"


def analyze() -> dict[str, Any]:
    dataset = load_nuclear_mass_dataset(REPO_ROOT / DEFAULT_DATASET_PATH)
    entries = sorted(
        dataset.entries, key=lambda entry: (entry.A, entry.Z, entry.N, entry.nuclide_id)
    )
    gate = yaml.safe_load((REPO_ROOT / DEFAULT_GATE_PATH).read_text(encoding="utf-8"))
    coefficients = _frozen_baseline_coefficients(gate)
    holdout_payload = load_post_ame2020_holdout_dataset(REPO_ROOT / DEFAULT_HOLDOUT_PATH)
    holdout_rows = [
        row for row in holdout_payload["entries"] if bool(row["included_in_time_split_holdout"])
    ]

    z_train, n_train, residual_train = _training_residuals(entries, coefficients)
    holdout = _holdout_arrays(holdout_rows, coefficients)
    fit = fit_residual_gp(z_train, n_train, residual_train)
    holdout_mean, holdout_sigma = fit.predict(holdout["Z"], holdout["N"])
    corrected_residual = holdout["baseline_residual"] - holdout_mean
    standardized_holdout = corrected_residual / holdout_sigma

    loo_standardized = _loo_standardized_residuals(fit, residual_train)
    scales = _candidate_scales(loo_standardized)
    scaled_holdout = {
        name: _coverage(corrected_residual, holdout_sigma, scale)
        for name, scale in scales.items()
    }

    source_metrics = json.loads(SOURCE_METRICS_PATH.read_text(encoding="utf-8"))
    region_labels = [
        ("a_band", ["light_A_lt_60", "medium_60_le_A_lt_140", "heavy_A_ge_140"]),
        (
            "neutron_excess_band",
            ["low_eta_lt_0_15", "mid_0_15_le_eta_lt_0_25", "high_eta_ge_0_25"],
        ),
        ("magic_neighborhood", ["near_magic_within_2", "not_near_magic"]),
    ]
    verdict = _adjudication_verdict(scaled_holdout)

    return {
        "task_id": TASK_ID,
        "source_task_id": SOURCE_TASK_ID,
        "source_agent_run_id": SOURCE_AGENT_RUN_ID,
        "input_references": {
            "dataset": _repo_relative_posix(REPO_ROOT / DEFAULT_DATASET_PATH),
            "frozen_gate": _repo_relative_posix(REPO_ROOT / DEFAULT_GATE_PATH),
            "post_ame2020_holdout": _repo_relative_posix(REPO_ROOT / DEFAULT_HOLDOUT_PATH),
            "source_metrics": _repo_relative_posix(SOURCE_METRICS_PATH),
            "frozen_baseline_id": FROZEN_BASELINE_ID,
        },
        "source_metric_consistency": {
            "holdout_rows": len(holdout_rows),
            "source_holdout_rows": source_metrics["dataset_summary"]["holdout_primary_row_count"],
            "gp_corrected_mae_mev": _error_summary(corrected_residual)["mae_mev"],
            "source_gp_corrected_mae_mev": source_metrics["extrapolation"][
                "gp_corrected_holdout"
            ]["mae_mev"],
            "calibration_verdict": _calibration_verdict(
                _calibration_summary(corrected_residual, holdout_sigma)
            ),
            "source_calibration_verdict": source_metrics["calibration_verdict"],
        },
        "holdout_standardized_residual_distribution": _standardized_summary(
            standardized_holdout
        ),
        "train_only_loo_standardized_residual_distribution": _standardized_summary(
            loo_standardized
        ),
        "train_only_candidate_interval_scales": {
            name: _rounded(scale) for name, scale in scales.items()
        },
        "holdout_coverage_by_train_only_scale": scaled_holdout,
        "per_region_holdout_coverage_unscaled": _region_summaries(
            holdout_rows, corrected_residual, holdout_sigma, region_labels
        ),
        "outlier_ledger_top_abs_standardized_residuals": _outlier_ledger(
            holdout_rows, corrected_residual, holdout_sigma
        ),
        "verdict": verdict,
        "decision": {
            "prediction_freeze_ready": verdict == "CALIBRATION_PATH_READY_FOR_FREEZE",
            "point_estimator_status": "retain_as_point_estimator_benchmark",
            "uncertainty_status": (
                "blocked_for_prediction_freeze"
                if verdict == "POINT_GAIN_ONLY_UNCERTAINTY_BLOCKED"
                else "train_only_path_available"
            ),
            "survival_margin_mev": SURVIVAL_MARGIN_MEV,
            "claim_impact": "none",
            "knowledge_impact": "none",
            "prediction_impact": "none",
        },
    }


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def render_markdown(payload: Mapping[str, Any]) -> str:
    holdout = payload["holdout_standardized_residual_distribution"]
    loo = payload["train_only_loo_standardized_residual_distribution"]
    consistency = payload["source_metric_consistency"]
    lines = [
        "# NMD-0003 GP Uncertainty Calibration Adjudication",
        "",
        f"**Task:** `{TASK_ID}`",
        f"**Source task:** `{SOURCE_TASK_ID}`",
        f"**Source metrics:** `agent_runs/{SOURCE_AGENT_RUN_ID}/metrics.json`",
        f"**Verdict:** `{payload['verdict']}`",
        "",
        "## Executive Decision",
        "",
    ]
    if payload["verdict"] == "POINT_GAIN_ONLY_UNCERTAINTY_BLOCKED":
        lines.extend(
            [
                "The TASK-0824 GP correction remains useful as point-estimator evidence,",
                "but its uncertainty envelope is not ready for prediction freeze. The",
                "holdout has a split personality: central coverage is already too wide",
                "at 1 sigma, while a small tail produces a large RMS standardized",
                "residual. A single train-only interval inflation rule therefore cannot",
                "make the envelope both calibrated and sharp enough for future PRED",
                "interval semantics.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "A train-only calibration path satisfies the configured coverage/RMS",
                "criteria. This would still need TASK-0827 freeze packaging before any",
                "prediction registry entry.",
                "",
            ]
        )

    lines.extend(
        [
            "## Source Consistency",
            "",
            f"- Holdout rows: `{consistency['holdout_rows']}` (source metrics `{consistency['source_holdout_rows']}`).",
            f"- GP-corrected MAE: `{consistency['gp_corrected_mae_mev']}` MeV (source `{consistency['source_gp_corrected_mae_mev']}`).",
            f"- Calibration verdict: `{consistency['calibration_verdict']}` (source `{consistency['source_calibration_verdict']}`).",
            "",
            "## Standardized Residual Diagnostics",
            "",
            "| diagnostic | train-only LOO | post-AME2020 holdout |",
            "| --- | ---: | ---: |",
            f"| count | `{loo['count']}` | `{holdout['count']}` |",
            f"| RMS standardized residual | `{loo['rms']}` | `{holdout['rms']}` |",
            f"| abs p68 | `{loo['abs_p68']}` | `{holdout['abs_p68']}` |",
            f"| abs p95 | `{loo['abs_p95']}` | `{holdout['abs_p95']}` |",
            f"| abs p99 | `{loo['abs_p99']}` | `{holdout['abs_p99']}` |",
            f"| abs max | `{loo['abs_max']}` | `{holdout['abs_max']}` |",
            f"| fraction beyond 2 sigma | `{loo['fraction_beyond_2sigma']}` | `{holdout['fraction_beyond_2sigma']}` |",
            f"| fraction beyond 3 sigma | `{loo['fraction_beyond_3sigma']}` | `{holdout['fraction_beyond_3sigma']}` |",
            "",
            "The holdout's nominal 1-sigma coverage is high, but the RMS standardized",
            "residual is also high. That combination is the calibration blocker:",
            "uniformly inflating intervals can suppress the tail RMS only by making",
            "the already-overcovered central region even less calibrated.",
            "",
            "## Train-Only Interval Scale Sensitivity",
            "",
            "| scale rule | scale | 1-sigma coverage | 2-sigma coverage | RMS z | verdict |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for name, row in payload["holdout_coverage_by_train_only_scale"].items():
        lines.append(
            "| "
            f"`{name}` | `{row['scale']}` | `{row['empirical_coverage_1sigma']}` | "
            f"`{row['empirical_coverage_2sigma']}` | `{row['rms_standardized_residual']}` | "
            f"`{row['calibration_verdict']}` |"
        )

    lines.extend(["", "## Per-Region Unscaled Coverage", ""])
    for family, rows in payload["per_region_holdout_coverage_unscaled"].items():
        lines.extend([f"### `{family}`", "", "| region | count | 1 sigma | 2 sigma | RMS z |", "| --- | ---: | ---: | ---: | ---: |"])
        for label, row in rows.items():
            lines.append(
                f"| `{label}` | `{row['count']}` | `{row['empirical_coverage_1sigma']}` | "
                f"`{row['empirical_coverage_2sigma']}` | `{row['rms_standardized_residual']}` |"
            )
        lines.append("")

    lines.extend(
        [
            "## Outlier Ledger",
            "",
            "| rank | nuclide | Z | N | A | residual MeV | sigma MeV | z | bands |",
            "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in payload["outlier_ledger_top_abs_standardized_residuals"]:
        bands = (
            f"{row['a_band']}; {row['neutron_excess_band']}; "
            f"{row['magic_neighborhood']}"
        )
        lines.append(
            f"| {row['rank']} | `{row['nuclide_id']}` | {row['Z']} | {row['N']} | {row['A']} | "
            f"`{row['corrected_residual_mev']}` | `{row['predictive_sigma_mev']}` | "
            f"`{row['standardized_residual']}` | {bands} |"
        )

    lines.extend(
        [
            "",
            "## TASK-0827 Implication",
            "",
            "- Prediction freeze impact: `blocked_for_uncertainty`; the GP may be carried",
            "  forward as a point-estimator candidate only.",
            "- A future freeze task would need a predeclared uncertainty model that handles",
            "  the tail/central-coverage mismatch without optimizing on the post-AME2020",
            "  holdout.",
            "- No PRED, CLAIM, RESULT, or KNOW artifact is created by this adjudication.",
            "",
            "## Output-Routing Summary",
            "",
            "- Canonical destination: `docs/reviews/nmd0003-gp-uncertainty-calibration-adjudication.md`.",
            f"- Calibration verdict: `{payload['verdict']}`.",
            "- Result impact: `none`.",
            "- Prediction impact: `none`; prediction freeze remains blocked.",
            "- Claim impact: `none`.",
            "- Knowledge impact: `none`.",
            "- Gate A / Gate B: not applicable; this is an adjudication note, not a RESULT/PRED promotion.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = build_parser().parse_args()
    payload = analyze()
    if args.no_write:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    json_path = Path(args.json_out)
    md_path = Path(args.md_out)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Wrote diagnostics: {json_path}")
    print(f"Wrote adjudication note: {md_path}")
    print(f"Verdict: {payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
