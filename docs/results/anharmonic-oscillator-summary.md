# Anharmonic Oscillator Period Benchmark — Result Summary

**Experiment:** EXP-0011
**Run:** RUN-0001
**Result:** RESULT-0014
**Task:** TASK-0159

## Scope

This benchmark evaluates the conservative quartic anharmonic oscillator with
`V(x) = 1/2 k x^2 + lambda x^4` on a predeclared weak-regime train slice,
holdout slice, and stress slice.

The benchmark is about approximation quality, not new physics.

## Candidate Models

- Harmonic baseline: `T = 2*pi*sqrt(m/k)`
- Leading perturbative baseline:
  `T = T0 * (1 - 3/2 * epsilon)`, `epsilon = lambda*A^2/k`
- Train-fitted empirical quadratic:
  `T = T0 * (1 + a*epsilon + b*epsilon^2)`

## Reference Path

The canonical reference period is computed from the conservative energy
integral, not from a fitted surrogate or external data source.

## Claim Ceiling

- No claim is made about negative `lambda`, double-well dynamics, damping,
  driving, resonance, or chaotic behavior.
- No empirical benchmark improvement is framed as a physical law.
