# Nuclear Prediction Variants: Shell and Magic-Number Controls

**Task:** `TASK-0230`
**Entries:** `PRED-0025`, `PRED-0026`
**Status:** `REGISTERED` (prospective only; not a claim or canonical result)

## Summary

This review note documents the model choice, deterministic calculation path,
target batch, and limitations for the two shell/magic-number control variants
registered in `TASK-0230`.

Both entries are intentionally conservative. They freeze bounded shell-aware
control formulas and coefficients for later reveal, but they do not promote
the underlying TASK-0200 sandbox families into accepted shell-model evidence.

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

The shell-proximity features use the frozen magic-number set
`(2, 8, 20, 28, 50, 82, 126)` and

```text
s_x = exp(-d(x, MAGIC)^2 / (2 * sigma^2)),  sigma = 2
```

with `d(x, MAGIC)` equal to the distance from the nearest magic number.

### `PRED-0025`: Z+N Gaussian shell-proximity negative control

Frozen residual-style correction:

```text
r_corr = c_sz * s_z + c_sn * s_n
c_sz = -1.5599853542897564 MeV
c_sn =  3.2082046765215466 MeV
```

These coefficients are copied from the full-`NMD-0002` fit used in
`AGENT-RUN-0009` / `HYP-PROPOSAL-0028`.

Purpose: preserve a future-reviewable control that responds to shell proximity
on both proton and neutron axes while keeping the sandbox verdict visible:
structured holdouts failed, so this is a negative control rather than a
promoted shell correction.

### `PRED-0026`: N-only Gaussian shell-proximity negative control

Frozen residual-style correction:

```text
r_corr = c_sn * s_n
c_sn = 1.6049071729432316 MeV
```

This coefficient is copied from the full-`NMD-0002` fit used in
`AGENT-RUN-0009` / `HYP-PROPOSAL-0029`.

Purpose: preserve a minimal neutron-axis-only shell control for later reveal.
The source sandbox run showed a small primary post-AME2020 improvement, but it
still failed the structured protocol and retained proton-rich regression, so it
remains a bounded control rather than a promoted model.

## Deterministic Calculation

For each target nuclide:

1. Compute the fitted semi-empirical binding energy from `RESULT-0015`.
2. Add the frozen shell-control correction `r_corr` in MeV.
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

Both entries use the same target batch: `shell-magic-control-probe`.

The batch is chosen to keep `N` near magic values while varying `Z`
proximity, so the difference between the `Z+N` and `N-only` controls stays
interpretable without targeting a known post hoc failure cluster.

All four targets are absent from both `NMD-0002` and the committed
post-AME2020 holdout dataset at registration time.

| Nuclide | Z | N | A | `PRED-0025` (MeV) | `PRED-0026` (MeV) | `PRED-0025 - PRED-0026` (MeV) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `Cu-79` | 29 | 50 | 79 | -30.839447 | -30.612832 | -0.226615 |
| `Kr-86` | 36 | 50 | 86 | -85.568463 | -83.965689 | -1.602774 |
| `Te-134` | 52 | 82 | 134 | -72.213310 | -71.556192 | -0.657118 |
| `Xe-138` | 54 | 84 | 138 | -74.203985 | -73.442657 | -0.761328 |

Pre-reveal reading only:

- `PRED-0025` is systematically more bound than `PRED-0026` on this batch
  because the negative `c_sz` term lowers mass excess whenever `Z` remains
  near a magic number.
- The largest divergence occurs for `Kr-86`, where `N=50` keeps the neutron
  term fully active but `Z=36` suppresses the `Z`-axis proximity in a way that
  makes the two controls easy to distinguish later.
- The batch is not evidence of predictive success. It is only a frozen future
  comparison surface.

## Reveal Rule

Both entries follow [`docs/prediction-registry-policy.md`](../prediction-registry-policy.md).
Any reveal or measurement comparison must happen in a separate
maintainer-reviewed task after a future reviewed source is committed.

The original `PRED-0025` and `PRED-0026` files must remain unchanged.

## Limitations

- Prospective registry entries only; no claim, result, or knowledge promotion.
- Both entries freeze coefficients copied from retrospective sandbox work in
  `AGENT-RUN-0009`; they do not convert that sandbox evidence into a canonical
  shell claim.
- `HYP-PROPOSAL-0028` and `HYP-PROPOSAL-0029` both failed the structured
  holdout gate and therefore remain negative controls.
- The target batch is small and intentionally diagnostic, not a broad
  forecasting slate.
- Repo-prospective status checks only committed repository datasets. True-world
  prospectiveness still requires later maintainer source-state review.
