# Quantum Almeida Fixed-Model LOO Methodology Stress Test

**Task:** `TASK-0816`
**Agent run:** `agent_runs/AGENT-RUN-0077/`
**Verdict:** `QUANTUM_LOO_STRESS_UNSTABLE`
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
| Fixed-reference LOO MAE | `0.063812943 eV` |
| Additive-offset LOO MAE | `0.077209343 eV` |
| Constant-mean LOO MAE | `0.263400000 eV` |
| Offset minus fixed LOO MAE | `0.013396400 eV` |
| Original fixed train MAE | `0.066896529 eV` |
| Original offset train MAE | `0.069212617 eV` |
| Original fixed 620 nm holdout error | `0.048395010 eV` |
| Original offset 620 nm holdout error | `0.059975446 eV` |
| Existing TASK-0225 constant-null holdout MAE | `0.420200 eV` |
| Existing TASK-0225 shuffled-control holdout MAE | `0.375676 eV` |

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

`QUANTUM_LOO_STRESS_UNSTABLE` — methodology stress test records overfit risk and does
not unblock `TASK-0226`.
