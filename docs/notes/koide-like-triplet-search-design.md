# Koide-Like Triplet Search Design

Task: `TASK-0039`  
Status: draft planning note for maintainer review

## Purpose

This note defines how APL should design a Koide-like triplet search before any
broader particle-mass scan is implemented.

The goal is not to search for a pretty equation at any cost. The goal is to
make triplet search falsification-first, source-aware, uncertainty-aware, and
resistant to numerology.

This task is planning only. It does not implement search code, produce result
artifacts, or strengthen any claim state.

## Search Object

The first search family should stay narrow:

- use unordered triplets of three distinct particles;
- evaluate fixed, predeclared relation forms only;
- record all mass-definition metadata before computing any score.

For the canonical Koide quantity, the search target is:

`Q = (m1 + m2 + m3) / (sqrt(m1) + sqrt(m2) + sqrt(m3))^2`

with comparison against the reference value `2/3`.

Future relation families may be added later, but each family must be declared
before the scan and scored against the same baseline and complexity rules.

## Candidate Families

### Allowed by default

- charged leptons, using pole masses from one explicit source edition;
- up-type quarks, only when all masses use one explicit scheme and scale;
- down-type quarks, only when all masses use one explicit scheme and scale.

### Conditionally allowed later

- neutrino scenario triplets, only when the scenario assumptions are explicit
  and the benchmark is clearly labeled assumption-sensitive;
- repeated scans across several approved quark scheme or scale snapshots, but
  only as separate benchmark slices rather than one silently pooled search.

### Forbidden by default

- mixed triplets spanning different particle families;
- charged-lepton and neutrino mixtures;
- lepton-quark mixtures;
- hadrons or other composite particles mixed into the core benchmark;
- triplets built from masses with incompatible `mass_type`, `scheme`, or
  `scale`;
- triplets that rely on missing uncertainty or ambiguous source provenance;
- hand-curated post hoc subsets that are chosen only after seeing scores.

## Family-Specific Cautions

### Charged leptons

Charged leptons are the cleanest first comparison target because the pole-mass
definitions are stable and the uncertainties are small enough for a useful
uncertainty-aware benchmark.

### Quarks

Quarks are allowed only with explicit scheme and scale discipline. A strong
score under one running-mass convention does not automatically transfer to
another convention.

### Neutrinos

Neutrino triplets should remain off by default for the first implementation.
Absolute masses are not directly settled, and scenario assumptions can dominate
the appearance of a pattern.

## Eligibility Rules For Any Search Run

Before search starts, the benchmark config must freeze:

- the eligible particle pool;
- the source edition or dataset snapshot;
- allowed triplet families;
- the relation forms to be evaluated;
- the baseline set;
- the uncertainty model;
- the ranking and reporting rules.

Each evaluated triplet must:

- contain three distinct particles;
- be treated as an unordered set, not three different permutations;
- use one consistent unit system;
- use one compatible mass-definition regime;
- carry explicit source metadata for every mass input.

## Baseline Requirements

No Koide-like triplet search should report a top hit without baseline context.

Minimum baseline set:

- a random baseline drawn from the same eligible particle pool under the same
  family and metadata constraints;
- a weakly structured baseline based on simple pairwise mass-ratio summaries;
- a weakly structured baseline based on low-flexibility power-law or
  log-linearity heuristics;
- a ranking comparison that applies the same uncertainty handling and
  complexity accounting to every candidate.

The random baseline should estimate how often a triplet from the same eligible
pool lands comparably close to the target by chance.

The simpler structured baselines should answer a different question: whether a
Koide-like relation is materially better than cheaper descriptive summaries of
mass hierarchy.

## Uncertainty Propagation

Every search-style result in this track must propagate input uncertainty.

Default design:

- use source-reported central values and uncertainties;
- sample the input masses with an explicit Monte Carlo procedure when the
  source supports it;
- keep all sampled masses physically valid, such as positive-valued masses;
- report a distribution for the target statistic, not just one point estimate;
- report whether uncertainty is negligible, comparable to the residual, or
  large enough to blur ranking differences.

When a source does not expose a full correlation model, the benchmark should
state that independence or another approximation was assumed.

## Overfit And Cherry-Picking Controls

Triplet search is especially vulnerable to multiple-comparison bias.

Future implementation should therefore require:

- a preregistered candidate universe before scores are inspected;
- a count of all tested triplets;
- a count of all tested relation forms;
- reporting of near-misses, not only the best triplet;
- deduplication of equivalent triplets under permutation;
- explicit disclosure of any filtering rules applied before final ranking;
- empirical significance or rank context relative to the random baseline.

APL should not present one successful triplet as meaningful evidence if the
broader search space was large and full of similar near-hits.

## Reporting Rules

Any future search result should report at least:

- eligible dataset scope and source edition;
- allowed families and forbidden families for that run;
- the full count of tested triplets;
- the evaluated relation forms and baselines;
- uncertainty-aware score summaries for the top-ranked triplets;
- the null or random-baseline reference distribution;
- a plain-language limitation summary.

Safe framing should describe the output as benchmark-scoped evidence, not as an
explanatory breakthrough.

## Implementation Gates

The first broad particle-mass search should remain gated until all of the
following are true:

1. `TASK-0037` charged-lepton reproduction is complete.
2. `TASK-0038` tau holdout design is complete.
3. `TASK-0041` complexity-penalty design is complete.
4. Search-oriented experiment and result schema support is defined clearly
   enough to avoid fake fit-style metadata.

Until those gates are met, `TASK-0040` should remain a controlled future
implementation target rather than an active benchmark rollout.
