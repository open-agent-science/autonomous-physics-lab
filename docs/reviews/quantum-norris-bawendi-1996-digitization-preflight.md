# Quantum Norris-Bawendi 1996 Digitization Preflight

**Task:** `TASK-0398`
**Campaign:** Quantum Size Effects
**Source candidate:** Norris & Bawendi 1996, Physical Review B 53, 16338-16346
**DOI:** `10.1103/PhysRevB.53.16338`
**Source manifest id:** `norris-bawendi-1996-prb-cdse-band-edge`
**Outcome:** `BLOCKER_DIGITIZATION_ARTIFACT_REQUIRED`

## Boundary

This preflight packages the source and digitization requirements for the
Norris-Bawendi 1996 CdSe candidate. It does not curate quantum-dot rows, does
not add a `qd-*.yaml` file, does not commit a publisher PDF or figure asset,
does not estimate graph coordinates, does not run a benchmark, and does not
promote any claim or accepted knowledge.

The outcome is intentionally blocker-safe: the source remains a high-priority
candidate, but row curation is blocked until a deterministic
WebPlotDigitizer-class artifact is committed and reviewed under
`docs/quantum-direct-measurement-digitization-protocol.md`.

## Source Target

The target publication is:

- **Citation:** Norris, D. J.; Bawendi, M. G. (1996), "Measurement and
  Assignment of the Size-Dependent Optical Spectrum in CdSe Quantum Dots,"
  *Physical Review B* **53**, 16338-16346.
- **DOI:** `10.1103/PhysRevB.53.16338`
- **Material:** CdSe quantum dots.
- **Candidate property axes:** `absorption_peak_eV` and `bandgap_eV`.
- **Size axis:** radius in nm, per the existing manifest candidate metadata.
- **Expected usable surface:** size-dependent optical-spectrum / PLE-derived
  figure surfaces rather than a currently committed printed table.

The existing manifest entry is metadata-only and remains `excluded` until a
reviewed task commits a checksum-pinned source artifact and row-level direct
measurement provenance.

## Prior Evidence Reviewed

### TASK-0347 open-direct-table triage

`docs/reviews/quantum-open-direct-table-source-triage.md` originally ranked the
Norris-Bawendi 1996 candidate first for a possible CdSe direct-measurement seed.
That triage treated the source as a likely high-value measurement surface, with
APS access potentially easier than ACS supporting-information routes.

### TASK-0364 PMC/arXiv direct-table attempt

`docs/reviews/quantum-pmc-arxiv-direct-table-source-attempt.md` later inspected a
maintainer-provided sandbox PDF copy and recorded a stricter finding:

- no printed `Table N` headers were recovered;
- no inline size-to-energy value pairs were recovered from body text;
- the candidate must be treated as `figure_derived` for row-curation purposes;
- no PDF, table, or row values were committed;
- the recommended next path is the digitization protocol rather than a
  table-derived row attempt.

This preflight accepts the TASK-0364 finding and does not reclassify the source
as table-derived.

## Protocol Gate

The applicable gate is `docs/quantum-direct-measurement-digitization-protocol.md`.
Under that protocol, figure-derived rows may enter `data/quantum_dots/qd-*.yaml`
only after all of the following are available:

1. a registered source manifest entry with accurate citation metadata,
   figure/table reference, license note, and checksum policy;
2. a deterministic WebPlotDigitizer-class extraction pass;
3. axis calibration anchors and per-point coordinates;
4. per-point provenance fields, including source figure reference,
   axis-calibration artifact, extraction tool, and coordinate uncertainty;
5. residual-vs-formula or measurement-consistency cross-checks where applicable;
6. a committed artifact under `data/quantum_dots/digitization/<source_id>/`;
7. at least six rows that survive the protocol gate before a `qd-*.yaml` seed is
   considered usable.

A row based on LLM visual inspection, memory, a sizing polynomial, or an
implicit table reconstruction remains forbidden.

## Preflight Artifact Package Status

No deterministic digitization artifact is available in this PR.

Expected future artifact path:

```text
data/quantum_dots/digitization/norris-bawendi-1996-prb-cdse-band-edge/
  README.md
  axis_calibration.csv
  extracted_points.csv
  notes.md
```

Required fields for the future artifact:

- exact source locator and figure/panel reference;
- tool name and version;
- axis calibration anchors and units;
- raw extracted coordinates;
- converted physical values and units;
- point-level inclusion/exclusion status;
- primary-source attribution if any plotted point comes from a cited source;
- coordinate uncertainty and any publication uncertainty floor;
- extraction notes sufficient for reviewer replay.

Do not commit the original APS PDF, raw figure image, or non-redistributable
publisher asset. The artifact must be re-runnable from an accessible source and
must contain only extraction metadata and derived per-point coordinates that the
repository is allowed to store.

## Source-Artifact Intake Checklist

Before any future row-curation PR uses this source, the PR must answer:

- Has the APS page or DOI landing page been identified and pinned?
- Is the publication readable by the curator without committing the PDF?
- Are the publisher reuse terms recorded for derived tabular extraction data?
- Is the target figure/panel named unambiguously?
- Are the axes, tick labels, and units visible enough for calibration?
- Are there at least four calibration anchors, preferably two per axis?
- Are there at least six discrete candidate points after exclusions?
- Does each point have uncertainty semantics and provenance?
- Are formula-derived or assignment-derived values kept separate from direct
  measurements?
- Does the resulting `qd-*.yaml` preserve `absorption_peak_eV` and `bandgap_eV`
  semantics rather than mixing optical-peak and band-edge claims?

## Row-Curation Decision

No `qd-*.yaml` rows are added by this task.

Current decision:

```text
row_curation_ready: false
source_artifact_ready: false
digitization_artifact_ready: false
benchmark_unblocked: false
```

Reason:

```text
A WebPlotDigitizer-class artifact with calibration anchors, per-point exported
coordinates, uncertainty notes, and replayable extraction metadata is not
committed.
```

## Relationship To TASK-0225

This task does not unblock `TASK-0225`. The quantum direct-measurement row-level
readiness gate still applies. A future successful digitization artifact may
support a separate row-curation PR, but the baseline residual benchmark must not
run on unreviewed figure-derived values.

## Relationship To TASK-0489

`TASK-0489` remains a compatible follow-up direction for a fuller source-artifact
review. This preflight records the row-level gate and artifact requirements for
Norris-Bawendi 1996; it does not replace any later source-package task that may
verify access, checksums, or extraction details with a human-run digitization
tool.

## Limitations

- This PR does not inspect or redistribute the original APS article.
- This PR does not run WebPlotDigitizer or an equivalent tool.
- This PR does not determine the exact figure-panel point count.
- This PR does not compute coordinate uncertainty or residual-vs-formula checks.
- This PR does not create a source artifact package under
  `data/quantum_dots/source_artifacts/` because no redistributable source file or
  deterministic extraction artifact is available.
- This PR does not update `data/quantum_dots/source_manifest.yaml`; the existing
  manifest already records this source as excluded pending artifact and
  provenance review.

## Verdict

`BLOCKER_DIGITIZATION_ARTIFACT_REQUIRED`

The Norris-Bawendi 1996 candidate remains scientifically promising, but it is not
row-ready. The next valid step is a human or tool-assisted deterministic
digitization pass that produces a replayable artifact package. Until then, the
source must remain excluded from curated `qd-*.yaml` rows and must not be used to
unblock the quantum size-effect baseline benchmark.
