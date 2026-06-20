# Quantum Size Effects Baseline Pre-Reveal Package

**Task:** `TASK-0225`
**Frozen before benchmark execution:** 2026-06-20

## Scope

- Dataset: `data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml`
- Source: Almeida et al. 2023, InP colloidal quantum dots, CC BY 4.0.
- Primary target: `absorption_peak_eV`.
- Size axis: tetrahedral `edge_length_nm`.
- Included rows: the six schema-valid, deterministic figure-extraction rows
  admitted by the TASK-0293 readiness gate.
- Excluded data: calibration-derived `QD-0001` and `QD-0002`; emission and
  bandgap axes; all live or unreviewed sources.

This is a single-material, six-row measurement-versus-model benchmark. It is
not a material-holdout test and cannot establish transfer across materials.
The TASK-0293 readiness decision explicitly selected a size-range holdout for
this first InP-only pass.

## Frozen Split

- Train: the five rows with edge length below `4.0 nm`.
- Holdout: the largest row, `almeida-2023-inp-620nm`, with edge length
  `4.112 nm`.
- Size bins for reporting:
  - small: edge length below `2.0 nm`;
  - mid: edge length from `2.0 nm` through `3.0 nm`;
  - large: edge length above `3.0 nm`.

The holdout value must not affect model selection or fitted coefficients.

## Frozen Models

1. `almeida_fixed_reference`
   - Published source-scoped relation:
     `E(L_A) = 1.33 + 9.128 * L_A^(-0.684)`, where
     `L_A = 10 * L_nm` converts the dataset edge length from nm to Angstrom.
   - No fitted parameters.
2. `inverse_edge_fit`
   - Train-fitted generalized baseline:
     `E(L) = c + a / L`.
   - Two fitted coefficients.
3. `inverse_square_fit`
   - Train-fitted effective-confinement proxy:
     `E(L) = c + a / L^2`.
   - Two fitted coefficients.
4. `constant_train_mean`
   - Negative/null control independent of size.
5. `shuffled_size_inverse_edge`
   - Deterministic negative control. Shuffle the five training sizes with
     `random.Random(225)`, fit `E = c + a/L`, and evaluate on the unchanged
     holdout size.

No additional exponents, piecewise forms, material parameters, or correction
terms may be searched after holdout inspection.

## Selection And Evaluation

- Select the primary size-aware model among models 1-3 using lowest train MAE.
- Tie-break by fewer fitted coefficients, then model id.
- Report train and holdout MAE/RMSE in eV for every model.
- Report per-row residuals, size-bin residual metrics, and absolute-residual
  outliers.
- Propagate the reported TEM edge-length standard deviation through each
  differentiable size-aware model as local prediction sensitivity
  `abs(dE/dL) * sigma_L`; this is not an optical-energy measurement error.

## Frozen Decision Rule

- `VALID_IN_RANGE`: selected model beats the constant-mean holdout MAE by at
  least `0.05 eV`, and the shuffled-size control is worse.
- `PARTIALLY_VALID`: selected model beats the null but by less than `0.05 eV`,
  or one control is not ordered as expected.
- `INVALID`: selected size-aware model does not beat the constant-mean null.

Any verdict remains bounded to this six-row InP figure-digitized dataset.

## Expected Limitations

- One material and one holdout row.
- Figure-derived edge lengths and absorption labels rather than source-table
  values.
- Tetrahedral edge length is not silently converted into spherical radius.
- Size uncertainty describes the TEM distribution, not the uncertainty of the
  absorption energy.
- The published Almeida relation is an external reference, not independent
  evidence and not a universal quantum-dot law.

## Output Boundary

- Allowed: deterministic engine/workflow, sandbox run package, metrics, report,
  review summary, and documentation summary.
- Not allowed: `CLAIM-*`, `KNOW-*`, `PRED-*`, golden-result changes, synthesis
  guidance, device claims, biomedical claims, or broad material-law wording.
