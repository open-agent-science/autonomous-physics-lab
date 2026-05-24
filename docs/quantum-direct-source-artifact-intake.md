# Quantum Direct Source Artifact Intake

**Task:** `TASK-0356`
**Campaign:** Quantum Size Effects
**Status:** intake protocol only

## Purpose

This protocol defines how a maintainer, human curator, or agent should package
a quantum-dot direct-measurement source artifact before any `qd-*.yaml` rows are
created.

The Quantum Size Effects campaign is blocked on measurement-grade direct rows.
Existing row seeds are calibration-derived and are not enough to unblock the
measurement-versus-model baseline. This intake path makes future source files
reviewable without inviting agents to copy values from memory, estimate figure
coordinates, or treat calibration polynomials as measurements.

This task does not add measurement values, run a benchmark, unblock
`TASK-0225`, or promote any claim.

## Expected Directory

Use one source-scoped directory under:

```text
data/quantum_dots/source_artifacts/<source_id>/
```

`<source_id>` must either already exist in
`data/quantum_dots/source_manifest.yaml` or be proposed in the same future
source-review task. Use the manifest `source_id` exactly so row curation can
join artifacts, source metadata, and dataset rows without a second mapping.

Example:

```text
data/quantum_dots/source_artifacts/jasieniak-2011-acs-nano-band-edge/
```

## Filename Convention

Future artifact packages should use stable, descriptive names. Do not commit
publisher PDFs, figures, or tables unless redistribution is explicitly allowed
by license and maintainer policy.

Recommended layout:

```text
data/quantum_dots/source_artifacts/<source_id>/
  README.md
  provenance.yaml
  raw/
    <official-upstream-filename>        # optional; only if redistributable
    <official-upstream-filename>.sha256 # optional checksum sidecar
  extracted/
    <table-or-section-id>.csv           # optional non-copyrighted extraction
    extraction_log.md
  review/
    curator_checklist.md
```

If the raw artifact cannot be committed, keep `raw/` absent and record the
locator, retrieval timestamp, checksum, and non-redistribution reason in
`provenance.yaml` and `README.md`.

Do not use vague names such as `paper.pdf`, `table.csv`, or `data.xlsx`.
Prefer the upstream filename or a locator-derived name, for example:

```text
nn201681s_si_001.pdf
nn201681s_si_001.pdf.sha256
supporting-information-table-s1.csv
figure-2-axis-calibration.csv
```

## Checksum Command

Record SHA-256 for every value-bearing artifact that is committed or used for
row extraction.

Cross-platform Python:

```bash
python3 -c "import hashlib, pathlib, sys; p=pathlib.Path(sys.argv[1]); print(hashlib.sha256(p.read_bytes()).hexdigest())" <path>
```

Windows PowerShell:

```powershell
Get-FileHash -Algorithm SHA256 <path>
```

Unix-like shell:

```bash
sha256sum <path>
```

Checksum scope must be explicit. State whether the digest covers the raw PDF,
the raw CSV, a normalized extraction, or a metadata-only locator record. A
checksum without scope is not enough to curate rows.

## Required Metadata Fields

Every source artifact package should record these fields in `provenance.yaml`
or in the package `README.md` until a schema is added:

```yaml
source_id: <manifest source_id>
task_id: <TASK-XXXX that packaged or reviewed the artifact>
source_title: <publication or dataset title>
doi_or_persistent_locator: <DOI, arXiv id, PMC id, archive URL, or database id>
source_url: <stable source locator>
retrieved_at_utc: <ISO-8601 timestamp or NOT_RETRIEVED>
retrieved_by: <human or agent id>
artifact_kind: published_si_pdf | published_table | author_csv | database_snapshot | digitization_export | metadata_only
artifact_path: <repo path or NOT_COMMITTED>
artifact_sha256: <64 hex chars or NOT_COMMITTED>
checksum_scope: <exact byte scope, e.g. official SI PDF as downloaded>
redistribution_status: file_committed_with_permission | metadata_only | nonredistributable | unknown_pending_maintainer
license_note: <source-specific reuse note>
property_kinds_expected:
  - absorption_peak_eV
  - emission_peak_eV
  - bandgap_eV
materials_expected:
  - <material labels exactly as reviewed>
size_axis_expected: diameter_nm | radius_nm | mixed_requires_row_review
row_evidence_class: direct_table | digitized_figure | calibration_polynomial | model_only | blocked
curation_decision: ready_for_row_curation | needs_digitization | blocked | rejected
decision_reason: <short reason>
```

Do not invent missing metadata. Use `unknown_pending_review` or
`NOT_RETRIEVED` when the source has not been inspected.

## Evidence Classes

### Direct Table Rows

Direct table rows are sufficient for row curation only when all of the
following are true:

- the table is from a registered source or a source being registered in the
  same review task;
