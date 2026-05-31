#!/usr/bin/env python3
"""Campaign output scorecard (TASK-0498).

Reports durable scientific-memory throughput per campaign — committed RESULT and
PRED artifacts by verdict/registry-status and review tier, plus sandbox
agent-run counts — so strategy agents and the Scientific Campaign Director can
steer by output rather than raw task/PR activity.

Descriptive only: it counts committed artifacts. It never promotes claims,
edits review tiers, or ranks scientific truth.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _fmt(counts: dict) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{k}:{v}" for k, v in sorted(counts.items()))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser


def main() -> int:
    from physics_lab.registry.campaign_scorecard import build_scorecard

    args = build_parser().parse_args()
    report = build_scorecard(args.root)

    if args.json:
        payload = {
            "totals": report.totals(),
            "campaigns": [
                {
                    "campaign_id": c.campaign_id,
                    "status": c.status,
                    "results": c.result_count,
                    "result_verdicts": c.result_verdicts,
                    "result_tiers": c.result_tiers,
                    "predictions": c.prediction_count,
                    "prediction_statuses": c.prediction_statuses,
                    "prediction_tiers": c.prediction_tiers,
                    "sandbox_agent_runs": c.sandbox_agent_runs,
                }
                for c in report.campaigns
            ],
            "repo_results": {
                "count": report.repo_result_count,
                "verdicts": report.repo_result_verdicts,
                "tiers": report.repo_result_tiers,
            },
            "repo_claims": report.repo_claims,
            "repo_knowledge": report.repo_knowledge,
            "unmapped_results": list(report.unmapped_results),
        }
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        return 0

    t = report.totals()
    sys.stdout.write("Campaign output scorecard\n")
    sys.stdout.write(
        f"- totals: results {t['results_total']} "
        f"({t['results_mapped_to_campaign']} mapped to a campaign), "
        f"predictions {t['predictions']}, sandbox runs {t['sandbox_agent_runs']}, "
        f"claims {t['claims']}, knowledge {t['knowledge']}\n"
    )
    sys.stdout.write(
        f"- repo-wide results: verdicts [{_fmt(report.repo_result_verdicts)}] "
        f"tiers [{_fmt(report.repo_result_tiers)}]\n"
    )
    sys.stdout.write(f"- claims by status: {_fmt(report.repo_claims)}\n\n")

    sys.stdout.write("Per-campaign durable output (results from profile current_results) + sandbox:\n")
    for c in report.campaigns:
        if not (c.result_count or c.prediction_count or c.sandbox_agent_runs):
            continue
        sys.stdout.write(
            f"- {c.campaign_id} [{c.status}]: "
            f"RESULT {c.result_count} (verdicts [{_fmt(c.result_verdicts)}], tiers [{_fmt(c.result_tiers)}]) | "
            f"PRED {c.prediction_count} (status [{_fmt(c.prediction_statuses)}]) | "
            f"sandbox {c.sandbox_agent_runs}\n"
        )

    if report.unmapped_results:
        sys.stdout.write(
            f"\nCoverage: {len(report.unmapped_results)} committed results are not "
            "referenced by any campaign profile's current_results, so they are not "
            "attributed to a campaign (counted only in repo-wide totals). Per-campaign "
            "result attribution reflects curated current_results, not a full census.\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
