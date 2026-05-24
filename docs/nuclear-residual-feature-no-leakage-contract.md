# Nuclear Residual-Feature No-Leakage Contract

## Purpose

This contract names which Nuclear Mass Surface residual-feature
families are **predictive-eligible**, which are **diagnostic-only**,
and which are **blocked**, and it defines the minimum artifact
checklist any later no-leakage predictive implementation task must
deliver before a `PRED-XXXX.yaml` entry or a reveal-scoring task is
opened.

It is the upstream eligibility gate for every Nuclear residual lane
that has surfaced so far: local curvature, high-error cluster,
shell-axis, source-status, and uncertainty-weighted residual. It
does **not** fit any model, does **not** register a prediction
entry, does **not** fetch external data, does **not** score any
reveal, and does **not** promote any claim.

This contract is downstream of, and consistent with, the
TASK-0352 freeze protocol
(`docs/nuclear-local-curvature-no-leakage-freeze-protocol.md`). The
freeze protocol locks the per-feature mechanics for one family
(local curvature). This contract is the cross-family eligibility map
plus the minimal implementation checklist.

## Inputs Reviewed

- `docs/reviews/nuclear-local-curvature-hypothesis-lane.md`
  (TASK-0339 / AGENT-RUN-0026 sandbox local-curvature lane)
- `docs/reviews/nuclear-local-curvature-adversarial-controls.md`
  (TASK-0351 / AGENT-RUN-0031 adversarial controls;
  `LOCAL-CURVATURE-001` survived, `-002` and `-003` falsified)
- `docs/reviews/nuclear-high-error-cluster-hypothesis-lane.md`
  (TASK-0343 / AGENT-RUN-0030 high-error cluster lane;
  `HIGHCLUSTER-001` and `HIGHCLUSTER-003` partially valid;
  matched controls beat by candidates)
- `docs/nuclear-local-curvature-no-leakage-freeze-protocol.md`
  (TASK-0352 per-family freeze protocol)
- `docs/nuclear-prediction-reveal-protocol.md`
- `prediction_registry/nuclear_masses/README.md`

## Feature-Family Classification

Each family is classified along three axes:

- **Eligibility class** — `predictive_eligible`, `diagnostic_only`, or
  `blocked`.
- **Leakage profile** — the canonical leakage channel for the family.
- **Promotion path** — what a future task must do to move a member of
  the family toward a `PRED-XXXX.yaml` entry, or why no such move is
  authorised.

### F1. Local-curvature residual features (chain / isotone neighbor
aggregates, second differences)

- **Eligibility class:** `predictive_eligible` **only** under the
  TASK-0352 freeze protocol.
- **Leakage profile:** the target row enters the chain or isotone
  mean used by its own feature; full-known neighbor caches reuse
  holdout residuals across folds; baseline residuals derived from
  candidate fits feed back into neighbor aggregates.
- **Promotion path:**
  1. Implement leave-one-out neighbor windows
     (`F1-REQ-LOO-WINDOW`).
  2. Use **baseline-only** residuals as the neighbor input; no
     candidate-fit residuals
     (`F1-REQ-BASELINE-ONLY-INPUT`).
  3. Recompute the neighbor cache **per fold** against the active
     train / validation split
     (`F1-REQ-PER-FOLD-CACHE`).
  4. Exclude `PRED-XXXX` target rows from every other row's
     neighbor window (`F1-REQ-PRED-EXCLUSION`).
  5. Pick and document one missing-neighbor strategy
     (`F1-REQ-MISSING-NEIGHBOR-DECLARED`).
  6. Survive the six TASK-0352 minimum controls
     (self-exclusion ablation, chain-shuffled, smooth-window,
     near-null, per-fold cache audit, source-status separation)
     with a primary survival margin of at least 0.25 MeV on
     `full_known` and majority wins across per-subset
     diagnostics. The adversarial controls TASK-0351 has already
     added (closest-neighbor only, label shuffle, smoother) count
     toward this minimum and may not be omitted.

  Only `LOCAL-CURVATURE-001` (the predecessor candidate that
  survived TASK-0351) is admissible as a future implementation
  target. `LOCAL-CURVATURE-002` and `-003` are
  **falsified** and remain sandbox memory only.

### F2. High-error cluster correction features (per-cluster offset,
per-cluster weighted residual)

- **Eligibility class:** `diagnostic_only`. **Not promotable** until
  the cluster definition is anchored on features that do **not**
  use the target residual.
