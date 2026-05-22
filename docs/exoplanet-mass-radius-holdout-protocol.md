# Exoplanet Mass-Radius Holdout Protocol

## Purpose

This protocol defines how the Exoplanet Mass-Radius campaign splits curated
catalog rows for holdout evaluation before any candidate baseline or
correction term is scored.

The goal is to distinguish:

- interpolation within a known mass-radius regime, planet class, and
  detection method;
- generalization across detection methods (transit only vs RV only vs
  joint vs microlensing or astrometry);
- generalization across host-star context (M / K / G / F dwarfs, subgiants,
  metallicity bins);
- size and mass-range extrapolation beyond the training distribution;
- transfer across catalog source dates (pre-2020 versus post-2020
  characterization).

This protocol is upstream of the first Exoplanet Mass-Radius baseline
residual benchmark. No holdout target should be inspected before the
benchmark is defined and its pre-reveal package is committed.

## Scope

The protocol applies to future exoplanet mass-radius benchmarks,
correction-hypothesis experiments, and sandbox autonomous pilots scoped to
`campaign_profiles/exoplanet-mass-radius.yaml` (when that profile lands).

It is intended for:

- conservative Chen-Kipping-style baseline comparisons;
- compact mass-radius scaling corrections with explicit class-applicability
  flags;
- residual structure exploration across planet classes, mass ranges,
  detection methods, and host-star context;
- negative-control candidates that should fail under structured holdout.

It is not a license to claim a universal planet mass-radius law, to support
target prioritization, habitability scoring, or biosignature inference, or to
publish discovery-style framing.

## Row Class Separation Policy

True-mass measurements, `M sin i` minimum masses, transit-radius-only rows,
mass-only rows, microlensing/astrometric masses, and model-inferred values
are **never combined on a single residual axis**. This is a hard rule, not a
guideline. Mixing row classes is the most likely overclaim trap in this
campaign.

Required separation:

- a residual axis labelled `true_mass_versus_radius` may only include rows
  with `row_class: direct_mass_radius_measurement` and `mass_class:
  true_mass`;
- a residual axis labelled `minimum_mass_versus_radius` is only meaningful
  when paired with the matching `mass_class: minimum_mass_msini` rows; its
  interpretation must include the average inclination bias correction in
  the review note;
- transit-radius-only rows can support a `radius_distribution` analysis but
  are not eligible for a mass-residual axis;
- microlensing or astrometric rows live on a separate `alternate_method`
  axis; they may be cross-referenced but not silently averaged with
  transit-plus-RV rows;
- model-inferred rows are never scored as benchmark evidence; they may be
  shown as a comparison surface for residual diagnostics with the
  `inferred` flag explicit on the panel.

## Required Holdouts

The first baseline benchmark must report at least three holdout splits.
Each split is reported separately; their unions are not collapsed into one
metric.

### 1. Planet class holdout (required)

Bin planets into the following classes by radius (when available):

| Class | Radius range | Notes |
| --- | --- | --- |
| terrestrial | R < 1.25 R_earth | rocky-candidate regime |
| super_earth | 1.25 ≤ R < 2.0 R_earth | rocky-to-volatile transition |
| sub_neptune | 2.0 ≤ R < 4.0 R_earth | radius valley straddler |
| neptune_like | 4.0 ≤ R < 6.0 R_earth | volatile-dominated |
| gas_giant | 6.0 ≤ R < 15.0 R_earth | jovian regime |
| inflated_hot_jupiter | R ≥ 15.0 R_earth | inflation regime |

Hold out one class at a time and report per-class residuals when training
on the others. The radius-valley straddler classes (`super_earth`,
`sub_neptune`) must be reported separately; combining them under one bin
hides the radius-valley structure.

### 2. Detection-method holdout (required)

Hold out one detection method at a time:

- `transit_and_radial_velocity` only;
- `transit` only with `model_inferred` mass (excluded from residual axis);
- `radial_velocity` only with `M sin i` mass;
- `transit_timing_variation` only;
- `microlensing` only;
- `astrometry` only;
- `direct_imaging` only.

Reporting must include per-method counts, per-method MAE/RMSE in dex (log10
mass and log10 radius) when applicable, and a note when a method's row
count is below a documented minimum (suggested floor: 5 rows).

### 3. Host-star context holdout (required)

Bin host stars into a coarse spectral-class plus metallicity grid:

| Host bin | Notes |
| --- | --- |
| M dwarf | cooler than ~3700 K |
| K dwarf | 3700 K ≤ Teff < 5200 K |
| G dwarf | 5200 K ≤ Teff < 6000 K |
| F dwarf | 6000 K ≤ Teff < 7500 K |
| hot host | Teff ≥ 7500 K |
| subgiant or evolved | log g ≤ 4.0 |

