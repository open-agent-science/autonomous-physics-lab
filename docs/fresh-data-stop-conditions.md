# Fresh-Data Stop Conditions

## Purpose

Fresh-data tasks should preserve failed source and row-curation attempts as
searchable scientific memory instead of rewriting them as ad hoc prose. This
vocabulary gives agents shared names for source blockers, extraction blockers,
row-class blockers, and admissibility blockers.

A stop condition is not a claim and not a result. It is a reviewable reason to
halt, split scope, preserve negative evidence, or keep rows out of benchmark
datasets until a later task clears the blocker.

Use this vocabulary with:

- [Fresh-Data Intake Protocol](fresh-data-intake-protocol.md)
- [Fresh-Data Source Policy](notes/fresh-data-source-policy.md)
- [Source Manifest Minimum Schema](source-manifest-minimum-schema.md)
- [Research Quality Gate](research-quality-gate.md)

## Stop-Condition Table

| Stop condition | Meaning | Halt when | Allowed follow-up | May rows be committed? |
| --- | --- | --- | --- | --- |
| `SOURCE_PAYWALLED_NO_TABLE` | The needed table or supporting artifact is not accessible from the reviewed source path. | The task cannot verify values from a primary table or open supplementary artifact. | Try an open archive, maintainer-provided artifact, institutional access, or alternate source. | No value-bearing rows. Metadata-only blocker notes are allowed. |
| `SOURCE_ARTIFACT_NOT_REDISTRIBUTABLE` | The artifact can be inspected but cannot be stored in the repository under its reuse terms. | Review requires a committed raw artifact but license or publisher terms forbid redistribution. | Store locator/checksum metadata only, request license review, or use an allowed archive copy. | Only metadata rows or blocker notes unless a task explicitly authorizes a non-redistributed validation path. |
| `FIGURE_DIGITIZATION_REQUIRED` | Values exist only in a figure and need deterministic digitisation. | A source has plot points but no table or extraction artifact. | Run WebPlotDigitizer-class extraction with calibration, raw export, uncertainty notes, and review. | No benchmark rows until digitisation artifacts and reviewer notes exist. |
| `COVARIANCE_NOT_SEPARABLE` | Shared uncertainties or correlations are mentioned but cannot be represented or separated. | Treating rows as independent would hide shared systematics or double-count evidence. | Locate covariance matrix, use documented source combination rule, split axes, or keep as blocked. | No production benchmark rows on the affected axis. Blocker-only rows may be preserved. |
| `DIRECT_ROWS_NOT_PRESENT` | The source surface has no direct measurements for the requested row class. | Available values are summaries, formulas, curves, or derived constraints rather than direct rows. | Choose another source, request maintainer waiver for a calibration-consistency benchmark, or record a negative source review. | No direct-measurement rows. Calibration or blocker artifacts may be committed if clearly labelled. |
| `CALIBRATION_DERIVED_ONLY` | Values are generated from a calibration curve, empirical relation, sizing formula, or model-derived transform. | The task asks for direct measurements but the source exposes only calibration-derived values. | Re-scope to calibration-consistency, find primary observations, or keep direct benchmark blocked. | Yes only as calibration-derived rows outside direct-measurement benchmark axes. |
| `SOURCE_ARTIFACT_VERSION_DRIFT` | Two source versions disagree on values, uncertainties, campaign windows, or row identity. | A preprint, version of record, supplement, archive, or API snapshot cannot be reconciled. | Pin both versions, write a version-drift review, choose a canonical source under maintainer review. | No value-bearing rows from the drifting fields until resolved. |
| `UNCERTAINTY_SEMANTICS_MISSING` | Required uncertainty meaning, confidence level, asymmetry, or component split is absent or ambiguous. | A row cannot state whether uncertainty is statistical, systematic, total, asymmetric, bounded, or correlated. | Locate source notes, add an uncertainty-semantics review, or exclude the row with a blocker. | Rows may be committed only as excluded/blocker rows, not benchmark rows. |
| `ROW_CLASS_AMBIGUOUS` | A value cannot be reliably classified as direct, derived, calibration-derived, model-derived, aggregate, or excluded. | Row class affects admissibility and the source text does not disambiguate it. | Add row-class review, split source classes, or escalate to maintainer decision. | No benchmark rows until row class is resolved. |
| `LICENSE_REVIEW_REQUIRED` | Reuse, citation, redistribution, or storage rights are not yet reviewed. | The task would commit artifacts or derived extracts before license posture is known. | Complete license review, use metadata-only locator, or select a redistributable source. | No raw artifacts or value-bearing extracts unless the task has explicit license clearance. |

