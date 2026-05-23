# Exoplanet Mass-Radius Baseline Protocol

## Purpose

This protocol defines the first benchmark contract for the Exoplanet
Mass-Radius campaign **before any catalog row is ingested or scored**.

The goal is to lock the baseline family, the null baseline, the allowed
metrics, the mandatory splits, the negative controls, and the row
exclusions in advance so that:

- a future benchmark task cannot pick a flattering metric after seeing
  the residuals;
- a Chen-Kipping-style baseline cannot be circularly "validated" using
  rows whose masses were already imputed from a similar relation;
- residual maps remain interpretable rather than post-hoc visual
  storytelling.

This protocol is upstream of any baseline implementation task. It does
not fetch live data, does not commit catalog rows, does not run any
metric, and does not promote any claim.

## Scope

The protocol applies to the first Exoplanet Mass-Radius baseline
benchmark and to bounded follow-up correction-hypothesis experiments.
It assumes the pinned snapshot policy from TASK-0345 and the holdout
protocol in
[`./exoplanet-mass-radius-holdout-protocol.md`](./exoplanet-mass-radius-holdout-protocol.md)
are honored.

It is not a license to:

- claim a universal planet mass-radius law;
- support planet prioritization, habitability scoring, or biosignature
  inference;
- mix true-mass and `M sin i` rows on a single residual axis;
- substitute model-inferred masses for missing measurements.

## Baseline Family

### Primary baseline — Chen-Kipping-style probabilistic forecaster

The first benchmark uses a **Chen-Kipping-style** probabilistic mass-
radius forecaster as the primary baseline. The exact reference
implementation is
*Chen, J. & Kipping, D. M., "Probabilistic Forecasting of the Masses
and Radii of Other Worlds," ApJ 834, 17 (2017)*. The baseline:

- treats the mass-radius relation as a piecewise power-law with
  changepoints between four regimes (Terran, Neptunian, Jovian,
  Stellar);
- returns a per-row predicted radius distribution given the observed
  mass (or vice versa), not a single point estimate;
- exposes both the median prediction and an explicit prediction
  interval.

Required of the implementation task:

- the baseline's parameters must be **reproduced from the published
  paper** at a frozen retrieval date and committed to a baseline
  configuration file;
- the baseline must **not** be re-fitted on the campaign's pinned
  catalog snapshot. A baseline that is re-fitted on the same data it
  is then evaluated against is no longer a reproducible reference;
- per-row baseline output must record the median, the 16th and 84th
  percentiles, and the regime label assigned by the changepoint.

### Allowed alternative baselines

A future benchmark task may substitute one of the following as an
alternative baseline, **provided the choice is committed to the
pre-reveal package before scoring** and the choice is justified:

- **Forecaster** (Chen-Kipping code release; same form, frozen
  parameters);
- **Otegi et al. 2020** (rocky vs volatile-dominated dichotomous fit;
  *A&A* 634, A43);
- **Müller, Bashi & Helled 2025** (or equivalent Bayesian forecaster
  with explicit intrinsic-scatter component, when available);
- **Bashi et al. 2017** (broken power-law fit).

Alternative baselines may also be reported **alongside** Chen-Kipping
as comparators. Mixing alternative baselines into a single residual
axis without explicit per-baseline reporting is forbidden.

## Null Baseline

The first benchmark must also report against a much simpler null
baseline so that any candidate improvement has a recognizable floor:

**Constant-radius-per-class null.** For each planet class defined in
the holdout protocol (terrestrial, super-Earth, sub-Neptune,
neptune-like, gas-giant, inflated hot Jupiter), compute the per-class
**median** radius on the training fold and predict that median for every
row in the held-out fold. The null does not use the row's mass.

A candidate baseline that fails to beat this constant-per-class null on
the holdout is **not useful** for that class. Negative outcomes are
preserved, not hidden.

## Allowed Metrics

The benchmark reports the following metrics. No other metric should be
introduced post-hoc without an amendment PR to this protocol.

### 1. Uncertainty-aware residuals

For each eligible row, compute:

- **predicted minus observed radius**, in Earth radii;
- **z-score residual** = `(observed_radius - predicted_radius_median)
  / combined_sigma`, where `combined_sigma^2 = observed_radius_sigma^2
  + predicted_radius_sigma^2` from the prediction interval;
