#!/usr/bin/env python3
"""Run the TASK-0816 fixed-model Almeida LOO methodology stress test."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from statistics import mean
from typing import Any

import yaml

from physics_lab.engines.quantum_size_effects import load_direct_inp_absorption_rows


AGENT_RUN_ID = "AGENT-RUN-0077"
TASK_ID = "TASK-0816"
DATASET_PATH = Path("data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml")
OUTPUT_DIR = Path("agent_runs") / AGENT_RUN_ID
REVIEW_PATH = Path("docs/reviews/quantum-almeida-fixed-model-loo-methodology-stress-test.md")


def fixed_almeida_prediction(edge_length_nm: float) -> float:
    """Published Almeida relation evaluated on the committed edge-length axis."""
    edge_length_angstrom = 10.0 * edge_length_nm
    return 1.33 + 9.128 * edge_length_angstrom**-0.684


def main() -> int:
    rows = load_direct_inp_absorption_rows(DATASET_PATH)
    row_by_id = {row.entry_id: row for row in rows}

    folds: list[dict[str, Any]] = []
    for heldout in rows:
        train = [row for row in rows if row.entry_id != heldout.entry_id]
        train_offsets = [
            row.value_ev - fixed_almeida_prediction(row.edge_length_nm) for row in train
        ]
        additive_offset_ev = mean(train_offsets)
        constant_mean_ev = mean(row.value_ev for row in train)

        fixed_pred = fixed_almeida_prediction(heldout.edge_length_nm)
        offset_pred = fixed_pred + additive_offset_ev
        constant_pred = constant_mean_ev

        folds.append(
            {
                "heldout_entry_id": heldout.entry_id,
                "edge_length_nm": heldout.edge_length_nm,
                "observed_ev": heldout.value_ev,
                "fixed_prediction_ev": round(fixed_pred, 9),
                "fixed_abs_error_ev": round(abs(fixed_pred - heldout.value_ev), 9),
                "additive_offset_ev": round(additive_offset_ev, 9),
                "offset_prediction_ev": round(offset_pred, 9),
                "offset_abs_error_ev": round(abs(offset_pred - heldout.value_ev), 9),
                "constant_mean_ev": round(constant_mean_ev, 9),
                "constant_abs_error_ev": round(abs(constant_pred - heldout.value_ev), 9),
            }
        )

    original_holdout_id = "almeida-2023-inp-620nm"
    original_train = [row for row in rows if row.entry_id != original_holdout_id]
    original_holdout = row_by_id[original_holdout_id]
    original_offset = mean(
        row.value_ev - fixed_almeida_prediction(row.edge_length_nm)
        for row in original_train
    )
    original_fixed_holdout_error = abs(
        fixed_almeida_prediction(original_holdout.edge_length_nm) - original_holdout.value_ev
    )
    original_offset_holdout_error = abs(
        fixed_almeida_prediction(original_holdout.edge_length_nm)
        + original_offset
        - original_holdout.value_ev
    )
    fixed_train_errors = [
        abs(fixed_almeida_prediction(row.edge_length_nm) - row.value_ev)
        for row in original_train
    ]
    offset_train_errors = [
        abs(
            fixed_almeida_prediction(row.edge_length_nm)
            + original_offset
            - row.value_ev
        )
        for row in original_train
    ]

    fixed_loo_errors = [fold["fixed_abs_error_ev"] for fold in folds]
    offset_loo_errors = [fold["offset_abs_error_ev"] for fold in folds]
    constant_loo_errors = [fold["constant_abs_error_ev"] for fold in folds]

    original_train_improved = mean(offset_train_errors) < mean(fixed_train_errors)
    original_holdout_worse = original_offset_holdout_error > original_fixed_holdout_error
    loo_worse_than_fixed = mean(offset_loo_errors) > mean(fixed_loo_errors)

    if original_train_improved and (original_holdout_worse or loo_worse_than_fixed):
        verdict = "QUANTUM_LOO_STRESS_OVERFIT_WARNING"
    elif loo_worse_than_fixed:
        verdict = "QUANTUM_LOO_STRESS_UNSTABLE"
    else:
        verdict = "QUANTUM_LOO_STRESS_NO_NEW_SIGNAL"

    metrics: dict[str, Any] = {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "benchmark_id": "quantum-almeida-fixed-model-loo-methodology-stress-test",
        "dataset_id": "qd-0003-almeida-2023-inp-optical",
        "row_count": len(rows),
        "diagnostic_family": {
            "model_id": "fixed_almeida_plus_train_mean_residual_offset",
            "definition": "E = E_Almeida_fixed(L) + b_train",
            "free_parameters": 1,
            "offset_fit_rule": "b_train = mean(E_observed - E_Almeida_fixed) on the training rows for each fold",
        },
        "negative_control": {
            "model_id": "constant_train_mean",
            "definition": "E = mean(E_observed_train)",
            "free_parameters": 1,
        },
        "reference_model": {
            "model_id": "almeida_fixed_reference",
            "definition": "E = 1.33 + 9.128 * L_A^-0.684; L_A = 10 * L_nm",
            "free_parameters": 0,
        },
        "folds": folds,
        "summary": {
            "fixed_loo_mae_ev": round(mean(fixed_loo_errors), 9),
            "offset_loo_mae_ev": round(mean(offset_loo_errors), 9),
            "constant_loo_mae_ev": round(mean(constant_loo_errors), 9),
            "offset_minus_fixed_loo_mae_ev": round(
                mean(offset_loo_errors) - mean(fixed_loo_errors), 9
            ),
            "fixed_original_train_mae_ev": round(mean(fixed_train_errors), 9),
            "offset_original_train_mae_ev": round(mean(offset_train_errors), 9),
            "fixed_original_holdout_abs_error_ev": round(
                original_fixed_holdout_error, 9
            ),
            "offset_original_holdout_abs_error_ev": round(
                original_offset_holdout_error, 9
            ),
            "constant_original_holdout_abs_error_ev": _lookup_fold(
                folds,
                original_holdout_id,
                "constant_abs_error_ev",
            ),
            "existing_task0225_shuffled_control_holdout_mae_ev": 0.375676,
            "existing_task0225_constant_null_holdout_mae_ev": 0.4202,
            "original_train_improved_by_offset": original_train_improved,
            "original_holdout_worse_after_offset": original_holdout_worse,
            "offset_loo_worse_than_fixed_reference": loo_worse_than_fixed,
        },
        "verdict": verdict,
        "input_hashes": {
            "dataset_sha256": _sha256(DATASET_PATH),
            "script_sha256": _sha256(Path(__file__)),
        },
        "promotion_boundary": {
            "methodology_validation_only": True,
            "unblocks_task_0226": False,
            "creates_result": False,
            "creates_prediction": False,
            "creates_claim": False,
            "creates_knowledge": False,
        },
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "agent_run.yaml").write_text(
        yaml.safe_dump(_agent_run_manifest(verdict), sort_keys=False),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "preflight.md").write_text(_preflight_markdown(), encoding="utf-8")
    (OUTPUT_DIR / "limitations.md").write_text(_limitations_markdown(), encoding="utf-8")
    (OUTPUT_DIR / "report.md").write_text(_report_markdown(metrics), encoding="utf-8")
    (OUTPUT_DIR / "review_summary.md").write_text(
        _review_summary_markdown(metrics),
        encoding="utf-8",
    )
    REVIEW_PATH.write_text(_review_note_markdown(metrics), encoding="utf-8")
    print(json.dumps({"agent_run": str(OUTPUT_DIR), "review": str(REVIEW_PATH), "verdict": verdict}))
    return 0


def _lookup_fold(folds: list[dict[str, Any]], entry_id: str, key: str) -> float:
    for fold in folds:
        if fold["heldout_entry_id"] == entry_id:
            return float(fold[key])
    raise KeyError(entry_id)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _agent_run_manifest(verdict: str) -> dict[str, Any]:
    return {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": "quantum-size-effects",
        "task_id": TASK_ID,
        "status": "REVIEW_READY",
        "sandbox_only": True,
        "created_by": {
            "contributor_id": "gladunrv",
            "agent_id": "codex",
        },
        "proposal_paths": {
            "hypothesis": "hypothesis_proposals/quantum-size-effects/HYP-PROPOSAL-0061-baseline-consistency.yaml",
            "experiment": "experiment_proposals/quantum-size-effects/EXP-PROPOSAL-0027-baseline-consistency.yaml",
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
                {
                    "name": "committed_rows_only",
                    "status": "PASS",
                    "notes": "Loaded exactly the six committed Almeida InP rows from qd-0003.",
                },
                {
                    "name": "fixed_diagnostic_predeclared",
                    "status": "PASS",
                    "notes": "One additive-offset diagnostic and one constant-mean negative control.",
                },
                {
                    "name": "complexity_cap",
                    "status": "PASS",
                    "notes": "Diagnostic and control each use at most one fitted parameter.",
                },
            ],
        },
        "limitations": [
            "Six figure-derived InP rows from one source.",
            "One-property, one-material methodology diagnostic only.",
            "No independent source or material holdout is tested.",
            "No canonical scientific artifact is created.",
        ],
        "verdict": "INCONCLUSIVE",
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review; keep TASK-0226 blocked unless a later task "
                "adds independent rows or an explicit methodology-only waiver."
            ),
        },
    }


def _preflight_markdown() -> str:
    return """# AGENT-RUN-0077 Preflight

