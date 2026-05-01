# Claim Patch Proposal for CLAIM-0001

## Target File

`claims/CLAIM-0001-pendulum-period-amplitude.md`

## Proposed Status

`PARTIALLY_SUPPORTED`

## Evidence Basis

- `RESULT-0001`
- `RESULT-0003`

## Required Human Review

Yes

## Rationale

Promote only to a range-aware supported status that preserves the remaining near-separatrix limitations.

## Proposed Diff

```diff
--- claims/CLAIM-0001-pendulum-period-amplitude.md
+++ claims/CLAIM-0001-pendulum-period-amplitude.md (proposed)
@@ -2,7 +2,7 @@
 id: CLAIM-0001
 title: Pendulum Period Depends on Amplitude
 domain: classical_mechanics
-status: DRAFT
+status: PARTIALLY_SUPPORTED
 hypothesis_id: HYP-0001
 evidence:
   experiments:
@@ -10,7 +10,7 @@
   results:
     - RESULT-0001
     - RESULT-0003
-scope: Initial scope covers amplitude correction for the ideal pendulum in classical mechanics.
+scope: Pendulum amplitude correction for the ideal pendulum within the configured benchmark ranges (train 0.0100-1.1002 rad; test 1.1080-1.5708 rad).
 ---
 
 # CLAIM-0001: Pendulum Period Depends on Amplitude
@@ -22,28 +22,28 @@
 
 ## Evidence Status
 
-`EXP-0001` has produced `RESULT-0001` and `RESULT-0003`. Together they show a
-verification-backed benchmark for low-order and theory-aware pendulum
-approximations. This claim remains in `DRAFT` until a human or later workflow
-explicitly accepts the suggested evidence update.
+`RESULT-0001` and `RESULT-0003` together support a bounded, verification-backed update for amplitude-dependent ideal-pendulum behavior.
+
+The evidence remains explicitly range-limited: the best overall verdict is `VALID_IN_RANGE`, and the near-separatrix diagnostics still fail even after the theory-aware follow-up.
 
 ## Review Recommendation
 
-Keep this claim in `DRAFT` for now.
+A maintainer may promote this claim to `PARTIALLY_SUPPORTED` after review.
 
 Reason:
 
-- the current benchmark is still range-limited;
-- the best overall verdict remains `VALID_IN_RANGE`;
-- the theory-aware candidate improves near-separatrix behavior, but the overall
-  evidence is still benchmark-scoped rather than globally valid.
+- `RESULT-0001` and `RESULT-0003` both pass the in-range verification gate;
+- the theory-aware follow-up improves separatrix behavior without making the claim exact;
+- remaining separatrix failures still require clearly bounded wording.
 
-If a maintainer wants to promote it later, the safest next status is
-`PARTIALLY_SUPPORTED` with explicit range-aware wording. A later split could
-separate:
+Promotion rationale: The benchmark supports the claim only within the tested scope and should remain range-aware.
 
-- a narrow claim about in-range approximation quality;
-- a broader claim about large-amplitude or separatrix-aware behavior.
+Do not promote this claim beyond `PARTIALLY_SUPPORTED` unless future evidence removes the remaining separatrix failure mode or narrows the claim further.
+
+Evidence from `RUN-0002` relative to `RUN-0001`:
+
+- Baseline end-ratio-to-exact: `0.350001`
+- Theory-aware end-ratio-to-exact: `0.754633`
 
 ## Scope
 
```
