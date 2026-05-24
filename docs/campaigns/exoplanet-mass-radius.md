# Exoplanet Mass-Radius Benchmark

## Goal

Prepare a fourth APL scientific campaign around the empirical relation between
exoplanet mass and radius, using curated public catalog snapshots, conservative
baselines, residual maps, and holdout discipline.

The target is not planet detection, habitability scoring, or a new universal
planet law. The target is a disciplined benchmark surface where standard
mass-radius forecasts and compact agent-proposed variants can be compared
against source-pinned catalog rows with uncertainty, provenance, and selection
effects kept visible.

## Current Status

Active benchmark surface with a pinned source snapshot, loader dry-run, first
baseline comparison, and one bounded regime scout. The campaign has useful
reviewable residual evidence, but no claim, prediction registry entry, RESULT-*,
or public article artifact yet.

This page records the strategic plan and source-ingestion posture. `TASK-0353`
produced a pinned NASA Exoplanet Archive PSCompPars snapshot with raw CSV,
normalized YAML, checksums, row-class labels, and inclusion/exclusion reasons.
`TASK-0354` added a loader dry-run for validating the ingestion path. `TASK-0361`
ran the first frozen Chen-Kipping-style baseline comparison on the committed
snapshot. `TASK-0370` ran a bounded regime residual scout over known transition
regions.

Current scientific reading:

- `TASK-0361` is **INCONCLUSIVE**: the frozen CK17-style baseline beats a
  per-class median null on the true-mass / transit-radius axis, but loses badly
  on the minimum-mass / transit-radius axis. This is a useful first benchmark
  and a warning that mass provenance must stay visible.
- `TASK-0370` is **INCONCLUSIVE**: three executed regime slices show visible
  residual structure, especially hot-Jupiter and Jovian-radius subsets, but the
  strongest matched controls explain enough of the improvement that no regime
  correction is promoted.
- `TASK-0362` and `TASK-0369` are the next useful science tasks: package the
  residual/failure map and audit the true-mass slice before opening a narrower
  correction-hypothesis task.

`TASK-0337` created the first source and schema surface before any agent runs
metrics:

- a value-free data-area README and source-manifest template;
- a row schema for mass, radius, uncertainties, provenance, and method flags;
- a holdout protocol for planet class, detection method, host-star context,
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

The first useful result should be a benchmark, not a validated claim:

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

Allowed current work:

- source manifest and license/provenance review;
- schema and loader planning or maintenance;
- deterministic snapshot policy;
- holdout protocol;
- residual failure-map packaging from the frozen baseline;
- true-mass residual slice audit;
- bounded regime follow-up only when matched controls stay explicit.

Not allowed yet:

- live archive fetching inside agent tasks without a pinned snapshot policy;
- claims that APL discovered a planet-composition law;
- habitability, life, biosignature, or planet-prioritization claims;
- public article work before a reviewed residual map exists;
- mixing true mass, minimum mass, and model-derived mass without explicit
  row-class flags.

Future catalog, source-artifact, row-curation, and residual-map tasks should
follow the [Fresh-Data Intake Protocol](../fresh-data-intake-protocol.md) so
catalog snapshots, extraction gates, row classes, baseline readiness, and
benchmark readiness stay separate.

## Recommended Next Shape

The campaign should mature in this order:

1. `TASK-0337` source and schema scaffold.
2. `TASK-0353` pinned catalog snapshot with checksum, citation, and retrieval
   date (DONE; no metrics).
3. Loader validation with row-class flags and uncertainty semantics
   (`TASK-0354`, DONE).
4. Conservative Chen-Kipping-style baseline reproduction (`TASK-0361`, DONE;
   inconclusive but useful).
5. Bounded regime residual scout (`TASK-0370`, DONE; no correction promoted).
6. Residual and failure-map report (`TASK-0362`, READY).
7. True-mass residual slice audit (`TASK-0369`, READY).
8. Bounded autonomous hypothesis pilot only after the residual map and
   true-mass audit identify a narrow, control-surviving target.

This campaign is now the fastest APL path to a visible, scientist-readable
benchmark artifact. It is not yet a discovery surface.
