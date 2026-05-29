# Nuclear Controls-First Hypothesis Gauntlet

## Purpose

This note defines a **reusable contract** every future Nuclear Mass
Surface residual-hypothesis lane must satisfy before any candidate is
scored. It is downstream of, and consistent with, the existing
discipline documents:

- [`docs/nuclear-residual-feature-no-leakage-contract.md`](../nuclear-residual-feature-no-leakage-contract.md)
  (cross-family eligibility map)
- [`docs/nuclear-local-curvature-no-leakage-freeze-protocol.md`](../nuclear-local-curvature-no-leakage-freeze-protocol.md)
  (per-family freeze protocol for F1 / local curvature)
- [`docs/nuclear-prediction-reveal-protocol.md`](../nuclear-prediction-reveal-protocol.md)
- [`docs/result-promotion-protocol.md`](../result-promotion-protocol.md)
- [`docs/reviews/nuclear-shell-axis-post-audit-decision.md`](../reviews/nuclear-shell-axis-post-audit-decision.md)
- [`docs/reviews/nuclear-local-curvature-no-leakage-prototype.md`](../reviews/nuclear-local-curvature-no-leakage-prototype.md)
- [`docs/reviews/nuclear-new-lanes-decision-after-uncertainty.md`](../reviews/nuclear-new-lanes-decision-after-uncertainty.md)
- [`docs/campaigns/nuclear-mass-surface.md`](../campaigns/nuclear-mass-surface.md)

The gauntlet does **not** add `PRED-XXXX.yaml` entries, score any
reveal, fetch external data, promote any `CLAIM`/`KNOW`/`RESULT`, or
relax any existing no-leakage gate. It is a planning template that
agents copy into their hypothesis-lane PR before running any model.

## Why a Gauntlet?

Recent Nuclear evidence shows two failure modes that any new
hypothesis lane must explicitly defend against:

1. **Retrospective overreading.** `LOCAL-CURVATURE-001` looked
   promising under the original lane and survived several adversarial
   controls, but was falsified once the no-leakage prototype removed
   target-row contributions from the neighbor cache. Shell-axis
   coefficients are fragile under deterministic 8-of-11 resampling,
   even though the aggregate panels look favorable.
2. **Label-side leakage.** F2 (high-error cluster) labels were
   originally derived from baseline residuals themselves, so any
   "improvement" was definitionally circular until the labels were
   refactored to use only `Z`, `N`, and `A`.

Both modes are easy to miss in a single-run sandbox without a hard
controls-first contract. The gauntlet exists so that each lane spends
the up-front cost of declaring its inputs, controls, holdout, and
failure condition **before** any candidate score is computed.

## Eligibility Precondition

Before opening a new hypothesis-lane PR, confirm the family's
classification under the cross-family contract:

| Family | Class | Eligible for this gauntlet? |
| --- | --- | --- |
| F1 — local curvature | `predictive_eligible` under freeze protocol | yes, but only `LOCAL-CURVATURE-001` is admissible; `-002`/`-003` are falsified. |
| F2 — high-error cluster | `diagnostic_only` | yes, only with residual-free labels per F2-REQ-LABEL-FROM-Z-N-ONLY. |
| F3 — shell-axis | `predictive_eligible` (governed by TASK-0303 source preflight) | yes, but registry expansion stays blocked under shell-axis post-audit decision; lane stays `DIAGNOSTIC_ONLY` unless the source gate is satisfied. |
| F4 — source-status | `blocked` | no. Source-status remains diagnostic-only and is not promotable. |
| F5 — uncertainty-weighted residual | `predictive_eligible` under committed-uncertainty rule | yes, with frozen weighting scheme. |
| new family | unclassified | classify under the cross-family contract first; do not run the gauntlet on an unclassified family. |

A lane whose family is `blocked` or unclassified must stop and produce
either a classification update for the cross-family contract or an
explicit blocker review. It must not run the gauntlet to "see what
happens".

## Mandatory Lane Sections

