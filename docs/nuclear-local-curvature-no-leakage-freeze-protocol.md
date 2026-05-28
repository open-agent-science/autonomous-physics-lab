# Nuclear Local-Curvature No-Leakage Freeze Protocol

## Purpose

This protocol locks the rules a future no-leakage local-curvature
candidate must satisfy **before** it can be considered for a frozen
prediction-registry entry or a real-reveal scoring task. It exists
because TASK-0339 / AGENT-RUN-0026 demonstrated that local-curvature
features computed from committed full-known neighbor residuals
produce a misleadingly strong diagnostic signal — the same neighbor
residuals contain target information through the row's own
contribution to nearby chain or isotone statistics.

The protocol is upstream of any future predictive local-curvature
implementation task. It does not fit any model, does not add a
prediction-registry entry, does not score any reveal, does not
fetch external data, and does not promote any claim.

## Scope

The protocol applies to:

- any Nuclear Mass Surface candidate whose features include
  per-target neighbor residuals, chain-mean residuals, isotone-mean
  residuals, or local-curvature signal derived from baseline
  residuals on nearby `(Z, N)` rows;
- any candidate that is intended to enter the prediction registry
  (`prediction_registry/nuclear_masses/PRED-XXXX.yaml`) for a future
  reveal-scoring task;
- bounded follow-up correction-hypothesis experiments that use
  neighbor-derived features and need a defensible no-leakage
  boundary.

It does **not** apply to:

- the existing TASK-0339 / AGENT-RUN-0026 sandbox diagnostic itself
  (which is already labelled `INCONCLUSIVE` and stays sandbox-only);
- frozen `PRED-0063`..`PRED-0068` shell-axis mini-wave entries, which
  use deterministic shell-distance features and are governed by the
  TASK-0303 source preflight;
- baseline benchmark replays that score the frozen semi-empirical
  model without adding new candidate features.

It is not a license to:

- promote any local-curvature candidate to a claim or canonical
  result;
- relax the TASK-0303 no-peek audit for shell-axis entries;
- run a real reveal of any new prediction entry before a separate
  maintainer-approved reveal task lands;
- describe local-curvature evidence as a discovery of a nuclear-
  mass correction.

## The Leakage Problem in One Sentence

A row's mass `M(Z, N)` enters every chain or isotone statistic that
includes it, so any feature that aggregates "neighbor residuals"
without first holding out the row's own contribution from those
aggregates is reading the target through a one-hop window.

The TASK-0339 / AGENT-RUN-0026 candidates achieved large `-2 MeV`
full-known delta MAE because neighbor windows centered at each row
used the same row's residual in the chain or isotone mean. A future
predictive use must close that window.

## Forbidden Feature Inputs

The following feature inputs are **forbidden** in any future
no-leakage local-curvature candidate intended for the prediction
registry. Each is the canonical source of the leakage observed in
AGENT-RUN-0026.

1. **Per-target self-inclusive chain mean residual.** Computing
   `mean(residual(Z, N') for N' in chain)` while `N' = N` is
   included in the average. The row's own residual then contributes
   to its own feature.
2. **Per-target self-inclusive isotone mean residual.** Same as
   above for `Z' = Z` aggregations.
3. **Self-inclusive curvature stencils.** Any second-difference or
   smoothing kernel of the form
   `(residual(N-1) + residual(N+1)) / 2 - residual(N)` is allowed
   only if `residual(N)` is the *baseline-only* prediction's
   residual; using a residual that itself depended on the target
   value through any earlier fit re-introduces leakage.
4. **Neighbor windows that cross the validation / holdout boundary.**
   A training row whose neighbor window pulls in a holdout-row
   residual leaks holdout information into training. The window
   must be re-evaluated per fold against the active split.
5. **Full-dataset chain or isotone normalisation.** Any feature
   `(residual - chain_mean) / chain_std` computed on the entire
   dataset before the fold split is leakage; the normalisation must
   be re-fit per fold.
6. **Source-status features that encode "is this row in the
   measured AME slice".** Such features are a proxy for "is the
   row part of training" and let a model trivially separate
   training rows from holdout rows.

## Required Feature Inputs

A no-leakage candidate must use one of the following feature shapes:

A. **Leave-one-out neighbor windows.** Compute every neighbor
   aggregate excluding the row itself. The simplest form is
   `chain_residual_excluding_self(Z, N) =
   mean(baseline_residual(Z, N') for N' != N in chain)`.

