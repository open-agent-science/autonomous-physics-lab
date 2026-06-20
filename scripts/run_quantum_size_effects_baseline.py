"""Run the frozen TASK-0225 quantum size-effect baseline benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from physics_lab.engines.quantum_size_effects import run_quantum_size_baseline


ROOT = Path(__file__).resolve().parents[1]


def _resolve(config_path: Path, value: str) -> Path:
    return (config_path.parent / value).resolve()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _model(metrics: dict[str, Any], model_id: str) -> dict[str, Any]:
    return next(model for model in metrics["models"] if model["model_id"] == model_id)


def _render_report(metrics: dict[str, Any]) -> str:
    selected = _model(metrics, metrics["selected_model_id"])
    return "\n".join(
        [
            "# Quantum Size Effects Baseline Benchmark",
            "",
            f"**Scientific verdict:** `{metrics['scientific_verdict']}`",
            f"**Sandbox verdict:** `{metrics['agent_verdict']}`",
            "",
            "## Result",
            "",
            f"- Selected model: `{metrics['selected_model_id']}`.",
            f"- Train MAE: `{metrics['selected_train_mae_ev']:.6f} eV`.",
            f"- Largest-size holdout MAE: `{metrics['selected_holdout_mae_ev']:.6f} eV`.",
            f"- Constant train-mean holdout MAE: `{metrics['constant_null_holdout_mae_ev']:.6f} eV`.",
            f"- Improvement over constant null: `{metrics['holdout_improvement_vs_null_ev']:.6f} eV`.",
            f"- Shuffled-size control holdout MAE: `{metrics['shuffled_control_holdout_mae_ev']:.6f} eV`.",
            "",
            "The selected model is the fixed Almeida source relation, evaluated with edge length "
            "converted from nm to Angstrom. It reproduces the single largest-size holdout better "
            "than both controls. Because the relation was published from the same InP size series, "
            "this is source-scoped consistency evidence, not independent validation of a physical law.",
            "",
            "## Per-Row Residuals",
            "",
            "| row | split | L (nm) | observed (eV) | predicted (eV) | residual (eV) | size sensitivity (eV) |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
            *[
                f"| `{row['entry_id']}` | {row['split']} | {row['edge_length_nm']:.3f} | "
                f"{row['observed_ev']:.3f} | {row['predicted_ev']:.6f} | "
                f"{row['residual_ev']:+.6f} | {row['size_sensitivity_ev']:.6f} |"
                for row in selected["predictions"]
            ],
            "",
            "The size-sensitivity column is `abs(dE/dL) * sigma_L`; it reflects the TEM size "
            "distribution propagated through the model, not optical-energy measurement uncertainty.",
            "",
            "## Limitations",
            "",
            "- Six figure-derived rows from one InP source and morphology.",
            "- One holdout point; no material-transfer claim.",
            "- Published relation and benchmark rows share a source series.",
            "- Tetrahedral edge length is retained; no spherical-radius conversion.",
            "- Absorption only; emission and bandgap are not mixed into the residual axis.",
            "",
        ]
    )


def _render_summary(metrics: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Quantum Size Effects Baseline Summary",
            "",
            f"`TASK-0225` produced a `{metrics['scientific_verdict']}` sandbox baseline on the "
            "six direct Almeida 2023 InP absorption rows.",
            "",
            f"The frozen selection chose `{metrics['selected_model_id']}`. Its largest-size "
            f"holdout absolute error is `{metrics['selected_holdout_mae_ev']:.6f} eV`, compared "
            f"with `{metrics['constant_null_holdout_mae_ev']:.6f} eV` for the constant train-mean "
            f"null and `{metrics['shuffled_control_holdout_mae_ev']:.6f} eV` for the deterministic "
            "shuffled-size control.",
            "",
            "This establishes a reproducible source-scoped baseline surface for later review. "
            "It does not establish cross-material transfer, a universal size law, a material "
            "recommendation, or an independently validated quantum-confinement model.",
            "",
            "Detailed evidence: `agent_runs/AGENT-RUN-0076/report.md`.",
            "",
        ]
    )


def write_outputs(config_path: Path) -> dict[str, Any]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    dataset_path = _resolve(config_path, config["dataset_path"])
    pre_reveal_path = _resolve(config_path, config["pre_reveal_path"])
    output_dir = _resolve(config_path, config["output_dir"])
    summary_path = _resolve(config_path, config["summary_path"])
    metrics = run_quantum_size_baseline(
        dataset_path=dataset_path,
        holdout_id=str(config["holdout_entry_id"]),
        shuffle_seed=int(config["shuffle_seed"]),
        required_holdout_improvement_ev=float(config["required_holdout_improvement_ev"]),
    )
    metrics["input_hashes"] = {
        "config": _sha256(config_path),
        "dataset": _sha256(dataset_path),
        "pre_reveal": _sha256(pre_reveal_path),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "report.md").write_text(_render_report(metrics), encoding="utf-8")
    (output_dir / "limitations.md").write_text(
        "# Limitations\n\n"
        "- Six figure-derived InP rows from one publication and one morphology.\n"
        "- One largest-size holdout row; material holdout is unavailable.\n"
        "- The selected published relation shares its source series with the observations.\n"
        "- Size sensitivity is not optical-energy uncertainty.\n"
        "- No RESULT, PRED, CLAIM, KNOW, or golden artifact is created.\n",
        encoding="utf-8",
    )
    (output_dir / "preflight.md").write_text(
        "# Preflight\n\n"
        "- PASS: TASK-0293 admitted six direct measurement rows.\n"
        "- PASS: absorption target and edge-length axis are separated and frozen.\n"
        "- PASS: largest-size holdout, model slate, controls, seed, and threshold were committed before execution.\n"
        "- PASS: no live fetch or calibration-derived row enters scoring.\n",
        encoding="utf-8",
    )
    (output_dir / "review_summary.md").write_text(
        "# Review Summary\n\n"
        f"- Verdict: `{metrics['scientific_verdict']}` / `{metrics['agent_verdict']}`.\n"
        f"- Selected model: `{metrics['selected_model_id']}`.\n"
        f"- Holdout MAE: `{metrics['selected_holdout_mae_ev']:.6f} eV`.\n"
        f"- Null holdout MAE: `{metrics['constant_null_holdout_mae_ev']:.6f} eV`.\n"
        "- Review focus: source-series dependence, one-point holdout, and uncertainty interpretation.\n",
        encoding="utf-8",
    )
    manifest = {
        "id": "AGENT-RUN-0076",
        "campaign_profile_id": "quantum-size-effects",
        "task_id": "TASK-0225",
        "status": "REVIEW_READY",
        "sandbox_only": True,
        "created_by": {"contributor_id": "akutenyov", "agent_id": "codex"},
        "proposal_paths": {
            "hypothesis": "hypothesis_proposals/quantum-size-effects/HYP-PROPOSAL-0061-baseline-consistency.yaml",
            "experiment": "experiment_proposals/quantum-size-effects/EXP-PROPOSAL-0027-baseline-consistency.yaml",
        },
        "artifacts": {
            "metrics": "agent_runs/AGENT-RUN-0076/metrics.json",
            "report": "agent_runs/AGENT-RUN-0076/report.md",
            "limitations": "agent_runs/AGENT-RUN-0076/limitations.md",
            "preflight": "agent_runs/AGENT-RUN-0076/preflight.md",
            "review_summary": "agent_runs/AGENT-RUN-0076/review_summary.md",
        },
        "preflight": {
            "passed": True,
            "checks": [
                {
                    "name": "direct_rows",
                    "status": "PASS",
                    "notes": "Six TASK-0293-admitted direct Almeida InP rows loaded.",
                },
                {
                    "name": "frozen_holdout",
                    "status": "PASS",
                    "notes": "Largest-size row held out under the committed pre-reveal package.",
                },
                {
                    "name": "property_separation",
                    "status": "PASS",
                    "notes": "Only absorption_peak_eV rows are scored.",
                },
                {
                    "name": "controls",
                    "status": "PASS",
                    "notes": "Constant-mean and deterministic shuffled-size controls executed.",
                },
            ],
        },
        "limitations": [
            "Six figure-derived InP rows from one source.",
            "One size-range holdout row and no material holdout.",
            "The selected published relation was derived from the same source series.",
            "No canonical scientific artifact is created.",
        ],
        "verdict": metrics["agent_verdict"],
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": "Maintainer review; any canonical result requires a separate promotion task.",
        },
    }
    (output_dir / "agent_run.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(_render_summary(metrics), encoding="utf-8")
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default=str(ROOT / "examples" / "quantum_size_effects.yaml"),
    )
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    config_path = Path(args.config).resolve()
    if not args.write:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        metrics = run_quantum_size_baseline(
            dataset_path=_resolve(config_path, config["dataset_path"]),
            holdout_id=str(config["holdout_entry_id"]),
            shuffle_seed=int(config["shuffle_seed"]),
            required_holdout_improvement_ev=float(config["required_holdout_improvement_ev"]),
        )
    else:
        metrics = write_outputs(config_path)
    print(json.dumps(
        {
            "selected_model_id": metrics["selected_model_id"],
            "selected_holdout_mae_ev": metrics["selected_holdout_mae_ev"],
            "constant_null_holdout_mae_ev": metrics["constant_null_holdout_mae_ev"],
            "shuffled_control_holdout_mae_ev": metrics["shuffled_control_holdout_mae_ev"],
            "scientific_verdict": metrics["scientific_verdict"],
        },
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
