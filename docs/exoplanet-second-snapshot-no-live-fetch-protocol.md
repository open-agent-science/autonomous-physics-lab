# Exoplanet Second-Snapshot No-Live-Fetch Protocol

**Task:** `TASK-0393`  
**Campaign:** `exoplanet_mass_radius`  
**Protocol class:** pre-reveal source and benchmark protocol  
**Status:** no live data fetched, ingested, inspected, or scored

## Purpose

This protocol defines how a future second PSCompPars snapshot may be prepared
for the Exoplanet Mass-Radius campaign without giving agents a live-fetch path
or a chance to tune hypotheses after seeing newer catalog rows.

The goal is to separate three phases:

1. pre-reveal freezing of benchmark choices;
2. maintainer-approved snapshot acquisition and checksum recording;
3. later scoring against the frozen benchmark contract.

This document does not fetch archive data, does not inspect new rows, does not
create prediction entries, and does not promote claims.

## Source Surface

The intended source family is the NASA Exoplanet Archive Planetary Systems
Composite Parameters table, using the existing repository query contract:

- source service: `https://exoplanetarchive.ipac.caltech.edu/TAP/sync`
- query file: `data/exoplanets/snapshot_plans/pscomppars_query.adql`
- first committed snapshot reference: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- baseline protocol: `docs/exoplanet-mass-radius-baseline-protocol.md`
- first residual review: `docs/reviews/exoplanet-mass-radius-residual-failure-map.md`

A future second-snapshot task may reuse the same ADQL query only after the
pre-reveal package below is frozen and reviewed. Any query change requires a
separate amendment PR before acquisition.

## Required Second-Snapshot Artifact Package

A future ingestion task must create a package that records, at minimum:

| artifact | requirement |
| --- | --- |
| source URL | exact TAP endpoint and archive page used |
| query | exact ADQL text or committed query-file SHA |
| retrieval timestamp | UTC timestamp from the maintainer-approved run |
| raw artifact path | repository path or external artifact reference for the raw response |
| normalized artifact path | repository path for the normalized snapshot, if committed |
| row count | total rows returned before exclusions |
| field list | exact selected columns |
| checksum | SHA-256 for raw and normalized artifacts |
| acquisition actor | maintainer or explicitly approved data-acquisition actor |
| no-peek attestation | statement that no benchmark tuning occurred after row inspection |

The package must not include ad hoc derived hypotheses, tuned thresholds, or
new metric choices created after viewing the second snapshot.

## No-Peek Boundary

Before any agent sees second-snapshot rows, the following must be frozen in a
reviewable pre-reveal package:

1. baseline family and any allowed comparator baselines;
2. residual hypotheses to be tested;
3. metric set;
4. eligible slices and split definitions;
5. row exclusion rules;
6. success, null, and blocker criteria;
7. output destination and review tier expectations.

Agents may read and update this protocol, the baseline protocol, the first
snapshot metadata, and first-snapshot review notes. Agents must not fetch,
ingest, browse, summarize, score, or manually inspect a newer live archive
snapshot until the maintainer explicitly approves the acquisition step.

## Frozen Benchmark Choices Before Ingestion

The second-snapshot reveal must preserve the first benchmark's conservative
shape unless an amendment PR is merged before acquisition.

### Baseline

- Primary baseline remains the frozen Chen-Kipping-style median baseline used
  by the first Exoplanet Mass-Radius benchmark.
- Alternative baselines may be listed only if the choice and parameters are
  frozen before the second snapshot is acquired.
- No baseline may be re-fit after seeing second-snapshot rows unless the
  pre-reveal package explicitly defines that as a separate diagnostic control.

### Metric Set

Allowed second-snapshot metrics are restricted to the baseline protocol's
existing metrics:

- log10-radius MAE and RMSE;
- z-score residual summaries where uncertainty support exists;
- interval-coverage diagnostics when the baseline exposes intervals;
- per-slice row counts and blocker labels;
- null-baseline comparison against the frozen constant-per-class median rule.

No new primary metric may be selected after seeing the second snapshot.

## Reveal Conditions

A future reveal is permitted only when all of the following are true:

1. the pre-reveal package exists and names all frozen benchmark choices;
2. the maintainer approves the exact source URL and query artifact;
3. the raw and normalized artifacts receive checksums before scoring;
4. the acquisition actor records retrieval timestamp and row count;
5. no benchmark metric, residual hypothesis, or eligible slice is changed after
   row inspection except through a separate amendment that marks the run
   exploratory rather than prospective.

## Outcome Classification

### Success

A second-snapshot result may be described as a bounded prospective success only
if a pre-registered residual hypothesis improves or reproduces its expected
pattern on the frozen eligible slice while clearing the frozen null-baseline and
sample-size criteria.

Success wording must stay scoped to the slice and metric. It is not a universal
planet mass-radius law, composition law, habitability signal, or discovery claim.

### Null

The outcome is `null` when the frozen residual hypothesis does not reproduce or
improve under the second snapshot, but the snapshot package, checksums, row
counts, and required fields are valid enough to score.

Null outcomes are preserved as campaign memory and should not be hidden.

### Blocker

The reveal is blocked when any of the following occurs:

- the source schema changed and required fields cannot be mapped;
- the acquisition lacks checksum or timestamp evidence;
- the query differs from the frozen query without a prior amendment;
- row counts or provenance metadata are inconsistent with the source artifact;
- required slices collapse below the pre-defined sample-size floor;
- baseline or metric choices changed after row inspection.

A blocker is a protocol outcome, not a failed scientific hypothesis.

## Maintainer Approval Requirements

Before second-snapshot acquisition, a maintainer must approve:

- the exact source URL;
- the exact query artifact or query-file commit SHA;
- who will acquire the data;
- where raw and normalized artifacts will be stored;
- checksum method;
- whether the next task is ingestion-only, scoring-only, or a combined reveal
  task.

## What This Protocol Does Not Authorize

This task and document do not authorize:

- live fetching or manual inspection of a new PSCompPars snapshot;
- ingestion of new catalog rows;
- scoring a second snapshot;
- changing the baseline after seeing new data;
- creating prediction registry entries;
- creating or promoting claims;
- modifying canonical result artifacts.

## Output Routing Summary

- task verdict: `not_applicable` — protocol-only task;
- canonical destination: review protocol documentation;
- review tier: `none`;
- Gate A status: not attempted;
- Gate B status: not attempted;
- claim impact: no claim change;
- knowledge impact: no knowledge change;
- result artifact impact: no `results/` artifacts modified.
