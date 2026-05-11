# PFF-005: Separatrix-Aware Log-Term Variant — Proposal and Falsification Plan

## Proposed Family

```
T/T0 = 1 + a·θ² + b·x·log(1/(1−x))   where x = sin²(θ/2)
```

## Rationale

As θ→π, x→1, so `log(1/(1−x))` diverges. This mirrors the known logarithmic
divergence of the complete elliptic integral K(k) near the separatrix: near
k=1, K(k) ≈ log(4/√(1−k²)), so T diverges logarithmically. Pure polynomial or
sinusoidal families cannot reproduce this growth; adding a log term in x is the
minimal extension that captures it structurally.

## Specific Falsification Test

1. Fit the family on the configured train range (0.01–1.10 rad).
2. If the fitted coefficient b ≤ 0, the log term is not providing growth toward
   the separatrix — reject the family on structural grounds.
3. Evaluate on θ ∈ [2.5, 3.0] rad (near-separatrix extrapolation). If mean
   relative error > 5%, the asymptotic correction is insufficient.

## Limitation Statement

This note is a planning proposal only. No numerical fit has been run. Verdict:
PROPOSED. All conclusions are speculative until numerical results are available
in the configured amplitude range.
