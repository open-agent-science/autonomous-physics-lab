# Nuclear Mass Holdout Protocol

## Purpose

This protocol defines how the nuclear mass campaign should evaluate correction
families after the baseline benchmark exists.

The goal is to distinguish:

- interpolation on familiar nuclides;
- generalization across isotope structure;
- shell-region behavior;
- neutron-rich extrapolation;
- later time-split behavior if a reviewed post-baseline dataset is added.

This protocol is downstream of `EXP-0012` / `RESULT-0015`. It does not
reinterpret that baseline result as a holdout result.

## Scope

The protocol applies to future nuclear-mass correction experiments and sandbox
autonomous pilots under `campaign_profiles/nuclear-mass-surface.yaml`.

It is intended for:

- compact shell-aware corrections;
- pairing or asymmetry refinements;
- small interpretable residual terms;
- negative-control candidates that should fail under structured holdout.

It is not a license to claim a universal mass law.

## Required Baseline Freeze

Before any candidate is judged under this protocol, freeze these surfaces:

- pinned dataset file and checksum;
- measured versus extrapolated semantics;
- baseline model family and coefficient source;
- residual target definition in `MeV`;
- subset definitions;
- complexity penalty rule;
- model-selection rule;
- candidate execution budget.

For the current campaign state, the frozen baseline reference is:

- dataset surface: `NMD-0002`
- baseline benchmark: `EXP-0012`
- canonical result: `RESULT-0015`

Later broader datasets may supersede the slice, but they must do so explicitly.

## Holdout Families

Every serious candidate should be evaluated against more than one holdout
family. A single random split is not enough.

### 1. Random Nuclide Holdout

Purpose:

- check whether a candidate improves average behavior without relying on one
  hand-picked subset.

Default rule:

- stratify by light / medium / heavy mass-number bands;
- preserve measured-only semantics;
- use a fixed seed recorded in the experiment artifact;
- keep the random holdout smaller than the structured holdouts in interpretive
  weight.

Recommended weight:

- diagnostic only, not the decisive metric by itself.

### 2. Isotope-Chain Holdout

Purpose:

- test whether a candidate generalizes across unseen members of an isotope
  chain rather than memorizing local nuclide neighborhoods.

Default rule:

- hold out complete chains for selected `Z` values;
- rotate across light, medium, and heavy chains where data density allows;
- report chain-wise metrics, not just one pooled number.

Interpretation:

- a candidate that improves random holdout but collapses on chain holdout is
  not trustworthy enough for shell-aware interpretation.

### 3. Magic-Number Region Holdout

Purpose:

- test whether shell-aware residual claims survive when one or more shell
  neighborhoods are hidden during fit or selection.

Default rule:

- define magic-number neighborhoods around
  `N, Z in {2, 8, 20, 28, 50, 82, 126}`;
- use an explicit neighborhood width, recorded in the benchmark artifact;
- hold out at least one proton-magic and one neutron-magic neighborhood when
  the pinned dataset supports it.

Interpretation:

- if the candidate only helps when the same shell region appears in training,
  record that as interpolation, not shell-structure generalization.

### 4. Neutron-Rich Extrapolation Holdout

Purpose:

- test whether a correction remains stable when pushed toward more asymmetric
  nuclei.

Default rule:

- define a neutron-rich subset explicitly, for example by thresholds on
  `N - Z`, `N / Z`, or distance from the valley of stability;
- train on less asymmetric nuclei and evaluate on the richer edge subset;
- keep the rule simple and fully recorded in the experiment artifact.

Interpretation:

- this slice is about stability under extrapolation pressure, not about
  claiming astrophysical validity.

### 5. Time-Split Holdout

Purpose:

- provide the strongest future external-style check when a later curated
  post-baseline measurement batch exists.
- distinguish retrospective post-baseline validation from true prospective
  prediction.

Rule:

- do not use this holdout until a separate reviewed dataset is committed and
  documented clearly;
- do not silently merge later measurements into the training surface;
- report the older training source and newer revealed source separately.
- call AME2020-trained and post-AME2020-evaluated work a retrospective
  time-split benchmark, not strict blind prediction.

Current status:

- `TASK-0187` provides a reviewed source manifest at
  `data/nuclear_masses/post_ame2020_sources.yaml`;
- `TASK-0196` provides the reviewed row-level holdout dataset at
  `data/nuclear_masses/post_ame2020_holdout.yaml` and its checksum record at
  `data/nuclear_masses/post_ame2020_checksums.md`;
