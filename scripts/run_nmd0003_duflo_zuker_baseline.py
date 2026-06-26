#!/usr/bin/env python3
"""Run TASK-0823 DZ10 published-equation diagnostic benchmark."""

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
        "--output-dir",
        default="agent_runs/AGENT-RUN-0078",
        help="Directory for metrics.json and report.md.",
    )
    parser.add_argument(
        "--review-path",
        default="docs/reviews/nmd0003-duflo-zuker-structured-baseline.md",
        help="Review note path to write.",
    )
    return parser


def main() -> int:
    from physics_lab.engines.nmd0003_duflo_zuker_baseline import (
        run_nmd0003_duflo_zuker_baseline,
    )

    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics = run_nmd0003_duflo_zuker_baseline()
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report = _render_report(metrics)
    (output_dir / "report.md").write_text(report, encoding="utf-8")
    review_path = Path(args.review_path)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(report, encoding="utf-8")
    print(f"TASK-0823 metrics: {output_dir / 'metrics.json'}")
    print(f"TASK-0823 review: {review_path}")
    print(f"Verdict: {metrics['verdict']}")
    print(f"Routing: {metrics['output_routing']['routing_decision']}")
    return 0


def _render_report(metrics: dict[str, object]) -> str:
    comparison = metrics["comparison"]
    surfaces = metrics["surfaces"]
    controls = metrics["controls"]
    routing = metrics["output_routing"]
    return f"""# TASK-0823 DZ10 Published-Equation Diagnostic Benchmark

Sandbox diagnostic for a deterministic 10-term DZ10 published-equation nuclear
mass baseline on the committed NMD-0003 training surface and the reviewed
post-AME2020 retrospective holdout.

This follows the published equations in Mendoza-Temis, Hirsch, and Zuker
(arXiv:0912.0882), but it is not a parity run of the unavailable AMDC/archival
DZ10 code. This PR therefore does not complete `TASK-0823`; the task remains
`READY` for a future true published-code or published-fixture parity
implementation.

## Inputs

- Training dataset: `data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml`
- Retrospective holdout: `data/nuclear_masses/post_ame2020_holdout.yaml`
- Inherited baseline: `results/EXP-0012/RUN-0001/result.yaml`
- Post-AME2020 rows used for fitting: `0`
- Code reference: `{metrics['gate_b_replay']['code_reference']}`
- Engine version: `{metrics['engine_version']}`
- Git commit at generation: `{metrics['gate_b_replay']['git_commit_at_generation']}`

## Metrics

| surface | MAE (MeV) | RMSE (MeV) | count |
| --- | ---: | ---: | ---: |
| NMD-0003 fit surface | {surfaces['nmd0003_fit_surface']['mae_mev']:.6f} | {surfaces['nmd0003_fit_surface']['rmse_mev']:.6f} | {surfaces['nmd0003_fit_surface']['count']} |
| post-AME2020 holdout | {surfaces['post_ame2020_holdout']['mae_mev']:.6f} | {surfaces['post_ame2020_holdout']['rmse_mev']:.6f} | {surfaces['post_ame2020_holdout']['count']} |

## Controls

| control | post-AME2020 MAE (MeV) |
| --- | ---: |
| inherited RESULT-0015 frozen | {controls['inherited_result0015_frozen']['post_ame2020_holdout']['mae_mev']:.6f} |
| NMD-0003 train-fitted liquid drop | {controls['nmd0003_train_fitted_liquid_drop']['post_ame2020_holdout']['mae_mev']:.6f} |
| smooth-A quadratic control | {controls['smooth_a_quadratic_control']['post_ame2020_holdout']['mae_mev']:.6f} |

Best control: `{metrics['best_control_on_post_ame2020_holdout']['control_id']}`
with MAE `{metrics['best_control_on_post_ame2020_holdout']['mae_mev']:.6f}` MeV.
The DZ10 published-equation variant margin vs best control is
`{comparison['margin_vs_best_control_mev']:.6f}` MeV against the predeclared
`{comparison['survival_margin_mev']:.6f}` MeV survival margin.

## Verdict

`{metrics['verdict']}`

Diagnostic outcome: `{comparison['diagnostic_outcome']}`.

Task completion: `{metrics['task_completion']['completes_task']}`. Reason:
{metrics['task_completion']['reason']}

## Output Routing

- Verdict: `{metrics['verdict']}`
- Canonical destination: {routing['canonical_destination']}
- Review tier: `{routing['review_tier']}`
- Gate A status: `{routing['gate_a_status']}`
- Gate B status: `{routing['gate_b_status']}`
- Claim impact: {routing['claim_impact']}
- Knowledge impact: {routing['knowledge_impact']}
- Routing decision: `{routing['routing_decision']}`

## Limitations

- This follows published DZ10 equations, but is not an archival DZ10-code parity
  reproduction.
- The post-AME2020 surface is retrospective time-split evidence, not a strict
  blind reveal.
- The model is fitted by ordinary least squares on the committed NMD-0003 train
  rows in the paper's `N,Z >= 8` domain only.
- No `PRED`, `CLAIM`, `KNOW`, or canonical `RESULT` artifact is created.
"""


if __name__ == "__main__":
    raise SystemExit(main())
