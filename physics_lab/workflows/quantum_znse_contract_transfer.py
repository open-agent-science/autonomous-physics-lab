"""Workflow adapter for the TASK-0957 ZnSe no-refit transfer RESULT.

This is the Gate-A/Gate-B replay bridge for AGENT-RUN-0090. It runs through
``physics_lab.cli run`` and reuses the committed quantum transfer engine, while
verifying the TASK-0914 frozen rows, thresholds, and source hashes before any
metric is packaged.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from physics_lab import __version__
from physics_lab.engines.quantum_cross_material_transfer import (
    BULK_GAP_EV,
    REQUIRED_MARGIN_EV,
    SHUFFLE_SEED,
    TETRA_EDGE_TO_EQUIV_DIAMETER,
    load_inp_rows,
    load_znse_rows,
    run_cross_material_transfer,
)
from physics_lab.registry.examples import load_example_config
from physics_lab.registry.experiments import load_experiment
from physics_lab.registry.hypotheses import load_hypothesis
from physics_lab.workflows.artifacts import (
    ExperimentArtifacts,
    ExperimentOutcome,
    find_repo_root,
    git_commit,
    relative_or_absolute,
    resolve_path,
    snapshot_input_files,
    task_path,
    write_text_atomic,
)

FIXTURE_RELATIVE = "data/quantum_dots/znse_no_refit_transfer_contract_fixture.yaml"
CODE_REFERENCE = "physics_lab/workflows/quantum_znse_contract_transfer.py"
COMMAND = "python -m physics_lab.cli run examples/quantum_znse_contract_transfer_result.yaml"
PUBLISHED_BY = {
    "contributor_id": "gladunrv",
    "github_username": "gladunrv",
    "agent_tool": "Codex",
    "model_version": "GPT-5",
}
LIMITATIONS = [
    "Agent-published, not yet independently validated or maintainer-reviewed.",
    "Scope is the TASK-0914 frozen two-material direct-size transfer contract only.",
    "Primary judge is InP calibration to ZnSe holdout on equivalent diameter; secondary routes cannot change the verdict.",
    "The transferred model beats the best control but misses the frozen 0.05 eV margin by 0.00341632 eV.",
    "Bulk gaps and the InP edge-to-equivalent-diameter conversion are fixed inputs, not fitted.",
    "No refit, correction search, threshold relaxation, effective-mass rescue, new row, source-byte redistribution, prediction, CLAIM, or KNOW artifact is created.",
    "No quantum-dot size law, material recommendation, device-performance guidance, biomedical wording, or design claim is made.",
]


def _dump_yaml(path: Path, payload: dict[str, Any]) -> None:
    write_text_atomic(path, yaml.safe_dump(payload, sort_keys=False, allow_unicode=True))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return payload


def _require_close(label: str, observed: float, expected: float, *, tolerance: float = 1e-9) -> None:
    if abs(float(observed) - float(expected)) > tolerance:
        raise ValueError(f"{label} drifted: observed {observed!r}, expected {expected!r}")


def _contract_survival_outcome(*, clears_predeclared_margin: bool, margin_ev: float) -> tuple[str, str]:
    if clears_predeclared_margin:
        return (
            "PASS_CLEARS_PREDECLARED_MARGIN",
            "bounded positive transfer memory (still no claim promotion)",
        )
    if margin_ev > 0.0:
        return (
            "FAIL_TO_CLEAR_PREDECLARED_MARGIN",
            "inconclusive/borderline memory, not a positive claim",
        )
    return (
        "NEGATIVE_MEMORY",
        "negative/control memory (the transferred model does not beat the best control)",
    )


def _verify_fixture(fixture: dict[str, Any], *, repo_root: Path) -> dict[str, Path]:
    contract = fixture["contract"]
    _require_close(
        "tetra_edge_to_equiv_diameter_factor",
        round(TETRA_EDGE_TO_EQUIV_DIAMETER, 9),
        contract["tetra_edge_to_equiv_diameter_factor"],
    )
    _require_close("required_margin_ev", REQUIRED_MARGIN_EV, contract["required_margin_ev"])
    if SHUFFLE_SEED != int(contract["shuffle_seed"]):
        raise ValueError(f"shuffle seed drifted: {SHUFFLE_SEED} != {contract['shuffle_seed']}")
    if BULK_GAP_EV != contract["bulk_gap_ev"]:
        raise ValueError(f"bulk-gap inputs drifted: {BULK_GAP_EV} != {contract['bulk_gap_ev']}")

    paths: dict[str, Path] = {}
    for key, loader in (("inp", load_inp_rows), ("znse", load_znse_rows)):
        dataset = fixture["datasets"][key]
        path = repo_root / str(dataset["path"])
        paths[key] = path
        observed_hash = _sha256(path)
        if observed_hash != dataset["sha256"]:
            raise ValueError(
                f"{key} dataset hash drifted: {observed_hash} != {dataset['sha256']}"
            )
        observed_row_ids = [row.entry_id for row in loader(path)]
        if observed_row_ids != list(dataset["row_ids"]):
            raise ValueError(
                f"{key} row ids drifted: {observed_row_ids!r} != {dataset['row_ids']!r}"
            )
    return paths


def _compute_metrics(fixture: dict[str, Any], *, repo_root: Path) -> dict[str, Any]:
    paths = _verify_fixture(fixture, repo_root=repo_root)
    metrics = run_cross_material_transfer(
        inp_dataset_path=paths["inp"],
        znse_dataset_path=paths["znse"],
    )
    outcome, routing = _contract_survival_outcome(
        clears_predeclared_margin=metrics["primary_clears_predeclared_margin"],
        margin_ev=metrics["primary_transfer_margin_vs_best_control_ev"],
    )
    metrics["contract_survival_outcome"] = outcome
    metrics["contract_outcome_routing"] = routing

    expected = fixture["expected_outcome"]
    exact_keys = (
        "primary_transfer_mae_ev",
        "primary_best_control_mae_ev",
        "primary_transfer_margin_vs_best_control_ev",
    )
    for key in exact_keys:
        _require_close(key, metrics[key], expected[key])
    if metrics["primary_best_control_id"] != expected["primary_best_control_id"]:
        raise ValueError("primary best-control id drifted")
    if metrics["primary_clears_predeclared_margin"] is not expected["primary_clears_predeclared_margin"]:
        raise ValueError("primary margin-clear boolean drifted")
    if metrics["scientific_verdict"] != expected["scientific_verdict"]:
        raise ValueError("scientific verdict drifted")
    if outcome != expected["contract_survival_outcome"]:
        raise ValueError("contract survival outcome drifted")
    if routing != expected["contract_outcome_routing"]:
        raise ValueError("contract routing drifted")
    return metrics


def _relative_difference(reference: float, observed: float) -> float:
    return round(abs(float(reference) - float(observed)) / abs(float(reference)), 9)


def _comparison_summary(fixture: dict[str, Any], metrics: dict[str, Any]) -> list[dict[str, Any]]:
    expected = fixture["expected_outcome"]
    margin = metrics["primary_transfer_margin_vs_best_control_ev"]
    required = fixture["contract"]["required_margin_ev"]
    transfer_mae = metrics["primary_transfer_mae_ev"]
    control_mae = metrics["primary_best_control_mae_ev"]
    reverse_margin = expected["secondary_reverse_margin_vs_best_control_ev"]
    return [
        {
            "target_id": "target_primary_margin_threshold",
            "label": "Primary InP-to-ZnSe transfer margin versus the predeclared survival threshold",
            "reference_value": required,
            "observed_value": margin,
            "unit": "eV",
            "absolute_difference": round(abs(required - margin), 9),
            "relative_difference": _relative_difference(required, margin),
            "notes": "The primary margin is positive but below the frozen threshold, so the contract fails to clear.",
        },
        {
            "target_id": "target_primary_transfer_control_mae",
            "label": "Primary transferred-model MAE versus best required control MAE",
            "reference_value": control_mae,
            "observed_value": transfer_mae,
            "unit": "eV",
            "absolute_difference": round(abs(control_mae - transfer_mae), 9),
            "relative_difference": _relative_difference(control_mae, transfer_mae),
            "notes": "Lower MAE is better; this margin is not large enough to clear the predeclared rule.",
        },
        {
            "target_id": "target_secondary_reverse_margin",
            "label": "Secondary ZnSe-to-InP margin versus the same survival threshold",
            "reference_value": required,
            "observed_value": reverse_margin,
            "unit": "eV",
            "absolute_difference": round(abs(reverse_margin - required), 9),
            "relative_difference": _relative_difference(required, reverse_margin),
            "notes": "The reverse direction clears, but it is secondary and cannot change the primary verdict.",
        },
    ]


def _verification_block(fixture: dict[str, Any], metrics: dict[str, Any]) -> dict[str, Any]:
    expected = fixture["expected_outcome"]
    shortfall = round(
        fixture["contract"]["required_margin_ev"]
        - metrics["primary_transfer_margin_vs_best_control_ev"],
        9,
    )
    return {
        "passed": True,
        "checks": [
            {
                "name": "contract_fixture_gate",
                "status": "PASS",
                "details": "The TASK-0914 frozen row ids, source dataset hashes, bulk gaps, shuffle seed, and margin are verified before metrics are packaged.",
                "metrics": {
                    "inp_row_count": len(fixture["datasets"]["inp"]["row_ids"]),
                    "znse_row_count": len(fixture["datasets"]["znse"]["row_ids"]),
                    "required_margin_ev": fixture["contract"]["required_margin_ev"],
                    "shuffle_seed": fixture["contract"]["shuffle_seed"],
                    "source_agent_run_id": fixture["source_agent_run_id"],
                },
            },
            {
                "name": "agent_run_0090_metric_reproduction",
                "status": "PASS",
                "details": "The workflow reproduces AGENT-RUN-0090 headline metrics exactly within 1e-9 tolerance.",
                "metrics": {
                    "primary_transfer_mae_ev": metrics["primary_transfer_mae_ev"],
                    "primary_best_control_mae_ev": metrics["primary_best_control_mae_ev"],
                    "primary_margin_ev": metrics["primary_transfer_margin_vs_best_control_ev"],
                    "expected_primary_margin_ev": expected["primary_transfer_margin_vs_best_control_ev"],
                },
            },
            {
                "name": "frozen_margin_outcome",
                "status": "PASS",
                "details": "The primary model beats both controls but falls short of the frozen 0.05 eV margin, preserving FAIL_TO_CLEAR_PREDECLARED_MARGIN.",
                "metrics": {
                    "primary_clears_predeclared_margin": metrics["primary_clears_predeclared_margin"],
                    "margin_shortfall_ev": shortfall,
                    "contract_survival_outcome": metrics["contract_survival_outcome"],
                    "best_verdict": metrics["scientific_verdict"],
                },
            },
            {
                "name": "no_refit_or_rescue",
                "status": "PASS",
                "details": "The engine fits C and n on the calibration material only; no target-material refit, threshold relaxation, correction search, or secondary-route rescue is performed.",
                "metrics": {
                    "no_refit": fixture["contract"]["no_refit"],
                    "no_correction_search": fixture["contract"]["no_correction_search"],
                    "no_post_hoc_threshold_change": fixture["contract"]["no_post_hoc_threshold_change"],
                    "secondary_reverse_margin_ev": expected["secondary_reverse_margin_vs_best_control_ev"],
                },
            },
            {
                "name": "source_boundary",
                "status": "PASS",
                "details": "The workflow uses committed curated factual rows only and vendors no publisher source bytes, figures, screenshots, or table images.",
                "metrics": {
                    "source_bytes_committed": False,
                    "inp_dataset_sha256": fixture["datasets"]["inp"]["sha256"],
                    "znse_dataset_sha256": fixture["datasets"]["znse"]["sha256"],
                },
            },
        ],
    }


def _render_report(result_id: str, fixture: dict[str, Any], metrics: dict[str, Any]) -> str:
    model = metrics["framings"]["equivalent_diameter"]["forward_inp_to_znse"]["frozen_model"]
    return "\n".join(
        [
            f"# {result_id}: Quantum ZnSe No-Refit Contract Transfer",
            "",
            "This AGENT_PUBLISHED result packages AGENT-RUN-0090 through a replayable `physics_lab.cli run` workflow.",
            "The primary outcome is `FAIL_TO_CLEAR_PREDECLARED_MARGIN`: the transferred model beats the best control but misses the frozen 0.05 eV survival margin.",
            "",
            "## Primary Judge",
            "",
            "| Quantity | Value |",
            "| --- | ---: |",
            f"| Transferred InP-to-ZnSe MAE | {metrics['primary_transfer_mae_ev']:.9f} eV |",
            f"| Best control (`{metrics['primary_best_control_id']}`) MAE | {metrics['primary_best_control_mae_ev']:.9f} eV |",
            f"| Margin over best control | {metrics['primary_transfer_margin_vs_best_control_ev']:.9f} eV |",
            f"| Required margin | {fixture['contract']['required_margin_ev']:.9f} eV |",
            "",
            "Frozen primary model:",
            f"`conf = {model['coefficient_C']:.6f} * d^(-{model['exponent_n']:.6f})`.",
            "",
            "## Verdict",
            "",
            "`INCONCLUSIVE`. The primary margin is positive but short by 0.00341632 eV. The reverse direction clears as a secondary diagnostic, but the TASK-0914 contract forbids using it to change the primary verdict.",
            "",
            "## Output Routing",
            "",
            "- Canonical destination: `results/EXP-0022/RUN-0001/result.yaml`.",
            "- Review tier: `AGENT_PUBLISHED`.",
            "- Gate A: passed by deterministic workflow, verification block, input hashes, and no-claim limitations.",
            "- Gate B: pending independent replay.",
            "- Claim impact: none.",
            "- Knowledge impact: none.",
            "- Publication blocker: none for this AGENT_PUBLISHED result; maintainer review is still required for endorsement.",
            "",
        ]
    )


def _render_no_promotion(title: str, kind: str, result_id: str) -> str:
    return "\n".join(
        [
            f"# {title} - none",
            "",
            f"No {kind} is created or updated by {result_id}. The result is bounded two-material control memory and does not promote a claim.",
            "",
        ]
    )


def _render_patch_stub(title: str, result_id: str) -> str:
    return "\n".join(
        [
            f"# {title} - none",
            "",
            "No file is targeted and no diff is proposed.",
            "",
            "```diff",
            f"# No patch proposed; {result_id} does not promote a CLAIM or KNOW artifact.",
            "```",
            "",
        ]
    )


def _render_review_summary(result_id: str, metrics: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# Review Summary - {result_id}",
            "",
            "Proposed review tier: AGENT_PUBLISHED. Proposed verdict: INCONCLUSIVE.",
            "",
            f"Primary margin: {metrics['primary_transfer_margin_vs_best_control_ev']} eV against the frozen 0.05 eV survival rule.",
            "The honest FAIL_TO_CLEAR_PREDECLARED_MARGIN outcome is preserved as bounded control memory.",
            "No CLAIM or KNOW promotion is proposed.",
            "",
        ]
    )


def _review_metadata(
    *,
    result_id: str,
    run_id: str,
    experiment_id: str,
    generated_at: str,
    claim_update_patch_path: str,
    knowledge_update_patch_path: str,
    review_summary_path: str,
) -> dict[str, Any]:
    return {
        "schema_version": "1",
        "artifact_type": "review_metadata",
        "result_id": result_id,
        "run_id": run_id,
        "experiment_id": experiment_id,
        "claim_id": None,
        "knowledge_id": None,
        "generated_at": generated_at,
        "proposed_claim_status": None,
        "required_human_review": True,
        "evidence_basis": [
            "agent_runs/AGENT-RUN-0090/metrics.json",
            "docs/reviews/quantum-znse-contract-transfer-benchmark.md",
            "data/quantum_dots/znse_no_refit_transfer_contract_fixture.yaml",
        ],
        "claim_target_file": None,
        "knowledge_target_file": None,
        "patch_artifacts": {
            "claim_patch": claim_update_patch_path,
            "knowledge_patch": knowledge_update_patch_path,
            "review_summary": review_summary_path,
        },
    }


def run_quantum_znse_contract_transfer_with_output(
    config_path: str | Path,
    output_dir: str | Path | None = None,
) -> ExperimentOutcome:
    """Package the ZnSe no-refit contract transfer as RESULT-0029."""
    config_path = Path(config_path).resolve()
    config = load_example_config(config_path)
    repo_root = find_repo_root(config_path)
    experiment_path = resolve_path(config_path, config["experiment_path"])
    hypothesis_path = resolve_path(config_path, config["hypothesis_path"])
    experiment = load_experiment(experiment_path)
    hypothesis = load_hypothesis(hypothesis_path)
    if experiment["hypothesis_id"] != hypothesis["id"]:
        raise ValueError(
            "Experiment hypothesis_id does not match loaded hypothesis id: "
            f"{experiment['hypothesis_id']} != {hypothesis['id']}"
        )

    task_id = str(config["task_id"])
    run_id = str(config["run_id"])
    result_id = str(config["result_id"])
    fixture_path = repo_root / FIXTURE_RELATIVE
    fixture = _load_yaml_mapping(fixture_path)
    metrics = _compute_metrics(fixture, repo_root=repo_root)
    generated_at = str(fixture["generated_at"])

    default_result_root = resolve_path(config_path, str(config["result_root"]))
    result_root = (
        Path(output_dir).resolve() / str(experiment["id"])
        if output_dir is not None
        else default_result_root
    )
    run_dir = result_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    result_path = run_dir / "result.yaml"
    report_path = run_dir / "report.md"
    metrics_path = run_dir / "metrics.json"
    claim_update_path = run_dir / "claim_update.md"
    claim_update_patch_path = run_dir / "claim_update.patch.md"
    knowledge_update_path = run_dir / "knowledge_update.md"
    knowledge_update_patch_path = run_dir / "knowledge_update.patch.md"
    review_summary_path = run_dir / "review_summary.md"
    review_metadata_path = run_dir / "review_metadata.yaml"
    gate_a_report_path = run_dir / "gate_a_report.md"

    task_file = task_path(repo_root, task_id)
    input_hashes = snapshot_input_files(
        run_dir=run_dir,
        repo_root=repo_root,
        input_files={
            "config": config_path,
            "fixture": fixture_path,
            "experiment": experiment_path,
            "hypothesis": hypothesis_path,
            "task": task_file,
        },
    )

    comparison_summary = _comparison_summary(fixture, metrics)
    verification = _verification_block(fixture, metrics)
    result_payload = {
        "result_id": result_id,
        "run_id": run_id,
        "experiment_id": experiment["id"],
        "title": "Quantum ZnSe no-refit contract transfer inconclusive control result",
        "hypothesis_id": hypothesis["id"],
        "task_id": task_id,
        "generated_at": generated_at,
        "engine_version": __version__,
        "git_commit": git_commit(repo_root),
        "command": COMMAND,
        "input_file_hashes": input_hashes,
        "code_reference": CODE_REFERENCE,
        "limitations": LIMITATIONS,
        "best_model_id": "model_inp_no_refit_confinement_power_law",
        "best_verdict": "INCONCLUSIVE",
        "review_tier": "AGENT_PUBLISHED",
        "agent_proposal_evaluation": {
            "review_tier_proposed": "AGENT_PUBLISHED",
            "best_verdict_proposed": "INCONCLUSIVE",
            "published_by": PUBLISHED_BY,
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
                "The workflow verifies the TASK-0914 frozen contract fixture, "
                "recomputes the AGENT-RUN-0090 metrics with the committed quantum "
                "transfer engine, and preserves the primary +0.04658368 eV margin "
                "as FAIL_TO_CLEAR_PREDECLARED_MARGIN under the frozen 0.05 eV rule."
            ),
            "followup_for_maintainer": (
                "Keep the AGENT_PUBLISHED qualifier explicit. Gate B next step: an "
                "independent agent can replay the recorded physics_lab.cli run command."
            ),
        },
        "verification": verification,
        "comparison_summary": comparison_summary,
        "uncertainty_summary": {
            "method": "deterministic_contract_control_comparison_no_predictive_interval",
            "observed_uncertainty": None,
            "reference_uncertainty": None,
            "combined_uncertainty": None,
            "z_score": None,
            "within_combined_uncertainty": None,
            "notes": "This no-refit transfer contract reports deterministic MAE/control margins, not calibrated predictive intervals.",
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

    metrics_payload = {
        "result_id": result_id,
        "run_id": run_id,
        "experiment_id": experiment["id"],
        "hypothesis_id": hypothesis["id"],
        "task_id": task_id,
        "source_agent_run_id": fixture["source_agent_run_id"],
        "contract": fixture["contract"],
        "expected_outcome": fixture["expected_outcome"],
        "engine_metrics": metrics,
    }

    _dump_yaml(result_path, result_payload)
    write_text_atomic(report_path, _render_report(result_id, fixture, metrics))
    write_text_atomic(
        metrics_path,
        json.dumps(metrics_payload, indent=2, sort_keys=True) + "\n",
    )
    write_text_atomic(claim_update_path, _render_no_promotion("Claim update", "claim", result_id))
    write_text_atomic(claim_update_patch_path, _render_patch_stub("Claim patch", result_id))
    write_text_atomic(
        knowledge_update_path,
        _render_no_promotion("Knowledge update", "knowledge", result_id),
    )
    write_text_atomic(
        knowledge_update_patch_path,
        _render_patch_stub("Knowledge patch", result_id),
    )
    write_text_atomic(review_summary_path, _render_review_summary(result_id, metrics))
    _dump_yaml(
        review_metadata_path,
        _review_metadata(
            result_id=result_id,
            run_id=run_id,
            experiment_id=str(experiment["id"]),
            generated_at=generated_at,
            claim_update_patch_path=relative_or_absolute(claim_update_patch_path, repo_root),
            knowledge_update_patch_path=relative_or_absolute(
                knowledge_update_patch_path, repo_root
            ),
            review_summary_path=relative_or_absolute(review_summary_path, repo_root),
        ),
    )
    write_text_atomic(
        gate_a_report_path,
        "\n".join(
            [
                f"# Gate A Report - {result_id}",
                "",
                f"- Artifact: `{relative_or_absolute(result_path, repo_root)}`",
                f"- Task: `{task_id}`",
                "- Proposed tier: `AGENT_PUBLISHED`",
                "- Verdict: `INCONCLUSIVE`",
                "- Gate A: `PASS`",
                "",
                "The workflow command is Gate-B-safe, records input hashes, verifies the frozen contract before scoring, and proposes no claim or knowledge promotion.",
                "",
            ]
        ),
    )

    return ExperimentOutcome(
        title=str(result_payload["title"]),
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(hypothesis["id"]),
        task_id=task_id,
        artifacts=ExperimentArtifacts(
            result_path=result_path,
            report_path=report_path,
            metrics_path=metrics_path,
            claim_update_path=claim_update_path,
            claim_update_patch_path=claim_update_patch_path,
            knowledge_update_path=knowledge_update_path,
            knowledge_update_patch_path=knowledge_update_patch_path,
            review_summary_path=review_summary_path,
            review_metadata_path=review_metadata_path,
        ),
        best_model_id="model_inp_no_refit_confinement_power_law",
        verdicts={"primary": "INCONCLUSIVE"},
        summary_lines=(
            "Primary margin versus best control: "
            f"{metrics['primary_transfer_margin_vs_best_control_ev']:.8f} eV",
            "Contract outcome: FAIL_TO_CLEAR_PREDECLARED_MARGIN",
        ),
    )