Every Nuclear hypothesis-lane PR must include a planning artifact
(typically a `docs/reviews/nuclear-<family>-<lane-name>-plan.md` or
the agent run's `preflight.md`) with the following sections, filled
in **before** the candidate runs:

### 1. Hypothesis Family And Candidate Identity

- name the family (F1 / F2 / F3 / F5);
- name the candidate (e.g. `HIGHCLUSTER-Z-ONLY-001`);
- one-paragraph hypothesis statement in plain language;
- one-paragraph mechanism statement (what physical or structural
  observation the candidate is supposed to reflect);
- one-line scope statement on what the lane is **not** trying to do
  (e.g. "this lane does not test light-nuclei behavior").

### 2. Allowed Inputs

Explicit list of every input field the candidate may consume. Each
entry must appear in the **Allowed Inputs** section of the no-leakage
contract:

- `Z`, `N`, `A`, parities, deterministic functions thereof;
- magic-number proximity from the published `{2, 8, 20, 28, 50, 82,
  126, 184}` list;
- shell-distance proxies derived from `Z` and `N` only;
- committed measurement uncertainties from
  `data/nuclear_masses/nmd-*.yaml`;
- baseline-only neighbor residuals under the TASK-0352 freeze
  protocol with leave-one-out windows and per-fold caches (F1 only);
- frozen NMD-0002 training slice plus any committed pre-reveal
  validation slice used under retrospective time-split with verdict
  `INCONCLUSIVE`.

The lane may not consume any input not in this list without first
updating the no-leakage contract under a separate maintainer-approved
task.

### 3. Forbidden Inputs

Explicit re-statement of the forbidden-inputs list from the
no-leakage contract, plus any lane-specific additions. At minimum:

- the target row's own residual, mass, binding energy, or any
  function thereof;
- post-registration measurement values for any row in a `PRED-XXXX`
  target set;
- full-known neighbor residuals not available at prediction time;
- residuals from candidate-fit models (only baseline residuals are
  admissible);
- labels built from future comparison rows or
  AME-update-derived "was extrapolated" flags on the target row;
- training-set-membership flags, residual-quantile flags, or any
  feature whose value differs between the same row in the training
  slice and the holdout slice;
- empirical high-error flags derived from baseline residuals;
- source-status as a predictor (F4 is `blocked`).

### 4. Baseline

- name the baseline model (e.g. the canonical NMD-0002 baseline
  binding-energy fit);
- commit SHA or canonical artifact path of the baseline residuals
  used as neighbor inputs (F1) or as the comparison surface;
- one-line statement that **only baseline residuals** (never
  candidate-fit residuals) feed any neighbor aggregate or label.

### 5. Controls (minimum two)

Every lane must declare **at least two controls**, run them against
the same label / feature construction the candidate uses, and report
their metrics alongside the candidate's. Acceptable control families:

- **Matched random control.** Same row population, same evaluation
  subsets, label values drawn from the same marginal distribution but
  shuffled across rows. Demonstrates the candidate is not just
  fitting the residual distribution at random.
- **Smooth-A control.** A label or feature defined as a smooth
  monotonic function of `A` alone, matched in coarse scale to the
  candidate. Demonstrates the candidate is not a mass-smoothness
  artifact.
- **Asymmetry-only control.** A label or feature defined as a
  function of `(N - Z) / A` only. Demonstrates the candidate carries
  information beyond bulk asymmetry.
- **Cluster-label-shuffle control** (F2 only). Same cluster
  definition, labels shuffled across rows within the same coarse
  mass-region bin. Demonstrates the cluster structure carries
  information beyond chance partition of the dataset.
- **Near-null control** (F5 only). Same weighting scheme applied to
  a near-null surrogate signal. Demonstrates the weighting does not
  manufacture an improvement on its own.
- **Self-exclusion ablation** (F1 only). The same feature with the
  row's own contribution forced into the aggregate; should noticeably
  improve the candidate's score, demonstrating the candidate's
  leakage path is genuinely closed.

A lane that only beats one control (or one control family) does not
clear the gauntlet on candidate-vs-control comparison; the verdict
defaults to `DIAGNOSTIC_ONLY` or `INCONCLUSIVE` per the rules
below.

### 6. Holdout, Split, And Leave-One-Out Logic

- name the train / validation / holdout split used (typically the
  frozen NMD-0002 training slice plus a committed pre-reveal
  validation slice; retrospective time-split with verdict
  `INCONCLUSIVE` is the default);
- declare whether the lane uses leave-one-out logic (mandatory for
  F1 neighbor aggregates; mandatory for any F2 cluster whose
  definition could otherwise be influenced by the target row);
- name the per-fold cache rebuild policy (F1 only) and pin the cache
  commit SHA;
- exclude every `PRED-XXXX` target row from every other row's
  neighbor window or cluster definition;
- state the no-peek boundary: the lane may not see post-AME2020
  comparison rows for any row in the holdout slice.

### 7. Leakage Audit

A short checklist confirming that, for the declared inputs and label
construction:

- no input field crosses the train / validation / holdout / reveal
  boundary;
- no input field is a function of the target row's residual, mass,
  or binding energy;
- no candidate-fit residual is reused as an input;
- no future comparison row contributes to label construction;
- no full-known neighbor residual is used when the target row is in
  the holdout slice;
- F2 labels are deterministic functions of `Z`, `N`, `A`, parity,
  magic-distance, and committed uncertainties only;
- F1 caches are per-fold and exclude the target row's own
  contribution;
- F5 weighting uses only committed measurement uncertainties from
  `data/nuclear_masses/nmd-*.yaml`.

If any item fails, the lane stops and records a blocker review; the
candidate is not scored.

### 8. Failure Condition (Stop Condition)

Declare the explicit conditions under which the candidate is
classified as `NEGATIVE_RESULT` or `INCONCLUSIVE` **before** the
score is computed. At minimum:

- the candidate fails to beat both declared controls on the
  `full_known` aggregate by the declared survival margin
  (≥ 0.25 MeV inherited from the TASK-0352 freeze protocol on
  full_known); or
- the candidate beats controls on `full_known` but regresses on the
  primary holdout panel; or
- the leakage audit fails any item in section 7; or
- coefficient stability fails under leave-one-out resampling of the
  candidate's free parameters.

A failed candidate must preserve its evidence as a negative-result
review under `docs/reviews/nuclear-<family>-<lane-name>.md` and
must not silently spawn a follow-up "let's try slightly different
labels" task in the same PR.

### 9. Output Routing

Declare the canonical destination of the lane's outputs **before**
the score is computed. The lane may write:

- `agent_runs/AGENT-RUN-NNNN/agent_run.yaml`,
  `metrics.json`, `report.md`, `limitations.md`, `preflight.md`,
  `review_summary.md` (schema-valid against
  `physics_lab/schemas/agent_run.schema.json`);
- `docs/reviews/nuclear-<family>-<lane-name>.md`;
- tests for any reusable runner or feature-labeling code;
- a `promotion_boundary` block in `agent_run.yaml` with
  `writes_canonical_result: false`,
  `claim_promotion_allowed: false`,
  `prediction_registry_allowed: false`.

The lane **may not** write any of the following without a separate
maintainer-approved task that explicitly authorizes that artifact
class:

- `prediction_registry/nuclear_masses/PRED-XXXX.yaml`;
- `claims/CLAIM-XXXX.md`;
- `knowledge/KNOW-XXXX.md`;
- `results/EXP-XXXX/RUN-XXXX/result.yaml`;
- any reveal score against future comparison rows.

### 10. Public Wording Boundary

Declare the wording the lane may use in its review and report:

- allowed: "retrospective", "sandbox evidence", "negative result",
  "diagnostic only", "bounded follow-up candidate", "inconclusive",
  "candidate beats / fails declared controls by X on subset Y",
  "no-leakage prototype", "preserved as failure-mode atlas";
- forbidden: "discovery", "new nuclear law", "broad formula",
  "first-principles", "explains nuclear masses", "predicts" without
  a frozen `PRED-XXXX` entry, "we have found", "anomaly explained",
  "shell-axis breakthrough", "near-magic regularity".

The wording boundary applies to the review note, the
`agent_run.yaml` summary, the PR body, and any associated chat
output.

## Verdict Vocabulary

A completed lane reports exactly one of:

- **`BOUNDED_FOLLOWUP_CANDIDATE`** — the candidate beats every
  declared control by the declared margin on `full_known`, does not
  regress the primary holdout panel, and passes every leakage-audit
  item. The candidate enters scope for a *separate*
  maintainer-approved no-leakage predictive implementation task; this
  lane does not author any `PRED-XXXX` entry. Use this verdict
  sparingly.
- **`DIAGNOSTIC_ONLY`** — the candidate either fails to beat all
  controls on `full_known`, or beats them on aggregate but regresses
  on the primary holdout panel or on a load-bearing subset, or is in
  a family that the cross-family contract holds at
  `diagnostic_only`. The lane is preserved as a failure-mode atlas
  and may inform future control design.
- **`NEGATIVE_RESULT`** — the candidate fails to beat at least one
  control or fails the leakage audit, and the lane explicitly
  classifies the candidate as falsified under its declared scope.
  Preserve the negative result as sandbox memory.
- **`INCONCLUSIVE`** — the lane was unable to evaluate the
  candidate against its declared controls or holdout (e.g. missing
  source data, broken cache, ambiguous label construction). Document
  the blocker and do not retry under the same name without
  resolution.

A lane may not invent a fifth verdict (`PROMISING`, `NEEDS_WORK`,
`PARTIALLY_VALID`, etc.) or escape the gauntlet by mixing categories
("inconclusive but worth a follow-up wave" is forbidden).

## Reusable Outside Nuclear?

The gauntlet's structure (eligibility precondition → mandatory
sections → verdict vocabulary) is plausibly reusable for other
residual-style campaigns (e.g. Exoplanet Mass-Radius residuals,
Materials Property Residuals). Reuse should be evaluated case by
case; this note does not extend the contract beyond Nuclear by
itself.

