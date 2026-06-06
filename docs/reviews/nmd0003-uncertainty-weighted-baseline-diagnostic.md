# NMD-0003 Uncertainty-Weighted Baseline Diagnostic

**Task:** `TASK-0596`
**Campaign:** Nuclear Mass Surface
**Status:** diagnostic-only
**Verdict:** `INCONCLUSIVE`
**Run:** `agent_runs/AGENT-RUN-0065/metrics.json`

## Scope

This diagnostic checks whether weighting the NMD-0003 liquid-drop baseline fit by
AME2020 *measurement* uncertainty changes the readiness interpretation before any
further residual-feature sprint, or whether it only adds a limitation note. It
uses committed NMD-0003 measured rows only and the frozen
`stratified_interleaved_70_30` interpolation split from
`data/nuclear_masses/nmd-0003-stratified-baseline-gate.yaml`.

It does not fetch external data, score the post-AME2020 reveal holdout, introduce
a residual-feature family, alter the frozen gate / baseline identity / split
manifest, or promote any prediction, claim, knowledge, or result artifact.

## Method

- Sort committed measured rows by `(A, Z, N)`; assign a row to the validation
  holdout when its sorted index modulo 10 is `>= 7` (train `1617`, validation
  `692`, total `2309`). This mirrors the frozen gate exactly.
- Fit the unweighted ordinary least-squares (OLS) audit baseline on all train
  rows. It reproduces the frozen gate's `required_audit_baseline` validation MAE
  of `2.614320` MeV, confirming the split and fit match the gate.
- Propagate each row's binding-energy measurement uncertainty `sigma` (MeV) from
  the committed atomic-mass uncertainty. Report rows with missing or non-positive
  (ambiguous) `sigma` explicitly and exclude them from the weighted fits.
- Fit four *predeclared* uncertainty-weighted least-squares variants on the
  positive-`sigma` rows and score each on the frozen validation holdout.

The weight policies are declared before scoring:

| policy | weight |
| --- | --- |
| `inverse_variance` | `w = 1 / sigma^2` |
| `inverse_sigma` | `w = 1 / sigma` |
| `inverse_variance_floored_0p1mev` | `w = 1 / max(sigma, 0.1 MeV)^2` |
| `inverse_variance_floored_1mev` | `w = 1 / max(sigma, 1.0 MeV)^2` |

## Uncertainty Coverage

On the `1617`-row train split, `1616` rows carry a positive `sigma`, none are
missing, and one is ambiguous: `C-12`. `C-12` defines the atomic mass unit, so
its atomic-mass uncertainty is exactly zero; raw inverse-variance weighting would
assign it infinite weight. It is reported and excluded rather than imputed.

## Result

Validation-holdout MAE versus the unweighted OLS audit baseline (`2.614320` MeV):

| weight policy | val MAE (MeV) | rel. improvement | effective sample fraction | readiness-relevant |
| --- | ---: | ---: | ---: | --- |
| `inverse_variance` | `67.678953` | `-24.89` | `0.001363` | `False` |
| `inverse_sigma` | `39.007964` | `-13.92` | `0.002351` | `False` |
| `inverse_variance_floored_0p1mev` | `2.559768` | `0.0209` | `0.973923` | `False` |
| `inverse_variance_floored_1mev` | `2.614166` | `0.00006` | `1.0` | `False` |

Raw inverse-variance weighting collapses the effective sample size to roughly two
of `1616` rows (the single most precise nuclide carries `50.75%` of all weight)
and worsens the validation holdout by about `26x`. Inverse-sigma weighting is
less extreme but still degrades the fit. The two floor-guarded variants, which cap
how precise a measurement is allowed to look, recover the unweighted fit: at the
`1.0` MeV liquid-drop model-error scale the weighting becomes effectively uniform
and the validation MAE returns to `2.614166` MeV.

The mechanism is physical: AME2020 measurement uncertainties are at the keV scale,
while the liquid-drop baseline residual is at the MeV scale. Inverse-variance
weighting by measurement uncertainty therefore concentrates the fit on a handful
of ultra-precise light nuclides whose measurement precision has no bearing on the
model's structural error.

## Readiness Interpretation

Under the predeclared rule (a weighted fit is readiness-relevant only if it beats
the unweighted OLS audit baseline by more than `5%` on the validation holdout
while keeping an effective sample fraction of at least `0.5`), no uncertainty-
weighted policy qualifies. The marginal `2.1%` improvement of the `0.1` MeV
floored variant is below the threshold and is not a basis for changing the frozen
baseline identity.

**Decision:** measurement-uncertainty weighting adds a limitation note rather than
changing candidate-readiness interpretation. Future bounded residual-feature
sprints should keep the unweighted OLS audit baseline and the frozen
region-stratified readiness baseline as the contract, and should not adopt raw
measurement-uncertainty weighting.

## Limitations

- Retrospective diagnostic on committed AME2020 measured rows under the frozen
  stratified interpolation split; not a post-AME2020 reveal.
- All baselines are five-coefficient liquid-drop fits; no residual-feature,
  shell-axis, or local-curvature family is tested.
- The weight-policy set is bounded and predeclared; it does not exhaust every
  possible measurement-aware weighting scheme.
- Sandbox diagnostic evidence only. No PRED, CLAIM, KNOW, or RESULT artifact is
  created and the frozen gate is unchanged.

## Output Routing Summary

- Task verdict: `INCONCLUSIVE`.
- Canonical destination: `agent_runs/AGENT-RUN-0065/metrics.json`,
  `agent_runs/AGENT-RUN-0065/report.md`, this review.
- Review tier: `none`.
- Gate A status: `not_attempted`.
- Gate B status: `not_applicable`.
- Claim impact: `none`.
- Knowledge impact: `none`.
- Result impact: `no RESULT artifact created`.