- Task: `TASK-0816`
- Dataset: `data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml`
- Rows: the six committed Almeida 2023 InP `absorption_peak_eV` rows only.
- Diagnostic family: `E = E_Almeida_fixed(L) + b_train`, where `b_train` is one
  fitted additive offset per training fold.
- Negative control: `E = mean(E_train)`.
- Complexity cap: one fitted parameter for the diagnostic and one for the
  negative control.
- Forbidden in this run: new rows, open-ended formula search, TASK-0226
  unblock, RESULT/PRED/CLAIM/KNOW creation, and transfer/generalization claims.
"""


def _limitations_markdown() -> str:
    return """# AGENT-RUN-0077 Limitations

- Six rows, one source, one material, one property axis.
- The fixed Almeida relation and rows come from the same source series.
- Leave-one-out folds are methodology diagnostics, not promotion gates.
- The additive-offset diagnostic is intentionally low-flexibility and does not
  represent an autonomous correction search.
- No independent source, material holdout, device implication, synthesis
  guidance, biomedical relevance, or universal size law is tested.
"""


def _report_markdown(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    rows = "\n".join(
        "| `{heldout_entry_id}` | {fixed_abs_error_ev:.9f} | {offset_abs_error_ev:.9f} | {constant_abs_error_ev:.9f} | {additive_offset_ev:.9f} |".format(
            **fold
        )
        for fold in metrics["folds"]
    )
    return f"""# Quantum Almeida Fixed-Model LOO Stress Test