- **chi-squared contribution** per row when the baseline returns a
  Gaussian-equivalent prediction interval;
- **per-class summary**: median z-score, fraction of rows with
  |z| > 2, fraction outside the 68% / 95% prediction intervals.

### 2. Log-space errors

Mass-radius residuals are dominated by the wide dynamic range of the
catalog (Earth-mass to Jupiter-mass+). Report log-space errors as the
primary aggregate metric:

- **MAE in log10 radius** = `mean(|log10(predicted_radius) -
  log10(observed_radius)|)`;
- **RMSE in log10 radius** = `sqrt(mean((log10(predicted_radius) -
  log10(observed_radius))^2))`;
- per-class log-space MAE and RMSE.

### 3. Calibration

When the baseline returns a prediction interval, report the empirical
coverage:

- **68% interval coverage**: fraction of held-out rows whose observed
  radius falls inside the predicted 68% interval;
- **95% interval coverage**: same for 95%;
- a coverage value far from the nominal level is a calibration
  failure, not a model failure; both are reported.

### 4. Failure-map summary

A failure map is a per-row table that lists, for each held-out row:

- planet class, mass class, detection method, host class;
- baseline median prediction and interval;
- observed mass, observed radius, uncertainties;
- z-score residual and its sign;
- failure flag when `|z| > 3` (extreme outlier).

The failure map is the campaign's primary visual artifact. It is **not
a metric**; it is preserved memory.

## Mandatory Splits

The first benchmark must report metrics under **at least** the
following splits (no exceptions; collapsing into a single number hides
the structure the campaign exists to surface):

### Split A — Planet class

Six bins per the holdout protocol. Each bin reported separately. The
radius-valley straddlers (super-Earth, sub-Neptune) are **always
reported separately**; combining them under one bin hides the radius-
valley structure.

### Split B — Detection method

Per detection method (transit-and-RV, transit-only, RV-only,
transit-timing, microlensing, astrometry, direct imaging). Methods
with row counts below the holdout protocol's documented floor are
reported with the count and an explicit "low-count" note rather than
silently dropped.

### Split C — Mass class

True-mass rows and `M sin i` rows are reported on **separate
residual axes** with separate metrics. They are never averaged.

### Split D — Host-star context

At least the coarse spectral-class bin from the holdout protocol
(M / K / G / F / hot / subgiant). A metallicity split is allowed when
`[Fe/H]` is available, but only after the spectral-class split has
been reported.

### Split E — Source-date (optional but recommended)

Pre-2014 / 2014-2020 / 2020+ split as defined in the holdout protocol.
Useful for diagnosing whether the baseline generalizes to recently-
confirmed planets.

### Split F — Measurement-quality filter (always applied)

The benchmark reports both **pre-filter** and **post-filter** metrics.
Filter thresholds match the holdout protocol defaults
(`sigma_M/M ≤ 0.30`, `sigma_R/R ≤ 0.15`). The pre/post comparison is
itself a diagnostic.

## Negative Controls

These controls are non-negotiable and catch the most likely failure
modes for this campaign.

### NC-1 — Circular-validation control

Re-run the benchmark **with the `model_inferred` rows included** (i.e.
including rows whose mass was already imputed from a published mass-
radius relation). The included-control metric will look misleadingly
good because the baseline is being scored against its own functional
form on those rows. Report the gap between the included-control and
the production (excluded) result. A small gap is suspicious; a large
gap is the expected protective behavior of excluding model-inferred
rows.

### NC-2 — Class-transfer control

Train the baseline on one class (e.g. gas giants) and evaluate on a
different class (e.g. sub-Neptunes). The cross-class residual is the
control that demonstrates class transfer is non-trivial. A candidate
that "wins" on the in-class holdout but fails dramatically under
class-transfer is a class-overfit candidate, not a general
improvement.

### NC-3 — Random-shuffle mass control

Within each class, **shuffle the mass column** randomly across rows and
re-fit the baseline (or apply the frozen baseline). The shuffled
residual is the noise floor: any candidate must show a clearly
larger improvement against the real-mass data than against the
shuffled-mass data.

### NC-4 — Wrong-method control

Train on transit-and-RV rows; evaluate on `M sin i`-only rows
**without** correcting for the inclination bias. The control's
residual reveals how much of the apparent radius prediction comes from
the average inclination bias of an `M sin i` mass distribution.

