# Microtask Note: DAV-002 - Bernoulli's Equation Density Mismatch

## Status
- **Microtask ID**: DAV-002
- **Campaign**: dimensional-analysis-validator
- **Contributor ID**: roman
- **Date**: 2026-05-09

## Formula (Incorrect)
$p + \frac{v^2}{2} + g \cdot h = C$

## Dimensions
- $p$ (pressure): $[M L^{-1} T^{-2}]$ (Pa = kg/(m s²))
- $v^2/2$ (velocity squared): $[L^2 T^{-2}]$ (m²/s²)
- $g \cdot h$ (gravity $\times$ height): $[L T^{-2}] \cdot [L] = [L^2 T^{-2}]$ (m²/s²)

## Rationale
The addition of terms requires identical dimensions. Here, the first term (pressure) has dimensions $[M L^{-1} T^{-2}]$, while the subsequent terms have $[L^2 T^{-2}]$. The mismatch is the missing density factor $\rho$ ($[M L^{-3}]$) in the kinetic and potential terms. 

Correct formula: $p + \frac{1}{2}\rho v^2 + \rho g h = C$

## Verdict
**INVALID**

## Limitations
This note identifies a dimensional mismatch only. It does not evaluate the applicability of Bernoulli's principle to compressible or viscous flows.
