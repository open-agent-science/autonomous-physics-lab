#!/usr/bin/env python3
"""TASK-0837 Stellar M-L high-mass transfer benchmark.

This runner freezes the RESULT-0022 best relation and transfers it onto the
disjoint high-mass DEBCat Route 2 regime (admitted rows with mass_solar > 2.0).
It reads only committed rows, performs no live fetch, does not refit or rescue
the frozen relation, and writes sandbox AGENT-RUN artifacts plus a review note.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
ROWS_REL = "data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml"
RESULT_0022_REL = "results/EXP-0015/RUN-0001/result.yaml"
SCOUT_REL = "docs/reviews/stellar-ml-independent-transfer-dataset-scout.md"
GATE_B_REL = "docs/reviews/stellar-ml-result0022-gate-b-replay.md"
SCRIPT_REL = "scripts/run_stellar_ml_high_mass_transfer.py"

AGENT_RUN_ID = "AGENT-RUN-0085"
TASK_ID = "TASK-0837"
BENCHMARK_ID = "stellar-ml-high-mass-debcat-transfer"
ENGINE_VERSION = "0.1.0"
FROZEN_MODEL_ID = "model_train_fitted_alpha"
EXPECTED_FROZEN_ALPHA = 4.526004
TRANSFER_MASS_MIN_EXCLUSIVE = 2.0
SURVIVAL_MARGIN_THRESHOLD_DEX = 0.02
SHUFFLE_SEEDS = (11, 23, 37, 53, 71)

Row = dict[str, Any]
Predictor = Callable[[Row], float]


def _load_yaml(rel: str) -> dict[str, Any]:
    payload = yaml.safe_load((REPO_ROOT / rel).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML mapping at {rel}")
    return payload


def _sha256_file(rel: str) -> str:
    return hashlib.sha256((REPO_ROOT / rel).read_bytes()).hexdigest()


def _git_commit() -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
            capture_output=True,
            check=True,
            text=True,
        )
        return proc.stdout.strip()
    except Exception:  # pragma: no cover - git may be unavailable in packaged use
        return "UNKNOWN"


def _round(value: float | None, ndigits: int = 6) -> float | None:
    if value is None or math.isnan(value):
        return None
    return round(float(value), ndigits)


def _load_frozen_alpha() -> float:
    result = _load_yaml(RESULT_0022_REL)
    if result.get("best_model_id") != FROZEN_MODEL_ID:
        raise ValueError(
            f"RESULT-0022 best_model_id changed: expected {FROZEN_MODEL_ID}, "
            f"observed {result.get('best_model_id')}"
        )
    scores = result.get("scores", [])
    for score in scores:
        if score.get("model_id") == FROZEN_MODEL_ID:
            alpha = float(score["coefficients"]["fitted_alpha"])
            if round(alpha, 6) != EXPECTED_FROZEN_ALPHA:
                raise ValueError(
                    f"Unexpected frozen alpha: expected {EXPECTED_FROZEN_ALPHA}, "
                    f"observed {alpha}"
                )
            return alpha
    raise ValueError(f"Could not find {FROZEN_MODEL_ID} coefficients in RESULT-0022")


def _admitted_rows() -> list[Row]:
    rows_doc = _load_yaml(ROWS_REL)
    return [r for r in rows_doc["rows"] if r.get("admissibility") == "admitted"]


def _high_mass_rows(rows: list[Row]) -> list[Row]:
    return [r for r in rows if float(r["mass_solar"]) > TRANSFER_MASS_MIN_EXCLUSIVE]


def _mae(rows: list[Row], predictor: Predictor) -> float | None:
    if not rows:
        return None
    return statistics.fmean(
        abs(float(row["log_luminosity_solar"]) - predictor(row)) for row in rows
    )


def _rmse(rows: list[Row], predictor: Predictor) -> float | None:
    if not rows:
        return None
    return math.sqrt(
        statistics.fmean(
            (float(row["log_luminosity_solar"]) - predictor(row)) ** 2 for row in rows
        )
    )


def _summary(rows: list[Row], predictor: Predictor) -> dict[str, Any]:
    residuals = [float(row["log_luminosity_solar"]) - predictor(row) for row in rows]
    abs_residuals = [abs(value) for value in residuals]
    return {
        "count": len(rows),
        "system_count": len({row["system_id"] for row in rows}),
        "mae_dex": _round(_mae(rows, predictor)),
        "rmse_dex": _round(_rmse(rows, predictor)),
        "median_residual_dex": _round(statistics.median(residuals) if residuals else None),
        "median_abs_residual_dex": _round(
            statistics.median(abs_residuals) if abs_residuals else None
        ),
        "max_abs_residual_dex": _round(max(abs_residuals) if abs_residuals else None),
    }


def _count_by(rows: list[Row], key: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row.get(key, "unknown")) for row in rows).items()))


def _summarize_by(rows: list[Row], key: str, predictor: Predictor) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[Row]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(key, "unknown"))].append(row)
    return {name: _summary(group, predictor) for name, group in sorted(grouped.items())}


def _massband_median_predictor(train_rows: list[Row]) -> Predictor:
    by_band: dict[str, list[float]] = defaultdict(list)
    for row in train_rows:
        by_band[str(row["mass_band"])].append(float(row["log_luminosity_solar"]))
    median_by_band = {band: statistics.median(values) for band, values in by_band.items()}
    global_median = statistics.median(
        [float(row["log_luminosity_solar"]) for row in train_rows]
    )
    return lambda row: median_by_band.get(str(row.get("mass_band", "unknown")), global_median)


def _nearest_mass_predictor(train_rows: list[Row]) -> Predictor:
    if not train_rows:
        raise ValueError("nearest-mass control requires train rows")

    def predict(row: Row) -> float:
        target_log_mass = float(row["log_mass_solar"])
        nearest = min(
            train_rows,
            key=lambda candidate: abs(float(candidate["log_mass_solar"]) - target_log_mass),
        )
        return float(nearest["log_luminosity_solar"])

    return predict


def _shuffle_control_maes(rows: list[Row], predictor: Predictor) -> dict[str, Any]:
    predictions = [predictor(row) for row in rows]
    per_seed: list[float] = []
    for seed in SHUFFLE_SEEDS:
        shuffled = list(predictions)
        random.Random(seed).shuffle(shuffled)
        mae = statistics.fmean(
            abs(float(row["log_luminosity_solar"]) - pred)
            for row, pred in zip(rows, shuffled)
        )
        per_seed.append(round(mae, 6))
    return {
        "definition": (
            "Frozen RESULT-0022 high-mass holdout predictions shuffled across "
            "holdout rows; preserves prediction distribution but breaks row pairing."
        ),
        "seeds": list(SHUFFLE_SEEDS),
        "mae_dex_per_seed": per_seed,
        "best_mae_dex": round(min(per_seed), 6),
        "mean_mae_dex": round(statistics.fmean(per_seed), 6),
    }


def _control_payload(
    *,
    high_mass_train: list[Row],
    high_mass_holdout: list[Row],
    frozen_predictor: Predictor,
) -> dict[str, dict[str, Any]]:
    null_pred = _massband_median_predictor(high_mass_train)
    mass_match_pred = _nearest_mass_predictor(high_mass_train)
    shuffled = _shuffle_control_maes(high_mass_holdout, frozen_predictor)
    return {
        "null_high_mass_train_massband_median": {
            "definition": (
                "Per-mass-band median log_luminosity_solar from high-mass train "
                "lane, with a global train-median fallback."
            ),
            "mae_dex": _round(_mae(high_mass_holdout, null_pred)),
        },
        "shuffled_relation_predictions": shuffled,
        "mass_matched_high_mass_train_nearest": {
            "definition": (
                "Nearest high-mass train-lane row by log_mass_solar; predicts that "
                "row's observed log_luminosity_solar. This is a local mass control, "
                "not a refit of RESULT-0022."
            ),
            "mae_dex": _round(_mae(high_mass_holdout, mass_match_pred)),
        },
    }


def _best_control(controls: dict[str, dict[str, Any]]) -> tuple[str, float]:
    candidates = {
        control_id: payload.get("mae_dex", payload.get("best_mae_dex"))
        for control_id, payload in controls.items()
    }
    numeric = {key: float(value) for key, value in candidates.items() if value is not None}
    if not numeric:
        raise ValueError("No numeric controls were produced")
    best_id = min(numeric, key=numeric.__getitem__)
    return best_id, numeric[best_id]


def build_metrics() -> dict[str, Any]:
    frozen_alpha = _load_frozen_alpha()
    rows = _admitted_rows()
    high_mass = _high_mass_rows(rows)
    high_mass_train = [row for row in high_mass if row["lane"] == "train"]
    high_mass_validation = [row for row in high_mass if row["lane"] == "validation"]
    high_mass_holdout = [row for row in high_mass if row["lane"] == "holdout"]

    def frozen_predictor(row: Row) -> float:
        return frozen_alpha * float(row["log_mass_solar"])

    relation_holdout_mae = _mae(high_mass_holdout, frozen_predictor)
    controls = _control_payload(
        high_mass_train=high_mass_train,
        high_mass_holdout=high_mass_holdout,
        frozen_predictor=frozen_predictor,
    )
    best_control_id, best_control_mae = _best_control(controls)
    survival_margin = (
        best_control_mae - relation_holdout_mae if relation_holdout_mae is not None else None
    )

    if survival_margin is None:
        verdict = "TRANSFER_INCONCLUSIVE"
        rationale = "No high-mass holdout MAE could be computed."
    elif survival_margin >= SURVIVAL_MARGIN_THRESHOLD_DEX:
        verdict = "TRANSFER_SUPPORTED_IN_SCOPE"
        rationale = (
            "Frozen RESULT-0022 relation clears the predeclared survival margin "
            "over the best control."
        )
    elif survival_margin < 0:
        verdict = "TRANSFER_NOT_SUPPORTED_BEST_CONTROL"
        rationale = (
            "Frozen RESULT-0022 relation does not transfer under controls: the "
            "best mass-matched control has lower MAE on the high-mass holdout."
        )
    else:
        verdict = "TRANSFER_MARGIN_INCONCLUSIVE"
        rationale = (
            "Frozen RESULT-0022 relation beats the best control but does not clear "
            "the predeclared survival margin."
        )

    lane_counts = {
        "train": len(high_mass_train),
        "validation": len(high_mass_validation),
        "holdout": len(high_mass_holdout),
    }
    metrics: dict[str, Any] = {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "benchmark_id": BENCHMARK_ID,
        "engine_version": ENGINE_VERSION,
        "git_commit": _git_commit(),
        "verdict": verdict,
        "rationale": rationale,
        "frozen_relation": {
            "source_result": "RESULT-0022",
            "source_result_review_tier": "AGENT_VALIDATED",
            "best_model_id": FROZEN_MODEL_ID,
            "formula": "log10(L/L_sun) = alpha_hat * log10(M/M_sun), fixed intercept 0",
            "alpha_hat": _round(frozen_alpha),
            "no_refit_performed": True,
            "source_scope": "0.5 <= mass_solar < 2.0, main_sequence_compatible",
        },
        "transfer_slice": {
            "source": "committed DEBCat Route 2 normalized rows",
            "filter": "admitted rows with mass_solar > 2.0",
            "primary_rows_include_all_stage_flags": True,
            "mass_min_exclusive": TRANSFER_MASS_MIN_EXCLUSIVE,
            "row_count": len(high_mass),
            "system_count": len({row["system_id"] for row in high_mass}),
            "lane_counts": lane_counts,
            "holdout_stage_counts": _count_by(high_mass_holdout, "evolutionary_stage_flag"),
            "holdout_luminosity_provenance_counts": _count_by(
                high_mass_holdout, "luminosity_provenance_class"
            ),
            "holdout_luminosity_uncertainty_counts": _count_by(
                high_mass_holdout, "luminosity_uncertainty_class"
            ),
        },
        "judge_and_provenance": {
            "experimental_judge": (
                "DEBCat detached-eclipsing-binary dynamical masses as inputs; "
                "catalogue-reported or Stefan-Boltzmann-derived luminosities as "
                "the observed log_luminosity_solar target."
            ),
            "mass_provenance_counts_high_mass": _count_by(high_mass, "mass_provenance_class"),
            "luminosity_provenance_counts_high_mass": _count_by(
                high_mass, "luminosity_provenance_class"
            ),
            "uncertainty_handling": (
                "No inverse-uncertainty weighting or row exclusion after metric "
                "inspection; uncertainty classes are reported as strata."
            ),
            "live_external_fetch": False,
        },
        "high_mass_holdout": {
            "frozen_relation": _summary(high_mass_holdout, frozen_predictor),
            "by_stage": _summarize_by(
                high_mass_holdout, "evolutionary_stage_flag", frozen_predictor
            ),
            "by_luminosity_provenance": _summarize_by(
                high_mass_holdout, "luminosity_provenance_class", frozen_predictor
            ),
            "by_luminosity_uncertainty": _summarize_by(
                high_mass_holdout, "luminosity_uncertainty_class", frozen_predictor
            ),
        },
        "controls": controls,
        "survival_margin": {
            "predeclared_threshold_dex": SURVIVAL_MARGIN_THRESHOLD_DEX,
            "relation_holdout_mae_dex": _round(relation_holdout_mae),
            "best_control_id": best_control_id,
            "best_control_mae_dex": _round(best_control_mae),
            "best_control_minus_relation_mae_dex": _round(survival_margin),
            "clears_threshold": (
                survival_margin is not None
                and survival_margin >= SURVIVAL_MARGIN_THRESHOLD_DEX
            ),
        },
        "replay": {
            "command": (
                "python3 scripts/run_stellar_ml_high_mass_transfer.py "
                "--output-dir agent_runs/AGENT-RUN-0085 "
                "--review-note docs/reviews/stellar-ml-high-mass-transfer-benchmark.md"
            ),
            "code_reference": SCRIPT_REL,
            "input_file_hashes": {
                ROWS_REL: f"sha256:{_sha256_file(ROWS_REL)}",
                RESULT_0022_REL: f"sha256:{_sha256_file(RESULT_0022_REL)}",
                SCOUT_REL: f"sha256:{_sha256_file(SCOUT_REL)}",
                GATE_B_REL: f"sha256:{_sha256_file(GATE_B_REL)}",
                SCRIPT_REL: f"sha256:{_sha256_file(SCRIPT_REL)}",
            },
            "engine_version": ENGINE_VERSION,
            "git_commit": _git_commit(),
        },
        "limitations": [
            "Regime transfer inside the same committed DEBCat source posture, not an "
            "external-catalog validation.",
            "High-mass rows intentionally include mixed stage flags; the all-stage "
            "primary transfer is stage-confounded and strata must be reviewed.",
            "The frozen RESULT-0022 relation is not refit or widened; failure against "
            "the best control is recorded as a boundary, not rescued.",
            "No claim, prediction, knowledge artifact, discovery wording, or universal "
            "stellar law is promoted.",
        ],
        "output_routing": {
            "canonical_destination": "sandbox_agent_run_plus_review_note",
            "gate_a_status": "not_attempted_relation_failed_best_control",
            "gate_b_status": "replayable_metadata_recorded",
            "result_artifact_created": False,
            "claim_impact": "none",
            "knowledge_impact": "none",
            "review_tier": "none",
        },
    }
    return metrics


def _table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return "\n".join(lines)


def render_report(metrics: dict[str, Any]) -> str:
    margin = metrics["survival_margin"]
    controls = metrics["controls"]
    holdout = metrics["high_mass_holdout"]["frozen_relation"]
    stage_rows = [
        [stage, values["count"], values["mae_dex"], values["median_residual_dex"]]
        for stage, values in metrics["high_mass_holdout"]["by_stage"].items()
    ]
    control_rows = [
        [
            control_id,
            payload.get("mae_dex", payload.get("best_mae_dex")),
            "best" if control_id == margin["best_control_id"] else "",
        ]
        for control_id, payload in controls.items()
    ]
    return f"""# {AGENT_RUN_ID} - Stellar M-L high-mass DEBCat transfer benchmark

