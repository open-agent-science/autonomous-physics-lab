"""Bounded disjoint A-site cation-family transfer benchmark (TASK-0838).

This module evaluates whether the *frozen* RESULT-0021 baseline model -- the
train-only exact unordered non-oxygen cation-pair mean of
``formation_energy_per_atom`` with a global-train-mean fallback -- transfers
across a chemically-disjoint A-site cation-family split of the committed
MD-0002 slice.

The split is the route the TASK-0817 transfer scout selected and that the
MD-0002 holdout manifest pre-authorizes
(``pre_score_split_axes.cation_pair_family``):

* ``alkali_transition`` family (alkali A-site cation + 3d transition cation);
* ``alkaline_earth_transition`` family (alkaline-earth A-site cation + 3d
  transition cation).

The two families are disjoint by construction, so when one is held out the
frozen cation-pair model has seen *none* of the held-out family's pairs and
falls back to the global train mean on every held-out row. Both holdout
directions are evaluated and the predeclared margin is checked against the best
control (null / shuffled / per-class-median) for each direction.

Guardrails (computed/simulated-is-not-the-judge, TASK-0831): the MD-0002 judge
is computed-DFT (Materials Project, CC BY 4.0). This is a BOUNDED model-vs-model
generalization benchmark, never a discovery, material-design-law,
property-prediction, or device statement.

The module does NOT mutate MD-0002 rows, the frozen baseline engine, or
RESULT-0021. It imports the frozen baseline descriptor (``cation_pair``) and the
frozen group-mean fit (``_fit_group_predictor``) and reuses them unchanged, so
no post-hoc descriptor / feature / hyperparameter change is possible after the
transfer error is read.
"""

from __future__ import annotations

import hashlib
import random
from pathlib import Path
from statistics import mean, median
from typing import Any

import yaml

