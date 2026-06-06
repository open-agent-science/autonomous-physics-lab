"""Nuclear F2 independent replay and control ledger (TASK-0612).

TASK-0553 found a large F2 finer-taxonomy diagnostic improvement on the committed
NMD-0003 measured surface but kept the lane diagnostic-only because the
controls-first survival margin was not cleared. This module independently replays
the committed F2 controls-first scoring (committed code, committed data, the
frozen NMD-0003 stratified gate) and verifies that it reproduces the committed
`AGENT-RUN-0060` metrics exactly, then records a control ledger so a later task can
decide whether F2 deserves promotion preflight, deeper ablation, or explicit
do-not-promote memory.

It does not fetch live data, refit anything new, score the post-AME2020 reveal,
or create PRED / reveal-score / RESULT / CLAIM / KNOW or discovery wording. If the
replay does not reproduce the committed metrics, it reports
`BLOCKED_REPLAY_MISMATCH` and stops before any interpretation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.run_nuclear_f2_controls_first_scoring import run_f2_controls_first_scoring

COMMITTED_RUN_ID = "AGENT-RUN-0060"
DEFAULT_COMMITTED_METRICS = Path("agent_runs") / COMMITTED_RUN_ID / "metrics.json"
CANDIDATE_LANE_ID = "candidate_f2_finer_taxonomy"
SURFACES = ("train_loo", "validation_holdout", "full_known")


def run_nuclear_f2_independent_replay(
    *, committed_metrics_path: Path | str = DEFAULT_COMMITTED_METRICS
) -> dict[str, Any]:
    """Run the deterministic TASK-0612 F2 independent replay and control ledger."""
    committed_metrics_path = Path(committed_metrics_path)

    # json round-trip normalizes tuples/whitespace so the comparison is structural.
    fresh = json.loads(json.dumps(run_f2_controls_first_scoring()))
    committed = json.loads(committed_metrics_path.read_text(encoding="utf-8"))

    mismatches = _diff_paths(committed, fresh)
    replay_match = not mismatches
    surface_verification = _surface_verification(committed=committed, fresh=fresh)
    surfaces_match = all(item["matches"] for item in surface_verification.values())

    replay_verdict = "REPLAY_MATCH" if (replay_match and surfaces_match) else "BLOCKED_REPLAY_MISMATCH"

    result: dict[str, Any] = {
        "task_id": "TASK-0612",
        "benchmark_id": "nuclear-f2-independent-replay-and-control-ledger",
        "input_references": {
            "committed_metrics": committed_metrics_path.as_posix(),
            "committed_run_id": COMMITTED_RUN_ID,
            "source_scoring_task": "TASK-0553",
            "controls_first_review": "docs/reviews/nuclear-f2-controls-first-scoring.md",
            "frozen_gate": "data/nuclear_masses/nmd-0003-stratified-baseline-gate.yaml",
        },
        "replay_check": {
            "full_metrics_deep_equal": replay_match,
            "candidate_surface_metrics_match": surfaces_match,
            "mismatch_count": len(mismatches),
            "mismatch_paths": mismatches[:50],
            "candidate_surface_verification": surface_verification,
        },
        "replay_verdict": replay_verdict,
    }

    if replay_verdict == "BLOCKED_REPLAY_MISMATCH":
        # Stop before any interpretation: do not emit a control ledger or verdict echo.
        result["control_ledger"] = {
            "status": "not_interpreted_due_to_replay_mismatch",
            "reason": (
                "The independent replay did not reproduce the committed AGENT-RUN-0060 "
                "metrics. Resolve the mismatch before interpreting F2."
            ),
        }
        result["limitations"] = [
            "Replay mismatch: committed code/data did not reproduce the committed metrics "
            "in this environment; no F2 interpretation is recorded.",
        ]
        result["output_routing"] = _routing(
            verdict="BLOCKED_REPLAY_MISMATCH",
            blocker="independent replay did not reproduce AGENT-RUN-0060 metrics",
        )
        return result

    result["control_ledger"] = _control_ledger(committed)
    result["limitations"] = [
        "Retrospective AME2020 measured-row replay only; no post-AME2020 reveal scoring.",
        "Replays committed TASK-0553 code and data under the frozen NMD-0003 stratified "
        "gate; it introduces no new fit, feature family, or label.",
        "F2 remains diagnostic_only: the controls-first survival margin is not cleared.",
        "Sandbox replay evidence only; no PRED, reveal score, RESULT, CLAIM, KNOW, or "
        "discovery wording is created.",
    ]
    result["output_routing"] = _routing(verdict="REPLAY_MATCH", blocker="none")
    return result


# --------------------------------------------------------------------------- #
# Comparison
# --------------------------------------------------------------------------- #


def _diff_paths(expected: Any, actual: Any, *, path: str = "") -> list[str]:
    """Return dotted paths where ``actual`` differs from ``expected``."""
    if isinstance(expected, dict) and isinstance(actual, dict):
        paths: list[str] = []
        for key in sorted(set(expected) | set(actual)):
            child = f"{path}.{key}" if path else str(key)
            if key not in expected:
                paths.append(f"{child} (unexpected)")
            elif key not in actual:
                paths.append(f"{child} (missing)")
            else:
                paths.extend(_diff_paths(expected[key], actual[key], path=child))
        return paths
    if isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            return [f"{path} (length {len(expected)} != {len(actual)})"]
        paths = []
        for index, (exp_item, act_item) in enumerate(zip(expected, actual)):
            paths.extend(_diff_paths(exp_item, act_item, path=f"{path}[{index}]"))
        return paths
    if expected != actual:
        return [f"{path} ({expected!r} != {actual!r})"]
    return []


def _surface_verification(*, committed: dict[str, Any], fresh: dict[str, Any]) -> dict[str, Any]:
    committed_lane = committed["lanes"][CANDIDATE_LANE_ID]
    fresh_lane = fresh["lanes"][CANDIDATE_LANE_ID]
    verification: dict[str, Any] = {}
    for surface in SURFACES:
        committed_metrics = {
            "baseline_mae_mev": committed_lane["baseline"][surface]["mae_mev"],
            "baseline_rmse_mev": committed_lane["baseline"][surface]["rmse_mev"],
            "corrected_mae_mev": committed_lane["corrected"][surface]["mae_mev"],
            "corrected_rmse_mev": committed_lane["corrected"][surface]["rmse_mev"],
            "mae_improvement_mev": committed_lane["improvement_vs_baseline"][surface][
                "mae_improvement_mev"
            ],
        }
        fresh_metrics = {
            "baseline_mae_mev": fresh_lane["baseline"][surface]["mae_mev"],
            "baseline_rmse_mev": fresh_lane["baseline"][surface]["rmse_mev"],
            "corrected_mae_mev": fresh_lane["corrected"][surface]["mae_mev"],
            "corrected_rmse_mev": fresh_lane["corrected"][surface]["rmse_mev"],
            "mae_improvement_mev": fresh_lane["improvement_vs_baseline"][surface][
                "mae_improvement_mev"
            ],
        }
        verification[surface] = {
            "committed": committed_metrics,
            "replayed": fresh_metrics,
            "matches": committed_metrics == fresh_metrics,
        }
    return verification


# --------------------------------------------------------------------------- #
# Control ledger
# --------------------------------------------------------------------------- #


def _control_ledger(committed: dict[str, Any]) -> dict[str, Any]:
    contract = committed["controls_first_contract"]
    decision = committed["decision"]
    lanes = committed["lanes"]
    controls = list(contract["controls"])

    control_rows = {
        control_id: {
            "full_known_mae_improvement_mev": lanes[control_id]["improvement_vs_baseline"][
                "full_known"
            ]["mae_improvement_mev"],
            "validation_holdout_mae_improvement_mev": lanes[control_id][
                "improvement_vs_baseline"
            ]["validation_holdout"]["mae_improvement_mev"],
        }
        for control_id in controls
    }
    best_control_id = max(
        controls,
        key=lambda control_id: control_rows[control_id]["full_known_mae_improvement_mev"],
    )

    return {
        "candidate_lane": CANDIDATE_LANE_ID,
        "controls": controls,
        "control_full_known_improvements_mev": control_rows,
        "candidate_full_known_mae_improvement_mev": decision[
            "candidate_full_known_mae_improvement_mev"
        ],
        "best_control_id": best_control_id,
        "best_control_full_known_mae_improvement_mev": decision[
            "best_control_full_known_mae_improvement_mev"
        ],
        "survival_margin_rule_mev": contract["survival_margin_mev"],
        "candidate_minus_best_control_mev": decision[
            "candidate_minus_best_control_full_known_mae_improvement_mev"
        ],
        "survival_margin_clears": decision["survival_margin_clears"],
        "validation_holdout_regresses": decision["validation_holdout_regresses"],
        "f2_scoring_verdict": committed["verdict"],
        "why_diagnostic_only": (
            "The F2 candidate improves the full-known surface by "
            f"{decision['candidate_full_known_mae_improvement_mev']} MeV, but the best "
            f"control ({best_control_id}) already explains "
            f"{decision['best_control_full_known_mae_improvement_mev']} MeV, leaving a "
            f"survival margin of {decision['candidate_minus_best_control_full_known_mae_improvement_mev']} "
            f"MeV below the {contract['survival_margin_mev']} MeV controls-first threshold. "
            "F2 is therefore control-dominated and stays diagnostic-only: no promotion, "
            "prediction, reveal score, or claim is authorized by this replay."
        ),
    }


def _routing(*, verdict: str, blocker: str) -> dict[str, Any]:
    return {
        "task_verdict": verdict,
        "canonical_destination": [
            "agent_runs/AGENT-RUN-0067/metrics.json",
            "agent_runs/AGENT-RUN-0067/report.md",
            "docs/reviews/nuclear-f2-independent-replay-and-control-ledger.md",
        ],
        "review_tier": "none",
        "gate_a_status": "not_attempted",
        "gate_b_status": "not_applicable",
        "claim_impact": "none",
        "knowledge_impact": "none",
        "result_impact": "no RESULT artifact created",
        "publication_blocker": blocker,
    }
