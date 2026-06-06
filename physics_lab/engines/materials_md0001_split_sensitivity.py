"""Materials MD-0001 split-sensitivity audit (TASK-0601).

MD-0001 has only 169 included rows per axis and a single committed 33-row holdout
(`material_id_mod10_70_10_20`). Before MD-0001 is used as the basis for wider
Materials tasks, this audit measures whether the committed formation-energy and
band-gap baseline conclusions are stable under predeclared alternative splits, or
whether they depend on the particular small holdout.

It reuses the committed TASK-0550 baseline primitives (row inclusion, the three
declared baselines, and residual metrics) so the comparison is faithful, keeps
formation energy and band gap as separate axes, and never pools them. It does not
fetch data, tune splits after seeing scores, propose materials, promote claims,
or issue materials guidance.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from physics_lab.engines.materials_md0001_baseline import (
    MaterialsRow,
    _fit_baselines,
    _included_rows,
    _load_axis_rows,
    _residual_metrics,
    cation_group,
    formula_family,
)

BASELINE_IDS = ("global_mean", "global_median", "cation_group_mean")

# Predeclared deterministic seeds for the random-resampling diagnostic. Python's
# random.Random Mersenne Twister is stable across Python versions and platforms.
SEEDED_RANDOM_SEEDS = (0, 1, 2, 3, 4)
SEEDED_RANDOM_TRAIN_FRACTION = 0.7

DEFAULT_AXES = (
    {
        "property_kind": "formation_energy_per_atom",
        "dataset_file": "data/materials/md-0001-materials-project-formation-energy.yaml",
    },
    {
        "property_kind": "band_gap",
        "dataset_file": "data/materials/md-0001-materials-project-band-gap.yaml",
    },
)
DEFAULT_COMMITTED_METRICS = Path("agent_runs/AGENT-RUN-0057/metrics.json")

# Predeclared robustness rule. The committed-holdout winning baseline is
# "split_robust" for an axis only if BOTH conditions hold:
#   1. it is also the seeded-random mean-MAE winner and wins a strong majority of
#      seeds (>= MIN_SEED_WINS of len(SEEDED_RANDOM_SEEDS)); and
#   2. its seeded-mean margin over the runner-up baseline exceeds the larger of
#      the two baselines' across-seed standard deviations (effect > noise).
MIN_SEED_WINS = 4


def run_materials_md0001_split_sensitivity_audit(
    *,
    axes: tuple[dict[str, str], ...] = DEFAULT_AXES,
    committed_metrics_path: Path | str = DEFAULT_COMMITTED_METRICS,
) -> dict[str, Any]:
    """Run the deterministic TASK-0601 MD-0001 split-sensitivity audit."""
    committed_metrics_path = Path(committed_metrics_path)
    committed = json.loads(committed_metrics_path.read_text(encoding="utf-8"))

    axis_outputs: dict[str, Any] = {}
    overall: dict[str, str] = {}
    for axis in axes:
        property_kind = axis["property_kind"]
        rows = _included_rows(
            _load_axis_rows(Path(axis["dataset_file"])), expected_property_kind=property_kind
        )
        committed_axis = committed["axis_outputs"][property_kind]
        committed_holdout_winner = committed_axis["best_holdout_baseline"]["baseline_id"]

        seeded = _seeded_random_diagnostic(rows)
        cation_holdout = _leave_one_group_out(rows, grouper=cation_group)
        formula_holdout = _leave_one_group_out(rows, grouper=formula_family)

        robustness = _split_robustness(
            committed_holdout_winner=committed_holdout_winner,
            seeded=seeded,
        )
        overall[property_kind] = robustness["verdict"]

        axis_outputs[property_kind] = {
            "dataset_file": axis["dataset_file"],
            "row_count": len(rows),
            "committed_reference": {
                "split_id": committed["split_policy"]["split_id"],
                "best_holdout_baseline": committed_axis["best_holdout_baseline"],
                "best_validation_baseline": committed_axis["best_validation_baseline"],
            },
            "seeded_random_70_30": seeded,
            "leave_one_cation_group_out": cation_holdout,
            "leave_one_formula_family_out": formula_holdout,
            "split_robustness": robustness,
        }

    return {
        "task_id": "TASK-0601",
        "benchmark_id": "materials-md0001-split-sensitivity-audit",
        "input_references": {
            "committed_metrics": committed_metrics_path.as_posix(),
            "committed_baseline_task": "TASK-0550",
            "committed_replay_task": "TASK-0578",
            "formation_energy_dataset": axes[0]["dataset_file"],
            "band_gap_dataset": axes[1]["dataset_file"],
        },
        "declared_alternative_splits": {
            "seeded_random_70_30": (
                "Five predeclared seeded shuffles of the included rows, each split "
                "70/30 into train/holdout. Measures whether the committed-split "
                "baseline ordering survives random resampling of the small holdout."
            ),
            "leave_one_cation_group_out": (
                "Each cation group is held out once while baselines fit on the "
                "remaining groups. Extrapolation stress diagnostic: a fully held-out "
                "cation group has no train rows, so cation_group_mean falls back to "
                "the global mean."
            ),
            "leave_one_formula_family_out": (
                "Each oxide stoichiometry family (monoxide, sesquioxide, dioxide, "
                "...) is held out once. Extrapolation stress diagnostic to an unseen "
                "oxide stoichiometry. Note: all MD-0001 rows are oxides, so the anion "
                "family is degenerate and is replaced by this oxide-stoichiometry "
                "diagnostic."
            ),
        },
        "robustness_rule": {
            "min_seed_wins": MIN_SEED_WINS,
            "seed_count": len(SEEDED_RANDOM_SEEDS),
            "rule": (
                "split_robust iff the committed-holdout winner is also the seeded "
                "mean winner with >= min_seed_wins seed wins AND its seeded-mean "
                "margin over the runner-up exceeds the larger across-seed std."
            ),
        },
        "axis_outputs": axis_outputs,
        "overall_split_robustness": overall,
        "verdict": "INCONCLUSIVE",
        "limitations": [
            "Computed DFT Materials Project stable-binary-oxide rows only; 169 rows "
            "per axis is small, so even alternative splits share the same dataset.",
            "Formation energy and band gap are separate axes and are never pooled.",
            "Baselines are the committed null/composition-aware controls, not tuned "
            "ML models; the audit tests split stability, not model quality.",
            "Leave-one-group-out diagnostics are extrapolation stress tests; with no "
            "train rows for a held-out group, cation_group_mean degenerates to the "
            "global mean by design.",
            "Sandbox audit evidence only. No RESULT, PRED, CLAIM, KNOW, materials "
            "guidance, or discovery wording is promoted, and the committed MD-0001 "
            "split, datasets, and result artifact are unchanged.",
        ],
        "output_routing": {
            "task_verdict": "INCONCLUSIVE",
            "canonical_destination": "docs/reviews/materials-md0001-split-sensitivity-audit.md",
            "review_tier": "none",
            "gate_a_status": "not_attempted",
            "gate_b_status": "not_applicable",
            "claim_impact": "none",
            "knowledge_impact": "none",
            "result_impact": "no RESULT artifact created",
        },
    }


# --------------------------------------------------------------------------- #
# Diagnostics
# --------------------------------------------------------------------------- #


def _seeded_random_diagnostic(rows: list[MaterialsRow]) -> dict[str, Any]:
    per_seed: list[dict[str, Any]] = []
    per_baseline_holdout: dict[str, list[float]] = {bid: [] for bid in BASELINE_IDS}
    win_counts: dict[str, int] = {bid: 0 for bid in BASELINE_IDS}
    for seed in SEEDED_RANDOM_SEEDS:
        shuffled = list(rows)
        random.Random(seed).shuffle(shuffled)
        cut = int(round(SEEDED_RANDOM_TRAIN_FRACTION * len(shuffled)))
        train, holdout = shuffled[:cut], shuffled[cut:]
        holdout_mae = _baseline_holdout_mae(train, holdout)
        winner = min(holdout_mae, key=lambda bid: holdout_mae[bid])
        win_counts[winner] += 1
        for bid in BASELINE_IDS:
            per_baseline_holdout[bid].append(holdout_mae[bid])
        per_seed.append(
            {
                "seed": seed,
                "train_count": len(train),
                "holdout_count": len(holdout),
                "holdout_mae": {bid: round(holdout_mae[bid], 6) for bid in BASELINE_IDS},
                "winner": winner,
            }
        )

    per_baseline = {
        bid: {
            "holdout_mae_mean": round(mean(per_baseline_holdout[bid]), 6),
            "holdout_mae_min": round(min(per_baseline_holdout[bid]), 6),
            "holdout_mae_max": round(max(per_baseline_holdout[bid]), 6),
            "holdout_mae_std": round(pstdev(per_baseline_holdout[bid]), 6),
            "seed_win_count": win_counts[bid],
        }
        for bid in BASELINE_IDS
    }
    mean_winner = min(per_baseline, key=lambda bid: per_baseline[bid]["holdout_mae_mean"])
    return {
        "seeds": list(SEEDED_RANDOM_SEEDS),
        "train_fraction": SEEDED_RANDOM_TRAIN_FRACTION,
        "per_seed": per_seed,
        "per_baseline": per_baseline,
        "mean_mae_winner": mean_winner,
    }


def _leave_one_group_out(rows: list[MaterialsRow], *, grouper: Any) -> dict[str, Any]:
    groups = sorted({grouper(row) for row in rows})
    per_group: dict[str, Any] = {}
    macro: dict[str, list[float]] = {bid: [] for bid in BASELINE_IDS}
    for group in groups:
        holdout = [row for row in rows if grouper(row) == group]
        train = [row for row in rows if grouper(row) != group]
        if not holdout or not train:
            continue
        holdout_mae = _baseline_holdout_mae(train, holdout)
        per_group[group] = {
            "holdout_count": len(holdout),
            "train_count": len(train),
            "holdout_mae": {bid: round(holdout_mae[bid], 6) for bid in BASELINE_IDS},
        }
        for bid in BASELINE_IDS:
            macro[bid].append(holdout_mae[bid])
    macro_mae = {
        bid: (round(mean(macro[bid]), 6) if macro[bid] else None) for bid in BASELINE_IDS
    }
    valid = {bid: value for bid, value in macro_mae.items() if value is not None}
    macro_winner = min(valid, key=lambda bid: valid[bid]) if valid else None
    return {
        "group_count": len(per_group),
        "per_group": per_group,
        "macro_holdout_mae": macro_mae,
        "macro_mae_winner": macro_winner,
    }


def _split_robustness(
    *, committed_holdout_winner: str, seeded: dict[str, Any]
) -> dict[str, Any]:
    per_baseline = seeded["per_baseline"]
    mean_winner = seeded["mean_mae_winner"]
    winner_seed_wins = per_baseline[committed_holdout_winner]["seed_win_count"]

    # Runner-up = best baseline by seeded mean other than the committed winner.
    runner_up = min(
        (bid for bid in BASELINE_IDS if bid != committed_holdout_winner),
        key=lambda bid: per_baseline[bid]["holdout_mae_mean"],
    )
    winner_mean = per_baseline[committed_holdout_winner]["holdout_mae_mean"]
    runner_up_mean = per_baseline[runner_up]["holdout_mae_mean"]
    margin = round(runner_up_mean - winner_mean, 6)
    noise = round(
        max(
            per_baseline[committed_holdout_winner]["holdout_mae_std"],
            per_baseline[runner_up]["holdout_mae_std"],
        ),
        6,
    )

    winner_consistent = (
        mean_winner == committed_holdout_winner and winner_seed_wins >= MIN_SEED_WINS
    )
    margin_exceeds_noise = margin > noise
    is_robust = winner_consistent and margin_exceeds_noise

    return {
        "committed_holdout_winner": committed_holdout_winner,
        "seeded_mean_winner": mean_winner,
        "winner_seed_win_count": winner_seed_wins,
        "runner_up_baseline": runner_up,
        "seeded_mean_margin_over_runner_up": margin,
        "across_seed_noise": noise,
        "winner_consistent": winner_consistent,
        "margin_exceeds_noise": margin_exceeds_noise,
        "verdict": "split_robust" if is_robust else "split_sensitive",
    }


def _baseline_holdout_mae(
    train: list[MaterialsRow], holdout: list[MaterialsRow]
) -> dict[str, float]:
    baselines = _fit_baselines(train)
    return {
        bid: float(_residual_metrics(holdout, predictor)["mae"])
        for bid, predictor in baselines.items()
    }