**Task:** `{TASK_ID}`
**Benchmark:** `{metrics["benchmark_id"]}`
**Verdict:** `{metrics["verdict"]}`

## Summary

This run freezes the `RESULT-0022` best relation
`log10(L/L_sun) = 4.526004 * log10(M/M_sun)` and transfers it onto committed
DEBCat Route 2 rows with `mass_solar > 2.0`. It performs no live fetch, no
alpha refit, no RESULT-0022 edit, and no rescue model.

The frozen relation scores `MAE={margin["relation_holdout_mae_dex"]}` dex on
the high-mass holdout. The best control is
`{margin["best_control_id"]}` with `MAE={margin["best_control_mae_dex"]}` dex,
so the survival margin (best control minus relation) is
`{margin["best_control_minus_relation_mae_dex"]}` dex against the predeclared
`{margin["predeclared_threshold_dex"]}` dex threshold.

## Transfer Slice

- Source: committed DEBCat Route 2 normalized rows.
- Filter: admitted rows with `mass_solar > 2.0`.
- Rows/systems: `{metrics["transfer_slice"]["row_count"]}` rows across
  `{metrics["transfer_slice"]["system_count"]}` systems.
- Lane counts: `{metrics["transfer_slice"]["lane_counts"]}`.
- Holdout rows: `{holdout["count"]}` rows across `{holdout["system_count"]}`
  systems.

