# Exoplanet Mass-Radius Source-Surface Review

**Task:** TASK-0337
**Status:** source-surface review (no rows ingested, no benchmark run)
**Campaign:** Exoplanet Mass-Radius (planned fourth campaign)
**Inputs reviewed:**

- `docs/campaigns/exoplanet-mass-radius.md`
- `docs/notes/fresh-data-source-policy.md`
- `data/exoplanets/README.md` (new)
- `data/exoplanets/source_manifest_template.yaml` (new)
- `physics_lab/schemas/exoplanet_mass_radius.schema.json` (new)
- `docs/exoplanet-mass-radius-holdout-protocol.md` (new)

## Scope

This review records the first preparation-only source-surface assessment
for the Exoplanet Mass-Radius campaign. It does not fetch live archive
data, does not commit any catalog rows, does not run a baseline, does not
register any prediction, and does not promote any claim.

The purpose is to make the future ingestion task reviewable in advance:
which source classes are admissible, which is the recommended
first-catalog source, which fields must be preserved per row, and which
cases must stop the ingestion task and surface as blockers.

## Method

1. Read the campaign page and confirmed the recommended-next-shape
   sequence (TASK-0337 source scaffold → pinned snapshot task → loader →
   baseline reproduction → residual map → optional autonomous pilot).
2. Read the fresh-data source policy and confirmed that the exoplanet
   axis is not currently on the WATCHLIST (PTA, GW catalogs, and
   event-level collider data remain there). Composite catalog snapshots
   plus peer-reviewed primary publications are admissible for a future
   preparation step.
3. Drafted the value-free `data/exoplanets/README.md`, the
   `source_manifest_template.yaml` scaffold mirroring the atomic-clock
   template structure, the JSON schema for row-level dataset snapshots,
   and the holdout protocol.
4. Recorded admissibility decisions per source class without listing or
   pinning any specific catalog version, paper, or row value.

## Findings

### F1. Composite catalog snapshots are the recommended first-catalog source

