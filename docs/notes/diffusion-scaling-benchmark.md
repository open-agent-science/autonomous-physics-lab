# Diffusion Scaling Benchmark — Planning Note

Task: `TASK-0015`  
Type: `benchmark_planning`  
Domain: statistical physics  
Status: planning only — no implementation yet  
Future experiment: `EXP-0003`

---

## Purpose

This document plans a falsification-first benchmark for the diffusion scaling
law. The goal is to test whether a physics engine can correctly identify the
mean-squared displacement (MSD) relation, distinguish it from plausible
imposters, and characterise the regime where the relation breaks down.

The work is intentionally planning-only. No simulation code is committed here.

---

## Core Physics Relation

Standard Brownian diffusion in one dimension:

```
<x²(t)> = 2 D t
```

where:

- `<x²(t)>` — mean-squared displacement (m²)
- `D` — diffusion coefficient (m² s⁻¹)
- `t` — time (s)

In `d` spatial dimensions the relation generalises to `<r²(t)> = 2 d D t`.

### Units

| Quantity | SI unit |
|----------|---------|
| `<x²>` | m² |
| `D` | m² s⁻¹ |
| `t` | s |

Dimensional check: `[D][t] = m² s⁻¹ · s = m²` ✓

### Analytic reference

The MSD follows directly from the Langevin equation for a free Brownian
particle in the overdamped limit:

```
dx/dt = η(t)
```

where `η(t)` is Gaussian white noise with `<η(t) η(t')> = 2D δ(t − t')`.
Integrating gives `<x²(t)> = 2Dt` exactly at all times in this idealised
limit.

---

## Benchmark Design

### What the engine must distinguish

| Candidate relation | Verdict | Reason |
|--------------------|---------|--------|
| `<x²> = 2 D t` | ✓ valid | Correct standard diffusion |
| `<x²> = D t` | ✗ wrong coefficient | Factor of 2 missing |
| `<x²> = 2 D t²` | ✗ wrong exponent | Ballistic, not diffusive |
| `<x²> = 2 D t^0.5` | ✗ wrong exponent | Sub-diffusive form |
| `<x²> = 2 D / t` | ✗ wrong sign of exponent | Unphysical |
| `<x²> = 2 D t + C` | ✗ spurious offset | No physical constant offset in free diffusion |
| `<x²(t)> = 2 d D t` (d=3) | ✓ valid | Correct 3-D generalisation |

### Scaling-law validation strategy

1. Simulate or analytically compute MSD at time points
   `t ∈ {0.1, 0.5, 1, 2, 5, 10, 50, 100}` s.
2. Fit log-log slope: `<x²> ~ t^α`. A correctly diffusive regime gives `α ≈ 1`.
3. Fit the prefactor: extract `D_fit = <x²> / (2t)` and compare to ground-truth `D`.
4. Score candidates by residual and dimensional consistency check.

---

## Stochastic Simulation Reference

A minimal 1-D random-walk simulation suitable as a reference:

```
x(t + Δt) = x(t) + √(2 D Δt) · ξ
```

where `ξ ~ N(0, 1)`. After `N` trajectories, estimate:

```
MSD(t) = (1/N) Σᵢ xᵢ(t)²
```

Parameters to fix for a canonical run:

| Parameter | Canonical value |
|-----------|----------------|
| `D` | 1.0 × 10⁻⁹ m² s⁻¹ (water-like) |
| `Δt` | 1.0 × 10⁻³ s |
| `N` (trajectories) | 10 000 |
| `T` (total time) | 1.0 s |
| Dimensions | 1 |
| Seed | fixed (e.g. 42) |

The simulation must use a fixed seed for reproducibility. Results must be
committed as canonical artifacts under `results/EXP-0003/RUN-0001/`.

---

## Noise and Finite-Sample Limitations

