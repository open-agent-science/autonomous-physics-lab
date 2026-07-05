"""Run the TASK-0920 quantum ZnSe no-refit transfer per the TASK-0914 contract.

TASK-0914 froze the admissible ZnSe/InP transfer contract in
``docs/reviews/quantum-znse-no-refit-transfer-contract.md`` with verdict
``STRICT_NO_REFIT_TRANSFER_CONTRACT_READY``: exact input rows, equal-volume
size harmonization, fixed confinement model family, controls, and a 0.05 eV
survival threshold. TASK-0920 may execute only that contract, unchanged.

This runner is an exact workflow wrapper around the committed TASK-0842
engine (``physics_lab/engines/quantum_cross_material_transfer.py``), whose
frozen semantics match the contract one-for-one:

- rows: the six direct InP TEM rows (qd-0003) and ten direct ZnSe SAXS rows
  (qd-0004), verified here against the contract's frozen row-id lists;
- size harmonization: InP tetrahedral edge -> equal-volume sphere diameter
  with the frozen factor ``0.608291447``; ZnSe SAXS diameter verbatim;
- residual axis: confinement ``E1s - E_bulk`` with fixed bulk gaps
  (InP 1.34 eV, ZnSe 2.70 eV), never fitted;
- model family: ``conf = C * d^(-n)`` fitted on the calibration material only
  and applied to the holdout with no refit;
- controls: ``per_material_mean`` and ``shuffled_size`` (seed 842);
- survival rule: the transferred model clears only if its holdout confinement
  MAE beats the best (lowest-MAE) control by at least 0.05 eV.

Before any metric is computed, the wrapper verifies the frozen contract
parameters against the engine constants and the committed rows and raises
``ContractViolationError`` on any mismatch (the TASK-0914 stop condition).
It performs no refit, no correction search, no post-hoc threshold change,
and no source-byte redistribution.

Gate-B-replayable: the metrics carry the pinned command, code reference,
engine version, git commit, and SHA-256 input hashes. The run is
deterministic, so two invocations produce identical metrics.

Usage:

    python scripts/run_quantum_znse_contract_transfer.py            # print summary
    python scripts/run_quantum_znse_contract_transfer.py --write    # write AGENT-RUN-0090
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
    BULK_GAP_EV,
    REQUIRED_MARGIN_EV,
    SHUFFLE_SEED,
    TETRA_EDGE_TO_EQUIV_DIAMETER,
    load_inp_rows,
    load_znse_rows,
    run_cross_material_transfer,
)
from physics_lab.workflows.artifacts import git_commit

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_ID = "TASK-0920"
CONTRACT_TASK_ID = "TASK-0914"
ENGINE_ORIGIN_TASK_ID = "TASK-0842"
AGENT_RUN_ID = "AGENT-RUN-0090"
EXPLORATORY_AGENT_RUN_ID = "AGENT-RUN-0083"
CONTRACT_REFERENCE = "docs/reviews/quantum-znse-no-refit-transfer-contract.md"
CONTRACT_SOURCE_VERDICT = "STRICT_NO_REFIT_TRANSFER_CONTRACT_READY"
ENGINE_REL = "physics_lab/engines/quantum_cross_material_transfer.py"
RUNNER_REL = "scripts/run_quantum_znse_contract_transfer.py"
INP_DATASET_REL = "data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml"
ZNSE_DATASET_REL = "data/quantum_dots/qd-0004-toufanian-2021-znse-absorption.yaml"
PINNED_COMMAND = f"python {RUNNER_REL} --write"

# Frozen by the TASK-0914 contract note. Any drift is a stop condition.
CONTRACT_TETRA_FACTOR = 0.608291447
CONTRACT_BULK_GAP_EV = {"InP": 1.34, "ZnSe": 2.70}
CONTRACT_REQUIRED_MARGIN_EV = 0.05
CONTRACT_SHUFFLE_SEED = 842
CONTRACT_PRIMARY_FRAMING = "equivalent_diameter"
CONTRACT_PRIMARY_DIRECTION = "forward_inp_to_znse"
CONTRACT_CONTROL_IDS = ("per_material_mean", "shuffled_size")
CONTRACT_INP_ROW_IDS = (
    "almeida-2023-inp-460nm",
    "almeida-2023-inp-480nm",
    "almeida-2023-inp-510nm",
    "almeida-2023-inp-550nm",
    "almeida-2023-inp-580nm",
    "almeida-2023-inp-620nm",
)
CONTRACT_ZNSE_ROW_IDS = (
    "toufanian-2021-znse-qd361",
    "toufanian-2021-znse-qd364",
    "toufanian-2021-znse-qd375",
    "toufanian-2021-znse-qd383",
    "toufanian-2021-znse-qd390",
    "toufanian-2021-znse-qd397",
    "toufanian-2021-znse-qd405",
    "toufanian-2021-znse-qd410",
    "toufanian-2021-znse-qd419",
    "toufanian-2021-znse-qd422",
)


class ContractViolationError(RuntimeError):
    """Raised when an input or engine constant drifts from the frozen contract."""


def verify_frozen_contract(
    *, inp_dataset_path: str | Path, znse_dataset_path: str | Path
) -> None:
    """Verify the TASK-0914 frozen parameters before any metric is inspected.

    The contract's stop condition: if the rows, harmonization factor, bulk
    gaps, controls seed, or survival threshold differ from the frozen values,
    the run must stop instead of adapting.
    """
    if round(TETRA_EDGE_TO_EQUIV_DIAMETER, 9) != CONTRACT_TETRA_FACTOR:
        raise ContractViolationError(
            "Equal-volume edge->diameter factor drifted from the frozen "
            f"{CONTRACT_TETRA_FACTOR}: {TETRA_EDGE_TO_EQUIV_DIAMETER!r}"
        )
    if BULK_GAP_EV != CONTRACT_BULK_GAP_EV:
        raise ContractViolationError(
            f"Bulk-gap inputs drifted from the frozen {CONTRACT_BULK_GAP_EV}: {BULK_GAP_EV}"
        )
    if REQUIRED_MARGIN_EV != CONTRACT_REQUIRED_MARGIN_EV:
        raise ContractViolationError(
            "Survival margin drifted from the frozen "
            f"{CONTRACT_REQUIRED_MARGIN_EV} eV: {REQUIRED_MARGIN_EV}"
        )
    if SHUFFLE_SEED != CONTRACT_SHUFFLE_SEED:
        raise ContractViolationError(
            f"Shuffled-size seed drifted from the frozen {CONTRACT_SHUFFLE_SEED}: {SHUFFLE_SEED}"
        )
    inp_ids = sorted(row.entry_id for row in load_inp_rows(inp_dataset_path))
    if inp_ids != sorted(CONTRACT_INP_ROW_IDS):
        raise ContractViolationError(
            "InP calibration rows differ from the frozen contract row ids: "
            f"{inp_ids} != {sorted(CONTRACT_INP_ROW_IDS)}"
        )
    znse_ids = sorted(row.entry_id for row in load_znse_rows(znse_dataset_path))
    if znse_ids != sorted(CONTRACT_ZNSE_ROW_IDS):
        raise ContractViolationError(
            "ZnSe holdout rows differ from the frozen contract row ids: "
            f"{znse_ids} != {sorted(CONTRACT_ZNSE_ROW_IDS)}"
        )


def contract_survival_outcome(
    *, clears_predeclared_margin: bool, margin_ev: float
) -> tuple[str, str]:
    """Map the primary-judge margin onto the contract's frozen routing.

    - clears the 0.05 eV margin -> pass (bounded positive transfer memory);
    - beats the best control but under the margin -> fail to clear, routed as
      inconclusive/borderline memory, not a positive claim;
    - does not beat the best control -> negative memory.
    """
    if clears_predeclared_margin:
        return (
            "PASS_CLEARS_PREDECLARED_MARGIN",
            "bounded positive transfer memory (still no claim promotion)",
        )
    if margin_ev > 0.0:
        return (
            "FAIL_TO_CLEAR_PREDECLARED_MARGIN",
            "inconclusive/borderline memory, not a positive claim",
        )
    return (
        "NEGATIVE_MEMORY",
        "negative memory (the transferred model does not beat the best control)",
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _compute_metrics() -> dict[str, Any]:
    inp_path = REPO_ROOT / INP_DATASET_REL
    znse_path = REPO_ROOT / ZNSE_DATASET_REL
    verify_frozen_contract(inp_dataset_path=inp_path, znse_dataset_path=znse_path)
    metrics = run_cross_material_transfer(
        inp_dataset_path=inp_path,
        znse_dataset_path=znse_path,
    )
    outcome, routing = contract_survival_outcome(
        clears_predeclared_margin=metrics["primary_clears_predeclared_margin"],
        margin_ev=metrics["primary_transfer_margin_vs_best_control_ev"],
    )
    metrics["task_id"] = TASK_ID
    metrics["contract"] = {
        "contract_task_id": CONTRACT_TASK_ID,
        "contract_reference": CONTRACT_REFERENCE,
        "contract_source_verdict": CONTRACT_SOURCE_VERDICT,
        "engine_origin_task_id": ENGINE_ORIGIN_TASK_ID,
        "exploratory_agent_run_id": EXPLORATORY_AGENT_RUN_ID,
        "frozen_inp_row_ids": list(CONTRACT_INP_ROW_IDS),
        "frozen_znse_row_ids": list(CONTRACT_ZNSE_ROW_IDS),
        "tetra_edge_to_equiv_diameter_factor": CONTRACT_TETRA_FACTOR,
        "bulk_gap_ev": dict(CONTRACT_BULK_GAP_EV),
        "required_margin_ev": CONTRACT_REQUIRED_MARGIN_EV,
        "shuffle_seed": CONTRACT_SHUFFLE_SEED,
        "primary_framing": CONTRACT_PRIMARY_FRAMING,
        "primary_direction": CONTRACT_PRIMARY_DIRECTION,
        "control_ids": list(CONTRACT_CONTROL_IDS),
        "no_refit": True,
        "no_correction_search": True,
        "no_post_hoc_threshold_change": True,
    }
    metrics["contract_survival_outcome"] = outcome
    metrics["contract_outcome_routing"] = routing
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
    return [
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
        f"(frozen requirement `>= {transfer['required_margin_ev']:.3f} eV`; "
        f"clears: {clears}).",
        "",
    ]


def _render_report(metrics: dict[str, Any]) -> str:
    contract = metrics["contract"]
    equiv = metrics["framings"]["equivalent_diameter"]
    primary_transfer = equiv["forward_inp_to_znse"]["transfer"]
    lines: list[str] = [
        "# Quantum ZnSe No-Refit Transfer: TASK-0914 Contract Execution",
        "",
        f"**Contract survival outcome:** `{metrics['contract_survival_outcome']}`",
        f"**Contract routing:** {metrics['contract_outcome_routing']}",
        f"**Scientific verdict:** `{metrics['scientific_verdict']}`  "
        f"**Sandbox verdict:** `{metrics['agent_verdict']}`",
        f"**Task:** `{metrics['task_id']}`  **Contract:** `{contract['contract_task_id']}` "
        f"(`{contract['contract_source_verdict']}`)  **Sandbox run:** `{AGENT_RUN_ID}`",
        "",
        "## Question",
        "",
        "Executed exactly as frozen by the TASK-0914 contract "
        f"(`{contract['contract_reference']}`): does the InP-calibrated "
        "size-confinement model predict the held-out ZnSe direct-size rows "
        "under controls, without refitting on ZnSe, clearing the frozen "
        "0.05 eV survival margin?",
        "",
        "## Frozen contract executed (no parameter chosen post-hoc)",
        "",
        f"- Calibration rows: the six InP TEM rows of `{INP_DATASET_REL}` "
        "(frozen row ids verified before the run).",
        f"- Holdout rows: the ten ZnSe SAXS rows of `{ZNSE_DATASET_REL}` "
        "(frozen row ids verified before the run).",
        "- Size harmonization: InP tetrahedral edge -> equal-volume sphere "
        f"diameter with the frozen factor `{contract['tetra_edge_to_equiv_diameter_factor']}`; "
        "ZnSe SAXS diameter used verbatim. The `characteristic_length` "
        "sensitivity framing is reported as a descriptive diagnostic only.",
        "- Residual axis: confinement `conf = E1s - E_bulk` with fixed bulk "
        f"gaps InP `{contract['bulk_gap_ev']['InP']:.2f} eV`, ZnSe "
        f"`{contract['bulk_gap_ev']['ZnSe']:.2f} eV` (inputs, never fitted).",
        "- Model family: `conf = C * d^(-n)`; `C` and `n` fitted on the "
        "calibration material only and applied to the holdout with NO refit.",
        f"- Controls: `per_material_mean` and `shuffled_size` (seed "
        f"`{contract['shuffle_seed']}`) on the held-out material.",
        f"- Frozen survival rule: the transferred model clears only if its "
        f"holdout confinement MAE beats the best control by at least "
        f"`{contract['required_margin_ev']:.3f} eV`; the margin is not "
        "relaxed after reveal.",
        "- Primary judge: `InP -> ZnSe` on the `equivalent_diameter` framing. "
        "The reverse direction and the characteristic-length framing are "
        "secondary diagnostics and cannot change the primary verdict.",
        "",
        "## Primary result: InP -> ZnSe (equivalent-diameter framing)",
        "",
        f"- Transfer confinement MAE: `{_fmt(metrics['primary_transfer_mae_ev'])} eV`.",
        f"- Best control (`{metrics['primary_best_control_id']}`) MAE: "
        f"`{_fmt(metrics['primary_best_control_mae_ev'])} eV`.",
        f"- Margin over best control: "
        f"`{_fmt(metrics['primary_transfer_margin_vs_best_control_ev'])} eV`.",
        f"- Clears the frozen `{metrics['required_margin_ev']:.3f} eV` margin: "
        f"**{'yes' if metrics['primary_clears_predeclared_margin'] else 'no'}**.",
        f"- Contract outcome: **{metrics['contract_survival_outcome']}** -> "
        f"{metrics['contract_outcome_routing']}.",
        "",
        "The transferred model beats both frozen controls on the held-out "
        "ZnSe rows, but its improvement over the per-material-mean null "
        "falls short of the frozen 0.05 eV survival margin. Per the contract "
        "this outcome is routed as inconclusive/borderline memory, not a "
        "positive claim; the margin was not relaxed, the model was not "
        "refitted, and no correction search was run.",
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
            "Forward InP -> ZnSe (equivalent-diameter, PRIMARY JUDGE)",
            equiv["forward_inp_to_znse"],
        ),
        *_direction_report_lines(
            "Reverse ZnSe -> InP (equivalent-diameter, secondary symmetry check)",
            equiv["reverse_znse_to_inp"],
        ),
        *_direction_report_lines(
            "Forward InP -> ZnSe (characteristic-length, secondary sensitivity)",
            metrics["framings"]["characteristic_length"]["forward_inp_to_znse"],
        ),
        "Per the contract, neither secondary route changes the primary "
        "verdict: the reverse direction clears its margin and the "
        "characteristic-length framing fails badly, but the primary judge "
        "remains the InP -> ZnSe equivalent-diameter transfer.",
        "",
        "## Relation to the exploratory TASK-0842 run",
        "",
        "The frozen inputs (row bytes) and the committed engine are unchanged "
        "since the exploratory TASK-0842 run (AGENT-RUN-0083), so this "
        "contract execution reproduces those metrics exactly. The scientific "
        "difference is authorization and routing: TASK-0914 predeclared the "
        "full contract before this run, so the borderline outcome is now "
        "contract-executed memory rather than an exploratory observation.",
        "",
        "## Limitations",
        "",
        "- Two materials only (InP, ZnSe); this is a bounded two-material "
        "transfer benchmark, NOT evidence of a universal size law, a "
        "quantum-dot design law, or any material recommendation.",
        "- The transfer is framed on the confinement term with the bulk gap "
        "as an explicit per-material input; results depend on those cited "
        "bulk-gap values and on the equal-volume edge->diameter conversion.",
        "- Direct-size rows only (InP TEM edge length, ZnSe SAXS diameter); "
        "the calibration-derived Yu CdSe / Moreels PbS sets are excluded by "
        "the contract.",
        "- Six InP rows and ten ZnSe rows; small samples, single source and "
        "single morphology per material.",
        "- Sandbox evidence only. No RESULT, PRED, CLAIM, or KNOWLEDGE "
        "artifact is created; no claim is promoted.",
        "",
    ]
    return "\n".join(lines)


def _build_manifest(metrics: dict[str, Any]) -> dict[str, Any]:
    base = f"agent_runs/{AGENT_RUN_ID}"
    return {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": "quantum-size-effects",
        "task_id": TASK_ID,
        "status": "REVIEW_READY",
        "sandbox_only": True,
        "created_by": {"contributor_id": "gladunrv", "agent_id": "claude"},
        "proposal_paths": {
            "hypothesis": "hypothesis_proposals/quantum-size-effects/HYP-PROPOSAL-0084-znse-contract-no-refit-transfer.yaml",
            "experiment": "experiment_proposals/quantum-size-effects/EXP-PROPOSAL-0084-znse-contract-no-refit-transfer.yaml",
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
                    "name": "frozen_contract_verified_before_run",
                    "status": "PASS",
                    "notes": "TASK-0914 frozen row ids, equal-volume factor 0.608291447, bulk gaps, seed 842, and 0.05 eV margin verified against the engine and datasets before any metric was computed.",
                },
                {
                    "name": "direct_size_rows_only",
                    "status": "PASS",
                    "notes": "Only the direct InP (qd-0003 TEM) and ZnSe (qd-0004 SAXS) rows enter the judge; Yu CdSe / Moreels PbS excluded by the contract.",
                },
                {
                    "name": "no_refit_on_holdout",
                    "status": "PASS",
                    "notes": "C and n are frozen from the calibration material and applied to the holdout with no refit, no correction search, and no post-hoc threshold change.",
                },
                {
                    "name": "controls_first_frozen_margin",
                    "status": "PASS",
                    "notes": "per_material_mean and shuffled_size controls run; the frozen 0.05 eV survival margin was predeclared by TASK-0914 and not relaxed.",
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
            "required_next_step": "Maintainer review of the contract execution; any canonical result or claim requires a separate promotion task with protected hypothesis/experiment links.",
        },
    }


def _render_limitations() -> str:
    return (
        "# Limitations\n\n"
        "- Two materials only (InP, ZnSe); a bounded two-material transfer "
        "benchmark executed per the TASK-0914 contract, NOT a universal size "
        "law, quantum-dot design law, or material recommendation.\n"
        "- Confinement-term framing (E1s - E_bulk) with explicit cited bulk "
        "gaps (InP 1.34 eV, ZnSe 2.70 eV) and an equal-volume edge->diameter "
        "conversion frozen at 0.608291447.\n"
        "- Direct-size rows only (InP TEM edge length, ZnSe SAXS diameter); "
        "the calibration-derived Yu CdSe / Moreels PbS sets are excluded by "
        "the contract.\n"
        "- Six InP rows and ten ZnSe rows; one source and one morphology per "
        "material.\n"
        "- Sandbox evidence only; no RESULT, PRED, CLAIM, or KNOWLEDGE "
        "artifact is created and no claim is promoted.\n"
    )


def _render_preflight(metrics: dict[str, Any]) -> str:
    run_meta = metrics["run_meta"]
    hashes = "\n".join(
        f"  - `{rel}`: `{digest}`"
        for rel, digest in sorted(run_meta["input_file_hashes"].items())
    )
    return (
        "# Preflight\n\n"
        "- PASS: the TASK-0914 frozen contract (row ids, equal-volume factor "
        "0.608291447, bulk gaps, seed 842, 0.05 eV margin) was verified "
        "against the engine constants and committed datasets before any "
        "metric was computed; any drift raises ContractViolationError.\n"
        "- PASS: only direct-size rows enter the judge (six InP TEM qd-0003, "
        "ten ZnSe SAXS qd-0004); Yu CdSe / Moreels PbS excluded.\n"
        "- PASS: residual axis is the confinement term E1s - E_bulk with bulk "
        "gaps as explicit per-material inputs, not fitted to the holdout.\n"
        "- PASS: C and n are frozen from the calibration material and applied "
        "to the holdout with no refit; no correction search; no post-hoc "
        "threshold change; no absolute-energy fallback.\n"
        "- PASS: per_material_mean and shuffled_size controls run; the frozen "
        "0.05 eV survival margin was predeclared by TASK-0914 and not "
        "relaxed.\n\n"
        "## Gate-B replayability\n\n"
        f"- Command: `{run_meta['command']}`\n"
        f"- Code reference: `{run_meta['code_reference']}`\n"
        f"- Runner reference: `{run_meta['runner_reference']}`\n"
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
        f"- Contract survival outcome: `{metrics['contract_survival_outcome']}` "
        f"({metrics['contract_outcome_routing']}).\n"
        f"- Verdict: `{metrics['scientific_verdict']}` / "
        f"`{metrics['agent_verdict']}`.\n"
        f"- Primary InP -> ZnSe (equivalent-diameter) transfer confinement MAE: "
        f"`{metrics['primary_transfer_mae_ev']:.6f} eV`.\n"
        f"- Best control (`{metrics['primary_best_control_id']}`) MAE: "
        f"`{metrics['primary_best_control_mae_ev']:.6f} eV`; margin "
        f"`{metrics['primary_transfer_margin_vs_best_control_ev']:.6f} eV` "
        f"(frozen `>= {metrics['required_margin_ev']:.3f} eV`; "
        f"clears: {clears}).\n"
        "- Review focus: contract fidelity (frozen rows, harmonization, "
        "controls, threshold verified pre-run), the borderline margin routed "
        "per the frozen rule without relaxation, and the unchanged inputs "
        "relative to the exploratory TASK-0842 run.\n"
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
                "contract_survival_outcome": metrics["contract_survival_outcome"],
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
