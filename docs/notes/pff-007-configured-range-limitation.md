# PFF-007: Configured-Range Limitation Note for EXP-0001/RUN-0003

## Context

This note documents the epistemic boundary of the results recorded in `results/EXP-0001/RUN-0003/result.yaml`. It is intended as a standing limitation record for the pendulum gauntlet experiment and should be read alongside any note or claim that cites EXP-0001/RUN-0003.

**Experiment:** EXP-0001  
**Run:** RUN-0003  
**Result ID:** RESULT-0004  
**Best model verdict:** VALID_IN_RANGE  
**Configured train range:** 0.01–1.10 rad  
**Configured test range:** 1.11–1.57 rad (≈ π/2)

---

## What the Result Establishes

Within the scope of EXP-0001/RUN-0003, the following conclusions are supported:

1. **In-range accuracy of the best model.** The model `model_t4_x1` achieves train MRE ≈ 3.58×10⁻⁶ and test MRE ≈ 3.05×10⁻⁴ within the configured windows. This is a quantified accuracy statement for those windows only.

2. **Structural check coverage.** Four structural checks pass for the best model within the configured range: `small_angle_limit`, `small_angle_window_accuracy`, `small_angle_curvature`, and `large_angle_window_accuracy`. These checks confirm that the model behaves consistently with the ideal pendulum over 0.01–1.57 rad.

3. **Relative model ranking.** The leaderboard provides a relative ranking of 100 candidate models by composite score within the configured range. This ranking is valid as a ranking within this experiment's setup; it does not imply an ordering over a larger model space.

4. **Candidate basis coverage.** All 100 candidates are built from a fixed basis of ten atoms and are linear-in-coefficients. The result establishes which combinations of these specific atoms perform best under least-squares fitting in the configured range.

---

## What the Result Does NOT Establish

The following claims are **not** supported by EXP-0001/RUN-0003:

1. **Performance beyond π/2.** The near-separatrix extrapolation diagnostic (`near_separatrix_extrapolation`: FAIL, MRE ≈ 14% on θ ∈ [2.36, 3.14] rad) and the `separatrix_asymptotic_alignment` diagnostic (FAIL, MRE ≈ 38%) confirm that the best model degrades substantially above the test range ceiling of 1.57 rad. No accuracy claim is supportable for θ > π/2.

2. **Validity under damping.** The experiment models an ideal mathematical pendulum with no damping and no driving force. Results do not apply to underdamped, overdamped, or driven pendulums. Physical pendulums subject to air resistance, pivot friction, or finite-amplitude driving are outside the scope of these results.

3. **Validity for non-ideal pendulums.** Effects such as finite rod mass, pivot elasticity, and nonlinear restoring force deviations from the small-angle approximation are not modeled. The result applies only to the idealized `T/T0` ratio for a point-mass pendulum.

4. **Exhaustive formula-family coverage.** The candidate pool is drawn from ten fixed atoms. Functional forms not representable as linear combinations of these atoms — including rational functions, transcendental combinations, Padé approximants with nonlinear denominators, and forms involving `log(cos θ)` or Jacobi elliptic functions directly — are not tested. The best model from this experiment is the best among 100 specific candidates, not the best possible formula.

5. **Discovery-level physics conclusions.** The gauntlet result is a numerical accuracy benchmark over a fixed candidate set. It does not constitute a derivation, a proof, or a discovery in the physics literature. No new physical law, formula family, or universal pendulum relation is established. The result is a data-fitting benchmark with structural sanity checks.

---

## Limitation Statement

EXP-0001/RUN-0003 supports quantitative accuracy and structural consistency claims within 0.01–1.57 rad for ideal, undamped pendulums, using linear-in-coefficients models from a ten-atom basis. It does not support any physics-resolution claim, does not identify a universal pendulum law, and does not represent a field-wide breakthrough. All citations to these results should carry the scope qualifier "within the configured range of EXP-0001/RUN-0003."
