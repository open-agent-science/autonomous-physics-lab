"""Run the frozen Chen-Kipping median-relation audit for TASK-0866."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from physics_lab.datasets.exoplanets import load_exoplanet_snapshot
from physics_lab.engines.exoplanet_mass_radius import (
    CHEN_KIPPING_SEGMENTS,
    JUP_MASS_TO_EARTH_MASS,
    chen_kipping_predict_radius,
    chen_kipping_segment_for_mass,
)


TASK_ID = "TASK-0866"
AGENT_RUN_ID = "AGENT-RUN-0088"
CAMPAIGN_PROFILE_ID = "exoplanet-mass-radius"
REPO_ROOT = Path(__file__).resolve().parents[1]
PRIMARY_SNAPSHOT = REPO_ROOT / "data/exoplanets/exo-0002-pscomppars-snapshot.yaml"
COMPATIBILITY_SNAPSHOT = REPO_ROOT / "data/exoplanets/exo-0001-pscomppars-snapshot.yaml"
OUTPUT_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
REVIEW_PATH = REPO_ROOT / "docs/reviews/exoplanet-chen-kipping-published-relation-audit.md"
BROWN_DWARF_CAP_MEARTH = 13.0 * JUP_MASS_TO_EARTH_MASS
TEST_BUCKET_MODULUS = 5
TEST_BUCKET = 0
SHUFFLE_SEEDS = tuple(range(1701, 1733))
CONTROL_IDS = (
    "global_median",
    "regime_median",
    "global_power_law",
    "regime_power_law",
    "shuffled_label_power_law",
)


def _is_positive_finite(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and float(value) > 0.0
    )


def _is_primary_row(row: dict[str, Any]) -> bool:
    mass = row.get("mass") or {}
    radius = row.get("radius") or {}
    return (
        row.get("inclusion_status") == "included"
        and row.get("row_class") == "direct_mass_radius_measurement"
        and mass.get("mass_class") == "true_mass"
        and radius.get("radius_class") == "transit_radius"
        and _is_positive_finite(mass.get("value"))
        and _is_positive_finite(radius.get("value"))
    )


def _is_minimum_mass_diagnostic(row: dict[str, Any]) -> bool:
    mass = row.get("mass") or {}
    radius = row.get("radius") or {}
    return (
        row.get("inclusion_status") == "included"
        and mass.get("mass_class") == "minimum_mass_msini"
        and radius.get("radius_class") == "transit_radius"
        and _is_positive_finite(mass.get("value"))
        and _is_positive_finite(radius.get("value"))
    )


def _has_complete_uncertainty(row: dict[str, Any]) -> bool:
    for block_name in ("mass", "radius"):
        block = row.get(block_name) or {}
        if not _is_positive_finite(block.get("uncertainty_upper")):
            return False
        lower = block.get("uncertainty_lower")
        if not isinstance(lower, (int, float)) or not math.isfinite(float(lower)):
            return False
        if abs(float(lower)) <= 0.0:
            return False
    return True


def _mass(row: dict[str, Any]) -> float:
    return float(row["mass"]["value"])


def _radius(row: dict[str, Any]) -> float:
    return float(row["radius"]["value"])


def _regime(row: dict[str, Any]) -> str:
    return chen_kipping_segment_for_mass(_mass(row)).name


def _holdout_key(row: dict[str, Any]) -> str:
    return str(row.get("planet_name") or row["row_id"]).strip().casefold()


def _is_test_row(row: dict[str, Any]) -> bool:
    digest = hashlib.sha256(_holdout_key(row).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % TEST_BUCKET_MODULUS == TEST_BUCKET


def _split_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    train = [row for row in rows if not _is_test_row(row)]
    test = [row for row in rows if _is_test_row(row)]
    return train, test


def _median(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot compute median of an empty sequence")
    return float(statistics.median(values))


def _fit_power_law(
    rows: list[dict[str, Any]], y_values: list[float] | None = None
) -> dict[str, float]:
    if len(rows) < 2:
        raise ValueError("power-law fit requires at least two rows")
    x = [math.log10(_mass(row)) for row in rows]
    y = y_values if y_values is not None else [math.log10(_radius(row)) for row in rows]
    x_mean = statistics.fmean(x)
    y_mean = statistics.fmean(y)
    denominator = sum((value - x_mean) ** 2 for value in x)
    slope = (
        0.0
        if denominator == 0.0
        else sum(
            (x_value - x_mean) * (y_value - y_mean) for x_value, y_value in zip(x, y, strict=True)
        )
        / denominator
    )
    return {"intercept": y_mean - slope * x_mean, "slope": slope}


def _line_prediction(model: dict[str, float], row: dict[str, Any]) -> float:
    return model["intercept"] + model["slope"] * math.log10(_mass(row))


def _freeze_controls(train: list[dict[str, Any]]) -> dict[str, Any]:
    global_median = _median([math.log10(_radius(row)) for row in train])
    regime_medians: dict[str, float] = {}
    regime_models: dict[str, dict[str, float]] = {}
    for segment in CHEN_KIPPING_SEGMENTS:
        segment_rows = [row for row in train if _regime(row) == segment.name]
        if segment_rows:
            regime_medians[segment.name] = _median(
                [math.log10(_radius(row)) for row in segment_rows]
            )
        if len(segment_rows) >= 2:
            regime_models[segment.name] = _fit_power_law(segment_rows)

    global_model = _fit_power_law(train)
    shuffled_models: list[dict[str, float]] = []
    observed_y = [math.log10(_radius(row)) for row in train]
    for seed in SHUFFLE_SEEDS:
        shuffled_y = observed_y.copy()
        random.Random(seed).shuffle(shuffled_y)
        shuffled_models.append(_fit_power_law(train, shuffled_y))

    return {
        "global_median": global_median,
        "regime_medians": regime_medians,
        "global_power_law": global_model,
        "regime_power_laws": regime_models,
        "shuffled_power_laws": shuffled_models,
        "train_count": len(train),
    }


def _predictions(rows: list[dict[str, Any]], controls: dict[str, Any]) -> dict[str, list[float]]:
    predictions: dict[str, list[float]] = {
        "chen_kipping_frozen": [],
        "global_median": [],
        "regime_median": [],
        "global_power_law": [],
        "regime_power_law": [],
        "shuffled_label_power_law": [],
    }
    for row in rows:
        regime = _regime(row)
        predictions["chen_kipping_frozen"].append(
            math.log10(chen_kipping_predict_radius(_mass(row)))
        )
        predictions["global_median"].append(controls["global_median"])
        predictions["regime_median"].append(
            controls["regime_medians"].get(regime, controls["global_median"])
        )
        predictions["global_power_law"].append(_line_prediction(controls["global_power_law"], row))
        regime_model = controls["regime_power_laws"].get(regime, controls["global_power_law"])
        predictions["regime_power_law"].append(_line_prediction(regime_model, row))
        shuffled_values = [
            _line_prediction(model, row) for model in controls["shuffled_power_laws"]
        ]
        predictions["shuffled_label_power_law"].append(_median(shuffled_values))
    return predictions


def _metric_summary(rows: list[dict[str, Any]], predictions: list[float]) -> dict[str, Any]:
    observed = [math.log10(_radius(row)) for row in rows]
    residuals = [
        actual - predicted for actual, predicted in zip(observed, predictions, strict=True)
    ]
    if not residuals:
        return {
            "count": 0,
            "log10_mae": None,
            "log10_rmse": None,
            "log10_bias": None,
            "median_log10_residual": None,
            "fraction_within_factor_2": None,
        }
    return {
        "count": len(residuals),
        "log10_mae": statistics.fmean(abs(value) for value in residuals),
        "log10_rmse": math.sqrt(statistics.fmean(value * value for value in residuals)),
        "log10_bias": statistics.fmean(residuals),
        "median_log10_residual": _median(residuals),
        "fraction_within_factor_2": statistics.fmean(
            1.0 if abs(value) <= math.log10(2.0) else 0.0 for value in residuals
        ),
    }


def _radius_log_sigma(row: dict[str, Any]) -> float:
    radius = row["radius"]
    absolute_sigma = 0.5 * (
        abs(float(radius["uncertainty_upper"])) + abs(float(radius["uncertainty_lower"]))
    )
    return absolute_sigma / _radius(row) / math.log(10.0)


def _weighted_metric_summary(
    rows: list[dict[str, Any]], predictions: list[float]
) -> dict[str, Any]:
    selected = [
        (row, prediction)
        for row, prediction in zip(rows, predictions, strict=True)
        if _has_complete_uncertainty(row)
    ]
    if not selected:
        return {"count": 0, "inverse_variance_log10_mae": None, "reduced_chi_square": None}
    weighted_absolute = 0.0
    weighted_square = 0.0
    weight_sum = 0.0
    for row, prediction in selected:
        sigma = _radius_log_sigma(row)
        weight = 1.0 / (sigma * sigma)
        residual = math.log10(_radius(row)) - prediction
        weighted_absolute += weight * abs(residual)
        weighted_square += (residual / sigma) ** 2
        weight_sum += weight
    return {
        "count": len(selected),
        "inverse_variance_log10_mae": weighted_absolute / weight_sum,
        "reduced_chi_square": weighted_square / len(selected),
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _evaluate_snapshot(path: Path) -> dict[str, Any]:
    snapshot = load_exoplanet_snapshot(path)
    entries = snapshot["entries"]
    direct_rows = [row for row in entries if _is_primary_row(row)]
    boundary_rows = [row for row in direct_rows if _mass(row) >= BROWN_DWARF_CAP_MEARTH]
    primary_rows = [row for row in direct_rows if _mass(row) < BROWN_DWARF_CAP_MEARTH]
    minimum_rows = [
        row
        for row in entries
        if _is_minimum_mass_diagnostic(row) and _mass(row) < BROWN_DWARF_CAP_MEARTH
    ]
    train, test = _split_rows(primary_rows)
    if len(train) < 2 or not test:
        raise ValueError(f"snapshot {_display_path(path)} cannot support the frozen split")
    controls = _freeze_controls(train)
    predictions = _predictions(test, controls)
    point_metrics = {
        model_id: _metric_summary(test, values) for model_id, values in predictions.items()
    }
    uncertainty_metrics = {
        model_id: _weighted_metric_summary(test, values) for model_id, values in predictions.items()
    }
    per_regime: dict[str, Any] = {}
    for segment in CHEN_KIPPING_SEGMENTS:
        indices = [index for index, row in enumerate(test) if _regime(row) == segment.name]
        regime_rows = [test[index] for index in indices]
        per_regime[segment.name] = {
            model_id: _metric_summary(regime_rows, [values[index] for index in indices])
            for model_id, values in predictions.items()
        }

    shuffled_seed_metrics = []
    for seed, model in zip(SHUFFLE_SEEDS, controls["shuffled_power_laws"], strict=True):
        seed_predictions = [_line_prediction(model, row) for row in test]
        summary = _metric_summary(test, seed_predictions)
        shuffled_seed_metrics.append({"seed": seed, "log10_mae": summary["log10_mae"]})

    minimum_predictions = [
        math.log10(chen_kipping_predict_radius(_mass(row))) for row in minimum_rows
    ]
    return {
        "snapshot": _display_path(path),
        "dataset_id": snapshot["dataset_id"],
        "input_sha256": _sha256(path),
        "counts": {
            "all_entries": len(entries),
            "direct_true_mass_transit_radius": len(direct_rows),
            "primary_below_13_mjup": len(primary_rows),
            "primary_with_complete_uncertainty": sum(
                _has_complete_uncertainty(row) for row in primary_rows
            ),
            "boundary_at_or_above_13_mjup": len(boundary_rows),
            "minimum_mass_diagnostic_below_13_mjup": len(minimum_rows),
            "train": len(train),
            "test": len(test),
            "test_with_complete_uncertainty": sum(_has_complete_uncertainty(row) for row in test),
        },
        "train_regime_counts": dict(sorted(Counter(_regime(row) for row in train).items())),
        "test_regime_counts": dict(sorted(Counter(_regime(row) for row in test).items())),
        "test_detection_method_counts": dict(
            sorted(Counter(str(row.get("detection_method")) for row in test).items())
        ),
        "fitted_controls": {
            "global_median_log10_radius": controls["global_median"],
            "regime_median_log10_radius": controls["regime_medians"],
            "global_power_law": controls["global_power_law"],
            "regime_power_laws": controls["regime_power_laws"],
            "shuffled_seed_count": len(SHUFFLE_SEEDS),
        },
        "point_metrics": point_metrics,
        "uncertainty_aware_metrics": uncertainty_metrics,
        "per_regime_point_metrics": per_regime,
        "shuffled_seed_metrics": shuffled_seed_metrics,
        "minimum_mass_diagnostic": {
            "classification": "diagnostic_only_not_primary",
            "point_metrics": _metric_summary(minimum_rows, minimum_predictions),
        },
        "probabilistic_calibration": {
            "status": "NOT_ATTEMPTED",
            "reason": "The frozen repository implementation returns the published median relation without predictive intervals.",
        },
    }


def _gate(primary: dict[str, Any], compatibility: dict[str, Any]) -> dict[str, Any]:
    primary_metrics = primary["point_metrics"]
    compatibility_metrics = compatibility["point_metrics"]
    candidate = primary_metrics["chen_kipping_frozen"]["log10_mae"]
    checks: dict[str, bool] = {
        "primary_test_count_at_least_200": primary["counts"]["test"] >= 200,
        "primary_uncertainty_test_count_at_least_100": primary["counts"][
            "test_with_complete_uncertainty"
        ]
        >= 100,
        "compatibility_test_count_at_least_200": compatibility["counts"]["test"] >= 200,
        "probabilistic_scope_not_overstated": primary["probabilistic_calibration"]["status"]
        == "NOT_ATTEMPTED",
    }
    for control_id in CONTROL_IDS:
        checks[f"primary_beats_{control_id}"] = candidate < primary_metrics[control_id]["log10_mae"]
    compatibility_candidate = compatibility_metrics["chen_kipping_frozen"]["log10_mae"]
    for control_id in ("global_median", "regime_median", "shuffled_label_power_law"):
        checks[f"compatibility_beats_{control_id}"] = (
            compatibility_candidate < compatibility_metrics[control_id]["log10_mae"]
        )
    failed = [name for name, passed in checks.items() if not passed]
    return {
        "status": "PASS" if not failed else "FAIL",
        "checks": checks,
        "failed_checks": failed,
        "candidate_primary_log10_mae": candidate,
        "best_primary_control": min(
            CONTROL_IDS, key=lambda item: primary_metrics[item]["log10_mae"]
        ),
        "best_primary_control_log10_mae": min(
            primary_metrics[item]["log10_mae"] for item in CONTROL_IDS
        ),
        "rule": "CK17 must beat every declared control on EXO-0002 and the three non-parametric/shuffled controls on EXO-0001; minimum row-count and scope checks must pass.",
    }


def run_audit(primary_path: Path, compatibility_path: Path) -> dict[str, Any]:
    primary = _evaluate_snapshot(primary_path)
    compatibility = _evaluate_snapshot(compatibility_path)
    gate = _gate(primary, compatibility)
    outcome = (
        "SCOPED_MEDIAN_RELATION_PASS" if gate["status"] == "PASS" else "CONTROL_SENSITIVE_NEGATIVE"
    )
    return {
        "task_id": TASK_ID,
        "agent_run_id": AGENT_RUN_ID,
        "command": "python scripts/run_exoplanet_chen_kipping_published_relation_audit.py",
        "relation": {
            "reference": "Chen and Kipping (2017), ApJ 834, 17, DOI 10.3847/1538-4357/834/1/17",
            "implementation": "physics_lab/engines/exoplanet_mass_radius.py",
            "direction": "mass_to_radius",
            "kind": "frozen_piecewise_median",
            "refit": False,
            "segments": [
                {
                    "name": segment.name,
                    "mass_lower_mearth": segment.mass_lower_mearth,
                    "mass_upper_mearth": (
                        None if math.isinf(segment.mass_upper_mearth) else segment.mass_upper_mearth
                    ),
                    "slope": segment.slope_log_r_per_log_m,
                    "prefactor": segment.prefactor_r_earth_per_mass_unit_pow_slope,
                }
                for segment in CHEN_KIPPING_SEGMENTS
            ],
        },
        "frozen_protocol": {
            "primary_snapshot": _display_path(primary_path),
            "compatibility_snapshot": _display_path(compatibility_path),
            "brown_dwarf_cap_mearth": BROWN_DWARF_CAP_MEARTH,
            "split": "sha256(casefold(planet_name)) modulo 5; bucket 0 test, buckets 1-4 train",
            "shuffle_seeds": list(SHUFFLE_SEEDS),
            "controls": list(CONTROL_IDS),
            "primary_axis": "true_mass_with_transit_radius_below_13_mjup",
            "minimum_mass_axis": "diagnostic_only",
        },
        "snapshots": {"primary_exo_0002": primary, "compatibility_exo_0001": compatibility},
        "promotion_gate": gate,
        "scientific_outcome": outcome,
        "artifact_routing": {
            "canonical_destination": f"agent_runs/{AGENT_RUN_ID}/ plus docs/reviews/exoplanet-chen-kipping-published-relation-audit.md",
            "review_tier": "none",
            "gate_a": "not_passed"
            if gate["status"] == "FAIL"
            else "eligible_for_separate_result_packaging_review",
            "gate_b": "not_attempted",
            "claim_impact": "none",
            "knowledge_impact": "none",
            "residual_lane": "monitor_only",
        },
    }


def _format_metric(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}"


def _report(metrics: dict[str, Any]) -> str:
    primary = metrics["snapshots"]["primary_exo_0002"]
    compatibility = metrics["snapshots"]["compatibility_exo_0001"]
    gate = metrics["promotion_gate"]
    lines = [
        "# TASK-0866 - Chen-Kipping Published-Relation Audit",
        "",
        f"**Outcome:** `{metrics['scientific_outcome']}`  ",
        f"**Promotion gate:** `{gate['status']}`  ",
        f"**Run:** `{AGENT_RUN_ID}`",
        "",
        "## Scope",
        "",
        "This audit tests the frozen Chen and Kipping (2017) mass-to-radius median relation on committed EXO-0002 rows, with EXO-0001 as a compatibility snapshot. No relation parameter, breakpoint, subset rule, or control was changed after scoring.",
        "",
        "The tested implementation is a deterministic median equation, not the full probabilistic Forecaster model. Interval calibration and predictive coverage were not tested.",
        "",
        "## Frozen Inputs And Split",
        "",
        "- Primary: `data/exoplanets/exo-0002-pscomppars-snapshot.yaml`.",
        "- Compatibility: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`.",
        "- Primary axis: included direct true-mass plus transit-radius rows below 13 Jupiter masses.",
        "- Minimum-mass rows: reported separately as diagnostic-only.",
        "- Split: stable planet-name SHA-256 bucket, 80% train and 20% test.",
        "- Controls: train-only global median, CK17-regime median, global power law, per-regime power law, and 32 shuffled-label power laws.",
        "",
        "## Subset Counts",
        "",
        "| snapshot | entries | direct rows | primary rows | uncertainty rows | boundary rows | train | test |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for snapshot in (primary, compatibility):
        counts = snapshot["counts"]
        lines.append(
            f"| `{snapshot['dataset_id']}` | {counts['all_entries']} | "
            f"{counts['direct_true_mass_transit_radius']} | {counts['primary_below_13_mjup']} | "
            f"{counts['primary_with_complete_uncertainty']} | "
            f"{counts['boundary_at_or_above_13_mjup']} | {counts['train']} | {counts['test']} |"
        )
    lines.extend(
        [
            "",
            "## Held-Out Point Metrics",
            "",
            "Lower log10 MAE and RMSE are better.",
            "",
            "| snapshot | model | log10 MAE | log10 RMSE | bias | within factor 2 |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for snapshot in (primary, compatibility):
        for model_id, summary in snapshot["point_metrics"].items():
            lines.append(
                f"| `{snapshot['dataset_id']}` | `{model_id}` | "
                f"{_format_metric(summary['log10_mae'])} | {_format_metric(summary['log10_rmse'])} | "
                f"{_format_metric(summary['log10_bias'])} | {_format_metric(summary['fraction_within_factor_2'])} |"
            )
    lines.extend(
        [
            "",
            "## Primary Per-Regime MAE",
            "",
            "| regime | test rows | CK17 | global median | regime median | global power law | regime power law | shuffled labels |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for regime, summaries in primary["per_regime_point_metrics"].items():
        lines.append(
            f"| `{regime}` | {summaries['chen_kipping_frozen']['count']} | "
            f"{_format_metric(summaries['chen_kipping_frozen']['log10_mae'])} | "
            f"{_format_metric(summaries['global_median']['log10_mae'])} | "
            f"{_format_metric(summaries['regime_median']['log10_mae'])} | "
            f"{_format_metric(summaries['global_power_law']['log10_mae'])} | "
            f"{_format_metric(summaries['regime_power_law']['log10_mae'])} | "
            f"{_format_metric(summaries['shuffled_label_power_law']['log10_mae'])} |"
        )
    primary_weighted = primary["uncertainty_aware_metrics"]
    lines.extend(
        [
            "",
            "## Uncertainty-Aware Check",
            "",
            f"The common complete-uncertainty mask contains {primary['counts']['test_with_complete_uncertainty']} EXO-0002 test rows. Inverse-variance log10 MAE is reported as a sensitivity metric; it is not Forecaster calibration.",
            "",
            "| model | weighted log10 MAE | reduced chi-square diagnostic |",
            "| --- | ---: | ---: |",
        ]
    )
    for model_id, summary in primary_weighted.items():
        lines.append(
            f"| `{model_id}` | {_format_metric(summary['inverse_variance_log10_mae'])} | "
            f"{_format_metric(summary['reduced_chi_square'])} |"
        )
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"The frozen relation has EXO-0002 held-out log10 MAE `{gate['candidate_primary_log10_mae']:.6f}`. The best declared control is `{gate['best_primary_control']}` at `{gate['best_primary_control_log10_mae']:.6f}`.",
            "",
        ]
    )
    if gate["status"] == "FAIL":
        lines.append(
            "The relation does not clear the predeclared all-controls promotion rule. This is a scoped control-sensitive negative for the median-equation audit, not a judgment about the full probabilistic model."
        )
    else:
        lines.append(
            "The relation clears the predeclared all-controls rule on the scoped median-equation audit. Canonical result packaging still requires a separate review decision."
        )
    lines.extend(
        [
            "",
            "Failed checks: "
            + (", ".join(f"`{item}`" for item in gate["failed_checks"]) or "none")
            + ".",
            "",
            "## Limitations",
            "",
            "- The two snapshots are successive composite-catalog snapshots, not independent instruments or surveys.",
            "- The repository implementation exposes only the median relation; probabilistic interval calibration remains untested.",
            "- Catalog errors and source heterogeneity are not a predictive-scatter model.",
            "- Data-derived controls are valid only for this frozen split and audit direction.",
            "- Brown-dwarf-boundary rows and minimum-mass rows do not determine the primary verdict.",
            "",
            "## Sources",
            "",
            "- Chen, J. and Kipping, D. M. (2017), ApJ 834, 17, DOI `10.3847/1538-4357/834/1/17`.",
            "- Otegi et al. (2020), A&A 634, A43, `arXiv:1911.04745`, used as transition-regime context only.",
            "",
            "## Output Routing",
            "",
            f"- Task verdict: `{metrics['scientific_outcome']}`.",
            f"- Canonical destination: sandbox `agent_runs/{AGENT_RUN_ID}/` plus this review note.",
            "- Review tier: `none`.",
            f"- Gate A: `{metrics['artifact_routing']['gate_a']}`.",
            "- Gate B: `not_attempted`.",
            "- Claim impact: none.",
            "- Knowledge impact: none.",
            "- Residual lane: `monitor_only`.",
        ]
    )
    return "\n".join(lines) + "\n"


def _agent_run(metrics: dict[str, Any]) -> dict[str, Any]:
    failed = metrics["promotion_gate"]["failed_checks"]
    return {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "task_id": TASK_ID,
        "status": "REVIEW_READY",
        "sandbox_only": True,
        "created_by": {"contributor_id": "akutenyov", "agent_id": "codex"},
        "proposal_paths": {
            "hypothesis": "hypothesis_proposals/exoplanet-mass/HYP-PROPOSAL-0049-frozen-baseline-benchmark.yaml",
            "experiment": "experiment_proposals/exoplanet-mass/EXP-PROPOSAL-0015-frozen-baseline-benchmark.yaml",
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
                    "name": "pinned_inputs",
                    "status": "PASS",
                    "notes": "EXO-0002 and EXO-0001 only; no live fetch.",
                },
                {
                    "name": "frozen_relation",
                    "status": "PASS",
                    "notes": "CK17 median segments reused without refit.",
                },
                {
                    "name": "held_out_controls",
                    "status": "PASS",
                    "notes": "Five declared control families scored on a stable test split.",
                },
                {
                    "name": "axis_separation",
                    "status": "PASS",
                    "notes": "True-mass primary and minimum-mass diagnostic rows remain separate.",
                },
            ],
        },
        "limitations": [
            "Median-equation point audit only; predictive interval calibration was not attempted.",
            "Successive composite snapshots are compatibility evidence, not independent replication.",
            "The all-controls promotion rule failed: " + ", ".join(failed) + ".",
            "Sandbox evidence only; no canonical result, claim, or knowledge artifact was created.",
        ],
        "verdict": "SANDBOX_FAIL" if failed else "SANDBOX_PASS",
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": "Maintainer review of the scoped negative and decision whether probabilistic Forecaster calibration merits a separate task.",
        },
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary", type=Path, default=PRIMARY_SNAPSHOT)
    parser.add_argument("--compatibility", type=Path, default=COMPATIBILITY_SNAPSHOT)
    parser.add_argument("--out-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--review", type=Path, default=REVIEW_PATH)
    args = parser.parse_args(argv)

    metrics = run_audit(args.primary, args.compatibility)
    report = _report(metrics)
    agent_run = _agent_run(metrics)
    _write_json(args.out_dir / "metrics.json", metrics)
    _write_text(args.out_dir / "report.md", report)
    _write_text(
        args.out_dir / "limitations.md",
        "# Limitations\n\n" + "\n".join(f"- {item}" for item in agent_run["limitations"]) + "\n",
    )
    _write_text(
        args.out_dir / "preflight.md",
        "# Preflight\n\nPinned inputs, frozen relation, stable split, declared controls, and axis separation passed.\n",
    )
    _write_text(
        args.out_dir / "review_summary.md",
        f"# Review Summary\n\nOutcome: `{metrics['scientific_outcome']}`. Promotion gate: `{metrics['promotion_gate']['status']}`. Sandbox-only.\n",
    )
    (args.out_dir / "agent_run.yaml").write_text(
        yaml.safe_dump(agent_run, sort_keys=False), encoding="utf-8"
    )
    _write_text(args.review, report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
