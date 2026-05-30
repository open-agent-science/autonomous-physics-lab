# Quantum Kang-Wise 1997 PbS Source Path Review

**Task:** `TASK-0400`
**Campaign:** Quantum Size Effects
**Candidate source:** Kang and Wise 1997 PbS/PbSe quantum-dot paper
**Outcome:** `BLOCKED_NO_DIRECT_ROWS_FOUND`

## Scope

This review verifies whether the Kang-Wise 1997 PbS source path can provide
direct row-level values for the Quantum Size Effects dataset. It does not add
`qd-*.yaml` rows, does not estimate figure coordinates, does not apply
calibration polynomials, does not run a benchmark, and does not promote any
claim or knowledge artifact.

Inputs reviewed:

- `docs/reviews/quantum-open-direct-table-source-triage.md`
- `docs/reviews/quantum-pmc-arxiv-direct-table-source-attempt.md`
- `data/quantum_dots/source_manifest.yaml`
- `docs/quantum-direct-measurement-digitization-protocol.md`
- `docs/fresh-data-intake-protocol.md`
- Optica primary article page for Kang and Wise, "Electronic structure and
  optical properties of PbS and PbSe quantum dots"

## Primary Source Correction

The committed triage/manifest path described the candidate as a Physical
Review B / APS source with DOI `10.1103/PhysRevB.56.9377`. The primary article
record shows a different source:

- authors: Inuk Kang and Frank W. Wise;
- title: "Electronic structure and optical properties of PbS and PbSe quantum
  dots";
- journal: `Journal of the Optical Society of America B`;
- volume/issue/pages: `14`(7), 1632-1646;
- publication date: July 1, 1997;
- DOI: `10.1364/JOSAB.14.001632`;
- publisher page: `https://opg.optica.org/josab/abstract.cfm?uri=josab-14-7-1632`.

This means the earlier APS public-access assumption is not a safe source path
for this candidate. Any future source-artifact task should use the Optica DOI
and publisher page, not the PRB locator.

## Direct-Row Assessment

The Optica article page exposes the article metadata and lists:

- `Figures (13)`;
- `Tables (2)`;
- article access status: not accessible without library or account access;
- article tables available only to subscribers on the publisher page.

The visible table metadata is not a size-energy measurement surface:

- Table 1: parameters of the `k · p` Hamiltonians of PbS and PbSe;
- Table 2: parameters of the anisotropy perturbation operator of PbS and PbSe.

Those tables are theory/model parameter tables, not direct PbS quantum-dot
measurement rows with `(diameter_nm, absorption_peak_eV)` or
`(diameter_nm, bandgap_eV)` pairs. They do not satisfy APL's direct-row gate.

The article abstract describes a four-band envelope-function calculation whose
allowed exciton energies agree with experimental data, but this metadata-level
review did not recover printed direct measurement rows, machine-readable
supplementary data, or a redistributable table artifact.

## Provenance-Class Decision

| Question | Finding |
| --- | --- |
| Printed table values for direct rows? | No direct size-energy table found in visible publisher metadata; visible tables are model-parameter tables. |
| Digitizable figure points? | Possible only as a future figure-digitization task if a curator has legitimate access to the figures and can produce a WebPlotDigitizer-class artifact. Not performed here. |
| Machine-readable supplement data? | None found from the primary article page in this review. |
| Usable row-level source for strict dataset gate now? | No. |

Decision: `BLOCKED_NO_DIRECT_ROWS_FOUND`.

The source remains a metadata-only candidate and should not be used by
`qd-*.yaml` rows until a later task either:

- obtains a legitimate source artifact and confirms direct printed values; or
- runs the full figure-digitization protocol with committed calibration and
  extracted-point artifacts.

## Manifest Update

`data/quantum_dots/source_manifest.yaml` is updated to preserve this negative
verification memory:

- corrects the source citation from the incorrect PRB/APS path to the Optica
  JOSA B path;
- changes the row expectation from table-derived to blocked/figure-only
  pending deterministic digitization;
- keeps the entry excluded from row-level dataset use;
- records that zero rows and zero source artifacts were added.

## What This Review Did Not Do

- It did not commit the article PDF, figures, or tables.
- It did not access subscriber-only article content.
- It did not estimate figure points by eye or through an LLM.
- It did not add any `qd-*.yaml` row.
- It did not run a quantum-dot baseline or pilot benchmark.
- It did not make synthesis, device, biomedical, or material-design claims.

## Limitations

- The review is based on the visible primary Optica article page and committed
  repository context. It does not inspect subscriber-only full article content.
- Because figure panels are subscriber-gated on the publisher page, this task
  cannot determine whether a future licensed curator could digitize enough
  points under `docs/quantum-direct-measurement-digitization-protocol.md`.
- The conclusion is a strict APL dataset-gate conclusion, not a judgement on
  the scientific value of the Kang-Wise paper.

## Verdict

`BLOCKED_WITH_NEGATIVE_MEMORY`.

Kang-Wise 1997 does not currently provide a deterministic direct-row path for
APL. The clean handoff is to keep the manifest entry excluded and preserve the
correct Optica locator plus blocker rationale for any future source-artifact or
digitization task.

## Output Routing Summary

- Task verdict: `BLOCKED_WITH_NEGATIVE_MEMORY`
- Canonical destination: blocker/source-path review under `docs/reviews/` and
  source-manifest metadata update
- Review tier: `none`
- Gate A status: not attempted; no result or prediction artifact was produced
- Gate B status: not attempted
- Claim impact: no claim change
- Knowledge impact: no knowledge change
- Publication blocker: no deterministic direct rows, no source artifact, and
  no figure-digitization artifact exist for this candidate
