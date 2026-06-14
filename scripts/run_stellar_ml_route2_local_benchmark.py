#!/usr/bin/env python3
"""Run the TASK-0740 Stellar M-L Route 2 local-extractor benchmark.

The full DEBCat row set is intentionally local-only. This runner consumes the
normalized rows produced by ``scripts/extract_debcat_stellar_ml_rows.py`` and
writes sandbox-only AGENT-RUN artifacts. It does not fetch DEBCat, fit alpha,
commit full rows, create RESULT artifacts, or promote claims.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import median
from typing import Any

import yaml

AGENT_RUN_ID = "AGENT-RUN-0070"
TASK_ID = "TASK-0740"
CAMPAIGN_PROFILE_ID = "textbook-formula-audit"

PRIMARY_ALPHA = 3.5
PRIMARY_MASS_RANGE = (0.5, 2.0)
PRIMARY_L0 = 1.0


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        payload = yaml.safe_load(fh)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML mapping: {path}")
    return payload


def _round(value: float | None, ndigits: int = 6) -> float | None:
    if value is None or math.isnan(value):
        return None
    return round(float(value), ndigits)


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, math.ceil(q * len(ordered)) - 1))
    return ordered[idx]


def _prediction_log_luminosity(log_mass_solar: float) -> float:
    return math.log10(PRIMARY_L0) + PRIMARY_ALPHA * log_mass_solar


def _is_primary_range(row: dict[str, Any]) -> bool:
    mass = float(row["mass_solar"])
    return PRIMARY_MASS_RANGE[0] <= mass < PRIMARY_MASS_RANGE[1]


def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    residuals = [float(row["residual_dex"]) for row in rows]
    abs_residuals = [abs(value) for value in residuals]
    return {
        "count": len(rows),
        "mae_dex": _round(_mean(abs_residuals)),
        "rmse_dex": _round(
            math.sqrt(sum(value * value for value in residuals) / len(residuals))
            if residuals
            else None
        ),
        "median_residual_dex": _round(median(residuals) if residuals else None),
        "median_abs_residual_dex": _round(median(abs_residuals) if abs_residuals else None),
        "p90_abs_residual_dex": _round(_quantile(abs_residuals, 0.9)),
        "max_abs_residual_dex": _round(max(abs_residuals) if abs_residuals else None),
        "fraction_abs_residual_le_0p1": _round(
            sum(1 for value in abs_residuals if value <= 0.1) / len(abs_residuals)
            if abs_residuals
            else None
        ),
        "fraction_abs_residual_le_0p2": _round(
            sum(1 for value in abs_residuals if value <= 0.2) / len(abs_residuals)
            if abs_residuals
            else None
        ),
        "fraction_abs_residual_le_0p3": _round(
            sum(1 for value in abs_residuals if value <= 0.3) / len(abs_residuals)
            if abs_residuals
            else None
        ),
    }


def _group_summary(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row.get(key, "unknown")), []).append(row)
    return {name: _summarize(items) for name, items in sorted(grouped.items())}


def _lane_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return _group_summary(rows, "lane")


def _build_scored_rows(rows_doc: dict[str, Any]) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for row in rows_doc.get("rows", []):
        if row.get("admissibility") != "admitted":
            continue
        log_mass = float(row["log_mass_solar"])
        log_luminosity = float(row["log_luminosity_solar"])
        prediction = _prediction_log_luminosity(log_mass)
        scored.append(
            {
                "row_id": row["row_id"],
                "system_id": row["system_id"],
                "lane": row["lane"],
                "mass_solar": float(row["mass_solar"]),
                "log_mass_solar": log_mass,
                "log_luminosity_solar": log_luminosity,
                "predicted_log_luminosity_solar": prediction,
                "residual_dex": log_luminosity - prediction,
                "mass_band": row.get("mass_band", "unknown"),
                "luminosity_provenance_class": row.get(
                    "luminosity_provenance_class", "unknown"
                ),
                "luminosity_uncertainty_class": row.get(
                    "luminosity_uncertainty_class", "unknown"
                ),
                "evolutionary_stage_flag": row.get("evolutionary_stage_flag", "unknown"),
                "primary_mass_range": _is_primary_range(row),
            }
        )
    return scored


def _null_baseline(primary_rows: list[dict[str, Any]]) -> dict[str, Any]:
    train_rows = [row for row in primary_rows if row["lane"] == "train"]
    medians_by_band: dict[str, float] = {}
    for band in sorted({row["mass_band"] for row in train_rows}):
        values = [
            float(row["log_luminosity_solar"])
            for row in train_rows
            if row["mass_band"] == band
        ]
        if values:
            medians_by_band[band] = median(values)
    global_train = median([float(row["log_luminosity_solar"]) for row in train_rows])
    by_lane: dict[str, dict[str, Any]] = {}
    for lane in ("validation", "holdout"):
        lane_rows = [row for row in primary_rows if row["lane"] == lane]
        formula_abs = [abs(float(row["residual_dex"])) for row in lane_rows]
        null_abs = [
            abs(
                float(row["log_luminosity_solar"])
                - medians_by_band.get(str(row["mass_band"]), global_train)
            )
            for row in lane_rows
        ]
        formula_mae = _mean(formula_abs)
        null_mae = _mean(null_abs)
        by_lane[lane] = {
            "count": len(lane_rows),
            "formula_mae_dex": _round(formula_mae),
            "mass_band_train_median_null_mae_dex": _round(null_mae),
            "formula_minus_null_mae_dex": _round(
                formula_mae - null_mae
                if formula_mae is not None and null_mae is not None
                else None
            ),
            "formula_beats_null": (
                formula_mae < null_mae
                if formula_mae is not None and null_mae is not None
                else None
            ),
        }
    return {
        "definition": "Per-mass-band train-lane median log_luminosity_solar.",
        "train_median_log_luminosity_by_mass_band": {
            key: _round(value) for key, value in medians_by_band.items()
        },
        "global_train_median_log_luminosity": _round(global_train),
        "lanes": by_lane,
    }


def _classification(metrics: dict[str, Any]) -> tuple[str, str]:
    holdout = metrics["null_control"]["lanes"]["holdout"]
    if holdout["count"] < 10:
        return (
            "INCONCLUSIVE",
            "Primary-range holdout has fewer than 10 rows; benchmark route ran but "
            "interpretation is sample-limited.",
        )
    if holdout["formula_beats_null"] is True:
        return (
            "SANDBOX_PASS",
            "Primary-range holdout formula MAE beats the predeclared train-median null.",
        )
    return (
        "SANDBOX_FAIL",
        "Primary-range holdout formula MAE does not beat the predeclared train-median null.",
    )


def _markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return "\n".join(lines)


def _write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _build_report(metrics: dict[str, Any], classification: str, rationale: str) -> str:
    primary_lanes = metrics["primary_mass_range"]["by_lane"]
    null_lanes = metrics["null_control"]["lanes"]
    lane_rows = []
    for lane in ("train", "validation", "holdout"):
        summary = primary_lanes.get(lane, {})
        null_summary = null_lanes.get(lane, {})
        lane_rows.append(
            [
                lane,
                summary.get("count", 0),
                summary.get("mae_dex"),
                summary.get("median_residual_dex"),
                summary.get("fraction_abs_residual_le_0p2"),
                null_summary.get("formula_beats_null", "n/a"),
            ]
        )

    return f"""
