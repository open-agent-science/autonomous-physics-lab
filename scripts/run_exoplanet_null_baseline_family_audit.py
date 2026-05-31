"""TASK-0483 exoplanet null-baseline family audit.

Compares the frozen CK17-style radius baseline with deterministic null
baseline families on the committed PSCompPars snapshot only. The audit is
sandbox-only: no live fetch, baseline refit, composition inference,
habitability wording, target-priority output, prediction entry, canonical
result, claim update, or knowledge edit is produced.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any, Callable

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.datasets.exoplanets import apply_inclusion_filters, load_exoplanet_snapshot  # noqa: E402
from physics_lab.engines.exoplanet_mass_radius import (  # noqa: E402
    chen_kipping_predict_radius,
    planet_class_for_mass,
)

AGENT_RUN_ID = "AGENT-RUN-0050"
TASK_ID = "TASK-0483"
CAMPAIGN_PROFILE_ID = "exoplanet-mass-radius"

DEFAULT_SNAPSHOT_PATH = REPO_ROOT / "data/exoplanets/exo-0001-pscomppars-snapshot.yaml"
DEFAULT_AGENT_RUN_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
DEFAULT_METRICS_PATH = DEFAULT_AGENT_RUN_DIR / "metrics.json"
DEFAULT_REPORT_PATH = DEFAULT_AGENT_RUN_DIR / "report.md"
DEFAULT_AGENT_RUN_PATH = DEFAULT_AGENT_RUN_DIR / "agent_run.yaml"
DEFAULT_LIMITATIONS_PATH = DEFAULT_AGENT_RUN_DIR / "limitations.md"
DEFAULT_PREFLIGHT_PATH = DEFAULT_AGENT_RUN_DIR / "preflight.md"
DEFAULT_REVIEW_SUMMARY_PATH = DEFAULT_AGENT_RUN_DIR / "review_summary.md"
DEFAULT_REVIEW_PATH = REPO_ROOT / "docs/reviews/exoplanet-null-baseline-family-audit.md"

MIN_SLICE_ROW_COUNT = 30


def _is_positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value)) and value > 0


def _mass_value(entry: dict[str, Any]) -> float:
    return float(entry["mass"]["value"])


def _radius_value(entry: dict[str, Any]) -> float:
    return float(entry["radius"]["value"])


def _row_has_axis(entry: dict[str, Any], *, mass_class: str) -> bool:
    mass = entry.get("mass") or {}
    radius = entry.get("radius") or {}
    return (
        mass.get("mass_class") == mass_class
        and radius.get("radius_class") == "transit_radius"
        and _is_positive_number(mass.get("value"))
        and _is_positive_number(radius.get("value"))
    )


def _relative_uncertainty(component: dict[str, Any]) -> float | None:
    value = component.get("value")
    if not _is_positive_number(value):
        return None
    candidates = [
        abs(float(v))
        for v in (component.get("uncertainty_upper"), component.get("uncertainty_lower"))
        if isinstance(v, (int, float)) and math.isfinite(float(v))
    ]
    if not candidates:
        return None
    return max(candidates) / float(value)


def _combined_uncertainty(entry: dict[str, Any]) -> float | None:
    values = [
        value
        for value in (
            _relative_uncertainty(entry.get("mass") or {}),
            _relative_uncertainty(entry.get("radius") or {}),
        )
        if value is not None
    ]
    return max(values) if values else None


def _uncertainty_band(entry: dict[str, Any]) -> str:
    value = _combined_uncertainty(entry)
    if value is None:
        return "missing"
    if value <= 0.05:
        return "tight_le5pct"
    if value <= 0.15:
        return "moderate_5_15pct"
    return "loose_gt15pct"


def _median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def _stats(residuals: list[float]) -> dict[str, Any]:
    if not residuals:
        return {"count": 0, "log10_rmse": None, "log10_mae": None, "log10_bias": None}
    return {
        "count": len(residuals),
        "log10_rmse": math.sqrt(sum(v * v for v in residuals) / len(residuals)),
        "log10_mae": sum(abs(v) for v in residuals) / len(residuals),
        "log10_bias": sum(residuals) / len(residuals),
    }


def _log_radius(entry: dict[str, Any]) -> float:
    return math.log10(_radius_value(entry))


def _log_mass(entry: dict[str, Any]) -> float:
    return math.log10(_mass_value(entry))


def _ck17_prediction(entry: dict[str, Any]) -> float | None:
    predicted = chen_kipping_predict_radius(_mass_value(entry))
    if not _is_positive_number(predicted):
        return None
    return math.log10(float(predicted))


def _group_median_predictions(
    rows: list[dict[str, Any]],
    *,
    group_key: Callable[[dict[str, Any]], str],
) -> dict[str, float]:
    if not rows:
        return {}
    grouped: dict[str, list[float]] = {}
    for row in rows:
        grouped.setdefault(group_key(row), []).append(_log_radius(row))
    medians = {key: float(_median(values)) for key, values in grouped.items() if values}
    fallback = float(_median([_log_radius(row) for row in rows]))
    return {row["row_id"]: medians.get(group_key(row), fallback) for row in rows}


def _nearest_other_predictions(
    rows: list[dict[str, Any]],
    *,
    key: Callable[[dict[str, Any]], float],
) -> dict[str, float]:
    predictions: dict[str, float] = {}
    for row in rows:
        candidates = [other for other in rows if other["row_id"] != row["row_id"]]
        if not candidates:
            continue
        nearest = min(candidates, key=lambda other: (abs(key(other) - key(row)), other["row_id"]))
        predictions[row["row_id"]] = _log_radius(nearest)
    return predictions


def _baseline_predictions(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    if not rows:
        return {
            "ck17_frozen": {},
            "per_class_median": {},
            "nearest_mass_neighbor": {},
            "nearest_radius_neighbor": {},
            "uncertainty_band_median": {},
        }
    return {
        "ck17_frozen": {
            row["row_id"]: pred
            for row in rows
            if (pred := _ck17_prediction(row)) is not None
        },
        "per_class_median": _group_median_predictions(
            rows,
            group_key=lambda row: planet_class_for_mass(_mass_value(row)),
        ),
        "nearest_mass_neighbor": _nearest_other_predictions(rows, key=_log_mass),
        "nearest_radius_neighbor": _nearest_other_predictions(rows, key=_log_radius),
        "uncertainty_band_median": _group_median_predictions(rows, group_key=_uncertainty_band),
    }


def _slice_predicates() -> dict[str, Callable[[dict[str, Any]], bool]]:
    return {
        "compact_radius_lt1p5Re": lambda row: _radius_value(row) < 1.5,
        "sub_neptune_radius_1p5_4Re": lambda row: 1.5 <= _radius_value(row) < 4.0,
        "jovian_radius_8_16Re": lambda row: 8.0 <= _radius_value(row) < 16.0,
        "hot_jupiter_period_lt10d_radius_ge8Re": lambda row: (
            8.0 <= _radius_value(row) < 16.0
            and _is_positive_number(row.get("orbital_period_days"))
            and float(row["orbital_period_days"]) < 10.0
        ),
    }


def _evaluate_surface(rows: list[dict[str, Any]]) -> dict[str, Any]:
    predictions = _baseline_predictions(rows)
    axis_stats: dict[str, Any] = {}
    for baseline_id, pred_by_row in predictions.items():
        residuals = [
            _log_radius(row) - pred_by_row[row["row_id"]]
            for row in rows
            if row["row_id"] in pred_by_row
        ]
        axis_stats[baseline_id] = _stats(residuals)

    slices: dict[str, Any] = {}
    for slice_id, predicate in _slice_predicates().items():
        target_rows = [row for row in rows if predicate(row)]
        baseline_stats: dict[str, Any] = {}
        for baseline_id, pred_by_row in predictions.items():
            residuals = [
                _log_radius(row) - pred_by_row[row["row_id"]]
                for row in target_rows
                if row["row_id"] in pred_by_row
            ]
            baseline_stats[baseline_id] = _stats(residuals)
        ck17_rmse = baseline_stats["ck17_frozen"]["log10_rmse"]
        best_null = min(
            (
                (baseline_id, stats["log10_rmse"])
                for baseline_id, stats in baseline_stats.items()
                if baseline_id != "ck17_frozen" and stats["log10_rmse"] is not None
            ),
            key=lambda item: item[1],
            default=(None, None),
        )
        classification = "underpowered_slice"
        if len(target_rows) >= MIN_SLICE_ROW_COUNT and ck17_rmse is not None and best_null[1] is not None:
            classification = (
                "ck17_beats_null_family"
                if ck17_rmse < best_null[1]
                else "null_family_matches_or_beats_ck17"
            )
        slices[slice_id] = {
            "count": len(target_rows),
            "baseline_stats": baseline_stats,
            "best_null_baseline": best_null[0],
            "classification": classification,
        }
    return {"axis_stats": axis_stats, "slices": slices}


def run_audit(snapshot_path: Path) -> dict[str, Any]:
    snapshot = load_exoplanet_snapshot(snapshot_path)
    filtered = apply_inclusion_filters(snapshot)
    entries = filtered.included_rows
    try:
        snapshot_label = str(snapshot_path.relative_to(REPO_ROOT))
    except ValueError:
        snapshot_label = str(snapshot_path)
    axes = {
        "true_mass_with_transit_radius": [
            entry for entry in entries if _row_has_axis(entry, mass_class="true_mass")
        ],
        "minimum_mass_with_transit_radius": [
            entry for entry in entries if _row_has_axis(entry, mass_class="minimum_mass_msini")
        ],
    }
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "snapshot": snapshot_label,
        "minimum_slice_row_count": MIN_SLICE_ROW_COUNT,
        "baseline_families": [
            "ck17_frozen",
            "per_class_median",
            "nearest_mass_neighbor",
            "nearest_radius_neighbor",
            "uncertainty_band_median",
        ],
        "axes": {axis: _evaluate_surface(rows) for axis, rows in axes.items()},
        "audit_class": "BENCHMARK_CONTROL_PANEL",
        "verdict": "INCONCLUSIVE",
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _report(metrics: dict[str, Any]) -> str:
    lines = [
        "# Exoplanet null-baseline family audit",
        "",
        f"- Agent run: `{AGENT_RUN_ID}`",
        f"- Task: `{TASK_ID}`",
        "- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`",
        "- Verdict: `INCONCLUSIVE`",
        "- Audit class: `BENCHMARK_CONTROL_PANEL`",
        "",
        "This sandbox audit compares the frozen CK17-style baseline with deterministic null baselines.",
        "It does not infer composition, habitability, target priority, or a new mass-radius law.",
        "",
        "## Axis and slice summary",
        "",
        "| axis | slice | rows | CK17 RMSE | best null | classification |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for axis, axis_payload in metrics["axes"].items():
        for slice_id, payload in axis_payload["slices"].items():
            ck17 = payload["baseline_stats"]["ck17_frozen"]["log10_rmse"]
            ck17_label = "n/a" if ck17 is None else f"{ck17:.6f}"
            lines.append(
                f"| `{axis}` | `{slice_id}` | {payload['count']} | {ck17_label} | "
                f"`{payload['best_null_baseline']}` | `{payload['classification']}` |"
            )
    lines.extend(
        [
            "",
            "## Output Routing",
            "",
            "- Task verdict: `INCONCLUSIVE`.",
            "- Canonical destination: sandbox-only `agent_runs/AGENT-RUN-0050/` plus review note.",
            "- Review tier: `none`.",
            "- Gate A: not attempted.",
            "- Gate B: not attempted.",
            "- Claim impact: no claim change.",
            "- Knowledge impact: no knowledge change.",
        ]
    )
    return "\n".join(lines) + "\n"


def _agent_run_yaml() -> dict[str, Any]:
    return {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "task_id": TASK_ID,
        "status": "SANDBOX_COMPLETE",
        "sandbox_only": True,
        "created_by": {"contributor_id": "roman", "agent_id": "codex"},
        "proposal_paths": {
            "hypothesis": "hypothesis_proposals/exoplanet-mass/HYP-PROPOSAL-0051-compact-subneptune-residual-pilot.yaml",
            "experiment": "experiment_proposals/exoplanet-mass/EXP-PROPOSAL-0017-compact-subneptune-residual-pilot.yaml",
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
                {"name": "data_boundary", "status": "PASS", "notes": "Committed snapshot only; no live fetch."},
                {"name": "baseline_freeze", "status": "PASS", "notes": "CK17 baseline reused without refit."},
                {"name": "null_family_panel", "status": "PASS", "notes": "Four deterministic null families compared."},
                {"name": "promotion_boundary", "status": "PASS", "notes": "No result, prediction, claim, or knowledge output."},
            ],
        },
        "limitations": [
            "Nearest-radius neighbor is a diagnostic control that uses observed radius and is not prospective.",
            "Minimum-mass axis remains sparse and diagnostic-only.",
            "Null baselines are deterministic controls, not physical models.",
            "No composition, habitability, target-priority, prediction, claim, or knowledge output is authorized.",
        ],
        "verdict": "INCONCLUSIVE",
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": "Maintainer review before any null-baseline control panel informs follow-up hypothesis wording.",
        },
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT_PATH)
    parser.add_argument("--out", type=Path, default=DEFAULT_METRICS_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--agent-run", type=Path, default=DEFAULT_AGENT_RUN_PATH)
    parser.add_argument("--limitations", type=Path, default=DEFAULT_LIMITATIONS_PATH)
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT_PATH)
    parser.add_argument("--review-summary", type=Path, default=DEFAULT_REVIEW_SUMMARY_PATH)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW_PATH)
    args = parser.parse_args(argv)

    metrics = run_audit(args.snapshot)
    _write_json(args.out, metrics)
    report = _report(metrics)
    _write_text(args.report, report)
    _write_text(args.review, report)
    _write_text(args.limitations, "\n".join(f"- {item}" for item in _agent_run_yaml()["limitations"]) + "\n")
    _write_text(args.preflight, "# Preflight\n\nAll checks passed; committed snapshot only; no live fetch.\n")
    _write_text(args.review_summary, "# Review Summary\n\nBENCHMARK_CONTROL_PANEL; sandbox-only.\n")
    args.agent_run.parent.mkdir(parents=True, exist_ok=True)
    args.agent_run.write_text(yaml.safe_dump(_agent_run_yaml(), sort_keys=False), encoding="utf-8")


if __name__ == "__main__":
    main()
