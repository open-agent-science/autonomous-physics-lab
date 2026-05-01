# Knowledge Patch Proposal for KNOW-0001

## Target File

`knowledge/classical_mechanics/pendulum.md`

## Sections To Update

- `Known Baseline`
- `Linked Objects`
- `Open Questions`

## Evidence Basis

- `RESULT-0001`
- `RESULT-0003`
- `TASK-0003`

## Required Human Review

Yes

## Rationale

Expand the knowledge note with explicit verification detail and the theory-aware RUN-0002 comparison without overstating global validity.

## Proposed Diff

```diff
--- knowledge/classical_mechanics/pendulum.md
+++ knowledge/classical_mechanics/pendulum.md (proposed)
@@ -41,9 +41,28 @@
 - `model_theta2_theta4`
 - verdict: `VALID_IN_RANGE`
 
-`RUN-0002` also shows that theory-aware candidate `model_x_x2_log` improves
-near-separatrix behavior relative to `RUN-0001`, but it does not turn the
-benchmark into an exact or globally valid formula.
+Verification summary for the latest canonical run:
+
+- Verification gate passed: `True`
+- small_angle_limit: `PASS`
+- small_angle_window_accuracy: `PASS`
+- small_angle_curvature: `PASS`
+- large_angle_window_accuracy: `PASS`
+- near_separatrix_extrapolation: `FAIL`
+- separatrix_asymptotic_alignment: `FAIL`
+- separatrix_log_growth_rate: `FAIL`
+- evenness: `PASS`
+- monotonicity: `PASS`
+- dimensional_consistency: `PASS`
+- known_small_angle_coefficients: `PASS`
+
+Theory-aware comparison note:
+
+- Candidate `model_x_x2_log` improves separatrix behavior relative to `RUN-0001`, but does not replace the simpler best-in-range model.
+- Baseline end-ratio-to-exact: `0.350001`
+- Theory-aware end-ratio-to-exact: `0.754633`
+- Baseline asymptotic max relative error: `0.649999`
+- Theory-aware asymptotic max relative error: `0.245367`
 
 ## Why It Matters
 
@@ -70,6 +89,6 @@
 
 - Which low-order formula gives the best accuracy/complexity tradeoff?
 - How quickly do polynomial amplitude corrections fail near large angles?
-- Can a theory-aware approximation improve separatrix behavior further without
-  losing in-range clarity or increasing complexity too much?
-- Should the next benchmark include damping or forcing?
+- Can a theory-aware approximation improve separatrix behavior further without losing in-range clarity or increasing complexity too much?
+- Which limitations must remain explicit if the claim is promoted to `PARTIALLY_SUPPORTED`?
+
```
