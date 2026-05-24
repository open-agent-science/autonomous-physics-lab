# Atomic-Clock Real-Row Readiness Gate

**Task:** `TASK-0332`  
**Domain:** `atomic_clock_residuals`  
**Gate verdict:** `READY_FOR_SOURCE_SPECIFIC_REVIEW`  
**Real-row seed status:** `NOT_READY_FOR_REAL_ROWS`  
**Evidence class:** metadata-only readiness review

## Scope

This gate reviews the current Atomic-Clock Residuals source surface before any
future task adds real direct frequency-ratio rows or derived constraints. It
uses the campaign scaffold, fresh-data source policy, source manifest template,
schema sketch, source-candidate note, synthetic loader, and existing
source-class review artifacts.

No real frequency ratios, clock values, drift values, sensitivity coefficients,
benchmark metrics, prediction registry entries, claims, or canonical results
are added.

## Inputs

| Input | Role in gate |
| --- | --- |
| `docs/campaigns/atomic-clock-residuals.md` | Campaign boundary and no-claim policy. |
| `docs/notes/fresh-data-source-policy.md` | Repository-wide source prerequisites. |
| `docs/notes/atomic-clock-source-candidates.md` | Candidate source classes and stop conditions. |
| `data/atomic_clocks/source_manifest_template.yaml` | Metadata-only source manifest template and source-family requirements. |
| `data/atomic_clocks/schema.md` | Planning row schema and direct-vs-derived separation. |
| `data/atomic_clocks/synthetic_loader_dry_run.yaml` | Fabricated fixture for loader mechanics only. |
| `physics_lab/engines/atomic_clock_residuals.py` | Synthetic-only loader implementation. |
| `docs/reviews/atomic-clock-source-manifest-template-review.md` | `SOURCE_TEMPLATE_READY` review. |
| `docs/reviews/atomic-clock-synthetic-loader-dry-run.md` | `SYNTHETIC_LOADER_READY` review. |
| `docs/reviews/atomic-clock-derived-constraint-source-review.md` | Metadata-only derived-constraint source-class review. |

## Method

The gate checks whether current committed artifacts satisfy the minimum
preconditions for three increasingly strong states:

1. `READY_FOR_SOURCE_SPECIFIC_REVIEW`: future tasks may inspect a concrete
   source artifact without copying values.
2. `READY_FOR_FIRST_ROW_SEED`: a future task may add a first real direct row or
   derived constraint.
3. `NOT_READY_FOR_REAL_ROWS`: real rows remain blocked.

The review treats missing source artifacts as blockers, not as reasons to infer
values from secondary summaries, plots, or memory.

## Evidence Inventory

Current ready evidence:

- source classes are separated in the manifest template;
- all manifest candidate families are marked `metadata_only_no_values`;
- global stop conditions block missing uncertainty, covariance, source,
  license, and archive information;
- the schema sketch distinguishes direct measurements, derived constraints,
  review summaries, and synthetic rows;
- the synthetic loader validates fabricated rows and rejects real-measurement
  flags in that fixture;
- the derived-constraint source class is documented as admissible only with
  recoverable input measurements, sensitivity coefficients, interval semantics,
  covariance notes, model assumptions, and license/citation status.

Missing evidence for real rows:

- no concrete source manifest entry with a stable locator is filled in;
- no source artifact, supplement, checksum, or archive record is frozen;
- no retrieval date is attached to a real atomic-clock source;
- no source-specific license/citation review exists for a real artifact;
- no real direct frequency-ratio row has reviewed transition labels, epoch,
  uncertainty semantics, covariance notes, and holdout boundary;
- no real derived constraint has reviewed input measurement sources,
  sensitivity-coefficient source, model assumptions, and interval semantics;
- no deterministic real-row loader path exists.

## Gate Decision

`READY_FOR_SOURCE_SPECIFIC_REVIEW`

The campaign has enough scaffolding to inspect a concrete primary paper,
supplement, official release, or evaluation source in a future source-specific
review. It does not yet have enough provenance, archive, uncertainty,
covariance, or loader evidence to add the first real row.

`READY_FOR_FIRST_ROW_SEED` is explicitly denied until a future source-specific
task satisfies the blockers below.