`EXO-SRC-CLASS-001` (NASA Exoplanet Archive Planetary Systems Composite
Parameters; the archive's `PSCompPars` table is the canonical example)
is the recommended first source for the future ingestion task. The
reasons:

- it is a centralised, freely available, well-maintained public archive;
- it aggregates per-row provenance fields including detection method,
  reference publication, host-star context, and per-parameter
  uncertainties;
- it supports a pinned snapshot via the archive's TAP service with an
  explicit retrieval date.

The first ingestion task should pin a single retrieval-date snapshot,
commit (or archive with checksum) the raw CSV, and record the per-row
`pl_bmasse` / `pl_rade` / `pl_bmassprov` style fields with the source-
manifest stop conditions enforced.

### F2. Composite catalogs must be paired with row-class flags

`PSCompPars` and similar composite catalogs report a mix of true masses,
`M sin i` minimum masses, transit-timing dynamical masses, and
model-inferred values under one logical column. A future loader must
populate `mass_class` per row from the catalog's provenance flag
(`pl_bmassprov` or equivalent) and refuse to score rows whose provenance
cannot be recovered.

Concretely: a row whose mass provenance is `Msini` must be loaded with
`mass_class: minimum_mass_msini` and excluded from the
`true_mass_versus_radius` residual axis even if it otherwise satisfies
the quality filter.

### F3. Per-publication primary tables are a follow-up, not a first step

`EXO-SRC-CLASS-002` (peer-reviewed primary publications, e.g. AJ, A&A,
ApJ, MNRAS) carries higher-fidelity uncertainty semantics but requires
per-paper review and per-paper redistribution-terms assessment. The
recommended sequence is: first ingest the composite snapshot, then
attach per-row references from primary publications as supplementary
provenance, then on a per-publication basis review whether a richer
uncertainty representation supersedes the composite value.

### F4. Mission-pipeline releases are admissible but selection-function gated

`EXO-SRC-CLASS-003` (Kepler / K2 / TESS confirmed-planet tables) is
admissible but only after the mission's selection function is
documented. Transit detection probability is a strong function of
planet radius, orbital period, host-star size, and observing window;
ignoring the selection function would silently bias residual maps.

A future task that wants to use Kepler or TESS data alone (e.g. for a
detection-method holdout) must commit a selection-function reference in
the source-manifest entry before scoring.

### F5. Archive copies must match the primary checksum

`EXO-SRC-CLASS-004` (institutional or third-party mirrors) is admissible
as a reproducibility copy of a primary source but only when the mirror's
SHA-256 matches the primary's `raw_checksum_sha256`. A mirror whose
checksum differs is treated as a separate source class and reviewed
under its own manifest entry.

### F6. Row-class separation is the most likely overclaim trap

The campaign has more failure modes from row-class mixing than from data
quality:

- using `M sin i` minimum masses as if they were true masses (silently
  biased low by ~20% for an isotropic-inclination distribution);
- using model-inferred masses (e.g. masses imputed from a Chen-Kipping
  forecast) as benchmark evidence to validate the same Chen-Kipping
  forecast (circular);
- mixing transit-radius-only rows with mass-only rows under one residual
  metric;
- treating microlensing or astrometric masses as interchangeable with
  RV true masses without method-class flags.

The schema and holdout protocol encode these separations as hard rules;
the source-manifest template encodes them as per-source stop conditions.

### F7. Composition-class labels are not loader output

The holdout protocol defines radius-bin classes (terrestrial, super-
Earth, sub-Neptune, Neptune-like, gas giant, inflated hot Jupiter) as
analysis-time labels, not source-manifest output. A loader must not
write "rocky" or "volatile-dominated" composition flags; those are
inferences that require their own review.

## What This Review Did Not Do

- It did not fetch any live data from NASA Exoplanet Archive, MAST,
  ExoFOP, or any other archive.
- It did not commit a catalog snapshot or any per-row YAML.
- It did not register any source-manifest entry with real metadata
  (only the template scaffold with `not_reviewed` and `null`
  placeholders).
- It did not write loader code, baseline code, or residual-map code.
- It did not register a prediction registry entry for any planet.
- It did not promote any claim or rewrite any canonical result.
- It did not produce composition, habitability, biosignature, or
  prioritization output.

## Stop Conditions Carried Forward Into Future Ingestion Tasks

A future ingestion task must stop and surface a blocker when:

- a source omits per-row mass-method labels or provenance flags;
- a source mixes true and minimum masses without a row-level flag;
- a source mixes direct measurements and model-inferred values without a
  row-level flag;
- a source omits uncertainty semantics or reports asymmetric uncertainties
  without conventions;
- a source lacks a retrieval date, archive plan, or stable identifier;
- a source's reuse terms are unclear (cannot redistribute even if
  required for benchmark reproducibility);
- the task requests habitability, biosignature, or target-prioritization
  output;
- the task requests a broad planet-formation-law fit before source review.

## Recommendation for the Next Task

The next maintainer-approved task after TASK-0337 should be a single
pinned-snapshot ingestion task targeting `EXO-SRC-CLASS-001`
(`PSCompPars`) with:

- a documented retrieval-date snapshot;
- raw CSV committed or archived with SHA-256;
- per-row loader output filling the `mass_class`, `radius_class`,
  `detection_method`, and `host_star` context fields;
- explicit `inclusion_status` decision per row, with quality-filter
  thresholds committed before any benchmark code is written;
- no metric computation in the same task.

That ingestion task should be reviewed before any baseline reproduction
task is opened.

## Limitations

- The source-class shortlist is intentionally narrow; future expansion
  (e.g. ESA Ariel data products, NASA Astrobiology samples, deep-survey
  follow-up archives) requires a separate source-class review.
- The review does not commit a specific NASA Exoplanet Archive snapshot
  date; pinning that date is the explicit job of the ingestion task.
- The recommended Chen-Kipping baseline in the holdout protocol is one
  reasonable conservative choice; an alternate baseline (e.g. Forecaster,
  Otegi 2020, Müller 2021) may be substituted as long as its choice is
  documented in the pre-reveal package.
- This review does not authorise live data fetches.

## Verdict

`PARTIALLY_VALID` for the campaign's preparation scaffold. The source
classes, manifest fields, schema shape, holdout discipline, and stop
conditions are now reviewable in advance. The campaign remains in
"planned fourth campaign" status; no benchmark, residual map, or
prediction registry entry exists. The next step is a maintainer-approved
pinned-snapshot ingestion task targeting `EXO-SRC-CLASS-001`.
