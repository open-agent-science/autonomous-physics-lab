#!/usr/bin/env python3
"""Run and package the TASK-0850 literature-effective-mass transfer."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from physics_lab import __version__
from physics_lab.engines.quantum_effective_mass_transfer import run_effective_mass_transfer
from physics_lab.workflows.artifacts import git_commit

ROOT = Path(__file__).resolve().parents[1]
AGENT_RUN_ID = "AGENT-RUN-0085"
ENGINE_REL = "physics_lab/engines/quantum_effective_mass_transfer.py"
RUNNER_REL = "scripts/run_quantum_effective_mass_transfer.py"
INP_REL = "data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml"
ZNSE_REL = "data/quantum_dots/qd-0004-toufanian-2021-znse-absorption.yaml"
MASS_REL = "data/quantum_dots/effective_mass_inputs.yaml"
COMMAND = f"python {RUNNER_REL} --write"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))


def compute_metrics() -> dict[str, Any]:
    metrics = run_effective_mass_transfer(
        inp_dataset_path=ROOT / INP_REL,
        znse_dataset_path=ROOT / ZNSE_REL,
        effective_mass_path=ROOT / MASS_REL,
    )
    metrics["run_meta"] = {
        "agent_run_id": AGENT_RUN_ID,
        "command": COMMAND,
        "code_reference": ENGINE_REL,
        "runner_reference": RUNNER_REL,
        "engine_version": __version__,
        "git_commit": git_commit(ROOT),
        "input_file_hashes": {
            rel: _sha(ROOT / rel)
            for rel in (INP_REL, ZNSE_REL, MASS_REL, ENGINE_REL, RUNNER_REL)
        },
        "deterministic": True,
    }
    return metrics


def _direction_lines(label: str, item: dict[str, Any]) -> list[str]:
    return [
        f"### {label}",
        "",
        f"- Literature-mass MAE: `{item['mass_scaled_transfer']['mae_ev']:.6f} eV`.",
        f"- TASK-0842 bulk-gap-only MAE: `{item['bulk_gap_only_transfer']['mae_ev']:.6f} eV`.",
        f"- Improvement versus bulk-gap-only: `{item['mass_scaled_improvement_vs_bulk_gap_only_ev']:+.6f} eV`.",
        f"- Best control: `{item['best_control_id']}` at `{item['best_control_mae_ev']:.6f} eV`.",
        f"- Margin versus best control: `{item['mass_scaled_margin_vs_best_control_ev']:+.6f} eV` (required `0.05 eV`; clears: `{item['clears_predeclared_margin']}`).",
        f"- Reduced-mass scaling factor: `{item['frozen_model']['reduced_mass_scaling_factor']:.6f}`; holdout fit: `none`.",
        "",
    ]


def render_report(metrics: dict[str, Any]) -> str:
    primary = metrics["framings"]["equivalent_diameter"]
    forward = primary["forward_inp_to_znse"]
    reverse = primary["reverse_znse_to_inp"]
    lines = [
        "# Literature-effective-mass InP-ZnSe confinement transfer",
        "",
        f"**Task:** `TASK-0850`  **Run:** `{AGENT_RUN_ID}`",
        f"**Verdict:** `{metrics['scientific_verdict']}`",
        "",
        "## Frozen model",
        "",
        "The TASK-0842 confinement curve is calibrated on one material only. Its coefficient is transferred as `C_target=C_source*(mu_source/mu_target)`, where `mu=(1/me+1/mh)^-1` and all masses come from the pre-registered literature input file. No mass, exponent, coefficient, or scaling factor is fit on a holdout.",
        "",
        "- InP: `me=0.08 m0`, `mh=0.64 m0`, `mu=0.071111 m0`; Wu et al., Chemical Science 2020, DOI `10.1039/D0SC01039A`.",
        "- ZnSe: `me=0.16 m0`, `mh=0.75 m0`, `mu=0.131868 m0`; Jang et al., Research Square 2022, DOI `10.21203/rs.3.rs-1183117/v1` (CC BY 4.0 preprint).",
        "",
        "## Primary equivalent-diameter results",
        "",
        *_direction_lines("InP -> ZnSe", forward),
        *_direction_lines("ZnSe -> InP", reverse),
        "The literature-mass prefactor worsens transfer in both directions relative to the TASK-0842 bulk-gap-only model and fails even the strongest control in both directions. The honest bounded result is material-specificity after this particular bulk effective-mass correction; no parameter is refit to rescue it.",
        "",
        "## Controls",
        "",
        "Each direction includes a calibration-material mean null, a held-out per-material mean upper-bound control, and a deterministic shuffled-size control. The predeclared survival threshold remains `0.05 eV`.",
        "",
        "## Scope and routing",
        "",
        "- Direct-size rows only: six InP TEM rows and ten ZnSe SAXS rows.",
        "- Two materials and bulk scalar effective masses only; nonparabolicity, anisotropy, dielectric confinement, and finite barriers are outside scope.",
        "- Gate A: not attempted; output remains sandbox because the bounded model fails controls and this task does not create protected HYP/EXP links.",
        "- Gate B: replay metadata complete; independent replay must use a different agent.",
        "- Claim status impact: none. No RESULT/PRED/CLAIM/KNOW is created.",
        "",
    ]
    return "\n".join(lines)


def write_outputs() -> dict[str, Any]:
    metrics = compute_metrics()
    out = ROOT / "agent_runs" / AGENT_RUN_ID
    _write(out / "metrics.json", json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    _write(out / "report.md", render_report(metrics))
    _write(
        out / "limitations.md",
        "# Limitations\n\n- Two materials, 6 InP and 10 ZnSe rows.\n- Bulk scalar literature masses; no nanocrystal nonparabolicity, anisotropy, finite barrier, or dielectric correction.\n- ZnSe mass source is a CC BY 4.0 preprint.\n- Negative sandbox evidence; no claim or canonical result promotion.\n",
    )
    _write(
        out / "preflight.md",
        f"# Preflight\n\n- PASS: masses frozen in `{MASS_REL}` before scoring.\n- PASS: no holdout fit; both directions use `C_target=C_source*mu_source/mu_target`.\n- PASS: direct-size rows only; calibration-derived datasets excluded.\n- PASS: bulk-gap-only model and three controls compared under the unchanged 0.05 eV margin.\n- Replay: `{COMMAND}`; code `{ENGINE_REL}`; commit `{metrics['run_meta']['git_commit']}`.\n",
    )
    _write(
        out / "review_summary.md",
        f"# Review Summary\n\nVerdict: `{metrics['scientific_verdict']}`. Effective-mass scaling worsens MAE versus TASK-0842 in both primary directions and clears neither best-control margin. No holdout fit and no claim impact.\n",
    )
    manifest = {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": "quantum-size-effects",
        "task_id": "TASK-0850",
        "status": "REVIEW_READY",
        "sandbox_only": True,
        "created_by": {"contributor_id": "akutenyov", "agent_id": "codex"},
        "proposal_paths": {
            "hypothesis": "hypothesis_proposals/quantum-size-effects/HYP-PROPOSAL-0083-cross-material-confinement-transfer.yaml",
            "experiment": "experiment_proposals/quantum-size-effects/EXP-PROPOSAL-0083-cross-material-confinement-transfer.yaml",
        },
        "artifacts": {
            "metrics": f"agent_runs/{AGENT_RUN_ID}/metrics.json",
            "report": f"agent_runs/{AGENT_RUN_ID}/report.md",
            "limitations": f"agent_runs/{AGENT_RUN_ID}/limitations.md",
            "preflight": f"agent_runs/{AGENT_RUN_ID}/preflight.md",
            "review_summary": f"agent_runs/{AGENT_RUN_ID}/review_summary.md",
        },
        "preflight": {
            "passed": True,
            "checks": [
                {"name": "literature_masses_frozen", "status": "PASS", "notes": "DOI-pinned masses recorded before scoring."},
                {"name": "no_holdout_fit", "status": "PASS", "notes": "No mass or model parameter fit on either holdout."},
                {"name": "controls_and_both_directions", "status": "PASS", "notes": "Three controls and both transfer directions executed."},
            ],
        },
        "limitations": [
            "Two materials and small direct-size samples only.",
            "Bulk scalar mass approximation omits several nanocrystal corrections.",
            "Sandbox evidence only; no canonical result or claim promotion.",
        ],
        "verdict": "REVIEW_NEEDED",
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": "Maintainer review; Gate B replay must be performed by a different agent.",
        },
    }
    _write(out / "agent_run.yaml", yaml.safe_dump(manifest, sort_keys=False, allow_unicode=False))
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    metrics = write_outputs() if args.write else compute_metrics()
    primary = metrics["framings"]["equivalent_diameter"]
    print(json.dumps({
        "scientific_verdict": metrics["scientific_verdict"],
        "forward_mae_ev": primary["forward_inp_to_znse"]["mass_scaled_transfer"]["mae_ev"],
        "forward_margin_ev": primary["forward_inp_to_znse"]["mass_scaled_margin_vs_best_control_ev"],
        "reverse_mae_ev": primary["reverse_znse_to_inp"]["mass_scaled_transfer"]["mae_ev"],
        "reverse_margin_ev": primary["reverse_znse_to_inp"]["mass_scaled_margin_vs_best_control_ev"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
