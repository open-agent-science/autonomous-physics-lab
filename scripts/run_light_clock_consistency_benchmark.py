"""Run the deterministic TE-001 light-clock consistency benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from physics_lab.engines.light_clock import run_light_clock_benchmark  # noqa: E402
from physics_lab.registry.task_discovery import find_task_file  # noqa: E402

DEFAULT_OUTPUT = ROOT / "agent_runs" / "AGENT-RUN-0086"


def _task_path(task_id: str) -> Path:
    path = find_task_file(ROOT, task_id)
    if path is None:
        raise FileNotFoundError(f"No task file found for {task_id}")
    return path


INPUT_PATHS = {
    "task": _task_path("TASK-0847"),
    "planning_note": ROOT / "docs" / "notes" / "light-clock-consistency-check.md",
    "hypothesis": ROOT / "hypotheses" / "HYP-0019-light-clock-consistency.yaml",
    "experiment": ROOT / "experiments" / "EXP-0019-light-clock-consistency.yaml",
    "engine": ROOT / "physics_lab" / "engines" / "light_clock.py",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_payload() -> dict[str, Any]:
    payload = run_light_clock_benchmark()
    payload.update(
        {
            "task_id": "TASK-0847",
            "hypothesis_id": "HYP-0019",
            "experiment_id": "EXP-0019",
            "run_id": "AGENT-RUN-0086",
            "command": (
                "python scripts/run_light_clock_consistency_benchmark.py "
                "--out-dir agent_runs/AGENT-RUN-0086"
            ),
            "code_reference": "physics_lab/engines/light_clock.py",
            "input_file_hashes": {
                name: {
                    "path": path.relative_to(ROOT).as_posix(),
                    "sha256": _sha256(path),
                }
                for name, path in INPUT_PATHS.items()
            },
            "output_routing": {
                "canonical_destination": "agent_runs/AGENT-RUN-0086 plus review note",
                "review_tier": "none",
                "gate_a_status": "not_attempted_sandbox_first",
                "gate_b_status": "not_attempted",
                "claim_impact": "none",
                "knowledge_impact": "none",
            },
        }
    )
    return payload


def render_report(payload: dict[str, Any]) -> str:
    rows = []
    for case in payload["valid_beta_sweep"]:
        checks = {check["id"]: check["status"] for check in case["checks"]}
        rows.append(
            f"| {case['beta']:.2f} | {case['gamma']:.12g} | "
            f"{checks['LC-001']} | {checks['LC-002']} | {checks['LC-003']} | "
            f"{checks['LC-005']} | {case['verdict']} |"
        )
    invalid = ", ".join(
        f"beta={case['beta']}: {case['verdict']}"
        for case in payload["undefined_beta_cases"]
    )
    max_errors = payload["summary"]["check_max_errors"]
    return "\n".join(
        [
            "# TE-001 Light-Clock Consistency Benchmark",
            "",
            "- Task: `TASK-0847`",
            "- Experiment: `EXP-0019`",
            "- Sandbox run: `AGENT-RUN-0086`",
            f"- Verdict: `{payload['verdict']}`",
            "",
            "## Method",
            "",
            "The benchmark evaluates the frozen Special Relativity light-clock",
            "relations on beta values `0, 0.1, 0.5, 0.9, 0.99`. It rejects",
            "`beta >= 1` before numerical evaluation and checks a deliberately",
            "wrong Newtonian candidate as a regression control.",
            "",
            "Reference equations:",
            "",
            "- `T_rest = 2 L / c`",
            "- `gamma = 1 / sqrt(1 - beta^2)`",
            "- `T_moving = gamma T_rest`",
            "- `d/2 = sqrt(L^2 + (v T_moving / 2)^2)`",
            "",
            "## Per-Case Checks",
            "",
            "| beta | gamma | LC-001 | LC-002 | LC-003 | LC-005 | verdict |",
            "| ---: | ---: | --- | --- | --- | --- | --- |",
            *rows,
            "",
            f"`LC-004`: `{payload['low_velocity_check']['status']}`. "
            f"Undefined guard cases: {invalid}.",
            "",
            "## Metrics",
            "",
            f"- LC-001 maximum relative error: `{max_errors['LC-001']:.3e}`",
            f"- LC-002 maximum relative error: `{max_errors['LC-002']:.3e}`",
            f"- LC-003 maximum relative error: `{max_errors['LC-003']:.3e}`",
            "- Newtonian `T_moving = T_rest` control: "
            f"`{payload['summary']['newtonian_lc001_status']}` on LC-001, "
            f"overall `{payload['wrong_candidate_control']['verdict']}`.",
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in payload["limitations"]],
            "",
            "## Output Routing",
            "",
            "- Canonical destination: sandbox agent run plus review note.",
            "- Review tier: `none`.",
            "- Gate A: not attempted; this task keeps the first implementation",
            "  sandbox-first rather than publishing a canonical RESULT.",
            "- Gate B: not attempted.",
            "- Claim impact: none.",
            "- Knowledge impact: none.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    out_dir = args.out_dir
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload()
    (out_dir / "metrics.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "report.md").write_text(render_report(payload), encoding="utf-8")
    display_path = out_dir.relative_to(ROOT) if out_dir.is_relative_to(ROOT) else out_dir
    print(f"{payload['verdict']}: {display_path}")
    return 0 if payload["verdict"] == "CONSISTENT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
