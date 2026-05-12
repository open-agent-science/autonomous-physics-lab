# Autonomous Nuclear Neutron-Rich Sandbox Batch 01

**Task:** `TASK-0202`
**Agent run:** `AGENT-RUN-0010`
**Status:** sandbox-only review; no claim or canonical result promotion
**Claim boundary:** advisory; this review does not authorize a third
sandbox batch in the neutron-rich lane and does not promote either
executed candidate.

## Scope

Second nuclear sandbox batch restricted to the neutron-rich residual
lane. Five hypothesis proposals were generated; two were executed and
three were rejected before execution. The two executed families test:

1. whether the prior negative-control `HYP-PROPOSAL-0022` quadratic
   asymmetry generalizes to a quartic extension (`HYP-PROPOSAL-0033`);
2. whether an asymmetric feature that is zero on proton-rich rows
   (`HYP-PROPOSAL-0034`) can avoid the one-way subset trade documented in
   [post-ame2020-timesplit-failure-analysis.md](./post-ame2020-timesplit-failure-analysis.md).

The lane does not target individual shell closures or isotopic chains
identified retrospectively on the post-AME2020 holdout. Such targeted
features were rejected explicitly under
[../nuclear-mass-robustness-gate.md](../nuclear-mass-robustness-gate.md)
leakage rules.

## Proposals

| Proposal | Family | Status | Reason |
| --- | --- | --- | --- |
| `HYP-PROPOSAL-0033` | quartic isospin-asymmetry | Executed | Stability test on the shape of HYP-0022's quadratic improvement. |
| `HYP-PROPOSAL-0034` | asymmetric `(N-Z)^2/A` (proton-rich neutral) | Executed | Designed so feature is zero on N<Z rows, addressing the one-way trade. |
| `HYP-PROPOSAL-0035` | In/Sb chain (Z in {49, 51}) indicator | Rejected | Post-hoc leakage from AGENT-RUN-0008 worst-residual cluster. |
| `HYP-PROPOSAL-0036` | free-power asymmetry `I^p` with p fitted | Rejected | Nonlinear knob on an 11-row training surface. |
| `HYP-PROPOSAL-0037` | per-shell N=50/82/126 indicator stack | Rejected | Targeted leakage; same family of objection as HYP-0031 and HYP-0035. |

## Method

Deterministic batch driven by `scripts/run_nuclear_neutron_rich_batch.py`
and recomputed by `tests/test_nuclear_neutron_rich_batch.py`.

For each executed family:

1. NMD-0002 four-holdout cross-validation: fit linear coefficients on the
   holdout complement, evaluate on the holdout, report MAE and RMSE
   deltas vs the frozen `RESULT-0015` baseline residuals.
2. Post-AME2020 evaluation: fit linear coefficients once on the full
   NMD-0002 residual surface, then apply to the 295-row primary holdout.
   Report feature-activation counts and per-subset MAE deltas, including
   `neutron_rich_delta_ge_20` and `neutron_rich_delta_ge_30` to expose
   extreme-isospin behavior.

## Structured Holdout Results

Both candidates land in `OVERFITTED` on the structured protocol.

| Candidate | Improved | Regressed | Mean delta MAE (MeV) | Worst regression (MeV) |
| --- | ---: | ---: | ---: | ---: |
| `HYP-PROPOSAL-0033` | 0 | 4 | +2.3105 | 5.9325 |
| `HYP-PROPOSAL-0034` | 0 | 4 | +0.9939 | 2.3910 |

## Post-AME2020 Primary Results (n=295)

Baseline primary MAE: `4.5526 MeV`.

| Candidate | Primary delta MAE | Magic-any | Near-magic | NR (>=20) | NR (>=30) | Proton-rich | Heavy | Odd-A |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `HYP-PROPOSAL-0033` | +0.5629 | +0.4987 | +0.4308 | +0.9006 | +0.5989 | +0.0742 | +0.6739 | +0.5671 |
| `HYP-PROPOSAL-0034` | -3.9e-13 | -3.6e-13 | -2.9e-13 | -5.2e-13 | -6.9e-13 | +2.0e-14 | -4.7e-13 | -4.6e-13 |

Two distinct readings:

- **`HYP-PROPOSAL-0033`** (quartic asymmetry) regresses primary MAE by
  `+0.56 MeV`. This is the **opposite sign** of the prior
  `HYP-PROPOSAL-0022` quadratic-only result (`-0.39 MeV` per
  `AGENT-RUN-0008`). Adding one polynomial degree on the same family
  reverses the aggregate sign. The fitted coefficients are
  `i_sq = +82.66 MeV`, `i_quartic = -1777.78 MeV`; the quartic term
  dominates at high `I` and overshoots.
- **`HYP-PROPOSAL-0034`** (asymmetric `(N-Z)^2/A`) fits a near-zero
  coefficient (`~3.5e-13`) because the heavy-weighted feature is
  essentially orthogonal to the training residuals on the 11-row
  NMD-0002 slice. All post-AME2020 subset deltas are at floating-point
  noise. The candidate is effectively null on the time-split surface.

## Feature Activation

| Candidate | Feature | Activation (n=295) |
| --- | --- | ---: |
| `HYP-PROPOSAL-0033` | `i_sq` | 292 |
| `HYP-PROPOSAL-0033` | `i_quartic` | 292 |
| `HYP-PROPOSAL-0034` | `neutron_excess_sq_over_a` | 264 |

