# Atomic-Clock Source Manifest Template Review

**Task:** `TASK-0327`  
**Manifest:** `data/atomic_clocks/source_manifest_template.yaml`  
**Campaign:** `atomic_clock_residuals`  
**Evidence class:** metadata-only source-manifest scaffold

## Scope

This review records a value-free source manifest template for the
Atomic-Clock Residuals campaign. It prepares provenance and admissibility
fields for future source review, but it does not ingest frequency ratios,
drift bounds, constants constraints, benchmark rows, prediction registry
entries, claims, or knowledge artifacts.

## Manifest Structure

The template separates four source families:

| Source family | Row class | Intended use |
| --- | --- | --- |
| `ACLOCK-SRC-CLASS-001` | direct frequency-ratio measurement | Primary direct measurement rows after source review. |
| `ACLOCK-SRC-CLASS-002` | repeated comparison campaign | Repeated direct comparisons with epoch and shared-systematic notes. |
| `ACLOCK-SRC-CLASS-003` | drift bound or constants constraint | Derived constraints only, never mixed with direct measurements. |
| `ACLOCK-SRC-CLASS-004` | evaluation or review summary | Review-summary-only until source lists and combination rules are recoverable. |

Every candidate source family is explicitly marked
`metadata_only_no_values`. All source locator, DOI, archive, retrieval,
checksum, uncertainty, covariance, and license fields remain placeholders for
future source-review tasks.

## Required Source Fields

Future ingestion tasks must preserve:

- source locator, release or publication date, retrieval date, and archive or
  checksum plan;
- direct-vs-derived row class;
- transition labels, ratio partners, units, epoch or campaign interval, and
  uncertainty semantics;
- covariance, correlation, shared-systematic, or repeat-group notes when
  available;
- source license and citation notes;
- holdout or reveal boundary before any model selection.

## Stop Conditions

The manifest stops future ingestion when a source:

- hides primary rows;
- mixes direct measurements and derived constraints without flags;
- omits uncertainty semantics;
- mentions covariance or shared systematics without recoverable notes;
- lacks a retrieval date, checksum, or archive policy;
- has unclear license or reuse terms;
- is being used for constants-drift fitting before source review.

## Boundary

No real atomic-clock values are recorded. No benchmark is run. No claim is
promoted. The manifest is only a review surface for later source-specific
tasks.

## Verdict

`SOURCE_TEMPLATE_READY`

The Atomic-Clock Residuals campaign now has a metadata-only source manifest
template suitable for future source review. The campaign remains pre-ingestion:
real rows, derived constraints, and constants-drift analysis stay blocked
until a later task reviews a concrete source and explicitly preserves
provenance, uncertainty, and holdout semantics.
