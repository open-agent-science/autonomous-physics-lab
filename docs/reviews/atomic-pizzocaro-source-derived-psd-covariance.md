# Atomic Pizzocaro Source-Derived PSD Covariance

- Task: `TASK-0666`
- Campaign: Atomic Clock Residuals
- Artifact:
  `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/vlbi_source_derived_psd_covariance_approximation.yaml`
- Covariance state: `COV_SOURCE_DERIVED_PSD_APPROX`
- Verdict: `PSD_APPROXIMATION_COMMITTED_SENSITIVITY_ONLY`

## Scope

This task turns the Pizzocaro VLBI per-window diagnostic ledger into a
deterministic source-derived PSD covariance approximation. It uses only
committed Pizzocaro source artifacts and does not aggregate windows into
benchmark rows, fit constants drift, compare sources, create predictions, or
promote claims.

## Frozen Recipe

The artifact freezes:

- row/window order: `PIZZOCARO-VLBI-W01` through `PIZZOCARO-VLBI-W10`;
- unit convention: dimensionless fractional uncertainty, with covariance
  entries reported in `(1e-17)^2 = 1e-34` relative-units-squared;
- diagonal source: each window's final `u` from the committed ledger, squared;
- off-diagonal recipe: common-mode `uB1_comb`, `uB2`, and `uB4_comb`, plus
  same-sign clock terms `uB1_clock` and `uB4_clock`;
- clock-correlation assumption: primary matrix uses fully correlated clock
  terms, while the artifact also records the uncorrelated-clock sensitivity
  lower bound;
- PSD checks for both sensitivity bounds;
- omitted-component list for VLBI↔IPPP/PPP coupling, network/geopotential
  terms, deadtime/drift, and statistical cross-window correlation.

## PSD And Sensitivity Result

Both committed sensitivity matrices pass the PSD check. This clears the policy
bar for `COV_SOURCE_DERIVED_PSD_APPROX`, not for `COV_EXACT_COMMITTED`.
Downstream benchmark consumers may use the matrix only as an approximate
covariance sensitivity input and must still report diagonal-only comparators.

## Stop Conditions Preserved

- No `data/atomic_clocks/acr-*.yaml` benchmark rows are added.
- No cross-window aggregate value or uncertainty is computed.
- No benchmark metric, constants-drift fit, prediction, claim, knowledge, or
  result artifact is created.
- The matrix must not be described as a paper-published exact covariance.

## Output Routing

- Task verdict: `PSD_APPROXIMATION_COMMITTED_SENSITIVITY_ONLY`.
- Canonical destination:
  `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/vlbi_source_derived_psd_covariance_approximation.yaml`
  and this review note.
- Review tier: `none`.
- Gate A status: not attempted; no `RESULT-*` or `PRED-*` artifact.
- Gate B status: not applicable.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Result impact: no `results/` artifact created or modified.
- Limitations / blockers: approximate covariance only; a later benchmark task
  must decide whether the sensitivity input is admissible for any metric.
