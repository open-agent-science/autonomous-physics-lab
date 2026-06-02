# NMD-0003 Baseline-Family Gate — Review (TASK-0535)

Review note for [AGENT-RUN-0056](../../agent_runs/AGENT-RUN-0056/report.md).
The run compares physically standard nuclear-mass baseline *families* on the
committed NMD-0003 AME2020 measured surface under two predeclared deterministic
splits, turning the TASK-0531 validation-holdout regression into a concrete
baseline-family gate. It introduces no residual-feature, shell-axis, or
local-curvature term.

## Result

- **Verdict:** `INCONCLUSIVE` sandbox benchmark evidence.
- Dataset: NMD-0003, 2309 committed measured AME2020 rows; post-AME2020 primary
  holdout excluded.
- Declared families: inherited frozen RESULT-0015, NMD-0003 OLS refit (TASK-0531),
  weighted least squares (`1/A`), ridge (`alpha=1.0`), and a region-stratified
  OLS diagnostic.
- Declared splits: `sorted_aZN_70_30` (heavy-mass tail holdout — extrapolation)
  and `stratified_interleaved_70_30` (every region represented — interpolation).

OLS refit validation MAE relative improvement versus the inherited baseline:
`-0.342` on the sorted split, `+0.475` on the stratified split. The
region-stratified diagnostic reaches `+0.619` (validation MAE 1.899 MeV) under
the stratified split.

## Interpretation

The TASK-0531 validation regression is **dominated by domain mismatch**, not by
baseline-family weakness. The sorted split places the entire heavy-mass tail in
the validation holdout, forcing extrapolation; under an interpolation split the
same refit nearly halves the validation MAE. A secondary structural limitation
is real but smaller: fitted liquid-drop coefficients drift across mass regions
(largest relative range `0.611` for `pairing`), so a single global
five-coefficient vector cannot fit all regions at once. Ridge at `alpha=1.0`
over-regularizes and is reported only as a declared negative family member.

This sharpens, rather than overturns, the TASK-0531 reading: TASK-0517 remains
control-dominated factory memory, and the inherited-vs-refit comparison on the
sorted split must not be used as a standalone Nuclear readiness gate.

## Recommendation

`create_narrower_baseline_follow_up`. Before any residual-feature sprint, freeze
a stratified (interpolation) validation split as the readiness gate, freeze the
working baseline family (OLS for a single global vector, or the region-stratified
diagnostic if region-aware coefficients are acceptable), and only then permit a
bounded residual-feature sprint with that baseline frozen.

## Output Routing

- **Canonical destination:** sandbox evidence in `agent_runs/AGENT-RUN-0056/`
  plus this review note.
- **Review tier:** none.
- **Gate A / Gate B:** not applicable.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Publication blocker:** baseline-diagnostic benchmark scope; both splits are
  retrospective inside AME2020 measured rows, not a post-AME2020 reveal.

## Follow-Up

Recommended next step: open a narrower baseline follow-up task that freezes the
stratified validation split and the winning baseline family, keeping baseline
diagnostics separate from residual-feature discovery, before the next Nuclear
factory sprint runs on NMD-0003.
