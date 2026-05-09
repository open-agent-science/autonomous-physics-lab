# Scientific Note: PMR-006 - Tau-Holdout Interpretation Limitations

## Status
- **Microtask ID**: PMR-006
- **Campaign**: particle-mass-relations
- **Contributor ID**: roman
- **Date**: 2026-05-09

## Context
The historical tau-mass holdout benchmark (EXP-0005) tests the predictive power of the exact Koide relation:
$m_e + m_\mu + m_\tau = \frac{2}{3} (\sqrt{m_e} + \sqrt{m_\mu} + \sqrt{m_\tau})^2$

Using 2025 PDG-derived pole masses for the electron and muon, the relation predicts a tau mass of approximately $1776.97$ MeV, which is within the experimental uncertainty of the measured value ($1776.93 \pm 0.09$ MeV).

## Limitation Assessment

1. **Numerical vs. Structural Evidence**: The closeness of the prediction is a purely numerical regularity. This benchmark does not establish a physical mechanism for mass generation or prove the existence of a "Koide field" or specific symmetry.
2. **Domain Specificity**: The successful holdout for charged leptons does **not** imply that the same relation holds for other families (neutrinos or quarks). Current repository results for neutrinos and quarks (EXP-0007, EXP-0008) show significant discrepancies or require non-obvious mixing assumptions.
3. **Definition Dependence**: The results are highly sensitive to the definition of mass. The benchmark uses `pole` masses. Using `MS-bar` masses at a specific scale would result in different numerical values and potentially falsify the exact relation.
4. **Historical Narrowness**: While this was a "holdout" test (predicting a value that was later measured more precisely), it remains a single data point. It cannot distinguish between a fundamental law and an accidental numerical coincidence.
5. **No Novel Physics**: This note confirms that the benchmark is a tool for auditing *predictive discipline*, not a discovery of new physics.

## Verdict
**REVIEW_NEEDED** (to ensure wording stays within conservative scientific bounds)

## References
- `results/EXP-0005/RUN-0005/report.md`
- `claims/CLAIM-0004-koide-tau-holdout.md`