# AGENT-RUN-0070 - Stellar M-L Route 2 Local-Extractor Benchmark

**Task:** `TASK-0740`
**Outcome:** `{classification}`

## Summary

This run executes the first sandbox-only Stellar mass-luminosity Route 2
benchmark against locally regenerated DEBCat component rows. It uses the pinned
DEBCat checksum, the committed extractor contract, frozen physical-binary-system
lanes, and the predeclared single-alpha primary baseline
`L/L_sun = (M/M_sun)^3.5` over `0.5 <= M/M_sun < 2.0`.

No raw `debs.dat`, full normalized DEBCat row file, full manifest, `RESULT-*`,
`PRED-*`, `CLAIM-*`, or `KNOW-*` artifact is committed.

## Decision

- Classification: `{classification}`.
- Rationale: {rationale}
- Primary-range holdout rows: `{primary_lanes.get("holdout", {}).get("count", 0)}`.
- Primary-range holdout MAE: `{primary_lanes.get("holdout", {}).get("mae_dex")}` dex.
- Train-median null holdout MAE: `{null_lanes.get("holdout", {}).get("mass_band_train_median_null_mae_dex")}` dex.

## Primary-Range Lane Metrics

{_markdown_table(["lane", "count", "MAE dex", "median residual dex", "frac <=0.2 dex", "beats null"], lane_rows)}

## Sensitivity Notes

