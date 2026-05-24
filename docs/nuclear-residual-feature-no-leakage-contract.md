# Nuclear Residual-Feature No-Leakage Contract

## Purpose

This contract defines which nuclear residual-derived feature families may be
used by a later pre-reveal prediction task, which must stay diagnostic-only,
and which are blocked unless redesigned. It is a gate between retrospective
sandbox diagnostics and any future prediction-registry implementation.

This task does not fit a model, add `PRED-*` entries, score reveal data, fetch
external measurements, promote claims, or rewrite canonical results.

## Scope

The contract applies to future Nuclear Mass Surface tasks that want to use
residual-adjacent structure from the committed nuclear benchmark stack,
including local-curvature, high-error-cluster, shell-axis, source-status, and
uncertainty-weighted residual features.

It inherits the boundaries in:

- [Nuclear Local-Curvature No-Leakage Freeze Protocol](./nuclear-local-curvature-no-leakage-freeze-protocol.md)
- [Nuclear Prediction Reveal Protocol](./nuclear-prediction-reveal-protocol.md)
- [Nuclear Mass Prediction Registry](../prediction_registry/nuclear_masses/README.md)

## Feature Eligibility Classes

| Feature family | Status | Allowed form | Blocked form |
| --- | --- | --- | --- |
| Local-curvature residual features | `CONDITIONAL_PREDICTIVE_ELIGIBLE` | Leave-one-out, training-only or per-fold neighbor caches built before reveal; baseline-only residuals from committed pre-registration training rows; future target rows excluded from every neighbor window. | Self-inclusive chain/isotone means, full-known neighbor residuals, full-dataset normalization, or any cache that uses holdout/reveal rows unavailable at prediction time. |
| High-error-cluster features | `DIAGNOSTIC_ONLY` by default; `CONDITIONAL_PREDICTIVE_ELIGIBLE` only after redesign | Source-independent proxies known before reveal, such as `(Z, N, A)`, magic-number proximity, parity, neutron excess, and pre-registered region descriptors. | Labels computed from target residuals, top-error membership, post hoc high-error thresholds, or future comparison rows. |
| Shell-axis features | `CONDITIONAL_PREDICTIVE_ELIGIBLE` | Deterministic shell descriptors from `(Z, N, A)`, magic-number distances, parity, and pre-registered target-batch metadata. Existing shell-axis evidence remains diagnostic unless a separate source-gated reveal task authorizes scoring. | Treating retrospective shell-axis improvements as claim support; adding registry entries from post-audit evidence; using post-registration source exposure to select targets or coefficients. |
| Source-status features | `LIMITED_PREDICTIVE_ELIGIBLE` for pre-registered metadata; otherwise `BLOCKED` | Source-manifest fields frozen before prediction, reported separately from residual performance, and audited so they do not encode training membership. | Flags that reveal whether a row is in training, holdout, measured after registration, or available in a future comparison source. |
| Uncertainty-weighted residual features | `DIAGNOSTIC_ONLY` by default; `CONDITIONAL_PREDICTIVE_ELIGIBLE` only with pre-frozen uncertainty metadata | Uncertainty class or weighting rules frozen before prediction for all candidate rows, with fit-grade semantics documented and no target residual dependency. | Target measured uncertainty learned after registration, inverse-error weights derived from residual size, or any weighting that changes after future measurements are inspected. |

`CONDITIONAL_PREDICTIVE_ELIGIBLE` means the feature family may be proposed in a
later implementation task only when the task supplies the artifacts and audits
listed below. It is not permission to register predictions in this task.

## Allowed Inputs For Future Pre-Reveal Prediction

Future predictive tasks may use only inputs known before the prediction
boundary:

- target identifiers and deterministic descriptors: `Z`, `N`, `A`, `N - Z`,
  parity, mass region, and source-independent nuclear descriptors;
- magic-number proximity and shell-closure distances computed directly from
  `(Z, N)`;
- committed pre-registration training rows explicitly listed by dataset id,
  row id, and git commit;
- baseline model terms and baseline-only residuals for training rows that are
  inside the approved training or per-fold cache;
- source-manifest metadata frozen before target selection, when it is not a
  proxy for training or reveal membership;
- uncertainty metadata only when it is available before prediction for all
  relevant rows and has documented semantics.

## Forbidden Inputs

The following inputs are forbidden for any prediction-registry candidate:

- target residuals, target measured masses, target binding energies, or target
  measurement uncertainties that were not available before registration;
- post-registration measurement values or source rows inspected before
  prediction freezing;
- full-known neighbor residuals unavailable at prediction time;
- self-inclusive local residual aggregates;
- labels computed from future comparison rows, including high-error cluster
  labels, top-error membership, or source availability after registration;
- source-status fields that encode training membership, holdout membership, or
  future reveal availability;
- feature normalization, weighting, target selection, or coefficient selection
  computed over the full known dataset when the future task claims a pre-reveal
  boundary.

## Minimum Artifact Checklist

A later predictive implementation task must provide all of the following
before any registry entry or reveal-scoring task can be reviewed:

- feature manifest naming every input field, its source file, its availability
  date or commit, and whether it is predictive-eligible, diagnostic-only, or
  blocked;
- frozen training-row manifest with dataset ids, row ids, source-status
  semantics, and git commit;
- per-fold or pre-reveal feature cache manifest with checksums and explicit
  target-row exclusion rules;
- no-peek audit proving that holdout and future reveal rows are absent from
  training caches, neighbor windows, normalization, target selection, and
  coefficient selection;
- source-status separation audit showing measured/extrapolated/source-class
  fields do not act as training-membership proxies;
- uncertainty semantics note if any uncertainty-derived feature or weight is
  used;
- negative controls appropriate to the feature family, including self-exclusion
  for local-curvature, shuffled or near-null controls for residual structure,
  and source-status ablation when metadata is used;
- explicit wording boundary stating that sandbox diagnostics, registry
  entries, and reveal comparisons do not promote claims.

## Review Consequence

If any required artifact is missing, the candidate must remain
`DIAGNOSTIC_ONLY` or be marked `BLOCKED`. Negative and inconclusive outcomes
must stay visible in the review note; they are not cleaned up by narrowing the
feature definition after scoring.

## Verdict

`PARTIALLY_VALID` protocol contract.

The residual-feature families now have a reviewable no-leakage boundary for
future implementation tasks. No prediction entries, reveal scores, or promoted
claims are created by this task.