- **Leakage profile:** the cluster label
  ("near magic high-error", "neutron-rich high-error",
  "sparse local high-error") is currently derived from the
  baseline residual itself. A predictive use must compute the
  cluster label from `Z`, `N`, `A`, magic-number proximity, and
  committed measurement uncertainties **only** — never from the
  baseline residual of the target row.
- **Promotion path:**
  1. Replace residual-derived cluster boundaries with deterministic
     `Z`/`N`-only or `A`-bin boundaries
     (`F2-REQ-LABEL-FROM-Z-N-ONLY`).
  2. Run the TASK-0343 control gate again with the new label, so
     `HIGHCLUSTER-CONTROL-001` (matched-random),
     `HIGHCLUSTER-CONTROL-002` (smooth-A), and
     `HIGHCLUSTER-CONTROL-003` (cluster-label-shuffle) all evaluate
     against the same label assignment
     (`F2-REQ-RERUN-CONTROL-GATE`).
  3. If the residual-free label still beats every control by a
     declared margin on at least one subset, the lane re-enters
     scope for a future predictive implementation task; otherwise
     it stays diagnostic-only and is preserved as a failure-mode
     atlas.

### F3. Shell-axis features (magic-number proximity, dual-anchor
weighting)

- **Eligibility class:** `predictive_eligible`. Already governed by
  the existing TASK-0303 source preflight and the frozen
  `PRED-0063`..`PRED-0068` mini-wave.
- **Leakage profile:** low. Shell-distance features depend on `Z`,
  `N`, and published magic numbers — no target residual is
  consumed.
- **Promotion path:** continues under TASK-0303 source preflight
  plus the prediction-reveal protocol
  (`docs/nuclear-prediction-reveal-protocol.md`). No new
  classification is required by this contract. Future shell-axis
  PRED entries above the existing wave still require their own
  maintainer-approved task before any reveal scoring.

### F4. Source-status features (measured vs extrapolated, AME2020
boundary)

- **Eligibility class:** `diagnostic_only`. **Not promotable** to
  the prediction registry. Source-status is a provenance label
  about the dataset, not a feature of nuclear structure; using it
  as a predictor lets the model trivially separate training-slice
  rows from holdout rows.
- **Leakage profile:** binary source-status is correlated with
  training-set membership for the curated NMD-0002 slice and with
  comparison-row presence for the post-AME2020 holdout slice. A
  predictor that uses it leaks the slice identity, not the row
  physics.
- **Promotion path:** none. Source-status remains a
  provenance-diagnostic field only. Future row-curation tasks may
  refine the field semantics; they may not promote it to a
  predictive feature.

### F5. Uncertainty-weighted residual features (sigma-weighted
neighbor residuals)

- **Eligibility class:** `predictive_eligible` **only** when the
  uncertainty values are committed at row ingestion time and the
  weighting scheme is locked **before** the candidate is fit.
