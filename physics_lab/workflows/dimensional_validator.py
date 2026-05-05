"""Dimensional-analysis validator workflow.

Runs ``physics_lab.engines.dimensions.validate_challenge_set`` over the
curated challenge set declared in the experiment file and writes a full
canonical result artifact directory (result.yaml, metrics.json, report.md,
claim_update.md, knowledge_update.md, review artefacts).

No training/test split, no curve fitting. The metric is agreement_fraction
(fraction of items whose computed verdict matches the curated label).

Verdict:
- VALID if agreement_fraction >= experiment.comparison_targets[0].reference_value
- INCONCLUSIVE otherwise
"""

from __future__ import annotations

import json
import math
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from physics_lab import __version__
from physics_lab.engines.dimensions import validate_challenge_set
from physics_lab.registry.examples import load_example_config
from physics_lab.registry.experiments import load_experiment
from physics_lab.registry.hypotheses import load_hypothesis
from physics_lab.registry.results import validate_result_payload
from physics_lab.workflows.artifacts import (
    ExperimentArtifacts,
    ExperimentOutcome,
    find_repo_root,
    git_commit,
    relative_or_absolute,
    render_patch_artifact,
    render_review_metadata,
    render_review_summary,
    resolve_path,
    snapshot_input_files,
    task_path,
    write_text_atomic,
)


