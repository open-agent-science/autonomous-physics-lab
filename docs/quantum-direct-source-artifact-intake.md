# Quantum Direct Source Artifact Intake Path

**Task:** `TASK-0356`
**Campaign:** Quantum Size Effects
**Status:** reference document (no measurement values; no benchmark scored)
**Created:** 2026-05-24

## Purpose

This document defines the end-to-end intake path for maintainer-provided or
open quantum-dot source files before any `qd-*.yaml` measurement rows are
created. It covers directory layout, filename convention, checksum procedure,
required metadata fields, evidence criteria for each row type, a curator
acceptance/rejection checklist, and handoff instructions to the row-curation
task.

It is upstream of future row-curation tasks. Historical `TASK-0336` is now
blocker memory for the archived Jasieniak route, not a current executor target.
Completing this checklist does not by itself unblock `TASK-0225`, `TASK-0293`,
archived `TASK-0336`, or any correction-search pilot; it records the conditions
a source artifact must meet before a new row task may proceed.

---

## 1. Local Artifact Directory and Filename Convention

### 1.1 Directory

All source artifact packages for the Quantum Size Effects campaign are stored
under:

```
data/quantum_dots/source_artifacts/
```

Each source gets its own subdirectory named after the `source_id` registered in
`data/quantum_dots/source_manifest.yaml`:

```
data/quantum_dots/source_artifacts/<source_id>/
```

**Example:**

```
data/quantum_dots/source_artifacts/jasieniak-2011-acs-nano-band-edge/
data/quantum_dots/source_artifacts/hens-moreels-2012-rsc-open-table-candidate/
```

### 1.2 Filename Convention for Source Files

When a maintainer supplies or a curator retrieves a physical source file (PDF,
CSV, TSV, or equivalent), name it using the pattern:

```
<author>-<year>-<material>-<property>.<ext>
```

Where:

- `<author>` — first-author surname, lowercase, ASCII only (e.g. `jasieniak`)
- `<year>` — four-digit publication year (e.g. `2011`)
- `<material>` — canonical material abbreviation, lowercase (e.g. `cdse`,
  `pbs`, `multi` for multi-material sources)
- `<property>` — property kind abbreviation: `absorption`, `emission`,
  `bandgap`, or `band-edge`
- `<ext>` — `pdf`, `csv`, `tsv`, or `xlsx`

**Examples:**

```
jasieniak-2011-multi-band-edge.pdf
hens-moreels-2012-pbs-absorption.pdf
yu-2003-cdse-absorption.csv
```

Do not use vague names such as `paper.pdf`, `table.csv`, or `data.xlsx`.
Prefer the upstream filename or a locator-derived name when the source ships a
persistent filename (e.g. `nn201681s_si_001.pdf`).

### 1.3 Associated Metadata File

Each artifact subdirectory must contain a `README.md` that records, at minimum:

- source locator (DOI, URL, or maintainer-supplied path)
- retrieval date (ISO-8601, e.g. `2026-05-24`)
- expected upstream filename (the publisher filename before renaming)
- SHA-256 checksum of the retrieved file (or `PENDING` if not yet retrieved)
- archival status: `doi_pinned`, `url_archived`, or `maintainer_supplied`
- redistribution decision: `metadata_only` or `file_committed_with_permission`
- table or figure identifiers to verify before row curation
- accepted evidence class: `table_derived`, `digitization_required`, or
  `blocked`
- current blocker, if any

The Jasieniak 2011 package at
`data/quantum_dots/source_artifacts/jasieniak-2011/README.md` is the canonical
example of a `METADATA_ONLY_BLOCKER` entry.

---

## 2. Checksum Command and Metadata Fields

### 2.1 Checksum Command

Compute the SHA-256 checksum of the retrieved file before committing any
artifact or using it as the basis for row curation:

```bash
sha256sum <filename>
```

Record the full hex digest in the artifact `README.md` under `sha256:`.

**Example:**

```bash
sha256sum jasieniak-2011-multi-band-edge.pdf
# output: a3f7b2c1...  jasieniak-2011-multi-band-edge.pdf
```

If the file cannot be retrieved (access-blocked or not yet supplied by the
maintainer), record `checksum_sha256: PENDING` and keep the source manifest
entry's `checksum_policy` as `doi_pinned` until the file is available.

Cross-platform Python alternative:

```bash
python3 -c "import hashlib, pathlib, sys; p=pathlib.Path(sys.argv[1]); print(hashlib.sha256(p.read_bytes()).hexdigest())" <path>
```

