# DFS-001: False Diffusion Scaling Relation — Proposal and Falsification Plan

## Proposed False Relation

MSD(t) = 2D · t²

(Wrong exponent: α = 2 instead of the correct α = 1 for standard diffusion)

## Why It Looks Plausible

The formula has the right units if D is redefined as [m²/s²] instead of [m²/s].
For short time intervals, the ballistic regime of a particle (before it
undergoes collisions) does show MSD ~ v²·t² ~ t², so a naive observer fitting
data at very short times could incorrectly infer α = 2.

## Concrete Falsification Test

1. Simulate N = 1000 independent random walk trajectories for T = 1000 steps.
2. Compute ensemble-averaged MSD at each time lag τ.
3. Fit a power law MSD ~ τ^α on a log-log plot.
4. The correct result is α = 1.00 ± 0.05. If the false relation were correct,
   α = 2 would be required. The observed α ≈ 1 rejects MSD = 2D·t² at long
   timescales.
5. Which deterministic check should reject it: a log-log slope test with
   tolerance ±0.1 around α = 1 should flag α = 2 as a FAIL.

## Limitation Statement

Proposal only. No simulation has been run. Falsification is described in terms
of future deterministic checks. No existing benchmark implementation is claimed.
