# Claim Patch Proposal for CLAIM-0001

## Target File

`claims/CLAIM-0001-pendulum-period-amplitude.md`

## Proposed Status

`DRAFT`

## Evidence Basis

- `RESULT-0001`
- `RESULT-0003`
- `RESULT-0008`

## Required Human Review

Yes

## Rationale

Gauntlet result strengthens range-limited evidence without overstating global validity.

## Proposed Diff

```diff
--- claims/CLAIM-0001-pendulum-period-amplitude.md
+++ claims/CLAIM-0001-pendulum-period-amplitude.md (proposed)
@@ -10,7 +10,7 @@
   results:
     - RESULT-0001
     - RESULT-0003
-scope: Initial scope covers amplitude correction for the ideal pendulum in classical mechanics.
+scope: Pendulum amplitude correction for the ideal pendulum within the configured benchmark ranges (train 0.0100-2.0985 rad; test 2.1135-3.0000 rad).
 ---
 
 # CLAIM-0001: Pendulum Period Depends on Amplitude
@@ -22,28 +22,19 @@
 
 ## Evidence Status
 
-`EXP-0001` has produced `RESULT-0001` and `RESULT-0003`. Together they show a
-verification-backed benchmark for low-order and theory-aware pendulum
-approximations. This claim remains in `DRAFT` until a human or later workflow
-explicitly accepts the suggested evidence update.
+`RESULT-0001`, `RESULT-0003`, and `RESULT-0004` together support a bounded, verification-backed update for amplitude-dependent ideal-pendulum behavior. The gauntlet (100 candidates) confirms the best-in-class formula family within the tested range. Near-separatrix diagnostics still fail.
 
 ## Review Recommendation
 
-Keep this claim in `DRAFT` for now.
+A maintainer may promote this claim to `DRAFT` after review.
 
 Reason:
 
-- the current benchmark is still range-limited;
-- the best overall verdict remains `VALID_IN_RANGE`;
-- the theory-aware candidate improves near-separatrix behavior, but the overall
-  evidence is still benchmark-scoped rather than globally valid.
+- Three independent runs (RUN-0001, RUN-0002, RUN-0003) pass the in-range gate;
+- a systematic 100-candidate gauntlet confirms the best formula family;
+- remaining separatrix failures require clearly bounded wording.
 
-If a maintainer wants to promote it later, the safest next status is
-`PARTIALLY_SUPPORTED` with explicit range-aware wording. A later split could
-separate:
-
-- a narrow claim about in-range approximation quality;
-- a broader claim about large-amplitude or separatrix-aware behavior.
+Promotion rationale: Verification checks did not fully pass, so the claim should remain draft until failures are resolved or reviewed.
 
 ## Scope
 
```
