# TASK-1054: OQMD within-source baseline/control preflight

## Decision

**`CONTRACT_READY_FOR_FROZEN_SPLIT`.** A value-blind contract now fixes the
only model, null, control, metric, margin, sensitivity, and stop rules allowed
for the first bounded OQMD benchmark.

## Clean-session declaration

- Contributor: `akutenyov`
- Agent: `Codex`
- Session: `codex-task1054-clean-20260716`
- OQMD target values or aggregate summaries inspected: **no**
- Rows assigned, fetched, fit, or scored: **no**

The contract was written from the task requirements, RESULT-0021 methodology,
and published OQMD field semantics. It did not open the OQMD raw or normalized
target surfaces.

## Frozen scientific scope

The future objective is OQMD `delta_e` under OQMD's own computed-DFT
reference/correction semantics. It is not numerically pooled with Materials
Project `formation_energy_per_atom`; no equality, offset, or cross-database
calibration claim is permitted.

The primary model is the train-only mean of an unordered non-oxygen cation
pair, with a train-only global-mean fallback for an unseen pair. Structural
descriptors and feature expansion are forbidden.

Required comparators are:

1. train-only global median;
2. train-only IUPAC cation-group-pair mean with global-mean fallback;
3. deterministic train-label shuffles;
4. deterministic cation-pair-label shuffles;
5. canonical-versus-reversed row-order invariance.

Shuffle and identity-group-preserving sensitivity seeds are
`1054, 2054, 3054, 4054, 5054`.

## Metrics and survival rule

- Primary metric: MAE in eV/atom.
- Secondary metric: RMSE in eV/atom.
- Absolute tolerance: `1e-12`.
- Relative tolerance: `1e-9`.
- Tie within tolerance: failure to survive.

For every required null and every control instance:

```text
model_mae <= comparator_mae - max(0.02 eV/atom, 0.05 * comparator_mae)
```

The absolute floor prevents a negligible win from being promoted; the relative
term scales the requirement when a comparator error is larger. All five
sensitivity seeds must pass. The rule was fixed before scoring.

## Missingness and stops

Non-numeric, missing, or non-finite targets must be excluded before future
partitioning and their counts reported. No imputation is allowed. Empty or
ambiguous eligibility is `INCONCLUSIVE`.

Execution must stop on contamination, unresolved `delta_e` semantics,
unavailable controls, invalid threshold application, identity leakage,
row-order drift, or insufficient group coverage. No contract term may be
changed after observing a score.

## Output routing

- Canonical destination: the adjacent machine-readable contract.
- Review tier: `none`.
- Gate A/B: not attempted.
- Claim and knowledge impact: none.
- Next gate: the frozen TASK-1053 split followed by a separate reviewed scoring
  task.
- Limitation: methodology readiness only; no OQMD result or materials-law claim.
