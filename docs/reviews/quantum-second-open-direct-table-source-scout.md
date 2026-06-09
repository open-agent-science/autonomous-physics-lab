# Quantum Second Open Direct-Table Source Scout

**Task:** `TASK-0656`  
**Campaign:** Quantum Size Effects  
**Candidate source family:** `prasad-2017-nanomaterials-cdse-zns-laser`  
**Verdict:** `BLOCKER_CORE_SHELL_DEVICE_CONTEXT`

## Scope

This scout checks exactly one additional open source family for a direct
table-like quantum-dot size and optical-peak surface. It does not transcribe
row values into `qd-*.yaml`, download or commit article files, digitize figures,
run a benchmark, or promote any claim.

The candidate was selected because the open article text exposes an explicit
table with quantum-dot core/shell sizes plus absorption and emission peaks. The
review is intentionally conservative: the table is real and useful as a future
excluded/reference surface, but it is not admissible for the current pure-core
Quantum Size Effects benchmark path.

## Source Locator

- Article: "A High Power, Frequency Tunable Colloidal Quantum Dot
  (CdSe/ZnS) Laser"
- DOI: `10.3390/nano7020029`
- Journal: `Nanomaterials`
- PMC locator: `https://pmc.ncbi.nlm.nih.gov/articles/PMC5333014/`
- Publisher locator: `https://www.mdpi.com/2079-4991/7/2/29`

## Candidate Summary

| Field | Assessment |
| --- | --- |
| Material family | CdSe/ZnS core-shell quantum dots |
| Property axis | `absorption_peak_eV` and `emission_peak_eV` candidates after wavelength-to-energy conversion in a future task |
| Size axis | Separate core and shell sizes in nm; not a single pure-core diameter row surface |
| Row surface | Article Table 1 lists quantum-dot size, absorption peak, emission peak, and Stokes shift |
| Access posture | Open article page and PMC mirror; metadata-only in this task |
| Expected row class | `table_derived_if_core_shell_axis_exists`; excluded for the current pure-core benchmark |
| Direct/model-derived status | Optical peaks are measurement-facing; size provenance is not sufficient for pure-core direct-measurement rows without source-copy and sizing-method review |

## Evidence Checked

The article abstract and methods context identify the source as a tunable laser
study using CdSe/ZnS quantum dots, not a primary pure-core quantum-size
benchmark. The source table is still relevant because it contains a compact
six-sample optical-peak series with explicit core and shell dimensions.

The table surface is not enough to unblock row curation for the current
campaign. It combines a CdSe core with a ZnS shell, and the experiment is
framed around amplified spontaneous emission and laser-cavity behavior. Those
surfaces would confound a first-pass pure material residual axis unless the
repository first defines a reviewed core-shell property axis and records
per-row shell semantics.

## Decision

`REJECT_FOR_CURRENT_BENCHMARK_KEEP_METADATA`

Add a metadata-only manifest entry for
`prasad-2017-nanomaterials-cdse-zns-laser` with
`inclusion_decision: excluded`.

This candidate should not feed `qd-*.yaml` rows until a future task does all of
the following:

- defines whether CdSe/ZnS core-shell rows belong in a separate emission or
  device-context axis;
- records both core size and shell thickness without collapsing them into one
  unreviewed diameter;
- verifies the article license/reuse posture on the exact selected article and
  supporting-information surfaces;
- checksum-pins any source artifacts if maintainer policy allows file commits;
- adds schema support for core/shell size semantics if needed;
- keeps laser/device metrics separate from absorption/emission peak residuals.

## Limitations

- No article PDF, supplementary file, table image, or source artifact was
  committed.
- No row values were copied into dataset files.
- No wavelength-to-energy conversion was performed.
- The source was not used to evaluate or tune any quantum-size model.
- The device/application framing in the article is ignored for APL; this
  review records only the source-surface decision.

## Output Routing

- Task verdict: `BLOCKER_CORE_SHELL_DEVICE_CONTEXT`.
- Canonical destination:
  `docs/reviews/quantum-second-open-direct-table-source-scout.md` plus a
  metadata-only excluded entry in `data/quantum_dots/source_manifest.yaml`.
- Review tier: none.
- Gate A status: not attempted; no `RESULT-*` or `PRED-*` artifact.
- Gate B status: not attempted; no independent replay target.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Dataset impact: no `qd-*.yaml` rows added or changed.
- Publication blocker: pure-core row admissibility remains blocked; this source
  needs a separate core-shell/device-axis decision before row curation.