### 2.2 Required Metadata Fields

Every source artifact package must record the following thirteen fields in the
subdirectory `README.md` (and optionally mirrored to `source_manifest.yaml`
when a new `checksum_sha256` field is added):

| Field | Description |
|---|---|
| `source_id` | Must match the `source_id` in `source_manifest.yaml` |
| `title` | Paper or dataset title as it appears in the publication |
| `authors` | Author list as a single string (last, first; semicolon-separated) |
| `year` | Four-digit publication year |
| `doi` | DOI or equivalent persistent identifier |
| `access_path` | URL or maintainer-supplied file path used for retrieval |
| `retrieval_date` | ISO-8601 date when the artifact was accessed (e.g. `2026-05-24`) |
| `checksum_sha256` | Hex digest from `sha256sum`, or `PENDING` |
| `license` | Reuse and redistribution terms as stated in the source or publisher policy |
| `artifact_type` | `pdf`, `csv`, `tsv`, `xlsx`, or `metadata_only` |
| `property_kind` | `absorption_peak_eV`, `emission_peak_eV`, `bandgap_eV`, or `band_edge` |
| `material_family` | Comma-separated list of materials covered (e.g. `CdSe, PbS`) |
| `row_type_expected` | `table_derived`, `digitization_required`, or `blocked` |

All thirteen fields are required. A package that is missing any field must not
be used as a source for `qd-*.yaml` row curation.

---

## 3. Evidence Sufficiency for Row Types

Three row types are recognized in this campaign. A curator must identify the
correct row type for each data section of a source before committing any
artifact or creating any `qd-*.yaml` entries. A single paper may contain
sections with different row types; catalogue them separately.

### 3.1 Direct Table Rows (`table_derived`)

A row may be classified `table_derived` when the source provides an explicit
numeric table in the main text or in publicly available Supporting Information
with all of the following:

- **Column headers** that identify at minimum the size axis (diameter or
  radius in nm) and the property axis (energy in eV or wavelength in nm)
- **Row identifiers** — each measurement point appears as a distinct row,
  not as a continuous curve or fitted line
- **Stated uncertainty values** — either per-row uncertainty columns or an
  explicit measurement uncertainty in the methods section that applies to
  all table rows

When these conditions are met, Step 1 of
`docs/quantum-direct-measurement-digitization-protocol.md` alone is sufficient:
the curator transcribes values from the printed table, records the table
reference in `source_table_ref`, and does not need to run a WebPlotDigitizer
pass.

Rows derived directly from a printed table must not use calibration polynomial
values, even if the same paper provides a sizing equation. The table values and
the polynomial values are separate provenance classes.

### 3.2 Digitized Figure Rows (`digitization_required`)

A row may be classified `digitization_required` when the source contains a
scatter plot of discrete measurement points that cannot be found in any printed
table in the main text or publicly accessible Supporting Information.

The full digitization workflow in
`docs/quantum-direct-measurement-digitization-protocol.md` (Steps 1–6) must be
followed:

1. Confirm no equivalent printed table exists.
2. Run a WebPlotDigitizer-class extraction on the figure using a deterministic
   tool with axis calibration.
3. Assign per-point provenance fields (Step 3 of the protocol).
4. Cross-check digitized coordinates against any published calibration formula
   (Step 4 of the protocol).
5. Commit the digitization artifact under
   `data/quantum_dots/digitization/<source_id>/`.
6. Build the `qd-*.yaml` file only after Steps 1–5 are complete.

An LLM agent that does not have access to a WebPlotDigitizer-class tool must
not estimate figure coordinates by eye. The row-level work must wait for a
curator who can run the tool, or for a maintainer waiver with explicitly
relaxed precision.

### 3.3 Blocked Calibration-Polynomial Rows (`blocked`)

A row is classified `blocked` when its energy or size value is, or would be,
derived from a published sizing polynomial, calibration curve, or effective-mass
approximation formula evaluated at a chosen diameter — even if the original
measurement data that produced the polynomial is plausible or the polynomial is
widely cited.

Calibration-polynomial rows cannot become direct rows without independent
primary evidence. The reasons are:

- the polynomial is a fit to an original dataset, not the dataset itself;
- evaluating the polynomial at a chosen size creates a synthetic value, not a
  measured one;
- two `qd-*.yaml` entries with identical `source_id` but one table-derived and
  one polynomial-derived cannot be distinguished after the fact without
  per-row provenance metadata;
