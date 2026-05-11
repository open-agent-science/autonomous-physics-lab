# DFS-002: Units Audit — Standard MSD Relation

## Formula Under Audit

MSD(t) = 2D · t   (standard diffusion, 1D)

## SI Unit Trace

| Quantity | Symbol | SI units |
|---|---|---|
| Mean squared displacement | MSD | m² |
| Diffusion coefficient | D | m²·s⁻¹ |
| Time | t | s |

LHS: MSD → [m²]

RHS: 2D·t → [m²·s⁻¹]·[s] = [m²]

LHS = RHS → **Verdict: units-consistent**

## Generalisation to d Dimensions

MSD(t) = 2d·D·t

The factor 2d is dimensionless (d is the spatial dimension, a pure integer).
Units remain [m²·s⁻¹]·[s] = [m²] ✓

## What Units Consistency Does NOT Confirm

- Physical correctness: this formula assumes Brownian motion, memoryless
  increments, and an ergodic ensemble. These assumptions are not tested by
  dimensional analysis.
- Anomalous diffusion: for MSD ~ t^α with α≠1, the coefficient D* has units
  [m²·s⁻ᵅ] — a fractional dimension. The standard formula is not applicable
  in that regime.
- Finite-time behaviour: at very short times (ballistic regime), MSD ~ t²,
  not t. The linear relation applies only in the diffusive regime.

## Limitation Statement

Units audit only. No simulation benchmark exists. The formula is units-
consistent for standard diffusion in the diffusive time regime.