## Additional Shared Codes

These codes are optional but recommended when they make a blocker more precise:

| Stop condition | Meaning | Halt when | Allowed follow-up | May rows be committed? |
| --- | --- | --- | --- | --- |
| `SOURCE_MANIFEST_INCOMPLETE` | Required locator, citation, checksum, live-fetch policy, row-class, or license metadata is missing. | A row would lack a reviewable source trail. | Complete the manifest or source artifact package. | No benchmark rows. |
| `PRIMARY_SOURCE_TRAIL_MISSING` | A review or secondary table gives numbers but hides the primary source path. | The task cannot verify where values originally came from. | Trace primary papers, archives, or collaboration artifacts. | No benchmark rows. |
| `LIVE_FETCH_NOT_AUTHORIZED` | The task would need an external API or download but its scope does not permit live retrieval. | Validation or extraction depends on network state outside a pinned artifact. | Create a source-artifact or snapshot task with retrieval timestamp and checksum. | No new value-bearing rows. |
| `UNIT_OR_SCALE_AMBIGUOUS` | Units, epochs, schemes, scales, or normalization conventions cannot be reviewed. | Combining rows would silently mix incompatible quantities. | Add unit-semantics review or split axes. | No benchmark rows on the ambiguous axis. |
| `INSUFFICIENT_CLEAN_ROWS` | After exclusions, too few admissible rows remain for the task's minimum row-count gate. | A benchmark or seed requires a declared row threshold and the clean subset misses it. | Preserve negative review, search alternate source, or request a scoped waiver. | Excluded/blocker rows may be committed; benchmark rows are not enough to unblock. |

## How To Record A Stop Condition

Use stop conditions in review notes, source manifests, extraction ledgers,
blocker notes, and task YAML status explanations. A useful blocker record
should include:

- stop condition code;
- source id or artifact id;
- exact source location if known;
- lifecycle stage where the halt occurred;
- attempted method;
- allowed follow-up;
- whether any rows were committed and why;
- claim-impact statement.

If multiple blockers apply, list the narrowest blocker first and add broader
context after it. For example, a figure-only source with inaccessible SI might
record `SOURCE_PAYWALLED_NO_TABLE` first and `FIGURE_DIGITIZATION_REQUIRED` as
the allowed follow-up if the plotted points remain usable.

## Existing Blocker Mapping

| Existing campaign wording | Shared stop condition |
| --- | --- |
| Quantum TASK-0283 direct measurement rows absent; qd seeds are calibration-derived. | `DIRECT_ROWS_NOT_PRESENT`; `CALIBRATION_DERIVED_ONLY` |
| Quantum figure points require WebPlotDigitizer-class extraction before rows enter `qd-*.yaml`. | `FIGURE_DIGITIZATION_REQUIRED` |
| Atomic Beloy 2021 shared campaign systematics not separable. | `COVARIANCE_NOT_SEPARABLE` |
| Atomic Beloy 2021 arXiv and version-of-record values may disagree. | `SOURCE_ARTIFACT_VERSION_DRIFT` |
| Atomic SI or covariance section not open-access. | `SOURCE_PAYWALLED_NO_TABLE`; `COVARIANCE_NOT_SEPARABLE` |
| Exoplanet PSCompPars mass provenance requires source-specific review. | `ROW_CLASS_AMBIGUOUS`; `PRIMARY_SOURCE_TRAIL_MISSING` |
| Exoplanet snapshot rows excluded for missing mass/radius fields. | `DIRECT_ROWS_NOT_PRESENT` |
| Any source artifact with unclear reuse terms. | `LICENSE_REVIEW_REQUIRED`; `SOURCE_ARTIFACT_NOT_REDISTRIBUTABLE` |

## Scope Limits

This vocabulary does not add data, authorize artifact redistribution, relax
uncertainty requirements, run benchmarks, or promote claims. It only standardizes
how blocked source and row-curation work is recorded for later review.