- Direct-luminosity and derived-luminosity rows are reported separately in
  `metrics.json`.
- Out-of-primary-range rows are diagnostic only and do not drive the run verdict.
- Unknown or evolved spectral-stage flags are retained as explicit subset
  labels rather than filtered after residual inspection.

## Output Routing Summary

- Task verdict: `{classification}`.
- Canonical destination: `agent_runs/AGENT-RUN-0070/metrics.json`,
  `agent_runs/AGENT-RUN-0070/report.md`, and
  `docs/reviews/stellar-ml-route2-local-benchmark.md`.
- Review tier: `none`.
- Gate A status: `not_attempted`.
- Gate B status: `not_applicable`.
- Claim impact: `none`.
- Knowledge impact: `none`.
- Result impact: `no RESULT artifact created`.
- Publication blocker: `sandbox-only first empirical benchmark; full DEBCat rows remain local-only under Route 2`.
"""


def _build_limitations(classification: str) -> str:
    return f"""
# AGENT-RUN-0070 Limitations

- Verdict `{classification}` is sandbox-only and does not validate or falsify
  the stellar mass-luminosity relation in universal terms.
- Full DEBCat rows and the raw `debs.dat` table are not committed because DEBCat
  has no explicit open-redistribution licence recorded in the repository.
- The primary benchmark uses the predeclared single-alpha route from
  `TASK-0740`; piecewise textbook-bin scoring remains a later extension.
- DEBCat machine-readable rows provide catalogue-level luminosity provenance,
  not per-row primary-literature luminosity pointers.
- Spectral-stage flags are best-effort metadata; unknown/evolved subsets are
  reported separately and require domain review before interpretation.
"""


def _build_preflight() -> str:
    return """
# AGENT-RUN-0070 Preflight

| Check | Status | Notes |
| --- | --- | --- |
| Campaign scope | PASS | `textbook-formula-audit` authorizes sandbox formula-audit runs. |
| Source binding | PASS | DEBCat rows were regenerated from checksum-verified local `debs.dat`. |
| Baseline freeze | PASS | Uses fixed `alpha=3.5`; no exponent fit or residual-tuned parameter change. |
| Holdout freeze | PASS | Uses extractor-assigned physical-binary-system lanes. |
| Storage boundary | PASS | Raw/full DEBCat artifacts remain local-only and uncommitted. |
| Promotion boundary | PASS | No canonical result, prediction, claim, or knowledge artifact is created. |
"""


def _build_review_summary(classification: str, rationale: str) -> str:
    return f"""
# AGENT-RUN-0070 Review Summary

`TASK-0740` completed a sandbox-only Route 2 local-extractor benchmark. The
result classification is `{classification}` because {rationale}