from physics_lab.datasets.materials_md0002 import load_md0002_dataset
from physics_lab.engines.materials_md0002_baseline import (
    DEFAULT_CONFIG as BASELINE_CONFIG,
    DEFAULT_DATASET,
    DEFAULT_MANIFEST,
    MaterialsMd0002Row,
    _fit_group_predictor,
    _load_formation_energy_rows,
    _residual_metrics,
    cation_pair,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

# Predeclared (frozen BEFORE any transfer error is read) -------------------------------

TASK_ID = "TASK-0838"
AGENT_RUN_ID = "AGENT-RUN-0081"
BENCHMARK_ID = "materials-md0002-cation-family-transfer-benchmark"

# The frozen RESULT-0021 baseline model under test: the exact unordered
# non-oxygen cation-pair train-mean with a global-train-mean fallback.
FROZEN_MODEL_ID = "model_cation_pair_mean"
FROZEN_DESCRIPTOR = "exact_unordered_non_oxygen_cation_pair"

# Deterministic shuffle-control seeds (fixed before scoring).
CONTROL_SEEDS = (0, 1, 2, 7, 11)

# Predeclared A-site cation-family vocabulary (frozen before scoring). Each
# included MD-0002 ternary-oxide row carries exactly one alkali OR alkaline-earth
# A-site cation and exactly one first-row (3d) transition cation, so the family
# label is total and the two classes are mutually exclusive.
ALKALI_CATIONS = frozenset({"Li", "Na", "K", "Rb", "Cs", "Fr"})
ALKALINE_EARTH_CATIONS = frozenset({"Be", "Mg", "Ca", "Sr", "Ba", "Ra"})
TRANSITION_3D_CATIONS = frozenset(
    {"Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn"}
)

FAMILY_ALKALI_TRANSITION = "alkali_transition"
FAMILY_ALKALINE_EARTH_TRANSITION = "alkaline_earth_transition"

# The two predeclared disjoint-family holdout directions. ``train_family`` is the
# class the frozen model is fitted on; ``holdout_family`` is the disjoint class it
# must transfer to.
TRANSFER_DIRECTIONS = (
    {
        "direction_id": "hold_out_alkaline_earth_transition",
        "train_family": FAMILY_ALKALI_TRANSITION,
        "holdout_family": FAMILY_ALKALINE_EARTH_TRANSITION,
    },
    {
        "direction_id": "hold_out_alkali_transition",
        "train_family": FAMILY_ALKALINE_EARTH_TRANSITION,
        "holdout_family": FAMILY_ALKALI_TRANSITION,
    },
)

# PREDECLARED pass/fail rule (stated before any metric is computed):
#   The frozen cation-pair model must beat the BEST control's holdout MAE by at
#   least MIN_TRANSFER_MARGIN_EV_PER_ATOM (absolute, eV/atom) on the held-out
#   family, in BOTH disjoint-family directions, to count as transferring.
# Margin chosen by analogy with the in-split benchmark gate
# (MIN_ABSOLUTE_IMPROVEMENT = 0.05 eV/atom in the baseline contract); transfer is
# a strictly harder regime, so the same 0.05 eV/atom floor over the best control
# is a conservative, non-trivial bar that is not gamed by the global-mean null.
MIN_TRANSFER_MARGIN_EV_PER_ATOM = 0.05

# Controls evaluated on the held-out family (each is a train-only comparator).
CONTROL_IDS = ("null_global_mean", "shuffled_cation_pair", "per_class_median")


def family_label(row: MaterialsMd0002Row) -> str:
    """Return the predeclared disjoint A-site cation-family label for a row.

    Raises if a row cannot be assigned to exactly one of the two declared
    families -- the route requires a clean, total partition with no peeking.
    """

    has_alkali = any(cation in ALKALI_CATIONS for cation in row.cations)
    has_alkaline_earth = any(
        cation in ALKALINE_EARTH_CATIONS for cation in row.cations
    )
    has_transition = any(
        cation in TRANSITION_3D_CATIONS for cation in row.cations
    )
    if not has_transition:
        raise ValueError(
            f"{row.row_id} has no first-row transition cation; family split undefined"
        )
    if has_alkali and not has_alkaline_earth:
        return FAMILY_ALKALI_TRANSITION
    if has_alkaline_earth and not has_alkali:
        return FAMILY_ALKALINE_EARTH_TRANSITION
    raise ValueError(
        f"{row.row_id} is not in exactly one declared A-site family "
        f"(cations={row.cations})"
    )


def run_materials_md0002_transfer_benchmark(
    config_path: Path | str = BASELINE_CONFIG,
) -> dict[str, Any]:
    """Run the frozen-baseline disjoint-family transfer benchmark.

    Returns JSON-safe metrics. Deterministic: re-running yields identical output.
    """

    config_path = Path(config_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    _assert_config_matches_frozen_baseline_contract(config)

    dataset_path = Path(config["dataset"]["dataset_file"])
    manifest_path = Path(config["dataset"]["holdout_manifest"])
    dataset = load_md0002_dataset(dataset_path)
    rows = _load_formation_energy_rows(dataset)

    families = _partition_by_family(rows)
    family_counts = {family: len(family_rows) for family, family_rows in families.items()}

    directions = [
        _evaluate_direction(direction, families) for direction in TRANSFER_DIRECTIONS
    ]
    transfers_in_all_directions = all(
        direction["clears_margin_over_best_control"] for direction in directions
    )
    verdict = "SANDBOX_PASS" if transfers_in_all_directions else "SANDBOX_FAIL"
    transfer_outcome = (
        "transfers_across_disjoint_family"
        if transfers_in_all_directions
        else "advantage_is_family_localized"
    )

    return {
        "task_id": TASK_ID,
        "agent_run_id": AGENT_RUN_ID,
        "benchmark_id": BENCHMARK_ID,
        "frozen_model_under_test": {
            "model_id": FROZEN_MODEL_ID,
            "descriptor": FROZEN_DESCRIPTOR,
            "source_result": "RESULT-0021",
            "source_run": "results/EXP-0014/RUN-0001/result.yaml",
            "definition": (
                "Train-only mean of formation_energy_per_atom grouped by the exact "
                "unordered non-oxygen cation pair; unseen pairs fall back to the "
                "global train mean. Imported unchanged from the frozen baseline engine."
            ),
            "frozen_before_reading_transfer_error": True,
            "post_hoc_descriptor_or_hyperparameter_change": False,
        },
        "method": (
            "Hold out one complete disjoint A-site cation-family class, fit the "
            "frozen RESULT-0021 cation-pair-mean model on the disjoint class, and "
            "score holdout MAE on the held-out family against null / shuffled / "
            "per-class-median controls. Both holdout directions are evaluated."
        ),
        "predeclared_split": {
            "route": "disjoint_a_site_cation_family_holdout",
            "scout_review_note": "docs/reviews/materials-independent-transfer-route-scout.md",
            "scout_task": "TASK-0817",
            "manifest_split_axis": "cation_pair_family",
            "family_vocabulary": {
                FAMILY_ALKALI_TRANSITION: sorted(ALKALI_CATIONS | TRANSITION_3D_CATIONS),
                FAMILY_ALKALINE_EARTH_TRANSITION: sorted(
                    ALKALINE_EARTH_CATIONS | TRANSITION_3D_CATIONS
                ),
            },
            "directions": [dict(direction) for direction in TRANSFER_DIRECTIONS],
            "leakage": "none_by_construction_families_share_no_a_site_cation",
        },
        "predeclared_pass_fail": {
            "metric": "held_out_family_holdout_mae_eV_per_atom",
            "rule": (
                "Frozen model must beat the BEST control's holdout MAE by at least "
                f"{MIN_TRANSFER_MARGIN_EV_PER_ATOM} eV/atom on the held-out family "
                "in BOTH disjoint-family directions."
            ),
            "minimum_margin_over_best_control_eV_per_atom": MIN_TRANSFER_MARGIN_EV_PER_ATOM,
            "controls": list(CONTROL_IDS),
            "control_seeds": list(CONTROL_SEEDS),
            "declared_before_metric_computation": True,
        },
        "input_references": {
            "config": config_path.as_posix(),
            "dataset": dataset_path.as_posix(),
            "holdout_manifest": manifest_path.as_posix(),
            "transfer_route_scout": "docs/reviews/materials-independent-transfer-route-scout.md",
            "baseline_result": "results/EXP-0014/RUN-0001/result.yaml",
        },
        "input_file_hashes": {
            config_path.as_posix(): _sha256(config_path),
            dataset_path.as_posix(): _sha256(dataset_path),
            manifest_path.as_posix(): _sha256(manifest_path),
        },
        "dataset_summary": {
            "dataset_family": dataset.payload["dataset_family"],
            "source_id": dataset.payload["source_id"],
            "source_version": str(dataset.payload["source_version"]),
            "snapshot_checksum_sha256": dataset.payload["snapshot_checksum_sha256"],
            "property_kind": "formation_energy_per_atom",
            "units": "eV_per_atom",
            "provenance_class": "computed_dft",
            "license": "CC_BY_4_0",
            "row_count": len(rows),
            "family_counts": family_counts,
            "live_external_fetch": False,
        },
        "transfer_directions": directions,
        "transfer_summary": {
            "transfers_in_all_directions": transfers_in_all_directions,
            "transfer_outcome": transfer_outcome,
            "per_direction_clears_margin": {
                direction["direction_id"]: direction["clears_margin_over_best_control"]
                for direction in directions
            },
        },
        "verdict": verdict,
        "limitations": [
            "Computed-DFT Materials Project formation energies only (CC BY 4.0); no "
            "experimental measurements, so residuals are computed-DFT benchmark "
            "diagnostics, not measurement errors.",
            "Bounded model-vs-model generalization benchmark on one frozen 362-row "
            "MD-0002 slice; not a materials-discovery, material-design-law, "
            "property-prediction, synthesis, device, or biomedical claim.",
            "Exactly one disjoint A-site cation-family split (alkali-transition vs "
            "alkaline-earth-transition); a single family axis, not a broad transfer "
            "study.",
            "By construction the two families share no cation pair, so the frozen "
            "cation-pair model falls back to the global train mean on every held-out "
            "row; the test measures whether that fallback still beats the controls.",
            "Formation energy is evaluated alone; band gap is neither scored nor pooled.",
            "The frozen baseline model and descriptor were fixed before any transfer "
            "error was read; no refit, feature add, or split change was made to rescue "
            "a negative outcome.",
        ],
        "output_routing": {
            "canonical_destination": "agent_runs/AGENT-RUN-0081/ and transfer-benchmark review note",
            "review_tier": "none",
            "gate_a_status": (
                "passed_sandbox_gates_packaging_blocked_default_sandbox"
                if transfers_in_all_directions
                else "not_eligible_negative_transfer_result"
            ),
            "gate_b_status": "replayable_not_yet_independently_replayed",
            "claim_impact": "no claim change",
            "knowledge_impact": "no knowledge change",
            "publication_blocker": (
                "A published RESULT requires linking into protected hypothesis/"
                "experiment artifacts outside this task's scope; default to sandbox."
            ),
        },
    }


def _assert_config_matches_frozen_baseline_contract(config: dict[str, Any]) -> None:
    """Bind to the same frozen MD-0002 source the baseline result used."""

    if config.get("task_id") != "TASK-0703":
        raise ValueError("Transfer benchmark must reuse the frozen TASK-0703 baseline config")
    dataset = config.get("dataset", {})
    if dataset.get("dataset_file") != DEFAULT_DATASET.as_posix():
        raise ValueError("Transfer benchmark must use the committed MD-0002 dataset")
    if dataset.get("holdout_manifest") != DEFAULT_MANIFEST.as_posix():
        raise ValueError("Transfer benchmark must use the committed MD-0002 holdout manifest")
    if dataset.get("property_kind") != "formation_energy_per_atom":
        raise ValueError("Transfer benchmark must score formation_energy_per_atom only")


def _partition_by_family(
    rows: list[MaterialsMd0002Row],
) -> dict[str, list[MaterialsMd0002Row]]:
    partition: dict[str, list[MaterialsMd0002Row]] = {
        FAMILY_ALKALI_TRANSITION: [],
        FAMILY_ALKALINE_EARTH_TRANSITION: [],
    }
    for row in rows:
        partition[family_label(row)].append(row)
    for family, family_rows in partition.items():
        if not family_rows:
            raise ValueError(f"Disjoint-family partition produced an empty class: {family}")
    return partition


def _evaluate_direction(
    direction: dict[str, str],
    families: dict[str, list[MaterialsMd0002Row]],
) -> dict[str, Any]:
    train_rows = sorted(
        families[direction["train_family"]], key=lambda row: row.material_id
    )
    holdout_rows = sorted(
        families[direction["holdout_family"]], key=lambda row: row.material_id
    )
    global_train_mean = mean(row.value for row in train_rows)

    # Frozen RESULT-0021 model: exact cation-pair train-mean, global fallback.
    frozen_predictor = _fit_group_predictor(train_rows, cation_pair, global_train_mean)
    frozen_mae = float(_residual_metrics(holdout_rows, frozen_predictor)["mae"])

    # How often does the frozen model actually have a learned pair (vs fallback)?
    train_pairs = {cation_pair(row) for row in train_rows}
    holdout_pairs = {cation_pair(row) for row in holdout_rows}
    holdout_rows_using_fallback = sum(
        1 for row in holdout_rows if cation_pair(row) not in train_pairs
    )

    controls = _evaluate_controls(train_rows, holdout_rows, global_train_mean)
    best_control_id = min(controls, key=lambda cid: controls[cid]["holdout_mae"])
    best_control_mae = controls[best_control_id]["holdout_mae"]
    margin_over_best_control = round(best_control_mae - frozen_mae, 6)
    clears_margin = margin_over_best_control >= MIN_TRANSFER_MARGIN_EV_PER_ATOM

    return {
        "direction_id": direction["direction_id"],
        "train_family": direction["train_family"],
        "holdout_family": direction["holdout_family"],
        "train_count": len(train_rows),
        "holdout_count": len(holdout_rows),
        "shared_cation_pairs_between_families": sorted(train_pairs & holdout_pairs),
        "holdout_rows_falling_back_to_global_mean": holdout_rows_using_fallback,
        "frozen_model_holdout_mae": frozen_mae,
        "controls": controls,
        "best_control_id": best_control_id,
        "best_control_holdout_mae": best_control_mae,
        "margin_over_best_control_eV_per_atom": margin_over_best_control,
        "required_margin_eV_per_atom": MIN_TRANSFER_MARGIN_EV_PER_ATOM,
        "clears_margin_over_best_control": clears_margin,
    }


def _evaluate_controls(
    train_rows: list[MaterialsMd0002Row],
    holdout_rows: list[MaterialsMd0002Row],
    global_train_mean: float,
) -> dict[str, Any]:
    # null control: predict the global train mean for every held-out row.
    null_predictor = lambda _row: global_train_mean  # noqa: E731
    null_mae = float(_residual_metrics(holdout_rows, null_predictor)["mae"])

    # per-class-median control: predict the train family's median for every row.
    train_median = float(median(row.value for row in train_rows))
    median_predictor = lambda _row: train_median  # noqa: E731
    median_mae = float(_residual_metrics(holdout_rows, median_predictor)["mae"])

    # shuffled control: permute the cation-pair labels on train before grouping,
    # then evaluate with the frozen descriptor. Deterministic across fixed seeds;
    # reported as the min over seeds (the strongest -- hardest to beat -- control).
    labels = [cation_pair(row) for row in train_rows]
    shuffle_maes: list[float] = []
    per_seed: list[dict[str, Any]] = []
    for seed in CONTROL_SEEDS:
        shuffled_labels = list(labels)
        random.Random(seed).shuffle(shuffled_labels)
        shuffled_predictor = _fit_group_predictor(
            train_rows, cation_pair, global_train_mean, labels=shuffled_labels
        )
        seed_mae = float(_residual_metrics(holdout_rows, shuffled_predictor)["mae"])
        shuffle_maes.append(seed_mae)
        per_seed.append({"seed": seed, "holdout_mae": seed_mae})
    shuffle_mae = round(min(shuffle_maes), 6)

    return {
        "null_global_mean": {
            "holdout_mae": round(null_mae, 6),
            "description": "Global train-mean prediction for every held-out row.",
        },
        "per_class_median": {
            "holdout_mae": round(median_mae, 6),
            "description": "Train-family median prediction for every held-out row.",
        },
        "shuffled_cation_pair": {
            "holdout_mae": shuffle_mae,
            "description": (
                "Cation-pair labels permuted on train before grouping; min holdout "
                "MAE over fixed seeds (strongest shuffle control)."
            ),
            "seeds": list(CONTROL_SEEDS),
            "per_seed": per_seed,
        },
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
