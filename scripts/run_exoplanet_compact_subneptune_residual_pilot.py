"""TASK-0390 compact/sub-Neptune exoplanet residual hypothesis pilot.

This sandbox runner tests bounded compact and sub-Neptune residual
hypotheses on the committed PSCompPars snapshot only. It keeps the
frozen Chen-Kipping baseline fixed, uses true-mass rows as the primary
interpretable axis, and reports minimum-mass rows as diagnostic-only.

The runner does not fetch live data, refit the baseline, write
canonical results, create prediction entries, promote claims, edit
knowledge, or infer composition, habitability, biosignatures, target
priority, or universal planet laws.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path
from typing import Any, Callable

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.datasets.exoplanets import (  # noqa: E402
    apply_inclusion_filters,
    load_exoplanet_snapshot,
)
from physics_lab.engines.exoplanet_mass_radius import (  # noqa: E402
    chen_kipping_predict_radius,
    planet_class_for_mass,
)

AGENT_RUN_ID = "AGENT-RUN-0036"
TASK_ID = "TASK-0390"
CAMPAIGN_PROFILE_ID = "exoplanet-mass-radius"
HYPOTHESIS_PATH = (
    "hypothesis_proposals/exoplanet-mass/"
    "HYP-PROPOSAL-0051-compact-subneptune-residual-pilot.yaml"
)
EXPERIMENT_PATH = (
    "experiment_proposals/exoplanet-mass/"
    "EXP-PROPOSAL-0017-compact-subneptune-residual-pilot.yaml"
)
DEFAULT_SNAPSHOT_PATH = (
    REPO_ROOT / "data" / "exoplanets" / "exo-0001-pscomppars-snapshot.yaml"
)
DEFAULT_AGENT_RUN_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
DEFAULT_METRICS_PATH = DEFAULT_AGENT_RUN_DIR / "metrics.json"
DEFAULT_REPORT_PATH = DEFAULT_AGENT_RUN_DIR / "report.md"
DEFAULT_AGENT_RUN_PATH = DEFAULT_AGENT_RUN_DIR / "agent_run.yaml"
DEFAULT_LIMITATIONS_PATH = DEFAULT_AGENT_RUN_DIR / "limitations.md"
DEFAULT_PREFLIGHT_PATH = DEFAULT_AGENT_RUN_DIR / "preflight.md"
DEFAULT_REVIEW_SUMMARY_PATH = DEFAULT_AGENT_RUN_DIR / "review_summary.md"
DEFAULT_REVIEW_PATH = (
    REPO_ROOT
    / "docs"
    / "reviews"
    / "exoplanet-compact-subneptune-residual-hypothesis-pilot.md"
)

MIN_HYPOTHESIS_ROW_COUNT: int = 30
SURVIVAL_LOG10_RMSE_MARGIN: float = 0.022
SHUFFLE_SEED: int = 20260526


def _is_positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value)) and value > 0


def _row_has_true_mass_and_transit_radius(entry: dict[str, Any]) -> bool:
    mass = entry.get("mass") or {}
    radius = entry.get("radius") or {}
    return (
        mass.get("mass_class") == "true_mass"
        and radius.get("radius_class") == "transit_radius"
        and _is_positive_number(mass.get("value"))
        and _is_positive_number(radius.get("value"))
    )


def _row_has_minimum_mass_and_transit_radius(entry: dict[str, Any]) -> bool:
    mass = entry.get("mass") or {}
    radius = entry.get("radius") or {}
    return (
        mass.get("mass_class") == "minimum_mass_msini"
        and radius.get("radius_class") == "transit_radius"
        and _is_positive_number(mass.get("value"))
        and _is_positive_number(radius.get("value"))
    )


def _log_residual(entry: dict[str, Any]) -> float | None:
    mass = float(entry["mass"]["value"])
    radius = float(entry["radius"]["value"])
    pred = chen_kipping_predict_radius(mass)
    if not math.isfinite(pred) or pred <= 0.0:
        return None
    return math.log10(radius) - math.log10(pred)


def _host_teff(entry: dict[str, Any]) -> float | None:
    value = (entry.get("host_star") or {}).get("effective_temperature_K")
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return None


def _relative_uncertainty(component: dict[str, Any]) -> float | None:
    value = component.get("value")
    if not _is_positive_number(value):
        return None
    upper = component.get("uncertainty_upper")
    lower = component.get("uncertainty_lower")
    candidates = [
        abs(float(v))
        for v in (upper, lower)
        if isinstance(v, (int, float)) and math.isfinite(float(v))
    ]
    if not candidates:
        return None
    return max(candidates) / float(value)


def _radius_value(entry: dict[str, Any]) -> float:
    return float(entry["radius"]["value"])


def _mass_value(entry: dict[str, Any]) -> float:
    return float(entry["mass"]["value"])


def _is_compact(entry: dict[str, Any]) -> bool:
    return _radius_value(entry) < 1.5


def _is_sub_neptune(entry: dict[str, Any]) -> bool:
    radius = _radius_value(entry)
    return 1.5 <= radius < 4.0


def _is_compact_or_sub_neptune(entry: dict[str, Any]) -> bool:
    return _radius_value(entry) < 4.0


GENERATED_HYPOTHESES: list[dict[str, Any]] = [
    {
        "id": "CSN-001",
        "label": "compact_radius_lt1p5Re",
        "description": (
            "Compact true-mass/transit-radius rows with R/Re < 1.5 have "
            "larger frozen CK17 residual stress than the eligible true-mass "
            "surface and matched controls."
        ),
        "predicate": _is_compact,
        "executed": True,
    },
    {
        "id": "CSN-002",
        "label": "sub_neptune_radius_1p5_4Re",
        "description": (
            "Sub-Neptune true-mass/transit-radius rows with 1.5 <= R/Re < 4 "
            "retain residual stress after class and sample-size controls."
        ),
        "predicate": _is_sub_neptune,
        "executed": True,
    },
    {
        "id": "CSN-003",
        "label": "compact_or_sub_neptune_radius_lt4Re",
        "description": (
            "The combined compact/sub-Neptune radius surface with R/Re < 4 "
            "is tested as a bounded high-stress envelope."
        ),
        "predicate": _is_compact_or_sub_neptune,
        "executed": True,
    },
    {
        "id": "CSN-004",
        "label": "neptunian_sub_neptune_overlap",
        "description": (
            "Neptunian CK17-class rows inside the sub-Neptune radius range "
            "are generated as a narrower overlap hypothesis."
        ),
        "predicate": lambda e: (
            planet_class_for_mass(_mass_value(e)) == "neptunian" and _is_sub_neptune(e)
        ),
        "executed": False,
    },
    {
        "id": "CSN-005",
        "label": "compact_subneptune_tight_radius_uncertainty",
        "description": (
            "Compact/sub-Neptune rows with reported radius relative "
            "uncertainty <= 5% are generated as a measurement-quality "
            "sensitivity hypothesis."
        ),
        "predicate": lambda e: (
            _is_compact_or_sub_neptune(e)
            and (_relative_uncertainty(e["radius"]) is not None)
            and _relative_uncertainty(e["radius"]) <= 0.05
        ),
        "executed": False,
    },
    {
        "id": "CSN-006",
        "label": "compact_subneptune_cool_host",
        "description": (
            "Compact/sub-Neptune rows around cool hosts (Teff < 5200 K) "
            "are generated as a selection-sensitive host-context hypothesis."
        ),
        "predicate": lambda e: (
            _is_compact_or_sub_neptune(e)
            and _host_teff(e) is not None
            and _host_teff(e) < 5200.0
        ),
        "executed": False,
    },
]


def _rmse(values: list[float]) -> float | None:
    if not values:
        return None
    return math.sqrt(sum(v * v for v in values) / len(values))


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    sorted_values = sorted(values)
    mid = len(sorted_values) // 2
    if len(sorted_values) % 2 == 1:
        return sorted_values[mid]
    return 0.5 * (sorted_values[mid - 1] + sorted_values[mid])


def _stats(values: list[float]) -> dict[str, Any]:
    return {
        "count": len(values),
        "log10_rmse": _rmse(values),
        "log10_mae": _mean([abs(v) for v in values]),
        "log10_bias": _mean(values),
        "log10_median": _median(values),
    }


def _per_class_median_residuals(
    entries: list[dict[str, Any]], residuals: dict[str, float]
) -> dict[str, float]:
    by_class: dict[str, list[float]] = {}
    for entry in entries:
        residual = residuals.get(entry["row_id"])
        if residual is None:
            continue
        label = planet_class_for_mass(_mass_value(entry))
        by_class.setdefault(label, []).append(residual)
    return {
        label: median
        for label, values in by_class.items()
        if (median := _median(values)) is not None
    }


def _candidate_residuals(
    hypothesis_entries: list[dict[str, Any]], residuals: dict[str, float]
) -> list[float]:
    return [
        residuals[entry["row_id"]]
        for entry in hypothesis_entries
        if residuals.get(entry["row_id"]) is not None
    ]


def _per_class_median_control_residuals(
    hypothesis_entries: list[dict[str, Any]], per_class_medians: dict[str, float]
) -> list[float]:
    out: list[float] = []
    for entry in hypothesis_entries:
        mass = _mass_value(entry)
        radius = _radius_value(entry)
        ck_pred = chen_kipping_predict_radius(mass)
        if not math.isfinite(ck_pred) or ck_pred <= 0.0:
            continue
        label = planet_class_for_mass(mass)
        shift = per_class_medians.get(label, 0.0)
        out.append(math.log10(radius) - (math.log10(ck_pred) + shift))
    return out


def _shuffled_label_control_residuals(
    hypothesis_entries: list[dict[str, Any]],
    eligible_entries: list[dict[str, Any]],
    residuals: dict[str, float],
    rng: random.Random,
) -> list[float]:
    """Deterministic shuffled-label control preserving candidate count."""

    k = min(len(hypothesis_entries), len(eligible_entries))
    if k <= 0:
        return []
    sampled_ids = rng.sample([entry["row_id"] for entry in eligible_entries], k)
    return [
        residuals[row_id]
        for row_id in sampled_ids
        if residuals.get(row_id) is not None
    ]


def _matched_size_neighbor_control_residuals(
    hypothesis_entries: list[dict[str, Any]],
    eligible_entries: list[dict[str, Any]],
    residuals: dict[str, float],
) -> list[float]:
    eligible_by_class: dict[str, list[tuple[float, dict[str, Any]]]] = {}
    for entry in eligible_entries:
        mass = _mass_value(entry)
        label = planet_class_for_mass(mass)
        eligible_by_class.setdefault(label, []).append((math.log10(mass), entry))
    for values in eligible_by_class.values():
        values.sort(key=lambda item: item[0])

    out: list[float] = []
    for entry in hypothesis_entries:
        label = planet_class_for_mass(_mass_value(entry))
        log_mass = math.log10(_mass_value(entry))
        best_id = None
        best_delta = float("inf")
        for peer_log_mass, peer in eligible_by_class.get(label, []):
            if peer["row_id"] == entry["row_id"]:
                continue
            delta = abs(peer_log_mass - log_mass)
            if delta < best_delta:
                best_delta = delta
                best_id = peer["row_id"]
        if best_id is not None and residuals.get(best_id) is not None:
            out.append(residuals[best_id])
    return out


def _classify_stress_outcome(
    candidate_stats: dict[str, Any],
    control_stats: dict[str, dict[str, Any]],
    eligible_stats: dict[str, Any],
    min_count: int,
    survival_margin: float,
) -> dict[str, Any]:
    candidate_count = candidate_stats["count"]
    candidate_rmse = candidate_stats["log10_rmse"]
    eligible_rmse = eligible_stats["log10_rmse"]
    if candidate_count < min_count:
        return {
            "outcome": "under_minimum_slice",
            "explanation": (
                f"Slice has {candidate_count} rows (< minimum {min_count}); "
                "no residual interpretation is allowed."
            ),
            "adverse_control": None,
            "delta_log10_rmse_candidate_minus_eligible": None,
            "delta_log10_rmse_candidate_minus_adverse_control": None,
        }

    adverse_control = None
    adverse_control_rmse = None
    for name, stats in control_stats.items():
        rmse = stats.get("log10_rmse")
        if rmse is None or stats.get("count", 0) == 0:
            continue
        if adverse_control_rmse is None or rmse > adverse_control_rmse:
            adverse_control_rmse = rmse
            adverse_control = name

    delta_eligible = (
        None
        if candidate_rmse is None or eligible_rmse is None
        else float(candidate_rmse - eligible_rmse)
    )
    delta_control = (
        None
        if candidate_rmse is None or adverse_control_rmse is None
        else float(candidate_rmse - adverse_control_rmse)
    )

    if (
        delta_eligible is not None
        and delta_eligible > survival_margin
        and delta_control is not None
        and delta_control > survival_margin
    ):
        outcome = "residual_stress_above_eligible_and_controls"
    elif delta_eligible is not None and delta_eligible > survival_margin:
        outcome = "residual_stress_above_eligible_only"
    elif delta_eligible is not None and delta_eligible < -survival_margin:
        outcome = "residual_stress_below_eligible"
    else:
        outcome = "inconclusive"

    return {
        "outcome": outcome,
        "explanation": (
            f"candidate log10 RMSE = {candidate_rmse}; "
            f"eligible log10 RMSE = {eligible_rmse}; "
            f"adverse control = {adverse_control} "
            f"(log10 RMSE = {adverse_control_rmse}); "
            f"survival margin = {survival_margin}."
        ),
        "adverse_control": adverse_control,
        "delta_log10_rmse_candidate_minus_eligible": delta_eligible,
        "delta_log10_rmse_candidate_minus_adverse_control": delta_control,
    }


def _agent_verdict(hypothesis_results: dict[str, dict[str, Any]]) -> str:
    executed = [
        result
        for result in hypothesis_results.values()
        if result.get("role") == "executed_hypothesis"
    ]
    if not executed:
        return "INCONCLUSIVE"
    outcomes = [item["classification"]["outcome"] for item in executed]
    if any(outcome == "residual_stress_above_eligible_and_controls" for outcome in outcomes):
        return "SANDBOX_PASS"
    return "INCONCLUSIVE"


def _residual_map(entries: list[dict[str, Any]]) -> dict[str, float]:
    residuals: dict[str, float] = {}
    for entry in entries:
        value = _log_residual(entry)
        if value is not None and math.isfinite(value):
            residuals[entry["row_id"]] = value
    return residuals


def build_metrics(snapshot_path: Path) -> dict[str, Any]:
    payload = load_exoplanet_snapshot(snapshot_path)
    filtered = apply_inclusion_filters(payload)
    eligible_true_mass = [
        entry
        for entry in filtered.included_rows
        if _row_has_true_mass_and_transit_radius(entry)
    ]
    true_mass_residuals = _residual_map(eligible_true_mass)
    eligible_with_residual = [
        entry for entry in eligible_true_mass if entry["row_id"] in true_mass_residuals
    ]
    eligible_stats = _stats(list(true_mass_residuals.values()))
    per_class_medians = _per_class_median_residuals(
        eligible_with_residual, true_mass_residuals
    )

    minimum_mass_entries = [
        entry
        for entry in filtered.included_rows
        if _row_has_minimum_mass_and_transit_radius(entry)
    ]
    minimum_mass_residuals = _residual_map(minimum_mass_entries)

    rng = random.Random(SHUFFLE_SEED)
    hypothesis_results: dict[str, dict[str, Any]] = {}
    for hypothesis in GENERATED_HYPOTHESES:
        predicate: Callable[[dict[str, Any]], bool] = hypothesis["predicate"]
        hypothesis_entries = [entry for entry in eligible_with_residual if predicate(entry)]
        candidate_values = _candidate_residuals(hypothesis_entries, true_mass_residuals)
        candidate_stats = _stats(candidate_values)

        if hypothesis["executed"]:
            controls = {
                "per_class_median": _stats(
                    _per_class_median_control_residuals(
                        hypothesis_entries, per_class_medians
                    )
                ),
                "shuffled_label": _stats(
                    _shuffled_label_control_residuals(
                        hypothesis_entries,
                        eligible_with_residual,
                        true_mass_residuals,
                        rng,
                    )
                ),
                "matched_size_neighbor": _stats(
                    _matched_size_neighbor_control_residuals(
                        hypothesis_entries,
                        eligible_with_residual,
                        true_mass_residuals,
                    )
                ),
            }
            classification = _classify_stress_outcome(
                candidate_stats,
                controls,
                eligible_stats,
                MIN_HYPOTHESIS_ROW_COUNT,
                SURVIVAL_LOG10_RMSE_MARGIN,
            )
            role = "executed_hypothesis"
        else:
            controls = {}
            classification = {
                "outcome": "generated_not_executed",
                "explanation": (
                    "Hypothesis generated and candidate stats recorded, but "
                    "not executed under the 1-3 hypothesis execution budget."
                ),
                "adverse_control": None,
                "delta_log10_rmse_candidate_minus_eligible": None,
                "delta_log10_rmse_candidate_minus_adverse_control": None,
            }
            role = "generated_only"

        hypothesis_results[hypothesis["id"]] = {
            "label": hypothesis["label"],
            "description": hypothesis["description"],
            "role": role,
            "candidate_stats": candidate_stats,
            "control_stats": controls,
            "classification": classification,
        }

    metrics: dict[str, Any] = {
        "task_id": TASK_ID,
        "agent_run_id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "snapshot_path": snapshot_path.relative_to(REPO_ROOT).as_posix(),
        "data_boundary": {
            "live_external_fetch_performed": False,
            "baseline_refit_performed": False,
            "minimum_mass_rows_in_headline_metrics": False,
            "true_mass_axis_primary": True,
        },
        "loader_summary": {
            "total_rows": filtered.total_rows,
            "pre_filter_included_count": filtered.pre_filter_included_count,
            "post_filter_included_count": filtered.post_filter_included_count,
            "eligible_true_mass_with_transit_radius": len(eligible_with_residual),
            "minimum_mass_with_transit_radius_diagnostic": len(minimum_mass_residuals),
        },
        "thresholds": {
            "min_hypothesis_row_count": MIN_HYPOTHESIS_ROW_COUNT,
            "survival_log10_rmse_margin": SURVIVAL_LOG10_RMSE_MARGIN,
            "shuffle_seed": SHUFFLE_SEED,
        },
        "eligible_true_mass_stats": eligible_stats,
        "minimum_mass_sparse_diagnostic": _stats(list(minimum_mass_residuals.values())),
        "per_class_medians_log10_residual": per_class_medians,
        "generated_hypothesis_count": len(GENERATED_HYPOTHESES),
        "executed_hypothesis_count": sum(
            1 for hypothesis in GENERATED_HYPOTHESES if hypothesis["executed"]
        ),
        "hypotheses": hypothesis_results,
    }
    metrics["verdict"] = _agent_verdict(hypothesis_results)
    return metrics


def _fmt(value: float | None, places: int = 6) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{places}f}"


def _render_report(metrics: dict[str, Any]) -> str:
    loader = metrics["loader_summary"]
    eligible = metrics["eligible_true_mass_stats"]
    lines = [
        f"# {AGENT_RUN_ID} - Exoplanet compact/sub-Neptune residual pilot",
        "",
        f"- Task: {TASK_ID}",
        f"- Campaign profile: {CAMPAIGN_PROFILE_ID}",
        f"- Snapshot: `{metrics['snapshot_path']}`",
        f"- Verdict: **{metrics['verdict']}**",
        "",
        "## Boundary",
        "",
        "Sandbox-only pilot using committed snapshot rows and frozen CK17 "
        "residuals. True-mass/transit-radius rows are the primary "
        "interpretable axis. Minimum-mass rows are diagnostic-only. The run "
        "does not infer composition, habitability, biosignatures, target "
        "priority, or universal planet laws.",
        "",
        "## Eligible Axis",
        "",
        f"- Total rows in snapshot: {loader['total_rows']}",
        f"- Pre-filter included: {loader['pre_filter_included_count']}",
        f"- Post-filter included: {loader['post_filter_included_count']}",
        (
            "- Eligible true-mass/transit-radius rows: "
            f"{loader['eligible_true_mass_with_transit_radius']}"
        ),
        (
            "- Diagnostic minimum-mass/transit-radius rows: "
            f"{loader['minimum_mass_with_transit_radius_diagnostic']}"
        ),
        (
            f"- True-mass CK17 log10 RMSE = {_fmt(eligible['log10_rmse'])}, "
            f"MAE = {_fmt(eligible['log10_mae'])}, "
            f"bias = {_fmt(eligible['log10_bias'])}"
        ),
        "",
        "## Generated Hypotheses",
        "",
        (
            f"- Generated: {metrics['generated_hypothesis_count']}; "
            f"executed: {metrics['executed_hypothesis_count']}"
        ),
        f"- Minimum hypothesis row count: {metrics['thresholds']['min_hypothesis_row_count']}",
        f"- Survival margin: {metrics['thresholds']['survival_log10_rmse_margin']}",
        f"- Shuffled-label seed: {metrics['thresholds']['shuffle_seed']}",
        "",
    ]
    for hypothesis_id, result in metrics["hypotheses"].items():
        stats = result["candidate_stats"]
        cls = result["classification"]
        lines.extend(
            [
                f"### {hypothesis_id} - `{result['label']}` ({result['role']})",
                "",
                result["description"],
                "",
                (
                    f"- Candidate slice: count {stats['count']}, "
                    f"log10 RMSE {_fmt(stats['log10_rmse'])}, "
                    f"MAE {_fmt(stats['log10_mae'])}, "
                    f"bias {_fmt(stats['log10_bias'])}"
                ),
            ]
        )
        if result["control_stats"]:
            lines.extend(
                [
                    "",
                    "| control | count | log10 RMSE | log10 MAE | log10 bias |",
                    "| --- | ---: | ---: | ---: | ---: |",
                ]
            )
            for name, control in result["control_stats"].items():
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            name,
                            str(control["count"]),
                            _fmt(control["log10_rmse"]),
                            _fmt(control["log10_mae"]),
                            _fmt(control["log10_bias"]),
                        ]
                    )
                    + " |"
                )
        lines.extend(["", f"- **Outcome:** `{cls['outcome']}`", f"- {cls['explanation']}", ""])
    lines.extend(
        [
            "## Output Routing",
            "",
            "- Task verdict: `SANDBOX_PASS` if any executed hypothesis exceeds both "
            "the eligible surface and adverse controls by the configured margin; "
            "otherwise `INCONCLUSIVE`.",
            "- Canonical destination: sandbox-only `agent_runs/` and review note.",
            "- Review tier: none; no `RESULT-*`, `PRED-*`, claim, or knowledge file.",
            "- Gate A: not attempted because this task requested sandbox evidence, "
            "not canonical result publication.",
            "- Gate B: not attempted.",
            "- Claim impact: no claim change.",
            "- Knowledge impact: no knowledge change.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_review(metrics: dict[str, Any]) -> str:
    lines = [
        "# Exoplanet compact/sub-Neptune residual hypothesis pilot",
        "",
        f"- Agent run: `{AGENT_RUN_ID}`",
        f"- Task: `{TASK_ID}`",
        f"- Snapshot: `{metrics['snapshot_path']}`",
        f"- Verdict: **{metrics['verdict']}**",
        "",
        "## Scope",
        "",
        "This review packages a sandbox-only compact/sub-Neptune residual "
        "hypothesis pilot. It uses only committed PSCompPars snapshot rows, "
        "keeps the Chen-Kipping baseline frozen, and keeps true-mass rows "
        "separate from diagnostic minimum-mass rows.",
        "",
        "No live fetch, baseline refit, canonical result, prediction-registry "
        "entry, claim, knowledge edit, composition inference, habitability "
        "wording, biosignature wording, target-priority ranking, or universal "
        "planet-law wording is authorized by this review.",
        "",
        "## Controls",
        "",
        "- `per_class_median`: shifts CK17 by the eligible-set median residual "
        "within each CK17 mass class.",
        "- `shuffled_label`: deterministic shuffled-label control preserving "
        "candidate row count.",
        "- `matched_size_neighbor`: sample-size matched nearest-mass same-class "
        "control.",
        "",
        "## Executed Hypotheses",
        "",
        "| hypothesis | label | count | RMSE | adverse control | delta vs eligible | delta vs adverse control | outcome |",
        "| --- | --- | ---: | ---: | --- | ---: | ---: | --- |",
    ]
    for hypothesis_id, result in metrics["hypotheses"].items():
        if result["role"] != "executed_hypothesis":
            continue
        stats = result["candidate_stats"]
        cls = result["classification"]
        lines.append(
            "| "
            + " | ".join(
                [
                    hypothesis_id,
                    result["label"],
                    str(stats["count"]),
                    _fmt(stats["log10_rmse"]),
                    str(cls["adverse_control"]) if cls["adverse_control"] else "n/a",
                    _fmt(cls["delta_log10_rmse_candidate_minus_eligible"]),
                    _fmt(cls["delta_log10_rmse_candidate_minus_adverse_control"]),
                    cls["outcome"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Generated But Not Executed",
            "",
        ]
    )
    for hypothesis_id, result in metrics["hypotheses"].items():
        if result["role"] == "executed_hypothesis":
            continue
        stats = result["candidate_stats"]
        lines.append(
            f"- `{hypothesis_id}` (`{result['label']}`): generated only; "
            f"candidate count {stats['count']}, RMSE {_fmt(stats['log10_rmse'])}."
        )
    lines.extend(
        [
            "",
            "## Negative And Null Results",
            "",
            "Generated-only hypotheses were not promoted beyond candidate stats. "
            "Executed hypotheses that do not clear both eligible and adverse-control "
            "margins remain visible in `agent_runs/AGENT-RUN-0036/metrics.json`.",
            "",
            "## Output Routing",
            "",
            "- Task verdict: `" + metrics["verdict"] + "`.",
            "- Canonical destination: sandbox-only `agent_runs/AGENT-RUN-0036/` "
            "and this review note.",
            "- Review tier: none.",
            "- Gate A: not attempted.",
            "- Gate B: not attempted.",
            "- Claim impact: no claim change.",
            "- Knowledge impact: no knowledge change.",
            "- Publication blocker: task scope authorizes sandbox evidence only.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_limitations(metrics: dict[str, Any]) -> str:
    del metrics
    bullets = [
        "Residual hypotheses use committed catalog fields and frozen CK17 "
        "residuals only.",
        "The shuffled-label control is one deterministic draw, not a Monte "
        "Carlo distribution.",
        "Controls share the same eligible true-mass surface and are "
        "diagnostic, not causal.",
        "Minimum-mass rows are reported only as sparse diagnostics.",
        "No composition, habitability, biosignature, target-priority, "
        "prediction, claim, or knowledge output is authorized.",
    ]
    return "# Limitations\n\n" + "\n".join(f"- {item}" for item in bullets) + "\n"


def _render_preflight(metrics: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Preflight",
            "",
            f"- Snapshot: `{metrics['snapshot_path']}`",
            "- Data boundary: only committed snapshot rows are read; no live fetch.",
            "- Baseline freeze: CK17 segments unchanged; no refit.",
            "- Primary axis: true-mass/transit-radius rows only.",
            "- Diagnostic axis: minimum-mass rows are excluded from headline metrics.",
            "- Controls: per-class median, shuffled-label, and matched-size controls.",
            "- Promotion boundary: sandbox-only; no canonical result, prediction, "
            "claim, or knowledge output.",
            "",
            "## Checks",
            "",
            "| name | status | notes |",
            "| --- | --- | --- |",
            "| data_boundary | PASS | Only committed snapshot rows are read. |",
            "| baseline_freeze | PASS | CK17 frozen segments are reused without refit. |",
            "| true_mass_axis | PASS | True-mass/transit-radius rows are primary. |",
            "| control_floor | PASS | Three controls per executed hypothesis. |",
            "| promotion_boundary | PASS | Sandbox-only output. |",
            "",
        ]
    )


def _render_review_summary(metrics: dict[str, Any]) -> str:
    lines = [
        "# Review summary",
        "",
        f"- Verdict: **{metrics['verdict']}**",
        f"- Snapshot: `{metrics['snapshot_path']}`",
        (
            "- Eligible true-mass/transit-radius rows: "
            f"{metrics['loader_summary']['eligible_true_mass_with_transit_radius']}"
        ),
        (
            "- Hypotheses generated / executed: "
            f"{metrics['generated_hypothesis_count']} / "
            f"{metrics['executed_hypothesis_count']}"
        ),
        "",
        "## Executed hypothesis outcomes",
        "",
    ]
    for hypothesis_id, result in metrics["hypotheses"].items():
        if result["role"] != "executed_hypothesis":
            continue
        cls = result["classification"]
        stats = result["candidate_stats"]
        lines.append(
            f"- `{hypothesis_id}` ({result['label']}): {cls['outcome']}; "
            f"count = {stats['count']}; "
            "delta_eligible = "
            f"{_fmt(cls['delta_log10_rmse_candidate_minus_eligible'])}; "
            "delta_adverse_control = "
            f"{_fmt(cls['delta_log10_rmse_candidate_minus_adverse_control'])}"
        )
    lines.extend(
        [
            "",
            "The pilot preserves generated-only, null, and weaker-control "
            "outcomes in sandbox artifacts. No claim or canonical result is "
            "promoted by this run.",
            "",
        ]
    )
    return "\n".join(lines)


def _build_agent_run_payload(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "task_id": TASK_ID,
        "status": "SANDBOX_COMPLETE",
        "sandbox_only": True,
        "created_by": {
            "contributor_id": "master",
            "agent_id": "codex",
        },
        "proposal_paths": {
            "hypothesis": HYPOTHESIS_PATH,
            "experiment": EXPERIMENT_PATH,
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
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": "Only committed snapshot rows are read; no live fetch.",
                },
                {
                    "name": "baseline_freeze",
                    "status": "PASS",
                    "notes": "CK17 frozen segments are reused without refit.",
                },
                {
                    "name": "true_mass_axis",
                    "status": "PASS",
                    "notes": "True-mass/transit-radius rows are the primary axis.",
                },
                {
                    "name": "control_floor",
                    "status": "PASS",
                    "notes": (
                        "Executed hypotheses include per-class median, "
                        "shuffled-label, and matched-size controls."
                    ),
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": "No canonical result, prediction, claim, or knowledge output.",
                },
            ],
        },
        "limitations": [
            "Residual hypotheses use committed catalog fields and frozen CK17 residuals only.",
            "The shuffled-label control is one deterministic draw, not a Monte Carlo distribution.",
            "Controls share the same eligible true-mass surface and are diagnostic, not causal.",
            "Minimum-mass rows are reported only as sparse diagnostics.",
            "No composition, habitability, biosignature, target-priority, prediction, claim, or knowledge output is authorized.",
        ],
        "verdict": metrics["verdict"],
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review before any canonical result, prediction "
                "registry entry, claim update, knowledge edit, or narrower "
                "follow-up task."
            ),
        },
    }


def write_outputs(
    metrics: dict[str, Any],
    *,
    out: Path,
    report: Path,
    agent_run: Path,
    limitations: Path,
    preflight: Path,
    review_summary: Path,
    review: Path,
) -> None:
    for path in (out, report, agent_run, limitations, preflight, review_summary, review):
        path.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2, sort_keys=True)
        fh.write("\n")
    report.write_text(_render_report(metrics), encoding="utf-8")
    limitations.write_text(_render_limitations(metrics), encoding="utf-8")
    preflight.write_text(_render_preflight(metrics), encoding="utf-8")
    review_summary.write_text(_render_review_summary(metrics), encoding="utf-8")
    review.write_text(_render_review(metrics), encoding="utf-8")
    with agent_run.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(_build_agent_run_payload(metrics), fh, sort_keys=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT_PATH)
    parser.add_argument("--out", type=Path, default=DEFAULT_METRICS_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--agent-run", type=Path, default=DEFAULT_AGENT_RUN_PATH)
    parser.add_argument("--limitations", type=Path, default=DEFAULT_LIMITATIONS_PATH)
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT_PATH)
    parser.add_argument("--review-summary", type=Path, default=DEFAULT_REVIEW_SUMMARY_PATH)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW_PATH)
    args = parser.parse_args(argv)
    metrics = build_metrics(args.snapshot)
    write_outputs(
        metrics,
        out=args.out,
        report=args.report,
        agent_run=args.agent_run,
        limitations=args.limitations,
        preflight=args.preflight,
        review_summary=args.review_summary,
        review=args.review,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