- the TASK-0283 readiness gate already rejected the existing
  `qd-0001` and `qd-0002` seeds because they are calibration-derived.

The only unblock path for a currently `blocked` source is access to the
primary dataset that underlies the polynomial — either as a printed table or
as a figure from which a deterministic digitization pass can be run.

Calibration-polynomial sources may support a separate weaker
`calibration_curve_consistency` benchmark only after an explicit
maintainer-approved scope task (see `TASK-0326` and `TASK-0335`). They must
not unblock the direct measurement-versus-model baseline (`TASK-0225`).

---

## 4. Curator Acceptance/Rejection Checklist

A curator must complete every item in this numbered checklist before creating
any `qd-*.yaml` rows from a source artifact. An unchecked item is a blocker;
the source artifact package may be committed as `METADATA_ONLY_BLOCKER`, but
no row curation may proceed until all items are checked.

```
[ ] 1.  Source artifact file (or metadata-only stub) committed to
        data/quantum_dots/source_artifacts/<source_id>/.

[ ] 2.  Checksum recorded in the artifact README.md under sha256:. If the
        file is not yet retrieved, mark checksum_sha256: PENDING and keep the
        package as METADATA_ONLY_BLOCKER.

[ ] 3.  Retrieval date (ISO-8601) and access path (URL or maintainer-supplied
        path) documented in the artifact README.md.

[ ] 4.  License and reuse terms confirmed. Default posture is metadata_only:
        commit locator, checksum, and extraction notes only — not the publisher
        PDF or full table — unless a maintainer explicitly confirms that the
        license and repository policy allow redistribution.

[ ] 5.  Property kind identified: absorption_peak_eV, emission_peak_eV,
        bandgap_eV, or band_edge. A single source artifact package must not
        mix property kinds under one row-curation task.

[ ] 6.  Material family identified: list all canonical material symbols
        covered (e.g. CdSe, PbS, CdTe, PbSe, InP). Core-shell or confounded
        compositions must be noted separately and may require exclusion.

[ ] 7.  Row type confirmed for each data section of the source:
        - table_derived: explicit printed table with column headers, row
          identifiers, and uncertainty values;
        - digitization_required: scatter-plot figure with discrete points,
          no equivalent table, requiring a WebPlotDigitizer-class pass;
        - blocked: values are calibration-polynomial outputs, not direct
          measurements.

[ ] 8.  Uncertainty fields identified in the source. Record whether
        uncertainty is per-row (preferred), per-method, or absent. If absent,
        the curator must decide whether the rows may still be committed as
        included or whether they enter with inclusion_status: excluded and an
        explicit exclusion_reason.

[ ] 9.  Size and diameter units confirmed. Record whether the source uses
        diameter_nm or radius_nm, whether uncertainty on the size axis is
        stated, and whether any unit conversion is required. Document the
        conversion in the artifact README.md.

[ ] 10. Direct versus calibration-derived status confirmed per data section.
        A table section and a figure section of the same paper may have
        different row types and must be catalogued separately.

[ ] 11. Schema compatibility verified. Spot-check the intended row fields
        against physics_lab/schemas/quantum_dot_size_effect.schema.json:
        - required fields: entry_id, material, property_kind, value_eV,
          source_id, inclusion_status;
        - size field: diameter_nm XOR radius_nm (not both);
        - inclusion_status: included or excluded;
        - exclusion_reason required when inclusion_status is excluded.

[ ] 12. Handoff task created or historical blocker referenced. See Section 5.
```

---

## 5. Handoff to a New Row-Curation Task

Once a curator has completed all twelve checklist items and at least one data
section is classified `table_derived` or `digitization_required` (with the
required artifact committed), the intake path hands off to a row-curation task
as follows.

### 5.1 If the source is Jasieniak 2011 (band-edge)

Treat `TASK-0336` as historical blocker memory, not as a current executor task.
That task was superseded after the Jasieniak route remained metadata-only. A
curator who completes this intake checklist for Jasieniak 2011 should create a
new bounded row-curation task or proposal referencing the reviewed artifact,
the historical `TASK-0334`/`TASK-0336` context, and the exact source-license
decision.

A future Jasieniak row-curation task must not be opened until at least one of
the following exists:

- a checksum-pinned `nn201681s_si_001.pdf` or equivalent official SI copy with
  maintainer confirmation that the file may be committed or that metadata-only
  extraction is sufficient;
