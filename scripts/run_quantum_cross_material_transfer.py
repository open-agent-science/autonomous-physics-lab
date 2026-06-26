"""Run the frozen TASK-0842 cross-material confinement transfer benchmark.

Calibrate a size-confinement power law on the direct InP rows (qd-0003), freeze
it, and predict the held-out direct ZnSe rows (qd-0004) under controls without
any refit. Emits the sandbox AGENT-RUN-0083 artifacts.

Gate-B-replayable: the metrics carry the pinned command, code reference, engine
version, git commit, and SHA-256 input hashes. The run is deterministic, so two
invocations produce identical metrics.

Usage:

    python scripts/run_quantum_cross_material_transfer.py            # print summary
    python scripts/run_quantum_cross_material_transfer.py --write    # write AGENT-RUN-0083
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from physics_lab import __version__
from physics_lab.engines.quantum_cross_material_transfer import (
    run_cross_material_transfer,
)
from physics_lab.workflows.artifacts import git_commit

REPO_ROOT = Path(__file__).resolve().parents[1]

AGENT_RUN_ID = "AGENT-RUN-0083"
ENGINE_REL = "physics_lab/engines/quantum_cross_material_transfer.py"
RUNNER_REL = "scripts/run_quantum_cross_material_transfer.py"
INP_DATASET_REL = "data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml"
ZNSE_DATASET_REL = "data/quantum_dots/qd-0004-toufanian-2021-znse-absorption.yaml"
PINNED_COMMAND = f"python {RUNNER_REL} --write"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _compute_metrics() -> dict[str, Any]:
    inp_path = REPO_ROOT / INP_DATASET_REL
    znse_path = REPO_ROOT / ZNSE_DATASET_REL
    metrics = run_cross_material_transfer(
        inp_dataset_path=inp_path,
        znse_dataset_path=znse_path,
    )
    metrics["run_meta"] = {
        "agent_run_id": AGENT_RUN_ID,
        "command": PINNED_COMMAND,
        "code_reference": ENGINE_REL,
        "runner_reference": RUNNER_REL,
        "engine_version": __version__,
        "git_commit": git_commit(REPO_ROOT),
        "input_file_hashes": {
            INP_DATASET_REL: _sha256(inp_path),
            ZNSE_DATASET_REL: _sha256(znse_path),
        },
        "deterministic": True,
        "shuffle_seed": metrics["shuffle_seed"],
    }
    return metrics


def _fmt(value: float) -> str:
    return f"{value:.6f}"


def _direction_report_lines(label: str, direction: dict[str, Any]) -> list[str]:
    model = direction["frozen_model"]
    transfer = direction["transfer"]
    controls = transfer["controls"]
    clears = "yes" if transfer["clears_predeclared_margin"] else "no"
    lines = [
        f"### {label}",
        "",
        f"- Calibration material: `{direction['calibration_material']}` -> "
        f"holdout material: `{direction['holdout_material']}`.",
        f"- Frozen confinement model: `conf = {model['coefficient_C']:.6f} * "
        f"d^(-{model['exponent_n']:.6f})` "
        f"(calibration train confinement MAE "
        f"`{_fmt(model['calibration_train_confinement_mae_ev'])} eV`).",
        f"- Transferred holdout confinement MAE: "
        f"`{_fmt(transfer['transferred']['mae_ev'])} eV`.",
        f"- Control `per_material_mean` MAE: "
        f"`{_fmt(controls['per_material_mean']['mae_ev'])} eV`.",
        f"- Control `shuffled_size` MAE: "
        f"`{_fmt(controls['shuffled_size']['mae_ev'])} eV`.",
        f"- Best control: `{transfer['best_control_id']}` "
        f"(`{_fmt(transfer['best_control_mae_ev'])} eV`).",
        f"- Margin over best control: "
        f"`{_fmt(transfer['transfer_margin_vs_best_control_ev'])} eV` "
        f"(predeclared requirement `>= {transfer['required_margin_ev']:.3f} eV`; "
        f"clears: {clears}).",
        "",
    ]
    return lines


def _render_report(metrics: dict[str, Any]) -> str:
    equiv = metrics["framings"]["equivalent_diameter"]
    primary = equiv["forward_inp_to_znse"]
    primary_transfer = primary["transfer"]
    lines: list[str] = [
        "# Cross-Material Confinement Transfer Benchmark (InP <-> ZnSe)",
        "",
        f"**Scientific verdict:** `{metrics['scientific_verdict']}`",
        f"**Sandbox verdict:** `{metrics['agent_verdict']}`",
        f"**Task:** `{metrics['task_id']}`  **Sandbox run:** `{AGENT_RUN_ID}`",
        "",
        "## Question",
        "",
        "Does an InP-calibrated size-confinement model predict the held-out ZnSe "
        "direct-size rows under controls, without refitting on ZnSe?",
        "",
        "## Frozen design",
        "",
        "- Residual axis is the SIZE-CONFINEMENT term `conf = E1s - E_bulk` (eV), "
        "not absolute energy. The bulk gap is an explicit per-material INPUT, "
        "never fitted to a holdout:",
        f"  - InP `E_bulk = {metrics['bulk_gap_ev']['InP']:.2f} eV` "
        f"({metrics['bulk_gap_source']['InP']})",
        f"  - ZnSe `E_bulk = {metrics['bulk_gap_ev']['ZnSe']:.2f} eV` "
        f"({metrics['bulk_gap_source']['ZnSe']})",
        "- Confinement form `conf = C * d^(-n)` (particle-in-a-box-like; the "
        "exponent is fitted on the calibration material because Coulomb and "
        "finite-barrier corrections soften it). Both `C` and `n` are frozen from "
        "the calibration material and applied to the holdout with NO refit.",
        "- The two datasets report different size axes: InP is a tetrahedral TEM "
        "`edge_length_nm`; ZnSe is a spherical SAXS `diameter_nm`. The PRIMARY "
        "framing converts the InP tetrahedral edge to an equivalent spherical "
        f"diameter (`d_eq = {metrics['tetra_edge_to_equiv_diameter_factor']:.6f} * "
        "a_edge`, equal-volume sphere) so confinement is compared on a "
        "physically-comparable axis. A `characteristic_length` sensitivity "
        "framing (reported size axes used verbatim) is also computed.",
        "- Controls on the held-out material: `per_material_mean` (size-"
        "independent null) and `shuffled_size` (frozen model on a deterministically "
        f"permuted size axis, seed `{metrics['shuffle_seed']}`).",
        f"- PREDECLARED survival rule (frozen before reveal): the transferred "
        f"model clears the controls only if its holdout confinement MAE beats the "
        f"best control by at least `{metrics['required_margin_ev']:.3f} eV`.",
        "",
        "## Primary result: InP -> ZnSe (equivalent-diameter framing)",
        "",
        f"- Transfer confinement MAE: `{_fmt(metrics['primary_transfer_mae_ev'])} eV`.",
        f"- Best control (`{metrics['primary_best_control_id']}`) MAE: "
        f"`{_fmt(metrics['primary_best_control_mae_ev'])} eV`.",
        f"- Margin over best control: "
        f"`{_fmt(metrics['primary_transfer_margin_vs_best_control_ev'])} eV`.",
        f"- Clears predeclared `{metrics['required_margin_ev']:.3f} eV` margin: "
        f"**{'yes' if metrics['primary_clears_predeclared_margin'] else 'no'}**.",
        "",
        "The InP-calibrated confinement curve, transferred onto the equal-volume "
        "ZnSe diameter axis, reduces the held-out ZnSe confinement error below "
        "both controls, but the improvement over the per-material-mean null does "
        "NOT reach the predeclared survival margin. The honest reading is "
        "INCONCLUSIVE: there is a size-confinement signal that survives shuffling "
        "and beats the null, but it is not strong enough to call a clean "
        "cross-material transfer pass under the frozen rule. Per the honest-stop "
        "rule, the margin was not relaxed and the model was not refitted to "
        "rescue the result.",
        "",
        "## Per-row ZnSe holdout (primary framing)",
        "",
        "| row | d (nm) | observed E1s (eV) | observed conf (eV) | predicted conf (eV) | residual (eV) |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        *[
            f"| `{row['entry_id']}` | {row['size_nm']:.2f} | "
            f"{row['observed_e1s_ev']:.3f} | {row['observed_confinement_ev']:.4f} | "
            f"{row['predicted_confinement_ev']:.4f} | "
            f"{row['confinement_residual_ev']:+.4f} |"
            for row in primary_transfer["predictions"]
        ],
        "",
        "## Directions and framings",
        "",
        *_direction_report_lines(
            "Forward InP -> ZnSe (equivalent-diameter, PRIMARY)",
            equiv["forward_inp_to_znse"],
        ),
        *_direction_report_lines(
            "Reverse ZnSe -> InP (equivalent-diameter)",
            equiv["reverse_znse_to_inp"],
        ),
        *_direction_report_lines(
            "Forward InP -> ZnSe (characteristic-length sensitivity)",
            metrics["framings"]["characteristic_length"]["forward_inp_to_znse"],
        ),
        "The asymmetry is informative: the ZnSe-calibrated curve (10 rows, "
        "exponent ~1.09) extrapolates onto the held-out InP rows and clears the "
        "margin, while the InP-calibrated curve (6 rows, exponent ~0.75) does not "
        "quite clear it on ZnSe. The characteristic-length framing (raw "
        "tetrahedral edge vs spherical diameter, no morphology conversion) fails "
        "badly, confirming that the morphology-comparability conversion is what "
        "brings the InP curve into the ZnSe size regime; this is a modeling "
        "choice, declared up front, not a tuned knob.",
        "",
        "## Limitations",
        "",
        "- Two materials only (InP, ZnSe); this is a bounded two-material transfer "
        "benchmark, NOT evidence of a universal size law, a quantum-dot design "
        "law, or any material recommendation.",
        "- The transfer is framed on the confinement term with the bulk gap as an "
        "explicit per-material input; results depend on those cited bulk-gap "
        "values and on the equal-volume edge->diameter conversion.",
        "- Direct-size rows only (InP TEM edge length, ZnSe SAXS diameter); the "
        "calibration-derived Yu CdSe / Moreels PbS sets are excluded by design.",
        "- Six InP rows and ten ZnSe rows; small samples, single source per "
        "material, single morphology per material.",
        "- Sandbox evidence only. No RESULT, PRED, CLAIM, or KNOWLEDGE artifact is "
        "created; no claim is promoted.",
        "",
    ]
    return "\n".join(lines)


def _build_manifest(metrics: dict[str, Any]) -> dict[str, Any]:
    base = f"agent_runs/{AGENT_RUN_ID}"
    return {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": "quantum-size-effects",
        "task_id": "TASK-0842",
        "status": "REVIEW_READY",
        "sandbox_only": True,
        "created_by": {"contributor_id": "gladunrv", "agent_id": "claude"},
        "proposal_paths": {
            "hypothesis": "hypothesis_proposals/quantum-size-effects/HYP-PROPOSAL-0083-cross-material-confinement-transfer.yaml",
            "experiment": "experiment_proposals/quantum-size-effects/EXP-PROPOSAL-0083-cross-material-confinement-transfer.yaml",
        },
        "artifacts": {
            "metrics": f"{base}/metrics.json",
            "report": f"{base}/report.md",
            "limitations": f"{base}/limitations.md",
            "preflight": f"{base}/preflight.md",
            "review_summary": f"{base}/review_summary.md",
        },
        "preflight": {
            "passed": True,
            "checks": [
                {
                    "name": "direct_size_rows_only",
                    "status": "PASS",
                    "notes": "Only the direct InP (qd-0003 TEM) and ZnSe (qd-0004 SAXS) rows enter the judge; Yu CdSe / Moreels PbS excluded.",
                },
                {
                    "name": "confinement_axis_with_explicit_bulk_gap",
                    "status": "PASS",
                    "notes": "Residual axis is E1s - E_bulk; bulk gaps are explicit per-material inputs (InP 1.34 eV, ZnSe 2.70 eV), not fitted.",
                },
                {
                    "name": "no_refit_on_holdout",
                    "status": "PASS",
                    "notes": "C and n are frozen from the calibration material and applied to the holdout with no refit.",
                },
                {
                    "name": "controls_first_predeclared_margin",
                    "status": "PASS",
                    "notes": "per_material_mean and shuffled_size controls run; 0.05 eV survival margin predeclared before reveal and not relaxed.",
                },
            ],
        },
        "limitations": [
            "Two materials only; not a universal size law or material recommendation.",
            "Confinement-term framing with explicit cited bulk gaps and an equal-volume edge->diameter conversion.",
            "Direct-size rows only; six InP and ten ZnSe rows; one source and morphology per material.",
            "Sandbox evidence only; no canonical scientific artifact is created.",
        ],
        "verdict": metrics["agent_verdict"],
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": "Maintainer review; any canonical result or claim requires a separate promotion task with protected hypothesis/experiment links.",
        },
    }


def _render_limitations() -> str:
    return (
        "# Limitations\n\n"
        "- Two materials only (InP, ZnSe); a bounded two-material transfer "
        "benchmark, NOT a universal size law, quantum-dot design law, or "
        "material recommendation.\n"
        "- Confinement-term framing (E1s - E_bulk) with explicit cited bulk "
        "gaps (InP 1.34 eV, ZnSe 2.70 eV) and an equal-volume edge->diameter "
        "conversion.\n"
        "- Direct-size rows only (InP TEM edge length, ZnSe SAXS diameter); the "
        "calibration-derived Yu CdSe / Moreels PbS sets are excluded.\n"
        "- Six InP rows and ten ZnSe rows; one source and one morphology per "
        "material.\n"
        "- Sandbox evidence only; no RESULT, PRED, CLAIM, or KNOWLEDGE artifact "
        "is created and no claim is promoted.\n"
    )


def _render_preflight(metrics: dict[str, Any]) -> str:
    run_meta = metrics["run_meta"]
    hashes = "\n".join(
        f"  - `{rel}`: `{digest}`"
        for rel, digest in sorted(run_meta["input_file_hashes"].items())
    )
    return (
        "# Preflight\n\n"
        "- PASS: only direct-size rows enter the judge (six InP TEM qd-0003, "
        "ten ZnSe SAXS qd-0004); Yu CdSe / Moreels PbS excluded.\n"
        "- PASS: residual axis is the confinement term E1s - E_bulk with bulk "
        "gaps as explicit per-material inputs, not fitted to the holdout.\n"
        "- PASS: C and n are frozen from the calibration material and applied "
        "to the holdout with no refit; no absolute-energy fallback.\n"
        "- PASS: per_material_mean and shuffled_size controls run; the 0.05 eV "
        "survival margin was predeclared before the reveal and not relaxed.\n\n"
        "## Gate-B replayability\n\n"
        f"- Command: `{run_meta['command']}`\n"
        f"- Code reference: `{run_meta['code_reference']}`\n"
        f"- Engine version: `{run_meta['engine_version']}`\n"
        f"- Git commit: `{run_meta['git_commit']}`\n"
        "- Input file SHA-256:\n"
        f"{hashes}\n"
        "- Deterministic: re-running the writer twice yields identical "
        "`metrics.json`.\n"
    )


def _render_review_summary(metrics: dict[str, Any]) -> str:
    clears = "yes" if metrics["primary_clears_predeclared_margin"] else "no"
    return (
        "# Review Summary\n\n"
        f"- Verdict: `{metrics['scientific_verdict']}` / "
        f"`{metrics['agent_verdict']}`.\n"
        f"- Primary InP -> ZnSe (equivalent-diameter) transfer confinement MAE: "
        f"`{metrics['primary_transfer_mae_ev']:.6f} eV`.\n"
        f"- Best control (`{metrics['primary_best_control_id']}`) MAE: "
        f"`{metrics['primary_best_control_mae_ev']:.6f} eV`; margin "
        f"`{metrics['primary_transfer_margin_vs_best_control_ev']:.6f} eV` "
        f"(predeclared `>= {metrics['required_margin_ev']:.3f} eV`; "
        f"clears: {clears}).\n"
        "- Review focus: the frozen confinement design, the borderline margin "
        "(beats controls but short of the predeclared threshold, not relaxed), "
        "the forward/reverse asymmetry, and the morphology-conversion choice.\n"
    )


def write_outputs() -> dict[str, Any]:
    metrics = _compute_metrics()
    output_dir = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "report.md").write_text(_render_report(metrics), encoding="utf-8")
    (output_dir / "limitations.md").write_text(
        _render_limitations(), encoding="utf-8"
    )
    (output_dir / "preflight.md").write_text(
        _render_preflight(metrics), encoding="utf-8"
    )
    (output_dir / "review_summary.md").write_text(
        _render_review_summary(metrics), encoding="utf-8"
    )
    manifest = _build_manifest(metrics)
    (output_dir / "agent_run.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help=f"Write the {AGENT_RUN_ID} sandbox artifacts.",
    )
    args = parser.parse_args()
    metrics = write_outputs() if args.write else _compute_metrics()
    print(
        json.dumps(
            {
                "scientific_verdict": metrics["scientific_verdict"],
                "agent_verdict": metrics["agent_verdict"],
                "primary_transfer_mae_ev": metrics["primary_transfer_mae_ev"],
                "primary_best_control_id": metrics["primary_best_control_id"],
                "primary_best_control_mae_ev": metrics["primary_best_control_mae_ev"],
                "primary_transfer_margin_vs_best_control_ev": metrics[
                    "primary_transfer_margin_vs_best_control_ev"
                ],
                "primary_clears_predeclared_margin": metrics[
                    "primary_clears_predeclared_margin"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
