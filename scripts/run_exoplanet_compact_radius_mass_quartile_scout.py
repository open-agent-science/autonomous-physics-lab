"""TASK-0480 compact-radius mass-quartile scout.

Sandbox-only scout of mass-quartile substructure inside the compact-radius
(`R < 1.5 R_earth`) true-mass/transit-radius slice on the committed PSCompPars
snapshot.

No live fetch, baseline refit, composition inference, habitability wording,
target-priority output, prediction entry, canonical result, claim update, or
knowledge edit is produced.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.datasets.exoplanets import apply_inclusion_filters, load_exoplanet_snapshot  # noqa: E402
from scripts.run_exoplanet_compact_subneptune_matched_control_audit import (  # noqa: E402
    CONTROL_MARGIN_LOG10_RMSE,
    MIN_SLICE_ROW_COUNT,
    _build_control,
    _build_residual_only_control,
    _detection_method_counts,
    _greedy_match_without_replacement,
    _is_compact,
    _mass_value,
    _per_class_median_control_residuals,
    _per_class_median_residuals,
    _radius_value,
    _residual_map,
    _residual_values,
    _row_has_true_mass_and_transit_radius,
    _stats,
)

AGENT_RUN_ID = "AGENT-RUN-0046"
TASK_ID = "TASK-0480"
CAMPAIGN_PROFILE_ID = "exoplanet-mass-radius"
SOURCE_AGENT_RUN_ID = "AGENT-RUN-0042"
SOURCE_TASK_ID = "TASK-0427"

DEFAULT_SNAPSHOT_PATH = REPO_ROOT / "data" / "exoplanets" / "exo-0001-pscomppars-snapshot.yaml"
DEFAULT_AGENT_RUN_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
DEFAULT_METRICS_PATH = DEFAULT_AGENT_RUN_DIR / "metrics.json"
DEFAULT_REPORT_PATH = DEFAULT_AGENT_RUN_DIR / "report.md"
DEFAULT_AGENT_RUN_PATH = DEFAULT_AGENT_RUN_DIR / "agent_run.yaml"
DEFAULT_REVIEW_PATH = REPO_ROOT / "docs" / "reviews" / "exoplanet-compact-radius-mass-quartile-scout.md"

COMPACT_RADIUS_THRESHOLD_REARTH: float = 1.5
QUARTILE_COUNT: int = 4


def _quantile_bounds(sorted_values: list[float], quartile_index: int) -> tuple[int, int]:
    """Return deterministic rank bounds for one quartile using committed order.

    The bins are predeclared as four rank-balanced bins over compact-slice mass
    values sorted by `(mass, row_id)`. Remainder rows are assigned to the earlier
    bins by integer rank slicing.
    """

    n = len(sorted_values)
    start = (quartile_index * n) // QUARTILE_COUNT
    end = ((quartile_index + 1) * n) // QUARTILE_COUNT
    return start, end


def _quartile_specs(compact_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(compact_entries, key=lambda row: (_mass_value(row), row["row_id"]))
    masses = [_mass_value(row) for row in ordered]
    specs: list[dict[str, Any]] = []
    for index in range(QUARTILE_COUNT):
        start, end = _quantile_bounds(masses, index)
        rows = ordered[start:end]
        if rows:
            mass_min = _mass_value(rows[0])
            mass_max = _mass_value(rows[-1])
        else:
            mass_min = None
            mass_max = None
        specs.append(
            {
                "id": f"CMQ-{index + 1:03d}",
                "label": f"compact_mass_quartile_{index + 1}",
                "rank_start_inclusive": start,
                "rank_end_exclusive": end,
                "mass_min_Mearth": mass_min,
                "mass_max_Mearth": mass_max,
                "row_ids": {row["row_id"] for row in rows},
                "description": (
                    "Predeclared rank-balanced mass quartile inside compact "
                    f"R < {COMPACT_RADIUS_THRESHOLD_REARTH} R_earth true-mass/"
                    "transit-radius rows."
                ),
            }
        )
    return specs


def _row_ids_predicate(row_ids: set[str]):
    return lambda row: row["row_id"] in row_ids


def _nearest_mass_outside_compact_control(
    target_entries: list[dict[str, Any]], compact_entries: list[dict[str, Any]], target_row_ids: set[str]
) -> list[dict[str, Any]]:
    candidates = [row for row in compact_entries if row["row_id"] not in target_row_ids]
    return _greedy_match_without_replacement(
        target_entries,
        candidates,
        target_key=lambda row: math.log10(_mass_value(row)),
        candidate_key=lambda row: math.log10(_mass_value(row)),
    )


def _nearest_mass_outside_compact_slice_control(
    target_entries: list[dict[str, Any]], eligible_entries: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    candidates = [row for row in eligible_entries if not _is_compact(row)]
    return _greedy_match_without_replacement(
        target_entries,
        candidates,
        target_key=lambda row: math.log10(_mass_value(row)),
        candidate_key=lambda row: math.log10(_mass_value(row)),
    )


def _classify_quartile(
    target_stats: dict[str, Any], eligible_stats: dict[str, Any], controls: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    count = target_stats["count"]
    target_rmse = target_stats["log10_rmse"]
    eligible_rmse = eligible_stats["log10_rmse"]
    if count < MIN_SLICE_ROW_COUNT:
        return {
            "verdict": "INCONCLUSIVE",
            "outcome": "under_minimum_slice",
            "adverse_control": None,
            "delta_log10_rmse_target_minus_eligible": None,
            "delta_log10_rmse_target_minus_adverse_control": None,
            "explanation": (
                f"Quartile has {count} rows (< {MIN_SLICE_ROW_COUNT}); no residual "
                "interpretation is allowed."
            ),
        }

    adverse_candidates = {
        name: control
        for name, control in controls.items()
        if control["status"] in {"usable_control", "partial_control"}
        and control["stats"]["log10_rmse"] is not None
        and control["kind"] in {"matched_cohort", "residual_shift"}
    }
    adverse_name = None
    adverse_rmse = None
    for name, control in adverse_candidates.items():
        rmse = control["stats"]["log10_rmse"]
        if adverse_rmse is None or rmse > adverse_rmse:
            adverse_name = name
            adverse_rmse = rmse

    delta_eligible = None if target_rmse is None or eligible_rmse is None else target_rmse - eligible_rmse
    delta_control = None if target_rmse is None or adverse_rmse is None else target_rmse - adverse_rmse

    if delta_eligible is not None and delta_eligible > CONTROL_MARGIN_LOG10_RMSE:
        if delta_control is not None and delta_control > CONTROL_MARGIN_LOG10_RMSE:
            outcome = "quartile_residual_stress_above_eligible_and_controls"
            verdict = "SANDBOX_PASS"
        else:
            outcome = "quartile_control_sensitive_residual_stress"
            verdict = "INCONCLUSIVE"
    elif delta_eligible is not None and abs(delta_eligible) <= CONTROL_MARGIN_LOG10_RMSE:
        outcome = "quartile_residual_close_to_eligible"
        verdict = "INCONCLUSIVE"
    elif delta_eligible is not None and delta_eligible < -CONTROL_MARGIN_LOG10_RMSE:
        outcome = "quartile_residual_below_eligible"
        verdict = "INCONCLUSIVE"
    else:
        outcome = "inconclusive"
        verdict = "INCONCLUSIVE"

    return {
        "verdict": verdict,
        "outcome": outcome,
        "adverse_control": adverse_name,
        "delta_log10_rmse_target_minus_eligible": delta_eligible,
        "delta_log10_rmse_target_minus_adverse_control": delta_control,
        "explanation": (
            f"quartile log10 RMSE = {target_rmse}; eligible log10 RMSE = {eligible_rmse}; "
            f"adverse control = {adverse_name} (log10 RMSE = {adverse_rmse}); "
            f"margin = {CONTROL_MARGIN_LOG10_RMSE}."
        ),
    }


def _audit_quartile(
    spec: dict[str, Any],
    compact_entries: list[dict[str, Any]],
    eligible_entries: list[dict[str, Any]],
    residuals: dict[str, float],
    per_class_medians: dict[str, float],
) -> dict[str, Any]:
    row_ids = spec["row_ids"]
    target_entries = [row for row in compact_entries if row["row_id"] in row_ids]
    target_stats = _stats(_residual_values(target_entries, residuals))
    eligible_stats = _stats(_residual_values(eligible_entries, residuals))
    compact_stats = _stats(_residual_values(compact_entries, residuals))

    outside_quartile_compact = _nearest_mass_outside_compact_control(target_entries, compact_entries, row_ids)
    outside_compact_slice = _nearest_mass_outside_compact_slice_control(target_entries, eligible_entries)
    per_class_residuals = _per_class_median_control_residuals(target_entries, per_class_medians)

    controls = {
        "nearest_mass_other_compact_quartiles": _build_control(
            "nearest_mass_other_compact_quartiles",
            outside_quartile_compact,
            residuals,
            target_count=len(target_entries),
            kind="matched_cohort",
            interpretation=(
                "Compact rows outside the target quartile, greedily matched by log mass; "
                "tests whether residual stress is specific to this compact mass rank bin."
            ),
        ),
        "nearest_mass_outside_compact_slice": _build_control(
            "nearest_mass_outside_compact_slice",
            outside_compact_slice,
            residuals,
            target_count=len(target_entries),
            kind="matched_cohort",
            interpretation=(
                "Non-compact eligible rows greedily matched by log mass; tests whether "
                "the mass subrange outside compact radius reproduces the target stress."
            ),
        ),
        "per_class_median": _build_residual_only_control(
            "per_class_median",
            per_class_residuals,
            target_count=len(target_entries),
            kind="residual_shift",
            interpretation=(
                "Per-class median residual shift on target rows; controls for baseline "
                "mass-class bias but is not an independent row slice."
            ),
        ),
    }

    return {
        "id": spec["id"],
        "label": spec["label"],
        "description": spec["description"],
        "rank_start_inclusive": spec["rank_start_inclusive"],
        "rank_end_exclusive": spec["rank_end_exclusive"],
        "mass_min_Mearth": spec["mass_min_Mearth"],
        "mass_max_Mearth": spec["mass_max_Mearth"],
        "target_stats": target_stats,
        "compact_slice_stats": compact_stats,
        "eligible_stats": eligible_stats,
        "controls": controls,
        "classification": _classify_quartile(target_stats, eligible_stats, controls),
        "detection_method_counts": _detection_method_counts(target_entries),
    }


def build_metrics(snapshot_path: Path) -> dict[str, Any]:
    payload = load_exoplanet_snapshot(snapshot_path)
    filtered = apply_inclusion_filters(payload)
    eligible = [row for row in filtered.included_rows if _row_has_true_mass_and_transit_radius(row)]
    residuals = _residual_map(eligible)
    eligible = [row for row in eligible if row["row_id"] in residuals]
    compact = [row for row in eligible if _is_compact(row)]
    per_class_medians = _per_class_median_residuals(eligible, residuals)

    specs = _quartile_specs(compact)
    quartiles = [
        _audit_quartile(spec, compact, eligible, residuals, per_class_medians)
        for spec in specs
    ]
    headline = {
        "eligible_true_mass_transit_radius": _stats(_residual_values(eligible, residuals)),
        "compact_radius_lt1p5Re": _stats(_residual_values(compact, residuals)),
        "interpretable_quartiles": [
            item["id"] for item in quartiles if item["classification"]["verdict"] == "SANDBOX_PASS"
        ],
        "underpowered_quartiles": [
            item["id"]
            for item in quartiles
            if item["classification"]["outcome"] == "under_minimum_slice"
        ],
    }
    return {
        "schema_version": "0.1.0",
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "source_task_id": SOURCE_TASK_ID,
        "source_agent_run_id": SOURCE_AGENT_RUN_ID,
        "snapshot_path": str(snapshot_path.relative_to(REPO_ROOT)),
        "live_fetch_performed": False,
        "baseline_refit_performed": False,
        "compact_radius_threshold_Rearth": COMPACT_RADIUS_THRESHOLD_REARTH,
        "minimum_slice_row_count": MIN_SLICE_ROW_COUNT,
        "control_margin_log10_rmse": CONTROL_MARGIN_LOG10_RMSE,
        "predeclared_bins": {
            "method": "rank_balanced_mass_quartiles_within_compact_slice",
            "sort_key": ["mass.value", "row_id"],
            "quartile_count": QUARTILE_COUNT,
        },
        "headline": headline,
        "quartiles": quartiles,
        "forbidden_interpretations": [
            "composition_inference",
            "habitability_or_biosignature_inference",
            "target_prioritization",
            "atmospheric_state_inference",
            "new_mass_radius_law",
            "claim_promotion",
        ],
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _render_report(metrics: dict[str, Any]) -> str:
    lines = [
        "# Exoplanet Compact-Radius Mass-Quartile Scout",
        "",
        f"**Task:** `{TASK_ID}`  ",
        f"**Agent run:** `{AGENT_RUN_ID}`  ",
        "**Verdict boundary:** sandbox benchmark diagnostic only",
        "",
        "## Summary",
        "",
        "This scout tests whether the compact-radius residual stress is concentrated "
        "in a predeclared mass quartile inside the `R < 1.5 R_earth` true-mass/"
        "transit-radius slice. It uses the committed PSCompPars snapshot only and "
        "does not perform a live fetch or baseline refit.",
        "",
        "## Headline Metrics",
        "",
        "| Quantity | Value |",
        "| --- | ---: |",
        f"| Eligible true-mass/transit-radius rows | `{metrics['headline']['eligible_true_mass_transit_radius']['count']}` |",
        f"| Eligible log10 RMSE | `{metrics['headline']['eligible_true_mass_transit_radius']['log10_rmse']}` |",
        f"| Compact rows | `{metrics['headline']['compact_radius_lt1p5Re']['count']}` |",
        f"| Compact log10 RMSE | `{metrics['headline']['compact_radius_lt1p5Re']['log10_rmse']}` |",
        "",
        "## Quartile Results",
        "",
        "| Quartile | Mass range M_earth | Rows | log10 RMSE | Verdict | Outcome | Adverse control | Delta vs eligible | Delta vs adverse |",
        "| --- | ---: | ---: | ---: | --- | --- | --- | ---: | ---: |",
    ]
    for quartile in metrics["quartiles"]:
        classification = quartile["classification"]
        lines.append(
            "| "
            f"`{quartile['id']}` | "
            f"`{quartile['mass_min_Mearth']}`-`{quartile['mass_max_Mearth']}` | "
            f"`{quartile['target_stats']['count']}` | "
            f"`{quartile['target_stats']['log10_rmse']}` | "
            f"`{classification['verdict']}` | "
            f"`{classification['outcome']}` | "
            f"`{classification['adverse_control']}` | "
            f"`{classification['delta_log10_rmse_target_minus_eligible']}` | "
            f"`{classification['delta_log10_rmse_target_minus_adverse_control']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "This scout may identify benchmark substructure or negative/control-sensitive memory. "
            "It does not support composition, habitability, target-priority, atmospheric, "
            "or new mass-radius-law wording.",
            "",
            "## Output Routing",
            "",
            "- Task verdict: sandbox benchmark diagnostic only",
            f"- Canonical destination: `agent_runs/{AGENT_RUN_ID}/` and "
            "`docs/reviews/exoplanet-compact-radius-mass-quartile-scout.md`",
            "- Review tier: none",
            "- Gate A status: not attempted",
            "- Gate B status: not attempted",
            "- Claim impact: no claim change",
            "- Knowledge impact: no knowledge change",
            "- Result artifact impact: no canonical `RESULT-*` created or edited",
            "",
        ]
    )
    return "\n".join(lines)


def _render_review(metrics: dict[str, Any]) -> str:
    return _render_report(metrics).replace(
        "# Exoplanet Compact-Radius Mass-Quartile Scout",
        "# Exoplanet Compact-Radius Mass-Quartile Scout Review",
        1,
    )


def _agent_run_payload(metrics_path: Path, report_path: Path, review_path: Path) -> dict[str, Any]:
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "status": "completed",
        "agent": {"contributor_id": "akutenyov", "agent_id": "codex"},
        "inputs": {
            "snapshot": str(DEFAULT_SNAPSHOT_PATH.relative_to(REPO_ROOT)),
            "source_agent_run_id": SOURCE_AGENT_RUN_ID,
            "source_task_id": SOURCE_TASK_ID,
            "live_fetch_performed": False,
        },
        "outputs": {
            "metrics": str(metrics_path.relative_to(REPO_ROOT)),
            "report": str(report_path.relative_to(REPO_ROOT)),
            "review": str(review_path.relative_to(REPO_ROOT)),
        },
        "result_boundary": "sandbox_benchmark_diagnostic_only",
        "forbidden_outputs": ["RESULT", "CLAIM", "KNOW", "PRED"],
    }


def write_outputs(metrics: dict[str, Any], metrics_path: Path, report_path: Path, agent_run_path: Path, review_path: Path) -> None:
    _write_json(metrics_path, metrics)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_render_report(metrics), encoding="utf-8")
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(_render_review(metrics), encoding="utf-8")
    _write_yaml(agent_run_path, _agent_run_payload(metrics_path, report_path, review_path))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT_PATH)
    parser.add_argument("--out", type=Path, default=DEFAULT_METRICS_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--agent-run", type=Path, default=DEFAULT_AGENT_RUN_PATH)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW_PATH)
    args = parser.parse_args()

    metrics = build_metrics(args.snapshot)
    write_outputs(metrics, args.out, args.report, args.agent_run, args.review)
    print(f"Completed: {TASK_ID} compact-radius mass-quartile scout")
    print(f"Metrics: {args.out}")
    print(f"Report: {args.report}")
    print(f"Agent run: {args.agent_run}")
    print(f"Review: {args.review}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
