# Published-Source and Reusable-Dataset Standard

**Task:** `TASK-0543`
**Status:** cross-campaign standard (unifies existing fresh-data docs)
**Scope:** how APL turns *published* sources into *reusable, provenance-rich,
citable* datasets — and what may and may not be committed.

## Why This Exists

APL's data layer is the load-bearing cross-campaign bottleneck. The standards
needed already exist but are **scattered** across:

- [Fresh-Data Intake Protocol](fresh-data-intake-protocol.md) — workflow gates;
- [Source-Manifest Minimum Schema](source-manifest-minimum-schema.md) — manifest fields;
- [Fresh-Data Stop Conditions](fresh-data-stop-conditions.md) — when to halt;
- [Fresh-Data Readiness Matrix](fresh-data-readiness-matrix.md) — per-campaign status;
- per-campaign intakes (e.g. `quantum-direct-source-artifact-intake.md`,
  `exoplanet-second-snapshot-no-live-fetch-protocol.md`).

This standard **unifies and references** them and adds the two things none of
them state explicitly: the **published ≠ redistributable** rule and the
**reusable-dataset publication standard**, plus a **`blocker_type` vocabulary**
that routes a stuck source to the correct unblock lane.

This document does not fetch data, does not commit third-party copyrighted
material, and does not relax any existing protocol.

## Core Principle

> APL agents do not create scientific data. They find published sources, verify
> provenance / licensing / extraction feasibility, and only then prepare a
> source artifact or a curated-dataset task. New measurement rows are added only
> by a bounded row-curation task, never automatically.

## Admissible Source Classes

| Class | Examples | Default handling |
| --- | --- | --- |
| Open licensed database | Materials Project (CC BY 4.0), JARVIS-DFT (NIST), OQMD, NASA Exoplanet Archive | Rows committable with attribution; pin a snapshot. |
| Open repository dataset | Zenodo / Figshare records with a stated open license | Rows committable per the record's license. |
| Author-deposited preprint | arXiv preprint PDF under an article-specific license | Metadata and expected checksum by default; commit PDF bytes only with a compatible license or explicit permission. |
| Open-access journal (verify per article) | APS public-access, PMC OA | Facts extractable; verify per-article reuse before committing tables. |
| Subscription / copyrighted | ACS, Nature, AIP version-of-record | Metadata-only; rows need an open mirror, permission, or maintainer-held artifact. |
| Model/theory output | DFT-only or fitted curves | Admissible only as explicitly excluded/labelled context, never as measured rows. |

## Published ≠ Redistributable

A source being *published* (readable, citable) does **not** mean its content is
*redistributable* (committable to this repo).

Publicly accessible source files are also not automatically worth vendoring.
If an upstream artifact is already stable and retrievable from its DOI, archive,
or source URL, APL's default is metadata-only: store the locator, expected
checksum, retrieval instructions, and provenance, not another copy of the file.
Commit raw upstream files only when they are license-clean, materially needed
for reproducibility, and explicitly approved for repository storage.