def run_dimensional_validator_with_output(
    config_path: str | Path,
    output_dir: str | Path | None = None,
) -> ExperimentOutcome:
    """Execute the dimensional-analysis validator benchmark."""
    config_path = Path(config_path).resolve()
    repo_root = find_repo_root(config_path)
    config = load_example_config(config_path)

    run_id = config["run_id"]
    result_id = config["result_id"]
    task_id = config["task_id"]

    experiment_path = resolve_path(config_path, config["experiment_path"])
    hypothesis_path = resolve_path(config_path, config["hypothesis_path"])
    experiment = load_experiment(experiment_path)
    hypothesis = load_hypothesis(hypothesis_path)

    experiment_id = experiment["id"]
    hypothesis_id = hypothesis["id"]

    # Locate the challenge set (dataset_path per experiment schema)
    challenge_set_relative = experiment["data"]["dataset_path"]
    challenge_set_path = resolve_path(experiment_path, challenge_set_relative)
    # Agreement threshold encoded in comparison_targets[0].reference_value
    targets = experiment.get("comparison_targets") or []
    agreement_threshold: float = float(targets[0]["reference_value"]) if targets else 0.90

    # Determine output directory
    result_root = Path(
        resolve_path(config_path, config["result_root"])
    )
    if output_dir is not None:
        run_dir = Path(output_dir).resolve()
    else:
        run_dir = result_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # Snapshot inputs
    # result schema only allows the four canonical input keys
    input_hashes = snapshot_input_files(
        run_dir=run_dir,
        repo_root=repo_root,
        input_files={
            "config": config_path,
            "experiment": experiment_path,
            "hypothesis": hypothesis_path,
            "task": task_path(repo_root, task_id),
        },
    )
    # Snapshot the challenge set separately (not in result.input_file_hashes)
    challenge_snapshot_dir = run_dir / "inputs"
    challenge_snapshot_dir.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy2(challenge_set_path, challenge_snapshot_dir / "challenge_set.yaml")

    # Run validator
    item_results, summary = validate_challenge_set(challenge_set_path)

    # Determine verdict
    agreement = summary.agreement_fraction
    best_verdict = "VALID" if agreement >= agreement_threshold else "INCONCLUSIVE"

    # Build verification checks
    checks = [
        {
            "name": "challenge_set_loaded",
            "status": "PASS",
            "details": f"Loaded {summary.total} items from the curated challenge set.",
            "metrics": {"item_count": summary.total},
        },
        {
            "name": "no_inconclusive_items",
            "status": "PASS" if summary.inconclusive_count == 0 else "WARN",
            "details": (
                "All items produced a definite verdict."
                if summary.inconclusive_count == 0
                else f"{summary.inconclusive_count} items returned INCONCLUSIVE."
            ),
            "metrics": {"inconclusive_count": summary.inconclusive_count},
        },
        {
            "name": "agreement_fraction",
            "status": "PASS" if agreement >= agreement_threshold else "FAIL",
            "details": (
                f"Validator agreed with {summary.agree}/{summary.total} curated labels "
                f"({agreement:.1%}), threshold {agreement_threshold:.0%}."
            ),
            "metrics": {
                "agree": summary.agree,
                "total": summary.total,
                "agreement_fraction": round(agreement, 6),
                "threshold": agreement_threshold,
            },
        },
    ]

    # ---------- metrics.json ----------
    metrics: dict[str, Any] = {
        "run_id": run_id,
        "experiment_id": experiment_id,
        "total_items": summary.total,
        "agree": summary.agree,
        "agreement_fraction": round(agreement, 6),
        "agreement_threshold": agreement_threshold,
        "valid_count": summary.valid_count,
        "invalid_count": summary.invalid_count,
        "suspicious_count": summary.suspicious_count,
        "inconclusive_count": summary.inconclusive_count,
        "best_verdict": best_verdict,
        "item_results": [
            {
                "id": r.item_id,
                "expected": r.expected_verdict,
                "computed": r.computed_verdict,
                "agrees": r.agrees,
                "detail": r.detail,
            }
            for r in item_results
        ],
    }

    metrics_path = run_dir / "metrics.json"
    write_text_atomic(metrics_path, json.dumps(metrics, indent=2))

    # ---------- report.md ----------
    disagree_rows = "\n".join(
        f"| {r.item_id} | {r.expected_verdict} | {r.computed_verdict} | {r.detail[:60]} |"
        for r in item_results
        if not r.agrees
    )
    report_text = textwrap.dedent(f"""\
        # Dimensional Analysis Validator MVP — Run Report

        **Run:** {run_id}  **Experiment:** {experiment_id}  **Verdict:** {best_verdict}

        ## Summary

        | Metric | Value |
        |---|---|
        | Total items | {summary.total} |
        | Agreement | {summary.agree}/{summary.total} ({agreement:.1%}) |
        | VALID computed | {summary.valid_count} |
        | INVALID computed | {summary.invalid_count} |
        | INCONCLUSIVE | {summary.inconclusive_count} |
        | Agreement threshold | {agreement_threshold:.0%} |
        | Best verdict | **{best_verdict}** |

        ## Disagreements

        | ID | Expected | Computed | Detail |
        |---|---|---|---|
        {disagree_rows if disagree_rows else "_None_"}

        ## Limitations

        - MVP scope: dimension-only check. Cannot detect KNOWN_LIMIT_FAIL
          (numerical limit violations) or semantically-empty dimensionless
          formulas (DA-310 class).
        - SUSPICIOUS items with explicit dimensional mismatch are classified
          INVALID; this is stricter but operationally correct (formula is flagged).
        - Unit symbol table is limited to SI base units and common derived units.
          Natural-unit or Gaussian-unit formulas are outside scope.

        ## Claim Ceiling

        The validator achieves {agreement:.1%} agreement on the 50-item
        DA-CHALLENGE-001 set. No claim about unseen formulas or physics
        domains outside the challenge set is made.
    """)
    report_path = run_dir / "report.md"
    write_text_atomic(report_path, report_text)

    _claim_target = "claims/CLAIM-0005-dimensional-analysis-validator.md"
    _know_target = "knowledge/physics_validation/dimensional_analysis_validator.md"
    _claim_target_path = repo_root / _claim_target
    _know_target_path = repo_root / _know_target
    _claim_original = _claim_target_path.read_text(encoding="utf-8") if _claim_target_path.exists() else ""
    _know_original = _know_target_path.read_text(encoding="utf-8") if _know_target_path.exists() else ""

    # ---------- claim_update ----------
    claim_update_text = textwrap.dedent(f"""\
        ## Claim Update

        Evidence source: {result_id}.
        Proposed status: DRAFT (no automatic promotion).

        The validator achieves {agreement:.1%} agreement on DA-CHALLENGE-001.
        CLAIM-0005 is already drafted with this scope restriction. No further
        update needed; maintainer review required before any status change.
    """)
    claim_update_path = run_dir / "claim_update.md"
    write_text_atomic(claim_update_path, claim_update_text)

    claim_update_patch_text = render_patch_artifact(
        title="Claim Patch Suggestion",
        target_file=_claim_target,
        evidence_basis=[result_id],
        original_text=_claim_original,
        proposed_text=_claim_original,
        proposed_status="DRAFT",
        sections_to_update=["Evidence Status"],
        rationale=f"Validator achieves {agreement:.1%} agreement; claim remains DRAFT pending human review.",
    )
    claim_update_patch_path = run_dir / "claim_update.patch.md"
    write_text_atomic(claim_update_patch_path, claim_update_patch_text)

    # ---------- knowledge_update ----------
    knowledge_update_text = textwrap.dedent(f"""\
        ## Knowledge Update

        Evidence source: {result_id}.

        Dimensional validator MVP benchmarked at {agreement:.1%} agreement
        on DA-CHALLENGE-001 (50 items). KNOW-0004 already captures this
        result. No field changes needed; re-verify if challenge set or engine
        is updated.
    """)
    knowledge_update_path = run_dir / "knowledge_update.md"
    write_text_atomic(knowledge_update_path, knowledge_update_text)

    knowledge_update_patch_text = render_patch_artifact(
        title="Knowledge Patch Suggestion",
        target_file=_know_target,
        evidence_basis=[result_id],
        original_text=_know_original,
        proposed_text=_know_original,
        sections_to_update=["MVP Benchmark Result"],
        rationale="Knowledge note already matches the run result; no change required.",
    )
    knowledge_update_patch_path = run_dir / "knowledge_update.patch.md"
    write_text_atomic(knowledge_update_patch_path, knowledge_update_patch_text)

    # ---------- review artefacts ----------
    now_iso = datetime.now(tz=timezone.utc).isoformat()
    review_summary_text = render_review_summary(
        result_id=result_id,
        claim_id="CLAIM-0005",
        knowledge_id="KNOW-0004",
        suggested_status="DRAFT",
        rationale=(
            f"Dimensional validator achieves {agreement:.1%} agreement on "
            "DA-CHALLENGE-001; keep DRAFT until independent review."
        ),
        highlights=[
            f"Agreement: {summary.agree}/{summary.total} ({agreement:.1%})",
            f"VALID: {summary.valid_count}, INVALID: {summary.invalid_count}",
            "One documented scope limit: DA-310-class semantically-empty formulas.",
        ],
        limitations=[
            "MVP scope: dimensional check only; cannot detect KNOWN_LIMIT_FAIL.",
            "Challenge set is internally curated (TASK-0017); no external validation.",
        ],
    )
    review_summary_path = run_dir / "review_summary.md"
    write_text_atomic(review_summary_path, review_summary_text)

    review_metadata_payload = render_review_metadata(
        result_id=result_id,
        run_id=run_id,
        experiment_id=experiment_id,
        claim_id="CLAIM-0005",
        knowledge_id="KNOW-0004",
        generated_at=now_iso,
        proposed_claim_status="DRAFT",
        evidence_basis=[result_id],
        claim_target_file=_claim_target,
        knowledge_target_file=_know_target,
        claim_patch_path=relative_or_absolute(claim_update_patch_path, repo_root),
        knowledge_patch_path=relative_or_absolute(knowledge_update_patch_path, repo_root),
        review_summary_path=relative_or_absolute(review_summary_path, repo_root),
    )
    review_metadata_path = run_dir / "review_metadata.yaml"
    import yaml as _yaml
    write_text_atomic(review_metadata_path, _yaml.safe_dump(review_metadata_payload, sort_keys=False))

    # ---------- result.yaml ----------
    commit = git_commit(repo_root)
    result_payload: dict[str, Any] = {
        "generated_at": now_iso,
        "result_id": result_id,
        "run_id": run_id,
        "experiment_id": experiment_id,
        "title": str(experiment["title"]),
        "hypothesis_id": hypothesis_id,
        "task_id": task_id,
        "engine_version": __version__,
        "git_commit": commit or "unknown",
        "command": f"physics-lab run {config_path.name}",
        "input_file_hashes": input_hashes,
        "code_reference": "physics_lab/workflows/dimensional_validator.py",
        "limitations": [
            "MVP scope: dimensional check only; cannot detect known-limit violations.",
            "SUSPICIOUS items with explicit dimensional mismatch are classified INVALID.",
            "Unit symbol table covers SI base units and common derived units only.",
            "Natural-unit or Gaussian-unit formulas are outside scope.",
        ],
        "best_verdict": best_verdict,
        "comparison_summary": [
            {
                "target_id": "target_agreement",
                "label": "Agreement fraction target",
                "reference_value": agreement_threshold,
                "observed_value": round(agreement, 6),
                "unit": None,
                "absolute_difference": round(abs(agreement - agreement_threshold), 6),
                "relative_difference": round(
                    abs(agreement - agreement_threshold) / agreement_threshold, 6
                ),
                "notes": (
                    f"Validator agreed with {summary.agree}/{summary.total} curated labels; "
                    f"threshold {agreement_threshold:.0%}."
                ),
            }
        ],
        "uncertainty_summary": {
            "method": "binomial standard error sqrt(p(1-p)/n) on agreement fraction",
            "observed_uncertainty": round(
                math.sqrt(agreement * (1.0 - agreement) / summary.total)
                if summary.total > 0
                else 0.0,
                6,
            ),
            "reference_uncertainty": 0.0,
            "combined_uncertainty": round(
                math.sqrt(agreement * (1.0 - agreement) / summary.total)
                if summary.total > 0
                else 0.0,
                6,
            ),
            "z_score": None,
            "within_combined_uncertainty": (
                abs(agreement - agreement_threshold)
                <= math.sqrt(agreement * (1.0 - agreement) / summary.total)
                if summary.total > 0
                else None
            ),
            "notes": (
                "Binomial standard error on the agreement fraction. "
                "Reference uncertainty is 0 because the threshold is a fixed target."
            ),
        },
        "verification": {
            "passed": best_verdict == "VALID",
            "checks": checks,
        },
        "artifacts": {
            "report": relative_or_absolute(report_path, repo_root),
            "metrics": relative_or_absolute(metrics_path, repo_root),
            "claim_update": relative_or_absolute(claim_update_path, repo_root),
            "claim_update_patch": relative_or_absolute(claim_update_patch_path, repo_root),
            "knowledge_update": relative_or_absolute(knowledge_update_path, repo_root),
            "knowledge_update_patch": relative_or_absolute(
                knowledge_update_patch_path, repo_root
            ),
            "review_summary": relative_or_absolute(review_summary_path, repo_root),
            "review_metadata": relative_or_absolute(review_metadata_path, repo_root),
        },
    }

    result_path = run_dir / "result.yaml"
    validate_result_payload(result_payload, source=result_path)
    write_text_atomic(result_path, yaml.dump(result_payload, sort_keys=False, allow_unicode=True))

    artifacts = ExperimentArtifacts(
        result_path=result_path,
        report_path=report_path,
        metrics_path=metrics_path,
        claim_update_path=claim_update_path,
        claim_update_patch_path=claim_update_patch_path,
        knowledge_update_path=knowledge_update_path,
        knowledge_update_patch_path=knowledge_update_patch_path,
        review_summary_path=review_summary_path,
        review_metadata_path=review_metadata_path,
    )

    return ExperimentOutcome(
        title=str(experiment["title"]),
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=hypothesis_id,
        task_id=task_id,
        artifacts=artifacts,
        verdicts={"dimensional_validation": best_verdict},
        summary_lines=(
            f"Agreement: {summary.agree}/{summary.total} ({agreement:.1%})",
            f"Verdict: {best_verdict}",
        ),
    )
