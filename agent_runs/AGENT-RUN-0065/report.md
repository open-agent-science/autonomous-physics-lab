# AGENT-RUN-0065 - NMD-0003 Uncertainty-Weighted Baseline Diagnostic

**Task:** `TASK-0596`
**Verdict:** `INCONCLUSIVE`

## Summary

This run asks whether weighting the NMD-0003 liquid-drop baseline fit by AME2020
*measurement* uncertainty changes the readiness interpretation or only adds a
limitation note. It uses committed NMD-0003 measured rows and the frozen
`stratified_interleaved_70_30` interpolation split. It does not alter the frozen
gate, baseline identity, or split manifest, and it creates no prediction, claim,
knowledge, or result artifact.

The unweighted ordinary least-squares (OLS) audit baseline reproduces the frozen
gate's `required_audit_baseline` validation MAE (`2.614320` MeV) on the same
split, confirming the diagnostic shares the gate's exact split and fit.

## Uncertainty Coverage (train split, 1617 rows)

- Present positive sigma: `1616`.
- Missing sigma: `0`.
- Non-positive (ambiguous) sigma: `1` -> `C-12`.

`C-12` defines the atomic mass unit, so its atomic-mass uncertainty is exactly
zero. It is reported as ambiguous and excluded from the weighted fits rather than
assigned infinite weight.

## Decision Metrics (validation holdout vs OLS audit baseline `2.614320` MeV)

| weight policy | val MAE (MeV) | rel. improvement | effective sample fraction | readiness-relevant |
| --- | ---: | ---: | ---: | --- |
| `inverse_variance` | `67.678953` | `-24.89` | `0.001363` | `False` |
| `inverse_sigma` | `39.007964` | `-13.92` | `0.002351` | `False` |
| `inverse_variance_floored_0p1mev` | `2.559768` | `0.0209` | `0.973923` | `False` |
| `inverse_variance_floored_1mev` | `2.614166` | `0.00006` | `1.0` | `False` |

Raw inverse-variance weighting collapses the effective sample onto roughly two of
1616 rows (top single nuclide carries `50.75%` of all weight) and worsens the
validation holdout by ~26x, because the liquid-drop model error (~MeV) is far
larger than the AME2020 measurement error (~keV). Floor-guarded variants at or
above the model-error scale recover the unweighted fit.

## Interpretation

No predeclared uncertainty-weighted policy produces a readiness-relevant
improvement (`>5%` validation MAE gain with effective sample fraction `>=0.5`).
Measurement-uncertainty weighting therefore adds a limitation note rather than
changing candidate-readiness interpretation. Future bounded residual-feature
sprints should keep the unweighted OLS audit baseline and the frozen
region-stratified readiness baseline as the contract.

## Output Routing Summary

- Task verdict: `INCONCLUSIVE`.
- Canonical destination: `agent_runs/AGENT-RUN-0065/metrics.json`, `agent_runs/AGENT-RUN-0065/report.md`, `docs/reviews/nmd0003-uncertainty-weighted-baseline-diagnostic.md`.
- Review tier: `none`.
- Gate A status: `not_attempted`.
- Gate B status: `not_applicable`.
- Claim impact: `none`.
- Knowledge impact: `none`.
- Result impact: `no RESULT artifact created`.
