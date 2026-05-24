# Fresh-Data Source Policy

## Purpose

This note defines source policy and ingestion prerequisites for future
non-saturated physics data axes. It is a planning artifact only.

`TASK-0309` does not ingest data, run analyses, add benchmark metrics, promote
claims, or move broad constants, anomalies, PTA, gravitational-wave, or
event-level collider topics out of WATCHLIST.

Use this policy with:

- [Fresh-Data Intake Protocol](../fresh-data-intake-protocol.md)
- [Fresh Physics Data Axes Campaign](../campaigns/fresh-physics-data-axes.md)
- [Blind Holdout Benchmark Protocol](../blind-holdout-benchmark-protocol.md)
- [Numerical Accuracy Policy](../numerical-accuracy-policy.md)
- [Research Quality Gate](../research-quality-gate.md)
- [Claim Promotion Policy](../claim-promotion-policy.md)

## Scope For The First Pass

The first pass is intentionally narrow:

- atomic-clock comparison campaigns;
- lattice-QCD aggregated outputs.

The following axes remain WATCHLIST until separate feasibility reviews exist:

- pulsar timing array public releases;
- gravitational-wave open-data catalogs;
- event-level collider data.

## General Ingestion Preconditions

A future ingestion task must define all of the following before adding rows,
arrays, or derived metrics:

1. **Fixed source list.** Exact publications, official release pages, archive
   records, or collaboration artifacts must be listed before retrieval.
2. **Frozen retrieval date.** The task must record when each source was
   accessed and which source version is frozen.
3. **Checksum policy.** Downloaded files must have checksums or an explicit
   archive policy when checksums are unavailable.
4. **License and citation review.** Reuse terms, required citations, and any
   redistribution limitations must be recorded before committing artifacts.
5. **Unit semantics.** Units, schemes, scales, epochs, reference transitions,
   or fiducial assumptions must be machine-readable.
6. **Uncertainty fields.** Statistical, systematic, correlated, asymmetric,
   and derived uncertainties must be represented without silently collapsing
   them.
7. **Correlation handling.** Known covariance must be preserved. Unknown
   correlation structure must be labelled as blocking or limiting.
8. **Holdout split.** The source freeze must state which entries are fit inputs
   and which later entries are reserved for evaluation.
9. **Deterministic loader.** Ingestion must use reviewed code with fixed inputs
   and reproducible outputs. LLM summaries are not datasets.
10. **Negative-result path.** The task must define how failed baselines,
    unusable covariance, or source-license blockers are preserved.

## Atomic-Clock Comparison Campaigns

### Accepted Source Classes

Atomic-clock source policy may use:

- peer-reviewed measurement papers for frequency ratios or drift bounds;
- official lab or collaboration release material linked from a peer-reviewed
  source;
- archived supplementary tables with stable locators;
- canonical evaluations only when the evaluation explicitly documents source
  provenance and combination rules.

### Required Fields

Future rows must record:

- clock species and transition;
- measured quantity, unit, epoch or campaign interval, and reference
  transition;
- central value and uncertainty components;
- systematic budget and known covariance or correlation notes;
- source citation, DOI or archive locator, retrieval date, and checksum or
  archive policy;
- license or reuse notes;
- holdout classification.

### Risk Notes

Atomic-clock data can be deceptively easy to overframe as broad constants
derivation. Future tasks must avoid that shortcut.

Specific risks:

- correlated lab systematics across repeated campaigns;
- derived constraints on constants that depend on sensitivity coefficients and
  model assumptions;
- epoch and campaign-duration mismatches;
- silently mixing frequency-ratio measurements with drift constraints;
- using review plots or summary tables without the primary source trail.

### Stop Conditions

Stop before ingestion when:

- only a secondary summary is available;
- sensitivity coefficients or reference transitions are ambiguous;
- correlated systematics are mentioned but not recoverable;
- the task asks for broad constants fitting rather than source policy or a
  narrow benchmark;
- source reuse terms are unclear.

## Lattice-QCD Aggregated Outputs

### Accepted Source Classes

Lattice-QCD source policy may use:

- FLAG-style canonical reviews or averages;
- peer-reviewed collaboration outputs;
- official collaboration repositories or archived supplementary artifacts;
- HEPData, Zenodo, or equivalent archives when linked to the primary work.

### Required Fields

Future rows or arrays must record:

- observable or matrix element name;
- scheme, scale, flavor content, and normalization convention;
- central value and uncertainty components;
- covariance or documented correlation limitations;
- aggregation source and whether the value is an average or a single
  collaboration result;
- source citation, locator, retrieval date, and checksum or archive policy;
- license or reuse notes;
- holdout classification.

### Risk Notes

Lattice-QCD outputs are not automatically independent just because they appear
as separate rows in an evaluation.

Specific risks:

- scheme and scale mismatches;
- shared ensembles or correlated systematics across collaborations;
- treating evaluated averages as raw independent measurements;
- combining matrix elements with PDG or nuclear values without a declared
  correlation model;
- hiding model choices inside derived quantities.

### Stop Conditions

Stop before ingestion when:

- the observable definition is scheme- or scale-ambiguous;
- an average lacks enough provenance for uncertainty interpretation;
- covariance is required but unavailable;
- the task asks for cross-domain fitting before a source manifest exists;
- a derived value would blur the boundary between data ingestion and theory
  interpretation.

## WATCHLIST Axes

The following axes are not in scope for ingestion under `TASK-0309`:

- **PTA releases:** require separate review of timing-residual products,
  noise models, covariance, and public-data reuse terms.
- **Gravitational-wave catalogs:** require separate review of catalog
  versions, posterior samples, selection effects, and detector-network
  assumptions.
- **Event-level collider data:** require separate review of event formats,
  analysis preservation, detector simulation boundaries, and licensing.

Future tasks may cite this policy, but they must not treat WATCHLIST axes as
active datasets without a maintainer-approved feasibility task.

## Unacceptable Source Shortcuts

Do not:

- scrape central values from review plots when primary tables exist;
- use LLM-recalled values;
- treat a PDF screenshot as a dataset;
- mix incompatible units, schemes, or epochs;
- discard covariance to simplify a loader;
- fit values that were not frozen before candidate selection;
- describe a source-policy task as evidence for scientific novelty.

## Future Task Checklist

A future ingestion task should include:

- source manifest path;
- frozen retrieval date;
- checksum or archive policy;
- deterministic loader path;
- unit and uncertainty schema;
- correlation policy;
- holdout split;
- validation commands;
- limitations and negative-result preservation plan.

If any item is missing, the task should remain planning-only.