- not yet active for benchmark scoring until a later benchmark task consumes
  the reviewed row-level dataset;
- `TASK-0188` records the source-audit-only guard and remains `INCONCLUSIVE`
  for active metrics;
- `TASK-0197` is the real post-AME2020 row-level time-split benchmark task
  after that boundary is satisfied.

### 6. Prospective Prediction Registry

Purpose:

- support true before-measurement predictions only when they are registered
  before later measurements are known.

Rule:

- keep prospective predictions in a dedicated prediction registry;
- freeze target nuclides, model state, prediction values, uncertainty semantics,
  and reveal conditions before measurement comparison;
- do not treat registry entries as claims or accepted knowledge before later
  review.

Current status:

- planned through `TASK-0189`.

## Metrics

Every candidate evaluated under this protocol should report these metrics:

- `MAE` in `MeV`;
- `RMSE` in `MeV`;
- mean absolute uncertainty-normalized residual where uncertainty semantics are
  trusted;
- improvement over the frozen baseline;
- subset-specific error for each holdout family;
- complexity penalty;
- extrapolation stability note.

### Baseline-Relative Improvement

Improvement must be reported against the frozen baseline, not only as an
absolute candidate score.

Minimum expectation:

- overall holdout delta;
- magic-region delta;
- neutron-rich delta;
- chain-holdout delta where applicable.

### Complexity Penalty

Candidates should not win purely by adding decorative structure.

Minimum reporting:

- parameter count;
- whether the candidate introduces new discontinuities, singularities, or
  region-specific switches;
- one composite complexity note or penalty used consistently within the task.

## Decision Rules

Use this vocabulary:

- `VALID_IN_RANGE`
- `PARTIALLY_VALID`
- `OVERFITTED`
- `INCONCLUSIVE`
- `INVALID`

Interpretive rule:

- a candidate may be promising if it improves multiple holdout families with a
  modest complexity increase;
- a candidate should be labeled `OVERFITTED` if it improves one attractive
  slice but regresses badly on chain, shell, or neutron-rich holdouts;
- a candidate should be labeled `INCONCLUSIVE` when the dataset is too thin or
  uncertainty semantics are not trustworthy enough for the claimed distinction.
- a candidate should not trigger another autonomous batch until it is reviewed
  through the nuclear robustness gate in
  [Nuclear Mass Candidate Robustness Gate](./nuclear-mass-robustness-gate.md).

### Robustness Gate Boundary

The robustness gate is advisory for bounded sandbox follow-up and strict for
claim or canonical result promotion.

Before a second nuclear sandbox batch expands a candidate family, the batch
must report:

- primary holdout behavior;
- split-sensitivity behavior;
- leakage and cherry-pick review;
- complexity penalty;
- negative-control comparison;
- post-AME2020 status or limitation;
- conservative limitation wording.

Until a reviewed row-level post-AME2020 benchmark result exists,
post-AME2020 behavior must be listed as pending external-style validation
rather than silently omitted.

## Negative Controls

At least one negative-control family should be recognized explicitly during
autonomous or search-style work.

Good negative controls include:

- a shell bump tuned to one held-in region only;
- a chain-specific residual term that collapses outside one isotope family;
- a high-flex asymmetry correction that improves train error but destabilizes
  neutron-rich holdout.

Negative controls are useful outcomes, not wasted work.

## Pre-Reveal and Review Boundary

When the task uses a hidden or sealed holdout:

- follow [Blind Holdout Benchmark Protocol](./blind-holdout-benchmark-protocol.md);
- freeze candidate family, baseline, subset definitions, and pass rule before
  reveal;
- keep reveal artifacts separate from pre-reveal planning notes.

When the task uses a public structured holdout rather than a hidden one:

- still freeze subset definitions and candidate budget before judging results;
- do not allow post hoc slice edits after seeing a candidate failure.

## Output Contract for Future Nuclear Tasks

Any later holdout-based nuclear-mass PR should include:

- dataset identifier and checksum;
- baseline reference;
- holdout family definitions;
- metrics for every active slice;
- negative-control or rejection note;
- limitations;
- verdict;
- maintainer review request.

## What Not To Claim

- Do not say a candidate explains all nuclear masses.
- Do not say shell-region improvement alone is new nuclear theory.
- Do not say random holdout success is enough.
- Do not treat one slice-fitted correction as a canonical result before review.
- Do not start `TASK-0170` style autonomy without this protocol frozen in the
  relevant artifact set.
