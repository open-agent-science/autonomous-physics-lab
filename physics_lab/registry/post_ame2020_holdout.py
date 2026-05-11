"""Post-AME2020 nuclear-mass time-split benchmark guard helpers."""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml


POST_AME2020_HOLDOUT_TARGET = "data/nuclear_masses/post_ame2020_holdout.yaml"


@dataclass(frozen=True)
class CandidateSpec:
    """Frozen candidate family metadata used to block post-hoc mutation."""

    candidate_id: str
    family: str
    formula: str
    parameter_count: int
    source_agent_run_id: str

    def to_dict(self) -> dict[str, object]:
        return {
            "candidate_id": self.candidate_id,
            "family": self.family,
            "formula": self.formula,
            "parameter_count": self.parameter_count,
            "source_agent_run_id": self.source_agent_run_id,
        }


HYP_0021_FROZEN_SPEC = CandidateSpec(
    candidate_id="HYP-PROPOSAL-0021",
    family="shell_dual_heavy_anchor_odd_a",
    formula="r_corr = c1*m2 + c2*mh + c3*oa",
    parameter_count=3,
    source_agent_run_id="AGENT-RUN-0005",
)


def calculate_time_split_metrics(
    observed_mev: Iterable[float],
    predicted_mev: Iterable[float],
    uncertainties_mev: Iterable[float | None] | None = None,
) -> dict[str, float | int | None]:
    """Compute deterministic error metrics for a future row-level holdout."""
    observed = [float(value) for value in observed_mev]
    predicted = [float(value) for value in predicted_mev]
    if len(observed) != len(predicted):
        raise ValueError("observed_mev and predicted_mev must have the same length")
    if not observed:
        raise ValueError("time-split metric calculation requires at least one row")

    residuals = [obs - pred for obs, pred in zip(observed, predicted)]
    abs_errors = [abs(value) for value in residuals]

    normalized: list[float] = []
    if uncertainties_mev is not None:
        uncertainties = list(uncertainties_mev)
        if len(uncertainties) != len(observed):
            raise ValueError("uncertainties_mev must match observed_mev length")
        normalized = [
            abs(error) / float(sigma)
            for error, sigma in zip(residuals, uncertainties)
            if sigma is not None and float(sigma) > 0.0
        ]

    return {
        "count": len(observed),
        "mae_mev": sum(abs_errors) / len(abs_errors),
        "rmse_mev": math.sqrt(sum(value * value for value in residuals) / len(residuals)),
        "max_abs_error_mev": max(abs_errors),
        "mean_error_mev": sum(residuals) / len(residuals),
        "mean_abs_uncertainty_normalized_error": (
            None if not normalized else sum(normalized) / len(normalized)
        ),
        "max_abs_uncertainty_normalized_error": None if not normalized else max(normalized),
    }


def assert_candidate_spec_unchanged(
    candidate: CandidateSpec | Mapping[str, object],
    *,
    frozen: CandidateSpec = HYP_0021_FROZEN_SPEC,
) -> None:
    """Raise if a candidate family changed after seeing the time-split surface."""
    payload = candidate.to_dict() if isinstance(candidate, CandidateSpec) else dict(candidate)
    expected = frozen.to_dict()
    mismatches = [
        key
        for key, expected_value in expected.items()
        if payload.get(key) != expected_value
    ]
    if mismatches:
        joined = ", ".join(mismatches)
        raise ValueError(f"candidate specification changed after freeze: {joined}")


def load_post_ame2020_source_manifest(path: str | Path) -> dict[str, Any]:
    """Load the reviewed source manifest created by TASK-0187."""
    manifest_path = Path(path)
    with manifest_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping in post-AME2020 manifest: {manifest_path}")
    return payload


