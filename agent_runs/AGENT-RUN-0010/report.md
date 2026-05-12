# Agent Run AGENT-RUN-0010 - Neutron-Rich Nuclear Sandbox Batch

**Task:** `TASK-0202`
**Lane:** neutron-rich residual corrections (second nuclear sandbox batch)
**Status:** SANDBOX_COMPLETE
**Claim boundary:** sandbox-only; no canonical result, claim, or knowledge artifact is updated.

## Scope

This batch generates five neutron-rich residual hypothesis proposals
(`HYP-PROPOSAL-0033` through `HYP-PROPOSAL-0037`), rejects three before
execution, and executes two:

- `HYP-PROPOSAL-0033` — quartic isospin-asymmetry residual
  (`r_corr = a * I^2 + b * I^4` with `I = (N - Z) / A`). Run as a stability
  test on the shape of `HYP-PROPOSAL-0022`'s prior quadratic-asymmetry
  improvement, not as a candidate for promotion.
- `HYP-PROPOSAL-0034` — asymmetric neutron-excess residual
  (`r_corr = c * max(N - Z, 0)^2 / A`). Designed so that the feature is
  identically zero on proton-rich rows (`N < Z`), addressing the one-way
  subset trade documented in
  [post-ame2020-timesplit-failure-analysis.md](../../docs/reviews/post-ame2020-timesplit-failure-analysis.md).

The lane does not target individual shell closures or isotopic chains
identified retrospectively on the post-AME2020 holdout. Such targeted
proposals were rejected explicitly under
[../../docs/nuclear-mass-robustness-gate.md](../../docs/nuclear-mass-robustness-gate.md)
leakage rules.

## Inputs

- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`
- `results/EXP-0012/RUN-0001/result.yaml` (frozen RESULT-0015 baseline)
- `agent_runs/AGENT-RUN-0006/metrics.json` (split-sensitivity context)
- `agent_runs/AGENT-RUN-0008/metrics.json` (post-AME2020 time-split context, including HYP-PROPOSAL-0022 negative-control reference)

## Method

Deterministic. For each executed family:

1. NMD-0002 four-holdout cross-validation
   (`random_stratified`, `oxygen_chain`, `magic_heavy_region`,
   `neutron_rich_edge`): fit linear coefficients on the holdout complement,
   evaluate on the holdout, report per-holdout MAE and RMSE deltas vs the
   frozen baseline residuals.
2. Post-AME2020 evaluation: fit linear coefficients once on the full
   NMD-0002 residual surface, then apply to the 295-row post-AME2020
   primary holdout. Report feature-activation counts, per-subset MAE
   (`primary`, `magic_any`, `near_magic`, `neutron_rich_delta_ge_20`,
   `neutron_rich_delta_ge_30`, `proton_rich_n_lt_z`, `heavy_a_ge_100`,
   `odd_a`), and the top 10 absolute residuals.

All numbers are reproducible from `scripts/run_nuclear_neutron_rich_batch.py`
and the recomputation test `tests/test_nuclear_neutron_rich_batch.py`.

## Structured Holdout Result

| Candidate | Improved | Regressed | Mean delta MAE (MeV) | Worst regression (MeV) | Structured verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| `HYP-PROPOSAL-0033` | 0 | 4 | +2.3105 | 5.9325 | `OVERFITTED` |
| `HYP-PROPOSAL-0034` | 0 | 4 | +0.9939 | 2.3910 | `OVERFITTED` |

Both candidates fail the structured-holdout protocol. For
`HYP-PROPOSAL-0033`, the two-parameter fit on 8-9 rows oscillates strongly
between holdouts because the residual surface is not well-described by a
polynomial in `I` on the small slice. For `HYP-PROPOSAL-0034`, despite the
post-AME2020 coefficient being essentially zero (see below), the
per-complement fits produce non-zero coefficients that overshoot on the
holdout rows.

## Post-AME2020 Primary Result (n=295)

Baseline primary MAE: `4.5526 MeV`.

| Candidate | Primary delta MAE | Magic-any | Near-magic | Neutron-rich (>=20) | Neutron-rich (>=30) | Proton-rich | Heavy A>=100 | Odd-A |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `HYP-PROPOSAL-0033` | +0.5629 | +0.4987 | +0.4308 | +0.9006 | +0.5989 | +0.0742 | +0.6739 | +0.5671 |
| `HYP-PROPOSAL-0034` | -3.9e-13 | -3.6e-13 | -2.9e-13 | -5.2e-13 | -6.9e-13 | +2.0e-14 | -4.7e-13 | -4.6e-13 |

Two distinct readings:

- The quartic-asymmetry candidate (`HYP-PROPOSAL-0033`) regresses the
  primary surface by `+0.56 MeV`. Crucially, this is the opposite sign of
  the prior `HYP-PROPOSAL-0022` quadratic-only improvement
  (`-0.39 MeV` per `AGENT-RUN-0008`). Adding one polynomial degree to the
  same family inverts the aggregate sign — strong evidence that the prior
  improvement was **shape-specific**, not a general asymmetry signal.
- The asymmetric neutron-excess candidate (`HYP-PROPOSAL-0034`) fits a
  near-zero coefficient (`~3.5e-13`) on the full NMD-0002 residual surface
  because the `(N - Z)^2 / A` feature, weighted toward heavy nuclei, is
  essentially orthogonal to the training residuals on the 11-row slice.
  All post-AME2020 subset deltas are floating-point noise (`<= 1e-12`).
  The candidate is effectively null on the time-split surface, while the
  structured-holdout protocol still records `OVERFITTED` because
  per-complement fits do produce non-zero coefficients.

## Feature Activation

| Candidate | Feature | Activation count on primary (n=295) |
| --- | --- | ---: |
| `HYP-PROPOSAL-0033` | `i_sq` | 292 |
| `HYP-PROPOSAL-0033` | `i_quartic` | 292 |
| `HYP-PROPOSAL-0034` | `neutron_excess_sq_over_a` | 264 |

`HYP-PROPOSAL-0034` is zero on the 28 proton-rich rows (`N < Z`) and on
the 3 `N = Z` rows in the primary holdout (by construction), matching the
expected `295 - 31 = 264`. The dormant-feature failure mode documented in
`AGENT-RUN-0008` does not apply in this lane.

## Negative-Control Reference (HYP-PROPOSAL-0022)

From `AGENT-RUN-0008` on the same post-AME2020 primary surface:

- `HYP-PROPOSAL-0022` (`r_corr = a * I + b * I^2`): primary delta MAE
  `-0.3886 MeV`; proton-rich subset delta MAE `+0.7910 MeV`.
- `HYP-PROPOSAL-0033` (this run): primary delta MAE `+0.5629 MeV`;
  proton-rich subset delta MAE `+0.0742 MeV`.
- `HYP-PROPOSAL-0034` (this run): primary delta MAE `~0 MeV`; proton-rich
  subset delta MAE `~0 MeV` (by construction).

Reading: `HYP-PROPOSAL-0022`'s aggregate improvement does not extend to a
higher-degree polynomial; adding a quartic term reverses the sign. This
confirms the prior gate outcome `ALLOW_ONLY_AS_NEGATIVE_CONTROL` and
sharpens the interpretation: the improvement was not a robust polynomial
expansion of asymmetry physics but a fortuitous quadratic fit on the small
training surface.

## Worst-Case Residuals After Correction

The In/Sb N=82 cluster persists. Top three absolute residuals:

- `HYP-PROPOSAL-0033`: `Ga-84` (`40.33 MeV` — worse than baseline `37.64`),
  `In-134` (`20.46 MeV`), `In-132` (`20.22 MeV`).
- `HYP-PROPOSAL-0034`: baseline residuals essentially unchanged
  (`Ga-84 37.64 MeV`, `In-132 17.87 MeV`, `In-131 17.52 MeV`).

The lane does not resolve the dominant baseline failures. For
`HYP-PROPOSAL-0033`, the quartic term actively worsens the worst cases
because extreme `I` rows like `Ga-84` (`I^2 = 0.069`, `I^4 = 0.0047`)
receive a large negative correction that overshoots.

## Comparison With Prior Evidence

- `AGENT-RUN-0006` same-shape 48-split spread: mean delta MAE
  `-0.058 MeV`, worst `+0.948 MeV` (for HYP-PROPOSAL-0021). The
  HYP-PROPOSAL-0033 post-AME2020 primary delta MAE (`+0.563 MeV`) is well
  inside this envelope on the positive (regression) side.
- `AGENT-RUN-0008` post-AME2020 reference: HYP-PROPOSAL-0021
  `+0.080 MeV`, HYP-PROPOSAL-0022 `-0.389 MeV`. HYP-PROPOSAL-0033 lands
  on the opposite side of zero from the negative control by `+0.95 MeV`.
- `AGENT-RUN-0009` shell-aware lane: continuous Gaussian shell-proximity
  improved `neutron_rich_delta_ge_20` by `-0.17 MeV` (HYP-PROPOSAL-0029).
  HYP-PROPOSAL-0033 regresses the same subset by `+0.90 MeV`.

## Verdict

`SANDBOX_PASS` for the run (sandbox protocol satisfied, no canonical
artifact changed). Scientific reading per candidate:

- `HYP-PROPOSAL-0033`: structured `OVERFITTED`; post-AME2020 primary
  regression and large neutron-rich subset regression. Gate outcome
  `ALLOW_ONLY_AS_NEGATIVE_CONTROL`. The lane delivers a useful stability
  finding: `HYP-PROPOSAL-0022`'s aggregate improvement is
  shape-specific, not a robust polynomial expansion.
- `HYP-PROPOSAL-0034`: structured `OVERFITTED`; post-AME2020 effect is
  numerically null because the feature is orthogonal to the training
  residuals on NMD-0002. Gate outcome `ALLOW_ONLY_AS_NEGATIVE_CONTROL`.
  The lane delivers a clean diagnostic: an asymmetric-by-design feature
  cannot rescue the one-way subset trade if the training surface does not
  carry the signal.

No follow-up batch is recommended from this run. The neutron-rich lane has
delivered the expected diagnostic value (stability test on HYP-0022 and
proton-rich-neutral construction); broader work requires a larger pinned
training surface, which is out of scope for TASK-0202.