Metallicity should be reported in a coarse split (metal-poor, solar,
metal-rich) when `[Fe/H]` is available. The first benchmark may use spectral
class alone as the host-context axis; a finer metallicity split is allowed
only after the spectral-class split has been reported.

### 4. Mass-range and radius-range holdouts (optional but recommended)

When the catalog count allows it:

- low-mass holdout (e.g. M < 5 M_earth);
- high-mass holdout (e.g. M ≥ 1 M_jup);
- small-radius holdout (R < 2 R_earth);
- large-radius holdout (R ≥ 10 R_earth).

Bin boundaries must be committed to the pre-reveal package before scoring.

### 5. Source-date holdout (optional)

Split by `discovery_year` or by `release_date_or_publication_date`:

- pre-2014 (mostly Kepler primary mission);
- 2014–2020 (K2 plus early TESS plus RV characterization wave);
- 2020 and later (TESS prime plus systematic RV follow-up).

This split is useful for diagnosing whether a candidate model generalises
to recently-confirmed planets. It is not a substitute for a planet-class
holdout.

### 6. Measurement-quality filter (always applied)

Every benchmark must report results both before and after filtering by:

- mass relative uncertainty below a documented threshold (suggested
  `sigma_M / M ≤ 0.30`);
- radius relative uncertainty below a documented threshold (suggested
  `sigma_R / R ≤ 0.15`);
- explicit `inclusion_status: included` flag.

A row that fails the quality filter is preserved with
`inclusion_status: excluded` and an `inclusion_reason` like
`quality_filter_failed`. It is never silently dropped.

## Negative Controls

The first baseline must include at least:

- **Constant-radius predictor per class**: a residual axis comparing the
  candidate baseline against a flat per-class median radius; the candidate
  must beat this floor in a holdout setting to count as useful;
- **Wrong-class baseline transfer**: evaluate a baseline trained only on
  gas giants when applied to sub-Neptunes (and vice versa); the residual is
  the negative control that demonstrates class transfer is non-trivial;
- **Random-shuffle mass control**: shuffle the mass column within a class
  and re-fit; the candidate must show a sign-pair break against this
  control.

## Forbidden In The First Benchmark

- mixing `true_mass`, `minimum_mass_msini`, and `model_inferred` rows under
  one residual axis;
- averaging residuals across detection methods;
- claiming a discovery-level mass-radius law from a single class;
- using `M sin i` rows as if they were true masses, even with a "small
  expected bias" hand-wave;
- target prioritization, habitability scoring, or biosignature inference
  framed as a benchmark outcome;
- substituting a model-inferred mass for a missing measurement and scoring
  the row as direct.

## Recommended First-Baseline Configuration (when unblocked)

When the source manifest and a pinned catalog snapshot land, the first
recommended baseline configuration is:

- **Primary axis**: `true_mass_versus_radius` using only
  `direct_mass_radius_measurement` rows with `mass_class: true_mass`;
- **Baseline family**: Chen-Kipping-style probabilistic mass-radius
  forecaster reproduced from the published parameters at a frozen
  retrieval date; baseline output is reported as a per-class prediction
  interval, not a single number;
- **Required holdouts**: planet class (one held out at a time) plus
  detection method (transit-plus-RV vs RV-only vs alternate-method);
- **Negative controls**: constant-radius-per-class predictor, wrong-class
  baseline transfer, random-shuffle mass control;
- **Quality filter**: applied; results reported both pre- and post-filter;
- **Visualization**: per-class residual scatter, classic mass-radius
  diagram with class colours, residual heatmap over (mass-bin, host-class).

## Relationship To Other Protocols

- [`./quantum-size-effect-holdout-protocol.md`](./quantum-size-effect-holdout-protocol.md)
  and [`./nuclear-mass-holdout-protocol.md`](./nuclear-mass-holdout-protocol.md)
  define the same holdout discipline shape for sibling campaigns;
- [`./blind-holdout-benchmark-protocol.md`](./blind-holdout-benchmark-protocol.md)
  remains the cross-campaign holdout reference;
- [`./reviews/exoplanet-mass-radius-source-surface-review.md`](./reviews/exoplanet-mass-radius-source-surface-review.md)
  is the source-readiness gate analogous to TASK-0283 for quantum size
  effects.

## Limitations

- This protocol is upstream of a benchmark; it does not by itself produce
  any score.
- Bin boundaries above are recommended defaults; a future benchmark task
  may justify different bins as long as they are committed to the
  pre-reveal package before scoring.
- The protocol does not authorise live external data fetches; it assumes a
  pinned snapshot governed by the source-manifest template.
- The protocol does not estimate how many rows will survive the quality
  filter for any specific catalog snapshot; that is a per-snapshot
  diagnostic.
- The protocol intentionally does not relax the row-class separation
  policy under any "small expected bias" argument.
