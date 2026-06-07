# Quantum Almeida 2023 License And Figure-Surface Review

**Task:** `TASK-0654`  
**Campaign:** Quantum Size Effects  
**Source ID:** `almeida-2023-nano-letters-inp-optical`  
**Verdict:** `VALID_IN_RANGE`

## Scope

This review completes the license, reuse, and figure-surface checklist for
Almeida et al. 2023 without digitizing coordinates, transcribing values,
converting tetrahedral axes into rows, running baselines, or creating claims.

It builds on:

- `TASK-0605` scout (`docs/reviews/quantum-open-direct-table-source-scout-02.md`)
- `TASK-0630` feasibility review
  (`docs/reviews/quantum-almeida-2023-source-artifact-digitization-feasibility.md`)
- `TASK-0637` non-spherical schema extension (status: `DONE`)
- `docs/quantum-direct-measurement-digitization-protocol.md`

No article PDF, SI PDF, figure raster, checksum, or `qd-*.yaml` row was
committed in this task.

## Source Locators And Retrieval

| Surface | Locator | Checksum / archive feasibility |
| --- | --- | --- |
| Article DOI | `10.1021/acs.nanolett.3c02630` | DOI-pinned; `checksum_policy: doi_pinned` |
| ACS article page | `https://pubs.acs.org/doi/10.1021/acs.nanolett.3c02630` | stable locator; article PDF checksum feasible in a future artifact task |
| PMC mirror | `https://pmc.ncbi.nlm.nih.gov/articles/PMC10540257/` | open article text; useful for license cross-check |
| TU Delft PDF | `https://research.tudelft.nl/files/160559018/acs.nanolett.3c02630.pdf` | institutional copy; SHA-256 feasible when maintainer approves download |
| Utrecht PDF | `https://dspace.library.uu.nl/bitstream/handle/1874/434964/almeida-et-al-2023-size-dependent-optical-properties-of-inp-colloidal-quantum-dots.pdf` | institutional copy; SHA-256 feasible when maintainer approves download |
| ChemRxiv SI PDF | `https://chemrxiv.org/engage/api-gateway/chemrxiv/assets/orp/resource/item/64b00532ae3d1a7b0d9cf337/original/si-size-dependent-optical-properties-of-in-p-colloidal-quantum-dots.pdf` | SI checksum feasible in a future artifact task |

Retrieval date for this metadata review: `2026-06-07`.

## License And Reuse Posture

| Item | Assessment |
| --- | --- |
| Publisher route | ACS Nano Letters |
| Open-access posture | Public article surfaces (ACS page, PMC mirror, institutional copies) indicate open access |
| Reuse terms surfaced | CC-BY 4.0 indicated on public article metadata reviewed by prior scouts; **recheck at artifact-download time** |
| Repository posture in this task | metadata-only; no publisher PDF, SI PDF, or figure asset committed |
| Figure-derived row policy | Permitted only via `docs/quantum-direct-measurement-digitization-protocol.md`; no LLM eyeballing |
| Redistribution guardrail | Do not commit publisher PDFs, SI PDFs, or full-resolution figure rasters unless a maintainer-reviewed source-artifact task explicitly approves file commits and records checksums |
| Digitization artifact posture | Committing axis-calibration CSV, extracted-point CSV, and README under `data/quantum_dots/digitization/<source_id>/` is the intended future path; it does not by itself authorize `qd-*.yaml` rows |

This task records reuse posture as **promising but artifact-gated**. A future
checksum-pinned source-artifact package must re-verify CC-BY terms on the exact
file copies selected for download before any publisher file is committed.

## Figure And Panel Surfaces

### Primary row-candidate surface

| Field | Value |
| --- | --- |
| Figure | Article Figure 1b |
| Property | first absorption transition `E1s` (`absorption_peak_eV`) |
| Size axes on figure | average tetrahedral edge length; geometrical volume |
| Accepted schema route after TASK-0637 | `edge_length_nm` or `volume_nm3` with `morphology: tetrahedral`; reviewed `equivalent_diameter_nm` only with `size_conversion` |
| Expected row class | `digitization_required` |
| Direct table status | no admissible size-energy printed table |

