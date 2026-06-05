# Quantum open direct-table source scout 02

- Task: `TASK-0605`
- Campaign: `quantum-size-effects`
- Candidate source family:
  `almeida-2023-nano-letters-inp-optical`
- Candidate title:
  "Size-Dependent Optical Properties of InP Colloidal Quantum Dots"

## Scope

This scout checks exactly one source family beyond the exhausted
Norris-Bawendi and Kang-Wise routes. It records source admissibility only.

It does not transcribe values, add `qd-*.yaml` rows, run figure digitization,
compute quantum-size baselines, add synthesis guidance, create prediction
entries, or promote claims/knowledge.

## Source locator

- Article DOI: `10.1021/acs.nanolett.3c02630`
- ACS article page:
  `https://pubs.acs.org/doi/10.1021/acs.nanolett.3c02630`
- TU Delft repository record:
  `https://repository.tudelft.nl/record/uuid:5462db79-04ff-4c4d-8240-a226efc53a45`
- Utrecht repository PDF locator:
  `https://dspace.library.uu.nl/bitstream/handle/1874/434964/almeida-et-al-2023-size-dependent-optical-properties-of-inp-colloidal-quantum-dots.pdf`
- ChemRxiv supporting-information locator:
  `https://chemrxiv.org/engage/api-gateway/chemrxiv/assets/orp/resource/item/64b00532ae3d1a7b0d9cf337/original/si-size-dependent-optical-properties-of-in-p-colloidal-quantum-dots.pdf`

## Candidate summary

| Field | Assessment |
| --- | --- |
| Material | InP core-only colloidal quantum dots |
| Property axis | `absorption_peak_eV` candidate via first absorption transition `E1s`; `emission_peak_eV` context exists but is not row-ready here |
| Size axis | edge length/volume in article; manifest records `diameter_nm` as the closest current schema axis, but a future task must decide whether tetrahedral edge length/volume needs schema extension |
| Reuse posture | open-access article surfaces indicate CC-BY 4.0; this PR keeps metadata only |
| Checksum feasibility | feasible for article PDF and SI PDF in a future source-artifact task |
| Expected row class | `digitization_required` |
| Direct table status | no direct size-energy row table accepted by this scout |
| Direct/model-derived status | optical transition values are measurement-facing, but size/volume semantics are morphology-derived and need per-point provenance labels |

## Evidence checked

The ACS article page exposes the key candidate surface as Figure 1b: sizing
curves relating first absorption peak energy `E1s` to average edge length and
geometrical volume. It also states that extra data points from Xu et al. are
included for comparison. That makes source attribution and per-point inclusion
state important for any later row work.

The supporting information contents list figure-based sections for sizing
curves, morphology/composition, second absorptive transition, cross-section
fits, PL microscopy, transient absorption, and Auger constants. The only
printed table visible in the text extraction is Table S1 for PL transient
analysis (`EPL`, lifetimes, amplitudes, average lifetime, and PL quantum yield),
not a direct size-energy table.

Therefore this candidate does not satisfy `table_derived` row curation now. It
is still a useful open-source candidate because the article/SI are reachable as
open PDFs, the article is CC-BY surfaced, and the figure route can be audited
under `docs/quantum-direct-measurement-digitization-protocol.md`.

## Decision

`PROMISING_DIGITIZATION_REQUIRED_SOURCE`

Add a metadata-only source-manifest entry for
`almeida-2023-nano-letters-inp-optical`, but keep
`inclusion_decision: excluded` until a future source-artifact/digitization task
does all of the following:

- checksum-pins the article PDF and SI PDF or records a maintainer-approved
  metadata-only source-copy policy;
- records the exact figure/panel and source-attribution split for article data
  versus Xu et al. comparison data;
- determines whether the current quantum-dot schema can represent tetrahedral
  edge length/volume or whether a schema/task proposal is needed;
- runs WebPlotDigitizer-class axis calibration and per-point extraction;
- records uncertainty semantics and direct-versus-derived size labels;
- creates rows only after the readiness gate accepts the artifact.

## Limitations

- No PDF or SI file was committed.
- No checksum was computed in this task.
- No table values, figure coordinates, or row-level data were transcribed.
- No baseline metrics or formula search were run.
- The source may still fail future row curation if axis semantics, uncertainty
  fields, or comparison-data provenance cannot be represented cleanly.

## Output routing

- Task verdict: `PROMISING_DIGITIZATION_REQUIRED_SOURCE`.
- Canonical destination:
  `docs/reviews/quantum-open-direct-table-source-scout-02.md` and a
  metadata-only update to `data/quantum_dots/source_manifest.yaml`.
- Review tier: `none`.
- Gate A status: not attempted; no `RESULT-*` or `PRED-*` artifact.
- Gate B status: not attempted; no independent replay target.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Dataset impact: no `qd-*.yaml` rows added or changed.
- Publication blocker: checksum-pinned source artifact, digitization package,
  axis-semantics decision, uncertainty policy, and row-readiness review are
  still missing.
