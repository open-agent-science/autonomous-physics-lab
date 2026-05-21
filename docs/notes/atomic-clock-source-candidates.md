# Atomic-Clock Source Candidates And Stop Conditions

## Purpose

This note lists candidate source classes and review questions for a future
atomic-clock residuals campaign. It is a planning artifact only: no data are
ingested, no values are copied, and no benchmark metrics are produced.

Use with:

- [Atomic-Clock Residuals Campaign](../campaigns/atomic-clock-residuals.md)
- [Fresh-Data Source Policy](./fresh-data-source-policy.md)
- [Atomic-Clock Schema Sketch](../../data/atomic_clocks/schema.md)

## Candidate Source Classes

| Source class | Possible use | Required review before ingestion |
| --- | --- | --- |
| Primary frequency-ratio measurement papers | Direct measurement rows. | DOI or stable archive, transition labels, epoch, uncertainty budget, license/citation notes. |
| Official supplementary tables linked from primary papers | Source manifest or row extraction. | Checksum or archive policy, table semantics, unit conventions, provenance back to primary paper. |
| National metrology institute or collaboration release pages | Source locator and provenance trail. | Stable versioning, retrieval date, whether values duplicate a paper or evaluation. |
| Evaluation or review tables | Review-summary rows only. | Combination rules, source list, covariance or correlation notes, whether central values are derived. |
| Drift-bound papers | Derived constraint rows. | Sensitivity coefficients, interval semantics, model assumptions, direct input measurements. |
| Synthetic rows | Loader and schema dry-run only. | Must be clearly fabricated and excluded from benchmark or claim paths. |

## Candidate Observable Families

Future tasks may review, but not ingest under `TASK-0311`, sources for:

- optical frequency ratios between named clock transitions;
- microwave-to-optical comparisons when reference semantics are explicit;
- repeated campaign measurements with date or interval metadata;
- drift constraints over declared intervals;
- systematic budget components tied to a direct measurement row.

## Direct, Derived, And Review-Summary Boundaries

Direct measurement rows should preserve the source measurement as closely as
possible. Derived constraints should be separate rows with explicit sensitivity
coefficients and assumptions. Review-summary values should not be used as raw
measurements unless the future task can recover the source list, combination
rules, uncertainty treatment, and correlation notes.

If a source mixes these classes in one table, future ingestion should either
split them explicitly or stop.

## Provenance Checklist

Before any future row is added, the task should answer:

- What exact source or archive is frozen?
- What is the retrieval date?
- Is there a checksum or an archive policy when checksums are unavailable?
- What license and citation requirements apply?
- Which transition, isotope, ratio partner, and epoch are represented?
- Are uncertainty components and covariance or correlation notes recoverable?
- Is the row direct, derived, review-summary, or synthetic?
- Is the row assigned to train, validation, holdout, or source-manifest-only
  status before any model selection?

## Stop Conditions

Stop and preserve a negative source-review result when:

- values are available only from a plot, screenshot, or informal summary;
- the source does not distinguish direct measurements from derived constants
  constraints;
- sensitivity coefficients are required but not traceable;
- covariance or shared-systematic notes are mentioned but cannot be recovered;
- epoch or campaign interval is ambiguous;
- source licensing or reuse terms are unclear;
- a task asks to fit broad constants drift before the source surface is
  reviewed.

## Safe Follow-Up Tasks

Good next tasks after this scaffold:

- create a value-free source manifest template for one atomic-clock source
  class;
- review one primary paper plus supplement for admissibility without copying
  values;
- create a synthetic-only loader dry-run with fabricated rows;
- define a no-peek freeze package for future clock-ratio updates;
- audit whether derived drift constraints can be represented without mixing
  them with direct measurements.

Bad next tasks:

- scrape values from review plots;
- add a frequency-ratio table without source checksums or archive policy;
- fit constants drift;
- combine atomic-clock rows with anomaly-registry or particle-mass topics;
- create prediction registry entries before a source manifest exists.
