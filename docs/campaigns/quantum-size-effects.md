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

This campaign is currently **scaffold-complete with source-manifest evidence,
but not yet row-level benchmark-ready**.

The first scaffold, dataset/schema surface, and holdout protocol have landed
under `TASK-0222`, `TASK-0223`, and `TASK-0224`. `TASK-0275` added the first
reviewed source-manifest seed. `TASK-0281` and `TASK-0282` added two
calibration-derived row-level seeds (Yu 2003 cadmium chalcogenides;
Moreels 2009 PbS). `TASK-0283` then ran the row-level readiness gate and
kept `TASK-0225` BLOCKED because every committed row is calibration-derived
rather than directly measured.

Current task posture:

- `TASK-0281` — Yu 2003 multi-material absorption row-level seed (DONE);
- `TASK-0282` — Moreels 2009 PbS absorption row-level extension (DONE);
- `TASK-0283` — row-level readiness gate before baseline (DONE; see
  `docs/reviews/quantum-size-row-level-data-readiness-for-baseline.md`);
- `TASK-0225` — baseline residual benchmark (BLOCKED; needs either a
  direct-measurement row-level seed or a maintainer waiver to score a
  calibration-curve consistency benchmark instead of a measurement-versus-
  model benchmark);
- `TASK-0291` — direct-measurement absorption seed (READY);
- `TASK-0292` — direct-measurement band-edge seed (READY);
- `TASK-0293` — re-run readiness gate after a direct seed (BLOCKED until
  `TASK-0291` or `TASK-0292` lands, or maintainer waiver is explicit);
- `TASK-0226` — first autonomous sandbox-only hypothesis pilot (BLOCKED).

Safe next contributions are:

- planning, scope, and limitation notes;
- direct-measurement row-level dataset curation that can re-run the
  `TASK-0283` readiness gate;
- a maintainer-approved waiver package if the first benchmark is intentionally
  scoped as calibration-curve consistency rather than measurement-versus-model;
- visualization sketches that do not require baseline residual artifacts.

### What not to implement yet

- do not fetch live datasets, scrape publication tables, or store raw vendor
  spec sheets in the repository without source-manifest review;
- do not treat `data/quantum_dots/source_manifest.yaml` as benchmark data;
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

No benchmark result yet.

Current evidence is infrastructure and source curation only:

- `TASK-0222` created this campaign page;
- `campaign_profiles/quantum-size-effects.yaml` — the campaign profile and
  guardrails;
- `docs/notes/quantum-size-effects-campaign-plan.md` — the sequenced plan;
- `tasks/microtasks/quantum-size-effects.yaml` — a small scoped microtask
  queue for planning-only contributions;
- `TASK-0223` defined the dataset/source-manifest schema surface;
- `TASK-0224` defined the holdout protocol;
- `TASK-0275` added a reviewed source-manifest seed, but no row-level
  measurement dataset.
- `TASK-0281` and `TASK-0282` added calibration-derived absorption row-level
  seeds for Yu 2003 cadmium chalcogenides and Moreels 2009 PbS.
- `TASK-0283` reviewed those seeds and kept the benchmark blocked because they
  are calibration-derived rather than direct measurement rows.

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
- `TASK-0275` has delivered the first source-manifest seed;
- `TASK-0281` and `TASK-0282` delivered calibration-derived row-level
  absorption seeds;
- `TASK-0283` keeps `TASK-0225` blocked because the committed rows are not
  direct measurement rows;
- `TASK-0291` and `TASK-0292` are the next parallel data-curation lanes for
  direct-measurement absorption and band-edge seeds;
- `TASK-0293` should re-run the readiness gate after either direct seed lands;
- next, add at least one direct-measurement row-level `qd-*.yaml` seed and
  re-run the readiness gate, or request a maintainer waiver for a
  calibration-curve consistency benchmark;
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