B. **Strict baseline-residual inputs.** All neighbor residuals must
   come from the **baseline-only** semi-empirical prediction (i.e.
   `residual = measured - baseline`), never from a candidate model
   that has itself seen the target during fitting.

C. **Per-fold neighbor caches.** When holdout folds are used, the
   neighbor window must be recomputed per fold so a training row
   never pulls a holdout row's residual into its own feature.

D. **Documented missing-neighbor behaviour.** Every feature must
   declare what happens when the requested neighbor row is missing
   (see "Missing-Neighbor Handling" below). Default-zero, "skip
   silently", and "imputed from chain mean" are all distinct
   choices with different leakage profiles; the candidate must pick
   one in advance and document it.

E. **Source-status separation.** Any feature that depends on
   "is row measured" must derive that flag from the row's
   `source_status` field in `data/nuclear_masses/nmd-*.yaml`, not
   from membership in the training slice. A row that is measured
   but held out must read identically to a row that is measured and
   in training.

## Training / Validation / Holdout / Reveal Separation

The fold structure for a no-leakage local-curvature candidate must
mirror the existing nuclear-mass holdout protocol, with one
explicit addition for neighbor-derived features.

1. **Training rows.** Use the frozen NMD-0002 training slice (or
   the slice the future task explicitly pins). Coefficients are
   fit on this slice only.
2. **Validation rows.** Pre-reveal validation uses the rows in
   `data/nuclear_masses/post_ame2020_holdout.yaml` only when the
   future task explicitly enables retrospective time-split. If
   retrospective validation is used, the verdict must remain
   `INCONCLUSIVE` per the established post-AME2020 boundary.
3. **Future-reveal rows.** Rows committed to a `PRED-XXXX.yaml`
   target set must be **excluded** from every neighbor window
   computation on every other row's features. Failure to exclude
   them re-introduces target information through one-hop windows
   even after the row is hidden.
4. **Per-fold neighbor cache.** When a multi-fold strategy is used,
   the neighbor cache for each fold must contain only rows
   admissible into that fold (training-only). The cache must be
   regenerated per fold; precomputing once over the full dataset is
   forbidden.
5. **Reveal boundary.** A reveal scoring task may evaluate the
   candidate against newly admitted measured rows only when the
   candidate's frozen features were computed against the
   pre-admission neighbor cache. The reveal task must record the
   commit SHA of the cache it used.

## Missing-Neighbor Handling

A neighbor window typically requests `chain(Z) ∩ {N-1, N+1, ...}`.
When a requested neighbor row is missing, the candidate must use
exactly one of these strategies and record the choice in the PRED
file's `model_reference.frozen_parameters_note`:

| Strategy | When acceptable | Trade-off |
| --- | --- | --- |
| `skip_silent` | When the candidate is robust to variable-width windows. | Reduces window quality near data edges. |
| `pad_zero` | When the baseline residual is centred at zero. | Biases features toward chain-rich regions. |
| `pad_chain_mean` | When chain-mean computation also excludes self. | Easy to leak by accident; use per-fold cache strictly. |
| `widen_window` | When chain coverage is sparse. | Smears local-curvature signal across larger windows. |
| `mark_row_excluded` | When the row cannot be predicted reliably. | Reduces target coverage; preserves discipline. |

Mixing strategies within a single candidate is forbidden. A
candidate that uses different strategies for different target rows
becomes an ad-hoc imputation surface.

## Sparse-Chain, Extrapolated-Row, and Source-Status Handling

- **Sparse-chain rows** — when a target row's chain `Z` has fewer
  than two committed neighbors, the row is `mark_row_excluded`
  unless the candidate explicitly pins a `widen_window` rationale.
- **Extrapolated rows** — when a target row's source is
  `extrapolated` (AME extrapolation flag), the row is treated as
  unmeasured for neighbor-window purposes and must not contribute
  to any other row's chain mean.
- **Source-status mixing** — measured and extrapolated rows must be
  separable per the existing nuclear-mass holdout protocol. The
  no-leakage candidate must not silently mix them in a single
  neighbor mean. When mixing is needed, the candidate must report
  measured-only and mixed metrics side by side.

## Minimum Controls Before Registry Entry

A future predictive local-curvature candidate may enter
`PRED-XXXX.yaml` only after all of the following controls have been
run and recorded in the accompanying review note:

