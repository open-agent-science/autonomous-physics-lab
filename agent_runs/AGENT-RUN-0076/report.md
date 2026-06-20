# Quantum Size Effects Baseline Benchmark

**Scientific verdict:** `VALID_IN_RANGE`
**Sandbox verdict:** `SANDBOX_PASS`

## Result

- Selected model: `almeida_fixed_reference`.
- Train MAE: `0.066897 eV`.
- Largest-size holdout MAE: `0.048395 eV`.
- Constant train-mean holdout MAE: `0.420200 eV`.
- Improvement over constant null: `0.371805 eV`.
- Shuffled-size control holdout MAE: `0.375676 eV`.

The selected model is the fixed Almeida source relation, evaluated with edge length converted from nm to Angstrom. It reproduces the single largest-size holdout better than both controls. Because the relation was published from the same InP size series, this is source-scoped consistency evidence, not independent validation of a physical law.

## Per-Row Residuals

| row | split | L (nm) | observed (eV) | predicted (eV) | residual (eV) | size sensitivity (eV) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `almeida-2023-inp-460nm` | train | 1.498 | 2.695 | 2.763262 | +0.068262 | 0.184552 |
| `almeida-2023-inp-480nm` | train | 2.002 | 2.583 | 2.505369 | -0.077631 | 0.109228 |
| `almeida-2023-inp-510nm` | train | 2.602 | 2.431 | 2.312439 | -0.118561 | 0.115183 |
| `almeida-2023-inp-550nm` | train | 2.787 | 2.254 | 2.267350 | +0.013350 | 0.083048 |
| `almeida-2023-inp-580nm` | train | 3.136 | 2.138 | 2.194678 | +0.056678 | 0.058276 |
| `almeida-2023-inp-620nm` | holdout | 4.112 | 2.000 | 2.048395 | +0.048395 | 0.051624 |

The size-sensitivity column is `abs(dE/dL) * sigma_L`; it reflects the TEM size distribution propagated through the model, not optical-energy measurement uncertainty.

## Limitations

- Six figure-derived rows from one InP source and morphology.
- One holdout point; no material-transfer claim.
- Published relation and benchmark rows share a source series.
- Tetrahedral edge length is retained; no spherical-radius conversion.
- Absorption only; emission and bandgap are not mixed into the residual axis.
