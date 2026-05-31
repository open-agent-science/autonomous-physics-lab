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
baseline comparison, residual/failure-map work, bounded residual audits, and a
new null-baseline control panel. The campaign has useful reviewable sandbox
evidence, but no claim, prediction registry entry, RESULT-*, or public article
artifact yet.

## Public Monitoring Snapshot

**Current question:** after stronger null-baseline controls, is any
Chen-Kipping-style residual slice still worth a host-context preflight on the
pinned NASA Exoplanet Archive PSCompPars snapshot?

**Shareable result:** the compact-radius slice (`R < 1.5 R_earth`) was the
strongest earlier matched-control diagnostic, but `TASK-0483` found that a
simple nearest-radius null baseline matches or beats the frozen CK17-style
baseline across the compact, sub-Neptune, Jovian-radius, and hot-Jupiter
true-mass slices. That is now the main public-safe result: the apparent
residual stress is control-sensitive.

**Not a claim:** this does not infer composition, habitability, atmospheric
physics, target priority, or a new mass-radius law. It is a benchmark
diagnostic and failure-map surface.

**Active next work:** `TASK-0481` is the important remaining benchmark-
hardening task: preflight whether host-star context can support a meaningful
follow-up after the null-baseline audit. `TASK-0480` landed as underpowered at
mass-quartile resolution, `TASK-0482` and `TASK-0484` packaged the
second-snapshot target freeze and external-reviewer capsule, and `TASK-0483`
landed as an `INCONCLUSIVE` null-baseline control panel. All work stays
no-live-fetch and benchmark-only.

**Current shareable artifact:** the
[compact-radius benchmark evidence card](../results/exoplanet-compact-radius-benchmark-card.md)
still packages the earlier scorecard-approved wording, but readers should pair
it with the [null-baseline family audit](../reviews/exoplanet-null-baseline-family-audit.md)
before interpreting the compact-radius diagnostic.

This page records the strategic plan and source-ingestion posture. `TASK-0353`
produced a pinned NASA Exoplanet Archive PSCompPars snapshot with raw CSV,
normalized YAML, checksums, row-class labels, and inclusion/exclusion reasons.
`TASK-0354` added a loader dry-run for validating the ingestion path. `TASK-0361`
ran the first frozen Chen-Kipping-style baseline comparison on the committed
snapshot. `TASK-0370` ran a bounded regime residual scout over known transition
regions. `TASK-0390` tested a compact/sub-Neptune residual hypothesis pilot,
`TASK-0391` ran a neptunian matched-control audit, and `TASK-0392` audited
host/uncertainty selection effects.

Current scientific reading:

- `TASK-0361` is **INCONCLUSIVE**: the frozen CK17-style baseline beats a
  per-class median null on the true-mass / transit-radius axis, but loses badly
  on the minimum-mass / transit-radius axis. This is a useful first benchmark
  and a warning that mass provenance must stay visible.
- `TASK-0370` is **INCONCLUSIVE**: three executed regime slices show visible
  residual structure, especially hot-Jupiter and Jovian-radius subsets, but the
  strongest matched controls explain enough of the improvement that no regime
  correction is promoted.
- `TASK-0390` is **SANDBOX_PASS** only for a bounded compact/sub-Neptune
  follow-up surface. It is not yet control-surviving evidence because the
  matched-control audit is still a separate task.
- `TASK-0391` is **INCONCLUSIVE**: neptunian matched controls do not currently
  justify a promoted correction.
- `TASK-0392` is **INCONCLUSIVE**: host and uncertainty slices expose selection
  effects, but they are diagnostics rather than causal planet-physics claims.
- `TASK-0427`, `TASK-0404`, `TASK-0393`, `TASK-0445`, and `TASK-0447` are the
  current exoplanet visibility spine: matched-control audit, benchmark-summary
  scorecard, second-snapshot no-live-fetch protocol, independent replay, and
  evidence-card packaging.
- `TASK-0480` is **INCONCLUSIVE**: the compact-radius slice has 92 eligible
  rows, so mass-quartile bins fall below the 30-row interpretation floor. A
  coarse mass-half diagnostic points toward upper-mass compact planets, but
  this is not a verdict driver or planet-physics conclusion.
- `TASK-0482` is a **VALID_IN_RANGE** target-freeze protocol for a future
  second snapshot. It freezes target names, row-field boundaries, checksums,
  true-mass/minimum-mass separation, and reveal conditions without fetching
  live data.
- `TASK-0484` packages the external-reviewer replication capsule. It preserves
  the current benchmark values and `BENCHMARK_SUMMARY_ONLY` scorecard, but
  does not strengthen the result into a claim.
- `TASK-0483` is **INCONCLUSIVE**: deterministic nearest-radius null baselines
  match or beat the frozen CK17-style baseline in the compact, sub-Neptune,
  Jovian-radius, and hot-Jupiter true-mass slices. This downgrades the
  compact-radius diagnostic from "strongest survivor" to "control-sensitive
  benchmark target."
- `TASK-0481` is now the most important executable task for this campaign. It
  should decide whether host-context fields can support a meaningful follow-up
  before any more residual interpretation.
- `TASK-0470`-era visibility work is now campaign memory. The current
  benchmark-hardening wave does not promote claims, knowledge, predictions, or
  canonical results.

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
- bounded regime follow-up only when matched controls stay explicit;
- result-promotion scorecards that decide benchmark/public wording without
  promoting a composition, habitability, or discovery claim.

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
6. Residual/failure-map and true-mass/selection-effect audits through
   `TASK-0392` (sandbox evidence; no claim promotion).
7. Compact/sub-Neptune matched-control audit (`TASK-0427`, DONE) before
   treating the `TASK-0390` pilot as a surviving hypothesis lane.
8. Result-promotion scorecard (`TASK-0404`, DONE) to decide whether the
   failure-map package is scientist-facing, benchmark-only, or not ready.
9. Second-snapshot no-live-fetch protocol (`TASK-0393`, DONE) before any
   cross-snapshot or prediction-readiness story.
10. Independent compact-radius replay (`TASK-0445`, DONE) and evidence card
    (`TASK-0447`, DONE) to make the benchmark surface inspectable
    without strengthening it into a claim.
11. Compact-radius mass-quartile scout (`TASK-0480`, DONE): preserve as
    underpowered/inconclusive until compact-slice coverage improves.
12. Second-snapshot target freeze and external-reviewer capsule (`TASK-0482`
    and `TASK-0484`, DONE): use these for no-peek discipline and scientific
    replayability.
13. Null-baseline family audit (`TASK-0483`, DONE) found the main residual
    slices control-sensitive; host-context preflight (`TASK-0481`, READY) is
    now the next benchmark-hardening step before any stronger residual
    interpretation.
14. Bounded autonomous hypothesis pilot only after a narrow target survives
    matched controls, null baselines, host-context preflight, and conservative
    promotion scoring.

This campaign is now the fastest APL path to a visible, scientist-readable
benchmark artifact. It is not yet a discovery surface.
