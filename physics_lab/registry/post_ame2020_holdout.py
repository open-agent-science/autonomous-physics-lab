"""Post-AME2020 nuclear-mass time-split benchmark guard helpers."""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np
import yaml

from physics_lab.engines.nuclear_mass_baselines import (
    MAGIC_NUMBERS,
    SemiEmpiricalCoefficients,
    semi_empirical_binding_energy,
)
from physics_lab.engines.nuclear_masses import NuclearMassEntry, load_nuclear_mass_dataset
from physics_lab.registry.validation import validate_document


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


HYP_0020_FROZEN_SPEC = CandidateSpec(
    candidate_id="HYP-PROPOSAL-0020",
    family="shell_dual_heavy_anchor",
    formula="r_corr = c1*m2 + c2*mh",
    parameter_count=2,
    source_agent_run_id="AGENT-RUN-0005",
)

HYP_0021_FROZEN_SPEC = CandidateSpec(
    candidate_id="HYP-PROPOSAL-0021",
    family="shell_dual_heavy_anchor_odd_a",
    formula="r_corr = c1*m2 + c2*mh + c3*oa",
    parameter_count=3,
    source_agent_run_id="AGENT-RUN-0005",
)

HYP_0022_FROZEN_SPEC = CandidateSpec(
    candidate_id="HYP-PROPOSAL-0022",
    family="quadratic_asymmetry_refinement",
    formula="r_corr = a*I + b*I^2",
    parameter_count=2,
    source_agent_run_id="AGENT-RUN-0005",
)

