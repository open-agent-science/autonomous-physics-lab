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
The CHIME/FRB Catalog 2 selection-effect audit is also near-active as a
metadata/source gate: the catalog table locator and exposure-only baseline
exist, the T-truncated split is specified, and the time-resolved exposure-map
artifact has been checksum-pinned and inspected. The blocker is now sharper:
that HDF5 artifact is a static cumulative full-window map with no time axis, so
it cannot support leakage-safe pre-T exposure construction. The next allowed
FRB step is an official time-indexed source scout, not construction from the
blocked map.

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

CHIME/FRB Catalog 2 is a near-active source-readiness lane, not a public result
or prediction campaign. Existing artifacts pin the public Catalog 2 table route,
define a version-locked temporal split, and preserve an exposure-only baseline
as the control any later morphology model must beat. `TASK-0910` pinned the
time-resolved / full-sky exposure-map source artifact as metadata only:
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
Until an official time-indexed exposure or operational source is pinned, do not
construct truncated exposure rows, fit morphology, freeze predictions, or claim
repeater classification ability.

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
- for FRB Catalog 2 only, scout an official time-indexed exposure or
  operational/sensitivity source before proposing any numeric truncated-exposure
  construction.

## Not Allowed Yet

Do not:

- ingest atomic-clock or lattice-QCD data;
- ingest PTA, gravitational-wave, or event-level collider data;
- commit FRB exposure-map bytes or bulk derived exposure rows without explicit
  maintainer license clearance;
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

For FRB Catalog 2 specifically, the next task shape is a metadata-only
time-indexed exposure source scout: official source candidates, interval
semantics, sky-coordinate mapping, rights/access posture, checksum feasibility,
and an explicit `READY` / `AMBIGUOUS` / `BLOCKED` verdict. It must not fetch
bulk value-bearing bytes or construct exposure rows.

## What Not To Claim

- Do not say these axes are more likely to reveal scientific novelty.
- Do not imply less-saturated data is automatically better evidence.
- Do not treat source-policy readiness as benchmark readiness.
- Do not move WATCHLIST axes into active work by citing this page.
