# Nuclear Residual-Feature No-Leakage Contract Review

**Task:** `TASK-0368`  
**Type:** benchmark protocol  
**Evidence class:** protocol-only residual-feature gate  
**Verdict:** `PARTIALLY_VALID`

## Scope

This review records the protocol boundary added in
[`docs/nuclear-residual-feature-no-leakage-contract.md`](../nuclear-residual-feature-no-leakage-contract.md).
It classifies residual-adjacent Nuclear Mass Surface feature families before
any future prediction-registry implementation task.

No data was fetched, no model was fit, no `PRED-*` entry was created, no
reveal comparison was run, and no claim or canonical result was promoted.

## Inputs Reviewed

- `docs/reviews/nuclear-local-curvature-adversarial-controls.md`
- `docs/reviews/nuclear-high-error-cluster-hypothesis-lane.md`
- `docs/nuclear-local-curvature-no-leakage-freeze-protocol.md`
- `docs/nuclear-prediction-reveal-protocol.md`
- `prediction_registry/nuclear_masses/README.md`
- `docs/reviews/nuclear-uncertainty-weighted-residual-lane.md`
- `docs/reviews/nuclear-shell-axis-post-audit-decision.md`

## Classification Summary

| Feature family | Review status | Reason |
| --- | --- | --- |
| Local-curvature | `CONDITIONAL_PREDICTIVE_ELIGIBLE` | The earlier leaky full-known residual form remains diagnostic-only, but a leave-one-out, training-only cache design can be reviewed later. |
| High-error-cluster | `DIAGNOSTIC_ONLY` by default | Existing high-error labels are computed from committed residuals, so they cannot become prediction inputs without a source-independent redesign. |
| Shell-axis | `CONDITIONAL_PREDICTIVE_ELIGIBLE` | Deterministic shell distances are pre-reveal descriptors, but the current post-audit shell-axis lane remains diagnostic-only and source-gated reveal scoring is still blocked. |
| Source-status | `LIMITED_PREDICTIVE_ELIGIBLE` or `BLOCKED` | Pre-frozen metadata may support stratified review; any status field that encodes training, holdout, or future-source availability is blocked. |
| Uncertainty-weighted residual | `DIAGNOSTIC_ONLY` by default | Current uncertainty fields are review-only; future use requires pre-frozen, fit-grade uncertainty semantics that do not depend on target residuals. |

## Allowed Future Inputs

The contract allows future predictive tasks to use `(Z, N, A)`,
source-independent descriptors, magic-number proximity, and committed
pre-registration training rows. Baseline-only residuals may be used only inside
approved training or per-fold caches. Source-status and uncertainty metadata
must be frozen before prediction and audited for leakage.

## Forbidden Future Inputs

The contract blocks target residuals, post-registration measurements,
full-known neighbor residuals unavailable at prediction time, self-inclusive
residual aggregates, future-row high-error labels, training-membership proxies,
and full-dataset normalization or weighting that crosses the reveal boundary.

## Artifact Gate For Later Work

Any later implementation task must provide a feature manifest, frozen
training-row manifest, cache checksums, no-peek audit, source-status separation
audit, uncertainty semantics note if needed, and negative controls. Missing
artifacts keep the candidate diagnostic-only or blocked.

## Limitations

- The contract does not estimate whether any residual-feature family has a
  genuine no-leakage predictive signal.
- The contract does not replace a future source-manifest or reveal protocol.
- The classification may need amendment if a later task proposes a feature
  shape outside the reviewed families.

## Verdict

`PARTIALLY_VALID`.

The task creates a usable no-leakage gate for future residual-feature work
while preserving current local-curvature, high-error-cluster, shell-axis, and
uncertainty evidence as bounded sandbox diagnostics.
