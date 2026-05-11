# DFS-005: Anomalous Diffusion and Multi-Dimensional Extension — Scope Note

## Out-of-Scope Extensions for the First Batch

### 1. Anomalous Diffusion (α ≠ 1)

Fractional Brownian motion, Lévy flights, continuous-time random walks, and
other anomalous diffusion processes have MSD ~ t^α with α ≠ 1.

These are excluded from the first batch because:
- The exponent α is a free parameter requiring additional model specification.
- Fitting α from a single trajectory conflates normal-diffusion variability
  with true anomalous behaviour.
- A separate, dedicated anomalous-diffusion benchmark would need to specify
  the memory kernel, Hurst parameter, or waiting-time distribution — a
  distinct modelling problem.

### 2. Multi-Dimensional Diffusion

While MSD(t) = 2d·D·t generalises trivially to d dimensions, a benchmark
covering 2D or 3D diffusion adds boundary conditions, anisotropy, and
confinement effects that are not present in 1D. These require additional
scenario specification.

## Why Exclusion Protects Benchmark Clarity

The first batch targets a single, falsifiable claim: MSD ~ t^1 for standard
Brownian motion in 1D. Adding anomalous or multi-dimensional cases to the same
benchmark would require specifying multiple distinct generating processes and
would dilute the single-target falsification value of the first run.

## Future Work

Anomalous diffusion and multi-dimensional extension are valid future campaign
tracks. They should be scoped as separate benchmark tasks, not added to the
first batch.

## Limitation Statement

This scope note does not imply anomalous diffusion is unimportant or physically
invalid. It is a scope choice that protects the clarity of the first benchmark.