- the table contains discrete size and property values, not only fit
  parameters;
- units, material labels, property semantics, and size-axis convention are
  explicit;
- the source artifact or extraction is checksum-pinned or has a documented
  metadata-only locator policy;
- redistribution and citation constraints are recorded;
- each future row can cite a table, row, section, or stable locator.

A table-derived row still needs row-level review before entering `qd-*.yaml`.
This intake step only decides whether the artifact is acceptable input for a
future row-curation task.

### Digitized Figure Rows

Figure-derived rows are acceptable only through
`docs/quantum-direct-measurement-digitization-protocol.md`.

Minimum artifact evidence:

- deterministic digitization tool name and version;
- figure and panel reference;
- axis-calibration anchors;
- extracted point export;
- coordinate uncertainty or exclusion note for each point;
- link to the source artifact checksum or locator;
- no interpolation along fitted curves;
- no LLM-estimated graph coordinates.

If any of these are missing, classify the package as `needs_digitization` or
`blocked`, not `ready_for_row_curation`.

### Blocked Calibration-Polynomial Rows

Calibration-polynomial sources are blocked for direct-measurement row curation
when the only available values are:

- polynomial outputs;
- sizing-curve values;
- fitted curve samples;
- back-computed values from formula parameters;
- aggregate means without original discrete points.

These sources may support a separate calibration-consistency benchmark only
after an explicit maintainer-approved scope task. They must not unblock the
direct measurement-versus-model baseline.

## Curator Checklist

Before any `qd-*.yaml` row is created, answer each item and preserve negative
answers in the source review.

- [ ] Is the source registered in `data/quantum_dots/source_manifest.yaml`, or
      is a metadata-only manifest update included in the same future task?
- [ ] Is live external fetching avoided by the curation script?
- [ ] Is the exact source locator recorded?
- [ ] Is the retrieval date recorded, or is the package explicitly
      `metadata_only`?
- [ ] Is the SHA-256 checksum recorded for every value-bearing artifact used?
- [ ] Is the checksum scope unambiguous?
- [ ] Are license and redistribution limits recorded?
- [ ] Is the source table, figure, panel, or database record locator specific
      enough for review?
- [ ] Are absorption, emission, and bandgap semantics kept separate?
- [ ] Is the size axis explicitly `diameter_nm` or `radius_nm`?
- [ ] Are materials and composition labels preserved from the source?
- [ ] Are uncertainty semantics recorded, or is their absence explicit?
- [ ] Are calibration-derived, model-only, and direct-measurement values
      separated?
- [ ] If figure-derived, is the digitization artifact complete under the
      digitization protocol?
- [ ] Are there at least six candidate included rows after exclusions, or is a
      blocker decision recorded?
- [ ] Does the package avoid synthesis, fabrication, device-performance, and
      biomedical claims?

Decision outcomes:

- `ready_for_row_curation` - a future row-curation task may create
  `qd-*.yaml` rows from this package.
- `needs_digitization` - source appears usable, but a deterministic
  digitization package is missing.
- `blocked` - access, license, checksum, table, or provenance evidence is
  insufficient.
- `rejected` - the source is calibration-only, model-only, confounded, or
  otherwise unsuitable for direct rows.

## Handoff To Row Curation

Use this intake result to route the next task:

- If `row_evidence_class: direct_table` and
  `curation_decision: ready_for_row_curation`, hand off to `TASK-0336` for
  Jasieniak-style band-edge rows or create a new row-curation task for the
  specific source and property kind.
- If `row_evidence_class: digitized_figure`, hand off first to a
  digitization-artifact task that follows
  `docs/quantum-direct-measurement-digitization-protocol.md`.
- If `row_evidence_class: calibration_polynomial`, keep `TASK-0225` blocked
  and use only a future maintainer-approved calibration-consistency task.
- If the source is `blocked` or `rejected`, preserve the review note and do
  not create dataset rows.

Any row-curation task must still run schema validation and the row-level
readiness gate. This intake protocol is necessary evidence, not sufficient
approval for a benchmark.

## What This Task Does Not Do

- It does not copy measurement values.
- It does not estimate figure coordinates.
- It does not fetch live sources.
- It does not commit raw publisher files.
- It does not edit `qd-*.yaml` datasets.
- It does not run `TASK-0225` or any quantum benchmark.
- It does not promote a source, result, claim, or knowledge entry.

## Limitations

- This protocol is a review checklist, not a source schema. A future task may
  add a formal source-artifact schema after at least two packages exercise the
  same fields.
- A metadata-only package can preserve a locator and checksum plan, but it
  cannot support row curation by itself.
- Public access and reuse terms can change. Future curators must verify source
  state at retrieval time and record the exact reviewed state.
- This task intentionally leaves `TASK-0225`, `TASK-0293`, and `TASK-0336`
  blocked until a real reviewed source artifact exists.
