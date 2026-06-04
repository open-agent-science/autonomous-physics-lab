# NMD-0003 Stratified Baseline Gate

**Task:** `TASK-0552`
**Campaign:** Nuclear Mass Surface
**Status:** frozen readiness gate
**Verdict:** `STRATIFIED_BASELINE_GATE_FROZEN`

## Scope

This task freezes the NMD-0003 split/baseline contract for future bounded
Nuclear residual-feature work. It uses only committed NMD-0003 measured rows and
the committed baseline-family evidence from `AGENT-RUN-0056`. It does not fetch
external data, score post-AME2020 holdout rows, introduce residual-feature
candidates, write prediction entries, or promote claims.

## Frozen Gate

The primary readiness split is now:

- `stratified_interleaved_70_30`
- row order: sort committed NMD-0003 measured rows by `(A, Z, N)`
- train rows: `sorted_index % 10 in {0, 1, 2, 3, 4, 5, 6}`
- validation holdout rows: `sorted_index % 10 in {7, 8, 9}`
- train count: `1617`
- validation holdout count: `692`

This split is an interpolation gate: every mass region is represented in train
and validation. The inherited `sorted_aZN_70_30` split remains useful only as a
heavy-tail extrapolation diagnostic.

## Frozen Baseline Contract

The primary readiness baseline is the region-stratified liquid-drop diagnostic
from `AGENT-RUN-0056`:

- baseline id: `nmd0003_region_stratified_diagnostic`
- fit policy: train-split-only OLS per A region
- stratified validation MAE: `1.899279` MeV
- stratified validation RMSE: `2.587583` MeV
- MAE relative improvement versus inherited RESULT-0015/NMD-0002 baseline:
  `0.618566`

Any future residual-feature sprint using this primary readiness baseline should
also report the single-vector OLS audit baseline:

- baseline id: `nmd0003_train_fitted_ols`
- stratified validation MAE: `2.614320` MeV
- stratified validation RMSE: `3.804107` MeV
- MAE relative improvement versus inherited baseline: `0.474964`

The inherited RESULT-0015/NMD-0002 frozen baseline remains the control baseline
for continuity.

## Future Sprint Decision

A future bounded Nuclear residual-feature sprint is allowed only under this
contract:

1. use committed NMD-0003 measured rows only;
2. use `stratified_interleaved_70_30` as the primary validation gate;
3. compare candidates against both the primary region-stratified readiness
   baseline and the required global OLS audit baseline;
4. report `sorted_aZN_70_30` only as extrapolation diagnostic;
5. exclude post-AME2020 holdout rows from fitting and scoring;
6. avoid unchanged reruns of the control-dominated `TASK-0517` slate;
7. do not write PRED, CLAIM, KNOW, or discovery wording.

This is permission for a bounded, predeclared residual-feature sprint, not a
claim that any residual structure exists.

## Rationale

`AGENT-RUN-0056` showed that the TASK-0531 validation regression is dominated by
split/domain mismatch. The global OLS refit regressed on the sorted heavy-tail
holdout (`-0.341856` relative MAE improvement) but improved on the stratified
holdout (`+0.474964`). The region-stratified diagnostic improved the
stratified holdout most strongly (`+0.618566`).

The sorted split should therefore no longer be used as the sole Nuclear
readiness gate. It asks a train fit to extrapolate into the heavy-mass tail and
confounds baseline quality with domain shift.

## Output Routing Summary

- Task verdict: `STRATIFIED_BASELINE_GATE_FROZEN`
- Canonical destination:
  `data/nuclear_masses/nmd-0003-stratified-baseline-gate.yaml` and this review
  note.
- Review tier: `none`
- Gate A status: not attempted; no benchmark `RESULT-*` artifact is published.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Result impact: no `RESULT-*` artifact created or modified.
- Limitations: retrospective AME2020 measured-row readiness gate only; no
  post-AME2020 reveal scoring and no residual-feature evidence.
