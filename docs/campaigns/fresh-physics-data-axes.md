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

No dataset has been ingested. No baseline has been run. No claim, result, or
knowledge entry is promoted.

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

### Lattice QCD

Lattice-QCD aggregated outputs are eligible only for source-policy review.
Future ingestion must record observable definitions, scheme and scale,
flavor content, aggregation source, uncertainty semantics, correlation notes,
source locators, license terms, and holdout classification.

This axis must not become cross-domain fitting before the project has a fixed
source manifest and correlation policy.

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

## Not Allowed Yet

Do not:

- ingest atomic-clock or lattice-QCD data;
- ingest PTA, gravitational-wave, or event-level collider data;
- run a real-data benchmark or cross-domain fit;
- derive broad physical constants;
- combine fresh axes with anomaly-registry topics;
- promote claims, results, or knowledge from this scaffold;
- use discovery, explanation, or breakthrough framing.

## Recommended Next Task Shape

The safest follow-up is a manifest-only task for one axis. It should list
candidate primary sources, license and citation status, retrieval policy,
checksum plan, unit and uncertainty schema, and blockers. It should still add
no numerical rows.

## What Not To Claim

- Do not say these axes are more likely to reveal new physics.
- Do not imply less-saturated data is automatically better evidence.
- Do not treat source-policy readiness as benchmark readiness.
- Do not move WATCHLIST axes into active work by citing this page.