## Controls

{_table(["control", "MAE dex", "note"], control_rows)}

## Stage Strata

{_table(["stage", "holdout rows", "MAE dex", "median residual dex"], stage_rows)}

## Judge And Provenance

{metrics["judge_and_provenance"]["experimental_judge"]} No row is excluded or
weighted after metric inspection; luminosity provenance and uncertainty classes
are recorded as strata in `metrics.json`.

## Decision

`{metrics["verdict"]}`: {metrics["rationale"]} This is a regime-limited boundary
for the frozen RESULT-0022 transfer route, not a universal stellar-law claim.

## Replay

- Command: `{metrics["replay"]["command"]}`
- Code reference: `{metrics["replay"]["code_reference"]}`
- Engine version: `{metrics["replay"]["engine_version"]}`
- Git commit: `{metrics["replay"]["git_commit"]}`

## Output Routing Summary

- Canonical destination: `{metrics["output_routing"]["canonical_destination"]}`.
- Gate A status: `{metrics["output_routing"]["gate_a_status"]}`.
- Gate B status: `{metrics["output_routing"]["gate_b_status"]}`.
- RESULT artifact created: `{metrics["output_routing"]["result_artifact_created"]}`.
- Claim impact: `{metrics["output_routing"]["claim_impact"]}`.
- Knowledge impact: `{metrics["output_routing"]["knowledge_impact"]}`.
"""


def render_review_note(metrics: dict[str, Any]) -> str:
    margin = metrics["survival_margin"]
    return f"""# Stellar M-L High-Mass DEBCat Transfer Benchmark

