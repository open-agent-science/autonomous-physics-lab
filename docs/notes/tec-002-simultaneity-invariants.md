# TEC-002: Relativity of Simultaneity — Invariant Map

## Scenario

Two events E₁ = (t₁, x₁) and E₂ = (t₂, x₂) are simultaneous in frame S
(t₁ = t₂, x₁ ≠ x₂). Frame S' moves at velocity v along the x-axis.

## Frame Relation

Lorentz transformation: t' = γ(t − vx/c²)

- t'₁ = γ(t₁ − vx₁/c²)
- t'₂ = γ(t₂ − vx₂/c²)

Since t₁ = t₂:
Δt' = t'₂ − t'₁ = γv(x₁ − x₂)/c²

For x₁ ≠ x₂ and v ≠ 0: Δt' ≠ 0. The events are NOT simultaneous in S'.

## What Should Remain Invariant

| Quantity | Invariant? | Reason |
|---|---|---|
| Spacetime interval Δs² = c²Δt² − Δx² | YES | Lorentz scalar |
| Sign of Δs² (spacelike: Δs² < 0) | YES | Spacelike events stay spacelike |
| Causal order for timelike events | YES | Not applicable here (spacelike) |

For the simultaneous events in S: Δt = 0, so Δs² = −Δx² < 0 (spacelike).
This spacelike character is invariant across all inertial frames.

## What Should NOT Remain Invariant

| Quantity | Invariant? | Reason |
|---|---|---|
| Time ordering Δt' | NO | Depends on sign and magnitude of v |
| Simultaneity (Δt = 0) | NO | Δt' ≠ 0 in general for x₁ ≠ x₂ |

## Limitation Statement

Planning note only. No benchmark implemented. Conclusions apply to inertial
frames only. General relativity and accelerated frames are out of scope.