`HYP-PROPOSAL-0034` is zero on the 28 proton-rich (`N < Z`) and 3 `N = Z`
rows in the primary holdout, by construction (`max(N-Z, 0)^2 / A = 0`).
The dormant-feature failure mode documented in `AGENT-RUN-0008` does not
apply in this lane.

## Negative-Control Reference (HYP-PROPOSAL-0022)

From `AGENT-RUN-0008`:

- `HYP-PROPOSAL-0022` primary delta MAE: `-0.3886 MeV`
- `HYP-PROPOSAL-0033` primary delta MAE: `+0.5629 MeV` (this run)
- `HYP-PROPOSAL-0034` primary delta MAE: `~0 MeV` (this run)

The two-degree-of-freedom polynomial extension of HYP-0022 does not
generalize. It reverses sign and lands almost exactly the same magnitude
on the regression side. This is a useful stability finding: the prior
`HYP-PROPOSAL-0022` improvement was a quadratic-shape artifact on the
training surface, not a robust higher-order asymmetry signal.

## Worst-Case Residuals After Correction

The In/Sb N=82 cluster persists, and `HYP-PROPOSAL-0033` makes it worse:

- `HYP-PROPOSAL-0033`: `Ga-84` `40.33 MeV` (baseline `37.64`),
  `In-134` `20.46 MeV`, `In-132` `20.22 MeV`.
- `HYP-PROPOSAL-0034`: residuals essentially unchanged from baseline
  (`Ga-84 37.64`, `In-132 17.87`, `In-131 17.52`).

For `HYP-PROPOSAL-0033`, the candidate makes the worst case worse: at
`Ga-84` (`Z=31, N=53, I^2 = 0.069, I^4 = 0.0047`), the quartic correction
overshoots by ~2.7 MeV.

## Comparison Context

- `AGENT-RUN-0006` 48-split same-shape spread: mean delta MAE
  `-0.058 MeV`, worst `+0.948 MeV`. HYP-0033's primary delta MAE
  (`+0.56 MeV`) is well inside this envelope on the regression side.
- `AGENT-RUN-0008` reference: HYP-0021 `+0.080`, HYP-0022 `-0.389`.
  HYP-0033 lands `+0.95 MeV` away from the negative control.
- `AGENT-RUN-0009` shell-aware lane (HYP-0029): neutron_rich (>=20) delta
  MAE `-0.17 MeV`. HYP-0033 regresses the same subset by `+0.90 MeV`.

## Robustness Gate

```text
Robustness gate:
- outcome: ALLOW_ONLY_AS_NEGATIVE_CONTROL (both executed candidates)
- baseline: RESULT-0015 :: model_fitted_semi_empirical (frozen)
- active holdouts: random_stratified, oxygen_chain, magic_heavy_region,
  neutron_rich_edge (NMD-0002 structured); post-AME2020 primary (295 rows).
- split-sensitivity summary: AGENT-RUN-0006 reference; same-shape spread
  mean -0.058 MeV, worst +0.948 MeV. HYP-0033 primary delta MAE +0.563 MeV
  is inside this envelope on the regression side; HYP-0034 is at machine
  precision.
- leakage review: HYP-PROPOSAL-0035 (In/Sb chain) and HYP-PROPOSAL-0037
  (per-shell N=50/82/126 stack) explicitly rejected. Executed features
  are symmetric polynomials in I or an asymmetric (N-Z, capped at zero)
  feature; neither targets a specific shell or chain.
- complexity note: HYP-PROPOSAL-0033 has 2 linear parameters,
  HYP-PROPOSAL-0034 has 1. No nonlinear knobs, no discontinuities, no
  magic-number switches.
- negative control: comparison against HYP-PROPOSAL-0022 from
  AGENT-RUN-0008. HYP-0033 reverses HYP-0022's aggregate sign,
  confirming the prior improvement was shape-specific.
- post-AME2020 status: ACTIVE_RETROSPECTIVE_TIME_SPLIT. HYP-0033
  regresses primary; HYP-0034 is numerically null.
- limitations: sandbox-only; NMD-0002 has 11 nuclides; structured
  holdouts OVERFITTED on both; retrospective time-split only.
```

## Decision

- `HYP-PROPOSAL-0033`: `ALLOW_ONLY_AS_NEGATIVE_CONTROL`. Useful stability
  diagnostic on HYP-0022's shape-specific improvement.
- `HYP-PROPOSAL-0034`: `ALLOW_ONLY_AS_NEGATIVE_CONTROL`. Useful clean
  diagnostic that an asymmetric-by-design feature does not rescue the
  lane on the current training surface.

No third neutron-rich sandbox batch is recommended from this run alone.
Promotion is blocked.

## Limitations

- Sandbox-only. No canonical artifact is updated.
- 11-row NMD-0002 training surface dominates structured-holdout
  instability and the orthogonality finding for HYP-0034.
- Post-AME2020 evaluation is retrospective time-split, not blind
  prediction.
- The "stability finding" on HYP-0022 sharpens its negative-control
  reading; it does not promote or demote HYP-0022, which remains
  sandbox-only under the existing gate outcome.
