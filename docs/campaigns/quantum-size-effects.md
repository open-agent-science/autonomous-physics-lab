# Quantum Size Effects

## Goal

Prepare a future APL campaign around size-dependent optical and electronic
properties of semiconductor quantum dots, using theory, computation, dataset
comparison, and visualization only.

The target is not a new quantum-dot design law and not a material-discovery
framing. The target is a disciplined benchmark surface where compact,
physically constrained size-scaling models can be compared against curated,
source-pinned measurement data with explicit residuals, breakdown maps, and
holdouts.

## Orientation Note for New Contributors

This campaign is currently **scaffold-complete and foundation-ready**.

The first scaffold, dataset/schema surface, and holdout protocol have landed
under `TASK-0222`, `TASK-0223`, and `TASK-0224`. The next safe work is source
curation and the first baseline residual benchmark:

- `TASK-0275` — source-manifest seed after schema closeout (READY);
- `TASK-0225` — baseline residual benchmark (READY);
- `TASK-0226` — first autonomous sandbox-only hypothesis pilot (BLOCKED).

Until those land in order, safe contributions are:

- planning, scope, and limitation notes;
- queued tasks already on the canonical track above;
- source-manifest curation under `TASK-0275`;
- baseline implementation under `TASK-0225`;
- visualization sketches that do not require baseline residual artifacts.

### What not to implement yet

- do not fetch live datasets, scrape publication tables, or store raw vendor
  spec sheets in the repository without source-manifest review;
- do not run visualization or autonomous-pilot work before the baseline
  residual artifact exists;
- do not run autonomous formula search across quantum-dot size data before
  `TASK-0225` lands a frozen baseline;
- do not start a public-facing campaign result, claim, or article task before
  the first canonical baseline exists.

## Why It Matters

This campaign is a candidate next real-data surface for APL because it
combines:

- size-dependent optical and electronic measurements with explicit
  experimental uncertainties;
- compact, interpretable baseline models such as Brus-style effective-mass
  approximations and related size-scaling functions;
- known systematic residual regions across material families, size regimes,
  and absorption-versus-emission semantics;
- holdout-friendly structure across materials, size ranges, sources, and
  composition families;
- easier-to-visualize residuals than nuclear binding-energy surfaces while
  still requiring discipline about provenance.

A clean failure map across material families is already useful scientific
memory, even before any compact correction term survives a holdout.

## Current Results

None.

The only current evidence is the campaign scaffold defined by merged
`TASK-0222`:

- this campaign page;
- `campaign_profiles/quantum-size-effects.yaml` — the campaign profile and
  guardrails;
- `docs/notes/quantum-size-effects-campaign-plan.md` — the sequenced plan;
- `tasks/microtasks/quantum-size-effects.yaml` — a small scoped microtask
  queue for planning-only contributions.

Historical context:

- `tasks/proposals/20260507-roman-quantum-dots-size-effects-campaign.yaml` is
  the accepted proposal that promoted this direction into the canonical
  `TASK-0222`..`TASK-0226` queue.

## Open Questions

- Which property kind should anchor the first benchmark — absorption peak,
  emission peak, or bandgap — and how should the other two be treated when the
  dataset task lands?
- Which baseline family should be the conservative first comparison — a
  Brus-style effective-mass approximation, a generalized size-scaling
  function, or both with explicit per-material applicability flags?
- Which holdout split should be required versus optional — material-level,
  size-range, publication-source, or composition-family?
- How should absorption-versus-emission and bandgap semantics be separated in
  the dataset so they are not mistakenly mixed under one residual metric?
- How should size-related fields be canonicalized — diameter versus radius,
  in nanometers, with what tolerance for reported uncertainty?

## Recommended Tasks

- `TASK-0223` and `TASK-0224` have delivered the dataset/schema and holdout
  foundation;
- run `TASK-0275` if a small source-manifest seed is needed before the
  baseline benchmark;
- run `TASK-0225` for the first baseline residual benchmark;
- after `TASK-0225`, use `TASK-0276` for conservative residual visuals and
  `TASK-0277` to review readiness before the autonomous pilot;
- run `TASK-0226` only after a maintainer-approved baseline exists.

Planning-only microtasks may be picked from
`tasks/microtasks/quantum-size-effects.yaml`. They must not produce canonical
results, claims, datasets, or experiments.

## Recommended Contributor Types

- condensed-matter contributors who like dataset curation and source-manifest
  work;
- benchmark designers comfortable with baselines, breakdown maps, and subset
  metrics;
- visualization contributors who can sketch residual maps without claiming
  unpublished data;
- reviewers focused on overclaim resistance, provenance discipline, and
  scope separation between synthesis and computation.

## What Not To Claim

- Do not say APL has discovered a quantum-dot design law.
- Do not say baseline residuals imply a new condensed-matter theory.
- Do not say the campaign supports material selection, device fabrication, or
  biomedical applications.
- Do not provide synthesis recipes, chemical handling guidance, or device
  fabrication instructions of any kind.
- Do not blur absorption peak, emission peak, and bandgap values under one
  residual metric.
- Do not promote sandbox fit improvements as canonical benchmark results.
- Do not open public-facing scientific claims before the first canonical
  baseline and residual benchmark exist.

## Visualization Ideas

- size-versus-bandgap scatter overlays per material family once the dataset
  task lands;
- per-material residual heatmaps over diameter or radius bins;
- absorption-versus-emission diagnostic panels showing why the two should not
  be merged;
- holdout-versus-train residual comparison strips once the holdout protocol
  exists;
- campaign flow diagram from pinned dataset to baseline to holdout to
  sandbox pilot to maintainer review.
