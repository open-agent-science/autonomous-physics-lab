# AGENT-RUN-0056 — NMD-0003 Baseline-Family Gate (TASK-0535)

Sandbox benchmark run comparing physically standard nuclear-mass baseline
*families* on the committed NMD-0003 AME2020 measured training surface. The run
turns the TASK-0531 validation-holdout regression into a concrete decision: it
asks whether that regression is dominated by a domain mismatch in the split or
by weakness of the liquid-drop baseline family. No residual-feature family,
shell-axis term, local-curvature term, high-error cluster label, or post-hoc
correction term is introduced; the only degrees of freedom are the five
liquid-drop coefficients and predeclared fit policies.

- Config: `examples/benchmarks/nuclear_mass_baseline_family_nmd0003.yaml`
- Dataset: `data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml`
- Split manifest: `data/nuclear_masses/nmd-0003-split-manifest.yaml`
- Inherited baseline: `results/EXP-0012/RUN-0001/result.yaml`
  (`model_fitted_semi_empirical`)
- Prior run: `agent_runs/AGENT-RUN-0055/metrics.json` (TASK-0531)
- Rows: 2309 committed measured AME2020 rows; post-AME2020 primary holdout
  excluded.

## Declared Baseline Families

All families were declared before metrics were read:

1. `inherited_result0015_nmd0002_frozen` — control; frozen RESULT-0015 /
   NMD-0002 coefficients, no refit.
2. `nmd0003_train_fitted_ols` — ordinary least squares on the train split (the
   TASK-0531 global refit).
3. `nmd0003_train_fitted_wls` — weighted least squares, per-row weights `1/A`
   (down-weights heavy-mass leverage).
4. `nmd0003_train_fitted_ridge` — ridge-regularized liquid-drop coefficients on
   standardized design columns, penalty `alpha=1.0`, no intercept.
5. `nmd0003_region_stratified_diagnostic` — independent OLS coefficients fit per
   A region (`A<=40`, `41<=A<=100`, `101<=A<=180`, `A>180`) on the train split,
   each region scored with its own coefficients.

## Declared Splits

- `sorted_aZN_70_30` — inherited TASK-0516/TASK-0531 split. Sort by `(A, Z, N)`,
  first 70% train, trailing 30% validation. Because `A` is the primary key, the
  validation holdout is the heavy-mass tail — an **extrapolation** holdout.
- `stratified_interleaved_70_30` — same sorted order, but a row is assigned to
  validation when its sorted index modulo 10 is `>= 7`. Every mass region is
  represented in both train and validation — an **interpolation** holdout.

## Result

**Verdict: INCONCLUSIVE sandbox benchmark evidence.**

Validation-holdout MAE (MeV) by family and split:

| family | sorted (extrapolation) | stratified (interpolation) |
| --- | ---: | ---: |
| inherited frozen | 5.761 | 4.979 |
| OLS refit (TASK-0531) | 7.730 | 2.614 |
| WLS `1/A` | 19.823 | 3.903 |
| ridge `alpha=1.0` | 26.569 | 10.212 |
| region-stratified diagnostic | 7.649 | 1.899 |

Validation MAE relative improvement versus the inherited frozen baseline:

| family | sorted | stratified | domain-mismatch signature |
| --- | ---: | ---: | :---: |
| OLS refit | −0.342 | +0.475 | yes |
| WLS `1/A` | −2.441 | +0.216 | yes |
| ridge `alpha=1.0` | −3.612 | −1.051 | no |
| region-stratified | −0.328 | +0.619 | yes |

## Interpretation

**The TASK-0531 validation regression is dominated by domain mismatch, not
baseline-family weakness.** The OLS refit regresses on the sorted holdout
(−0.342) yet improves the stratified holdout strongly (+0.475). The sorted
split places the entire heavy-mass tail (`A>180`, `Z>82`, `N>126`) in the
validation holdout, so the train fit is being asked to extrapolate far beyond
its support. Under an interpolation split, the same refit nearly halves the
validation MAE (from 4.979 to 2.614 MeV).

A secondary, structural limitation is also visible and is independent of the
split. The region-stratified diagnostic shows the fitted liquid-drop
coefficients drift across mass regions — the largest relative coefficient range
is `0.611` for `pairing`, with `coulomb` at `0.266` and `asymmetry` at `0.204`.
A single global five-coefficient vector therefore cannot fit all mass regions at
once. Under the interpolation split the region-stratified diagnostic is the best
family (validation MAE 1.899 MeV, +0.619 relative improvement).

Ridge at `alpha=1.0` on standardized columns over-regularizes and is not
competitive on either split; it is reported as a declared negative member of the
family rather than a tuned candidate.

## Recommendation

`create_narrower_baseline_follow_up`.

The TASK-0531 sorted-split holdout conflates heavy-mass extrapolation with
baseline quality and should not be used as the Nuclear readiness gate by itself.
Before any residual-feature sprint, a narrower follow-up should:

1. freeze a stratified (interpolation) validation split as the readiness gate;
2. freeze the working baseline family — OLS for a single global vector, or the
   region-stratified diagnostic if region-aware coefficients are acceptable;
3. only then permit a bounded residual-feature sprint with that baseline frozen.

This keeps baseline diagnostics separate from residual-law discovery and gives
the next sprint an interpolation gate that measures genuine surface skill rather
than heavy-mass extrapolation.

## Residual Map Scope

The metrics file records, for the primary `sorted_aZN_70_30` split, residual
summaries overall and by A range, Z range, N range, magic-distance bin,
odd/even pairing class, neutron-richness bin, plus the top absolute residual
rows for every family. The `stratified_interleaved_70_30` split records overall
train/validation/full residual summaries and comparisons for every family. The
`region_coefficient_diagnostic` block records per-region and global train
coefficients and their spread.

## Output Routing

- **Verdict:** `INCONCLUSIVE`
- **Canonical destination:** sandbox evidence in `agent_runs/AGENT-RUN-0056/`
  plus review note in `docs/reviews/nmd0003-baseline-family-gate.md`.
- **Review tier:** none.
- **Gate A / Gate B:** not applicable; no canonical `RESULT-*` or `PRED-*`
  artifact is published.
- **Claim impact:** none.
- **Knowledge impact:** none; the follow-up direction is left as a maintainer
  decision, not a knowledge entry.
- **Publication blocker:** baseline-diagnostic benchmark scope; both splits are
  retrospective inside AME2020 measured rows, not a post-AME2020 reveal.

## Limitations

- Both splits are retrospective within AME2020 measured rows, not a
  post-AME2020 reveal.
- All families are five-coefficient liquid-drop baselines; no residual-feature,
  shell-axis, or local-curvature family is tested.
- The primary post-AME2020 holdout remains excluded and unscored.
- Ridge uses a single declared `alpha=1.0`; no penalty sweep was performed, so
  ridge is reported only as a declared family member, not a tuned baseline.
- Sandbox benchmark evidence only; no PRED, CLAIM, KNOW, or discovery wording is
  promoted.