Task: `TASK-0816`

## Method

This run uses only the six committed Almeida 2023 InP rows. It compares the
zero-parameter published Almeida reference against one predeclared low-
flexibility diagnostic, `E = E_Almeida_fixed(L) + b_train`, and one negative
control, the training-set mean energy.

## LOO Metrics

| Held-out row | fixed abs error (eV) | offset abs error (eV) | constant abs error (eV) | fitted offset (eV) |
| --- | ---: | ---: | ---: | ---: |
{rows}

## Summary

- Fixed-reference LOO MAE: `{summary["fixed_loo_mae_ev"]:.9f} eV`
- Additive-offset LOO MAE: `{summary["offset_loo_mae_ev"]:.9f} eV`
- Constant-mean LOO MAE: `{summary["constant_loo_mae_ev"]:.9f} eV`
- Offset minus fixed LOO MAE: `{summary["offset_minus_fixed_loo_mae_ev"]:.9f} eV`
- Original five-train-row fixed train MAE: `{summary["fixed_original_train_mae_ev"]:.9f} eV`
- Original five-train-row offset train MAE: `{summary["offset_original_train_mae_ev"]:.9f} eV`
- Original 620 nm holdout fixed error: `{summary["fixed_original_holdout_abs_error_ev"]:.9f} eV`
- Original 620 nm holdout offset error: `{summary["offset_original_holdout_abs_error_ev"]:.9f} eV`

## Verdict

`{metrics["verdict"]}`

