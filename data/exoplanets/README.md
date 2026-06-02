# Exoplanet Mass-Radius Data Area

This directory is reserved for the future Exoplanet Mass-Radius scientific
campaign source surface.

`TASK-0337` is a preparation-only task. It defines admissible source classes,
manifest metadata fields, schema shape, and holdout discipline **without
fetching live archive data, without committing catalog rows, and without
running any benchmark**.

## Current Contents

- [`source_manifest_template.yaml`](./source_manifest_template.yaml):
  metadata-only source manifest template defining admissible source families
  and the per-family pinning, license, citation, and uncertainty-semantics
  fields a future ingestion task must populate.

Schema sketch and holdout protocol live one level up under:

- [`../../physics_lab/schemas/exoplanet_mass_radius.schema.json`](../../physics_lab/schemas/exoplanet_mass_radius.schema.json)
- [`../../docs/exoplanet-mass-radius-holdout-protocol.md`](../../docs/exoplanet-mass-radius-holdout-protocol.md)
- [`../../docs/reviews/exoplanet-mass-radius-source-surface-review.md`](../../docs/reviews/exoplanet-mass-radius-source-surface-review.md)

## Row Classes

Future row-level files under this directory must declare exactly one of the
following row classes per entry. **Mixing classes on a single residual axis
is forbidden** and is the most likely overclaim trap in this campaign:

| Row class | Meaning | Ingestion rule |
| --- | --- | --- |
| `direct_mass_radius_measurement` | Both mass and radius are direct measurements (e.g. transit radius + RV true mass for a transiting hot Jupiter; transit radius + transit-timing variation true mass). | Allowed only after source-manifest review and per-row uncertainty semantics. |
| `transit_radius_with_rv_minimum_mass` | Radius is direct from transit; mass is `M sin i` from radial velocity only (no transit-induced inclination break). | Allowed only with explicit `minimum_mass` flag; **must not** be silently treated as true mass. |
| `transit_radius_only` | Radius is direct from transit; mass is absent or model-inferred. | Treat as radius-only row; do not impute a mass value. |
| `rv_minimum_mass_only` | Mass is `M sin i` from RV; radius is absent or model-inferred. | Treat as mass-only row; do not impute a radius value. |
| `microlensing_or_astrometry_mass` | Mass is from microlensing, astrometry, or transit-timing dynamics; radius is absent or model-inferred. | Allowed only with method-class flag preserved per row. |
| `model_inferred` | Mass or radius is back-computed from a published mass-radius relation or composition model. | **Not ingestible as benchmark evidence**; allowed only as explicit comparison surface with `inferred` flag. |
| `synthetic_dry_run` | Fabricated values for testing schema or loaders. | Allowed only when row carries `synthetic: true` and `real_measurement_source: false`. |

A future curator who cannot satisfy a row class must record the row with
`inclusion_status: excluded` and an explicit `exclusion_reason`, not collapse
the row into a different class to satisfy a benchmark count.

## Admissible Source Classes

| Source family id | Admissible row classes | First-attempt examples |
| --- | --- | --- |
| `EXO-SRC-CLASS-001` | composite-catalog snapshots | NASA Exoplanet Archive Planetary Systems Composite Parameters (`PSCompPars`) |
| `EXO-SRC-CLASS-002` | per-planet primary-publication tables | peer-reviewed discovery and characterization papers in AJ, A&A, ApJ, MNRAS, Nature, Science |
| `EXO-SRC-CLASS-003` | mission-pipeline catalog releases | Kepler DR25, K2 mission catalog, TESS confirmed-planet tables |
| `EXO-SRC-CLASS-004` | archive copy of any of the above | institutional repository mirrors of EXO-SRC-CLASS-001..003 with stable identifiers |

Each future source-manifest entry must record the source family id, source
locator, release date, retrieval date, checksum (or explicit
`not_committed_reason`), license note, value semantics, uncertainty semantics,
detection-method coverage, and stop conditions.

## Normalized Snapshot Checksum

The pinned PSCompPars snapshot carries two SHA-256 checksums with distinct
scopes:

- `source_manifest.yaml` records the SHA-256 hash of the committed normalized YAML snapshot file exactly as stored in git;
- the snapshot's embedded `snapshot_provenance.normalized_checksum_sha256`
  records a deterministic canonical-payload SHA-256. The canonicalizer parses
  the YAML mapping, replaces the embedded checksum field with `null`, encodes
  the full payload as sorted compact JSON, and hashes the UTF-8 bytes. This
  avoids a self-referential file hash while detecting row and metadata drift.

Cross-platform embedded-checksum replay:

```bash
python3 scripts/check_exoplanet_normalized_snapshot_checksum.py
```

Linux/macOS reproduction:

```bash
sha256sum data/exoplanets/exo-0001-pscomppars-snapshot.yaml
```

Windows PowerShell reproduction:

```powershell
Get-FileHash data\exoplanets\exo-0001-pscomppars-snapshot.yaml -Algorithm SHA256
```

The manifest checksum covers the entire committed normalized YAML file, not a
canonical re-serialization of selected rows. Any byte-level change to the
committed snapshot file changes that checksum. The embedded canonical-payload
checksum detects semantic payload changes while remaining stable across YAML
formatting changes.

This checksum is a source-provenance guard only. It does not validate scientific
correctness, benchmark metrics, planet classifications, or residual claims.

## Allowed Future Contents

A future maintainer-approved task may add:

- a pinned `PSCompPars` snapshot with retrieval date and checksum;
- per-publication row-level `exo-NNNN-*.yaml` files;
- deterministic loader contracts;
- synthetic-only dry-run rows with fabricated values;
- direct-measurement rows only after source-manifest review, license, checksum,
  uncertainty semantics, detection-method coverage, and holdout protocol are
  all reviewed.

## Not Allowed Yet

Do not add:

- live archive fetches inside agent tasks without a pinned snapshot policy;
- catalog rows from any source until the source-manifest entry is reviewed;
- mass values labelled as direct when they are `M sin i` minimum masses;
- model-inferred mass or radius values mixed with direct measurements on a
  single residual axis;
- composition-class labels that imply rocky / volatile / gas without an
  explicit decision rule;
- habitability scores, biosignature flags, or "Earth-like" classifications;
- benchmark metrics before the schema and holdout protocol are reviewed;
- prediction registry entries for any planet;
- broad planetary-formation-law fits.

## Required Coordination

Future tasks under this campaign must read:

- [`../../docs/campaigns/exoplanet-mass-radius.md`](../../docs/campaigns/exoplanet-mass-radius.md)
- [`../../docs/exoplanet-mass-radius-holdout-protocol.md`](../../docs/exoplanet-mass-radius-holdout-protocol.md)
- [`../../docs/reviews/exoplanet-mass-radius-source-surface-review.md`](../../docs/reviews/exoplanet-mass-radius-source-surface-review.md)
- [`../../docs/notes/fresh-data-source-policy.md`](../../docs/notes/fresh-data-source-policy.md)

before any source-manifest entry, schema change, loader, or benchmark task is
opened.

## What Not To Claim

- Do not say APL has discovered an exoplanet mass-radius law.
- Do not say residual structure implies a new planet-formation theory.
- Do not say the campaign supports planet-prioritization, target-selection,
  habitability scoring, or biosignature inference.
- Do not blur `M sin i` minimum masses, true masses, transit-timing dynamical
  masses, and model-derived masses under one metric.
- Do not promote sandbox residual maps as canonical campaign results.
- Do not open public-facing scientific claims before the first canonical
  benchmark and residual map exist.
