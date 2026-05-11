# DFS-003: Log-Log Slope Test Case for Standard Diffusion Validation

## Target Slope

α = 1.00 (normal diffusion exponent in MSD ~ t^α)

## Parameter Regime

- Spatial dimension: d = 1 (1D random walk)
- Time range: τ ∈ [10, 1000] steps (lag range avoiding ballistic onset at τ < 5
  and finite-size effects at τ > N/2)
- Particle count: N_particles ≥ 500 (for reliable ensemble average)
- Number of steps per trajectory: T ≥ 2000

## Expected Failure Interpretation

| Fitted α | Interpretation |
|---|---|
| 0.9 ≤ α ≤ 1.1 | PASS — consistent with normal diffusion |
| α < 0.9 | FAIL — subdiffusive behaviour; possible finite-size or confinement effect |
| α > 1.1 | FAIL — superdiffusive or ballistic contamination; lag range starts too early |

## Tolerance and Comparison Rule

- Fit MSD(τ) = A·τ^α by OLS regression on log(MSD) vs log(τ).
- Report fitted α with 95% confidence interval from the regression.
- PASS criterion: |α − 1.00| < 0.10 and the 95% CI includes 1.00.
- The constant A should be close to 2D (in appropriate units); report A as a
  secondary metric but do not use it as the primary pass/fail criterion.

## Limitation Statement

Test case specification only. No simulation exists. Parameter regime choices
(τ range, N_particles) are provisional and may need adjustment based on
convergence diagnostics once a simulation is implemented.
