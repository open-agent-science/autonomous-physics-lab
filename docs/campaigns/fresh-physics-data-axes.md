# Fresh Physics Data Axes

## Goal

Define a conservative source-policy surface for future physics datasets that
are less saturated than the current PDG and AME-style benchmark inputs.

This campaign is not a data-ingestion campaign yet. Its purpose is to make
future ingestion tasks reviewable before any agent adds rows, runs analyses,
or starts cross-domain fitting.

## Current Status

Planning scaffold only.

`TASK-0309` defines:

- source policy and ingestion prerequisites:
  [Fresh-Data Source Policy](../notes/fresh-data-source-policy.md);
- first-pass scope for atomic-clock comparison campaigns and lattice-QCD
  aggregated outputs;
- WATCHLIST boundaries for PTA releases, gravitational-wave catalogs, and
  event-level collider data.

Atomic clocks have since graduated into their own source-gated campaign page.
FRB / radio transients has also graduated from generic fresh-data scouting into
an activated sealed-prediction preparation lane. The older CHIME/FRB Catalog 2
HDF5 map remains blocked for pre-T construction because it is a static
cumulative full-window map with no time axis. The active route is now the
separate Catalog-1 interval exposure pair: its checksum/schema gate passed, and
`TASK-0963` constructed a compact 479-row pre-T exposure feature surface, and
`TASK-0964` froze the exposure-only model surface for the follow-on
`TASK-0965` sealed-registration pack.

No broad fresh-data dataset has been ingested from this scaffold. No claim,
result, or knowledge entry is promoted.

## Why This Exists

APL already has disciplined benchmark surfaces for pendulum, damped
oscillator, particle masses, dimensional analysis, and nuclear masses.
Fresh-data axes may eventually give future agents less-mined evidence
surfaces, but only if source policy comes first.

The campaign therefore focuses on:

- canonical source classes;
- citation and license expectations;
- checksum and archive discipline;
- unit, scheme, scale, epoch, and uncertainty semantics;
- covariance and correlation handling;
- holdout freeze rules;
- negative-result preservation.

## First-Pass Axes

### Atomic Clocks

Atomic-clock comparison campaigns are eligible only for source-policy review.
Future ingestion must record clock species, transitions, epochs, frequency
ratios or drift bounds, uncertainty budgets, covariance notes, source
locators, license terms, and holdout classification.

This axis must not become broad constants derivation. Derived constraints on
alpha or mass ratios require explicit sensitivity coefficients, assumptions,
and a separate maintainer-reviewed task.

`TASK-0311` adds the first atomic-clock-specific scaffold:

- [Atomic-Clock Residuals](./atomic-clock-residuals.md);
- [Atomic-Clock Source Candidates](../notes/atomic-clock-source-candidates.md);
- [`data/atomic_clocks/schema.md`](../../data/atomic_clocks/schema.md).

It remains source-surface work only; no rows or metrics are ingested.

### Lattice QCD

Lattice-QCD aggregated outputs are eligible only for source-policy review.
Future ingestion must record observable definitions, scheme and scale,
flavor content, aggregation source, uncertainty semantics, correlation notes,
source locators, license terms, and holdout classification.

This axis must not become cross-domain fitting before the project has a fixed
source manifest and correlation policy.

### FRB Selection-Effect Audit

CHIME/FRB remains a source-readiness and prediction-preparation lane, not a
public result or repeater-population claim. Existing artifacts pin the public
Catalog 2 table route, define a version-locked temporal split, and preserve an
exposure-only baseline as the control any later morphology model must beat.
`TASK-0910` pinned the time-resolved / full-sky exposure-map source artifact as
metadata only:
`chimefrbcat2_exposure.h5`, HDF5, approximately 206 MB, dataset DOI
`10.11570/25.0066`, Public read on the CANFAR vault, with source bytes not
redistributable in this repository.

`TASK-0930` then fetched a local license-clear copy, pinned exact identity
(`216024090` bytes, SHA-256
`cd8411f92d0ac31bd05dff47f62797638c354444de27a5c056113ca00470d514`), and
inspected the HDF5 schema. The current blocker is
`CONSTRUCTION_BLOCKED_STATIC_FULL_WINDOW_ONLY`: the file contains `/upper` and
`/lower` cumulative HEALPix maps over the full observing window, with no
timestamp dataset, interval boundary table, or per-interval exposure axis.
That Catalog 2 map remains blocked for pre-T construction. The active FRB path
therefore uses the Catalog-1 interval exposure pair instead: `TASK-0947` passed
the checksum/schema gate, and `TASK-0963` wrote
`data/radio_transients/frb_catalog1_pre_t_exposure_feature_surface.yaml` from
pre-T source coordinates and exposure counts only. It did not read repeater
labels, register predictions, or make a population claim. `TASK-0964` then
froze the exposure-only model surface without label contact. The next allowed
step is the sequenced `TASK-0965` sealed-registration pack under maintainer
approval.

## WATCHLIST Axes

These remain WATCHLIST:

- pulsar timing array public releases;
- gravitational-wave open-data catalogs;
- event-level collider data.

Those axes need separate feasibility reviews before any source manifest,
loader, or benchmark task can be proposed.

## Allowed Future Work

Allowed next steps, only after maintainer assignment:

- create a source-manifest template for atomic clocks or lattice-QCD outputs;
- write a license and citation review checklist for one axis;
- define a deterministic loader contract without ingesting real values;
- run a synthetic-only loader dry-run with fabricated rows;
- review one candidate source class and preserve blockers.
- for FRB, continue only through the already activated Catalog-1 chain
  (`TASK-0965` after the frozen `TASK-0964` surface) or through a separate
  metadata-only source scout for a future Catalog-2-compatible time-indexed
  exposure source.

## Not Allowed Yet

Do not:

- ingest atomic-clock or lattice-QCD data;
- ingest PTA, gravitational-wave, or event-level collider data;
- commit FRB exposure-map bytes or bulk derived exposure rows without explicit
  maintainer license clearance;
- treat the Catalog-1 pre-T feature surface as a repeater model, prediction
  registry, reveal result, or source of population claims;
- run a real-data benchmark or cross-domain fit;
- derive broad physical constants;
- combine fresh axes with anomaly-registry topics;
- promote claims, results, or knowledge from this scaffold;
- use discovery, explanation, or breakthrough framing.

## Recommended Next Task Shape

The safest generic follow-up is a manifest-only task for one axis. It should
list candidate primary sources, license and citation status, retrieval policy,
checksum plan, unit and uncertainty schema, and blockers. It should still add
no numerical rows.

For FRB specifically, the active next task shape is no longer generic source
scouting: it is the sequenced Catalog-1 model/contract freeze and sealed
registration pack. A future Catalog-2-compatible route would still start as a
metadata-only time-indexed exposure source scout with official source
candidates, interval semantics, sky-coordinate mapping, rights/access posture,
checksum feasibility, and an explicit `READY` / `AMBIGUOUS` / `BLOCKED`
verdict. It must not fetch bulk value-bearing bytes or construct exposure rows
without a new maintainer-reviewed task.

## What Not To Claim

- Do not say these axes are more likely to reveal scientific novelty.
- Do not imply less-saturated data is automatically better evidence.
- Do not treat source-policy readiness as benchmark readiness.
- Do not move WATCHLIST axes into active work by citing this page.
