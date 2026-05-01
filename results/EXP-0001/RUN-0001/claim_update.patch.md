# Claim Patch Proposal for CLAIM-0001

## Target File

`claims/CLAIM-0001-pendulum-period-amplitude.md`

## Proposed Status

`PARTIALLY_SUPPORTED`

## Evidence Basis

- `RESULT-0001`

## Required Human Review

Yes

## Rationale

The original pendulum benchmark supports a bounded, range-aware promotion only. The claim should not be promoted beyond `PARTIALLY_SUPPORTED` because the low-order candidate fails near-separatrix diagnostics.

## Proposed Diff

```diff
--- claims/CLAIM-0001-pendulum-period-amplitude.md
+++ claims/CLAIM-0001-pendulum-period-amplitude.md (proposed)
@@
-status: DRAFT
+status: PARTIALLY_SUPPORTED
@@
-scope: Initial scope covers amplitude correction for the ideal pendulum in classical mechanics.
+scope: Pendulum amplitude correction for the ideal pendulum within the configured benchmark ranges.
```