- **Leakage profile:** if the uncertainty estimate is itself a
  function of the residual (e.g. an empirical "high-error percentile
  flag"), the weighting re-encodes the target. If the uncertainty
  estimate is an external committed measurement uncertainty, the
  weighting is leakage-safe.
- **Promotion path:**
  1. Use only committed measurement uncertainties from the curated
     dataset; no residual-derived weights
     (`F5-REQ-COMMITTED-UNCERTAINTY-ONLY`).
  2. Freeze the weighting scheme in the
     `experiment_proposals/nuclear-mass/EXP-PROPOSAL-XXXX.yaml`
     before any candidate fit
     (`F5-REQ-WEIGHTING-FROZEN`).
  3. Run a `near-null` control with the same weighting and confirm
     it does not beat the unweighted baseline by more than the
     declared survival margin
     (`F5-REQ-NEAR-NULL-CONTROL`).

## Allowed Inputs for a Pre-Reveal Predictive Implementation

A future no-leakage predictive implementation task for any of the
predictive-eligible families above may consume **only** these
inputs:

- `Z`, `N`, `A` and any deterministic function of them
  (e.g. `(N - Z) / A`, even/odd parities, mass-number bins);
- magic-number proximity computed from published magic-number lists
  (`{2, 8, 20, 28, 50, 82, 126, 184}`);
- shell-distance proxies derived from `Z` and `N` only;
- committed measurement uncertainties from the curated
  `data/nuclear_masses/nmd-*.yaml` files;
- **baseline-only** neighbor residuals computed under the TASK-0352
  freeze protocol, with leave-one-out neighbor windows and per-fold
  caches;
- the frozen pre-registration training slice (NMD-0002) and any
  explicitly committed pre-reveal validation slice
  (post-AME2020 holdout) used under retrospective time-split with
  verdict `INCONCLUSIVE`.

## Forbidden Inputs

A future no-leakage predictive implementation task **may not**
consume any of the following:

- the target row's own residual, mass, binding energy, or any
  function thereof;
- post-registration measurement values for any row in a `PRED-XXXX`
  target set;
- full-known neighbor residuals that are not available at prediction
  time;
- residuals computed from candidate-fit models (only baseline
  residuals are admissible neighbor inputs);
- labels computed from future comparison rows, including any
  AME-update-derived "was extrapolated" flag on the target row;
- training-set-membership flags, residual-quantile flags, or any
  feature whose value differs between a row in the training slice
  and the same row in the holdout slice;
- empirical high-error flags derived from baseline residuals;
- features that cross the train / validation / holdout / reveal
  boundary in any direction.

## Minimal Artifact Checklist for a Predictive Implementation Task

Any later task that intends to convert a predictive-eligible
candidate into a `PRED-XXXX.yaml` entry must deliver, at minimum:

1. A canonical `tasks/TASK-XXXX-*.yaml` referencing this contract,
   the TASK-0352 freeze protocol, and the
   `docs/nuclear-prediction-reveal-protocol.md`.
2. A paired
   `hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-XXXX-*.yaml`
   and `experiment_proposals/nuclear-mass/EXP-PROPOSAL-XXXX-*.yaml`
   that explicitly state which feature family (F1, F3, or F5) the
   candidate belongs to and enumerate every input field by name.
3. A deterministic runner under `scripts/run_nuclear_*.py` that
   exercises the leave-one-out neighbor cache (F1) or the locked
   weighting (F5) and emits a JSON manifest of every feature value
   per row.
4. A control suite that includes, at minimum:
   - self-exclusion ablation (the same feature with the row's own
     contribution forced into the aggregate; should noticeably
     improve, demonstrating the leakage path is closed in the
     candidate);
   - the six TASK-0352 minimum controls for F1, or the
     near-null control for F5;
   - the F2-style label-shuffle control adapted to the feature
     family.
5. An `agent_runs/AGENT-RUN-NNNN/` bundle with
   `agent_run.yaml`, `metrics.json`, `report.md`,
   `limitations.md`, `preflight.md`, and `review_summary.md`,
   schema-valid against `physics_lab/schemas/agent_run.schema.json`.
6. A `docs/reviews/nuclear-<family>-no-leakage-implementation.md`
   review note recording the survival margin per subset, the
   control gate outcome, and the declared promotion boundary.
7. A pinned per-fold neighbor cache commit SHA recorded inside the
   agent_run report when F1 features are used.
8. An explicit `promotion_boundary` block in `agent_run.yaml` with
   `writes_canonical_result: false` and
   `claim_promotion_allowed: false`. A `PRED-XXXX.yaml` entry is
   created only by a separate maintainer-approved task downstream
   of the agent run.

## What This Contract Does Not Do

- It does not add any `PRED-XXXX.yaml` entry.
- It does not score any reveal.
- It does not promote any claim, knowledge entry, RESULT-*, or
  canonical hypothesis.
- It does not fit any candidate or run any sandbox lane.
- It does not relax the TASK-0303 shell-axis source preflight, the
  TASK-0352 freeze protocol, or the prediction-reveal protocol.

## Recommended Follow-Up Tasks

These are recommendations only; this contract does not create
canonical tasks. Each would be a separate maintainer-approved
task.

- **R-F1.** No-leakage local-curvature predictive implementation
  for `LOCAL-CURVATURE-001`, implementing the F1 promotion path
  end to end (leave-one-out cache, per-fold rebuild, full TASK-0352
  control suite, no PRED entry; PRED entry is a downstream task).
- **R-F2.** High-error cluster label refactor to a Z/N/A-only
  definition, rerun of the TASK-0343 control gate, and a
  decision review note declaring whether F2 re-enters
  predictive-eligible scope.
- **R-F5.** Uncertainty-weighted predictive implementation using
  only committed measurement uncertainties and a frozen weighting
  scheme; documents the near-null control outcome.

## Limitations

- The classification is based on the residual lanes that have
  surfaced so far. New families (e.g. parity-pair residuals,
  deformation-proxy residuals) require their own classification
  before any predictive implementation.
- The minimum survival margin (0.25 MeV) and the six-control
  minimum are inherited from the TASK-0352 freeze protocol; this
  contract does not relax them.
- This contract is policy, not code; it does not lint, validate, or
  block a PR by itself. Compliance is enforced by the per-task
  preflight checks in any future predictive implementation task.
