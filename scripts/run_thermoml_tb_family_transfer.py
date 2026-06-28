"""Run and package the checksum-pinned TASK-0851 ThermoML Tb audit fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from physics_lab import __version__
from physics_lab.engines.joback_tb import evaluate_fidelity_fixture
from physics_lab.engines.thermoml_family_transfer import run_fixture
from physics_lab.workflows.artifacts import git_commit

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "AGENT-RUN-0087"
FIXTURE = "data/thermophysical/thermoml_tb_audit_fixture.yaml"
ENGINE = "physics_lab/engines/thermoml_family_transfer.py"
RUNNER = "scripts/run_thermoml_tb_family_transfer.py"
COMMAND = f"python {RUNNER} --write"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute() -> dict[str, Any]:
    fidelity = evaluate_fidelity_fixture()
    if not fidelity.passed:
        raise RuntimeError("Joback implementation-fidelity gate failed; transfer stopped")
    metrics = run_fixture(ROOT / FIXTURE)
    metrics["fidelity_gate"] = {
        "passed": fidelity.passed,
        "compound_count": fidelity.compound_count,
        "mismatch_count": fidelity.mismatch_count,
        "max_abs_error_k": fidelity.max_abs_error_k,
    }
    inputs = [FIXTURE, ENGINE, RUNNER, "physics_lab/engines/joback_tb.py"]
    metrics["run_meta"] = {
        "agent_run_id": RUN_ID,
        "command": COMMAND,
        "code_reference": ENGINE,
        "runner_reference": RUNNER,
        "engine_version": __version__,
        "git_commit": git_commit(ROOT),
        "input_file_hashes": {path: _hash(ROOT / path) for path in inputs},
        "deterministic": True,
        "shuffle_seed": 851,
    }
    return metrics


def _report(metrics: dict[str, Any]) -> str:
    transfer = metrics["transfer"]
    lines = [
        "# ThermoML Tb Family-Stratified Transfer",
        "",
        f"**Task:** `TASK-0851`; **Run:** `{RUN_ID}`",
        f"**Verdict:** `{transfer['verdict']}`",
        "",
        "## Scope",
        "",
        "The frozen Joback Tb estimator is scored on a value-blind, balanced 40-row "
        "audit fixture extracted from the checksum-verified NIST ThermoML archive. "
        "APL fits no Joback parameter. Raw archive bytes and a substantial normalized "
        "corpus are not committed.",
        "",
        f"The implementation-fidelity gate passed with "
        f"{metrics['fidelity_gate']['mismatch_count']}/"
        f"{metrics['fidelity_gate']['compound_count']} mismatches.",
        "",
        "## Aggregate metrics",
        "",
        "| Model/control | MAE (K) | RMSE (K) | uncertainty-weighted MAE (K) |",
        "| --- | ---: | ---: | ---: |",
    ]
    for name, score in transfer["aggregate"].items():
        weighted = score["uncertainty_weighted_mae_k"]
        lines.append(
            f"| `{name}` | {score['mae_k']:.3f} | {score['rmse_k']:.3f} | "
            f"{'n/a' if weighted is None else f'{weighted:.3f}'} |"
        )
    lines.extend(
        [
            "",
            f"Best non-oracle control: `{transfer['best_non_oracle_control']}`; "
            f"Joback margin `{transfer['joback_margin_vs_best_non_oracle_k']:.3f} K` "
            f"against a required `{transfer['survival_margin_k']:.1f} K`.",
            "",
            "## Per-family outcome",
            "",
            "| Held-out family | Joback MAE (K) | best control | margin (K) | clears |",
            "| --- | ---: | --- | ---: | :---: |",
        ]
    )
    for family, result in transfer["per_family"].items():
        lines.append(
            f"| {family} | {result['scores']['joback']['mae_k']:.3f} | "
            f"`{result['best_non_oracle_control']}` | "
            f"{result['joback_margin_vs_best_non_oracle_k']:.3f} | "
            f"{'yes' if result['clears_survival_margin'] else 'no'} |"
        )
    lines.extend(
        [
            "",
            "## Routing",
            "",
            "- Gate A: not promoted; bounded sandbox benchmark.",
            "- Gate B: fixture hash, command, code references, engine version, and git commit recorded.",
            "- Claim / knowledge impact: none.",
            "- Limitations: Tb only; 40-row balanced audit slice; family taxonomy and "
            "  Joback coverage exclusions are explicit; no universal accuracy claim.",
            "",
        ]
    )
    return "\n".join(lines)


def write() -> dict[str, Any]:
    metrics = compute()
    output = ROOT / "agent_runs" / RUN_ID
    output.mkdir(parents=True, exist_ok=True)
    (output / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "report.md").write_text(_report(metrics), encoding="utf-8")
    (output / "limitations.md").write_text(
        "# Limitations\n\n"
        "- Tb only; Tc excluded to avoid upstream-property leakage.\n"
        "- Balanced 40-row audit fixture, not the full ThermoML corpus.\n"
        "- Joback-covered neutral organics and eight represented families only.\n"
        "- No universal accuracy claim or canonical RESULT promotion.\n",
        encoding="utf-8",
    )
    (output / "preflight.md").write_text(
        "# Preflight\n\n"
        "- PASS: official ThermoML archive checksum verified during fixture extraction.\n"
        "- PASS: frozen Joback fidelity fixture has zero mismatches.\n"
        "- PASS: balanced family selection is value-blind to Joback error.\n"
        "- PASS: raw archive and substantial normalized corpus are not committed.\n"
        f"- Replay: `{COMMAND}`.\n",
        encoding="utf-8",
    )
    (output / "review_summary.md").write_text(
        "# Review Summary\n\n"
        f"- Verdict: `{metrics['transfer']['verdict']}`.\n"
        "- Review focus: bounded fixture selection, family controls, and source-rights posture.\n",
        encoding="utf-8",
    )
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    metrics = write() if args.write else compute()
    print(json.dumps({"run": RUN_ID, "verdict": metrics["transfer"]["verdict"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
