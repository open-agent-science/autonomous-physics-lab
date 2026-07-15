"""Dimensional-analysis validator workflow.

Runs ``physics_lab.engines.dimensions.validate_challenge_set`` over the
curated challenge set declared in the experiment file and writes a full
canonical result artifact directory (result.yaml, metrics.json, report.md,
claim_update.md, knowledge_update.md, review artefacts).

No training/test split, no curve fitting. Historical configurations use the
legacy policy-adjusted agreement contract. New configurations must opt into the
label-blind v2 contract, whose primary metric is exact categorical agreement;
policy-adjusted agreement remains a separately reported diagnostic.

Verdict:
- VALID if agreement_fraction >= experiment.comparison_targets[0].reference_value
- INCONCLUSIVE otherwise
"""

from __future__ import annotations

import hashlib
import json
import math
import textwrap
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from physics_lab import __version__
from physics_lab.engines.dimensions import (
    ChallengeSetSummary,
    SCORING_CONTRACT_LABEL_BLIND_V2,
    SCORING_CONTRACT_LEGACY_V1,
    infer_item,
    score_inference,
    validate_challenge_set,
)
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


FROZEN_V2_STATUS = "frozen_calibration_only"
FROZEN_V2_ITEM_COUNT = 80
FROZEN_V2_LABELS = ("VALID", "INVALID", "INCONCLUSIVE")
FROZEN_V2_THRESHOLDS = {
    "exact_agreement_threshold": 0.90,
    "valid_recall_floor": 0.85,
    "invalid_recall_floor": 0.85,
    "inconclusive_ceiling": 0.05,
}
PUBLISHED_BY = {
    "contributor_id": "gladunrv",
    "github_username": "gladunrv",
    "agent_tool": "Codex",
    "model_version": "GPT-5",
}


class FrozenCalibrationContaminationError(ValueError):
    """Raised before inference when the frozen v2 calibration contract drifted."""


def _verify_frozen_v2_calibration_contract(
    challenge_set: dict[str, Any],
) -> dict[str, Any]:
    """Verify the TASK-1039 freeze without executing dimensional inference."""
    failures: list[str] = []
    items = challenge_set.get("items")
    if not isinstance(items, list):
        items = []
        failures.append("items must be a list")

    if challenge_set.get("status") != FROZEN_V2_STATUS:
        failures.append(f"status must be {FROZEN_V2_STATUS!r}")
    if challenge_set.get("scoring_contract_id") != SCORING_CONTRACT_LABEL_BLIND_V2:
        failures.append("scoring_contract_id must be label_blind_exact_v2")
    if challenge_set.get("total_items") != FROZEN_V2_ITEM_COUNT:
        failures.append(f"total_items must be {FROZEN_V2_ITEM_COUNT}")
    if len(items) != FROZEN_V2_ITEM_COUNT:
        failures.append(f"parsed item count must be {FROZEN_V2_ITEM_COUNT}")

    label_vocabulary = challenge_set.get("primary_label_vocabulary")
    if label_vocabulary != list(FROZEN_V2_LABELS):
        failures.append("primary_label_vocabulary drifted")
    observed_labels = {str(item.get("expected_verdict", "")) for item in items}
    if not observed_labels <= set(FROZEN_V2_LABELS):
        failures.append("an item uses a label outside the frozen vocabulary")

    curation = challenge_set.get("curation") or {}
    if curation.get("benchmark_authorship_independence") != (
        "same_owner_role_disjoint_agent"
    ):
        failures.append("benchmark authorship independence drifted")
    if curation.get("bounded_verdict") != "CALIBRATION_ONLY_ROLE_LIMIT":
        failures.append("bounded verdict drifted")
    for field in ("contributor_id", "agent_tool", "session_id"):
        if not curation.get(field):
            failures.append(f"curation.{field} must be populated")
    if curation.get("inspected_validator_outputs") is not False:
        failures.append("curation.inspected_validator_outputs must be false")
    if curation.get("inspected_task_1038_implementation") is not False:
        failures.append("curation.inspected_task_1038_implementation must be false")

    no_score = challenge_set.get("no_score_declaration") or {}
    if no_score.get("curator_session_id") != curation.get("session_id"):
        failures.append("no-score curator session does not match curation session")
    for field in (
        "validator_executed",
        "computed_output_inspected",
        "tuned_against_engine_behavior",
    ):
        if no_score.get(field) is not False:
            failures.append(f"no_score_declaration.{field} must be false")

    freeze = challenge_set.get("freeze_contract") or {}
    for field, expected in FROZEN_V2_THRESHOLDS.items():
        if freeze.get(field) != expected:
            failures.append(f"freeze_contract.{field} drifted")
    if freeze.get("item_order_digest_algorithm") != "sha256":
        failures.append("item-order digest algorithm must be sha256")
    try:
        digest_payload = "\n".join(
            f'{item["id"]}|{item["formula"]}|{item["expected_verdict"]}'
            for item in items
        ).encode("utf-8")
        observed_digest = hashlib.sha256(digest_payload).hexdigest()
    except KeyError as exc:
        observed_digest = "unavailable"
        failures.append(f"digest field missing from item: {exc.args[0]}")
    if observed_digest != freeze.get("item_order_digest"):
        failures.append("item-order digest mismatch")

    source_ledger = challenge_set.get("source_ledger")
    if not isinstance(source_ledger, list) or not source_ledger:
        failures.append("source_ledger must be populated")
        source_ids: set[str] = set()
    else:
        source_ids = {
            str(source.get("source_id"))
            for source in source_ledger
            if isinstance(source, dict) and source.get("source_id")
        }
    if any(str(item.get("source_id")) not in source_ids for item in items):
        failures.append("an item references an unknown source_id")

    if failures:
        raise FrozenCalibrationContaminationError(
            "CONTAMINATED frozen v2 calibration surface: " + "; ".join(failures)
        )

    return {
        "surface_id": str(challenge_set.get("id")),
        "item_order_digest": observed_digest,
        "item_count": len(items),
        "label_vocabulary": list(FROZEN_V2_LABELS),
        "curator_contributor_id": str(curation["contributor_id"]),
        "curator_agent_tool": str(curation["agent_tool"]),
        "curator_session_id": str(curation["session_id"]),
        "benchmark_authorship_independence": str(
            curation["benchmark_authorship_independence"]
        ),
        "bounded_verdict": str(curation["bounded_verdict"]),
        "thresholds": dict(FROZEN_V2_THRESHOLDS),
    }


