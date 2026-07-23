# GWTC-5.0 / O4b Source-Version Incubator

Task: `TASK-1085`
Review date: 2026-07-23
Scope: metadata and benchmark contract only

## Verdict

`HOLD_SELECTION_FUNCTION`

The official GWOSC and LVK release surface resolves catalog identity,
versioning, event semantics, rights, and API discovery. It does not yet support
an auditable O4b-only selection control: the official O4b run boundary and the
boundary stated by the O4a+O4b sensitivity README differ by two days, while
the record's generated-count and analysis-time normalization are aggregate.
No source manifest or benchmark ingestion is authorized until that conflict is
resolved by official metadata or a deterministic schema proof.

This decision does not activate a gravitational-wave campaign or authorize
numeric ingestion. No strain, posterior samples, candidate tables, event
rows, or event-level physical parameter values were downloaded or committed.
No model, statistic, residual, or scientific verdict was calculated.

## Official Source And Version Table

| Source class | Frozen identity | Release state | Role |
| --- | --- | --- | --- |
| O4b open data | [GWOSC O4b release](https://gwosc.org/O4/O4b/), dataset DOI [`10.7935/8emv-ag54`](https://doi.org/10.7935/8emv-ag54), first release 2026-05-26 | O4b observing interval is documented separately from the preceding engineering data included in the open-data release. Data are CC BY 4.0. | Run identity, detector set, official time boundary, data-quality documentation, and license. Bulk strain is out of scope. |
| GWTC-5.0 catalog documentation | [GWOSC documentation](https://gwosc.org/GWTC-5.0/), page DOI [`10.7935/bk00-6a89`](https://doi.org/10.7935/bk00-6a89), published 2026-05-26 | Catalog semantic version `GWTC-5.0`; cumulative through O4b, with revised O4a content. | Canonical release identity, inclusion/PE rules, current Stable Release mapping, and event naming. |
| Results publication | LVK DCC [`LIGO-P2600152-v6`](https://dcc.ligo.org/LIGO-P2600152-v6/public), [arXiv:2605.27225](https://arxiv.org/abs/2605.27225) | Pin the explicit DCC version, not the moving unversioned DCC alias. | Catalog definitions, search results, source-property conventions, and publication citation. |
| Methods publication | LVK DCC [`LIGO-P2600166-v6`](https://dcc.ligo.org/LIGO-P2600166-v6/public) | Submitted-publication version current at review time. | Search, validation, PE, waveform, and pipeline semantics. |
| Open-data publication | LVK DCC [`LIGO-P2600085-v8`](https://dcc.ligo.org/LIGO-P2600085-v8/public), [arXiv:2605.27090](https://arxiv.org/abs/2605.27090) | Submitted-publication version current at review time. | Data-release citation and technical context. |
| Candidate data | GWTC-5.0 Stable Release 9, Zenodo record [`10.5281/zenodo.20348004`](https://doi.org/10.5281/zenodo.20348004), modified 2026-06-15 | Zenodo page version `v2`; internal GWTC stable-release identity `9`. These are different version namespaces. | Future canonical search-summary and catalog-membership source. |
| Parameter estimation | Stable Release 9 Part 1 [`10.5281/zenodo.20348005`](https://doi.org/10.5281/zenodo.20348005) and Part 2 [`10.5281/zenodo.20348006`](https://doi.org/10.5281/zenodo.20348006), modified 2026-06-15 | Current GWOSC portal parameters are documented as deriving from Stable Release 9. | Future PE summary metadata. Posterior files remain external and prohibited for the manifest task. |
| O4 selection function | O4a+O4b sensitivity record [`10.5281/zenodo.19500064`](https://doi.org/10.5281/zenodo.19500064), version `v1` | CC BY 4.0; schema README and HDF identity are versioned. Its stated O4b start conflicts with the official GWOSC run boundary. | Candidate O4b search-sensitivity control, blocked pending boundary and normalization reconciliation. |
| Cumulative selection reference | O1-O4b sensitivity record [`10.5281/zenodo.19500052`](https://doi.org/10.5281/zenodo.19500052), version `v1` | CC BY 4.0. | Cross-run schema reference only. The later benchmark must use a pre-O4 release for development sensitivity. |
| Programmatic discovery | [GWOSC API v2](https://gwosc.org/api/), [v2 root](https://gwosc.org/api/v2/), and [OpenAPI schema](https://gwosc.org/api/v2/schema) | Read-only unauthenticated REST API with pagination and throttling. API v1 is deprecated. | Metadata discovery and cross-checking, not the canonical numeric source. |

The future manifest must pin all four independent version axes:

1. catalog release: `GWTC-5.0`;
2. GWOSC API generation: `v2`;
3. per-event version: `event_name-vN` or `event_name@catalog`;
4. Zenodo/internal stable release: Stable Release 9 and exact record DOI.

No axis may be inferred from another.

## Rights And Attribution

GWOSC states that website data are licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) and publishes a
required [acknowledgement route](https://gwosc.org/acknowledgement/). The
Zenodo candidate and sensitivity records also identify CC BY 4.0.

A future manifest must:

- identify the LIGO Scientific Collaboration, Virgo Collaboration, and KAGRA
  Collaboration as creators;
- cite the exact GWTC-5.0 results, methods, and open-data records used;
- include the GWOSC acknowledgement required at retrieval time;
- preserve the license and DOI per source artifact;
- avoid redistributing bulk strain, search archives, or posterior files in the
  repository merely because the license permits reuse.

This review follows the repository's
[fresh-data source policy](../../notes/fresh-data-source-policy.md) and does
not treat open licensing as permission to skip provenance or size controls.

## Retrieval And Checksum Policy

The later source-manifest task may retrieve metadata only.

### Zenodo artifacts

- Use version-record DOIs above, never a moving concept DOI.
- Record record id, internal stable-release label, filename, byte length,
  upstream MD5, publication/modification timestamps, and direct file URL.
- Compute SHA-256 locally for every retrieved file and retain the upstream MD5
  as a second identity check.
- Candidate and PE summary HDF5 files require a separate schema preflight
  before any row extraction.
- Posterior HDF5 files, archived search results, skymaps, strain, and the
  multi-gigabyte injection HDF5 are not manifest deliverables.

### GWOSC API

- Pin `/api/v2/schema` bytes, response headers, retrieval UTC, and SHA-256.
- Fetch catalog metadata through paginated
  `/api/v2/catalogs/GWTC-5.0/events` only in the later task.
- Preserve each raw response page and its SHA-256 before combining pages.
- Record `next`, page number, result count, HTTP status, content type, ETag,
  and Last-Modified when supplied.
- Do not use live API default parameters as the canonical numeric record;
  match them against Stable Release 9 summary artifacts.

### Documentation

Pin the exact DCC versioned PDF bytes and SHA-256. Record the GWOSC page DOI,
retrieval UTC, and body SHA-256 because documentation pages can be corrected
without a new catalog name.

## Event Identity And Version Semantics

The event key is not the display name alone. The future schema must use:

```text
event_name + event_version + catalog_name + stable_release
```

Rules:

- `event_name` follows the documented UTC timestamp convention.
- Different event versions may represent changed calibration, cleaning,
  analysis, or publication context.
- GWTC-5.0 is cumulative and supersedes earlier catalog summaries, but it must
  not overwrite their historical records.
- Revised O4a content inside GWTC-5.0 is a distinct `GWTC-4.1`-class source
  surface and is excluded from this O4b benchmark.
- Deduplicate by canonical event name only after retaining every source record
  and explicit `supersedes` relation.
- Low-latency GraceDB alerts, GCN notices, search triggers, catalog candidates,
  and PE-qualified events are separate source classes. They must not be joined
  by timestamp alone.
- Events from the engineering interval included in the O4b open-data release
  are excluded unless the future task explicitly changes the benchmark scope.

## Inclusion Classes

GWTC-5.0 uses a probability-of-astrophysical-origin catalog threshold and
event validation. Parameter estimation is provided for a stricter
false-alarm-rate subset. The candidate archive itself extends to a much looser
search-trigger threshold.

The future manifest therefore keeps these classes distinct:

| Class | Meaning | Benchmark posture |
| --- | --- | --- |
| `catalog_included_o4b` | Validated O4b candidate satisfying the catalog's `p_astro` inclusion rule. | Membership source only. |
| `pe_qualified_o4b` | Catalog candidate with PE made available under the documented FAR rule. | Eligible for the proposed parameter benchmark after schema review. |
| `search_archive_candidate` | Trigger present in the broader candidate-data archive. | Excluded from benchmark rows unless a new task defines a background model. |
| `legacy_confident` / `legacy_marginal` | Historical release labels from older GWTC surfaces. | Preserve as source metadata; never translate automatically to the GWTC-5.0 classes. |
| `low_latency_alert` | Preliminary alert identity. | Link-only provenance; never a catalog-membership substitute. |

Missing PE is a defined selection class, not a missing-at-random value. It must
not be imputed.

## Parameter And Interval Semantics

- Preserve detector-frame and source-frame parameter names as separate fields.
- Do not derive source-frame values with an APL-chosen cosmology.
- The proposed primary benchmark uses a detector-frame parameter to avoid
  adding a cosmology conversion to the main score.
- GWOSC displays 90% credible intervals from a default PE result, but the PE
  release contains multiple samplers, waveform configurations, and mixed
  samples. Store the credible level, point statistic, sampler, waveform,
  pipeline configuration, and default/mixed designation with every future
  value.
- Stable Release 9 includes PE corrections relative to the earlier release.
  Stable Release 6 and 9 values must never be mixed.
- A new PE revision after Stable Release 9 requires a new manifest decision;
  it cannot silently replace frozen benchmark inputs.

## One Candidate Benchmark Question

**Question:** Can a detector-frame chirp-mass population baseline frozen using
only pre-O4 catalog data retain calibrated posterior-predictive performance on
the PE-qualified O4b catalog after transport through the O4b search
sensitivity, without refitting?

This is distinct from an LVK/GWOSC catalog summary because it is a one-shot
temporal generalization test. The model family, parameterization, inclusion
rule, score, and threshold are frozen from pre-O4 inputs; O4b is used only as a
reveal surface. It is not a new population fit and cannot support anomaly or
new-physics wording. The question is parked until the selection-function
blocker is cleared.

## Selection-Function Control

The O4a+O4b sensitivity package documents simulated-CBC parameters, draw
densities, injection time, search-specific FAR and `p_astro`, and mixture
weights. However, its README states an O4b start of GPS `1396969218`, whereas
the [official GWOSC O4b release](https://gwosc.org/O4/O4b/) states GPS
`1396796418`. The difference is `172800` seconds, or exactly two days. Both
sources state the same O4b end, GPS `1422118818`. The sensitivity artifact also
reports aggregate generated-count and analysis-time normalization for O4a and
O4b rather than an explicit O4b-only denominator.

This is an unresolved source-semantic conflict, not a value to repair locally.
The route remains blocked until an official LVK/GWOSC correction or a
deterministic schema derivation proves the intended file coverage and the
O4b-only denominator, analysis time, and mixture-weight normalization.

Before any event value is read, a later deterministic preflight must prove:

1. the authoritative O4b start and the reason for the two-day discrepancy;
2. the O4b time filter excludes O4a and engineering intervals;
3. the generated-count denominator and analysis-time normalization are
   correct for the O4b subset;
4. mixture weights remain valid after the time split;
5. the injection detection rule matches the event PE-qualification FAR rule
   across the same search-pipeline set;
6. source/detector-frame transformations and draw-density factors match the
   frozen model;
7. the effective injection sample size clears a predeclared floor.

Any failed item stops benchmark ingestion. The existence of a sensitivity file
alone is not evidence that the control was implemented correctly.

## Row Cap And Future Schema

Hard caps for a later manifest:

- at most 100 unique pre-O4 development events from a pre-O4 release;
- at most 200 unique O4b catalog candidates;
- at most 300 unique event identities in the combined contract;
- zero strain rows, posterior samples, skymaps, search-trigger rows, or
  sensitivity-injection rows committed to git.

Future event fields:

```text
event_name
event_version
catalog_name
catalog_version
stable_release
observing_run
source_class
catalog_inclusion_rule
pe_qualification_rule
search_pipeline_set
default_search_configuration
default_pe_configuration
sampler
waveform_model
parameter_name
parameter_frame
point_statistic
credible_level
value_unit
source_record_doi
source_filename
source_md5
source_sha256
retrieved_at_utc
supersedes
duplicate_of
license
attribution
```

Numeric value and interval fields may be added only by a later approved
ingestion task.

## No-Peek Boundary

The model-building agent may read only a frozen pre-O4 catalog release,
contemporaneous pre-O4 sensitivity products, and the benchmark contract. It
must not inspect:

- GWTC-4.x or GWTC-5.0 event parameters;
- O4a or O4b PE summaries or posterior samples;
- O4 population-paper conclusions;
- event-list plots, rankings, or parameter distributions;
- selection-adjusted O4 metrics.

Freeze the model digest, parameter target, transforms, inclusion rule,
selection implementation, nulls, controls, score, and pass/fail threshold
before a separate reveal agent retrieves Stable Release 9 rows. O4a is neither
development nor holdout data. Revised earlier-run rows copied into GWTC-5.0
must not replace the pre-O4 development release.

## Nulls, Controls, And Stop Conditions

Primary null: no population shift beyond the pre-O4 baseline after applying
the documented O4b selection function.

Controls:

- a pre-O4 chronological replay validates the pipeline without O4 contact;
- a predeclared stricter search-threshold sensitivity check tests dependence
  on marginal catalog membership;
- a missing-PE ledger verifies that the scored surface is the
  PE-qualified subset rather than all catalog members.

Stop before ingestion if:

- Stable Release 9 cannot be matched consistently across candidate, PE, and
  API records;
- the official O4b boundary and sensitivity README boundary remain
  inconsistent;
- O4b sensitivity normalization cannot be reconstructed independently;
- event-version or duplicate rules remain ambiguous;
- the benchmark model or threshold was influenced by O4 values;
- fewer than the predeclared effective sample floor remains;
- the proposed work becomes a refit, catalog summary, or anomaly search.

## Limitations

This packet establishes source readiness only. The candidate question may have
limited power, depends on PE and search-selection assumptions, and excludes
catalog members without PE. A retrospective time split is weaker than a
prospectively registered prediction. Stable Release 9 is already public, so
role separation and immutable pre-reveal artifacts are essential. The
two-day boundary conflict and aggregate sensitivity normalization are active
blockers, not documentation caveats.

## Output Routing

- Canonical destination: this incubator review packet.
- Source manifest: not authorized until the selection-function blocker clears.
- Dataset impact: none.
- Review tier: none; no `RESULT-*`, `PRED-*`, `CLAIM-*`, or `KNOW-*` artifact
  is produced.
- Gate A / Gate B: not attempted and not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Campaign activation: maintainer / Scientific Director decision required.
- Publication blocker: source-manifest construction and numeric ingestion
  remain blocked until the O4b boundary conflict, exact artifact checksums,
  schema reconciliation, O4b-only selection normalization, and a frozen
  no-peek benchmark package are reviewed.

Source readiness is not a gravitational-wave population result, anomaly,
cosmology constraint, prediction success, or new-physics claim.
