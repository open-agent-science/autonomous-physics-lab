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
- `RESULT-0004`
- `TASK-0010`

## Required Human Review

Yes

## Rationale

Expand with gauntlet evidence and all three canonical runs.

## Proposed Diff

```diff
--- knowledge/classical_mechanics/pendulum.md
+++ knowledge/classical_mechanics/pendulum.md (proposed)
@@ -31,19 +31,32 @@
 
 `T / T0 = (2 / pi) * K(k^2)` where `k = sin(theta / 2)`.
 
-The current public-alpha benchmark has two canonical pendulum runs:
+The current public-alpha benchmark has three canonical pendulum runs:
 
-- `RESULT-0001` / `RUN-0001` for the original low-order candidate comparison;
-- `RESULT-0003` / `RUN-0002` for the theory-aware near-separatrix follow-up.
+- `RESULT-0001` / `RUN-0001` — original low-order candidate comparison;
+- `RESULT-0003` / `RUN-0002` — theory-aware near-separatrix follow-up;
+- `RESULT-0004` / `RUN-0003` — systematic gauntlet of 100 candidates.
 
-The current best overall candidate remains:
+The gauntlet best candidate is:
 
-- `model_theta2_theta4`
+- `model_t4_x1`
+- formula: `1 + a*theta^4 + b*x`
 - verdict: `VALID_IN_RANGE`
 
-`RUN-0002` also shows that theory-aware candidate `model_x_x2_log` improves
-near-separatrix behavior relative to `RUN-0001`, but it does not turn the
-benchmark into an exact or globally valid formula.
+Verification summary for the gauntlet best candidate:
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
+- dimensional_consistency: `PLACEHOLDER`
+- known_small_angle_coefficients: `PLACEHOLDER`
 
 ## Why It Matters
 
@@ -62,14 +75,16 @@
 - Tasks:
   - `TASK-0001`
   - `TASK-0003`
+  - `TASK-0010`
 - Canonical results:
   - `RESULT-0001`
   - `RESULT-0003`
+  - `RESULT-0004`
 
 ## Open Questions
 
 - Which low-order formula gives the best accuracy/complexity tradeoff?
 - How quickly do polynomial amplitude corrections fail near large angles?
-- Can a theory-aware approximation improve separatrix behavior further without
-  losing in-range clarity or increasing complexity too much?
-- Should the next benchmark include damping or forcing?
+- The gauntlet (100 candidates) confirms the best family; are there further improvements beyond the tested atom basis?
+- Which limitations must remain explicit if the claim is promoted to `PARTIALLY_SUPPORTED`?
+
```
