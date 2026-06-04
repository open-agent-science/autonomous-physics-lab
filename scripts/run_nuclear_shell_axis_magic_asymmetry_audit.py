"""TASK-0321 nuclear shell-axis magic-N versus magic-Z asymmetry audit.

This sandbox-only runner separates proton-axis, neutron-axis, and product
behavior on committed TASK-0310 surfaces. It evaluates magic-N, magic-Z,
near-magic, double-magic, and deterministic non-magic A-matched control
subsets without fetching live data, scoring prospective prediction entries,
writing canonical RESULT-* artifacts, updating claims, or editing knowledge.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.engines.nuclear_mass_baselines import MAGIC_NUMBERS  # noqa: E402

import scripts.run_nuclear_shell_axis_full_known_audit as full_known  # noqa: E402


AGENT_RUN_ID = "AGENT-RUN-0021"
TASK_ID = "TASK-0321"
SPARSE_WARNING_THRESHOLD = 10
SHUFFLE_OFFSET = full_known.SHUFFLE_OFFSET

AUDIT_CANDIDATE_IDS = (
    "FULLKNOWN-SHELL-001",
    "FULLKNOWN-SHELL-002",
    "FULLKNOWN-SHELL-003",
    "FULLKNOWN-SHELL-004",
    "FULLKNOWN-SHELL-005",
    "FULLKNOWN-SHELL-006",
)

FOCUS_SUBSETS = (
    "primary_holdout",
    "magic_n",
    "magic_z",
    "near_magic",
    "double_magic",
    "non_magic_matched_magic_n",
    "non_magic_matched_magic_z",
    "non_magic_matched_near_magic",
    "non_magic_matched_double_magic",
)


def _is_magic(row: dict[str, Any]) -> bool:
    return int(row["Z"]) in MAGIC_NUMBERS or int(row["N"]) in MAGIC_NUMBERS


def _subset_indices(rows: list[dict[str, Any]], subset_id: str) -> list[int]:
    return [
        idx
        for idx, row in enumerate(rows)
        if subset_id in full_known._surface_subset_ids(row)  # noqa: SLF001
    ]


def _matched_non_magic_indices(
    rows: list[dict[str, Any]],
    target_indices: list[int],
) -> list[int]:
    """Select deterministic non-magic controls matched by A without replacement."""
    target_set = set(target_indices)
    pool = [
        idx
        for idx, row in enumerate(rows)
        if idx not in target_set and not _is_magic(row)
    ]
    selected: list[int] = []
    selected_set: set[int] = set()
    for target_idx in target_indices:
        target = rows[target_idx]
        available = [idx for idx in pool if idx not in selected_set]
        if not available:
            break
        best_idx = min(
            available,
            key=lambda idx: (
                abs(int(rows[idx]["A"]) - int(target["A"])),
                str(rows[idx]["source_surface"]) != str(target["source_surface"]),
                str(rows[idx]["row_id"]),
            ),
        )
        selected.append(best_idx)
        selected_set.add(best_idx)
    return selected


def build_subset_index(rows: list[dict[str, Any]]) -> dict[str, list[int]]:
    """Return base and matched subset membership over the audit rows."""
    subset_index: dict[str, list[int]] = {
        subset_id: _subset_indices(rows, subset_id)
        for subset_id in (
            "full_known",
            "primary_holdout",
            "training_slice",
            "magic_n",
            "magic_z",
            "near_magic",
            "double_magic",
        )
    }
    matched_sources = {
        "non_magic_matched_magic_n": "magic_n",
        "non_magic_matched_magic_z": "magic_z",
        "non_magic_matched_near_magic": "near_magic",
        "non_magic_matched_double_magic": "double_magic",
    }
    for matched_id, source_id in matched_sources.items():
        subset_index[matched_id] = _matched_non_magic_indices(rows, subset_index[source_id])
    return subset_index


def _summarize_index(
    rows: list[dict[str, Any]],
    subset_index: dict[str, list[int]],
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for subset_id, indices in subset_index.items():
        out[subset_id] = {
            "row_count": len(indices),
            "nuclide_ids": [str(rows[idx]["nuclide_id"]) for idx in indices],
            "sparse_warning": (
                subset_id == "double_magic" or subset_id.startswith("non_magic_matched_")
            )
            and len(indices) < SPARSE_WARNING_THRESHOLD,
        }
    return out


def _baseline_metrics(
    rows: list[dict[str, Any]],
    subset_index: dict[str, list[int]],
) -> dict[str, dict[str, Any]]:
    return {
        subset_id: full_known._summarize_errors(  # noqa: SLF001
            [float(rows[idx]["baseline_residual_mev"]) for idx in indices]
        )
        for subset_id, indices in sorted(subset_index.items())
    }


def _fit_candidate(
    candidate: dict[str, Any],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
    proton_only_beta: float,
) -> tuple[np.ndarray, dict[str, float]]:
    feature_names = tuple(candidate["feature_names"])
    fit_mode = str(candidate.get("fit_mode", "lstsq"))
    if fit_mode == "fixed_zero":
        return np.asarray([], dtype=float), {}
    if fit_mode == "lstsq":
        beta = full_known._fit_lstsq(feature_names, training_rows, training_residuals)  # noqa: SLF001
    elif fit_mode == "lstsq_sign_inverted":
        beta = np.asarray([-proton_only_beta], dtype=float)
    elif fit_mode == "lstsq_shuffled":
        train_x = full_known._shuffled_feature_array(  # noqa: SLF001
            feature_names,
            training_rows,
            offset=SHUFFLE_OFFSET,
        )
        beta, *_ = np.linalg.lstsq(train_x, training_residuals, rcond=None)
    else:
        raise RuntimeError(f"Unknown fit_mode {fit_mode!r}")
    return beta, {name: float(value) for name, value in zip(feature_names, beta)}


def _candidate_residuals(
    candidate: dict[str, Any],
    *,
    rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
    proton_only_beta: float,
) -> tuple[list[float], dict[str, float]]:
    feature_names = tuple(candidate["feature_names"])
    fit_mode = str(candidate.get("fit_mode", "lstsq"))
    beta, fitted_coefficients = _fit_candidate(
        candidate,
        training_rows,
        training_residuals,
        proton_only_beta,
    )
    shuffled_features = None
    if fit_mode == "lstsq_shuffled":
        shuffled_features = full_known._shuffled_feature_array(  # noqa: SLF001
            feature_names,
            rows,
            offset=SHUFFLE_OFFSET,
        )

    residuals: list[float] = []
    for row_idx, row in enumerate(rows):
        if fit_mode == "fixed_zero":
            correction = 0.0
        elif shuffled_features is not None:
            correction = float(np.asarray(shuffled_features[row_idx], dtype=float) @ beta)
        else:
            values = full_known._feature_vector(  # noqa: SLF001
                feature_names,
                z=int(row["Z"]),
                n=int(row["N"]),
            )
            correction = float(np.asarray(values, dtype=float) @ beta)
        predicted = float(row["baseline_predicted_mev"]) + correction
        residuals.append(float(row["observed_mev"]) - predicted)
    return residuals, fitted_coefficients


def _metrics_for_residuals(
    residuals: list[float],
    *,
    subset_index: dict[str, list[int]],
) -> dict[str, dict[str, Any]]:
    return {
        subset_id: full_known._summarize_errors(  # noqa: SLF001
            [residuals[idx] for idx in indices]
        )
        for subset_id, indices in sorted(subset_index.items())
    }


def _delta_by_subset(
    candidate_metrics: dict[str, dict[str, Any]],
    baseline: dict[str, dict[str, Any]],
) -> dict[str, float | None]:
    return {
        subset_id: full_known._delta_mae(candidate_metrics.get(subset_id), baseline.get(subset_id))  # noqa: SLF001
        for subset_id in sorted(baseline)
    }


def _worst_subset_regression(delta_by_subset: dict[str, float | None]) -> dict[str, Any]:
    positive = {
        key: value
        for key, value in delta_by_subset.items()
        if value is not None and value > 0.0
    }
    if not positive:
        return {"subset_id": "none", "delta_mae_mev": 0.0}
    subset_id, delta = max(positive.items(), key=lambda item: item[1])
    return {"subset_id": subset_id, "delta_mae_mev": float(delta)}


def _directional_label(item: dict[str, Any]) -> str:
    deltas = item["focus_delta_mae_mev"]
    magic_n = deltas["magic_n"]
    magic_z = deltas["magic_z"]
    if magic_n is None or magic_z is None:
        return "TOO_SPARSE_TO_INTERPRET"
    if magic_n >= 0.0 and magic_z >= 0.0:
        return "NO_MAGIC_AXIS_SUPPORT"
    margin = 0.05
    if magic_n < 0.0 and magic_z < 0.0 and abs(float(magic_n) - float(magic_z)) <= margin:
        return "SYMMETRIC_OR_TIED"
    if magic_n < magic_z - margin:
        return "NEUTRON_DOMINANT"
    if magic_z < magic_n - margin:
        return "PROTON_DOMINANT"
    return "TIED"


def _matched_contrast(item: dict[str, Any], magic_subset: str, matched_subset: str) -> float | None:
    deltas = item["focus_delta_mae_mev"]
    magic_delta = deltas.get(magic_subset)
    matched_delta = deltas.get(matched_subset)
    if magic_delta is None or matched_delta is None:
        return None
    return float(magic_delta) - float(matched_delta)


def _overall_direction(candidate_items: list[dict[str, Any]]) -> dict[str, Any]:
    primary = [
        item
        for item in candidate_items
        if item["candidate_id"]
        in {"FULLKNOWN-SHELL-001", "FULLKNOWN-SHELL-002", "FULLKNOWN-SHELL-003"}
    ]
    labels = {item["candidate_id"]: item["directional_label"] for item in primary}
    neutron_dominant = sum(1 for label in labels.values() if label == "NEUTRON_DOMINANT")
    proton_dominant = sum(1 for label in labels.values() if label == "PROTON_DOMINANT")
    tied = sum(1 for label in labels.values() if label in {"SYMMETRIC_OR_TIED", "TIED"})
    if neutron_dominant >= 2:
        verdict = "NEUTRON_DOMINANT_BUT_SPARSE"
    elif proton_dominant >= 2:
        verdict = "PROTON_DOMINANT_BUT_SPARSE"
    elif tied >= 2:
        verdict = "SYMMETRIC_OR_TIED_BUT_SPARSE"
    else:
        verdict = "TOO_SPARSE_TO_INTERPRET"
    return {
        "verdict": verdict,
        "primary_candidate_labels": labels,
        "neutron_dominant_candidate_count": neutron_dominant,
        "proton_dominant_candidate_count": proton_dominant,
        "tied_candidate_count": tied,
        "interpretation": (
            "Primary shell-axis candidates favor magic-N more than magic-Z, but "
            "magic subsets are sparse and the result remains sandbox-only."
            if verdict == "NEUTRON_DOMINANT_BUT_SPARSE"
            else "Magic-axis direction remains too sparse or mixed for promotion."
        ),
        "claim_promotion_allowed": False,
    }


def evaluate_candidates() -> dict[str, Any]:
    """Evaluate all requested candidates on magic-axis and matched subsets."""
    coefficients = full_known.load_frozen_baseline_coefficients()
    rows, training_rows, training_residuals, baseline_bundle = full_known.build_audit_surface(
        coefficients
    )
    subset_index = build_subset_index(rows)
    baseline = _baseline_metrics(rows, subset_index)
    proton_only_beta = float(
        full_known._fit_lstsq(("s_z2",), training_rows, training_residuals)[0]  # noqa: SLF001
    )
    candidate_by_id = {
        str(candidate["candidate_id"]): candidate
        for candidate in full_known.EXECUTED_CANDIDATES
    }
    candidate_items: list[dict[str, Any]] = []
    for candidate_id in AUDIT_CANDIDATE_IDS:
        candidate = candidate_by_id[candidate_id]
        residuals, fitted_coefficients = _candidate_residuals(
            candidate,
            rows=rows,
            training_rows=training_rows,
            training_residuals=training_residuals,
            proton_only_beta=proton_only_beta,
        )
        candidate_metrics = _metrics_for_residuals(residuals, subset_index=subset_index)
        delta = _delta_by_subset(candidate_metrics, baseline)
        focus_delta = {subset_id: delta.get(subset_id) for subset_id in FOCUS_SUBSETS}
        item = {
            "candidate_id": candidate["candidate_id"],
            "source_candidate_id": candidate.get("source_candidate_id"),
            "name": candidate["name"],
            "formula": candidate["formula"],
            "complexity": candidate["complexity"],
            "fit_mode": candidate["fit_mode"],
            "fitted_coefficients": fitted_coefficients,
            "metrics_by_subset": candidate_metrics,
            "delta_mae_by_subset_mev": delta,
            "focus_delta_mae_mev": focus_delta,
            "magic_n_minus_matched_control_delta_mev": _matched_contrast(
                {"focus_delta_mae_mev": focus_delta},
                "magic_n",
                "non_magic_matched_magic_n",
            ),
            "magic_z_minus_matched_control_delta_mev": _matched_contrast(
                {"focus_delta_mae_mev": focus_delta},
                "magic_z",
                "non_magic_matched_magic_z",
            ),
            "worst_subset_regression": _worst_subset_regression(delta),
            "limitations": [
                "Magic-axis subsets are sparse and retrospective.",
                "Candidate coefficients are fit on the 11-row NMD-0002 residual slice.",
                "Output is sandbox-only and does not promote a claim.",
            ],
        }
        item["directional_label"] = _directional_label(item)
        if candidate.get("sign_inverted"):
            item["sign_inverted"] = True
        if candidate.get("baseline_reference_control"):
            item["baseline_reference_control"] = True
        if candidate["fit_mode"] == "lstsq_shuffled":
            item["shuffle_scheme"] = candidate.get("shuffle_scheme", "cyclic-shift-5")
            item["shuffle_seed"] = int(candidate.get("shuffle_seed", SHUFFLE_OFFSET))
        candidate_items.append(item)

    return {
        "coefficients": coefficients,
        "rows": rows,
        "baseline_bundle": baseline_bundle,
        "subset_index": subset_index,
        "subset_summary": _summarize_index(rows, subset_index),
        "baseline_metrics": baseline,
        "candidate_items": candidate_items,
    }


def build_metrics() -> dict[str, Any]:
    """Build deterministic magic-axis asymmetry metrics."""
    evaluated = evaluate_candidates()
    candidate_items = evaluated["candidate_items"]
    overall = _overall_direction(candidate_items)
    coefficients = evaluated["coefficients"]
    baseline_bundle = evaluated["baseline_bundle"]
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "shell_axis_magic_axis_asymmetry_audit",
        "sandbox_only": True,
        "evidence_class": "retrospective_full_known_magic_axis_asymmetry_audit",
        "live_external_fetch_allowed": False,
        "summary": {
            "candidate_count": len(candidate_items),
            "focus_subsets": list(FOCUS_SUBSETS),
            "directional_verdict": overall["verdict"],
            "sparse_warning_threshold": SPARSE_WARNING_THRESHOLD,
            "canonical_results_changed": False,
            "canonical_claims_changed": False,
            "prediction_registry_changed": False,
            "claim_promotion_allowed": False,
        },
        "frozen_baseline": {
            "result_id": "RESULT-0015",
            "model_id": "model_fitted_semi_empirical",
            "coefficients": coefficients.to_dict(),
        },
        "datasets": {
            "training_residual_source": "data/nuclear_masses/nmd-0002-curated-measured-slice.yaml",
            "holdout_source": "data/nuclear_masses/post_ame2020_holdout.yaml",
            **baseline_bundle["metadata"],
        },
        "subset_summary": evaluated["subset_summary"],
        "baseline_metrics_by_subset": evaluated["baseline_metrics"],
        "directional_summary": overall,
        "candidate_items": candidate_items,
        "promotion_boundary": {
            "writes_prediction_registry": False,
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "writes_knowledge": False,
            "required_next_step": (
                "Maintainer review before any registry expansion, reveal scoring, RESULT-* artifact, "
                "claim, or knowledge update."
            ),
        },
        "limitations": [
            "Sandbox-only retrospective audit; no prediction registry, canonical result, claim, or knowledge artifact is updated.",
            "Magic-N, magic-Z, and double-magic subsets are sparse and cannot carry standalone conclusions.",
            "Matched controls are deterministic A-nearest non-magic diagnostics, not causal controls.",
            "All coefficients are fit on the 11-row NMD-0002 residual slice.",
            "The full-known surface is committed repository data; this is not a future-measurement reveal.",
        ],
    }


def _format_delta(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value == 0.0:
        return "+0.000000"
    return f"{'+' if value > 0 else '-'}{abs(value):.6f}"


def _summary_table(items: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Candidate | Magic-N ΔMAE | Magic-Z ΔMAE | Near-magic ΔMAE | Double-magic ΔMAE | Matched-N ΔMAE | Matched-Z ΔMAE | Label |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in items:
        deltas = item["focus_delta_mae_mev"]
        lines.append(
            "| `{cid}` | {mn} | {mz} | {near} | {double} | {match_n} | {match_z} | `{label}` |".format(
                cid=item["candidate_id"],
                mn=_format_delta(deltas.get("magic_n")),
                mz=_format_delta(deltas.get("magic_z")),
                near=_format_delta(deltas.get("near_magic")),
                double=_format_delta(deltas.get("double_magic")),
                match_n=_format_delta(deltas.get("non_magic_matched_magic_n")),
                match_z=_format_delta(deltas.get("non_magic_matched_magic_z")),
                label=item["directional_label"],
            )
        )
    return lines


def _subset_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| Subset | Rows | Sparse warning |",
        "| --- | ---: | --- |",
    ]
    for subset_id in FOCUS_SUBSETS:
        summary = metrics["subset_summary"][subset_id]
        lines.append(
            f"| `{subset_id}` | {summary['row_count']} | "
            f"{'yes' if summary['sparse_warning'] else 'no'} |"
        )
    return lines


def render_report(metrics: dict[str, Any]) -> str:
    """Render the agent-run report."""
    lines = [
        "# Nuclear Shell-Axis Magic-Axis Asymmetry Audit",
        "",
        f"**Agent run:** `{metrics['agent_run_id']}`  ",
        f"**Task:** `{metrics['task_id']}`  ",
        "**Evidence class:** retrospective full-known magic-axis asymmetry audit  ",
        "**Baseline:** `RESULT-0015::model_fitted_semi_empirical`  ",
        "**Script:** `scripts/run_nuclear_shell_axis_magic_asymmetry_audit.py`  ",
        f"**Metrics:** `agent_runs/{metrics['agent_run_id']}/metrics.json`",
        "",
        "## Scope",
        "",
        "This sandbox audit separates magic-N, magic-Z, near-magic, double-magic, "
        "and deterministic non-magic A-matched control behavior for the committed "
        "TASK-0310 candidate family. It does not score future measurements or "
        "promote claims.",
        "",
        "## Subset Counts",
        "",
        *_subset_table(metrics),
        "",
        "Subsets with fewer than 10 rows are explicit sparse diagnostics.",
        "",
        "## Directional Verdict",
        "",
        f"`{metrics['directional_summary']['verdict']}`",
        "",
        metrics["directional_summary"]["interpretation"],
        "",
        "## Candidate Outcomes",
        "",
        *_summary_table(metrics["candidate_items"]),
        "",
        "Negative deltas mean lower retrospective MAE than the frozen baseline. "
        "Positive deltas are regressions.",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in metrics["limitations"])
    lines.extend(
        [
            "",
            "## Promotion Boundary",
            "",
            "- Prediction registry files are not edited.",
            "- Canonical `RESULT-*` files are not edited.",
            "- Claims and knowledge files are not edited.",
            "- No future measurement reveal is scored.",
            "",
        ]
    )
    return "\n".join(lines)


def write_agent_run_support_files(metrics: dict[str, Any], run_dir: Path) -> None:
    """Write manifest and companion review files for AGENT-RUN-0021."""
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "task_id": TASK_ID,
        "status": "SANDBOX_COMPLETE",
        "sandbox_only": True,
        "created_by": {"contributor_id": "roman", "agent_id": "codex"},
        "proposal_paths": {
            "hypothesis": (
                "hypothesis_proposals/nuclear-mass/"
                "HYP-PROPOSAL-0044-shell-axis-stress-scout-batch.yaml"
            ),
            "experiment": (
                "experiment_proposals/nuclear-mass/"
                "EXP-PROPOSAL-0010-nuclear-shell-axis-stress-scout.yaml"
            ),
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
                    "name": "task_scope",
                    "status": "PASS",
                    "notes": "TASK-0321 requests magic-axis asymmetry diagnostics, not reveal scoring.",
                },
                {
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": "Only committed repository datasets are used; no live external fetch is performed.",
                },
                {
                    "name": "control_boundary",
                    "status": "PASS",
                    "notes": "Sign-inverted, shuffled-feature, baseline, and non-magic matched controls are preserved.",
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": "No prediction registry, canonical result, claim, or knowledge file is written.",
                },
            ],
        },
        "limitations": metrics["limitations"],
        "verdict": "INCONCLUSIVE",
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": metrics["promotion_boundary"]["required_next_step"],
        },
    }
    (run_dir / "agent_run.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False),
        encoding="utf-8",
    )
    preflight = [
        "# AGENT-RUN-0021 Preflight",
        "",
        "**Task:** TASK-0321  ",
        "**Lane:** nuclear shell-axis magic-axis asymmetry audit  ",
        "**Mode:** sandbox-only retrospective audit",
        "",
        "## Inputs Checked",
        "",
        "- `TASK-0321`",
        "- `scripts/run_nuclear_shell_axis_full_known_audit.py`",
        "- `agent_runs/AGENT-RUN-0018/metrics.json`",
        "- `docs/reviews/nuclear-shell-axis-validity-domain-after-0310.md`",
        "- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`",
        "- `data/nuclear_masses/post_ame2020_holdout.yaml`",
        "",
        "## Guardrails",
        "",
        "- Live external fetch: not allowed and not used.",
        "- Prediction registry writes: not allowed and not used.",
        "- Canonical results, claims, and knowledge promotion: not allowed and not used.",
        "- PRED-0063 through PRED-0068 are not reveal-scored.",
        "",
        "## Plan",
        "",
        "1. Reuse the TASK-0310 committed full-known audit surface.",
        "2. Evaluate proton-axis, neutron-axis, product, sign-inverted, shuffled, and baseline candidates.",
        "3. Build deterministic non-magic A-matched controls for magic-N, magic-Z, near-magic, and double-magic subsets.",
        "4. Report row counts, sparse warnings, subset deltas, and directional labels.",
        "5. Keep outputs sandbox-only.",
        "",
    ]
    (run_dir / "preflight.md").write_text("\n".join(preflight), encoding="utf-8")
    limitations = ["# AGENT-RUN-0021 Limitations", ""]
    limitations.extend(f"- {item}" for item in metrics["limitations"])
    limitations.append("")
    (run_dir / "limitations.md").write_text("\n".join(limitations), encoding="utf-8")
    review = [
        "# AGENT-RUN-0021 Review Summary",
        "",
        f"`{metrics['directional_summary']['verdict']}` for the magic-axis asymmetry audit.",
        "",
        metrics["directional_summary"]["interpretation"],
        "",
        "The result is subset-limited and retrospective. No prediction registry, "
        "canonical result, claim, or knowledge artifact is promoted.",
        "",
    ]
    (run_dir / "review_summary.md").write_text("\n".join(review), encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    """Write deterministic metrics, report, and companion agent-run files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "metrics.json",
        help="Path for the metrics JSON artifact.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "report.md",
        help="Path for the markdown report artifact.",
    )
    parser.add_argument(
        "--support-files",
        action="store_true",
        help="Write agent_run.yaml, preflight.md, limitations.md, and review_summary.md.",
    )
    args = parser.parse_args(argv)

    metrics = build_metrics()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(metrics, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")

    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(render_report(metrics), encoding="utf-8")
        print(f"wrote {args.report}")

    if args.support_files:
        write_agent_run_support_files(metrics, args.out.parent)
        print(f"wrote support files in {args.out.parent}")


if __name__ == "__main__":
    main()