Future digitization must calibrate both size axes separately or declare which
panel/curve is authoritative before rows are built. Do not coerce edge length or
volume into undocumented `diameter_nm` fields.

### Comparison and attribution requirement

Figure 1b includes comparison points from Xu et al. Any future digitization
package must record per-point `primary_source_id` for:

- Almeida article data;
- Xu et al. comparison data;
- excluded/context-only points when provenance cannot be separated cleanly.

Points without separable primary-source provenance must use
`inclusion_status: excluded` with an explicit reason.

### Supporting-information surfaces

The SI is a cross-check and uncertainty surface, not a direct row table source
unless a future curator finds a printed size-energy table and records the table
locator.

| SI surface | Role for future curation |
| --- | --- |
| Sizing-curve figures | cross-check axis labels, morphology context, and uncertainty language |
| Morphology/composition figures | morphology validation only; not a substitute for per-point size read |
| Second absorptive transition figures | separate property axis; do not mix with `E1s` rows |
| Cross-section / PL / transient figures | context or exclusion review; not the primary size-energy surface |
| Table S1 (PL transient analysis) | **not** a size-energy table; do not use for `qd-*.yaml` row curation |

## Schema And Tooling Blockers

| Blocker | Status after this review |
| --- | --- |
| Non-spherical size-axis schema (`TASK-0637`) | **resolved** — `edge_length_nm`, `volume_nm3`, `equivalent_diameter_nm`, `morphology`, and `size_conversion` are accepted |
| License / figure-surface checklist (`TASK-0654`) | **resolved by this review** |
| Checksum-pinned article/SI source artifact | **still blocked** — no committed PDF or SHA-256 digest |
| WebPlotDigitizer-class digitization export | **still blocked** — no real axis calibration or extracted-point artifact |
| Non-spherical digitization fixture dry-run | recommended follow-up (`TASK-0655` or equivalent) before real Almeida coordinates |
| Per-point uncertainty and formula cross-check | **still blocked** — requires real digitization pass |
| Six-row readiness gate and `TASK-0225` baseline | **still blocked** — no measurement rows exist |

`TASK-0637` no longer blocks this source. The remaining blockers are source
artifact packaging, deterministic digitization tooling output, and row-readiness
review — not schema shape.

## Manifest Update

`data/quantum_dots/source_manifest.yaml` was updated metadata-only to:

- set `size_axis: edge_length_nm` for the accepted tetrahedral route;
- record this review in `license_note` and `notes`;
- keep `inclusion_decision: excluded` until a future digitization artifact and
  row-readiness review pass.

## Recommended Follow-Up

1. Land or merge a non-spherical digitization fixture dry-run
   (`TASK-0655`) to validate ledger-to-schema mechanics before real figure reads.
2. Open a checksum-pinned Almeida source-artifact package task that downloads
   and records SHA-256 for the selected article and SI copies after maintainer
   approval.
3. Run WebPlotDigitizer-class extraction on Figure 1b only after the artifact
   package and attribution split are reviewed.
4. Keep `inclusion_decision: excluded` until at least six included rows pass
   the direct-measurement digitization protocol and readiness gate.

## Limitations

- No checksum was computed because no article or SI file was downloaded or
  committed.
- CC-BY posture is metadata-only and must be rechecked on the exact file copy
  used by a future artifact task.
- No figure coordinates or optical values were transcribed.
- This review does not evaluate InP formulas, baselines, synthesis, devices, or
  biomedical claims.

## Output Routing Summary

- task verdict: `VALID_IN_RANGE`;
- canonical destination:
  `docs/reviews/quantum-almeida-license-figure-surface-review.md` and optional
  metadata-only `source_manifest.yaml` notes;
- review tier: `none`;
- Gate A status: not attempted;
- Gate B status: not attempted;
- claim impact: no claim change;
- knowledge impact: no knowledge change;
- result artifact impact: no `results/` artifacts modified;
- publication blocker: checksum-pinned source artifact, real digitization export,
  per-point provenance, and row-readiness review remain missing.
