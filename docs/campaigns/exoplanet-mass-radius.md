# Exoplanet Mass-Radius Benchmark

## Goal

Prepare a fourth APL scientific campaign around the empirical relation between
exoplanet mass and radius, using curated public catalog snapshots, conservative
baselines, residual maps, and holdout discipline.

The target is not planet discovery, habitability scoring, or a new universal
planet law. The target is a disciplined benchmark surface where standard
mass-radius forecasts and compact agent-proposed variants can be compared
against source-pinned catalog rows with uncertainty, provenance, and selection
effects kept visible.

## Current Status

Planned fourth campaign.

This page records the strategic plan only. No exoplanet dataset, source
snapshot, schema, benchmark, residual map, prediction registry entry, result,
claim, or public article artifact exists yet.

`TASK-0337` is the first preparation task. It should create the source and
schema surface before any agent runs metrics:

- a value-free data-area README and source-manifest template;
- a row schema for mass, radius, uncertainties, provenance, and method flags;
- a holdout protocol for planet class, discovery method, host-star context,
  mass/radius ranges, and source-date splits;
- a source-surface review that decides what a pinned NASA Exoplanet Archive
  snapshot may contain and what must stay excluded.

## Why It Matters

Exoplanet mass-radius data are a strong APL candidate because they combine:

- a recognizable scientific object and highly visual scatter plots;
- thousands of catalogued planets in public archives;
- known baseline models such as Chen-Kipping-style probabilistic
  mass-radius forecasting;
- real residual structure around rocky planets, sub-Neptunes, gas giants, and
  inflated hot Jupiters;
- natural holdouts across planet class, detection method, host-star properties,
  equilibrium temperature, source date, and measurement quality;
- meaningful negative results when a simple relation fails to transfer.

This is useful even if no agent finds a better model. A clean failure map that
shows where standard mass-radius forecasts break is a real scientific artifact
and an accessible public story.

## Expected Results

The first useful result should be a benchmark, not a discovery claim:

- reproduce a conservative mass-radius baseline on a frozen catalog snapshot;
- report residuals and uncertainty-aware errors by planet class and method;
- identify where baseline behavior is brittle, such as the super-Earth to
  sub-Neptune transition, gas-giant inflation regimes, or sparse high-mass
  regions;
- preserve measurement-quality and `M sin i` limitations instead of hiding
  them inside a single score;
- publish negative controls and failed simple formulas as first-class memory;
- later, freeze prediction records for planets whose mass or radius is
  uncertain or pending update, but only after a no-peek source policy exists.

In plain language: the campaign can tell us whether APL agents can map where
standard exoplanet mass-radius forecasts work, where they fail, and whether
bounded variants survive honest holdouts.

## Guardrails

Allowed early work:

- source manifest and license/provenance review;
- schema and loader planning;
- deterministic snapshot policy;
- holdout protocol;
- baseline reproduction plan;
- residual visualization plan without metrics.

Not allowed yet:

- live archive fetching inside agent tasks without a pinned snapshot policy;
- benchmark metrics before the schema and holdout protocol exist;
- claims that APL discovered a planet-composition law;
- habitability, life, biosignature, or planet-prioritization claims;
- public article work before a reviewed benchmark artifact exists;
- mixing true mass, minimum mass, and model-derived mass without explicit
  row-class flags.

## Recommended Next Shape

The campaign should mature in this order:

1. `TASK-0337` source and schema scaffold.
2. Pinned catalog snapshot task with checksum, citation, and retrieval date.
3. Loader validation with row-class flags and uncertainty semantics.
4. Conservative Chen-Kipping-style baseline reproduction.
5. Residual and failure-map report.
6. Bounded autonomous hypothesis pilot only after the benchmark is frozen.

Until step 4 lands, this campaign is a preparation lane, not an active result
surface.