POST_AME2020_CANDIDATE_SPECS = (
    HYP_0020_FROZEN_SPEC,
    HYP_0021_FROZEN_SPEC,
    HYP_0022_FROZEN_SPEC,
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


def load_post_ame2020_holdout_dataset(path: str | Path) -> dict[str, Any]:
    """Load and schema-validate the reviewed row-level post-AME2020 holdout."""
    dataset_path = Path(path)
    with dataset_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping in post-AME2020 holdout dataset: {dataset_path}")
    validate_document(payload, kind="post_ame2020_holdout", source=dataset_path)
    return payload


def _default_dataset_path_for_manifest(manifest_path: Path) -> Path:
    if manifest_path.is_absolute():
        return manifest_path.parent.parent.parent / POST_AME2020_HOLDOUT_TARGET
    return Path(POST_AME2020_HOLDOUT_TARGET)


def assess_post_ame2020_activation(
    manifest_path: str | Path,
    *,
    row_level_dataset_path: str | Path | None = None,
) -> dict[str, object]:
    """Return whether the post-AME2020 benchmark may run active metrics."""
    resolved_manifest_path = Path(manifest_path)
    manifest = load_post_ame2020_source_manifest(resolved_manifest_path)
    activation = manifest.get("activation_status", {})
    if not isinstance(activation, dict):
        raise ValueError("post-AME2020 manifest must include activation_status mapping")

    row_values_committed = bool(activation.get("row_level_holdout_dataset_committed"))
    manifest_active = bool(activation.get("time_split_holdout_active"))
    dataset_path = (
        Path(row_level_dataset_path)
        if row_level_dataset_path is not None
        else _default_dataset_path_for_manifest(resolved_manifest_path)
    )
    dataset_exists = dataset_path.exists()
    active = row_values_committed and manifest_active and dataset_exists

    if active:
        status = "ACTIVE"
        reason = "Reviewed row-level post-AME2020 holdout data are present."
    elif row_values_committed and dataset_exists:
        status = "ROW_LEVEL_HOLDOUT_READY_METRICS_BLOCKED"
        reason = (
            "Reviewed row-level post-AME2020 holdout data are committed, but "
            "active time-split metrics remain blocked until a benchmark task runs."
        )
    elif row_values_committed:
        status = "ROW_LEVEL_MANIFEST_WITH_MISSING_DATASET"
        reason = "The source manifest expects a row-level holdout dataset, but the file is missing."
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


def build_post_ame2020_time_split_benchmark(
    *,
    holdout_dataset_path: str | Path,
    source_manifest_path: str | Path,
    result_path: str | Path,
    training_dataset_path: str | Path,
    split_replay_metrics_path: str | Path,
    guard_metrics_path: str | Path,
) -> dict[str, Any]:
    """Evaluate frozen nuclear residual families on the row-level holdout.

    Candidate formulas stay frozen; only their linear coefficients are fitted
    on the pre-existing NMD-0002 training surface. Post-AME2020 rows are used
    only for evaluation.
    """
    activation = assess_post_ame2020_activation(
        source_manifest_path,
        row_level_dataset_path=holdout_dataset_path,
    )
    if activation["status"] != "ACTIVE":
        raise ValueError(
            "post-AME2020 time-split benchmark requires active row-level data; "
            f"got {activation['status']}"
        )

    holdout_payload = load_post_ame2020_holdout_dataset(holdout_dataset_path)
    primary_rows = [
        row
        for row in holdout_payload["entries"]
        if bool(row["included_in_time_split_holdout"])
    ]
    if not primary_rows:
        raise ValueError("post-AME2020 holdout has no primary evaluation rows")

    with Path(result_path).open("r", encoding="utf-8") as handle:
        result_payload = yaml.safe_load(handle)
    if not isinstance(result_payload, dict):
        raise ValueError(f"Expected mapping in RESULT-0015 file: {result_path}")
    coefficients = _fitted_result_coefficients(result_payload)

    training_dataset = load_nuclear_mass_dataset(training_dataset_path)
    training_rows = list(training_dataset.entries)
    baseline_predictions = [
        _baseline_prediction_for_holdout_row(row, coefficients) for row in primary_rows
    ]
    observed = [float(row["new_measurement"]["value_mev"]) for row in primary_rows]
    uncertainties = [float(row["new_measurement"]["uncertainty_mev"]) for row in primary_rows]

    baseline_evaluation = _build_model_evaluation(
        model_id="RESULT-0015::model_fitted_semi_empirical",
        label="Frozen RESULT-0015 fitted semi-empirical baseline",
        kind="frozen_baseline",
        holdout_rows=primary_rows,
        observed_mev=observed,
        predicted_mev=baseline_predictions,
        uncertainties_mev=uncertainties,
        baseline_abs_errors=None,
        coefficients=coefficients.to_dict(),
        formula="Fitted semi-empirical mass formula from RESULT-0015",
    )
    baseline_abs_errors = _absolute_errors(observed, baseline_predictions)

    candidate_evaluations: dict[str, Any] = {}
    for spec in POST_AME2020_CANDIDATE_SPECS:
        assert_candidate_spec_unchanged(spec, frozen=spec)
        correction_coefficients = _fit_candidate_coefficients(
            spec=spec,
            training_rows=training_rows,
            baseline_coefficients=coefficients,
        )
        predicted = [
            baseline_prediction + _candidate_correction(spec, row, correction_coefficients)
            for row, baseline_prediction in zip(primary_rows, baseline_predictions)
        ]
        evaluation = _build_model_evaluation(
            model_id=spec.candidate_id,
            label=f"{spec.candidate_id} {spec.family}",
            kind="frozen_candidate_family",
            holdout_rows=primary_rows,
            observed_mev=observed,
            predicted_mev=predicted,
            uncertainties_mev=uncertainties,
            baseline_abs_errors=baseline_abs_errors,
            coefficients=correction_coefficients,
            formula=spec.formula,
        )
        evaluation["frozen_spec"] = spec.to_dict()
        evaluation["feature_activation_counts"] = _feature_activation_counts(spec, primary_rows)
        evaluation["delta_vs_frozen_baseline"] = _subset_deltas(
            evaluation["metrics_by_subset"],
            baseline_evaluation["metrics_by_subset"],
        )
        candidate_evaluations[spec.candidate_id] = evaluation

    ame2020_predictions = [
        float(row["ame2020_comparison"]["value_mev"]) for row in primary_rows
    ]
    ame2020_sanity = _build_model_evaluation(
        model_id="AME2020-comparison-table",
        label="AME2020 comparison values from the source table",
        kind="external_reference_sanity_check",
        holdout_rows=primary_rows,
        observed_mev=observed,
        predicted_mev=ame2020_predictions,
        uncertainties_mev=uncertainties,
        baseline_abs_errors=baseline_abs_errors,
        coefficients={},
        formula="Source table AME2020 comparison column; not an APL candidate",
    )
    ame2020_sanity["delta_vs_frozen_baseline"] = _subset_deltas(
        ame2020_sanity["metrics_by_subset"],
        baseline_evaluation["metrics_by_subset"],
    )

    with Path(split_replay_metrics_path).open("r", encoding="utf-8") as handle:
        split_replay = json.load(handle)
    with Path(guard_metrics_path).open("r", encoding="utf-8") as handle:
        guard_metrics = json.load(handle)

    best_candidate_id = min(
        candidate_evaluations,
        key=lambda candidate_id: candidate_evaluations[candidate_id]["metrics_by_subset"][
            "primary"
        ]["mae_mev"],
    )
    hyp21_delta = candidate_evaluations["HYP-PROPOSAL-0021"]["delta_vs_frozen_baseline"][
        "primary"
    ]["delta_mae_mev"]
    hyp22_delta = candidate_evaluations["HYP-PROPOSAL-0022"]["delta_vs_frozen_baseline"][
        "primary"
    ]["delta_mae_mev"]

    return {
        "agent_run_id": "AGENT-RUN-0008",
        "task_id": "TASK-0197",
        "campaign_profile_id": "nuclear-mass-surface",
        "benchmark_status": "ACTIVE_RETROSPECTIVE_TIME_SPLIT",
        "evidence_class": "retrospective_time_split_validation_not_blind_prediction",
        "sandbox_only": True,
        "canonical_results_changed": False,
        "canonical_claims_changed": False,
        "claim_promotion_allowed": False,
        "input_references": {
            "holdout_dataset": str(holdout_dataset_path),
            "source_manifest": str(source_manifest_path),
            "frozen_result": str(result_path),
            "training_dataset": str(training_dataset_path),
            "split_replay_context": str(split_replay_metrics_path),
            "guard_context": str(guard_metrics_path),
        },
        "activation": activation,
        "dataset_summary": {
            "dataset_id": holdout_payload["dataset_id"],
            "published_row_count": holdout_payload["row_scope"]["published_row_count"],
            "primary_holdout_row_count": len(primary_rows),
            "excluded_row_count": holdout_payload["row_scope"]["excluded_row_count"],
            "ame2020_extrapolated_comparison_count": sum(
                1 for row in primary_rows if row["ame2020_comparison"]["was_extrapolated"]
            ),
            "new_measurement_publication_years": holdout_payload["row_scope"][
                "new_measurement_publication_years"
            ],
            "excluded_rows": [
                {
                    "nuclide_id": row["nuclide_id"],
                    "reason": row["exclusion_reason"],
                }
                for row in holdout_payload["entries"]
                if not row["included_in_time_split_holdout"]
            ],
        },
        "training_policy": {
            "policy": "fit_candidate_coefficients_on_frozen_NMD-0002_only",
            "training_dataset_id": training_dataset.dataset_id,
            "training_row_count": len(training_rows),
            "post_ame2020_rows_used_for_fitting": 0,
            "baseline_result_id": result_payload["result_id"],
            "baseline_model_id": result_payload["best_model_id"],
            "baseline_coefficients": coefficients.to_dict(),
        },
        "evaluations": {
            "frozen_baseline": baseline_evaluation,
            "candidate_families": candidate_evaluations,
            "ame2020_comparison_sanity": ame2020_sanity,
        },
        "summary": {
            "primary_holdout_count": len(primary_rows),
            "evaluated_candidate_count": len(candidate_evaluations),
            "best_candidate_by_primary_mae": best_candidate_id,
            "candidate_primary_mae_improved_count": sum(
                1
                for evaluation in candidate_evaluations.values()
                if evaluation["delta_vs_frozen_baseline"]["primary"]["delta_mae_mev"] < 0.0
            ),
            "hyp_0021_primary_delta_mae_mev": hyp21_delta,
            "hyp_0021_primary_classification": (
                "regressed" if hyp21_delta > 0.0 else "improved_or_tied"
            ),
            "hyp_0022_negative_control_primary_delta_mae_mev": hyp22_delta,
            "hyp_0022_negative_control_note": (
                "The prior overfit/negative-control family improves this retrospective "
                "surface overall, so it remains review-needed evidence rather than a claim."
            ),
            "no_claim_promotion": True,
            "retrospective_not_blind_prediction": True,
            "verdict": "INCONCLUSIVE",
        },
        "split_replay_context": {
            "source_agent_run_id": split_replay["agent_run_id"],
            "classification": split_replay["stability_assessment"]["classification"],
            "same_shape_summary": split_replay["same_shape_stratified_summary"],
        },
        "guard_context": {
            "source_agent_run_id": guard_metrics.get("agent_run_id", "AGENT-RUN-0007"),
            "prior_benchmark_status": guard_metrics["benchmark_status"],
            "prior_time_split_metrics_active": guard_metrics["time_split_metrics_active"],
            "candidate_evaluations_performed": guard_metrics["candidate_evaluations_performed"],
        },
        "limitations": [
            "This is retrospective post-AME2020 validation, not strict blind prediction.",
            "Candidate formulas were selected before this row-level holdout task but after internal sandbox evidence existed.",
            "Candidate coefficients are fitted only on the small frozen NMD-0002 training surface.",
            "The AME2020 comparison column is a sanity reference, not an APL model or candidate.",
            "No canonical RESULT, claim, knowledge, or hypothesis artifact is promoted by this run.",
        ],
    }


def _fitted_result_coefficients(result_payload: Mapping[str, Any]) -> SemiEmpiricalCoefficients:
    for score in result_payload.get("scores", []):
        if score.get("model_id") == "model_fitted_semi_empirical":
            coefficients = score["coefficients"]
            return SemiEmpiricalCoefficients(
                volume=float(coefficients["volume"]),
                surface=float(coefficients["surface"]),
                coulomb=float(coefficients["coulomb"]),
                asymmetry=float(coefficients["asymmetry"]),
                pairing=float(coefficients["pairing"]),
            )
    raise ValueError("RESULT-0015 does not contain model_fitted_semi_empirical coefficients")


def _baseline_prediction_for_holdout_row(
    row: Mapping[str, Any],
    coefficients: SemiEmpiricalCoefficients,
) -> float:
    return semi_empirical_binding_energy(
        z=int(row["Z"]),
        n=int(row["N"]),
        coefficients=coefficients,
    )


def _baseline_prediction_for_training_entry(
    entry: NuclearMassEntry,
    coefficients: SemiEmpiricalCoefficients,
) -> float:
    return semi_empirical_binding_energy(
        z=entry.Z,
        n=entry.N,
        coefficients=coefficients,
    )


def _fit_candidate_coefficients(
    *,
    spec: CandidateSpec,
    training_rows: Iterable[NuclearMassEntry],
    baseline_coefficients: SemiEmpiricalCoefficients,
) -> dict[str, float]:
    rows = list(training_rows)
    design = np.asarray([_candidate_feature_values(spec, row) for row in rows], dtype=float)
    targets = np.asarray(
        [
            row.binding_energy_mev
            - _baseline_prediction_for_training_entry(row, baseline_coefficients)
            for row in rows
        ],
        dtype=float,
    )
    solution, *_ = np.linalg.lstsq(design, targets, rcond=None)
    return {
        name: float(value)
        for name, value in zip(_candidate_feature_names(spec), solution)
    }


def _candidate_correction(
    spec: CandidateSpec,
    row: Mapping[str, Any],
    coefficients: Mapping[str, float],
) -> float:
    names = _candidate_feature_names(spec)
    values = _candidate_feature_values(spec, row)
    return float(sum(float(coefficients[name]) * value for name, value in zip(names, values)))


def _candidate_feature_names(spec: CandidateSpec) -> tuple[str, ...]:
    if spec.candidate_id == "HYP-PROPOSAL-0020":
        return ("magic_both", "heavy_double_magic")
    if spec.candidate_id == "HYP-PROPOSAL-0021":
        return ("magic_both", "heavy_double_magic", "odd_a")
    if spec.candidate_id == "HYP-PROPOSAL-0022":
        return ("isospin_asymmetry", "isospin_asymmetry_sq")
    raise ValueError(f"Unsupported post-AME2020 candidate: {spec.candidate_id}")


def _candidate_feature_values(
    spec: CandidateSpec,
    row: NuclearMassEntry | Mapping[str, Any],
) -> tuple[float, ...]:
    z = int(row.Z if isinstance(row, NuclearMassEntry) else row["Z"])
    n = int(row.N if isinstance(row, NuclearMassEntry) else row["N"])
    a = int(row.A if isinstance(row, NuclearMassEntry) else row["A"])
    magic_both = 1.0 if z in MAGIC_NUMBERS and n in MAGIC_NUMBERS else 0.0
    heavy_double_magic = 1.0 if magic_both and a >= 100 else 0.0
    odd_a = 1.0 if a % 2 == 1 else 0.0
    isospin_asymmetry = float(n - z) / float(a)

    if spec.candidate_id == "HYP-PROPOSAL-0020":
        return (magic_both, heavy_double_magic)
    if spec.candidate_id == "HYP-PROPOSAL-0021":
        return (magic_both, heavy_double_magic, odd_a)
    if spec.candidate_id == "HYP-PROPOSAL-0022":
        return (isospin_asymmetry, isospin_asymmetry * isospin_asymmetry)
    raise ValueError(f"Unsupported post-AME2020 candidate: {spec.candidate_id}")


def _feature_activation_counts(
    spec: CandidateSpec,
    rows: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    names = _candidate_feature_names(spec)
    counts = {name: 0 for name in names}
    for row in rows:
        for name, value in zip(names, _candidate_feature_values(spec, row)):
            if value != 0.0:
                counts[name] += 1
    return counts


def _build_model_evaluation(
    *,
    model_id: str,
    label: str,
    kind: str,
    holdout_rows: list[Mapping[str, Any]],
    observed_mev: list[float],
    predicted_mev: list[float],
    uncertainties_mev: list[float],
    baseline_abs_errors: list[float] | None,
    coefficients: Mapping[str, float],
    formula: str,
) -> dict[str, Any]:
    row_errors = []
    for row, observed, predicted, uncertainty in zip(
        holdout_rows,
        observed_mev,
        predicted_mev,
        uncertainties_mev,
    ):
        residual = observed - predicted
        abs_error = abs(residual)
        row_errors.append(
            {
                "row_id": row["row_id"],
                "nuclide_id": row["nuclide_id"],
                "Z": row["Z"],
                "N": row["N"],
                "A": row["A"],
                "observed_mev": observed,
                "predicted_mev": predicted,
                "residual_mev": residual,
                "abs_error_mev": abs_error,
                "uncertainty_mev": uncertainty,
                "abs_uncertainty_normalized_error": (
                    None if uncertainty <= 0.0 else abs_error / uncertainty
                ),
                "ame2020_comparison_was_extrapolated": row["ame2020_comparison"][
                    "was_extrapolated"
                ],
            }
        )

    evaluation: dict[str, Any] = {
        "model_id": model_id,
        "label": label,
        "kind": kind,
        "formula": formula,
        "coefficients": {key: float(value) for key, value in coefficients.items()},
        "metrics_by_subset": {},
        "worst_abs_error_cases": sorted(
            row_errors,
            key=lambda item: float(item["abs_error_mev"]),
            reverse=True,
        )[:10],
    }

    for subset_id, subset_rows in _subset_rows(holdout_rows, row_errors).items():
        evaluation["metrics_by_subset"][subset_id] = _metrics_for_error_rows(subset_rows)

    if baseline_abs_errors is not None:
        regression_rows = []
        for row_error, baseline_abs_error in zip(row_errors, baseline_abs_errors):
            delta = float(row_error["abs_error_mev"]) - baseline_abs_error
            regression_row = dict(row_error)
            regression_row["baseline_abs_error_mev"] = baseline_abs_error
            regression_row["delta_abs_error_vs_baseline_mev"] = delta
            regression_rows.append(regression_row)
        evaluation["worst_regression_cases_vs_baseline"] = sorted(
            regression_rows,
            key=lambda item: float(item["delta_abs_error_vs_baseline_mev"]),
            reverse=True,
        )[:10]

    return evaluation


def _subset_rows(
    holdout_rows: list[Mapping[str, Any]],
    error_rows: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    subsets: dict[str, list[dict[str, Any]]] = {
        "primary": [],
        "ame2020_extrapolated_comparison": [],
        "ame2020_measured_comparison": [],
        "magic_any": [],
        "double_magic": [],
        "near_magic": [],
        "neutron_rich_delta_ge_20": [],
        "proton_rich_n_lt_z": [],
        "heavy_a_ge_100": [],
        "odd_a": [],
    }
    for row, error_row in zip(holdout_rows, error_rows):
        z = int(row["Z"])
        n = int(row["N"])
        a = int(row["A"])
        subsets["primary"].append(error_row)
        if bool(row["ame2020_comparison"]["was_extrapolated"]):
            subsets["ame2020_extrapolated_comparison"].append(error_row)
        else:
            subsets["ame2020_measured_comparison"].append(error_row)
        if z in MAGIC_NUMBERS or n in MAGIC_NUMBERS:
            subsets["magic_any"].append(error_row)
        if z in MAGIC_NUMBERS and n in MAGIC_NUMBERS:
            subsets["double_magic"].append(error_row)
        if _nearest_magic_distance(z) <= 2 or _nearest_magic_distance(n) <= 2:
            subsets["near_magic"].append(error_row)
        if n - z >= 20:
            subsets["neutron_rich_delta_ge_20"].append(error_row)
        if n < z:
            subsets["proton_rich_n_lt_z"].append(error_row)
        if a >= 100:
            subsets["heavy_a_ge_100"].append(error_row)
        if a % 2 == 1:
            subsets["odd_a"].append(error_row)
    return subsets


def _metrics_for_error_rows(rows: list[Mapping[str, Any]]) -> dict[str, float | int | None]:
    if not rows:
        return {
            "count": 0,
            "mae_mev": None,
            "rmse_mev": None,
            "max_abs_error_mev": None,
            "mean_error_mev": None,
            "mean_abs_uncertainty_normalized_error": None,
            "max_abs_uncertainty_normalized_error": None,
        }
    return calculate_time_split_metrics(
        observed_mev=[float(row["observed_mev"]) for row in rows],
        predicted_mev=[float(row["predicted_mev"]) for row in rows],
        uncertainties_mev=[float(row["uncertainty_mev"]) for row in rows],
    )


def _subset_deltas(
    metrics: Mapping[str, Mapping[str, Any]],
    baseline_metrics: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, float | bool | None]]:
    deltas: dict[str, dict[str, float | bool | None]] = {}
    for subset_id, subset_metrics in metrics.items():
        baseline_subset = baseline_metrics[subset_id]
        candidate_mae = subset_metrics["mae_mev"]
        baseline_mae = baseline_subset["mae_mev"]
        candidate_rmse = subset_metrics["rmse_mev"]
        baseline_rmse = baseline_subset["rmse_mev"]
        delta_mae = (
            None
            if candidate_mae is None or baseline_mae is None
            else float(candidate_mae) - float(baseline_mae)
        )
        delta_rmse = (
            None
            if candidate_rmse is None or baseline_rmse is None
            else float(candidate_rmse) - float(baseline_rmse)
        )
        deltas[subset_id] = {
            "delta_mae_mev": delta_mae,
            "delta_rmse_mev": delta_rmse,
            "improvement_mae_mev": None if delta_mae is None else -delta_mae,
            "improved_mae": None if delta_mae is None else delta_mae < 0.0,
        }
    return deltas


def _absolute_errors(observed: Iterable[float], predicted: Iterable[float]) -> list[float]:
    return [abs(float(obs) - float(pred)) for obs, pred in zip(observed, predicted)]


def _nearest_magic_distance(value: int) -> int:
    return min(abs(value - magic) for magic in MAGIC_NUMBERS)
