"""Run the TASK-0958 AHS common-scheme geometric-midpoint diagnostic."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from physics_lab.engines.particle_common_scheme_baseline import run_from_config
from physics_lab.registry.agent_runs import validate_agent_run_payload


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "examples" / "benchmarks" / "particle_ahs_common_scheme_baseline.yaml"
DEFAULT_OUTPUT = ROOT / "agent_runs" / "AGENT-RUN-0091"

LIMITATIONS = [
    "Exactly six source-derived running Yukawa couplings and two charge sectors on one MS-bar-at-M_Z surface.",
    "The geometric-midpoint baseline is descriptive and zero-parameter; it is not a physical mass-generation model.",
    "The source does not provide a recoverable six-parameter covariance matrix, so no uncertainty significance is reported.",
    "The values were already committed and readable; fixture predeclaration is a procedural convention, not an enforceable blind.",
    "Sandbox diagnostic only; no Koide test, formula search, canonical RESULT, CLAIM, KNOW, PRED, or BSM interpretation.",
]


def _render_report(metrics: dict[str, Any]) -> str:
    rows = []
    for sector in metrics["sectors"]:
        rows.append(
            "| {sector_id} | {params} | {pred:.12g} | {obs:.12g} | {signed:.9f} | {factor:.6f} |".format(
                sector_id=sector["sector_id"],
                params=" / ".join(sector["ordered_parameters"]),
                pred=sector["predicted_middle_yukawa"],
                obs=sector["observed_middle_yukawa"],
                signed=sector["signed_residual_dex"],
                factor=sector["multiplicative_deviation_factor"],
            )
        )
    agg = metrics["aggregate"]
    return "\n".join(
        [
            "# AHS Common-Scheme Geometric-Midpoint Baseline",
            "",
            "- Task: `TASK-0958`",
            "- Sandbox run: `AGENT-RUN-0091`",
            "- Verdict: `INCONCLUSIVE`",
            f"- Source SHA-256: `{metrics['source']['sha256']}`",
            "",
            "## Method",
            "",
            "For each fixed charge sector, the zero-parameter baseline predicts the middle",
            "running Yukawa as `sqrt(y_light * y_heavy)`. The signed diagnostic is",
            "`log10(y_middle / predicted_middle)` in dex. The metric and sector ordering",
            "were frozen in the fixture before scoring; this is procedural rather than blind",
            "because the source rows were already committed and readable.",
            "",
            "## Results",
            "",
            "| sector | ordered parameters | predicted middle | observed middle | signed residual (dex) | deviation factor |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
            *rows,
            "",
            f"- Mean signed residual: `{agg['mean_signed_residual_dex']:.9f}` dex",
            f"- Mean absolute residual: `{agg['mean_absolute_residual_dex']:.9f}` dex",
            f"- Root-mean-square residual: `{agg['root_mean_square_residual_dex']:.9f}` dex",
            f"- Maximum absolute residual: `{agg['maximum_absolute_residual_dex']:.9f}` dex",
            "",
            "## Interpretation Boundary",
            "",
            "The two residuals are a descriptive reference for equal log spacing on one",
            "common-scheme surface. No quality threshold was predeclared, and two sectors",
            "cannot support generalization. Residual size is not statistical significance.",
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in LIMITATIONS],
            "",
            "## Output Routing",
            "",
            "- Canonical destination: sandbox `agent_runs/AGENT-RUN-0091/` plus review note.",
            "- Review tier: `none`; no canonical RESULT was created.",
            "- Gate A / Gate B: not attempted.",
            "- Claim / knowledge / prediction impact: none.",
            "",
        ]
    )


def _render_preflight(metrics: dict[str, Any]) -> str:
    source = metrics["source"]
    return "\n".join(
        [
            "# AGENT-RUN-0091 Preflight",
            "",
            f"- Pinned source checksum `{source['sha256']}` matched before scoring: PASS",
            "- Exact six positive Yukawa rows present: PASS",
            "- Common surface `running_yukawa`, `MS-bar`, `M_Z`, dimensionless: PASS",
            "- Metric, sector order, aggregates, and null threshold frozen in fixture: PASS",
            "- Procedural-not-blind disclosure present: PASS",
            "- No live fetch, source mutation, Koide metric, formula search, or canonical write: PASS",
            "",
        ]
    )


def _render_review(metrics: dict[str, Any]) -> str:
    agg = metrics["aggregate"]
    return "\n".join(
        [
            "# AGENT-RUN-0091 Review Summary",
            "",
            "The pinned AHS common-scheme surface produced two deterministic",
            "geometric-midpoint residuals. Aggregate descriptive values are",
            f"MAE `{agg['mean_absolute_residual_dex']:.9f}` dex and RMSE",
            f"`{agg['root_mean_square_residual_dex']:.9f}` dex.",
            "",
            "Verdict remains `INCONCLUSIVE`: no quality threshold, holdout, or",
            "generalization surface was defined. Preserve as sandbox benchmark memory.",
            "",
        ]
    )


def write_outputs(metrics: dict[str, Any], output_dir: Path) -> None:
    """Write the deterministic sandbox package and validate its manifest."""
    output_dir.mkdir(parents=True, exist_ok=True)
    run_id = str(metrics["agent_run_id"])
    if output_dir.name != run_id:
        raise ValueError(f"Output directory must end in {run_id}, got {output_dir}")
    relative_dir = Path("agent_runs") / run_id
    artifacts = {
        "metrics": (relative_dir / "metrics.json").as_posix(),
        "report": (relative_dir / "report.md").as_posix(),
        "limitations": (relative_dir / "limitations.md").as_posix(),
        "preflight": (relative_dir / "preflight.md").as_posix(),
        "review_summary": (relative_dir / "review_summary.md").as_posix(),
    }
    manifest = {
        "id": run_id,
        "campaign_profile_id": "particle-mass-relations",
        "task_id": "TASK-0958",
        "status": "REVIEW_READY",
        "sandbox_only": True,
        "created_by": {"contributor_id": "akutenyov", "agent_id": "codex"},
        "proposal_paths": {
            "hypothesis": "hypothesis_proposals/particle-mass-relations/HYP-PROPOSAL-0085-ahs-geometric-midpoint-baseline.yaml",
            "experiment": "experiment_proposals/particle-mass-relations/EXP-PROPOSAL-0085-ahs-geometric-midpoint-baseline.yaml",
        },
        "artifacts": artifacts,
        "preflight": {
            "passed": True,
            "checks": [
                {"name": "pinned_source_identity", "status": "PASS", "notes": "Source SHA-256 matched the frozen fixture before scoring."},
                {"name": "single_common_scheme_surface", "status": "PASS", "notes": "All six rows are dimensionless running Yukawas in MS-bar at M_Z."},
                {"name": "metric_contract_predeclared", "status": "PASS", "notes": "Metric, sector order, aggregates, and null quality threshold were frozen before scoring."},
                {"name": "procedural_not_blind", "status": "PASS", "notes": "The fixture states that committed values were visible and predeclaration is procedural."},
                {"name": "bounded_sandbox_routing", "status": "PASS", "notes": "No live fetch, fit, Koide metric, formula search, canonical result, claim, knowledge, or prediction write occurred."},
            ],
        },
        "limitations": LIMITATIONS,
        "verdict": "INCONCLUSIVE",
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": "Maintainer review of the bounded diagnostic; separate approval is required for any RESULT or broader benchmark.",
        },
    }
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "report.md").write_text(_render_report(metrics), encoding="utf-8")
    (output_dir / "limitations.md").write_text(
        "# Limitations\n\n" + "\n".join(f"- {item}" for item in LIMITATIONS) + "\n",
        encoding="utf-8",
    )
    (output_dir / "preflight.md").write_text(_render_preflight(metrics), encoding="utf-8")
    (output_dir / "review_summary.md").write_text(_render_review(metrics), encoding="utf-8")
    (output_dir / "agent_run.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
    )
    try:
        output_dir.resolve().relative_to(ROOT)
    except ValueError:
        validation_root = None
    else:
        validation_root = ROOT
    validate_agent_run_payload(
        manifest,
        source=output_dir / "agent_run.yaml",
        root=validation_root,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    config_path = args.config if args.config.is_absolute() else ROOT / args.config
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    metrics = run_from_config(config_path, root=ROOT)
    write_outputs(metrics, output_dir)
    display_path = output_dir.relative_to(ROOT) if output_dir.is_relative_to(ROOT) else output_dir
    print(
        f"INCONCLUSIVE: {display_path} "
        f"(MAE={metrics['aggregate']['mean_absolute_residual_dex']:.9f} dex)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
