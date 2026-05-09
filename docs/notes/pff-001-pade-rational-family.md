# Microtask Note: PFF-001 - Pade-like Rational Formula Family Proposal

## Status
- **Microtask ID**: PFF-001
- **Campaign**: pendulum-formula-falsification
- **Contributor ID**: roman
- **Date**: 2026-05-09

## Formula Family
$T/T_0 = \frac{1 + a \cdot x}{1 - b \cdot x}$, where $x = \sin^2(\theta/2)$

- **Variable**: $x \in [0, 1]$
- **Parameters**: $a, b$ (Complexity: 2)

## Rationale
Existing polynomial models fail near the separatrix ($\theta \to \pi$, $x \to 1$) because they approach a finite limit while the exact period diverges. This family uses a rational structure to introduce a pole. 

If $b \approx 1$, the denominator $1 - bx \to 0$ as $x \to 1$, allowing the model to simulate the divergence required by the exact elliptic integral solution.

## Evenness Verification
The formula is a function of $x(\theta) = \sin^2(\theta/2)$.
Since $x(-\theta) = \sin^2(-\theta/2) = (-\sin(\theta/2))^2 = \sin^2(\theta/2) = x(\theta)$, the variable $x$ is even in $\theta$.
Any function $f(x(\theta))$ is therefore also even in $\theta$:
$f(x(-\theta)) = f(x(\theta))$
**Verdict**: Evenness is guaranteed.

## Expected Failure Regime
While this family can diverge, its divergence is of the form $1/(1-x)^n$ (polynomial singularity). The exact pendulum period $K(x)$ diverges **logarithmically** as $\ln(1/(1-x))$ near $x=1$.

**Failure Mode**: Singularity mismatch. The model will likely over-predict the divergence or fail to match the curvature near the separatrix compared to the true logarithmic growth.

## Scientific Value
Proposing this family allows the APL benchmark to test how well a simple 2-parameter rational model outperforms higher-complexity polynomials in high-amplitude regimes ($ > 2.5$ rad).

## Verdict
**REVIEW_NEEDED** (Scientific proposal ready for maintainer audit)
