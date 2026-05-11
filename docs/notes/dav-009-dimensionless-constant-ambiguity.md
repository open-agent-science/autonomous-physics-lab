# DAV-009: Dimensionless Constants and Verdict Ambiguity

## The General Rule

A true dimensionless constant (a pure number such as an integer, π, e, or a
unitless ratio) does **not** affect the dimensional verdict. The constant
carries no SI base dimensions and can be multiplied into any formula without
changing its dimensional balance.

## Harmless Example

`F = G·m₁·m₂/r²` vs `F′ = (4π)·G·m₁·m₂/r²`

Both have SI dimensions [M·L³·T⁻²·M²·L⁻²] = [M·L·T⁻²] = [N]. The factor 4π
is a pure number — it does not affect the verdict. Both are **VALID**.

## Where It Becomes Misleading

If a formula writes `c = 1` (speed of light in natural units) as a
dimensionless 1, inserting it into an SI formula makes the dimensions appear to
balance, but only because a factor of [m·s⁻¹] has been suppressed. This `1`
is not truly dimensionless in SI — it carries dimensions that are hidden.

## Boundary Rule

| Constant category | Effect on verdict |
|---|---|
| Integer, π, e, unit ratios, α_fine, counts | None — truly dimensionless |
| Physical constants set to 1 (c, ℏ, k_B) in natural units | Hides SI dimensions — misleading |

The boundary: a constant is harmless if it has no SI dimensions in the
convention being used. It is misleading if it carries suppressed SI dimensions
from a natural-unit convention.

## Limitation Statement

Boundary rule is conceptual. No validator implementation has been updated. Edge
cases in composite natural-unit expressions may require maintainer judgment.
