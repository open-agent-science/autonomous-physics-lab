# NMD-0003 Broad-Surface Baseline Freeze — Review (TASK-0531)

Review note for [AGENT-RUN-0055](../../agent_runs/AGENT-RUN-0055/report.md).
The run compares inherited RESULT-0015 / NMD-0002 frozen coefficients with a
train-fitted NMD-0003 baseline over the committed AME2020 measured training
surface.

## Result

- **Verdict:** `INCONCLUSIVE` sandbox benchmark evidence.
- Dataset: NMD-0003, 2309 committed measured AME2020 rows.
- Split: 1616 train rows and 693 validation-holdout rows, with primary
  post-AME2020 holdout rows excluded by the split manifest.
- Train MAE relative improvement: `0.441918`.
- Full-surface MAE relative improvement: `0.155469`.
- Validation-holdout MAE relative improvement: `-0.341856`.

The train-fitted broad-surface baseline improves train/full-surface MAE but
worsens the predeclared validation holdout. This is not a benchmark promotion
result and does not authorize a new residual-family sprint by itself.

## TASK-0517 Interpretation

TASK-0517 should remain interpreted as control-dominated factory memory under a
mismatched inherited baseline. TASK-0531 adds a sharper limitation: a simple
NMD-0003 least-squares refit is not enough, because it regresses on the
predeclared validation holdout.

## Output Routing

- **Canonical destination:** sandbox evidence in `agent_runs/AGENT-RUN-0055/`
  plus this review note.
- **Review tier:** none.
- **Gate A / Gate B:** not applicable.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Publication blocker:** validation holdout regression and scoped sandbox
  benchmark status.

## Follow-Up

Recommended next step: define a better broad-surface baseline readiness task
before running more expressive Nuclear residual-feature families on NMD-0003.
Candidate directions include stratified split policies, mass-region-aware
baseline diagnostics, or an explicit baseline-family comparison that remains
separate from residual-feature hypothesis testing.