- a non-copyrighted table extraction from the SI, with table identifiers, row
  locators, units, uncertainty semantics, and source checksum metadata;
- a deterministic WebPlotDigitizer-class package for the relevant figure,
  including axis calibration, extracted points, tool/version notes, and
  coordinate uncertainty.

### 5.2 If the source is a new candidate (PMC, arXiv, open database, or ZnSe/Toufanian)

Create a new row-curation task (following `docs/agent-task-protocol.md`) with:

- a `TASK-XXXX` yaml file in `tasks/` referencing this intake document
- `input.related_objects` listing:
  - the artifact path under `data/quantum_dots/source_artifacts/<source_id>/`
  - `data/quantum_dots/source_manifest.yaml`
  - `docs/quantum-direct-measurement-digitization-protocol.md`
  - `physics_lab/schemas/quantum_dot_size_effect.schema.json`
- requirements matching the accepted evidence class (`table_derived` or
  `digitization_required`) confirmed in checklist item 7
- `accepted_outputs` listing the expected `qd-*.yaml` file and any test updates

The new task must not attempt to curate rows from sources still classified
`blocked` or with unchecked checklist items.

For the current ZnSe/Toufanian route, complete `TASK-0870` first. Row curation
is not authorized until that task records an admissible source/license verdict.

### 5.3 Ranked candidate sources for the next row-curation task

Per the TASK-0347 open-direct-table source triage
(`docs/reviews/quantum-open-direct-table-source-triage.md`), the ranked
candidate order for the next row-curation task is:

1. PMC open-access reprints of NIH-funded papers with a printed
   (size, energy) table for CdSe or PbS
2. arXiv condensed-matter preprints with a CSV or LaTeX tabular supplement
3. Hens-Moreels 2012 (RSC review), if SI access can be confirmed public
4. NanoMine / Materials Project / NOMAD open databases (with per-record
   license verification)

A curator who exhausts candidates 1 and 2 without finding a clean candidate
should escalate to the maintainer with the list of attempted sources rather
than relaxing the digitization protocol.

---

## 6. Explicit Restrictions

The following are out of scope for this task and for any task that cites this
intake document as its sole authority:

- **Do not copy measurement values.** This document does not authorize
  transcribing energy or size values from any publication into `qd-*.yaml`.
- **Do not estimate figure coordinates.** Coordinate estimation by eye — by
  an LLM agent or any other method — is explicitly forbidden by
  `docs/quantum-direct-measurement-digitization-protocol.md`.
- **Do not run benchmarks.** The quantum baseline residual benchmark
  (`TASK-0225`) requires direct-measurement rows that have passed the TASK-0283
  readiness gate. This intake document does not satisfy that gate.
- **Do not unblock TASK-0225.** `TASK-0225` remains `BLOCKED` for
  measurement-versus-model benchmarking until direct-measurement rows pass the
  readiness gate independently.
- **Do not unblock archived TASK-0226.** The historical autonomous sandbox
  pilot route has been superseded. Any future pilot requires a new
  maintainer-approved task after source/license and negative-memory gates.
- **Do not commit publisher PDFs, figures, or full tables** unless the
  maintainer explicitly confirms the license and repository policy allow
  redistribution.
- **Do not treat calibration-polynomial outputs as direct rows.** The existing
  `qd-0001` and `qd-0002` seeds are calibration-derived and are explicitly
  excluded from the measurement benchmark for this reason.
- **Do not add synthesis protocols, device claims, or biomedical content** to
  any artifact committed under this intake path.

---

## Relationship to Other Documents

- `data/quantum_dots/source_manifest.yaml` — registry of accepted and excluded
  source families; every source that enters this intake path must have an entry
  here
- `docs/quantum-direct-measurement-digitization-protocol.md` — the mandatory
  Step 1–6 workflow for `digitization_required` rows
- `docs/campaigns/quantum-size-effects.md` — campaign orientation and current
  task posture
- `docs/reviews/quantum-jasieniak-2011-source-artifact-package.md` — the
  TASK-0334 blocker package; the canonical example of a `METADATA_ONLY_BLOCKER`
  outcome
- `docs/reviews/quantum-open-direct-table-source-triage.md` — the TASK-0347
  ranked candidate list for alternative open sources
- `physics_lab/schemas/quantum_dot_size_effect.schema.json` — schema that all
  future `qd-*.yaml` files must satisfy
- `TASK-0336` —
  historical blocker memory for the archived Jasieniak row-curation route; do
  not treat it as a current executor task
