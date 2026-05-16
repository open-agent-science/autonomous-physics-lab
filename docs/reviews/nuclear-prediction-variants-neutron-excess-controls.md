# Nuclear Prediction Variants: Neutron-Excess and Asymmetry Controls

**Task:** `TASK-0231`
**Entries:** `PRED-0027`, `PRED-0028`
**Status:** `REGISTERED` (prospective only; not a claim or canonical result)

## Summary

This note records two new prospective entries in the nuclear mass prediction
registry for the neutron-excess / asymmetry lane.

Both entries preserve bounded negative-control readings from
`AGENT-RUN-0010`. They freeze future-reviewable control variants, but they do
not promote the underlying `TASK-0202` sandbox families into accepted
evidence.

## Model Variants

Both entries derive from the same frozen baseline:
`RESULT-0015::model_fitted_semi_empirical`

Baseline coefficients (from `results/EXP-0012/RUN-0001/result.yaml`):

| Term | Coefficient |
| --- | ---: |
| volume | 15.51423612106804 MeV |
| surface | 17.29318120951770 MeV |
| coulomb | 0.68781560915689 MeV |
| asymmetry | 23.84655788394849 MeV |
| pairing | 15.99084511339891 MeV |

### `PRED-0027`: quartic asymmetry negative control

Frozen residual-style correction:

```text
r_corr = c_i2 * I^2 + c_i4 * I^4
I = (N - Z) / A
c_i2 = 82.66196399343987 MeV
c_i4 = -1777.7853009092412 MeV
```

These coefficients are copied from the full-`NMD-0002` fit used in
`AGENT-RUN-0010` / `HYP-PROPOSAL-0033`.

Purpose: preserve a future-reviewable control showing the instability of a
higher-order asymmetry family. The sandbox run found that the quartic term
reversed the sign of the earlier quadratic-control reading and overshot on
extreme neutron-rich rows, so this entry is a negative control rather than a
candidate correction.

### `PRED-0028`: asymmetric neutron-excess near-null control

Frozen residual-style correction:

```text
r_corr = c_ne * max(N - Z, 0)^2 / A
c_ne = 3.4709894797642375e-13 MeV
```

This coefficient is copied from the full-`NMD-0002` fit used in
`AGENT-RUN-0010` / `HYP-PROPOSAL-0034`.

Purpose: preserve a near-null control where the feature is structurally
one-sided (`N > Z` only) but the fitted coefficient collapses almost exactly to
zero. The entry is useful precisely because it does **not** rescue the lane on
the current training surface.

## Deterministic Calculation

For each target nuclide:

1. Compute the fitted semi-empirical binding energy from `RESULT-0015`.
2. Add the frozen control correction `r_corr` in MeV.
3. Convert the corrected binding energy to atomic mass:

```text
atomic_mass_u = Z*m_H + N*m_n - (B_base + r_corr) / 931.494013
```

4. Convert atomic mass to mass excess:

```text
mass_excess_mev = (atomic_mass_u - A) * 931.494013
```

Physical constants:

- `m_H = 1.00782503207 u`
- `m_n = 1.00866491600 u`
- `1 u = 931.494013 MeV`

All stored values are deterministic point estimates rounded to 6 decimals.
No live external data was fetched during registration.

## Target Batch

Both entries use the same target batch: `neutron-excess-control-probe`.

The batch is chosen to span light and heavier neutron-rich targets with
substantial `N-Z`, so the difference between a strongly shape-sensitive quartic
control and a near-null asymmetric control stays visible without targeting any
known post hoc failure cluster.

All four targets are absent from both `NMD-0002` and the committed
post-AME2020 holdout dataset at registration time.

| Nuclide | Z | N | A | `PRED-0027` (MeV) | `PRED-0028` (MeV) | `PRED-0027 - PRED-0028` (MeV) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `Na-39` | 11 | 28 | 39 | 147.493226 | 99.017052 | 48.476174 |
| `Mg-40` | 12 | 28 | 40 | 104.080021 | 71.794631 | 32.285390 |
| `Co-81` | 27 | 54 | 81 | 38.719704 | 25.956400 | 12.763304 |
| `Ni-82` | 28 | 54 | 82 | 18.346025 | 8.687752 | 9.658273 |

Pre-reveal reading only:

- `PRED-0027` becomes dramatically less bound on the more extreme light
  neutron-rich targets because the frozen quartic term overshoots there.
- `PRED-0028` stays effectively at the baseline to 6-decimal precision because
  the fitted `c_ne` coefficient is near zero.
- This contrast is exactly the negative-control signal preserved from
  `AGENT-RUN-0010`; it is not evidence of predictive success.

## Reveal Rule

Both entries follow [`docs/prediction-registry-policy.md`](../prediction-registry-policy.md).
Any reveal or measurement comparison must happen in a separate
maintainer-reviewed task after a future reviewed source is committed.

The original `PRED-0027` and `PRED-0028` files must remain unchanged.

## Limitations

- Prospective registry entries only; no claim, result, or knowledge promotion.
- Both entries freeze coefficients copied from retrospective sandbox work in
  `AGENT-RUN-0010`; they do not convert that sandbox evidence into a canonical
  neutron-rich or asymmetry claim.
- `HYP-PROPOSAL-0033` and `HYP-PROPOSAL-0034` both failed the structured
  holdout gate and therefore remain negative controls.
- The target batch is small and intentionally diagnostic, not a broad
  forecasting slate.
- Repo-prospective status checks only committed repository datasets. True-world
  prospectiveness still requires later maintainer source-state review.