def assess_post_ame2020_activation(
    manifest_path: str | Path,
    *,
    row_level_dataset_path: str | Path | None = None,
) -> dict[str, object]:
    """Return whether the post-AME2020 benchmark may run active metrics."""
    manifest = load_post_ame2020_source_manifest(manifest_path)
    activation = manifest.get("activation_status", {})
    if not isinstance(activation, dict):
        raise ValueError("post-AME2020 manifest must include activation_status mapping")

    row_values_committed = bool(activation.get("row_level_holdout_dataset_committed"))
    manifest_active = bool(activation.get("time_split_holdout_active"))
    dataset_path = Path(row_level_dataset_path or POST_AME2020_HOLDOUT_TARGET)
    dataset_exists = dataset_path.exists()
    active = row_values_committed and manifest_active and dataset_exists

    if active:
        status = "ACTIVE"
        reason = "Reviewed row-level post-AME2020 holdout data are present."
    elif dataset_exists:
        status = "DATASET_PRESENT_BUT_MANIFEST_INACTIVE"
        reason = "A row-level file exists, but the source manifest has not activated it."
    else:
        status = "NOT_ACTIVATED_SOURCE_MANIFEST_ONLY"
        reason = (
            "TASK-0187 provides source provenance only; no reviewed row-level "
            "post-AME2020 holdout dataset is committed."
        )

    import_plan = manifest.get("candidate_row_import_plan", {})
    if not isinstance(import_plan, dict):
        import_plan = {}

    return {
        "status": status,
        "active": active,
        "reason": reason,
        "source_manifest_id": manifest.get("manifest_id"),
        "row_level_holdout_dataset_committed": row_values_committed,
        "time_split_holdout_active": manifest_active,
        "row_level_dataset_path": str(dataset_path),
        "row_level_dataset_exists": dataset_exists,
        "required_columns": tuple(import_plan.get("required_columns", ())),
        "required_row_filters": tuple(import_plan.get("required_row_filters", ())),
    }


def build_post_ame2020_dry_run_metrics(
    *,
    manifest_path: str | Path,
    split_replay_metrics_path: str | Path,
) -> dict[str, object]:
    """Build a conservative TASK-0188 dry-run metrics payload."""
    activation = assess_post_ame2020_activation(manifest_path)
    assert_candidate_spec_unchanged(HYP_0021_FROZEN_SPEC)

    with Path(split_replay_metrics_path).open("r", encoding="utf-8") as handle:
        split_replay = json.load(handle)
    split_summary = split_replay["same_shape_stratified_summary"]

    return {
        "task_id": "TASK-0188",
        "benchmark_status": activation["status"],
        "time_split_metrics_active": activation["active"],
        "source_manifest_id": activation["source_manifest_id"],
        "row_level_dataset_path": activation["row_level_dataset_path"],
        "row_level_dataset_exists": activation["row_level_dataset_exists"],
        "candidate_evaluations_performed": False,
        "canonical_results_changed": False,
        "canonical_claims_changed": False,
        "frozen_candidate": HYP_0021_FROZEN_SPEC.to_dict(),
        "metric_fields_when_active": (
            "count",
            "mae_mev",
            "rmse_mev",
            "max_abs_error_mev",
            "mean_abs_uncertainty_normalized_error",
            "max_abs_uncertainty_normalized_error",
        ),
        "split_replay_context": {
            "source_agent_run_id": split_replay["agent_run_id"],
            "classification": split_replay["stability_assessment"]["classification"],
            "improved_count": split_summary["improved_count"],
            "regressed_count": split_summary["regressed_count"],
            "tied_count": split_summary["tied_count"],
            "worst_delta_mae_mev": split_summary["worst_delta_mae_mev"],
        },
        "activation_guard": {
            "result": activation["reason"],
            "required_next_step": (
                "Commit a reviewed row-level post-AME2020 holdout dataset with "
                "source-artifact checksum, unit mapping, measured/extrapolated flags, "
                "and exclusion reasons before active benchmark metrics can run."
            ),
        },
    }
