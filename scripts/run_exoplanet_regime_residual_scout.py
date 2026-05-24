"""TASK-0370 exoplanet regime residual scout runner.

Bounded sandbox scout that tests interpretable residual hypotheses
around known regime boundaries on the committed PSCompPars snapshot:
the super-Earth / sub-Neptune transition (FGK-host transit slice),
the Jovian-radius plateau, and the high-irradiation / hot-Jupiter
regime. Every hypothesis is evaluated against the frozen Chen-Kipping
2017 baseline residuals together with per-class median,
shuffled-regime, and sample-size-matched controls. Minimum slice
counts are enforced before any residual statistic is interpreted.

The runner does not fetch live data, does not refit any CK17
segment, does not score any reveal, does not produce habitability /
biosignature / target-prioritization output, and does not write
canonical results, PRED entries, claims, or knowledge files.
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

AGENT_RUN_ID = "AGENT-RUN-0035"
TASK_ID = "TASK-0370"
CAMPAIGN_PROFILE_ID = "exoplanet-mass-radius"
HYPOTHESIS_PATH = (
    "hypothesis_proposals/exoplanet-mass/"
    "HYP-PROPOSAL-0050-exoplanet-regime-residual-scout.yaml"
)
EXPERIMENT_PATH = (
    "experiment_proposals/exoplanet-mass/"
    "EXP-PROPOSAL-0016-exoplanet-regime-residual-scout.yaml"
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
    REPO_ROOT / "docs" / "reviews" / "exoplanet-regime-residual-scout.md"
)

# Minimum slice counts are enforced before any residual stat is
# interpreted. A regime with fewer rows is reported but flagged
# `under_minimum_slice` and excluded from the verdict.
MIN_REGIME_ROW_COUNT: int = 30
# Survival margin: a candidate must beat its strongest control by
# at least this many log10 RMSE units to be classified as
# `survives_controls`. 0.022 ≈ a ~5% RMSE improvement.
SURVIVAL_LOG10_RMSE_MARGIN: float = 0.022
# Deterministic RNG seed for the shuffled-regime control.
SHUFFLE_SEED: int = 20260524


# ---------------------------------------------------------------------------
# Row eligibility (true-mass + transit radius, FGK host when available)
# ---------------------------------------------------------------------------


def _row_has_true_mass_and_transit_radius(entry: dict[str, Any]) -> bool:
    mass = entry.get("mass") or {}
    radius = entry.get("radius") or {}
    return (
        mass.get("mass_class") == "true_mass"
        and radius.get("radius_class") == "transit_radius"
        and isinstance(mass.get("value"), (int, float))
        and isinstance(radius.get("value"), (int, float))
        and float(mass.get("value")) > 0.0
        and float(radius.get("value")) > 0.0
    )


def _log_residual(entry: dict[str, Any]) -> float | None:
    mass = float(entry["mass"]["value"])
    radius = float(entry["radius"]["value"])
    pred = chen_kipping_predict_radius(mass)
    if not math.isfinite(pred) or pred <= 0.0:
        return None
    try:
        return math.log10(radius) - math.log10(pred)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Regime predicates (generated hypothesis families)
# ---------------------------------------------------------------------------


def _stellar_teff(entry: dict[str, Any]) -> float | None:
    host = entry.get("host_star") or {}
    value = host.get("effective_temperature_K")
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return None


def _equilibrium_temp_K(entry: dict[str, Any]) -> float | None:
    value = entry.get("equilibrium_temperature_K")
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return None


def _orbital_period_days(entry: dict[str, Any]) -> float | None:
    value = entry.get("orbital_period_days")
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return None


# Hypothesis families. Each predicate returns True if the row belongs
# to the regime. Predicates are simple, deterministic, and use only
# committed catalog fields plus the frozen baseline.
GENERATED_HYPOTHESES: list[dict[str, Any]] = [
    {
        "id": "REGIME-001",
        "label": "super_earth_to_sub_neptune_transition",
        "description": (
            "FGK-host transit slice (4000 K ≤ Teff ≤ 7200 K), planet mass "
            "1.5 ≤ M/M_earth ≤ 12. Tests CK17 residual structure across the "
            "super-Earth / sub-Neptune transition."
        ),
        "predicate": lambda e: (
            _stellar_teff(e) is not None
            and 4000.0 <= _stellar_teff(e) <= 7200.0
            and 1.5 <= float(e["mass"]["value"]) <= 12.0
        ),
        "executed": True,
    },
    {
        "id": "REGIME-002",
        "label": "jovian_radius_plateau",
        "description": (
            "Mass slice 100 ≤ M/M_earth ≤ 1000 (sub-Jovian to Jovian). Tests "
            "the CK17 jovian-segment near-flat-slope residual."
        ),
        "predicate": lambda e: 100.0 <= float(e["mass"]["value"]) <= 1000.0,
        "executed": True,
    },
    {
        "id": "REGIME-003",
        "label": "hot_jupiter_high_irradiation",
        "description": (
            "Hot Jupiter slice: M > 30 M_earth AND equilibrium temperature "
            "> 1500 K. Tests CK17 residual structure in the hot-Jupiter "
            "inflated regime."
        ),
        "predicate": lambda e: (
            float(e["mass"]["value"]) > 30.0
            and _equilibrium_temp_K(e) is not None
            and _equilibrium_temp_K(e) > 1500.0
        ),
        "executed": True,
    },
    {
        "id": "REGIME-004",
        "label": "ultra_short_period_irradiation",
        "description": (
            "Ultra-short-period slice: orbital_period_days < 1. Tests "
            "CK17 residual structure for tidally-stressed planets."
        ),
        "predicate": lambda e: (
            _orbital_period_days(e) is not None
            and _orbital_period_days(e) < 1.0
        ),
        "executed": False,
    },
    {
        "id": "REGIME-005",
        "label": "cold_host_transit_subset",
        "description": (
            "Cool-host slice: Teff < 4000 K (M dwarfs). Tests CK17 residual "
            "structure on the M-dwarf transit sub-population."
        ),
        "predicate": lambda e: (
            _stellar_teff(e) is not None and _stellar_teff(e) < 4000.0
        ),
        "executed": False,
    },
    {
        "id": "REGIME-006",
        "label": "warm_host_long_period_subset",
        "description": (
            "Long-period FGK-host slice: orbital_period_days > 100, "
            "Teff between 5000 and 6500 K. Bounded counter-regime for "
            "the hot-Jupiter slice."
        ),
        "predicate": lambda e: (
            _orbital_period_days(e) is not None
            and _orbital_period_days(e) > 100.0
            and _stellar_teff(e) is not None
            and 5000.0 <= _stellar_teff(e) <= 6500.0
        ),
        "executed": False,
    },
]


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


def _rmse(values: list[float]) -> float | None:
    if not values:
        return None
    return math.sqrt(sum(v * v for v in values) / len(values))


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    s = sorted(values)
    mid = len(s) // 2
    if len(s) % 2 == 1:
        return s[mid]
    return 0.5 * (s[mid - 1] + s[mid])


def _stats(values: list[float]) -> dict[str, Any]:
    return {
        "count": len(values),
        "log10_rmse": _rmse(values),
        "log10_mae": _mean([abs(v) for v in values]),
        "log10_bias": _mean(values),
        "log10_median": _median(values),
    }


# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------


def _per_class_median_residuals(
    entries: list[dict[str, Any]], residuals: dict[str, float]
) -> dict[str, float]:
    """Per-CK17-class median log-radius residual on the eligible set."""

    by_class: dict[str, list[float]] = {}
    for entry in entries:
        residual = residuals.get(entry["row_id"])
        if residual is None:
            continue
        mass = float(entry["mass"]["value"])
        label = planet_class_for_mass(mass)
        by_class.setdefault(label, []).append(residual)
    return {label: _median(values) for label, values in by_class.items()}


def _candidate_residual_for_regime(
    regime_entries: list[dict[str, Any]],
    residuals: dict[str, float],
) -> list[float]:
    """Candidate is identity: report the CK17 log-residuals as the
    regime-specific 'candidate' fit.

    The scout's hypothesis is structural: it asks whether the regime
    has a smaller log10 RMSE than the full eligible set (positive
    selection), not whether a per-regime correction beats CK17.
    Reporting the per-regime CK17 residual stat directly is therefore
    the correct evidence channel.
    """

    return [
        residuals[entry["row_id"]]
        for entry in regime_entries
        if residuals.get(entry["row_id"]) is not None
    ]


def _per_class_median_control_residuals(
    regime_entries: list[dict[str, Any]],
    per_class_medians: dict[str, float],
) -> list[float]:
    """Control 1 — per-CK17-class median radius prediction.

    For each regime row, the control predicts radius from the
    per-class median residual (i.e. CK17 prediction shifted by the
    median residual of its CK17 class). Residual = log10(observed)
    − [log10(CK17_pred) + class_median] = original CK17 residual −
    class_median.
    """

    out: list[float] = []
    for entry in regime_entries:
        mass = float(entry["mass"]["value"])
        radius = float(entry["radius"]["value"])
        ck_pred = chen_kipping_predict_radius(mass)
        if not math.isfinite(ck_pred) or ck_pred <= 0.0:
            continue
        label = planet_class_for_mass(mass)
        shift = per_class_medians.get(label, 0.0) or 0.0
        log_residual = math.log10(radius) - (math.log10(ck_pred) + shift)
        out.append(log_residual)
    return out


def _shuffled_regime_control_residuals(
    regime_entries: list[dict[str, Any]],
    eligible_entries: list[dict[str, Any]],
    residuals: dict[str, float],
    rng: random.Random,
) -> list[float]:
    """Control 2 — shuffled-regime: sample ``len(regime_entries)``
    rows uniformly at random from the eligible set (with replacement
    disabled when possible) and report their CK17 residuals. If the
    candidate's regime residuals are not visibly different from a
    random matched-size slice of the eligible set, the regime
    boundary does not carry information beyond sample composition.
    """

    eligible_ids = [entry["row_id"] for entry in eligible_entries]
    k = min(len(regime_entries), len(eligible_ids))
    if k <= 0:
        return []
    sampled = rng.sample(eligible_ids, k)
    return [residuals[row_id] for row_id in sampled if residuals.get(row_id) is not None]


def _matched_size_neighbor_control_residuals(
    regime_entries: list[dict[str, Any]],
    eligible_entries: list[dict[str, Any]],
    residuals: dict[str, float],
) -> list[float]:
    """Control 3 — sample-size-matched mass-neighbor control.

    Build a deterministic matched-size slice by taking each regime
    row's nearest CK17-class peer (by log10 mass, excluding the row
    itself) from the eligible set. This control isolates whether the
    regime cut adds information beyond what a same-class same-size
    nearest-mass slice already carries.
    """

    eligible_by_class: dict[str, list[tuple[float, dict[str, Any]]]] = {}
    for entry in eligible_entries:
        mass = float(entry["mass"]["value"])
        label = planet_class_for_mass(mass)
        eligible_by_class.setdefault(label, []).append((math.log10(mass), entry))
    for label in eligible_by_class:
        eligible_by_class[label].sort(key=lambda item: item[0])

    out: list[float] = []
    for row in regime_entries:
        row_mass = float(row["mass"]["value"])
        label = planet_class_for_mass(row_mass)
        log_mass = math.log10(row_mass)
        peers = eligible_by_class.get(label, [])
        best_id = None
        best_delta = float("inf")
        for peer_log_mass, peer_entry in peers:
            if peer_entry["row_id"] == row["row_id"]:
                continue
            delta = abs(peer_log_mass - log_mass)
            if delta < best_delta:
                best_delta = delta
                best_id = peer_entry["row_id"]
        if best_id is not None and residuals.get(best_id) is not None:
            out.append(residuals[best_id])
    return out


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------


def _classify_regime_outcome(
    candidate_stats: dict[str, Any],
    control_stats: dict[str, dict[str, Any]],
    eligible_stats: dict[str, Any],
    min_count: int,
    survival_margin: float,
) -> dict[str, Any]:
    candidate_rmse = candidate_stats["log10_rmse"]
    candidate_count = candidate_stats["count"]
    if candidate_count < min_count:
        return {
            "outcome": "under_minimum_slice",
            "explanation": (
                f"Slice has {candidate_count} rows (< minimum {min_count}); "
                "no residual interpretation is allowed."
            ),
            "strongest_control": None,
            "delta_log10_rmse_eligible_minus_candidate": None,
            "delta_log10_rmse_strongest_control_minus_candidate": None,
        }

    eligible_rmse = eligible_stats["log10_rmse"]
    delta_eligible = (
        None
        if (candidate_rmse is None or eligible_rmse is None)
        else float(eligible_rmse - candidate_rmse)
    )

    strongest_control = None
    best_control_rmse = None
    for name, stats in control_stats.items():
        rmse = stats.get("log10_rmse")
        if rmse is None or stats.get("count", 0) == 0:
            continue
        if best_control_rmse is None or rmse < best_control_rmse:
            best_control_rmse = rmse
            strongest_control = name
    delta_control = (
        None
        if (candidate_rmse is None or best_control_rmse is None)
        else float(best_control_rmse - candidate_rmse)
    )

    if (
        delta_eligible is not None
        and delta_eligible > survival_margin
        and delta_control is not None
        and delta_control > survival_margin
    ):
        outcome = "regime_residual_lower_than_eligible_and_controls"
    elif delta_eligible is not None and delta_eligible > survival_margin:
        outcome = "regime_residual_lower_than_eligible_only"
    elif delta_eligible is not None and delta_eligible < -survival_margin:
        outcome = "regime_residual_higher_than_eligible"
    else:
        outcome = "inconclusive"
    return {
        "outcome": outcome,
        "explanation": (
            f"candidate log10 RMSE = {candidate_rmse}; "
            f"eligible log10 RMSE = {eligible_rmse}; "
            f"strongest control = {strongest_control} "
            f"(log10 RMSE = {best_control_rmse}); "
            f"survival margin = {survival_margin}."
        ),
        "strongest_control": strongest_control,
        "delta_log10_rmse_eligible_minus_candidate": delta_eligible,
        "delta_log10_rmse_strongest_control_minus_candidate": delta_control,
    }


def _agent_verdict(
    regime_results: dict[str, dict[str, Any]]
) -> str:
    """Map regime outcomes to a sandbox-verdict enum.

    The scout itself does not promote candidates; it surfaces whether
    bounded regime hypotheses produce visible structure.
    """

    executed = {
        name: result
        for name, result in regime_results.items()
        if result.get("role") == "executed_regime"
    }
    if not executed:
        return "INCONCLUSIVE"
    outcomes = [r["classification"]["outcome"] for r in executed.values()]
    any_surviving = any(
        o == "regime_residual_lower_than_eligible_and_controls"
        for o in outcomes
    )
    any_higher = any(o == "regime_residual_higher_than_eligible" for o in outcomes)
    if any_surviving:
        return "SANDBOX_PASS"
    if all(o in {"inconclusive", "regime_residual_higher_than_eligible"} for o in outcomes):
        if any_higher:
            return "INCONCLUSIVE"
        return "INCONCLUSIVE"
    return "INCONCLUSIVE"


# ---------------------------------------------------------------------------
# Build metrics
# ---------------------------------------------------------------------------


def build_metrics(snapshot_path: Path) -> dict[str, Any]:
    payload = load_exoplanet_snapshot(snapshot_path)
    filtered = apply_inclusion_filters(payload)
    eligible = [
        entry
        for entry in filtered.included_rows
        if _row_has_true_mass_and_transit_radius(entry)
    ]
    residuals: dict[str, float] = {}
    for entry in eligible:
        value = _log_residual(entry)
        if value is None or not math.isfinite(value):
            continue
        residuals[entry["row_id"]] = value
    eligible_with_residual = [
        entry for entry in eligible if entry["row_id"] in residuals
    ]
    eligible_residuals = [residuals[row_id] for row_id in residuals]
    eligible_stats = _stats(eligible_residuals)

    per_class_medians = _per_class_median_residuals(
        eligible_with_residual, residuals
    )

    rng = random.Random(SHUFFLE_SEED)

    regime_results: dict[str, dict[str, Any]] = {}
    for hypothesis in GENERATED_HYPOTHESES:
        predicate: Callable[[dict[str, Any]], bool] = hypothesis["predicate"]
        regime_entries = [
            entry
            for entry in eligible_with_residual
            if predicate(entry)
        ]
        candidate_residuals = _candidate_residual_for_regime(
            regime_entries, residuals
        )
        candidate_stats = _stats(candidate_residuals)

        if hypothesis["executed"]:
            control_per_class = _per_class_median_control_residuals(
                regime_entries, per_class_medians
            )
            control_shuffled = _shuffled_regime_control_residuals(
                regime_entries, eligible_with_residual, residuals, rng
            )
            control_matched = _matched_size_neighbor_control_residuals(
                regime_entries, eligible_with_residual, residuals
            )
            control_stats = {
                "per_class_median": _stats(control_per_class),
                "shuffled_regime": _stats(control_shuffled),
                "matched_size_neighbor": _stats(control_matched),
            }
            classification = _classify_regime_outcome(
                candidate_stats,
                control_stats,
                eligible_stats,
                MIN_REGIME_ROW_COUNT,
                SURVIVAL_LOG10_RMSE_MARGIN,
            )
            role = "executed_regime"
        else:
            control_stats = {}
            classification = {
                "outcome": "generated_not_executed",
                "explanation": (
                    "Hypothesis generated and recorded but not executed; "
                    "kept for review as part of the bounded scout's "
                    "candidate slate."
                ),
                "strongest_control": None,
                "delta_log10_rmse_eligible_minus_candidate": None,
                "delta_log10_rmse_strongest_control_minus_candidate": None,
            }
            role = "generated_only"

        regime_results[hypothesis["id"]] = {
            "label": hypothesis["label"],
            "description": hypothesis["description"],
            "role": role,
            "candidate_stats": candidate_stats,
            "control_stats": control_stats,
            "classification": classification,
        }

    metrics: dict[str, Any] = {
        "task_id": TASK_ID,
        "agent_run_id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "snapshot_path": str(snapshot_path.relative_to(REPO_ROOT)),
        "loader_summary": {
            "total_rows": filtered.total_rows,
            "pre_filter_included_count": filtered.pre_filter_included_count,
            "post_filter_included_count": filtered.post_filter_included_count,
            "eligible_true_mass_with_transit_radius": len(eligible_with_residual),
        },
        "thresholds": {
            "min_regime_row_count": MIN_REGIME_ROW_COUNT,
            "survival_log10_rmse_margin": SURVIVAL_LOG10_RMSE_MARGIN,
            "shuffle_seed": SHUFFLE_SEED,
        },
        "eligible_stats": eligible_stats,
        "per_class_medians_log10_residual": per_class_medians,
        "generated_hypothesis_count": len(GENERATED_HYPOTHESES),
        "executed_hypothesis_count": sum(
            1 for h in GENERATED_HYPOTHESES if h["executed"]
        ),
        "regimes": regime_results,
    }
    metrics["verdict"] = _agent_verdict(regime_results)
    return metrics


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _fmt(value: float | None, places: int = 6) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{places}f}"


def _render_report(metrics: dict[str, Any]) -> str:
    loader = metrics["loader_summary"]
    elig = metrics["eligible_stats"]
    lines = [
        f"# {AGENT_RUN_ID} — Exoplanet regime residual scout",
        "",
        f"- Task: {TASK_ID}",
        f"- Campaign profile: {CAMPAIGN_PROFILE_ID}",
        f"- Snapshot: `{metrics['snapshot_path']}`",
        f"- Verdict: **{metrics['verdict']}**",
        "",
        "## Boundary",
        "",
        "Sandbox-only scout. Uses only committed snapshot rows. Does not "
        "fetch live data, does not refit CK17, does not score reveals, and "
        "does not produce habitability / biosignature / target-prioritization "
        "output.",
        "",
        "## Eligible Slice",
        "",
        f"- Total rows in snapshot: {loader['total_rows']}",
        f"- Pre-filter included: {loader['pre_filter_included_count']}",
        f"- Post-filter included: {loader['post_filter_included_count']}",
        (
            f"- Eligible (true mass + transit radius): "
            f"{loader['eligible_true_mass_with_transit_radius']}"
        ),
        (
            f"- Eligible log10 RMSE = {_fmt(elig['log10_rmse'])}, "
            f"log10 MAE = {_fmt(elig['log10_mae'])}, "
            f"log10 bias = {_fmt(elig['log10_bias'])}"
        ),
        "",
        "## Thresholds",
        "",
        (
            f"- Minimum regime row count: "
            f"{metrics['thresholds']['min_regime_row_count']}"
        ),
        (
            f"- Survival log10 RMSE margin: "
            f"{metrics['thresholds']['survival_log10_rmse_margin']}"
        ),
        f"- Shuffle seed: {metrics['thresholds']['shuffle_seed']}",
        "",
        "## Per-Class CK17 Median Log10 Residuals (eligible set)",
        "",
        "| class | median log10 residual |",
        "| --- | --- |",
    ]
    for label, value in sorted(metrics["per_class_medians_log10_residual"].items()):
        lines.append(f"| {label} | {_fmt(value)} |")
    lines.append("")
    lines.append("## Generated Hypotheses")
    lines.append("")
    lines.append(
        f"- Generated: {metrics['generated_hypothesis_count']}"
    )
    lines.append(
        f"- Executed: {metrics['executed_hypothesis_count']}"
    )
    lines.append("")
    for regime_id, regime in metrics["regimes"].items():
        lines.append(f"### {regime_id} — `{regime['label']}` ({regime['role']})")
        lines.append("")
        lines.append(regime["description"])
        lines.append("")
        cs = regime["candidate_stats"]
        lines.append(
            f"- Candidate slice: count {cs['count']}, "
            f"log10 RMSE {_fmt(cs['log10_rmse'])}, "
            f"log10 MAE {_fmt(cs['log10_mae'])}, "
            f"log10 bias {_fmt(cs['log10_bias'])}"
        )
        if regime["control_stats"]:
            lines.append("")
            lines.append("| control | count | log10 RMSE | log10 MAE | log10 bias |")
            lines.append("| --- | --- | --- | --- | --- |")
            for name, stats in regime["control_stats"].items():
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            name,
                            str(stats["count"]),
                            _fmt(stats.get("log10_rmse")),
                            _fmt(stats.get("log10_mae")),
                            _fmt(stats.get("log10_bias")),
                        ]
                    )
                    + " |"
                )
        classification = regime["classification"]
        lines.append("")
        lines.append(f"- **Outcome:** `{classification['outcome']}`")
        lines.append(f"- {classification['explanation']}")
        lines.append("")
    return "\n".join(lines)


def _render_limitations(metrics: dict[str, Any]) -> str:
    bullets = [
        "Regime predicates use only committed catalog fields and CK17; no "
        "per-regime CK17 refit is performed.",
        "Per-class median, shuffled-regime, and sample-size-matched controls "
        "share rows with the candidate where they overlap; control bias "
        "from the shared eligible set is expected and reported by-design.",
        "Minimum slice count is 30 rows; smaller regimes are flagged "
        "`under_minimum_slice` and excluded from the verdict.",
        "Shuffled-regime control is single-draw with a deterministic seed; "
        "no Monte-Carlo distribution is computed.",
        "Equilibrium temperature and orbital period are present for only a "
        "subset of rows; regimes that depend on them are smaller by "
        "construction.",
        "No habitability, biosignature, composition, target-priority, "
        "prediction registry, claim, or knowledge promotion is authorised.",
    ]
    return "# Limitations\n\n" + "\n".join(f"- {b}" for b in bullets) + "\n"


def _render_preflight(metrics: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Preflight",
            "",
            f"- Snapshot: `{metrics['snapshot_path']}`",
            (
                "- Data boundary: only committed snapshot is read; no live "
                "NASA Exoplanet Archive fetch."
            ),
            (
                "- Baseline freeze: CK17 segments unchanged; no per-regime "
                "or per-row refit."
            ),
            (
                "- Control floor: per-class median, shuffled-regime, and "
                "sample-size-matched neighbor controls evaluated on every "
                "executed regime."
            ),
            (
                "- Minimum-slice gate: regimes below the minimum row count "
                "are flagged and excluded from the verdict."
            ),
            (
                "- Promotion boundary: no canonical result, PRED, claim, "
                "knowledge, or habitability / biosignature / "
                "target-prioritization output."
            ),
            (
                "- Task scope: TASK-0370 requests bounded regime "
                "hypotheses, not reveal scoring."
            ),
            "",
            "## Checks",
            "",
            "| name | status | notes |",
            "| --- | --- | --- |",
            "| data_boundary | PASS | Only the committed snapshot is read. |",
            "| baseline_freeze | PASS | CK17 segments unchanged. |",
            "| control_floor | PASS | Three controls per executed regime. |",
            (
                "| minimum_slice_gate | PASS | Regimes < min_row_count "
                "flagged and excluded from verdict. |"
            ),
            (
                "| promotion_boundary | PASS | No PRED, RESULT, claim, "
                "knowledge, or habitability output. |"
            ),
            (
                "| task_scope | PASS | TASK-0370 requests bounded regime "
                "hypotheses, not reveal scoring. |"
            ),
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
            f"- Eligible rows (true mass + transit radius): "
            f"{metrics['loader_summary']['eligible_true_mass_with_transit_radius']}"
        ),
        (
            f"- Hypotheses generated / executed: "
            f"{metrics['generated_hypothesis_count']} / "
            f"{metrics['executed_hypothesis_count']}"
        ),
        "",
        "## Executed regime outcomes",
        "",
    ]
    for regime_id, regime in metrics["regimes"].items():
        if regime["role"] != "executed_regime":
            continue
        classification = regime["classification"]
        lines.append(
            f"- `{regime_id}` ({regime['label']}): "
            f"{classification['outcome']}; "
            f"candidate count = {regime['candidate_stats']['count']}; "
            f"delta_eligible = "
            f"{_fmt(classification['delta_log10_rmse_eligible_minus_candidate'])}; "
            f"delta_strongest_control = "
            f"{_fmt(classification['delta_log10_rmse_strongest_control_minus_candidate'])}"
        )
    lines.append("")
    lines.append(
        "The scout does not promote any candidate. The maintainer should "
        "decide whether any regime warrants a narrower follow-up under "
        "the existing exoplanet baseline protocol."
    )
    lines.append("")
    return "\n".join(lines)


def _render_review_note(metrics: dict[str, Any]) -> str:
    lines = [
        "# Exoplanet regime residual scout",
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
            "Bounded sandbox scout that tests interpretable residual "
            "hypotheses around three known regime boundaries on the "
            "committed PSCompPars snapshot: the super-Earth / sub-Neptune "
            "transition, the Jovian-radius plateau, and the high-"
            "irradiation / hot-Jupiter regime. Every hypothesis is "
            "evaluated against the frozen CK17 baseline plus per-class "
            "median, shuffled-regime, and sample-size-matched controls."
        ),
        "",
        "## Bounds",
        "",
        (
            f"- Minimum regime row count: "
            f"{metrics['thresholds']['min_regime_row_count']} (smaller slices "
            "flagged and excluded from the verdict)."
        ),
        (
            f"- Survival margin: "
            f"{metrics['thresholds']['survival_log10_rmse_margin']} log10 RMSE "
            "(≈ 5% RMSE improvement)."
        ),
        (
            f"- Shuffle seed: {metrics['thresholds']['shuffle_seed']} "
            "(deterministic)."
        ),
        "",
        "## Executed regime outcomes",
        "",
        "| regime | label | count | log10 RMSE | strongest control | delta vs control |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for regime_id, regime in metrics["regimes"].items():
        if regime["role"] != "executed_regime":
            continue
        cs = regime["candidate_stats"]
        cls = regime["classification"]
        lines.append(
            "| "
            + " | ".join(
                [
                    regime_id,
                    regime["label"],
                    str(cs["count"]),
                    _fmt(cs["log10_rmse"]),
                    str(cls["strongest_control"]) if cls["strongest_control"] else "n/a",
                    _fmt(cls["delta_log10_rmse_strongest_control_minus_candidate"]),
                ]
            )
            + " |"
        )
    lines.append("")
    lines.append("## Generated-but-not-executed hypotheses (review surface)")
    lines.append("")
    for regime_id, regime in metrics["regimes"].items():
        if regime["role"] == "executed_regime":
            continue
        cs = regime["candidate_stats"]
        lines.append(
            f"- `{regime_id}` ({regime['label']}): generated only; "
            f"slice size = {cs['count']}."
        )
    lines.append("")
    lines.append("## Follow-up boundary")
    lines.append("")
    lines.append(
        "Maintainer review only. No PRED entry, no RESULT-*, no claim, no "
        "knowledge edit, no habitability / biosignature / "
        "target-prioritization output authorised by this run. A future "
        "task may scope a narrower per-regime correction; this scout does "
        "not author that task."
    )
    lines.append("")
    return "\n".join(lines)


def _build_agent_run_payload(metrics: dict[str, Any]) -> dict[str, Any]:
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
                {"name": "data_boundary", "status": "PASS",
                 "notes": "Only the committed snapshot is read; no live fetch."},
                {"name": "baseline_freeze", "status": "PASS",
                 "notes": "CK17 segments unchanged; no per-regime refit."},
                {"name": "control_floor", "status": "PASS",
                 "notes": "Three controls per executed regime (per-class median, shuffled-regime, sample-size-matched neighbor)."},
                {"name": "minimum_slice_gate", "status": "PASS",
                 "notes": f"Regimes with fewer than {MIN_REGIME_ROW_COUNT} rows are flagged and excluded from the verdict."},
                {"name": "promotion_boundary", "status": "PASS",
                 "notes": "No PRED, RESULT, claim, knowledge, or habitability / biosignature / target-prioritization output."},
                {"name": "task_scope", "status": "PASS",
                 "notes": "TASK-0370 requests bounded regime hypotheses, not reveal scoring."},
            ],
        },
        "limitations": [
            "Regime predicates use only committed catalog fields and CK17; no per-regime CK17 refit is performed.",
            "Per-class median, shuffled-regime, and sample-size-matched controls share rows with the candidate where they overlap.",
            f"Minimum slice count is {MIN_REGIME_ROW_COUNT}; smaller regimes are flagged and excluded from the verdict.",
            "Shuffled-regime control is single-draw with a deterministic seed; no Monte-Carlo distribution is computed.",
            "Equilibrium temperature and orbital period are present for only a subset of rows; regimes that depend on them are smaller by construction.",
            "No habitability, biosignature, composition, target-priority, prediction registry, claim, or knowledge promotion is authorised.",
        ],
        "verdict": metrics["verdict"],
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review before any per-regime correction "
                "follow-up, canonical result, prediction registry entry, "
                "claim update, knowledge file edit, or habitability / "
                "biosignature / target-prioritization promotion."
            ),
        },
    }


# ---------------------------------------------------------------------------
# CLI
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
    for path in (out, report, agent_run, limitations, preflight, review_summary, review):
        path.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2, sort_keys=True)
        fh.write("\n")
    report.write_text(_render_report(metrics), encoding="utf-8")
    limitations.write_text(_render_limitations(metrics), encoding="utf-8")
    preflight.write_text(_render_preflight(metrics), encoding="utf-8")
    review_summary.write_text(_render_review_summary(metrics), encoding="utf-8")
    review.write_text(_render_review_note(metrics), encoding="utf-8")
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
        out=args.out, report=args.report, agent_run=args.agent_run,
        limitations=args.limitations, preflight=args.preflight,
        review_summary=args.review_summary, review=args.review,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