If a future task wants to generalize the gauntlet to another
campaign, it should:

1. produce a campaign-specific eligibility map analogous to the
   cross-family contract;
2. adapt the controls list to the campaign's leakage failure modes;
3. re-derive the survival margin from a campaign-specific freeze
   protocol;
4. open a new `docs/notes/<campaign>-controls-first-hypothesis-gauntlet.md`
   rather than overload this Nuclear-specific document.

## Limitations

- This gauntlet is a planning template. It does not lint, validate,
  or block a PR by itself. Compliance is enforced by per-task
  preflight checks and by maintainer review.
- The survival margin (≥ 0.25 MeV on `full_known`) and the
  minimum-two-controls rule are inherited from the TASK-0352 freeze
  protocol and from the F2 control gate; this gauntlet does not
  relax either.
- The eligibility table reflects feature families that have
  surfaced so far. New families need their own classification under
  the cross-family contract before they can run this gauntlet.
- The gauntlet does not authorize any change to canonical
  `results/`, `prediction_registry/`, `claims/`, or `knowledge/`
  files. Those changes remain maintainer-only and require their own
  authorized tasks.

## What This Gauntlet Does Not Do

- It does not add any `PRED-XXXX.yaml` entry.
- It does not score any reveal.
- It does not promote any `CLAIM-*`, `KNOW-*`, `RESULT-*`, or
  canonical hypothesis.
- It does not fit any candidate or run any sandbox lane by itself.
- It does not relax the TASK-0303 shell-axis source preflight, the
  TASK-0352 freeze protocol, the no-leakage contract, or the
  prediction-reveal protocol.
- It does not reopen `LOCAL-CURVATURE-001` as a positive candidate
  (the no-leakage falsification stands).
- It does not reopen shell-axis as a registry-expansion lane (the
  post-audit decision keeps shell-axis `DIAGNOSTIC_ONLY` until the
  source gate is satisfied).