### NC-5 — Constant-radius null

Defined above. The candidate must beat this null in holdout to count
as useful for that class.

## Mandatory Row Exclusions

The first benchmark must exclude the following rows from the
**true-mass residual axis**. Each exclusion is preserved in the
failure map with `inclusion_status: excluded` and an explicit reason;
none is silently dropped.

- rows with `mass_class: model_inferred` (always excluded; circular
  validation risk);
- rows with `mass_class: minimum_mass_msini` (excluded from the true-
  mass axis; they live on the separate minimum-mass axis);
- rows where the radius is `model_inferred` rather than `transit_radius`
  or `direct_imaging_radius`;
- rows that fail the measurement-quality filter (excluded from the
  post-filter metric only; preserved in the pre-filter result);
- rows where the host-star context is incomplete and the analysis
  requires a host-context split (excluded only from the host-context
  split, not from the planet-class split);
- rows with `inclusion_status: excluded` in the snapshot file
  regardless of reason.

## What This Protocol Does Not Authorize

- It does not authorize running any baseline against any catalog
  snapshot.
- It does not authorize fetching live archive data.
- It does not authorize a benchmark implementation task in this PR.
- It does not authorize claim promotion, prediction registry entries,
  or canonical result artifacts.
- It does not authorize habitability, biosignature, or target-
  prioritization output.
- It does not authorize composition-class labels (rocky / volatile /
  gas) as baseline output. Those remain analysis-time labels.

## Recommended Follow-Up Implementation Task Shape

A future maintainer-approved task may implement the first baseline
benchmark. That task should:

- depend on a merged TASK-0345 ingestion plan;
- depend on a merged ingestion task that committed a pinned
  `PSCompPars` snapshot under
  `data/exoplanets/exo-NNNN-pscomppars-snapshot.yaml`;
- commit the frozen Chen-Kipping baseline parameters to
  `data/exoplanets/baselines/chen_kipping_2017.yaml` (or equivalent)
  with explicit retrieval citation;
- compute the metrics under the splits and controls above on the
  pinned snapshot;
- emit a benchmark result artifact under `agent_runs/AGENT-RUN-XXXX/`
  with the failure map, per-split metrics, calibration coverages, and
  negative-control comparisons;
- **not** retrain the baseline on the pinned snapshot;
- **not** introduce new metrics or new splits without an amendment
  PR to this protocol.

## Relationship to Other Protocols

- [`./exoplanet-mass-radius-holdout-protocol.md`](./exoplanet-mass-radius-holdout-protocol.md)
  defines the holdout discipline this protocol assumes;
- [`./reviews/exoplanet-mass-radius-source-surface-review.md`](./reviews/exoplanet-mass-radius-source-surface-review.md)
  is the source-surface gate;
- [`./reviews/exoplanet-pscomppars-snapshot-ingestion-plan.md`](./reviews/exoplanet-pscomppars-snapshot-ingestion-plan.md)
  defines the ingestion contract for the snapshot this benchmark will
  consume;
- [`./blind-holdout-benchmark-protocol.md`](./blind-holdout-benchmark-protocol.md)
  remains the cross-campaign holdout reference.

## Limitations

- The Chen-Kipping baseline is one reasonable conservative choice;
  alternatives (Forecaster, Otegi 2020, Müller 2025) are equally
  acceptable as long as the choice is locked in the pre-reveal
  package.
- The null baseline (constant per-class median) is a deliberately
  weak floor. A candidate that beats it has cleared a low bar and
  must still beat the primary baseline before being useful.
- The protocol does not estimate how many rows will survive the
  filters for any specific snapshot; that is a per-snapshot
  diagnostic.
- The protocol intentionally does not relax the row-class separation
  policy under any "small expected bias" argument.
- The protocol does not authorize live external data fetches or
  archive snapshots outside the TASK-0345 ingestion contract.

## Verdict

`PARTIALLY_VALID` for the baseline benchmark contract. The baseline
family, null baseline, allowed metrics, mandatory splits, negative
controls, and row exclusions are now reviewable in advance. No
benchmark has run; no metric exists; no result artifact is committed.
The next allowed step is a maintainer-approved ingestion task
(per TASK-0345) followed by a separate maintainer-approved baseline
implementation task that follows this protocol verbatim.
