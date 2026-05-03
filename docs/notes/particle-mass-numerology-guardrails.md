# Particle Mass Numerology Guardrails

Task: `TASK-0042`  
Status: draft guardrail note for maintainer review

## Purpose

Particle-mass relations are unusually vulnerable to numerology, retrospective
storytelling, and scope drift.

This note defines the minimum guardrails APL should enforce before treating a
particle-mass result as meaningful benchmark evidence.

The goal is not to suppress interesting patterns. The goal is to make future
particle-mass work falsification-first, source-aware, and reviewable.

## Core Rule

No discovery claim follows from fit quality alone.

A numerically impressive relation must still survive:

- explicit source review;
- uncertainty-aware evaluation;
- baseline comparison;
- complexity accounting;
- holdout or out-of-sample discipline where applicable;
- anti-cherry-picking review.

Without those checks, a good-looking fit is only a candidate pattern.

## What APL Must Not Claim

Future particle-mass tasks must not treat a good fit as evidence that a
relation:

- explains the origin of particle masses;
- establishes new physics;
- generalizes across all particle families;
- survives scheme or scale changes without testing;
- remains meaningful after a broad search unless the search accounting is made
  explicit.

## Data Guardrails

Every particle-mass task must record explicit source metadata for each input
mass.

Minimum requirements:

- use explicit, versioned PDG-backed sources or an equally explicit
  maintainer-approved source;
- record mass units and uncertainty units explicitly;
- record `mass_type`, such as `pole` or `running`;
- record `scheme` and `scale` whenever the mass definition requires them;
- do not silently mix incompatible mass definitions in one benchmark.

Special caution:

- charged leptons are comparatively clean because pole masses are well defined;
- quark masses are high-risk because scheme and scale changes can materially
  change the apparent strength of a relation;
- neutrino tasks must not pretend that unknown absolute masses are settled
  inputs.

## Anti-Cherry-Picking Rules

APL must forbid silent cherry-picking.

That means:

- no hand-selected particle triplet may be presented as meaningful without
  stating whether other eligible triplets were considered;
- no post hoc choice of constants, exponents, or family boundaries may be
  hidden behind a clean final formula;
- no benchmark may treat a single success case as representative if the search
  space was broader and mostly unsuccessful.

If a task explores many candidates, it must record:

- the candidate-generation rules;
- the allowed and forbidden combinations;
- the number of tested candidates;
- how many near-misses or false positives appeared;
- what was held fixed before looking at the results.

## Baseline Requirements

Every search-style or score-style particle-mass task must compare against
baselines.

Minimum baseline rules:

- require a random baseline for triplet-search or formula-search tasks;
- require at least one weakly structured baseline, such as simple ratios or
  low-flexibility power-law forms;
- do not report a pattern as strong merely because it beats a null of
  "no formula at all" when many cheap alternatives were not tested.

The relevant question is not "does the fit look small?" The relevant question
is "does this survive comparison against simpler or random alternatives?"

## Holdout Requirements

Prediction framing must use real holdout discipline.

Minimum rules:

- if a task claims predictive value, at least one quantity must be treated as a
  holdout rather than fitted jointly with the others;
- the holdout rule must be stated before reporting the comparison;
- a prediction reconstructed from already-used information must not be marketed
  as an independent forecast.

For the Koide track, the historical tau-mass benchmark is acceptable because it
can be framed explicitly as a holdout-style reproduction task rather than a new
prediction claim.

## Uncertainty Requirements

Future particle-mass tasks must propagate uncertainty when the inputs support
it.

Minimum rules:

- use the reported uncertainty model from the source when available;
- do not compare against exact-looking constants while ignoring measurement
  uncertainty;
- do not present tiny residuals without clarifying whether they are materially
  larger or smaller than propagated input uncertainty;
- note when uncertainty treatment is approximate, missing, or assumption-heavy.

## Complexity-Penalty Requirements

A particle-mass relation should pay for flexibility.

Future scoring or ranking must penalize at least:

- parameter count;
- arbitrary constants;
- tuned exponents;
- formula-length or structural flexibility;
- cross-family mixing without physical justification;
- post hoc reuse of known values inside a prediction narrative.

If a more complicated relation beats a simpler one only marginally, APL should
prefer the simpler interpretation until stronger evidence exists.

## Review Checklist For Future Particle-Mass Tasks

Before a maintainer treats a particle-mass result as meaningful evidence,
confirm:

1. The dataset source and edition are explicit.
2. `mass_type`, `scheme`, and `scale` are recorded where relevant.
3. The task states whether it is reproduction, holdout, search, or exploratory work.
4. The candidate space and search accounting are visible.
5. A random baseline is included when search is involved.
6. A simpler structured baseline is included when ranking formulas.
7. Uncertainty propagation is present or its absence is explained.
8. Any predictive framing uses a real holdout, not a refit disguised as prediction.
9. The wording avoids "discovery", "new physics", and broad explanatory claims.
10. The result is described as benchmark evidence, not as autonomous scientific conclusion.

## Allowed Safe Wording

Prefer wording such as:

- `reproduction result`
- `holdout benchmark`
- `candidate relation`
- `benchmark-scoped evidence`
- `numerically interesting but not explanatory`
- `not evidence of new physics by itself`

Avoid wording such as:

- `solved particle masses`
- `discovered the mass formula`
- `proof of hidden structure`
- `new physics from fit quality alone`

## Interaction With Other Tasks

This note should constrain:

- `TASK-0037` charged-lepton Koide reproduction;
- `TASK-0038` tau holdout benchmark;
- `TASK-0039` triplet-search design;
- `TASK-0041` complexity-penalty design;
- any future `TASK-0040` falsifier implementation work.

If a future task cannot satisfy these guardrails, it should remain clearly
labeled as exploratory and should not strengthen any claim state automatically.