1. **Self-exclusion ablation.** Re-run the candidate twice: once
   with leave-one-out neighbor windows (the canonical form) and
   once with self-inclusive neighbor windows (the leaky form). The
   delta MAE between the two reveals the size of the leakage signal.
   The candidate may only be registered when the leave-one-out form
   alone improves on the baseline.
2. **Chain-shuffled control.** Reuse the
   `LOCAL-CONTROL-001`-style shuffled-chain control from
   AGENT-RUN-0026. The candidate's improvement must be **larger**
   than the shuffled control's improvement on the same metric.
3. **Smooth-window control.** Reuse the
   `LOCAL-CONTROL-002`-style smooth-window control. The candidate
   must beat it on at least the magic and neutron-rich subsets.
4. **Near-null negative control.** Add a near-null candidate that
   sets the local-curvature feature weight to zero. The near-null
   must produce a measurable regression that is recorded explicitly
   in the registry entry's `limitations` list.
5. **Per-fold neighbor cache audit.** The reviewer must verify the
   cache SHA per fold. A single shared cache across folds
   invalidates the registry entry.
6. **Source-status separation audit.** The reviewer must verify
   that `source_status` features do not act as training-membership
   proxies (compute the candidate's accuracy on measured vs
   extrapolated rows separately).

A candidate that fails any of these controls is not eligible for
registry entry. Failing-control evidence is preserved in the
sandbox review with verdict `INCONCLUSIVE` or `FALSIFIED` as
appropriate.

## Recommendation on TASK-0351

TASK-0351 (described in the campaign documentation as the
"local-curvature retrospective falsification" lane) must reach
`DONE` and produce an explicit pass / fail verdict **before** any
future predictive local-curvature implementation task is opened.
A predictive candidate that has not been tested against the
TASK-0351 retrospective baseline does not have the falsification
evidence the registry policy expects.

If TASK-0351 has not yet been completed, a future task should not
attempt to register a predictive local-curvature candidate. The
existing TASK-0339 sandbox surface remains the diagnostic of
record, with verdict `INCONCLUSIVE`.

## What This Protocol Did Not Do

- It did not fit any model.
- It did not add or modify any `PRED-XXXX.yaml` entry.
- It did not fetch any external data.
- It did not score any reveal.
- It did not promote any claim, knowledge entry, or canonical
  result.
- It did not change the existing TASK-0339 / AGENT-RUN-0026 sandbox
  verdict from `INCONCLUSIVE`.

## Relationship to Other Protocols

- [`./nuclear-mass-holdout-protocol.md`](./nuclear-mass-holdout-protocol.md)
  defines the holdout discipline this protocol inherits;
- [`./nuclear-prediction-reveal-protocol.md`](./nuclear-prediction-reveal-protocol.md)
  defines the reveal-scoring contract any predictive local-curvature
  candidate must satisfy;
- [`./nuclear-reveal-source-readiness-checklist.md`](./nuclear-reveal-source-readiness-checklist.md)
  defines the source preflight that a future reveal task must run;
- [`./blind-holdout-benchmark-protocol.md`](./blind-holdout-benchmark-protocol.md)
  remains the cross-campaign holdout reference.

## Limitations

- The leakage modes documented here are the ones AGENT-RUN-0026
  surfaced. A future candidate may introduce a new feature shape
  that bypasses this checklist; the protocol should be amended
  rather than relaxed if that happens.
- The required controls (1)–(6) are a minimum, not a maximum. A
  candidate that is unusual in shape (e.g. uses third-order
  neighbor information) may need additional controls; the reviewer
  must call them out before scoring.
- This protocol does not estimate how strong the genuine
  no-leakage local-curvature signal is. AGENT-RUN-0026's `-2 MeV`
  number was leakage-amplified; the residual genuine signal may be
  much smaller.
- The protocol does not authorise live external data fetches or
  changes to canonical result artifacts.

## Verdict

`PARTIALLY_VALID` for the no-leakage local-curvature freeze
contract. The forbidden feature inputs, required feature inputs,
fold structure, missing-neighbor strategies, sparse-chain handling,
source-status separation, six minimum controls, and TASK-0351
prerequisite are now reviewable in advance. No candidate has been
registered; no metric has been computed. The next allowed step is a
TASK-0351 completion (retrospective falsification) followed by a
maintainer-approved predictive implementation task that satisfies
this protocol verbatim.