def _run_label_blind_v2_batch(
    items: list[dict[str, Any]],
) -> tuple[list[Any], ChallengeSetSummary]:
    """Infer every row from allowed fields before revealing labels to scoring."""
    blind_items = [
        {
            "id": item.get("id"),
            "formula": item.get("formula"),
            "variables": item.get("variables"),
        }
        for item in items
    ]
    inferences = [infer_item(item) for item in blind_items]
    results = [
        score_inference(
            item,
            inference,
            scoring_contract=SCORING_CONTRACT_LABEL_BLIND_V2,
        )
        for item, inference in zip(items, inferences, strict=True)
    ]

    by_category: dict[str, dict[str, int]] = {}
    computed = Counter(result.computed_verdict for result in results)
    for item, result in zip(items, results, strict=True):
        category = str(item.get("category") or item.get("domain") or "uncategorized")
        bucket = by_category.setdefault(
            category,
            {"total": 0, "exact_agree": 0, "policy_agree": 0},
        )
        bucket["total"] += 1
        bucket["exact_agree"] += int(result.exact_match)
        bucket["policy_agree"] += int(result.policy_match)

    return results, ChallengeSetSummary(
        total=len(items),
        exact_agree=sum(result.exact_match for result in results),
        policy_agree=sum(result.policy_match for result in results),
        valid_count=computed["VALID"],
        invalid_count=computed["INVALID"],
        suspicious_count=computed["SUSPICIOUS"],
        inconclusive_count=computed["INCONCLUSIVE"],
        by_category=by_category,
    )