**Generally committable** (subject to the source's license/ToS):

- citation, DOI, URL, access date, version/query;
- SHA-256 checksums and source locators;
- our own extraction ledger and curated schema;
- APL-authored normalized/curated dataset rows when source license, ToS,
  attribution, and row provenance allow redistribution;
- individual factual numeric values (a mass, radius, band gap) — facts are not
  copyrightable — when license/ToS allow and with attribution;
- author-deposited preprint PDFs only when the exact artifact has a compatible
  license or explicit permission recorded in a machine-readable marker.

**Generally NOT committable**:

- publisher PDFs, page scans, or typeset table images;
- copyrighted figures or full supplementary files;
- arXiv or other preprint PDFs when the available license only grants the
  archive itself a distribution right rather than a clear third-party
  redistribution right;
- raw upstream source files that are already public and stable elsewhere,
  unless the task records a clear reproducibility need, compatible license, and
  maintainer approval for committing the bytes;
- bulk extraction that triggers a database's terms-of-service or the EU
  sui-generis database right.

Guardrails:

- prefer **openly licensed** sources so the actual rows are committable;
- always record `license_status` and attribution per source;
- for metadata-only source artifacts, preserve DOI/URL, expected SHA-256, and a
  local fetch+verify command instead of vendoring the artifact bytes;
- distinguish source artifacts from APL datasets: do not copy public upstream
  files just because they are accessible, but do preserve curated benchmark
  rows when they are license-clean and scientifically useful;
- if a PDF artifact is explicitly redistributable and must be committed, add a
  sibling `<artifact>.license.yaml` marker with `redistribution_status` set to
  `cc_by_4_0`, `cc0`, `public_domain`, or `explicit_permission_recorded`, plus
  a non-empty `permission_evidence` field; repository validation guards this;
- never commit secrets, API keys, tokens, cookies, or private files;
- this is engineering guidance, not legal advice — for borderline closed
  sources, get explicit permission or stay metadata-only.

## Blocker Type Vocabulary

Every source candidate or blocked data surface is tagged with exactly one
`blocker_type`, which routes it to an unblock lane:

| `blocker_type` | Meaning | Routes to |
| --- | --- | --- |
| `T1_access` | Source identified, but the needed copy/version-of-record is access- or license-restricted. | Maintainer-provided source artifact (acquisition lane). |
| `T2_extraction_tool` | Data lives in figures/scans; needs a deterministic extraction/digitization run. | Extraction-runner lane. |
| `T3_coverage` | Source admissible, but the curated slice is too small/sparse to score. | Coverage-expansion task. |
| `T4_snapshot_approval` | Open source, but needs a maintainer-approved, checksum-pinned snapshot fetch. | Acquisition/source-pinning lane. |
| `none` | Source is admissible and pinnable now. | Row-curation task. |

The acquisition/pinning and extraction lanes are defined by `TASK-0545`
(`docs/source-acquisition-lane.md`).

## Reusable-Dataset Publication Standard

An APL dataset may be called a **reusable dataset** (and is worth a Zenodo DOI
or external citation) only when it carries all of:

- `dataset_id` and `version` (semantic version), with a `changelog`;
- a machine-readable schema (fields, units, types);
- a `source_manifest` with per-source license, version, checksum, citation;
- per-row provenance class: `direct_measurement | derived | digitized |
  model_only | excluded | metadata_only`;
- uncertainty semantics (per-row or per-method; or explicit `absent`);
- license + attribution for the dataset itself (e.g. CC BY) and for each source;
- validator tests covering the schema and provenance separation;
- a `README` with limitations and intended use;
- an explicit **no-claim boundary**: a dataset is not a scientific claim, a
  benchmark result, or a model; promotion remains a separate maintainer task.

Datasets that meet this bar are APL's second public output class (alongside
results): provenance-rich benchmark datasets others can verify, cite, and reuse.

## Current Repository Boundary

For the current private-repository phase, APL keeps reusable dataset candidates
inside the main repository:

- small curated seed datasets;
- schemas, source manifests, loaders, tests, examples, and benchmark configs;
- citation and reuse metadata when a dataset reaches a stable internal version.

Separate public dataset repositories are deferred until a dataset is genuinely
reusable: stable version, clear license and attribution, validator coverage,
README/limitations, citation/DOI plan, and enough size or usefulness for other
projects. Moving a dataset to `open-agent-science` or any public dataset repo
requires a separate maintainer-approved publication task.

The current public organization boundary is
`https://github.com/open-agent-science`, and citation planning may use the
maintainer identity:

- Roman Hladun — ORCID: `https://orcid.org/0009-0004-4853-5212`

This identity does not replace per-source attribution. For example, a Materials
Project-derived dataset must still preserve Materials Project CC BY attribution
and citation text for every reusable artifact.

## What This Standard Does Not Authorize

- live fetching or autonomous crawling inside agent task PRs;
- committing copyrighted PDFs, tables, or figures;
- adding measurement rows without a bounded row-curation task;
- moving a dataset into an external repository or minting a DOI without a
  separate maintainer-approved publication task;
- auto-unblocking a benchmark task from a source verdict;
- promoting any claim, knowledge entry, or canonical result.

## Relationship To Other Documents

- [Fresh-Data Intake Protocol](fresh-data-intake-protocol.md) — the step-by-step
  workflow this standard sits above.
- [Source-Manifest Minimum Schema](source-manifest-minimum-schema.md) — the
  per-source manifest fields a reusable dataset must satisfy.
- [Fresh-Data Stop Conditions](fresh-data-stop-conditions.md) — when to halt
  ingestion.
- [Fresh-Data Readiness Matrix](fresh-data-readiness-matrix.md) — per-campaign
  data-gate status.
- [Result Promotion Protocol](result-promotion-protocol.md) — routing of any
  downstream result; datasets are not results.
- `TASK-0545` (`docs/source-acquisition-lane.md`) — the acquisition/pinning and
  extraction lanes the `blocker_type` values route to.

## Output Routing Summary

- Task verdict: `not_applicable` (standard/infrastructure).
- Canonical destination: this standard plus a pointer in the fresh-data intake
  protocol.
- Review tier: `none`. Claim/knowledge impact: none.
- Limitations: this is policy, not code; it does not lint or fetch. Compliance
  is enforced by per-task preflight and maintainer review.
