# Claim Patch Proposal for CLAIM-0009

## Target File

`claims/CLAIM-0009-anharmonic-oscillator-period.md`

## Proposed Status

`PARTIALLY_SUPPORTED`

## Sections To Update

- `Evidence Status`
- `Review Recommendation`

## Evidence Basis

- `RESULT-0016`

## Required Human Review

Yes

## Rationale

Keep any claim promotion benchmark-scoped and explicitly range-aware.

## Proposed Diff

```diff
--- claims/CLAIM-0009-anharmonic-oscillator-period.md
+++ claims/CLAIM-0009-anharmonic-oscillator-period.md (proposed)
@@ -2,13 +2,13 @@
 id: CLAIM-0009
 title: Anharmonic Oscillator Period Benchmark
 domain: classical_mechanics
-status: DRAFT
+status: PARTIALLY_SUPPORTED
 hypothesis_id: HYP-0011
 evidence:
   experiments:
     - EXP-0011
   results:
-    - RESULT-0014
+    - RESULT-0016
 scope: Benchmark-scoped support for weak-regime anharmonic oscillator period approximations under the configured quartic potential and holdout slices.
 ---
 
@@ -29,7 +29,7 @@
 
 ## Review Recommendation
 
-A maintainer should review benchmark wording before any promotion.
+The benchmark supports the claim only within the tested scope and should remain range-aware.
 
 ## Scope
 
```