Task: `TASK-0837`
Sandbox run: `agent_runs/{AGENT_RUN_ID}/`
Related result: `RESULT-0022` (`AGENT_VALIDATED`)
Verdict: **{metrics["verdict"]}**

## Scope

This benchmark tests whether the frozen `RESULT-0022` best relation transfers
from its validated 0.5-2.0 M_sun main-sequence-compatible slice onto the disjoint
high-mass DEBCat Route 2 regime (`mass_solar > 2.0`). It uses only committed
DEBCat rows, performs no live source fetch, and does not edit `RESULT-0022`.

The transfer slice intentionally keeps all high-mass stage flags in the primary
benchmark and reports stage/provenance strata separately. This follows the scout
warning that the high-mass route is useful but stage-confounded.

## Result

- Frozen relation: `log10(L/L_sun) = 4.526004 * log10(M/M_sun)`.
- High-mass holdout: `{metrics["high_mass_holdout"]["frozen_relation"]["count"]}`
  rows across `{metrics["high_mass_holdout"]["frozen_relation"]["system_count"]}`
  systems.
- Frozen relation holdout MAE: `{margin["relation_holdout_mae_dex"]}` dex.
- Best control: `{margin["best_control_id"]}` at
  `{margin["best_control_mae_dex"]}` dex.
