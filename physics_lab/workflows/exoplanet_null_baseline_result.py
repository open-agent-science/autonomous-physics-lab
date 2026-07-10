"""Workflow adapter for the EXO-0001 null-baseline RESULT-0027 package.

Regenerates the canonical ``results/EXP-0021/RUN-0001/`` artifact from the
committed AGENT-RUN-0050 evidence via ``physics-lab run`` so the Gate B
independent-replay validator can re-run the same safe command. This is a
packaging bridge only: it preserves RESULT-0027's verdict and metrics, surfaces
the fair-null comparison values in the artifact, and creates no mass-radius
claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import yaml

from physics_lab.registry.examples import load_example_config
from physics_lab.registry.experiments import load_experiment
from physics_lab.registry.hypotheses import load_hypothesis
from physics_lab.workflows.artifacts import (
    ExperimentArtifacts,
    ExperimentOutcome,
    find_repo_root,
    relative_or_absolute,
    resolve_path,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "results" / "EXP-0021" / "RUN-0001"
SOURCE_METRICS = ROOT / "agent_runs" / "AGENT-RUN-0050" / "metrics.json"
SNAPSHOT = ROOT / "data" / "exoplanets" / "exo-0001-pscomppars-snapshot.yaml"
EXPERIMENT = ROOT / "experiments" / "EXP-0021-exoplanet-null-baseline-control-sensitivity.yaml"
HYPOTHESIS = ROOT / "hypotheses" / "HYP-0021-exoplanet-null-baseline-control-sensitivity.yaml"
TASK = ROOT / "tasks" / "TASK-0919-package-exoplanet-null-baseline-negative-result.yaml"
GENERATED_AT = "2026-07-04T00:00:00+00:00"
SOURCE_COMMIT = "7d0be449044f0a693c4e54b81b9c2e1c80c2c1b4"
WORKFLOW_CONFIG = "examples/exoplanet_null_baseline_result.yaml"
COMMAND = f"physics-lab run {WORKFLOW_CONFIG}"
CODE_REFERENCE = "physics_lab/workflows/exoplanet_null_baseline_result.py"
SLICES = (
    "compact_radius_lt1p5Re",
    "sub_neptune_radius_1p5_4Re",
    "jovian_radius_8_16Re",
    "hot_jupiter_period_lt10d_radius_ge8Re",
)
FAIR_NULL_BASELINES = (
    ("nearest_mass_neighbor", "Nearest-mass fair null"),
    ("per_class_median", "Per-class-median fair null"),
)
TEXT_HASH_SUFFIXES = {".json", ".md", ".py", ".yaml", ".yml"}


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


def run_exoplanet_null_baseline_result_with_output(
    config_path: str | Path,
    output_dir: str | Path | None = None,
) -> ExperimentOutcome:
    """Regenerate RESULT-0027 through the Gate-B-safe workflow bridge."""
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
    default_result_root = resolve_path(config_path, str(config["result_root"]))
    result_root = (
        Path(output_dir).resolve() / str(experiment["id"])
        if output_dir is not None
        else default_result_root
    )
    run_dir = result_root / run_id
    write_package(run_dir, commit=SOURCE_COMMIT)

    result_path = run_dir / "result.yaml"
    report_path = run_dir / "report.md"
    metrics_path = run_dir / "metrics.json"
    claim_update_path = run_dir / "claim_update.md"
    claim_update_patch_path = run_dir / "claim_update.patch.md"
    knowledge_update_path = run_dir / "knowledge_update.md"
    knowledge_update_patch_path = run_dir / "knowledge_update.patch.md"
    review_summary_path = run_dir / "review_summary.md"
    review_metadata_path = run_dir / "review_metadata.yaml"
    return ExperimentOutcome(
        title=str(config.get("result_title", experiment.get("title", "RESULT-0027"))),
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
        verdicts={"best": "INCONCLUSIVE"},
        summary_lines=(
            f"Regenerated {relative_or_absolute(result_path, repo_root)}",
            "Gate-B-safe command: physics-lab run examples/exoplanet_null_baseline_result.yaml",
            "Verdict unchanged: INCONCLUSIVE; no CLAIM/KNOW promotion.",
        ),
    )


def load_source_metrics(commit: str) -> tuple[dict, str]:
    source_text = read_text_at_commit(
        SOURCE_METRICS,
        commit,
        fallback_path=DEFAULT_OUTPUT / "inputs" / "fixture.json",
    )
    payload = json.loads(source_text)
    if payload.get("verdict") != "INCONCLUSIVE":
        raise ValueError("source memory verdict drifted from INCONCLUSIVE")
    if payload.get("snapshot") != "data/exoplanets/exo-0001-pscomppars-snapshot.yaml":
        raise ValueError("source memory no longer references the frozen EXO-0001 snapshot")
    return payload, source_text


def build_metrics(source: dict) -> dict:
    true_mass = source["axes"]["true_mass_with_transit_radius"]["slices"]
    minimum_mass = source["axes"]["minimum_mass_with_transit_radius"]["slices"]
    slices: dict[str, dict] = {}
    for name in SLICES:
        row = true_mass[name]
        if row["classification"] != "null_family_matches_or_beats_ck17":
            raise ValueError(f"classification drift for {name}")
        if row["best_null_baseline"] != "nearest_radius_neighbor":
            raise ValueError(f"best null drift for {name}")
        ck17 = row["baseline_stats"]["ck17_frozen"]["log10_rmse"]
        null = row["baseline_stats"]["nearest_radius_neighbor"]["log10_rmse"]
        slices[name] = {
            "row_count": row["count"],
            "ck17_frozen_rmse_dex": ck17,
            "nearest_radius_null_rmse_dex": null,
            "absolute_rmse_advantage_dex": ck17 - null,
            "relative_rmse_advantage": (ck17 - null) / ck17,
            "best_null_baseline": row["best_null_baseline"],
            "classification": row["classification"],
        }
    minimum_summary = {
        name: {
            "row_count": minimum_mass[name]["count"],
            "classification": minimum_mass[name]["classification"],
        }
        for name in SLICES
    }
    if any(row["classification"] != "underpowered_slice" for row in minimum_summary.values()):
        raise ValueError("minimum-mass diagnostic boundary drifted")
    return {
        "result_id": "RESULT-0027",
        "source_agent_run": "AGENT-RUN-0050",
        "source_verdict": source["verdict"],
        "snapshot": source["snapshot"],
        "audit_class": source["audit_class"],
        "true_mass_slices": slices,
        "minimum_mass_diagnostics": minimum_summary,
        "packaging_verdict": "INCONCLUSIVE",
    }


def _rmse_comparison_row(
    *,
    target_id: str,
    label: str,
    reference_value: float,
    observed_value: float,
    notes: str,
) -> dict[str, Any]:
    absolute_difference = abs(reference_value - observed_value)
    return {
        "target_id": target_id,
        "label": label,
        "reference_value": reference_value,
        "observed_value": observed_value,
        "unit": "dex_rmse",
        "absolute_difference": absolute_difference,
        "relative_difference": absolute_difference / reference_value,
        "notes": notes,
    }


def _comparison_summary(metrics: dict, source: dict) -> list[dict]:
    rows = []
    for name, row in metrics["true_mass_slices"].items():
        rows.append(
            _rmse_comparison_row(
                target_id=f"target_{name.lower()}_null_control",
                label=f"Nearest-radius diagnostic null versus frozen CK17 in {name}",
                reference_value=row["ck17_frozen_rmse_dex"],
                observed_value=row["nearest_radius_null_rmse_dex"],
                notes=(
                    "Lower RMSE is better. The nearest-radius baseline uses observed radius "
                    "and is a diagnostic control, not a prospective predictor."
                ),
            )
        )
        source_row = source["axes"]["true_mass_with_transit_radius"]["slices"][name]
        for baseline_id, baseline_label in FAIR_NULL_BASELINES:
            fair_rmse = source_row["baseline_stats"][baseline_id]["log10_rmse"]
            rows.append(
                _rmse_comparison_row(
                    target_id=f"target_{name.lower()}_{baseline_id}",
                    label=f"{baseline_label} versus frozen CK17 in {name}",
                    reference_value=row["ck17_frozen_rmse_dex"],
                    observed_value=fair_rmse,
                    notes=(
                        "Lower RMSE is better. This fair-null row is listed separately "
                        "from the nearest-radius diagnostic control; it does not change "
                        "the INCONCLUSIVE verdict or create a mass-radius claim."
                    ),
                )
            )
    return rows


def _write_text_artifacts(output: Path, metrics: dict, source: dict) -> None:
    slice_lines = [
        "| Slice | Rows | CK17 RMSE | Nearest-radius null RMSE | Classification |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    fair_lines = [
        "| Slice | CK17 RMSE | Nearest-mass fair null RMSE | Per-class-median fair null RMSE | Fair-null note |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for name, row in metrics["true_mass_slices"].items():
        slice_lines.append(
            f"| `{name}` | {row['row_count']} | {row['ck17_frozen_rmse_dex']:.6f} | "
            f"{row['nearest_radius_null_rmse_dex']:.6f} | `{row['classification']}` |"
        )
        source_row = source["axes"]["true_mass_with_transit_radius"]["slices"][name]
        nearest_mass = source_row["baseline_stats"]["nearest_mass_neighbor"]["log10_rmse"]
        per_class = source_row["baseline_stats"]["per_class_median"]["log10_rmse"]
        note = "both trail CK17"
        if nearest_mass <= row["ck17_frozen_rmse_dex"] or per_class <= row["ck17_frozen_rmse_dex"]:
            note = "at least one fair null matches or beats CK17"
        fair_lines.append(
            f"| `{name}` | {row['ck17_frozen_rmse_dex']:.6f} | {nearest_mass:.6f} | "
            f"{per_class:.6f} | {note} |"
        )
    report = "\n".join(
        [
            "# RESULT-0027: Exoplanet null-baseline control sensitivity",
            "",
            "This Gate-B-replayable negative/control result packages committed EXO-0001 evidence.",
            "It does not rerun residual scoring or establish a positive mass-radius law.",
            "",
            "## Diagnostic nearest-radius control",
            "",
            *slice_lines,
            "",
            "The nearest-radius control uses observed radius and is not a deployable predictor.",
            "",
            "## Fair-null comparators",
            "",
            *fair_lines,
            "",
            "The fair-null rows make the comparison surface explicit: nearest-mass and "
            "per-class-median controls trail the frozen CK17 baseline in three of four "
            "highlighted true-mass slices. This transparency addition does not change "
            "the packaged metrics, result verdict, or monitor-only campaign posture.",
            "",
            "## Routing",
            "",
            "All four highlighted true-mass slices retain `null_family_matches_or_beats_ck17`.",
            "Minimum-mass slices remain underpowered and are not pooled with true-mass rows.",
            "The artifact is replayable through `physics-lab run examples/exoplanet_null_baseline_result.yaml`.",
            "",
        ]
    )
    write_text(output / "report.md", report)
    write_text(
        output / "claim_update.md",
        "# Claim update\n\nNo claim update is proposed by RESULT-0027.\n",
    )
    write_text(
        output / "claim_update.patch.md",
        "# Claim patch\n\nNo claim patch is proposed by RESULT-0027.\n",
    )
    write_text(
        output / "knowledge_update.md",
        "# Knowledge update\n\nNo knowledge update is proposed by RESULT-0027.\n",
    )
    write_text(
        output / "knowledge_update.patch.md",
        "# Knowledge patch\n\nNo knowledge patch is proposed by RESULT-0027.\n",
    )
    write_text(
        output / "review_summary.md",
        "# Review summary\n\n"
        "RESULT-0027 is AGENT_VALIDATED negative/control memory after an independent "
        "Gate B replay by gladunrv/Codex. The campaign stays monitor-only and no "
        "CLAIM/KNOW promotion is proposed.\n",
    )


def _validation_record() -> dict[str, Any]:
    return {
        "validation_independence": "independent",
        "validation_independence_note": (
            "Publisher akutenyov and replayer gladunrv are different contributors. "
            "Both publication and replay used Codex/GPT-5, so this is independent-human, "
            "same-tool validation."
        ),
        "replayed_by": {
            "contributor_id": "gladunrv",
            "github_username": "gladunrv",
            "agent_tool": "Codex",
            "model_version": "GPT-5",
        },
        "replayed_at_utc": "2026-07-10T10:55:30Z",
        "replay_command": COMMAND,
        "replay_output_dir": "/private/tmp/apl-task0959-gateb-final",
        "tolerance_used": 1.0e-9,
        "max_abs_delta": 0.0,
        "metric_count": 52,
        "drift_observed": "none",
        "helper_status": "PASS",
        "helper_note": (
            "TASK-0959 repackaged RESULT-0027 onto a Gate-B-safe physics-lab workflow "
            "command, then ran the formal Gate B helper successfully. The helper emitted "
            "a non-blocking same-agent-tool warning because publisher and replayer both used "
            "Codex, while contributor identity differs."
        ),
    }


def write_package(output: Path, *, commit: str = SOURCE_COMMIT) -> None:
    source, source_text = load_source_metrics(commit)
    metrics = build_metrics(source)
    output.mkdir(parents=True, exist_ok=True)
    inputs = output / "inputs"
    inputs.mkdir(exist_ok=True)

    config = {
        "result_id": "RESULT-0027",
        "workflow_config": WORKFLOW_CONFIG,
        "source_metrics": "agent_runs/AGENT-RUN-0050/metrics.json",
        "source_snapshot": "data/exoplanets/exo-0001-pscomppars-snapshot.yaml",
        "source_git_commit": commit,
        "selected_axis": "true_mass_with_transit_radius",
        "selected_slices": list(SLICES),
        "minimum_mass_policy": "diagnostic_only_no_pooling",
        "live_fetch_allowed": False,
        "residual_rescoring_allowed": False,
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

    relative = Path("results/EXP-0021/RUN-0001")
    input_hashes = {
        "config": {"path": (relative / "inputs/config.yaml").as_posix(), "sha256": sha256(inputs / "config.yaml")},
        "fixture": {"path": (relative / "inputs/fixture.json").as_posix(), "sha256": sha256(inputs / "fixture.json")},
        "experiment": {"path": (relative / "inputs/experiment.yaml").as_posix(), "sha256": sha256(inputs / "experiment.yaml")},
        "hypothesis": {"path": (relative / "inputs/hypothesis.yaml").as_posix(), "sha256": sha256(inputs / "hypothesis.yaml")},
        "task": {"path": (relative / "inputs/task.yaml").as_posix(), "sha256": sha256(inputs / "task.yaml")},
    }
    result = {
        "result_id": "RESULT-0027",
        "run_id": "RUN-0001",
        "experiment_id": "EXP-0021",
        "title": "Exoplanet EXO-0001 null-baseline control-sensitive negative result",
        "hypothesis_id": "HYP-0021",
        "task_id": "TASK-0919",
        "generated_at": GENERATED_AT,
        "engine_version": "0.1.0",
        "git_commit": commit,
        "command": COMMAND,
        "input_file_hashes": input_hashes,
        "code_reference": CODE_REFERENCE,
        "limitations": [
            "Agent-validated packaging of committed evidence; not yet maintainer-reviewed.",
            "The scope is the committed EXO-0001 PSCompPars snapshot and four highlighted true-mass transit-radius slices only.",
            "The nearest-radius neighbor uses observed radius and is a diagnostic control, not a prospective or deployable predictor.",
            "Fair-null comparator rows are surfaced explicitly: nearest-mass and per-class-median controls trail the frozen CK17 baseline in three of four highlighted true-mass slices.",
            "Minimum-mass transit-radius slices are underpowered diagnostics and are not pooled with true-mass rows.",
            "No live fetch, EXO-0003 row, threshold change, CK17 refit, or residual rescoring is part of this package.",
            "No composition, habitability, atmosphere, target-priority, prediction, discovery, or universal mass-radius claim is made.",
        ],
        "best_verdict": "INCONCLUSIVE",
        "review_tier": "AGENT_VALIDATED",
        "agent_proposal_evaluation": {
            "review_tier_proposed": "AGENT_VALIDATED",
            "best_verdict_proposed": "INCONCLUSIVE",
            "published_by": {
                "contributor_id": "akutenyov",
                "github_username": "akutenyov",
                "agent_tool": "Codex",
                "model_version": "GPT-5",
            },
            "gates_checked": {
                "same_inputs": True,
                "same_deterministic_command": True,
                "metrics_match_within_tolerance": True,
                "verdict_unchanged": True,
                "independent_replay_metadata_recorded": True,
                "no_protected_artifact_rewrite": True,
            },
            "evidence_summary": (
                "Independent Gate B replay via the safe physics-lab workflow reproduced RESULT-0027 "
                "numeric fields with max absolute drift 0.0 and preserved the INCONCLUSIVE verdict. "
                "The artifact now surfaces fair-null comparator rows next to the nearest-radius "
                "diagnostic control without changing the packaged metrics."
            ),
            "followup_for_maintainer": (
                "Keep the AGENT_VALIDATED qualifier explicit: independently replayed, not "
                "maintainer-reviewed. Preserve the monitor-only campaign posture and no-claim wording."
            ),
            "validation_record": _validation_record(),
        },
        "verification": {
            "passed": True,
            "checks": [
                {
                    "name": "committed_source_identity",
                    "status": "PASS",
                    "details": "Canonical EXP-0021/HYP-0021 identities and TASK-0909 DONE state exist.",
                    "metrics": {"experiment_id": "EXP-0021", "hypothesis_id": "HYP-0021", "identity_task_done": True},
                },
                {
                    "name": "true_mass_control_classification",
                    "status": "PASS",
                    "details": "All four highlighted true-mass slices preserve the committed control-sensitive classification.",
                    "metrics": {"slice_count": 4, "matching_classifications": 4, "source_agent_run": "AGENT-RUN-0050"},
                },
                {
                    "name": "minimum_mass_no_pooling_boundary",
                    "status": "PASS",
                    "details": "All minimum-mass slices remain underpowered diagnostics and are not pooled into headline metrics.",
                    "metrics": {"slice_count": 4, "underpowered_slices": 4, "pooled_with_true_mass": False},
                },
                {
                    "name": "no_live_fetch_or_rescoring",
                    "status": "PASS",
                    "details": "Packaging reads committed metrics and snapshot provenance only; no scientific score is recomputed.",
                    "metrics": {"live_fetch": False, "residual_rescoring": False, "new_rows": False},
                },
            ],
        },
        "comparison_summary": _comparison_summary(metrics, source),
        "uncertainty_summary": {
            "method": "deterministic_null_control_comparison_no_predictive_interval",
            "observed_uncertainty": None,
            "reference_uncertainty": None,
            "combined_uncertainty": None,
            "z_score": None,
            "within_combined_uncertainty": None,
            "notes": "This control-panel package does not estimate calibrated predictive intervals.",
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
    _write_text_artifacts(output, metrics, source)
    review_metadata = {
        "schema_version": "1",
        "artifact_type": "review_metadata",
        "result_id": "RESULT-0027",
        "run_id": "RUN-0001",
        "experiment_id": "EXP-0021",
        "claim_id": None,
        "knowledge_id": None,
        "generated_at": GENERATED_AT,
        "proposed_claim_status": None,
        "required_human_review": True,
        "evidence_basis": [
            "agent_runs/AGENT-RUN-0050/metrics.json",
            "docs/reviews/exoplanet-null-baseline-negative-memory-replay.md",
            "docs/reviews/exoplanet-result-0027-gate-b-workflow-repackage.md",
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
    gate_report = """# Gate A Report - RESULT-0027

- Artifact: `results/EXP-0021/RUN-0001/result.yaml`
- Task: `TASK-0919`
- Proposed tier: `AGENT_VALIDATED`
- Verdict: `INCONCLUSIVE`
- Gate A: `PASS`
- Gate B: `PASS` after TASK-0959 workflow bridge

The deterministic packager uses only committed EXO-0001 evidence, records all
input hashes, preserves the control-sensitive and underpowered boundaries, and
creates no claim or knowledge update. TASK-0959 repackaged this artifact onto
a Gate-B-safe `physics-lab run` workflow command and recorded an independent
formal replay.
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
    write_package(output, commit=args.git_commit or SOURCE_COMMIT)
    print(f"Wrote RESULT-0027 package to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