## Direct Measurement Row Blockers

Direct measurement rows remain blocked until a future task records all of the
following for a concrete source:

| Blocker | Required resolution |
| --- | --- |
| Source locator missing | Stable DOI, official release page, archive record, or primary paper plus supplement. |
| Retrieval and archive missing | Retrieval date plus checksum, archived copy policy, or explicit reason a checksum is unavailable. |
| License/citation unreviewed | Reuse terms, citation requirements, and commit policy for any source artifact. |
| Transition semantics unreviewed | Clock species, isotope when applicable, transition label, reference transition, and ratio partner. |
| Unit semantics unreviewed | Dimensionless ratio, absolute frequency, residual form, or other declared observable form. |
| Epoch/campaign semantics missing | Measurement date, campaign interval, or explicit interval limitation. |
| Uncertainty semantics incomplete | Total, statistical, systematic, confidence/coverage, and asymmetric handling when applicable. |
| Covariance/correlation unresolved | Shared-systematic, repeated-campaign, lab, or covariance-group notes; unknown covariance must be a limitation or blocker. |
| Holdout boundary missing | Source-manifest-only, train/validation/holdout, or no-peek freeze boundary before model selection. |
| Loader not real-row capable | Deterministic validation for non-synthetic rows that rejects missing source, uncertainty, covariance, and holdout fields. |

Stop if the value is available only from a review plot, screenshot, secondary
summary, or mixed table that cannot split direct rows from derived constraints.

## Derived Constraint Blockers

Derived constraints remain blocked until a future task records all direct-row
blockers that apply plus these additional requirements:

| Blocker | Required resolution |
| --- | --- |
| Input measurement chain hidden | Explicit source list or row ids for all direct measurements entering the constraint. |
| Sensitivity coefficients missing | Source, transition labels, coefficient values, assumptions, and citation or table locator. |
| Interval semantics missing | Start/end dates, campaign duration, elapsed-time convention, or explicit interval limitation. |
| Model assumptions hidden | Constants varied, constants fixed, linearization assumptions, and whether multiple constants are fit together. |
| Quantity and units ambiguous | Quantity constrained, unit semantics, and whether the value is a bound, estimate, slope, or fitted coefficient. |
| Constraint covariance unresolved | Coefficient correlations, shared measurement systematics, or explicit limitation when unrecoverable. |
| Direct-vs-derived flags absent | Machine-readable row class that prevents treating derived constraints as independent direct measurements. |

Stop if a source quotes a constants-variation bound without recoverable input
measurements and sensitivity assumptions.

## Minimum Accepted Artifact Set For A Future Real-Row Seed

A future row-seed PR should include, at minimum:

- filled source manifest entry for exactly scoped source artifact(s);
- source-specific review document with admissibility verdict and blockers;
- retrieval date and checksum or archive policy;
- license and citation review;
- row-class label: direct measurement, derived constraint, review summary, or
  synthetic;
- transition labels, ratio partners, units, and epoch/campaign semantics;
- uncertainty semantics and covariance/correlation notes;
- holdout or reveal boundary set before any model selection;
- deterministic loader or schema validation for the real-row class;
- negative-result preservation path for source-access, license, covariance, or
  uncertainty blockers;
- explicit no-claim/no-benchmark boundary until a later maintainer-reviewed
  benchmark task exists.

## Metrics

No physics metrics were run. The only metric-like outcome is the gate state:

- source-specific review readiness: pass;
- first real-row seed readiness: fail;
- benchmark readiness: fail;
- claim-promotion readiness: fail.

## Limitations

- This gate does not inspect a concrete real source artifact.
- It does not decide which primary paper, supplement, or official release
  should be used first.
- It does not add or validate a real-row loader.
- It does not rank direct measurement rows against derived constraints.
- It does not create a follow-up task; existing READY atomic-clock tasks can
  continue the source-surface work.

## Verdict

`READY_FOR_SOURCE_SPECIFIC_REVIEW`

Atomic Clock Residuals may proceed to a future source-specific review, but not
to real-row ingestion. The first real atomic-clock row remains blocked until a
concrete source artifact, source review, checksum/archive plan, row-class
label, uncertainty semantics, covariance notes, holdout/reveal boundary, and
real-row validation path are present.
