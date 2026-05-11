# PFF-010: Large-Angle Data Slice Proposal for Harder Falsification

## Proposed Slice

Amplitude interval: θ ∈ [1.4, 3.0] rad, with dense sampling in [2.5, 3.0] rad
(at least 50 points in the near-separatrix sub-interval).

## Motivation

The current gauntlet test window tops out at π/2 ≈ 1.571 rad. The
near_separatrix_extrapolation diagnostic for model_t4_x1 already shows MRE ≈
14% on θ ∈ [2.36, 3.14] rad — a regime that the configured benchmark does not
directly stress.

## Why This Slice Improves Falsification Value

A training slice that includes θ > 1.6 rad forces candidate formulas to capture
the accelerating growth of T/T0 as the separatrix is approached. Models that
pass the [0.01, 1.57] rad window by fitting a smooth polynomial will fail more
visibly here unless they include a log-divergent or asymptotically correct term.

## Intended Stress Behaviour

On the proposed slice, we expect:
- Pure polynomial families (model_t2_t4, model_t2_t4_t6) to show MRE > 10% in
  [2.5, 3.0] rad.
- Log-term families (model_t2_t6_l1, pff-005 proposal) to show better residuals
  in [2.5, 3.0] rad if the log coefficient is positive.

## Limitation Statement

Future proposal only. No data generated and no model evaluated on this slice.
Amplitude interval is proposed, not tested. The slice has not been validated
within the repository.
