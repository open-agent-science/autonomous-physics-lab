"""TASK-0361 exoplanet mass-radius frozen-baseline benchmark runner.

Runs the first executed residual surface for the Exoplanet Mass-Radius
campaign on the committed PSCompPars snapshot. Compares a frozen
Chen-Kipping 2017 piecewise median baseline against a per-class median
null baseline on both eligible residual axes. Writes deterministic
``agent_runs/AGENT-RUN-0032/`` artifacts plus a docs/reviews note.

The runner does not fetch live data, does not refit any CK17 segment on
the snapshot, does not produce habitability / biosignature /
target-prioritization output, does not register prediction-registry
entries, and does not write canonical results or claim updates.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.datasets.exoplanets import (  # noqa: E402
    DEFAULT_MASS_SIGMA_THRESHOLD,
    DEFAULT_RADIUS_SIGMA_THRESHOLD,
    apply_inclusion_filters,
    load_exoplanet_snapshot,
    summarize,
)
from physics_lab.engines.exoplanet_mass_radius import (  # noqa: E402
    benchmark_result_to_dict,
    chen_kipping_baseline_metadata,
    planet_class_distribution,
    run_benchmark,
)

AGENT_RUN_ID = "AGENT-RUN-0032"
TASK_ID = "TASK-0361"
CAMPAIGN_PROFILE_ID = "exoplanet-mass-radius"
HYPOTHESIS_PATH = (
    "hypothesis_proposals/exoplanet-mass/"
    "HYP-PROPOSAL-0049-frozen-baseline-benchmark.yaml"
)
EXPERIMENT_PATH = (
    "experiment_proposals/exoplanet-mass/"
    "EXP-PROPOSAL-0015-frozen-baseline-benchmark.yaml"
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
    / "exoplanet-mass-radius-baseline-benchmark.md"
)


# ---------------------------------------------------------------------------
# Metric assembly
# ---------------------------------------------------------------------------


def build_metrics(snapshot_path: Path) -> dict[str, Any]:
    """Build the deterministic benchmark metrics payload."""

    payload = load_exoplanet_snapshot(snapshot_path)
    filtered = apply_inclusion_filters(payload)
    benchmark = run_benchmark(filtered.included_rows)

    metrics: dict[str, Any] = {
        "task_id": TASK_ID,
        "agent_run_id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "snapshot_path": str(snapshot_path.relative_to(REPO_ROOT)),
        "loader_summary": summarize(filtered),
        "baseline": chen_kipping_baseline_metadata(),
        "null_baseline": {
            "name": "per-CK17-class median log10(radius) null baseline",
            "trained_on": "post-filter included rows for the given axis",
        },
        "axes": {
            name: benchmark_result_to_dict(result)
            for name, result in benchmark.items()
        },
        "planet_class_distribution": {
            name: planet_class_distribution(result.rows)
            for name, result in benchmark.items()
        },
        "verdict_inputs": _build_verdict_inputs(benchmark),
    }
    metrics["verdict"] = _decide_verdict(metrics["verdict_inputs"])
    return metrics


def _build_verdict_inputs(benchmark: dict[str, Any]) -> dict[str, Any]:
    inputs: dict[str, Any] = {}
    for axis_name, result in benchmark.items():
        ck_rmse = result.overall_chen_kipping.log10_rmse
        null_rmse = result.overall_null.log10_rmse
        delta = (
            None
            if (ck_rmse is None or null_rmse is None)
            else float(null_rmse - ck_rmse)
        )
        inputs[axis_name] = {
            "chen_kipping_log10_rmse": ck_rmse,
            "null_baseline_log10_rmse": null_rmse,
            "log10_rmse_delta_null_minus_ck": delta,
            "ck_beats_null": (
                None if delta is None else bool(delta > 0.0)
            ),
            "row_count_chen_kipping": result.overall_chen_kipping.count,
            "row_count_null": result.overall_null.count,
        }
    return inputs


def _decide_verdict(verdict_inputs: dict[str, Any]) -> str:
    """Map benchmark outcome to a sandbox verdict.

    The benchmark is the first executed residual surface for the
    campaign. We classify the outcome on whether the frozen CK17
    baseline beats the per-class median null on overall log10 RMSE for
    both eligible axes, both, or neither.
    """

    flags = [
        bool(entry.get("ck_beats_null"))
        for entry in verdict_inputs.values()
        if entry.get("ck_beats_null") is not None
    ]
    if not flags:
        return "INCONCLUSIVE"
    if all(flags):
        return "SANDBOX_PASS"
    if not any(flags):
        return "FALSIFIED"
    return "INCONCLUSIVE"


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


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
    out.parent.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    agent_run.parent.mkdir(parents=True, exist_ok=True)
    review.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2, sort_keys=True)
        fh.write("\n")

    report.write_text(_render_report(metrics), encoding="utf-8")
    limitations.write_text(_render_limitations(metrics), encoding="utf-8")
    preflight.write_text(_render_preflight(metrics), encoding="utf-8")
    review_summary.write_text(
        _render_review_summary(metrics), encoding="utf-8"
    )
    review.write_text(_render_review_note(metrics), encoding="utf-8")

    with agent_run.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(_build_agent_run_payload(metrics), fh, sort_keys=False)


def _fmt(value: float | None, places: int = 6) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{places}f}"


def _render_axis_block(axis_name: str, axis: dict[str, Any]) -> list[str]:
    ck = axis["overall_chen_kipping"]
    null = axis["overall_null"]
    lines = [
        f"### Axis: `{axis_name}`",
        "",
        f"- Eligible row count: {axis['eligible_row_count']}",
        "",
        "| metric | Chen-Kipping (frozen) | Per-class median null |",
        "| --- | --- | --- |",
        f"| count | {ck['count']} | {null['count']} |",
        f"| log10 MAE | {_fmt(ck['log10_mae'])} | {_fmt(null['log10_mae'])} |",
        f"| log10 RMSE | {_fmt(ck['log10_rmse'])} | {_fmt(null['log10_rmse'])} |",
        f"| log10 bias | {_fmt(ck['log10_bias'])} | {_fmt(null['log10_bias'])} |",
        f"| median log10 residual | {_fmt(ck['median_log10_residual'])} | {_fmt(null['median_log10_residual'])} |",
        f"| within factor 1.5 | {_fmt(ck['interval_68_coverage'])} | {_fmt(null['interval_68_coverage'])} |",
        f"| within factor 2 | {_fmt(ck['fraction_within_factor_2'])} | {_fmt(null['fraction_within_factor_2'])} |",
        "",
    ]
    per_class_ck = axis["per_class_chen_kipping"]
    per_class_null = axis["per_class_null"]
    class_labels = sorted(set(per_class_ck) | set(per_class_null))
    if class_labels:
        lines.append("#### Per-class log10 RMSE")
        lines.append("")
        lines.append("| class | CK count | CK log10 RMSE | null count | null log10 RMSE |")
        lines.append("| --- | --- | --- | --- | --- |")
        for label in class_labels:
            ck_entry = per_class_ck.get(label, {})
            null_entry = per_class_null.get(label, {})
            lines.append(
                "| "
                + " | ".join(
                    [
                        label,
                        str(ck_entry.get("count", 0)),
                        _fmt(ck_entry.get("log10_rmse")),
                        str(null_entry.get("count", 0)),
                        _fmt(null_entry.get("log10_rmse")),
                    ]
                )
                + " |"
            )
        lines.append("")
    per_method = axis["per_detection_method_chen_kipping"]
    if per_method:
        lines.append("#### Per-detection-method log10 RMSE (Chen-Kipping)")
        lines.append("")
        lines.append("| detection method | count | log10 RMSE | log10 bias |")
        lines.append("| --- | --- | --- | --- |")
        for label in sorted(per_method):
            entry = per_method[label]
            lines.append(
                "| "
                + " | ".join(
                    [
                        label,
                        str(entry["count"]),
                        _fmt(entry["log10_rmse"]),
                        _fmt(entry["log10_bias"]),
                    ]
                )
                + " |"
            )
        lines.append("")
    return lines


def _render_report(metrics: dict[str, Any]) -> str:
    loader = metrics["loader_summary"]
    lines = [
        f"# {AGENT_RUN_ID} — Exoplanet mass-radius frozen-baseline benchmark",
        "",
        f"- Task: {TASK_ID}",
        f"- Campaign profile: {CAMPAIGN_PROFILE_ID}",
        f"- Snapshot: `{metrics['snapshot_path']}`",
        f"- Snapshot retrieval (UTC): {loader.get('retrieval_date_utc')}",
        f"- Verdict: **{metrics['verdict']}**",
        "",
        "## Loader summary",
        "",
        f"- Total rows in snapshot: {loader['total_rows']}",
        f"- Pre-filter included: {loader['pre_filter_included_count']}",
        f"- Post-filter included: {loader['post_filter_included_count']}",
        (
            f"- Quality thresholds: sigma_M/M <= "
            f"{loader['thresholds']['mass_sigma_threshold']}, "
            f"sigma_R/R <= {loader['thresholds']['radius_sigma_threshold']}"
        ),
        "",
        "### Exclusion reasons",
        "",
        "| reason | count |",
        "| --- | --- |",
    ]
    for reason, count in sorted(loader["exclusion_reason_counts"].items()):
        lines.append(f"| {reason} | {count} |")
    lines.append("")
    lines.append("## Frozen baseline metadata")
    lines.append("")
    baseline = metrics["baseline"]
    lines.append(f"- Reference: {baseline['reference']}")
    lines.append(f"- No new parameters fit on the snapshot: {baseline['no_new_parameters_fit']}")
    lines.append("")
    lines.append("| segment | mass lower (M_earth) | mass upper (M_earth) | slope | prefactor |")
    lines.append("| --- | --- | --- | --- | --- |")
    for segment in baseline["segments"]:
        upper = segment["mass_upper_mearth"]
        upper_label = "infinity" if upper is None else _fmt(float(upper), 3)
        lines.append(
            "| "
            + " | ".join(
                [
                    segment["name"],
                    _fmt(float(segment["mass_lower_mearth"]), 3),
                    upper_label,
                    _fmt(float(segment["slope_log_r_per_log_m"]), 3),
                    _fmt(
                        float(segment["prefactor_r_earth_per_mass_unit_pow_slope"]),
                        6,
                    ),
                ]
            )
            + " |"
        )
    lines.append("")
    lines.append("## Benchmark axes")
    lines.append("")
    for axis_name, axis in metrics["axes"].items():
        lines.extend(_render_axis_block(axis_name, axis))
    lines.append("## Verdict inputs")
    lines.append("")
    lines.append("| axis | CK log10 RMSE | null log10 RMSE | delta (null - CK) | CK beats null |")
    lines.append("| --- | --- | --- | --- | --- |")
    for axis_name, entry in metrics["verdict_inputs"].items():
        lines.append(
            "| "
            + " | ".join(
                [
                    axis_name,
                    _fmt(entry["chen_kipping_log10_rmse"]),
                    _fmt(entry["null_baseline_log10_rmse"]),
                    _fmt(entry["log10_rmse_delta_null_minus_ck"]),
                    "n/a" if entry["ck_beats_null"] is None else str(entry["ck_beats_null"]),
                ]
            )
            + " |"
        )
    lines.append("")
    lines.append(
        "Negative outcomes — null beating CK on either axis — are preserved as "
        "valid review evidence and not retried with a tuned baseline."
    )
    lines.append("")
    return "\n".join(lines)


def _render_limitations(metrics: dict[str, Any]) -> str:
    bullets = [
        "Chen-Kipping segment slopes, changepoints, and prefactors are frozen; "
        "the snapshot is not used to refit any segment.",
        "The minimum-mass axis treats M sin i as a lower bound on true mass and "
        "therefore biases residuals on RV-only systems.",
        "Quality filters use only reported sigma_M and sigma_R; covariance with "
        "host-star parameters is not modelled.",
        "The per-class median null baseline shares training rows with its scoring "
        "rows; this is intentional as a non-trivial floor, not predictive evidence.",
        "Per-detection-method splits are computed on the post-filter included set "
        "and are sensitive to sample composition.",
        "No habitability, biosignature, target-priority, prediction registry, "
        "claim, or knowledge promotion is authorised.",
    ]
    return "# Limitations\n\n" + "\n".join(f"- {line}" for line in bullets) + "\n"


def _render_preflight(metrics: dict[str, Any]) -> str:
    lines = [
        "# Preflight",
        "",
        f"- Snapshot: `{metrics['snapshot_path']}`",
        (
            "- Loader policy: committed loader and quality-filter chain applied; "
            "no live NASA Exoplanet Archive fetch performed."
        ),
        (
            "- Baseline policy: frozen Chen-Kipping 2017 piecewise relation; "
            "no segment was refit on the snapshot."
        ),
        "- Null baseline: per-CK17-class median log10(radius) on the same eligible rows.",
        (
            "- Promotion boundary: no canonical result, prediction registry entry, "
            "claim update, knowledge file edit, or habitability/biosignature/"
            "target-prioritization output is produced."
        ),
        "",
        "## Checks",
        "",
        "| name | status | notes |",
        "| --- | --- | --- |",
        "| data_boundary | PASS | Only the committed snapshot is read; no live fetch. |",
        "| baseline_freeze | PASS | CK17 segments are frozen from the published reference. |",
        "| null_floor | PASS | Per-class median null baseline is computed and reported on both axes. |",
        "| promotion_boundary | PASS | No canonical result, PRED, claim, knowledge, or habitability output is written. |",
        "| task_scope | PASS | TASK-0361 requests a benchmark on the pinned snapshot, not reveal scoring. |",
        "",
    ]
    return "\n".join(lines)


def _render_review_summary(metrics: dict[str, Any]) -> str:
    inputs = metrics["verdict_inputs"]
    lines = [
        "# Review summary",
        "",
        f"- Verdict: **{metrics['verdict']}**",
        f"- Snapshot: `{metrics['snapshot_path']}`",
        "",
        "## Axis outcomes",
        "",
    ]
    for axis_name, entry in inputs.items():
        delta = entry["log10_rmse_delta_null_minus_ck"]
        verdict_line = (
            "no comparison available"
            if entry["ck_beats_null"] is None
            else ("CK beats null" if entry["ck_beats_null"] else "null beats or ties CK")
        )
        lines.append(
            f"- `{axis_name}`: CK log10 RMSE = {_fmt(entry['chen_kipping_log10_rmse'])}, "
            f"null log10 RMSE = {_fmt(entry['null_baseline_log10_rmse'])}, "
            f"delta (null - CK) = {_fmt(delta)} -> {verdict_line}"
        )
    lines.append("")
    lines.append(
        "The benchmark is the first executed residual surface for the exoplanet "
        "campaign. The maintainer should decide whether the outcome warrants a "
        "narrower follow-up lane (for example, a hot-Jupiter inflation subset) or "
        "whether the surface stays as a frozen comparison baseline for future agent "
        "candidates."
    )
    lines.append("")
    return "\n".join(lines)


def _render_review_note(metrics: dict[str, Any]) -> str:
    loader = metrics["loader_summary"]
    inputs = metrics["verdict_inputs"]
    lines = [
        "# Exoplanet mass-radius frozen-baseline benchmark",
        "",
        f"- Agent run: {AGENT_RUN_ID}",
        f"- Task: {TASK_ID}",
        f"- Campaign profile: {CAMPAIGN_PROFILE_ID}",
        f"- Snapshot: `{metrics['snapshot_path']}`",
        f"- Verdict: **{metrics['verdict']}**",
        "",
        "## Purpose",
        "",
        (
            "This note records the first executed residual surface for the "
            "Exoplanet Mass-Radius campaign. It compares a frozen Chen-Kipping "
            "2017 piecewise median baseline against a per-class median null "
            "baseline on the committed PSCompPars snapshot. No segment of the "
            "CK17 relation is refit on the snapshot, and no habitability, "
            "biosignature, target-priority, prediction registry, or canonical "
            "result artifact is produced."
        ),
        "",
        "## Data scope",
        "",
        f"- Total rows: {loader['total_rows']}",
        f"- Pre-filter included: {loader['pre_filter_included_count']}",
        f"- Post-filter included: {loader['post_filter_included_count']}",
        (
            f"- Quality thresholds: sigma_M/M <= "
            f"{loader['thresholds']['mass_sigma_threshold']}, "
            f"sigma_R/R <= {loader['thresholds']['radius_sigma_threshold']}"
        ),
        "",
        "## Axis outcomes",
        "",
        "| axis | CK log10 RMSE | null log10 RMSE | delta (null - CK) | CK beats null |",
        "| --- | --- | --- | --- | --- |",
    ]
    for axis_name, entry in inputs.items():
        ck_beats = entry["ck_beats_null"]
        lines.append(
            "| "
            + " | ".join(
                [
                    axis_name,
                    _fmt(entry["chen_kipping_log10_rmse"]),
                    _fmt(entry["null_baseline_log10_rmse"]),
                    _fmt(entry["log10_rmse_delta_null_minus_ck"]),
                    "n/a" if ck_beats is None else str(ck_beats),
                ]
            )
            + " |"
        )
    lines.append("")
    lines.append("## Reading the verdict")
    lines.append("")
    lines.append(
        "- SANDBOX_PASS: CK17 beats the per-class median null on log10 RMSE on "
        "every eligible axis. The frozen baseline survives this floor."
    )
    lines.append(
        "- INCONCLUSIVE: CK17 beats the null on at least one axis but not all. "
        "The result is preserved and not retried with a tuned baseline."
    )
    lines.append(
        "- FALSIFIED: CK17 does not beat the per-class median on any axis. "
        "The negative outcome is preserved as a first-class result."
    )
    lines.append("")
    lines.append("## Follow-up boundary")
    lines.append("")
    lines.append(
        "The maintainer is asked to decide whether to preserve this benchmark "
        "as the campaign's first frozen comparison baseline or to scope a "
        "narrower follow-up (for example a hot-Jupiter inflation subset, a "
        "sub-Neptune transition subset, or a high-uncertainty hold-back set). "
        "No prediction registry, claim, knowledge, RESULT-*, or "
        "habitability/target-prioritization output is authorised by this run."
    )
    lines.append("")
    return "\n".join(lines)


def _build_agent_run_payload(metrics: dict[str, Any]) -> dict[str, Any]:
    verdict = metrics["verdict"]
    return {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "task_id": TASK_ID,
        "status": "SANDBOX_COMPLETE",
        "sandbox_only": True,
        "created_by": {
            "contributor_id": "roman",
            "agent_id": "claude",
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
                    "notes": (
                        "Only the committed exo-0001-pscomppars-snapshot.yaml "
                        "is read; no live NASA Exoplanet Archive fetch is "
                        "performed."
                    ),
                },
                {
                    "name": "baseline_freeze",
                    "status": "PASS",
                    "notes": (
                        "Chen-Kipping 2017 segments, slopes, and changepoints "
                        "are frozen from the published reference; no segment "
                        "is refit on the snapshot."
                    ),
                },
                {
                    "name": "null_floor",
                    "status": "PASS",
                    "notes": (
                        "Per-CK17-class median log10(radius) null baseline is "
                        "computed and reported on every eligible axis."
                    ),
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": (
                        "No canonical result, prediction registry entry, "
                        "claim update, knowledge file edit, or "
                        "habitability/biosignature/target-prioritization "
                        "output is written."
                    ),
                },
                {
                    "name": "task_scope",
                    "status": "PASS",
                    "notes": (
                        "TASK-0361 requests a benchmark on the pinned "
                        "snapshot, not reveal scoring or claim promotion."
                    ),
                },
            ],
        },
        "limitations": [
            (
                "Chen-Kipping segment slopes, changepoints, and prefactors are "
                "frozen; the snapshot is not used to refit any segment."
            ),
            (
                "The minimum-mass axis treats M sin i as a lower bound on true "
                "mass and therefore biases residuals on RV-only systems."
            ),
            (
                "Quality filters use only reported sigma_M and sigma_R; "
                "covariance with host-star parameters is not modelled."
            ),
            (
                "The per-class median null baseline shares training rows with "
                "its scoring rows; this is intentional as a non-trivial "
                "floor, not predictive evidence."
            ),
            (
                "Per-detection-method splits are computed on the post-filter "
                "included set and are sensitive to sample composition."
            ),
            (
                "No habitability, biosignature, target-priority, prediction "
                "registry, claim, or knowledge promotion is authorised."
            ),
        ],
        "verdict": verdict,
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review before any canonical result, prediction "
                "registry entry, claim update, knowledge file edit, or "
                "habitability/biosignature/target-prioritization follow-up."
            ),
        },
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT_PATH)
    parser.add_argument("--out", type=Path, default=DEFAULT_METRICS_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument(
        "--agent-run", type=Path, default=DEFAULT_AGENT_RUN_PATH
    )
    parser.add_argument(
        "--limitations", type=Path, default=DEFAULT_LIMITATIONS_PATH
    )
    parser.add_argument(
        "--preflight", type=Path, default=DEFAULT_PREFLIGHT_PATH
    )
    parser.add_argument(
        "--review-summary", type=Path, default=DEFAULT_REVIEW_SUMMARY_PATH
    )
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW_PATH)
    parser.add_argument(
        "--mass-sigma-threshold",
        type=float,
        default=DEFAULT_MASS_SIGMA_THRESHOLD,
    )
    parser.add_argument(
        "--radius-sigma-threshold",
        type=float,
        default=DEFAULT_RADIUS_SIGMA_THRESHOLD,
    )
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