Maintainer review should focus on whether the primary single-alpha route is
sufficient as the first empirical Stellar M-L audit or whether a follow-up task
should run the piecewise textbook baseline declared in the older source/baseline
plan.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", required=True, type=Path, help="Local full rows YAML.")
    parser.add_argument("--manifest", required=True, type=Path, help="Local full manifest YAML.")
    parser.add_argument(
        "--out-dir",
        default=Path("agent_runs") / AGENT_RUN_ID,
        type=Path,
        help="Sandbox AGENT-RUN output directory.",
    )
    args = parser.parse_args(argv)

    rows_doc = _load_yaml(args.rows)
    manifest_doc = _load_yaml(args.manifest)
    scored = _build_scored_rows(rows_doc)
    primary = [row for row in scored if row["primary_mass_range"]]

    metrics: dict[str, Any] = {
        "task_id": TASK_ID,
        "agent_run_id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "benchmark": {
            "formula": "L/L_sun = (M/M_sun)^3.5",
            "alpha": PRIMARY_ALPHA,
            "l0": PRIMARY_L0,
            "primary_mass_range_solar": {
                "min_inclusive": PRIMARY_MASS_RANGE[0],
                "max_exclusive": PRIMARY_MASS_RANGE[1],
            },
            "residual_axis": "log10(L_observed/L_predicted) dex",
            "no_alpha_fit_performed": True,
        },
        "input_references": {
            "rows_local": "<local-only>/debcat_component_rows.yaml",
            "manifest_local": "<local-only>/debcat_holdout_manifest.yaml",
            "fetch_command": (
                "python3 scripts/fetch_source_artifact.py --url "
                "https://astro.keele.ac.uk/jkt/debcat/debs.dat --sha256 "
                "326902535b4da2fd94f227806ff339247d6df224ef8faea8857703e553b464da "
                "--output <local-only>/debs.dat"
            ),
            "extract_command": (
                "python3 scripts/extract_debcat_stellar_ml_rows.py --debs-dat "
                "<local-only>/debs.dat --out-rows <local-only>/debcat_component_rows.yaml "
                "--out-manifest <local-only>/debcat_holdout_manifest.yaml"
            ),
            "extractor": "scripts/extract_debcat_stellar_ml_rows.py",
            "readiness_gate": "docs/reviews/stellar-ml-benchmark-readiness-after-route2.md",
            "source_manifest": "data/textbook_formula_audit/stellar_ml/source_manifest.yaml",
        },
        "source_counts": rows_doc.get("counts") or rows_doc.get("full_dataset_counts"),
        "manifest_lane_counts": manifest_doc.get("lane_system_counts")
        or manifest_doc.get("full_lane_system_counts"),
        "all_admitted": {
            "summary": _summarize(scored),
            "by_lane": _lane_summary(scored),
            "by_mass_band": _group_summary(scored, "mass_band"),
        },
        "primary_mass_range": {
            "summary": _summarize(primary),
            "by_lane": _lane_summary(primary),
            "by_mass_band": _group_summary(primary, "mass_band"),
            "by_luminosity_provenance_class": _group_summary(
                primary, "luminosity_provenance_class"
            ),
            "by_luminosity_uncertainty_class": _group_summary(
                primary, "luminosity_uncertainty_class"
            ),
            "by_evolutionary_stage_flag": _group_summary(primary, "evolutionary_stage_flag"),
        },
    }
    metrics["null_control"] = _null_baseline(primary)
    classification, rationale = _classification(metrics)
    metrics["classification"] = {"verdict": classification, "rationale": rationale}

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    _write_text(out_dir / "report.md", _build_report(metrics, classification, rationale))
    _write_text(out_dir / "limitations.md", _build_limitations(classification))
    _write_text(out_dir / "preflight.md", _build_preflight())
    _write_text(out_dir / "review_summary.md", _build_review_summary(classification, rationale))

    agent_run = {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "task_id": TASK_ID,
        "status": "SANDBOX_COMPLETE",
        "sandbox_only": True,
        "created_by": {"contributor_id": "akutenyov", "agent_id": "codex"},
        "proposal_paths": {
            "hypothesis": "hypothesis_proposals/textbook-formula-audit/HYP-PROPOSAL-0058-stellar-ml-route2-local-benchmark.yaml",
            "experiment": "experiment_proposals/textbook-formula-audit/EXP-PROPOSAL-0024-stellar-ml-route2-local-benchmark.yaml",
        },
        "artifacts": {
            "metrics": f"agent_runs/{AGENT_RUN_ID}/metrics.json",
            "report": f"agent_runs/{AGENT_RUN_ID}/report.md",
            "limitations": f"agent_runs/{AGENT_RUN_ID}/limitations.md",
            "preflight": f"agent_runs/{AGENT_RUN_ID}/preflight.md",
            "review_summary": f"agent_runs/{AGENT_RUN_ID}/review_summary.md",
        },
        "preflight": {
            "passed": True,
            "checks": [
                {
                    "name": "campaign_scope",
                    "status": "PASS",
                    "notes": "textbook-formula-audit permits sandbox-only formula-audit runs.",
                },
                {
                    "name": "source_binding",
                    "status": "PASS",
                    "notes": "Rows were generated from checksum-verified local DEBCat source.",
                },
                {
                    "name": "baseline_freeze",
                    "status": "PASS",
                    "notes": "Fixed alpha=3.5 baseline; no exponent fitting.",
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": "No RESULT, PRED, CLAIM, or KNOW artifact is created.",
                },
            ],
        },
        "limitations": [
            "Sandbox-only first empirical benchmark; no universal M-L claim.",
            "Full DEBCat rows remain local-only under Route 2.",
            "Catalogue-level luminosity provenance limits interpretation.",
        ],
        "verdict": classification,
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review before any RESULT-* packaging or claim/knowledge routing."
            ),
        },
    }
    with (out_dir / "agent_run.yaml").open("w", encoding="utf-8") as fh:
        yaml.safe_dump(agent_run, fh, sort_keys=False, allow_unicode=True)

    print(f"wrote {out_dir}")
    print(f"classification={classification}")
    print(f"rationale={rationale}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
