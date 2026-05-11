# PMR-007: Complexity Penalty for Over-Tuned Mass Relations

**Microtask ID:** PMR-007  
**Queue:** particle-mass-relations  
**Run:** MICROTASK-RUN-0021  
**Verdict:** REVIEW_NEEDED  
**Review state:** UNREVIEWED  

---

## Principle

A formula with k free parameters fitted post-hoc to k observations has zero degrees of freedom. It provides no predictive constraint beyond the data used to construct it and cannot serve as evidence for a physical law.

This is a methodological criterion analogous to AIC/BIC penalization: the penalty increases with the number of tuned exponents, constants, or adjustable factors beyond what a null model requires.

---

## Formal Statement

Let a proposed mass relation have:
- n observables used to construct or constrain the formula
- k free parameters (adjustable exponents, multiplicative constants, or chosen fundamental constant combinations)

Effective degrees of freedom: d = n − k

- If d ≤ 0: the formula is over-parameterized. It cannot be falsified by the data used to construct it.
- If d > 0: the formula makes at least one prediction beyond the input data. It is potentially falsifiable.

A relation with d ≤ 0 may still be physically meaningful if it can be derived from first principles independently of the data. Without such a derivation, it provides no evidential weight.

---

## Concrete Example

Hypothetical formula: m_τ / m_μ = exp(α + β)

Suppose α and β are chosen from combinations of fundamental constants (e.g., the fine-structure constant, π, ln 2) such that exp(α + β) matches the observed ratio m_τ/m_μ ≈ 16.82.

- Number of observables used to fix α and β: 1 (the ratio m_τ/m_μ)
- Number of free parameters: 2 (α and β, reverse-engineered to fit)
- Effective degrees of freedom: 1 − 2 = −1

This formula has negative degrees of freedom. Even if α and β are presented as "fundamental constants," they were chosen post-hoc to reproduce the ratio. The formula predicts nothing that was not already known.

The same logic applies to any formula where the number of adjustable inputs equals or exceeds the number of independent empirical constraints.

---

## Why This Is Methodological, Not Metaphysical

The penalty does not assert that the formula is wrong, nor that fundamental constants are unrelated to particle masses. It enforces that fitting n parameters to ≤ n data points does not constitute evidence for a physical law.

The criterion is operationally grounded: a formula provides evidential value only if it makes at least one prediction that was not used in its construction and that prediction is subsequently tested. "Fundamental" status of the constants used does not exempt a formula from this requirement.

---

## Implications for the PMR Queue

Mass relations submitted to the particle-mass-relations queue must:

1. Identify all free parameters explicitly.
2. Count the independent observables used to fix or constrain those parameters.
3. Demonstrate at least one degree of freedom (a prediction not used in construction).
4. If d ≤ 0, classify the relation as OBSERVATION_ONLY — it may document a numerical coincidence but cannot be promoted to a physical law claim.

---

## Limitations

- The complexity penalty does not prove any particular formula is incorrect.
- A formula with d ≤ 0 may later acquire evidential value if a theoretical derivation is found that predicts the parameters from first principles without referring to the observed masses.
- This note addresses post-hoc formula construction. Koide's original formula (Q = 2/3) is a one-parameter constraint on a three-observable system, giving d = 3 − 1 = 2, and is not over-tuned in this sense — but it also lacks a first-principles derivation.

---

## Verdict

REVIEW_NEEDED — the complexity penalty criterion is clearly methodological and applicable. Its application to specific mass relations in this queue requires case-by-case evaluation of the parameter count.
