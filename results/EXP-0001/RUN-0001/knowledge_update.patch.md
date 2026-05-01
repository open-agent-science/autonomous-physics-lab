# Knowledge Patch Proposal for KNOW-0001

## Target File

`knowledge/classical_mechanics/pendulum.md`

## Sections To Update

- `Known Baseline`
- `Linked Objects`
- `Open Questions`

## Evidence Basis

- `RESULT-0001`
- `TASK-0001`

## Required Human Review

Yes

## Rationale

This historical run established the original low-order pendulum benchmark and should remain documented as the baseline that later motivated the theory-aware near-separatrix follow-up.

## Proposed Diff

```diff
--- knowledge/classical_mechanics/pendulum.md
+++ knowledge/classical_mechanics/pendulum.md (proposed)
@@
+- `RESULT-0001` / `RUN-0001` established the original low-order baseline.
+- Near-separatrix diagnostics fail for this run, which motivated the later theory-aware follow-up.
```
