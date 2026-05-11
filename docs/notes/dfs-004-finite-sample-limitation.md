# DFS-004: Finite-Sample Limitation Note for MSD Estimation

## Three Sources of Finite-Sample Error

### 1. Finite-N Variance

The ensemble-averaged MSD at lag τ is:

MSD(τ) = (1/N) Σᵢ [x_i(t+τ) − x_i(t)]²

For finite N, the variance of this estimator scales as ~ 1/N. For N = 100
particles, the relative standard deviation of MSD is approximately 1/√100 = 10%
at each lag. This propagates into the slope fit α.

### 2. Short-Time Bias (Ballistic Onset)

At very short lags (τ ≲ τ_collision), particle motion is correlated (ballistic:
MSD ~ t²). Including these lags in the slope fit biases α upward toward 2.
Mitigation: exclude τ < 5 from the fit range.

### 3. Long-Time Drift (Finite Trajectory Bias)

At lags τ > T/2 (where T is trajectory length), fewer independent displacement
pairs are available. The MSD estimator becomes noisy and the effective N
decreases to ≈ T − τ. This produces upward scatter in MSD at long lags.
Mitigation: restrict fitting to τ < T/3 or T/4.

## How These Constraints Limit Interpretation

A fitted α value from a simulation with N = 100 particles and T = 1000 steps
should be reported with its confidence interval, not as a precise point estimate.
Claiming α = 1.000 ± 0.001 from finite simulation data is unjustified; a
realistic precision is ±0.05 to ±0.10.

## Limitation Statement

Finite-sample effects are unavoidable in discrete simulations. Any future MSD
benchmark must report N, T, lag range, and confidence intervals explicitly.
Noise is not negligible at default settings.