- Survival margin: `{margin["best_control_minus_relation_mae_dex"]}` dex
  (best control minus relation), threshold
  `{margin["predeclared_threshold_dex"]}` dex.
- Decision: `{metrics["verdict"]}`.

The frozen relation beats the null and shuffled controls, but it does **not**
beat the nearest-mass high-mass train-lane control. Therefore this run records an
honest high-mass transfer boundary rather than promoting a new canonical result.

## Controls

- `null_high_mass_train_massband_median`: mass-band median luminosity from the
  high-mass train lane.
- `shuffled_relation_predictions`: frozen RESULT-0022 predictions shuffled across
  high-mass holdout rows, preserving prediction distribution but breaking row
  pairing.
- `mass_matched_high_mass_train_nearest`: nearest high-mass train row by
  `log_mass_solar`; predicts that row's observed luminosity.

## Gate-B Replayability

- Command: `python3 scripts/run_stellar_ml_high_mass_transfer.py --output-dir agent_runs/AGENT-RUN-0085 --review-note docs/reviews/stellar-ml-high-mass-transfer-benchmark.md`
- Code reference: `scripts/run_stellar_ml_high_mass_transfer.py`
- Inputs: committed DEBCat rows, `RESULT-0022`, the transfer scout note, and the
  Gate-B replay note; hashes are recorded in
  `agent_runs/{AGENT_RUN_ID}/metrics.json`.
- Engine version: `{metrics["engine_version"]}`.

## Output Routing Summary

- Canonical destination: sandbox `AGENT-RUN-0085` plus this review note.
- Gate A: not attempted; relation failed the best-control survival margin.
- Gate B: replay metadata recorded.
- RESULT impact: no `RESULT-*` artifact created.
- Claim impact: none.
- Knowledge impact: none.
- Limitation: same committed DEBCat source posture; this is a disjoint-regime
  transfer test, not an external-catalog validation or a universal-law claim.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "agent_runs" / AGENT_RUN_ID,
        help="directory for metrics.json and report.md",
    )
    parser.add_argument(
        "--review-note",
        type=Path,
        default=REPO_ROOT / "docs/reviews/stellar-ml-high-mass-transfer-benchmark.md",
        help="review note path to write",
    )
    args = parser.parse_args(argv)

    metrics = build_metrics()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "report.md").write_text(render_report(metrics), encoding="utf-8")
    args.review_note.parent.mkdir(parents=True, exist_ok=True)
    args.review_note.write_text(render_review_note(metrics), encoding="utf-8")
    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