| Limitation | Description |
|------------|-------------|
| Finite-`N` variance | MSD estimator has variance `∝ 1/N`; 10 000 trajectories gives ~1% relative error at each time point |
| Short-time bias | For very small `t`, discrete time step `Δt` dominates; ignore `t < 5 Δt` |
| Long-time drift | For very long runs, boundary effects or numerical drift accumulate |
| Gaussian assumption | Langevin model assumes Gaussian noise; anomalous diffusion requires a separate model |
| 1-D only | Planning covers 1-D; extension to `d` dimensions is straightforward but not included in EXP-0003 scope |
| No hydrodynamic interactions | Free particle only; no crowding or caging effects |

The benchmark must report these limitations explicitly in the run report.

---

## EXP-0003 Candidate Output Outline

```
results/EXP-0003/
├── experiment.yaml          # experiment metadata
└── RUN-0001/
    ├── result.yaml          # scored candidate table
    ├── metrics.json         # MSD values, fitted α, fitted D, residuals
    ├── report.md            # human-readable summary
    ├── claim_update.md      # proposed claim update (if any)
    ├── claim_update.patch.md
    ├── knowledge_update.md  # proposed knowledge update
    ├── knowledge_update.patch.md
    ├── review_summary.md    # reviewer checklist
    └── review_metadata.yaml # machine-readable review metadata
```

### `result.yaml` schema (candidate-level)

Each scored candidate should include:

```yaml
- candidate_id: "model_2Dt"
  formula: "<x^2> = 2 * D * t"
  verdict: pass
  dimensional_check: pass
  scaling_exponent_alpha: 1.00
  prefactor_ratio: 1.000
  residual_rms: 0.0
  notes: "canonical relation"
```

### `experiment.yaml` fields

```yaml
id: EXP-0003
title: Diffusion scaling law verification
domain: statistical_physics
hypothesis_id: HYP-0003
core_relation: "<x^2> = 2 D t"
dimensions: 1
benchmark_type: scaling_law
canonical_D: 1.0e-9
seed: 42
N_trajectories: 10000
```

---

## Scoring and Falsification Criteria

A candidate relation passes if:

1. Dimensional check passes.
2. Log-log slope `α ∈ [0.95, 1.05]` (within 5% of 1).
3. Prefactor ratio `(2 D_fit) / (2 D_true) ∈ [0.97, 1.03]` (within 3%).
4. RMS residual normalised by MSD < 0.02.

A candidate that passes on coefficient but fails on units must be marked
`fail_units`.

---

## Relation to Other APL Benchmarks

| Experiment | Domain | Core relation |
|------------|--------|---------------|
| EXP-0001 | classical mechanics | pendulum period `T = 2π √(L/g)` |
| EXP-0002 | classical mechanics | damped oscillator decay |
| EXP-0003 (planned) | statistical physics | `<x²> = 2Dt` |

Diffusion is the first statistical-physics entry in APL. It is a useful next
step because:

- the ground truth is analytically exact;
- stochastic simulation is simple and seed-controlled;
- the scaling exponent `α` is a clean falsification target;
- anomalous diffusion (`α ≠ 1`) provides natural wrong-answer candidates.

---

## Open Questions Before Implementation

1. Should EXP-0003 include a multi-dimension sweep (d = 1, 2, 3)?
2. Should anomalous diffusion (`<x²> ~ t^α`, `α ≠ 1`) be added as an
   extended benchmark, or kept as a separate future experiment?
3. Which hypothesis and claim registry entries should EXP-0003 link to?
4. Should the stochastic reference use a true random walk or solve the
   Fokker–Planck equation numerically for cross-validation?

These questions should be resolved by the maintainer before implementation
begins.

---

## Limitations of This Planning Note

- No simulation code is provided or implied.
- Parameter choices (D, Δt, N, T) are illustrative; they must be validated
  before committing as canonical values.
- Scoring thresholds (5%, 3%) are proposals; they need calibration against
  actual simulation noise.
- This note does not create or modify any `results/` artifacts.
