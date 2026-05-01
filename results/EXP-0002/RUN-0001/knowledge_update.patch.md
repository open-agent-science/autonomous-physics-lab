# Knowledge Patch Proposal for KNOW-0002

## Target File

`knowledge/classical_mechanics/damped_oscillator.md`

## Sections To Update

- `Known Baseline`
- `Linked Objects`
- `Open Questions`

## Evidence Basis

- `RESULT-0002`
- `TASK-0002`

## Required Human Review

Yes

## Rationale

Preserve the exact linear benchmark as a reusable knowledge baseline with explicit verification detail.

## Proposed Diff

```diff
--- knowledge/classical_mechanics/damped_oscillator.md
+++ knowledge/classical_mechanics/damped_oscillator.md (proposed)
@@ -36,17 +36,18 @@
 
 - `RESULT-0002` / `RUN-0001`
 
-Its verification summary passes all current checks, including:
+Its verification summary passes all current checks:
 
-- regime classification;
-- initial-condition recovery;
-- underdamped energy decay;
-- oscillatory vs non-oscillatory behavior;
-- dimensional consistency;
-- `c -> 0` undamped-limit behavior;
-- underdamped envelope decay-rate behavior;
-- critical damping boundary behavior;
-- overdamped asymptotic tail behavior.
+- Verification gate passed: `True`
+- regime_classification: `PASS`
+- initial_condition_recovery: `PASS`
+- underdamped_energy_decay: `PASS`
+- oscillatory_vs_nonoscillatory_behavior: `PASS`
+- dimensional_consistency: `PASS`
+- c_to_zero_limit: `PASS`
+- envelope_decay_rate: `PASS`
+- critical_damping_boundary: `PASS`
+- overdamped_asymptotic_behavior: `PASS`
 
 ## Why It Matters
 
@@ -67,6 +68,7 @@
 
 ## Open Questions
 
-- Which deterministic checks best separate the three damping regimes?
-- How should energy decay be reported across regimes?
-- Should the next step benchmark driven or nonlinear oscillators?
+- Which exact checks are most reusable when the project adds driven or nonlinear oscillators?
+- How should future benchmarks report energy decay and asymptotic behavior in one shared format?
+- When should this exact linear benchmark be treated as a baseline rather than the main claim evidence?
+
```