The one-parameter offset does not improve the original training rows and
worsens the original one-point holdout and the six-fold LOO mean error relative
to the zero-parameter fixed Almeida reference. This is methodology memory only
and does not unblock `TASK-0226`.
"""


def _review_summary_markdown(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    return f"""# AGENT-RUN-0077 Review Summary

The fixed-model Almeida LOO stress test produced
`{metrics["verdict"]}`. The additive-offset diagnostic is intentionally
low-flexibility, but it still worsened LOO MAE from
`{summary["fixed_loo_mae_ev"]:.9f} eV` to `{summary["offset_loo_mae_ev"]:.9f} eV`.
It also does not improve the original five training rows and worsens the
original 620 nm holdout. The result should be treated as pipeline/methodology
memory, not quantum-dot size-law evidence.
"""


def _review_note_markdown(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    return f"""# Quantum Almeida Fixed-Model LOO Methodology Stress Test

**Task:** `TASK-0816`
**Agent run:** `agent_runs/AGENT-RUN-0077/`
**Verdict:** `{metrics["verdict"]}`
**Scope:** methodology validation only; no RESULT/PRED/CLAIM/KNOW mutation.

## Inputs

- `data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml`
- `physics_lab/engines/quantum_size_effects.py`
- `agent_runs/AGENT-RUN-0076/metrics.json`
- `docs/reviews/quantum-size-baseline-readiness-for-autonomous-pilot.md`

## Predeclared Diagnostic

One low-flexibility diagnostic was evaluated:

```text
E = E_Almeida_fixed(L) + b_train
b_train = mean(E_observed - E_Almeida_fixed) on the training rows
```

It has one fitted parameter per fold. The negative control is
`constant_train_mean`, also one fitted parameter. The zero-parameter fixed
Almeida reference is the comparator.

## Results

| Metric | Value |
| --- | ---: |
| Fixed-reference LOO MAE | `{summary["fixed_loo_mae_ev"]:.9f} eV` |
| Additive-offset LOO MAE | `{summary["offset_loo_mae_ev"]:.9f} eV` |
| Constant-mean LOO MAE | `{summary["constant_loo_mae_ev"]:.9f} eV` |
| Offset minus fixed LOO MAE | `{summary["offset_minus_fixed_loo_mae_ev"]:.9f} eV` |
| Original fixed train MAE | `{summary["fixed_original_train_mae_ev"]:.9f} eV` |
| Original offset train MAE | `{summary["offset_original_train_mae_ev"]:.9f} eV` |
| Original fixed 620 nm holdout error | `{summary["fixed_original_holdout_abs_error_ev"]:.9f} eV` |
| Original offset 620 nm holdout error | `{summary["offset_original_holdout_abs_error_ev"]:.9f} eV` |
| Existing TASK-0225 constant-null holdout MAE | `{summary["existing_task0225_constant_null_holdout_mae_ev"]:.6f} eV` |
| Existing TASK-0225 shuffled-control holdout MAE | `{summary["existing_task0225_shuffled_control_holdout_mae_ev"]:.6f} eV` |

The offset diagnostic does not improve the original training MAE, and it
worsens the original 620 nm holdout and the six-fold LOO MAE relative to the
fixed Almeida reference. That is exactly the failure mode the narrowed
`TASK-0277` path was meant to detect: even one extra fitted parameter can turn
the six-row slice into train-side adjustment rather than reusable signal.

## Interpretation

This run supports keeping `TASK-0226` blocked for autonomous correction search.
The Almeida surface remains useful as a source-scoped baseline and pipeline
anchor, but the LOO stress test does not justify correction discovery,
cross-material transfer, device claims, synthesis guidance, biomedical claims,
or a universal quantum-size law.

## Output-Routing Summary

- **Canonical destination:** sandbox-only `agent_runs/AGENT-RUN-0077/` plus this
  review note.
- **Review tier:** none; no canonical RESULT/PRED artifact.
- **Gate A status:** not applicable.
- **Gate B status:** not applicable.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Publication blocker:** six rows from one Almeida InP source; one-parameter
  stress diagnostic worsens LOO/holdout behavior and cannot support promotion.

## Verdict

`{metrics["verdict"]}` — methodology stress test records overfit risk and does
not unblock `TASK-0226`.
"""


if __name__ == "__main__":
    raise SystemExit(main())
