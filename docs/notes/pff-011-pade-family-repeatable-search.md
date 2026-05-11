# PFF-011: Repeatable Formula-Search Attempt — Padé-Type Family

## Candidate Family

```
T/T0 = (1 + a·x) / (1 − b·x)   where x = sin²(θ/2)
```

## Rationale

Padé approximants allow rational-function behaviour that can handle the growth
of T/T0 toward the separatrix better than pure polynomials, since the
denominator (1−bx) can diverge as x→1 if b→1.

## Computation Method

Least-squares fit (scipy.optimize.curve_fit) against the exact elliptic-integral
reference T/T0 = (2/π)·K(sin²(θ/2)) on the configured train range.

Train range: θ ∈ [0.01, 1.10] rad (500 points)
Test range:  θ ∈ [1.11, π/2] rad (200 points)

## Results

Fitted coefficients:
- a = -0.34321805
- b = 0.59254747

Metrics:
- Train MRE = 1.106818e-05
- Test MRE  = 8.818868e-04
- Train max RE = 4.628562e-05
- Test max RE  = 2.703599e-03

## Verdict

VALID_IN_RANGE (configured range only). Test MRE = 8.818868e-04 < 1e-3, so the
Padé family passes the configured test range [1.11, π/2] rad with sub-0.1%
mean relative error. Note that a < 0, which is structurally unusual — the
numerator correction is negative, relying on the denominator suppression to
produce the correct growth. This warrants further physical scrutiny.

## Failure Mode

If b → 1, the denominator (1−bx) → 0 as x→1 (the separatrix θ→π), producing
a singularity. This means the family can only approach the separatrix if b < 1
strictly. Extrapolation beyond the configured range is not supported.

## Novelty Check

PFF-001 described a Padé rational family at a note level. This is the first
numerical attempt for this specific (1+ax)/(1−bx) form fitted against the
exact reference.

## Limitation Statement

Results apply only to train range [0.01, 1.10] rad and test range [1.11, π/2]
rad. No claim is made beyond the configured range. Single attempt — not
promoted to knowledge.
