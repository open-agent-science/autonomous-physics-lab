#!/usr/bin/env python3
"""Run the TASK-0838 MD-0002 disjoint A-site cation-family transfer benchmark.

Deterministic: re-running with the same committed inputs produces identical
metrics. Writes ``metrics.json`` (and, with ``--write-report``, ``report.md``)
into the output directory.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default="examples/benchmarks/materials_md0002_formation_energy.yaml",
        help="Frozen TASK-0703 baseline benchmark config (reused for the source binding).",
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Also render a human-readable report.md alongside metrics.json.",
    )
    return parser


def _render_report(metrics: dict) -> str:
    lines: list[str] = []
    lines.append(f"# {metrics['agent_run_id']} Report")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(
        "`TASK-0838` is a BOUNDED computed-DFT transfer benchmark. It asks whether "
        "the frozen RESULT-0021 baseline model (the exact unordered non-oxygen "
        "cation-pair train-mean of `formation_energy_per_atom`, with a global-train-"
        "mean fallback) transfers across a chemically-disjoint A-site cation-family "
        "split of the committed MD-0002 stable ternary-oxide slice. The judge is "
        "computed-DFT (Materials Project, CC BY 4.0); this is a model-vs-model "
        "generalization benchmark, not a discovery, material-design-law, property-"
        "prediction, or device statement."
    )
    lines.append("")
    lines.append("## Frozen model and predeclared split")
    lines.append("")
    lines.append(
        f"Frozen model under test: `{metrics['frozen_model_under_test']['model_id']}` "
        f"(descriptor `{metrics['frozen_model_under_test']['descriptor']}`), imported "
        "unchanged from the baseline engine. The model and descriptor were fixed "
        "before any transfer error was read."
    )
    fc = metrics["dataset_summary"]["family_counts"]
    lines.append("")
    lines.append(
        "Disjoint A-site cation-family partition (route selected by the TASK-0817 "
        f"scout): `alkali_transition` = {fc['alkali_transition']} rows, "
        f"`alkaline_earth_transition` = {fc['alkaline_earth_transition']} rows. The "
        "two families share no A-site cation, so leakage is none by construction."
    )
    lines.append("")
    lines.append("## Predeclared pass/fail")
    lines.append("")
    pf = metrics["predeclared_pass_fail"]
    lines.append(
        f"Metric: {pf['metric']}. Rule: {pf['rule']} Controls: "
        f"{', '.join(pf['controls'])}."
    )
    lines.append("")
    lines.append("## Transfer error vs controls")
    lines.append("")
    lines.append(
        "| Direction | Frozen MAE | null | per-class-median | shuffled | best control | margin | clears? |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for d in metrics["transfer_directions"]:
        c = d["controls"]
        lines.append(
            f"| hold out `{d['holdout_family']}` | {d['frozen_model_holdout_mae']} | "
            f"{c['null_global_mean']['holdout_mae']} | "
            f"{c['per_class_median']['holdout_mae']} | "
            f"{c['shuffled_cation_pair']['holdout_mae']} | "
            f"`{d['best_control_id']}` {d['best_control_holdout_mae']} | "
            f"{d['margin_over_best_control_eV_per_atom']} | "
            f"{'yes' if d['clears_margin_over_best_control'] else 'no'} |"
        )
    lines.append("")
    for d in metrics["transfer_directions"]:
        lines.append(
            f"- Holding out `{d['holdout_family']}`: "
            f"{d['holdout_rows_falling_back_to_global_mean']} of {d['holdout_count']} "
            "held-out rows fall back to the global train mean (the families share no "
            "cation pair), so the frozen model cannot use any learned pair on the "
            "held-out family."
        )
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    lines.append(
        f"`{metrics['verdict']}` -- {metrics['transfer_summary']['transfer_outcome']}. "
        "The frozen cation-pair advantage does NOT transfer across a disjoint A-site "
        "cation family on this computed-DFT slice. This is the honest negative the "
        "task accepts; no refit, feature add, or split change was made to rescue it."
    )
    lines.append("")
    lines.append("## Output routing")
    lines.append("")
    routing = metrics["output_routing"]
    lines.append(f"- Canonical destination: {routing['canonical_destination']}")
    lines.append(f"- Review tier: {routing['review_tier']}")
    lines.append(f"- Gate A: {routing['gate_a_status']}")
    lines.append(f"- Gate B: {routing['gate_b_status']}")
    lines.append(f"- Claim impact: {routing['claim_impact']}")
    lines.append(f"- Knowledge impact: {routing['knowledge_impact']}")
    lines.append(f"- Publication blocker: {routing['publication_blocker']}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    from physics_lab.engines.materials_md0002_transfer import (
        run_materials_md0002_transfer_benchmark,
    )

    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics = run_materials_md0002_transfer_benchmark(Path(args.config))
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Metrics: {output_dir / 'metrics.json'}")
    if args.write_report:
        (output_dir / "report.md").write_text(_render_report(metrics), encoding="utf-8")
        print(f"Report: {output_dir / 'report.md'}")
    print(f"Verdict: {metrics['verdict']}")
    print(f"Transfer outcome: {metrics['transfer_summary']['transfer_outcome']}")
    for direction in metrics["transfer_directions"]:
        print(
            f"  {direction['direction_id']}: frozen MAE="
            f"{direction['frozen_model_holdout_mae']} "
            f"best control={direction['best_control_id']} "
            f"({direction['best_control_holdout_mae']}) "
            f"margin={direction['margin_over_best_control_eV_per_atom']} "
            f"clears={direction['clears_margin_over_best_control']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
