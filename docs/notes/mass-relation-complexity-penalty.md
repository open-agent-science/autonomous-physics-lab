# Mass-Relation Complexity Penalty Design

Task: `TASK-0041`  
Status: draft planning note for maintainer review

## Purpose

This note defines how APL should penalize flexibility in future
particle-mass-relation benchmarks.

The goal is to stop broad search or clever algebra from winning only because
the candidate relation was allowed too much expressive freedom. A better fit
should count as stronger evidence only when it also survives a fair complexity
penalty.

This task is design only. It does not implement scoring code or create result
artifacts.

## Why APL Needs A Separate Penalty Policy

The current repository scoring logic is benchmark-specific and lightweight. For
the pendulum benchmark, complexity is already encoded as a small integer and
used as a deterministic tie-break inside `physics_lab/engines/scoring.py`.

The particle-mass track is different:

- the search space can be tiny in data size but huge in symbolic flexibility;
- a relation may look impressive after tuning constants or exponents;
- cross-family mixing can hide post hoc selection;
- prediction framing can be overstated when known values were already reused.

Because of that, particle-mass work needs a more explicit penalty breakdown
than the current single-number model complexity used in existing benchmarks.

## Design Goals

The penalty policy should:

- reward simpler candidate relations when fit quality is similar;
- make hidden flexibility visible in the result payload;
- discourage hand-tuned constants and exponents;
- penalize unjustified family mixing;
- penalize prediction stories that secretly reuse known targets;
- stay simple enough to explain in a benchmark report.

## Penalty Components

Future particle-mass scoring should compute a component-wise penalty ledger.

Minimum components:

### Parameter count penalty

Penalize every fitted free parameter.

Guideline:

- zero penalty for a fully fixed relation with no fitted parameters;
- increasing penalty for each independently fitted coefficient;
- additional penalty when a parameter is used only to rescue one weak case.

### Arbitrary constant penalty

Penalize constants that are inserted without physical grounding.

Examples:

- hand-picked decimal constants;
- unexplained offsets;
- hidden normalization factors chosen for one family only.

Constants that are fixed by the benchmark definition ahead of time should not
pay the same penalty as constants tuned from the observed masses.

### Tuned exponent penalty

Penalize flexible exponents more strongly than ordinary coefficients.

Rationale:

- a tuned exponent can absorb structure that would otherwise fail;
- irrational-looking or many-decimal exponents are especially high-risk for
  post hoc fit stories.

The penalty should distinguish between:

- simple predeclared exponents such as `1/2` when they are part of the tested
  relation family;
- fitted or triplet-specific exponents that were chosen after seeing results.

### Structural flexibility penalty

Penalize relation forms that gain power from symbolic flexibility rather than
from a small number of interpretable ingredients.

Examples:

- long nested expressions;
- piecewise definitions;
- branch-specific formulas;
- relations that switch structure across particle families;
- expressions that require many optional operations to stay competitive.

### Cross-family mixing penalty

Penalize relations that mix particles across families unless the benchmark
declared that scope in advance and gave a defensible reason for it.

The default Koide track should prefer family-local comparisons. Mixed-family
relations should therefore pay a material penalty unless they are explicitly
framed as exploratory.

### Post hoc prediction-framing penalty

Penalize a candidate when its reported “prediction” depends on information that
was already used to tune the relation or define the winning pattern.

This penalty is needed because predictive language is easy to overstate in
small-data mass relations. If the target value was effectively reused during
selection, the benchmark should either apply a large penalty or mark the
prediction framing ineligible.

## Disqualifying Cases

Some cases should not merely score worse. They should be treated as
ineligible for strong ranking claims.

Examples:

- a candidate requires incompatible mass definitions in one formula;
- a candidate uses hidden per-triplet retuning;
- a candidate is presented as a holdout prediction after the holdout was used
  for search or model selection;
- a candidate depends on a search scope that was not disclosed.

In those cases, the benchmark should prefer an ineligible or exploratory flag
over pretending the issue is just a small numeric penalty.

## Suggested Scoring Shape

Future implementation should expose both fit quality and complexity details.

One acceptable shape is:

`composite_score = fit_score + lambda_complexity * normalized_complexity_penalty`

Where:

- `fit_score` comes from the benchmark-specific residual or holdout metric;
- `normalized_complexity_penalty` is the sum of weighted penalty components;
- `lambda_complexity` is fixed per benchmark family before evaluating
  candidates.

The exact weights can be tuned later, but they must be benchmark-level choices,
not candidate-specific rescue knobs.

## Reporting Requirements

Any future ranking output should report:

- the total complexity penalty;
- the per-component penalty breakdown;
- whether any disqualifying flag was triggered;
- whether the candidate stayed within one family or mixed families;
- whether the candidate used fitted coefficients, tuned constants, or tuned
  exponents.

APL should not hide these details behind one opaque leaderboard number.

## Default Relative Severity

The first implementation should treat these as rough severity bands:

- low: one or two simple fitted coefficients inside a predeclared relation
  family;
- medium: extra coefficients plus modest structural flexibility;
- high: tuned exponents, unexplained constants, or family mixing;
- very high: post hoc prediction framing or search-dependent retuning.

These bands are intentionally qualitative at this stage. The numeric weights
should stay reviewable and adjustable once benchmark code exists.

## Mapping To A Future Engine Module

This policy should later map cleanly into a dedicated module such as
`physics_lab/engines/mass_relation_scoring.py`.

Suggested outline:

```python
@dataclass(frozen=True)
class MassRelationPenaltyBreakdown:
    parameter_count: float
    arbitrary_constants: float
    tuned_exponents: float
    structural_flexibility: float
    cross_family_mixing: float
    post_hoc_prediction: float
    total: float
    disqualifying_flags: tuple[str, ...]


def score_mass_relation_candidate(
    candidate: MassRelationCandidate,
    fit_summary: MassRelationFitSummary,
    policy: MassRelationPenaltyPolicy,
) -> MassRelationScore:
    ...
```

The important part is not the exact class names. The important part is that
future code should return both:

- benchmark-fit metrics;
- interpretable penalty breakdown data.

That keeps review, reporting, and later schema evolution aligned.

## Interaction With Other Tasks

This design should constrain:

- `TASK-0039` triplet-search design;
- `TASK-0037` charged-lepton reproduction when multiple relation families are
  later compared;
- `TASK-0038` tau holdout work when prediction framing is evaluated;
- any future `TASK-0040` falsifier or search implementation.

Search-oriented schema support is also still needed before broader
particle-mass scoring can be expressed honestly in canonical result artifacts.