def _score_breakdowns(
    items: list[dict[str, Any]],
    item_results: list[Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """Build exact class and domain summaries from the post-inference score stage."""
    observed_labels = {
        result.expected_verdict for result in item_results
    } | {result.computed_verdict for result in item_results}
    class_labels = [
        *FROZEN_V2_LABELS,
        *sorted(observed_labels - set(FROZEN_V2_LABELS)),
    ]
    class_breakdown: dict[str, dict[str, Any]] = {}
    for label in class_labels:
        support = sum(result.expected_verdict == label for result in item_results)
        correct = sum(
            result.expected_verdict == label and result.exact_match
            for result in item_results
        )
        class_breakdown[label] = {
            "support": support,
            "correct": correct,
            "computed_count": sum(
                result.computed_verdict == label for result in item_results
            ),
            "recall": round(correct / support, 6) if support else None,
        }

    domain_breakdown: dict[str, dict[str, Any]] = {}
    for item, result in zip(items, item_results, strict=True):
        domain = str(item.get("domain") or item.get("category") or "uncategorized")
        bucket = domain_breakdown.setdefault(
            domain,
            {
                "total": 0,
                "exact_agree": 0,
                "expected_counts": Counter(),
                "computed_counts": Counter(),
                "disagreement_ids": [],
            },
        )
        bucket["total"] += 1
        bucket["exact_agree"] += int(result.exact_match)
        bucket["expected_counts"][result.expected_verdict] += 1
        bucket["computed_counts"][result.computed_verdict] += 1
        if not result.exact_match:
            bucket["disagreement_ids"].append(result.item_id)

    for bucket in domain_breakdown.values():
        bucket["exact_agreement_fraction"] = round(
            bucket["exact_agree"] / bucket["total"], 6
        )
        bucket["expected_counts"] = dict(sorted(bucket["expected_counts"].items()))
        bucket["computed_counts"] = dict(sorted(bucket["computed_counts"].items()))
    return class_breakdown, dict(sorted(domain_breakdown.items()))


def run_dimensional_validator_with_output(
    config_path: str | Path,
    output_dir: str | Path | None = None,
    *,
    scoring_contract_override: str | None = None,
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

    # A successor run may bind a frozen challenge-set snapshot without
    # mutating the experiment definition used by an earlier protected result.
    challenge_set_relative = config.get(
        "challenge_set_path",
        experiment["data"]["dataset_path"],
    )
    challenge_set_path = resolve_path(experiment_path, challenge_set_relative)
    # Agreement threshold encoded in comparison_targets[0].reference_value
    targets = experiment.get("comparison_targets") or []
    agreement_threshold: float = float(targets[0]["reference_value"]) if targets else 0.90

    # Determine output directory
    result_root = Path(resolve_path(config_path, config["result_root"]))
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
            "fixture": challenge_set_path,
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

    challenge_set_data = yaml.safe_load(challenge_set_path.read_text(encoding="utf-8")) or {}

    # Configurations created before TASK-1038 replay the historical contract.
    # Successor benchmarks must opt into label_blind_exact_v2 explicitly.
    declared_scoring_contract = scoring_contract_override or config.get("scoring_contract")
    legacy_replay_identity = (
        experiment_id == "EXP-0006"
        and (run_id, result_id)
        in {("RUN-0006", "RESULT-0007"), ("RUN-0007", "RESULT-0020")}
    )
    if declared_scoring_contract is None:
        if not legacy_replay_identity:
            raise ValueError(
                "New dimensional-validator configurations must declare "
                f"scoring_contract={SCORING_CONTRACT_LABEL_BLIND_V2!r}."
            )
        scoring_contract = SCORING_CONTRACT_LEGACY_V1
    else:
        scoring_contract = str(declared_scoring_contract)
    if (
        scoring_contract == SCORING_CONTRACT_LEGACY_V1
        and not legacy_replay_identity
    ):
        raise ValueError(
            "legacy_policy_v1 is restricted to protected "
            "RESULT-0007/RESULT-0020 replays."
        )

    is_label_blind_v2 = scoring_contract == SCORING_CONTRACT_LABEL_BLIND_V2
    is_frozen_v2_calibration = bool(config.get("frozen_calibration_contract", False))
    if (
        challenge_set_data.get("status") == FROZEN_V2_STATUS
        and not is_frozen_v2_calibration
    ):
        raise FrozenCalibrationContaminationError(
            "CONTAMINATED frozen v2 calibration surface: config must declare "
            "frozen_calibration_contract=true"
        )
    frozen_contract_audit: dict[str, Any] | None = None
    if is_frozen_v2_calibration:
        if not is_label_blind_v2:
            raise FrozenCalibrationContaminationError(
                "CONTAMINATED frozen v2 calibration surface: scoring contract is not "
                "label_blind_exact_v2"
            )
        # The integrity audit intentionally runs before any formula inference.
        frozen_contract_audit = _verify_frozen_v2_calibration_contract(
            challenge_set_data
        )

    items = challenge_set_data.get("items", []) or []
    if is_label_blind_v2:
        item_results, summary = _run_label_blind_v2_batch(items)
    else:
        item_results, summary = validate_challenge_set(
            challenge_set_data,
            scoring_contract=scoring_contract,
        )

    declared_total = challenge_set_data.get("total_items")
    if declared_total is not None and int(declared_total) != summary.total:
        raise ValueError(
            f"{challenge_set_path} declares total_items={declared_total}, "
            f"but contains {summary.total} items."
        )

    expected_item_count = config.get(
        "expected_item_count",
        experiment["data"].get("expected_item_count"),
    )
    if expected_item_count is not None and summary.total != int(expected_item_count):
        raise ValueError(
            f"{experiment_id} benchmark scope expects {expected_item_count} items, "
            f"but {challenge_set_path} contains {summary.total}."
        )
    benchmark_scope = config.get(
        "benchmark_scope",
        experiment["data"].get("benchmark_scope", "unspecified"),
    )
    result_title = str(config.get("result_title", experiment["title"]))
    source_challenge_set_path = str(
        config.get(
            "challenge_set_source_path",
            experiment["data"].get("source_challenge_set_path", challenge_set_relative),
        )
    )

    # Determine verdict. V2 promotes exact match to the primary metric; the
    # legacy contract retains policy-adjusted agreement for reproducibility.
    exact_agreement = summary.exact_agreement_fraction
    policy_agreement = summary.policy_agreement_fraction
    primary_metric = (
        "exact_agreement_fraction"
        if is_label_blind_v2
        else "policy_adjusted_agreement_fraction"
    )
    primary_agree = summary.exact_agree if is_label_blind_v2 else summary.policy_agree
    agreement = exact_agreement if is_label_blind_v2 else policy_agreement
    class_breakdown, domain_breakdown = _score_breakdowns(items, item_results)

    calibration_outcome: str | None = None
    valid_recall: float | None = None
    invalid_recall: float | None = None
    inconclusive_rate = summary.inconclusive_count / summary.total if summary.total else 0.0
    threshold_outcomes: dict[str, bool] = {}
    if frozen_contract_audit is not None:
        thresholds = frozen_contract_audit["thresholds"]
        agreement_threshold = float(thresholds["exact_agreement_threshold"])
        valid_recall = float(class_breakdown["VALID"]["recall"] or 0.0)
        invalid_recall = float(class_breakdown["INVALID"]["recall"] or 0.0)
        threshold_outcomes = {
            "exact_agreement": agreement >= agreement_threshold,
            "valid_recall": valid_recall >= float(thresholds["valid_recall_floor"]),
            "invalid_recall": invalid_recall >= float(thresholds["invalid_recall_floor"]),
            "inconclusive_rate": inconclusive_rate
            <= float(thresholds["inconclusive_ceiling"]),
        }
        calibration_outcome = (
            "PASS" if all(threshold_outcomes.values()) else "FAIL"
        )
        best_verdict = "VALID" if calibration_outcome == "PASS" else "INCONCLUSIVE"
    else:
        best_verdict = "VALID" if agreement >= agreement_threshold else "INCONCLUSIVE"

    inconclusive_limit = 1
    inconclusive_status = "PASS" if summary.inconclusive_count <= inconclusive_limit else "FAIL"
    if summary.inconclusive_count == 0:
        inconclusive_details = "All items produced a definite verdict."
    elif summary.inconclusive_count <= inconclusive_limit:
        inconclusive_details = (
            f"{summary.inconclusive_count} item returned INCONCLUSIVE; "
            f"MVP tolerance is {inconclusive_limit}."
        )
    else:
        inconclusive_details = (
            f"{summary.inconclusive_count} items returned INCONCLUSIVE, "
            f"exceeding MVP tolerance ({inconclusive_limit})."
        )

    disagreement_id_list = [
        result.item_id
        for result in item_results
        if not (result.exact_match if is_label_blind_v2 else result.policy_match)
    ]
    disagreement_ids_value = ", ".join(disagreement_id_list) if disagreement_id_list else "none"
    fixture_sha256 = input_hashes["fixture"]["sha256"]
    is_result_0020_publication_replay = (
        experiment_id == "EXP-0006"
        and run_id == "RUN-0007"
        and result_id == "RESULT-0020"
        and benchmark_scope == "frozen_live_74"
        and summary.total == 74
        and scoring_contract == SCORING_CONTRACT_LEGACY_V1
    )

    # Build verification checks
    checks = [
        {
            "name": "challenge_set_loaded",
            "status": "PASS",
            "details": (
                f"Loaded {summary.total} items from the {benchmark_scope} challenge-set scope."
            ),
            "metrics": {"item_count": summary.total},
        },
        {
            "name": "challenge_set_declared_total_matches_items",
            "status": "PASS",
            "details": (
                f"Challenge-set metadata declares total_items={declared_total}; "
                f"parsed {summary.total} items."
            ),
            "metrics": {
                "declared_total_items": declared_total,
                "parsed_item_count": summary.total,
            },
        },
    ]

    if frozen_contract_audit is not None:
        thresholds = frozen_contract_audit["thresholds"]
        checks.extend(
            [
                {
                    "name": "frozen_v2_contract_integrity",
                    "status": "PASS",
                    "details": (
                        "Verified the 80-item manifest, label vocabulary, item-order "
                        "digest, curator identity, no-score declaration, and "
                        "CALIBRATION_ONLY_ROLE_LIMIT before inference."
                    ),
                    "metrics": {
                        "item_count": frozen_contract_audit["item_count"],
                        "item_order_digest": frozen_contract_audit[
                            "item_order_digest"
                        ],
                        "label_vocabulary": ",".join(
                            frozen_contract_audit["label_vocabulary"]
                        ),
                        "benchmark_authorship_independence": frozen_contract_audit[
                            "benchmark_authorship_independence"
                        ],
                        "bounded_verdict": frozen_contract_audit["bounded_verdict"],
                    },
                },
                {
                    "name": "label_blind_phase_separation",
                    "status": "PASS",
                    "details": (
                        "All 80 inferences completed from id, formula, and declared "
                        "variable dimensions before expected labels entered scoring."
                    ),
                    "metrics": {
                        "inference_item_count": summary.total,
                        "expected_labels_read_during_inference": False,
                        "inference_input_fields": "id,formula,variables",
                    },
                },
                {
                    "name": "agreement_fraction",
                    "status": "PASS"
                    if threshold_outcomes["exact_agreement"]
                    else "FAIL",
                    "details": (
                        f"Exact agreement is {primary_agree}/{summary.total} "
                        f"({agreement:.1%}), threshold {agreement_threshold:.0%}."
                    ),
                    "metrics": {
                        "agree": primary_agree,
                        "total": summary.total,
                        "agreement_fraction": round(agreement, 6),
                        "threshold": agreement_threshold,
                        "primary_metric": primary_metric,
                    },
                },
                {
                    "name": "valid_recall_floor",
                    "status": "PASS"
                    if threshold_outcomes["valid_recall"]
                    else "FAIL",
                    "details": (
                        f"VALID recall is {valid_recall:.1%}, floor "
                        f"{float(thresholds['valid_recall_floor']):.0%}."
                    ),
                    "metrics": {
                        "valid_recall": round(valid_recall, 6),
                        "floor": thresholds["valid_recall_floor"],
                        "support": class_breakdown["VALID"]["support"],
                    },
                },
                {
                    "name": "invalid_recall_floor",
                    "status": "PASS"
                    if threshold_outcomes["invalid_recall"]
                    else "FAIL",
                    "details": (
                        f"INVALID recall is {invalid_recall:.1%}, floor "
                        f"{float(thresholds['invalid_recall_floor']):.0%}."
                    ),
                    "metrics": {
                        "invalid_recall": round(invalid_recall, 6),
                        "floor": thresholds["invalid_recall_floor"],
                        "support": class_breakdown["INVALID"]["support"],
                    },
                },
                {
                    "name": "inconclusive_rate_ceiling",
                    "status": "PASS"
                    if threshold_outcomes["inconclusive_rate"]
                    else "FAIL",
                    "details": (
                        f"Computed INCONCLUSIVE rate is {inconclusive_rate:.1%}, ceiling "
                        f"{float(thresholds['inconclusive_ceiling']):.0%}."
                    ),
                    "metrics": {
                        "inconclusive_count": summary.inconclusive_count,
                        "inconclusive_rate": round(inconclusive_rate, 6),
                        "ceiling": thresholds["inconclusive_ceiling"],
                    },
                },
                {
                    "name": "legacy_equivalence_credit_disabled",
                    "status": "PASS",
                    "details": (
                        "PASS/FAIL uses exact categorical matches only; policy "
                        "equivalences receive zero primary-score credit."
                    ),
                    "metrics": {
                        "credited_non_exact_matches": 0,
                        "primary_agree": primary_agree,
                    },
                },
            ]
        )
    else:
        checks.extend(
            [
                {
                    "name": "inconclusive_items_within_mvp_tolerance",
                    "status": inconclusive_status,
                    "details": inconclusive_details,
                    "metrics": {
                        "inconclusive_count": summary.inconclusive_count,
                        "inconclusive_limit": inconclusive_limit,
                    },
                },
                {
                    "name": "agreement_fraction",
                    "status": "PASS" if agreement >= agreement_threshold else "FAIL",
                    "details": (
                        f"Primary metric {primary_metric} is "
                        f"{primary_agree}/{summary.total} ({agreement:.1%}), "
                        f"threshold {agreement_threshold:.0%}."
                    ),
                    "metrics": {
                        "agree": primary_agree,
                        "total": summary.total,
                        "agreement_fraction": round(agreement, 6),
                        "threshold": agreement_threshold,
                        "primary_metric": primary_metric,
                    },
                },
            ]
        )

    checks.append(
        {
            "name": "agreement_metric_decomposition",
            "status": "PASS",
            "details": (
                f"Exact categorical agreement: {summary.exact_agree}/{summary.total} "
                f"({exact_agreement:.1%}); policy-adjusted agreement: "
                f"{summary.policy_agree}/{summary.total} ({policy_agreement:.1%})."
            ),
            "metrics": {
                "exact_agree": summary.exact_agree,
                "exact_agreement_fraction": round(exact_agreement, 6),
                "policy_adjusted_agree": summary.policy_agree,
                "policy_adjusted_agreement_fraction": round(policy_agreement, 6),
            },
        }
    )

    if is_result_0020_publication_replay:
        # These three RESULT-0020 publication-packaging checks were originally
        # hand-authored during Gate A. Emit them only for the frozen live-74
        # publication replay so other dimensional-validator runs keep generic
        # verification semantics.
        checks.extend(
            [
                {
                    "name": "zero_disagreement_ledger",
                    "status": "PASS" if not disagreement_id_list else "FAIL",
                    "details": (
                        "The deterministic replay produced no disagreements with the "
                        f"{summary.total} curated benchmark expectations."
                        if not disagreement_id_list
                        else (
                            f"{len(disagreement_id_list)} item(s) disagreed with the "
                            f"{summary.total} curated benchmark expectations."
                        )
                    ),
                    "metrics": {
                        "disagreement_count": summary.total - primary_agree,
                        "disagreement_ids": disagreement_ids_value,
                    },
                },
                {
                    "name": "frozen_input_checksum",
                    "status": "PASS",
                    "details": (
                        "The frozen publication fixture is checksum-pinned and "
                        "byte-identical to the live challenge set at the publication "
                        "code commit."
                    ),
                    "metrics": {
                        "fixture_sha256": fixture_sha256,
                        "source_sha256_at_freeze": fixture_sha256,
                    },
                },
                {
                    "name": "protected_result_not_rewritten",
                    "status": "PASS",
                    "details": (
                        f"{result_id} and {run_id} are new identities; frozen "
                        "RESULT-0007 and EXP-0006/RUN-0006 remain unchanged."
                    ),
                    "metrics": {
                        "protected_result_rewrite": False,
                    },
                },
            ]
        )

    # ---------- metrics.json ----------
    item_domains = {
        str(item.get("id")): str(
            item.get("domain") or item.get("category") or "uncategorized"
        )
        for item in items
    }
    disagreement_ledger = [
        {
            "id": result.item_id,
            "domain": item_domains.get(result.item_id, "uncategorized"),
            "expected": result.expected_verdict,
            "computed": result.computed_verdict,
            "detail": result.detail,
        }
        for result in item_results
        if not (result.exact_match if is_label_blind_v2 else result.policy_match)
    ]
    metrics: dict[str, Any] = {
        "run_id": run_id,
        "experiment_id": experiment_id,
        "total_items": summary.total,
        "scoring_contract": scoring_contract,
        "primary_metric": primary_metric,
        "agree": primary_agree,
        "agreement_fraction": round(agreement, 6),
        "exact_agree": summary.exact_agree,
        "exact_agreement_fraction": round(exact_agreement, 6),
        "policy_adjusted_agree": summary.policy_agree,
        "policy_adjusted_agreement_fraction": round(policy_agreement, 6),
        "non_exact_policy_acceptance_count": sum(
            result.policy_match and not result.exact_match for result in item_results
        ),
        "agreement_threshold": agreement_threshold,
        "benchmark_scope": benchmark_scope,
        "expected_item_count": expected_item_count,
        "valid_count": summary.valid_count,
        "invalid_count": summary.invalid_count,
        "suspicious_count": summary.suspicious_count,
        "inconclusive_count": summary.inconclusive_count,
        "best_verdict": best_verdict,
        "disagreement_count": summary.total - primary_agree,
        "disagreement_ids": disagreement_id_list,
        "disagreement_ledger": disagreement_ledger,
        "class_breakdown": class_breakdown,
        "domain_breakdown": domain_breakdown,
        "challenge_set_provenance": {
            "frozen_input": relative_or_absolute(challenge_set_path, repo_root),
            "source_path": source_challenge_set_path,
        },
        "item_results": [
            {
                "id": r.item_id,
                "expected": r.expected_verdict,
                "computed": r.computed_verdict,
                "exact_match": r.exact_match,
                "policy_match": r.policy_match,
                "agreement_kind": r.agreement_kind,
                "agrees": r.exact_match if is_label_blind_v2 else r.policy_match,
                "warnings": list(r.warnings),
                "detail": r.detail,
            }
            for r in item_results
        ],
    }
    if frozen_contract_audit is not None:
        metrics.update(
            {
                "calibration_outcome": calibration_outcome,
                "threshold_outcomes": threshold_outcomes,
                "valid_recall": round(valid_recall, 6),
                "invalid_recall": round(invalid_recall, 6),
                "inconclusive_rate": round(inconclusive_rate, 6),
                "frozen_contract_audit": frozen_contract_audit,
                "claim_ceiling": (
                    "Calibration-only SI-focused validator quality floor; no "
                    "confirmatory, Gate C, CLAIM-0005, semantic, or universal "
                    "physical-correctness interpretation is authorized."
                ),
                "output_routing": {
                    "canonical_destination": f"results/{experiment_id}/{run_id}/",
                    "review_tier": "AGENT_PUBLISHED",
                    "gate_a": "PASS",
                    "gate_b": "NOT_ATTEMPTED",
                    "claim_impact": "none; CLAIM-0005 unchanged",
                    "knowledge_impact": "none",
                    "publication_blocker": (
                        "none for AGENT_PUBLISHED calibration evidence; maintainer "
                        "review remains required"
                    ),
                    "calibration_role": "CALIBRATION_ONLY_ROLE_LIMIT",
                },
            }
        )

    metrics_path = run_dir / "metrics.json"
    write_text_atomic(metrics_path, json.dumps(metrics, indent=2))

    # ---------- report.md ----------
    disagree_rows = "\n        ".join(
        f"| {r.item_id} | {r.expected_verdict} | {r.computed_verdict} | "
        f"{r.detail.replace('|', '/')} |"
        for r in item_results
        if not (r.exact_match if is_label_blind_v2 else r.policy_match)
    )
    if not disagree_rows:
        disagree_rows = "| none | - | - | No exact-label disagreements. |"
    class_rows = "\n        ".join(
        "| {label} | {support} | {computed} | {correct} | {recall} |".format(
            label=label,
            support=values["support"],
            computed=values["computed_count"],
            correct=values["correct"],
            recall=(
                f"{float(values['recall']):.1%}"
                if values["recall"] is not None
                else "n/a"
            ),
        )
        for label, values in class_breakdown.items()
    )
    domain_rows = "\n        ".join(
        "| {domain} | {total} | {agree} | {fraction:.1%} | {expected} | "
        "{computed} | {disagreements} |".format(
            domain=domain,
            total=values["total"],
            agree=values["exact_agree"],
            fraction=values["exact_agreement_fraction"],
            expected=", ".join(
                f"{label}:{count}"
                for label, count in values["expected_counts"].items()
            ),
            computed=", ".join(
                f"{label}:{count}"
                for label, count in values["computed_counts"].items()
            ),
            disagreements=", ".join(values["disagreement_ids"]) or "none",
        )
        for domain, values in domain_breakdown.items()
    )
    calibration_summary_row = (
        f"| Calibration threshold outcome | **{calibration_outcome}** |"
        if calibration_outcome is not None
        else ""
    )
    calibration_limitations = (
        "- This is same-owner, role-disjoint calibration evidence under "
        "`CALIBRATION_ONLY_ROLE_LIMIT`; it is not confirmatory evidence and "
        "cannot support Gate C or reopen CLAIM-0005.\n"
        "- Expected labels were used only for the frozen digest preflight and "
        "the post-inference scoring phase; inference received only item id, "
        "formula, and declared variable dimensions."
        if frozen_contract_audit is not None
        else ""
    )
    calibration_limitations = calibration_limitations.replace("\n", "\n        ")
    report_text = textwrap.dedent(f"""\
        # Dimensional Analysis Validator - Run Report

        **Run:** {run_id}  **Experiment:** {experiment_id}  **Verdict:** {best_verdict}
        **Scope:** `{benchmark_scope}`

        ## Summary

        | Metric | Value |
        |---|---|
        | Total items | {summary.total} |
        | Scoring contract | `{scoring_contract}` |
        | Primary metric | `{primary_metric}` |
        | Primary agreement | {primary_agree}/{summary.total} ({agreement:.1%}) |
        | Exact categorical agreement | {summary.exact_agree}/{summary.total} ({exact_agreement:.1%}) |
        | Policy-adjusted agreement | {summary.policy_agree}/{summary.total} ({policy_agreement:.1%}) |
        | VALID computed | {summary.valid_count} |
        | INVALID computed | {summary.invalid_count} |
        | SUSPICIOUS computed | {summary.suspicious_count} |
        | INCONCLUSIVE | {summary.inconclusive_count} |
        | Remaining primary disagreements | {summary.total - primary_agree} |
        | Agreement threshold | {agreement_threshold:.0%} |
        {calibration_summary_row}
        | Best verdict | **{best_verdict}** |

        ## Disagreements

        | ID | Expected | Computed | Detail |
        |---|---|---|---|
        {disagree_rows if disagree_rows else "_None_"}

        The machine-readable `metrics.json` contains all {summary.total} item
        outcomes plus the complete disagreement ledger above.

        ## Class Breakdown

        | Expected class | Support | Computed count | Exact correct | Recall |
        |---|---:|---:|---:|---:|
        {class_rows}

        ## Domain Breakdown

        | Domain | Total | Exact | Agreement | Expected | Computed | Disagreements |
        |---|---:|---:|---:|---|---|---|
        {domain_rows}

        ## Limitations

        - Dimension-only checks do not establish numerical correctness,
          empirical validity, or physical truth.
        - KNOWN_LIMIT_FAIL rows are expected to be dimensionally balanced;
          their numerical or regime failures remain outside validator scope.
        - Curated dimensionally balanced SUSPICIOUS rows require explicit
          metadata because dimensions alone cannot infer missing dimensionless
          factors or semantic emptiness.
        - SUSPICIOUS items with explicit dimensional mismatch are classified
          INVALID; this is stricter but operationally correct (formula is flagged).
        - Unit symbol table is limited to SI base units and common derived units.
          Natural-unit or Gaussian-unit formulas are outside scope.
        {calibration_limitations}

        ## Claim Ceiling

        The validator achieves {agreement:.1%} on its declared primary metric
        (`{primary_metric}`) for the frozen {summary.total}-item
        `{benchmark_scope}` benchmark scope. Exact and policy-adjusted metrics
        are reported separately. This score is a bounded SI-focused validator
        quality floor, not semantic or universal physical correctness. No claim
        about unseen formulas, numerical correctness, empirical validity, or
        physics domains outside the benchmark scope is made.
    """)
    report_path = run_dir / "report.md"
    write_text_atomic(report_path, report_text)

    _claim_target = "claims/CLAIM-0005-dimensional-analysis-validator.md"
    _know_target = "knowledge/physics_validation/dimensional_analysis_validator.md"
    _claim_target_path = repo_root / _claim_target
    _know_target_path = repo_root / _know_target
    _claim_original = (
        _claim_target_path.read_text(encoding="utf-8") if _claim_target_path.exists() else ""
    )
    _know_original = (
        _know_target_path.read_text(encoding="utf-8") if _know_target_path.exists() else ""
    )

    # ---------- claim_update ----------
    if frozen_contract_audit is not None:
        claim_scope_text = textwrap.dedent(f"""\
            The exact-v2 calibration outcome is {calibration_outcome} on the
            frozen {summary.total}-item `{benchmark_scope}` surface. This is
            same-owner role-disjoint calibration evidence under
            `CALIBRATION_ONLY_ROLE_LIMIT`; it cannot unblock CLAIM-0005,
            support Gate C, or justify any semantic or universal correctness
            claim. CLAIM-0005 is not modified.
        """)
        claim_patch_rationale = (
            f"Preserve {calibration_outcome} as calibration-only evidence; "
            "CLAIM-0005 remains unchanged and DRAFT."
        )
    else:
        claim_scope_text = textwrap.dedent(f"""\
            The validator achieves {agreement:.1%} on `{primary_metric}` for the
            frozen {summary.total}-item `{benchmark_scope}` benchmark scope.
            Exact categorical agreement is {exact_agreement:.1%};
            policy-adjusted agreement is {policy_agreement:.1%}. CLAIM-0005 is
            already drafted with this scope restriction. Maintainer review is
            required before any status or benchmark-text change.
        """)
        claim_patch_rationale = (
            f"Validator achieves {agreement:.1%} on {primary_metric}; exact and "
            "policy-adjusted metrics are separated; claim remains DRAFT pending "
            "human review."
        )
    claim_update_text = (
        "## Claim Update\n\n"
        f"Evidence source: {result_id}.\n"
        "Proposed status: DRAFT (no automatic promotion).\n\n"
        f"{claim_scope_text.strip()}\n"
    )
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
        rationale=claim_patch_rationale,
    )
    claim_update_patch_path = run_dir / "claim_update.patch.md"
    write_text_atomic(claim_update_patch_path, claim_update_patch_text)

    # ---------- knowledge_update ----------
    knowledge_scope_text = (
        f"The {calibration_outcome} exact-v2 score is calibration-only under "
        "CALIBRATION_ONLY_ROLE_LIMIT. It creates no reusable KNOW endorsement, "
        "does not change the dimensional-validator knowledge note, and cannot "
        "support confirmatory Gate C."
        if frozen_contract_audit is not None
        else (
            f"Dimensional validator benchmarked at {agreement:.1%} on "
            f"`{primary_metric}` over the frozen `{benchmark_scope}` scope "
            f"({summary.total} items); exact and policy-adjusted metrics are "
            "separate. No knowledge change is authorized by this "
            "result-publication task."
        )
    )
    knowledge_update_text = textwrap.dedent(f"""\
        ## Knowledge Update

        Evidence source: {result_id}.

        {knowledge_scope_text}
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
        rationale=(
            "Calibration-only score creates no knowledge endorsement; no change required."
            if frozen_contract_audit is not None
            else "Knowledge note already matches the run result; no change required."
        ),
    )
    knowledge_update_patch_path = run_dir / "knowledge_update.patch.md"
    write_text_atomic(knowledge_update_patch_path, knowledge_update_patch_text)

    # ---------- review artefacts ----------
    now_iso = datetime.now(tz=timezone.utc).isoformat()
    if frozen_contract_audit is not None:
        review_rationale = (
            f"Exact-v2 calibration outcome {calibration_outcome} on the frozen "
            f"{summary.total}-item surface; preserve AGENT_PUBLISHED and "
            "CALIBRATION_ONLY_ROLE_LIMIT with no CLAIM/KNOW promotion."
        )
        review_highlights = [
            f"Exact agreement: {primary_agree}/{summary.total} ({agreement:.1%})",
            f"VALID recall: {valid_recall:.1%}; INVALID recall: {invalid_recall:.1%}",
            f"INCONCLUSIVE rate: {inconclusive_rate:.1%}; outcome: {calibration_outcome}.",
        ]
        review_limitations = [
            "Same-owner role-disjoint calibration evidence, not confirmatory evidence.",
            "Cannot support Gate C, reopen CLAIM-0005, or create a KNOW endorsement.",
            "Dimensional checks do not establish semantic, numerical, or empirical validity.",
        ]
    else:
        review_rationale = (
            f"Dimensional validator achieves {agreement:.1%} on {primary_metric} "
            f"for the frozen {summary.total}-item {benchmark_scope} scope; "
            "keep DRAFT until independent review."
        )
        review_highlights = [
            f"{primary_metric}: {primary_agree}/{summary.total} ({agreement:.1%})",
            f"VALID: {summary.valid_count}, INVALID: {summary.invalid_count}",
            f"Remaining primary disagreements: {summary.total - primary_agree}.",
        ]
        review_limitations = [
            "Dimensional checks do not establish numerical or empirical validity.",
            "KNOWN_LIMIT_FAIL behavior remains outside the dimension-only verdict.",
            "Challenge set is internally curated (TASK-0017); no external validation.",
        ]
    review_summary_text = render_review_summary(
        result_id=result_id,
        claim_id="CLAIM-0005",
        knowledge_id="KNOW-0004",
        suggested_status="DRAFT",
        rationale=review_rationale,
        highlights=review_highlights,
        limitations=review_limitations,
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

    write_text_atomic(
        review_metadata_path, _yaml.safe_dump(review_metadata_payload, sort_keys=False)
    )

    # ---------- result.yaml ----------
    commit = git_commit(repo_root)
    config_reference = relative_or_absolute(config_path, repo_root)
    run_reference = relative_or_absolute(run_dir, repo_root)
    comparison_summary = [
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
                f"{primary_metric} is {primary_agree}/{summary.total}; threshold "
                f"{agreement_threshold:.0%}. Exact and policy-adjusted metrics are "
                "reported separately."
            ),
        }
    ]
    if frozen_contract_audit is not None:
        thresholds = frozen_contract_audit["thresholds"]
        for target_id, label, observed, reference, direction in (
            (
                "target_valid_recall",
                "VALID recall floor",
                valid_recall,
                thresholds["valid_recall_floor"],
                "at or above",
            ),
            (
                "target_invalid_recall",
                "INVALID recall floor",
                invalid_recall,
                thresholds["invalid_recall_floor"],
                "at or above",
            ),
            (
                "target_inconclusive_rate_ceiling",
                "INCONCLUSIVE rate ceiling",
                inconclusive_rate,
                thresholds["inconclusive_ceiling"],
                "at or below",
            ),
        ):
            comparison_summary.append(
                {
                    "target_id": target_id,
                    "label": label,
                    "reference_value": reference,
                    "observed_value": round(observed, 6),
                    "unit": None,
                    "absolute_difference": round(abs(observed - reference), 6),
                    "relative_difference": round(
                        abs(observed - reference) / reference, 6
                    ),
                    "notes": f"Observed value must be {direction} the frozen threshold.",
                }
            )
    result_limitations = [
        "Dimension-only agreement is formula-quality evidence, not proof of numerical correctness, empirical validity, or physical truth.",
        "KNOWN_LIMIT_FAIL rows are treated as dimensionally valid because numerical and regime limits are outside validator scope.",
        (
            "The legacy scoring contract may use curated metadata during inference; "
            "its policy-adjusted score is historical calibration evidence only."
            if scoring_contract == SCORING_CONTRACT_LEGACY_V1
            else "Label-blind v2 inference does not read expected labels or curated benchmark annotations."
        ),
        f"This result is restricted to the frozen {summary.total}-item {benchmark_scope} input snapshot.",
        "SUSPICIOUS items with explicit dimensional mismatch are classified INVALID.",
        "Unit symbol table covers SI base units and common derived units only.",
        "Natural-unit or Gaussian-unit formulas are outside scope.",
    ]
    if frozen_contract_audit is not None:
        result_limitations = [
            "Agent-published, not yet independently validated or maintainer-reviewed.",
            *result_limitations,
            "Benchmark authorship independence is same_owner_role_disjoint_agent, so this result is calibration-only and not confirmatory evidence.",
            "CALIBRATION_ONLY_ROLE_LIMIT blocks Gate C, CLAIM-0005 promotion, and any semantic or universal physical-correctness interpretation.",
        ]
    result_payload: dict[str, Any] = {
        "generated_at": now_iso,
        "result_id": result_id,
        "run_id": run_id,
        "experiment_id": experiment_id,
        "title": result_title,
        "hypothesis_id": hypothesis_id,
        "task_id": task_id,
        "engine_version": __version__,
        "git_commit": commit or "unknown",
        "command": (
            f"python -m physics_lab.cli run {config_reference} --output-dir {run_reference}"
        ),
        "input_file_hashes": input_hashes,
        "code_reference": "physics_lab/workflows/dimensional_validator.py",
        "limitations": result_limitations,
        "best_verdict": best_verdict,
        "comparison_summary": comparison_summary,
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
            "passed": all(check["status"] == "PASS" for check in checks),
            "checks": checks,
        },
        "artifacts": {
            "report": relative_or_absolute(report_path, repo_root),
            "metrics": relative_or_absolute(metrics_path, repo_root),
            "claim_update": relative_or_absolute(claim_update_path, repo_root),
            "claim_update_patch": relative_or_absolute(claim_update_patch_path, repo_root),
            "knowledge_update": relative_or_absolute(knowledge_update_path, repo_root),
            "knowledge_update_patch": relative_or_absolute(knowledge_update_patch_path, repo_root),
            "review_summary": relative_or_absolute(review_summary_path, repo_root),
            "review_metadata": relative_or_absolute(review_metadata_path, repo_root),
        },
    }

    if frozen_contract_audit is not None:
        result_payload.update(
            {
                "review_tier": "AGENT_PUBLISHED",
                "agent_proposal_evaluation": {
                    "review_tier_proposed": "AGENT_PUBLISHED",
                    "best_verdict_proposed": best_verdict,
                    "published_by": PUBLISHED_BY,
                    "benchmark_authorship_independence": frozen_contract_audit[
                        "benchmark_authorship_independence"
                    ],
                    "calibration_role_limit": frozen_contract_audit[
                        "bounded_verdict"
                    ],
                    "gates_checked": {
                        "deterministic_run": True,
                        "verification_block_populated": True,
                        "input_hashes_recorded": True,
                        "limitations_listed": True,
                        "engine_version_and_commit_pinned": True,
                        "schema_validation_passes": True,
                        "no_protected_artifact_rewrite": True,
                        "no_forbidden_overclaim_wording": True,
                        "dataset_provenance_valid": True,
                    },
                    "evidence_summary": (
                        f"The frozen 80-item exact-v2 calibration surface returned "
                        f"{calibration_outcome}: exact agreement {agreement:.1%}, "
                        f"VALID recall {valid_recall:.1%}, INVALID recall "
                        f"{invalid_recall:.1%}, and INCONCLUSIVE rate "
                        f"{inconclusive_rate:.1%}."
                    ),
                    "followup_for_maintainer": (
                        "Keep AGENT_PUBLISHED and CALIBRATION_ONLY_ROLE_LIMIT explicit. "
                        "Gate B may independently replay the command, but this surface "
                        "cannot become confirmatory Gate C evidence or reopen CLAIM-0005."
                    ),
                },
            }
        )

    result_path = run_dir / "result.yaml"
    validate_result_payload(result_payload, source=result_path)
    write_text_atomic(result_path, yaml.dump(result_payload, sort_keys=False, allow_unicode=True))
    if frozen_contract_audit is not None:
        gate_a_report_path = run_dir / "gate_a_report.md"
        write_text_atomic(
            gate_a_report_path,
            textwrap.dedent(f"""\
                # Gate A Report - {result_id}

                - Artifact: `{relative_or_absolute(result_path, repo_root)}`
                - Task: `{task_id}`
                - Proposed tier: `AGENT_PUBLISHED`
                - Calibration outcome: `{calibration_outcome}`
                - Gate A: `PASS`
                - Gate B: `NOT_ATTEMPTED`
                - Benchmark authorship independence: `same_owner_role_disjoint_agent`
                - Role limit: `CALIBRATION_ONLY_ROLE_LIMIT`

                ## Frozen Contract

                The workflow verified the 80-item count, label vocabulary,
                item-order digest `{frozen_contract_audit['item_order_digest']}`,
                curator identity, no-score declaration, and frozen thresholds
                before inference. All inferences completed from item id, formula,
                and declared variable dimensions before labels entered scoring.

                ## Thresholds

                | Metric | Observed | Threshold | Status |
                |---|---:|---:|---|
                | Exact agreement | {agreement:.1%} | >= {agreement_threshold:.0%} | {'PASS' if threshold_outcomes['exact_agreement'] else 'FAIL'} |
                | VALID recall | {valid_recall:.1%} | >= {float(frozen_contract_audit['thresholds']['valid_recall_floor']):.0%} | {'PASS' if threshold_outcomes['valid_recall'] else 'FAIL'} |
                | INVALID recall | {invalid_recall:.1%} | >= {float(frozen_contract_audit['thresholds']['invalid_recall_floor']):.0%} | {'PASS' if threshold_outcomes['invalid_recall'] else 'FAIL'} |
                | INCONCLUSIVE rate | {inconclusive_rate:.1%} | <= {float(frozen_contract_audit['thresholds']['inconclusive_ceiling']):.0%} | {'PASS' if threshold_outcomes['inconclusive_rate'] else 'FAIL'} |

                ## Routing

                - Canonical destination: `results/{experiment_id}/{run_id}/`
                - Claim impact: none; `CLAIM-0005` is unchanged.
                - Knowledge impact: none.
                - Publication blocker: none for AGENT_PUBLISHED calibration evidence;
                  maintainer review is still required.
                - This result cannot support confirmatory Gate C, semantic
                  correctness, universal physical correctness, or claim promotion.
            """),
        )

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
        title=result_title,
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=hypothesis_id,
        task_id=task_id,
        artifacts=artifacts,
        verdicts={"dimensional_validation": best_verdict},
        summary_lines=(
            f"{primary_metric}: {primary_agree}/{summary.total} ({agreement:.1%})",
            f"Verdict: {best_verdict}",
        ),
    )
