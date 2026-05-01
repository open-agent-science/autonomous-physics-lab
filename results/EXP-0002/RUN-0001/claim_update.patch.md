# Claim Patch Proposal for CLAIM-0002

## Target File

`claims/CLAIM-0002-damped-oscillator-regimes.md`

## Proposed Status

`SUPPORTED`

## Evidence Basis

- `RESULT-0002`

## Required Human Review

Yes

## Rationale

If a maintainer accepts the current exact benchmark as sufficient, the claim can move from DRAFT to SUPPORTED without widening its scope.

## Proposed Diff

```diff
--- claims/CLAIM-0002-damped-oscillator-regimes.md
+++ claims/CLAIM-0002-damped-oscillator-regimes.md (proposed)
@@ -2,14 +2,14 @@
 id: CLAIM-0002
 title: Damped Oscillator Regime Structure
 domain: classical_mechanics
-status: DRAFT
+status: SUPPORTED
 hypothesis_id: HYP-0002
 evidence:
   experiments:
     - EXP-0002
   results:
     - RESULT-0002
-scope: Initial scope covers exact regime verification for the linear damped harmonic oscillator.
+scope: Exact regime verification for the linear, unforced damped harmonic oscillator under the configured benchmark scenarios.
 ---
 
 # CLAIM-0002: Damped Oscillator Regime Structure
@@ -22,22 +22,23 @@
 
 ## Evidence Status
 
-`RESULT-0002` now exists for the configured benchmark, but this claim remains
-`DRAFT` until the result is reviewed and the scope wording is confirmed.
+`RESULT-0002` passes the current exact, in-scope verification stack for the configured damped-oscillator scenarios.
+
+This remains maintainer-reviewed evidence rather than an automatic promotion, but the current benchmark supports a narrow `SUPPORTED` interpretation within its stated scope.
 
 ## Review Recommendation
 
-This claim can remain `DRAFT` until a maintainer explicitly reviews the public
-wording, but it is a good candidate for eventual promotion to `SUPPORTED`.
+A maintainer may promote this claim to `SUPPORTED` after review.
 
 Reason:
 
-- `RESULT-0002` passes exact, in-scope verification checks;
+- `RESULT-0002` passes all configured analytic verification checks;
 - the claim is already scoped to the linear, unforced damped oscillator;
-- no known failing verification checks remain within that benchmark scope.
+- no in-scope verification failures remain for this benchmark.
 
-This claim does not currently need to be split. The better next step is a
-deliberate maintainer review rather than automatic promotion.
+Promotion rationale: The configured benchmark passed exact, in-scope verification checks without failure.
+
+Do not broaden the claim beyond the exact linear benchmark without additional evidence for driven or nonlinear cases.
 
 ## Scope
 
```
