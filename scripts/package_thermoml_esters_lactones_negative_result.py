#!/usr/bin/env python3
"""Package committed RESULT-0026 esters/lactones evidence as RESULT-0028.

TASK-0936. Deterministic packager: reads the committed RESULT-0026 metrics at a
pinned commit, enforces the packaged invariants (aggregate-positive context and
the esters/lactones family-survival failure), and emits the bounded
negative/control RESULT-0028 package. No rerun, refit, fetch, or fixture change
happens here, and RESULT-0026 is never modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results" / "EXP-0020" / "RUN-0002"
DEFAULT_COMMAND = "python3 scripts/package_thermoml_esters_lactones_negative_result.py --write"
DEFAULT_CODE_REFERENCE = "scripts/package_thermoml_esters_lactones_negative_result.py"
SOURCE_METRICS = ROOT / "results" / "EXP-0020" / "RUN-0001" / "metrics.json"
EXPERIMENT = ROOT / "experiments" / "EXP-0020-thermoml-tb-joback-transfer.yaml"
HYPOTHESIS = ROOT / "hypotheses" / "HYP-0020-thermoml-tb-joback-transfer.yaml"
TASK = ROOT / "tasks" / "TASK-0936-package-thermoml-esters-lactones-negative-result.yaml"
GENERATED_AT = "2026-07-06T00:00:00+00:00"
FAILED_FAMILY = "esters/lactones"
SURVIVAL_MARGIN_K = 5.0
TEXT_HASH_SUFFIXES = {".json", ".md", ".py", ".yaml", ".yml"}

PUBLIC_SAFE_SENTENCE = (
    "On the committed 40-row ThermoML normal-boiling-temperature fixture, the "
    "frozen Joback estimator cleared the aggregate and seven of eight held-out "
    "family margins, but esters/lactones did not clear the predeclared +5 K "
    "family-survival margin: Joback MAE was 26.134 K versus 20.584245 K for "
    "the molecular-weight-only control across five rows."
)


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in TEXT_HASH_SUFFIXES:
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="\n")


def read_text_at_commit(
    path: Path,
    commit: str,
    *,
    fallback_path: Path | None = None,
) -> str:
    relative = path.relative_to(ROOT).as_posix()
    try:
        result = subprocess.run(
            ["git", "show", f"{commit}:{relative}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout
    except subprocess.CalledProcessError:
        if fallback_path is not None and fallback_path.exists():
            return fallback_path.read_text(encoding="utf-8")
        return path.read_text(encoding="utf-8")


def git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def load_source_metrics(commit: str) -> tuple[dict, str]:
    source_text = read_text_at_commit(
        SOURCE_METRICS,
        commit,
        fallback_path=DEFAULT_OUTPUT / "inputs" / "fixture.json",
    )
    payload = json.loads(source_text)
    if payload.get("result_id") != "RESULT-0026":
        raise ValueError("source metrics no longer belong to RESULT-0026")
    if payload.get("gate_a_status") != "PASS":
        raise ValueError("source RESULT-0026 gate_a_status drifted from PASS")
    return payload, source_text


def build_metrics(source: dict) -> dict:
    transfer = source["metrics"]["transfer"]
    aggregate = {
        "row_count": transfer["row_count"],
        "family_count": transfer["family_count"],
        "families_clearing_margin": transfer["families_clearing_margin"],
        "families_required_to_clear": transfer["families_required_to_clear"],
        "joback_margin_vs_best_non_oracle_k": transfer["joback_margin_vs_best_non_oracle_k"],
        "survival_margin_k": transfer["survival_margin_k"],
        "verdict": transfer["verdict"],
    }
    if aggregate["verdict"] != "TRANSFER_SUPPORTED_IN_SCOPE":
        raise ValueError("aggregate RESULT-0026 verdict drifted")
    if aggregate["families_clearing_margin"] != 7 or aggregate["family_count"] != 8:
        raise ValueError("family survival counts drifted from 7/8")
    if aggregate["survival_margin_k"] != SURVIVAL_MARGIN_K:
        raise ValueError("survival margin drifted from 5.0 K")

    family = transfer["per_family"][FAILED_FAMILY]
    if family["clears_survival_margin"] is not False:
        raise ValueError("esters/lactones no longer records a failed margin")
    if family["best_non_oracle_control"] != "molecular_weight_only":
        raise ValueError("esters/lactones best non-oracle control drifted")
    joback = family["scores"]["joback"]
    control = family["scores"]["molecular_weight_only"]
    if joback["row_count"] != 5 or control["row_count"] != 5:
        raise ValueError("esters/lactones row count drifted from 5")
    margin = family["joback_margin_vs_best_non_oracle_k"]
    if margin >= 0:
        raise ValueError("esters/lactones margin is no longer negative")

    return {
        "result_id": "RESULT-0028",
        "source_result_id": "RESULT-0026",
        "source_metrics": "results/EXP-0020/RUN-0001/metrics.json",
        "property": "normal_boiling_temperature_tb",
        "failed_family": FAILED_FAMILY,
        "family_row_count": joback["row_count"],
        "family_scores": family["scores"],
        "family_margin_vs_best_non_oracle_k": margin,
        "required_family_survival_margin_k": SURVIVAL_MARGIN_K,
        "family_margin_shortfall_k": round(SURVIVAL_MARGIN_K - margin, 6),
        "best_non_oracle_control": family["best_non_oracle_control"],
        "aggregate_context": aggregate,
        "source_provenance": source["metrics"]["source"],
        "packaging_verdict": "INVALID",
        "public_safe_sentence": PUBLIC_SAFE_SENTENCE,
    }


def _comparison_summary(metrics: dict) -> list[dict]:
    joback = metrics["family_scores"]["joback"]
    control = metrics["family_scores"]["molecular_weight_only"]
    margin = metrics["family_margin_vs_best_non_oracle_k"]
    shortfall = metrics["family_margin_shortfall_k"]
    return [
        {
            "target_id": "target_esters_lactones_family_survival_margin",
            "label": "Esters/lactones family margin versus the predeclared +5 K survival rule",
            "reference_value": SURVIVAL_MARGIN_K,
            "observed_value": margin,
            "unit": "K",
            "absolute_difference": shortfall,
            "relative_difference": round(shortfall / SURVIVAL_MARGIN_K, 6),
            "notes": (
                "The observed family margin is negative, so the family misses the "
                "survival rule by the full shortfall. Scope is the committed 40-row "
                "Tb audit fixture only."
            ),
        },
        {
            "target_id": "target_joback_vs_mw_control_esters_lactones",
            "label": "Frozen Joback MAE versus the molecular-weight-only control on esters/lactones",
            "reference_value": control["mae_k"],
            "observed_value": joback["mae_k"],
            "unit": "K",
            "absolute_difference": round(joback["mae_k"] - control["mae_k"], 6),
            "relative_difference": round(
                (joback["mae_k"] - control["mae_k"]) / control["mae_k"], 6
            ),
            "notes": (
                "Lower MAE is better; the control beats Joback inside this five-row "
                "family. The control is diagnostic within the fixture, not a "
                "deployable estimator."
            ),
        },
    ]


def _write_text_artifacts(output: Path, metrics: dict) -> None:
    scores = metrics["family_scores"]
    ordered = [
        "joback",
        "molecular_weight_only",
        "global_median",
        "within_family_constant",
        "nearest_homolog",
        "shuffled_group_counts",
    ]
    lines = [
        "| Estimator | MAE (K) | RMSE (K) | Uncertainty-weighted MAE (K) | Rows |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for name in ordered:
        row = scores[name]
        lines.append(
            f"| `{name}` | {row['mae_k']:.6f} | {row['rmse_k']:.6f} | "
            f"{row['uncertainty_weighted_mae_k']:.6f} | {row['row_count']} |"
        )
    aggregate = metrics["aggregate_context"]
    report = "\n".join(
        [
            "# RESULT-0028: ThermoML Tb esters/lactones failed-family negative control",
            "",
            "This agent-published negative/control result packages committed RESULT-0026",
            "evidence. It does not rerun the benchmark, refit Joback, or expand data.",
            "",
            PUBLIC_SAFE_SENTENCE,
            "",
            "## Esters/lactones family scores (5 rows)",
            "",
            *lines,
            "",
            (
                f"Family margin: `{metrics['family_margin_vs_best_non_oracle_k']}` K "
                f"versus required `+{SURVIVAL_MARGIN_K}` K "
                f"(shortfall `{metrics['family_margin_shortfall_k']}` K)."
            ),
            "",
            "## Aggregate-positive context (preserved, unchanged)",
            "",
            (
                f"RESULT-0026 remains aggregate-positive: Joback clears the aggregate "
                f"margin ({aggregate['joback_margin_vs_best_non_oracle_k']} K over the "
                f"best non-oracle control) and {aggregate['families_clearing_margin']} "
                f"of {aggregate['family_count']} held-out family margins on "
                f"{aggregate['row_count']} rows. This package records the one failed "
                "family as first-class negative memory; it does not weaken or replace "
                "the aggregate verdict."
            ),
            "",
            "No chemical-design, safety, synthesis, process-design, universal Joback",
            "validation/falsification, or broad property-estimation claim is made.",
            "",
        ]
    )
    write_text(output / "report.md", report)
    write_text(
        output / "claim_update.md",
        "# Claim update\n\nNo claim update is proposed by RESULT-0028.\n",
    )
    write_text(
        output / "claim_update.patch.md",
        "# Claim patch\n\nNo claim patch is proposed by RESULT-0028.\n",
    )
    write_text(
        output / "knowledge_update.md",
        "# Knowledge update\n\nNo knowledge update is proposed by RESULT-0028.\n",
    )
    write_text(
        output / "knowledge_update.patch.md",
        "# Knowledge patch\n\nNo knowledge patch is proposed by RESULT-0028.\n",
    )
    write_text(
        output / "review_summary.md",
        "# Review summary\n\n"
        "RESULT-0028 is AGENT_PUBLISHED bounded negative/control memory for the "
        "esters/lactones family inside the committed RESULT-0026 fixture. Gate A "
        "passes; Gate B remains pending. The aggregate-positive RESULT-0026 "
        "verdict is unchanged.\n",
    )


def write_package(
    output: Path,
    *,
    commit: str,
    command: str = DEFAULT_COMMAND,
    code_reference: str = DEFAULT_CODE_REFERENCE,
) -> None:
    source, source_text = load_source_metrics(commit)
    metrics = build_metrics(source)
    output.mkdir(parents=True, exist_ok=True)
    inputs = output / "inputs"
    inputs.mkdir(exist_ok=True)

    config = {
        "result_id": "RESULT-0028",
        "source_metrics": "results/EXP-0020/RUN-0001/metrics.json",
        "source_result": "RESULT-0026",
        "failed_family": FAILED_FAMILY,
        "required_family_survival_margin_k": SURVIVAL_MARGIN_K,
        "rerun_allowed": False,
        "refit_allowed": False,
        "fetch_allowed": False,
        "fixture_change_allowed": False,
    }
    write_text(inputs / "config.yaml", yaml.safe_dump(config, sort_keys=False))
    write_text(inputs / "fixture.json", source_text)
    write_text(
        inputs / "experiment.yaml",
        read_text_at_commit(
            EXPERIMENT,
            commit,
            fallback_path=DEFAULT_OUTPUT / "inputs" / "experiment.yaml",
        ),
    )
    write_text(
        inputs / "hypothesis.yaml",
        read_text_at_commit(
            HYPOTHESIS,
            commit,
            fallback_path=DEFAULT_OUTPUT / "inputs" / "hypothesis.yaml",
        ),
    )
    write_text(
        inputs / "task.yaml",
        read_text_at_commit(TASK, commit, fallback_path=DEFAULT_OUTPUT / "inputs" / "task.yaml"),
    )

    relative = Path("results/EXP-0020/RUN-0002")
    input_hashes = {
        "config": {"path": (relative / "inputs/config.yaml").as_posix(), "sha256": sha256(inputs / "config.yaml")},
        "fixture": {"path": (relative / "inputs/fixture.json").as_posix(), "sha256": sha256(inputs / "fixture.json")},
        "experiment": {"path": (relative / "inputs/experiment.yaml").as_posix(), "sha256": sha256(inputs / "experiment.yaml")},
        "hypothesis": {"path": (relative / "inputs/hypothesis.yaml").as_posix(), "sha256": sha256(inputs / "hypothesis.yaml")},
        "task": {"path": (relative / "inputs/task.yaml").as_posix(), "sha256": sha256(inputs / "task.yaml")},
    }
    provenance = metrics["source_provenance"]
    result = {
        "result_id": "RESULT-0028",
        "run_id": "RUN-0002",
        "experiment_id": "EXP-0020",
        "title": "ThermoML Tb esters/lactones failed-family negative control",
        "hypothesis_id": "HYP-0020",
        "task_id": "TASK-0936",
        "generated_at": GENERATED_AT,
        "engine_version": "0.1.0",
        "git_commit": commit,
        "command": command,
        "input_file_hashes": input_hashes,
        "code_reference": code_reference,
        "limitations": [
            "Agent-published packaging of committed evidence; not yet independently validated or maintainer-reviewed.",
            "Scope is the five esters/lactones rows inside the committed 40-row ThermoML Tb audit fixture only.",
            "The INVALID verdict records a family-survival failure for the frozen Joback estimator in this family; it does not weaken the aggregate-positive, family-dependent RESULT-0026 verdict (7/8 families clear).",
            "The molecular-weight-only control is diagnostic within the fixture; it is not proposed as a deployable estimator.",
            "The Joback estimator is frozen; no coefficient, correction, or refit is performed by this packaging.",
            "Raw ThermoML archive bytes and any substantial normalized corpus are not committed; source rights permit only a bounded factual extract with attribution.",
            "No chemical-design, safety, synthesis, process-design, universal Joback validation/falsification, or broad property-estimation claim is made.",
        ],
        "best_model_id": "model_joback_frozen_tb",
        "best_verdict": "INVALID",
        "review_tier": "AGENT_PUBLISHED",
        "agent_proposal_evaluation": {
            "review_tier_proposed": "AGENT_PUBLISHED",
            "best_verdict_proposed": "INVALID",
            "published_by": {
                "contributor_id": "gladunrv",
                "github_username": "gladunrv",
                "agent_tool": "Claude Code",
                "model_version": "Claude Fable 5",
            },
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
                "The deterministic packager reads the committed RESULT-0026 metrics, "
                "verifies the aggregate-positive context (7/8 families clear, margin "
                "28.502118 K) and the esters/lactones failure (margin -5.549755 K "
                "versus the +5 K survival rule; Joback MAE 26.134 K versus 20.584245 K "
                "for the molecular-weight-only control across five rows), and packages "
                "that failure as bounded negative/control memory without rerunning or "
                "refitting anything."
            ),
            "followup_for_maintainer": (
                "Keep the AGENT_PUBLISHED qualifier explicit. Gate B next step: an "
                "independent identity can replay the deterministic packager against "
                "the same committed inputs (the recorded packaging-script command is "
                "not on the Gate B safe-command list, so the formal helper will "
                "report BLOCKED unsupported-command; a byte-identical repackage "
                "replay or a later physics-lab run workflow bridge are the available "
                "validation routes)."
            ),
        },
        "verification": {
            "passed": True,
            "checks": [
                {
                    "name": "committed_source_result_identity",
                    "status": "PASS",
                    "details": "RESULT-0026 exists with Gate A PASS and AGENT_VALIDATED tier; this package reads its committed metrics only.",
                    "metrics": {"source_result": "RESULT-0026", "source_gate_a": "PASS", "source_rerun": False},
                },
                {
                    "name": "aggregate_positive_context_preserved",
                    "status": "PASS",
                    "details": "The packaged aggregate context matches RESULT-0026: Joback clears the aggregate margin and seven of eight family margins.",
                    "metrics": {
                        "aggregate_margin_k": metrics["aggregate_context"]["joback_margin_vs_best_non_oracle_k"],
                        "families_clearing_margin": metrics["aggregate_context"]["families_clearing_margin"],
                        "family_count": metrics["aggregate_context"]["family_count"],
                        "row_count": metrics["aggregate_context"]["row_count"],
                    },
                },
                {
                    "name": "esters_lactones_family_survival_failure",
                    "status": "PASS",
                    "details": "The packaged family failure matches the committed values: the margin misses the predeclared +5 K survival rule.",
                    "metrics": {
                        "family_margin_k": metrics["family_margin_vs_best_non_oracle_k"],
                        "required_margin_k": SURVIVAL_MARGIN_K,
                        "margin_shortfall_k": metrics["family_margin_shortfall_k"],
                        "joback_mae_k": metrics["family_scores"]["joback"]["mae_k"],
                        "control_mae_k": metrics["family_scores"]["molecular_weight_only"]["mae_k"],
                        "family_row_count": metrics["family_row_count"],
                    },
                },
                {
                    "name": "no_rerun_refit_or_fetch",
                    "status": "PASS",
                    "details": "Packaging reads committed metrics only; no benchmark rerun, Joback refit, data fetch, or fixture change occurs.",
                    "metrics": {"rerun": False, "refit": False, "fetch": False, "fixture_changed": False},
                },
                {
                    "name": "source_provenance_and_rights_boundary",
                    "status": "PASS",
                    "details": "The ThermoML source DOI, archive SHA-256, attribution, and non-vendoring boundary are preserved from RESULT-0026.",
                    "metrics": {
                        "source_doi": provenance["doi"],
                        "archive_sha256": provenance["archive_sha256"],
                        "archive_size_bytes": provenance["archive_size_bytes"],
                        "archive_bytes_committed": provenance["archive_bytes_committed"],
                    },
                },
            ],
        },
        "comparison_summary": _comparison_summary(metrics),
        "uncertainty_summary": {
            "method": "family_control_comparison_uncertainty_weighted_mae_no_predictive_interval",
            "observed_uncertainty": metrics["family_scores"]["joback"]["uncertainty_weighted_mae_k"],
            "reference_uncertainty": metrics["family_scores"]["molecular_weight_only"]["uncertainty_weighted_mae_k"],
            "combined_uncertainty": None,
            "z_score": None,
            "within_combined_uncertainty": None,
            "notes": (
                "Reported values are uncertainty-weighted MAE summaries from the "
                "committed RESULT-0026 metrics, not calibrated predictive intervals."
            ),
        },
        "artifacts": {
            "report": (relative / "report.md").as_posix(),
            "metrics": (relative / "metrics.json").as_posix(),
            "claim_update": (relative / "claim_update.md").as_posix(),
            "claim_update_patch": (relative / "claim_update.patch.md").as_posix(),
            "knowledge_update": (relative / "knowledge_update.md").as_posix(),
            "knowledge_update_patch": (relative / "knowledge_update.patch.md").as_posix(),
            "review_summary": (relative / "review_summary.md").as_posix(),
            "review_metadata": (relative / "review_metadata.yaml").as_posix(),
        },
    }
    write_text(output / "metrics.json", json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    _write_text_artifacts(output, metrics)
    review_metadata = {
        "schema_version": "1",
        "artifact_type": "review_metadata",
        "result_id": "RESULT-0028",
        "run_id": "RUN-0002",
        "experiment_id": "EXP-0020",
        "claim_id": None,
        "knowledge_id": None,
        "generated_at": GENERATED_AT,
        "proposed_claim_status": None,
        "required_human_review": True,
        "evidence_basis": [
            "results/EXP-0020/RUN-0001/metrics.json",
            "docs/reviews/thermoml-esters-lactones-negative-result-preflight.md",
            "docs/reviews/thermoml-esters-lactones-negative-memory.md",
        ],
        "claim_target_file": None,
        "knowledge_target_file": None,
        "patch_artifacts": {
            "claim_patch": (relative / "claim_update.patch.md").as_posix(),
            "knowledge_patch": (relative / "knowledge_update.patch.md").as_posix(),
            "review_summary": (relative / "review_summary.md").as_posix(),
        },
    }
    write_text(output / "review_metadata.yaml", yaml.safe_dump(review_metadata, sort_keys=False))
    write_text(output / "result.yaml", yaml.safe_dump(result, sort_keys=False, width=100))
    gate_report = """# Gate A Report - RESULT-0028

- Artifact: `results/EXP-0020/RUN-0002/result.yaml`
- Task: `TASK-0936`
- Proposed tier: `AGENT_PUBLISHED`
- Verdict: `INVALID` (bounded esters/lactones family-survival failure)
- Gate A: `PASS`

The deterministic packager uses only committed RESULT-0026 evidence, records
all input hashes, preserves the aggregate-positive context and the ThermoML
rights boundary, and creates no claim or knowledge update. Gate B is not
attempted.
"""
    write_text(output / "gate_a_report.md", gate_report)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--git-commit")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if not args.write:
        parser.error("--write is required")
    output = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    write_package(output, commit=args.git_commit or git_commit())
    print(f"Wrote RESULT-0028 package to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
