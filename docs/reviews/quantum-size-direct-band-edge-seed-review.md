# Quantum Direct-Measurement Band-Edge Seed Investigation

**Task:** TASK-0292
**Status:** review (no `qd-*.yaml` seed produced)
**Source candidate:** `jasieniak-2011-acs-nano-band-edge`
**Decision:** review-only blocker record

## Scope

This note records a first-attempt investigation of the TASK-0292 band-edge
seed path. It does not create a row-level `qd-*.yaml` dataset file, does not
modify `source_manifest.yaml`, does not fetch or commit source tables, and
does not unblock TASK-0225 or TASK-0293.

The task asked for one reviewed `bandgap_eV` or band-edge-derived dataset
seed with at least six included rows if the source supports direct
measurement provenance. The repository source manifest already contains the
accepted first-attempt source:

- `jasieniak-2011-acs-nano-band-edge`
- Jasieniak, J. J.; Califano, M.; Watkins, S. E. (2011)
- DOI: <https://doi.org/10.1021/nn201681s>

## Inputs Reviewed

- `data/quantum_dots/source_manifest.yaml`
- `docs/reviews/quantum-direct-measurement-source-triage.md`
- `docs/reviews/quantum-size-row-level-data-readiness-for-baseline.md`
- `docs/reviews/quantum-size-direct-absorption-seed-review.md`
- `docs/quantum-direct-measurement-digitization-protocol.md`
- `data/quantum_dots/digitization/README.md`
- `physics_lab/schemas/quantum_dot_size_effect.schema.json`
- TASK-0292 task contract
- ACS article metadata page for DOI `10.1021/nn201681s`
- Monash publication metadata page for the same article
- Riken Keiki usage note summarizing the measurement method

## Method

1. Re-read the TASK-0298 triage classification for
   `jasieniak-2011-acs-nano-band-edge`.
2. Verified from source metadata that the article is the correct band-edge
   candidate for CdSe, CdTe, PbS, and PbSe.
3. Checked whether a curation path exists without LLM-estimated graph
   coordinates.
4. Attempted to retrieve the ACS Supporting Information PDF in `/tmp`:
   `nn201681s_si_001.pdf`.
5. Preserved the no-fabrication rule when the table data could not be
   retrieved and reviewed locally.

## Findings

### F1. Jasieniak 2011 is the right source class

The source remains a valid first-attempt source candidate. The Monash
metadata page describes the article as a peer-reviewed ACS Nano paper that
uses photoelectron spectroscopy in air (PESA) to study size-dependent
valence and conduction band-edge energies for CdSe, CdTe, PbS, and PbSe
quantum dots.

The Riken Keiki method note is consistent with the manifest caveat:
valence band energy is measured by AC-2 / PESA-style photoelectron
spectroscopy, while the optical conduction-band edge is calculated from
the measured valence-band edge and photoabsorption energy. Therefore any
`bandgap_eV` row must preserve the derivation from underlying band-edge
measurements rather than relabeling optical absorption or emission peaks
as direct bandgap values.

### F2. The ACS metadata indicates a table path exists

The ACS article page lists Supporting Information for DOI
`10.1021/nn201681s` and describes it as containing, among other supporting
materials, tabulated energy-point data and size-dependent optical band-gap
relations.

That means the source likely supports a future compliant band-edge seed if
a curator can access, inspect, and cite the Supporting Information table
directly.

### F3. This environment could not retrieve the Supporting Information

The attempted SI retrieval was blocked:

```text
curl -L --fail --silent --show-error --output /tmp/nn201681s_si_001.pdf \
  https://pubs.acs.org/doi/suppl/10.1021/nn201681s/suppl_file/nn201681s_si_001.pdf
```

Result:

```text
curl: (22) The requested URL returned error: 403
```

Retrying with a browser-like User-Agent returned the same `403`.

Because the SI table was not retrieved, no row values, uncertainty fields,
or per-material table references could be verified. The review therefore
cannot create `qd-0004-direct-band-edge.yaml` without violating the
measurement-grade provenance rule.

### F4. Figure-only fallback is not acceptable in this pass

The source may also contain size-dependent energy diagrams, but no
WebPlotDigitizer-class artifact exists under
`data/quantum_dots/digitization/jasieniak-2011-acs-nano-band-edge/`.

Under `docs/quantum-direct-measurement-digitization-protocol.md`, an
LLM-only figure read is not acceptable provenance. Any figure-derived
band-edge row would need:

- axis-calibration anchors;
- exported per-point coordinates;
- tool/version notes;
- per-point uncertainty;
- explicit links from each row to the digitisation artifact;
- preservation of the valence-band / conduction-band / optical-gap
  derivation.

None of those artifacts exists yet.

## Decision

No `qd-0004` band-edge dataset is produced in this pass.

The source appears promising, and unlike the TASK-0291 Yu 2003 absorption
case, the article metadata suggests a direct table path may exist in the
Supporting Information. However, the actual table was not available to this
agent for review, and the repository has no deterministic digitisation
artifact for a figure-derived fallback.

The correct output is therefore a review-only blocker record rather than a
fabricated dataset.

## Unblock Paths

Any one of these would be sufficient for a future TASK-0292 retry or
follow-up:

1. A maintainer or human curator retrieves the ACS Supporting Information,
   verifies the tabulated energy-point rows, and supplies at least six
   reviewed `(material, diameter_nm, bandgap_eV)` rows with source table
   references and derivation notes.
2. A deterministic parser or manual curation note extracts rows from the
   Supporting Information table, records source-table references, and keeps
   the raw SI file out of the repository unless redistribution is allowed.
3. A WebPlotDigitizer-class artifact is committed under
   `data/quantum_dots/digitization/jasieniak-2011-acs-nano-band-edge/`
   and then used to create a figure-derived band-edge seed.
4. A maintainer waiver explicitly permits a narrower metadata-only or
   table-citation-only seed, with the limitation recorded in the seed
   file, campaign page, and readiness-gate rerun.

## What This Investigation Did Not Do

- It did not add `data/quantum_dots/qd-0004-direct-band-edge.yaml`.
- It did not modify any existing `qd-*.yaml` file.
- It did not modify `data/quantum_dots/source_manifest.yaml`.
- It did not redistribute ACS article text, figures, or Supporting
  Information tables.
- It did not use LLM-estimated graph coordinates.
- It did not unblock TASK-0225 or TASK-0293.
- It did not promote a claim, result, or knowledge entry.

## Limitations

- The conclusion is access-limited, not source-disqualifying. The source
  may still be suitable once the Supporting Information table can be
  reviewed.
- The investigation did not inspect the official SI table values, so it
  cannot estimate row count, material coverage, or uncertainty semantics.
- The review did not evaluate whether `bandgap_eV` should be derived from
  optical gap alone, `E_CB - E_VB`, or another source-specific convention;
  a future seed must lock that semantic before rows are added.
- The review does not change the calibration-derived status of qd-0001 and
  qd-0002.

## Verdict

`INCONCLUSIVE` for row-level seed curation. `VALID` as a blocker record:
Jasieniak 2011 remains the correct first-attempt band-edge source, but no
measurement-grade `bandgap_eV` seed can be committed by this agent without
access to the SI table or a deterministic digitisation artifact.
