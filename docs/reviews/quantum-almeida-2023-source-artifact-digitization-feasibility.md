# Quantum Almeida 2023 Source Artifact And Digitization Feasibility

**Task:** `TASK-0630`
**Campaign:** Quantum Size Effects
**Source ID:** `almeida-2023-nano-letters-inp-optical`
**Verdict:** `SCHEMA_EXTENSION_NEEDED`

## Scope

This review packages the metadata-only source-artifact and digitization
feasibility decision for Almeida et al. 2023, "Size-Dependent Optical
Properties of InP Colloidal Quantum Dots." It does not download or commit
article/SI PDFs, digitize coordinates, transcribe values, add `qd-*.yaml` rows,
run baselines, search formulas, create predictions, or promote claims,
knowledge, or result artifacts.

## Source Locators

| Surface | Locator | Feasibility |
| --- | --- | --- |
| Article DOI | `10.1021/acs.nanolett.3c02630` | DOI-pinned |
| ACS article page | `https://pubs.acs.org/doi/10.1021/acs.nanolett.3c02630` | source locator stable |
| PMC article mirror | `https://pmc.ncbi.nlm.nih.gov/articles/PMC10540257/` | open article text available |
| TU Delft PDF locator | `https://research.tudelft.nl/files/160559018/acs.nanolett.3c02630.pdf` | checksum feasible in future artifact task |
| Utrecht PDF locator | `https://dspace.library.uu.nl/bitstream/handle/1874/434964/almeida-et-al-2023-size-dependent-optical-properties-of-inp-colloidal-quantum-dots.pdf` | checksum feasible in future artifact task |
| ChemRxiv SI locator | `https://chemrxiv.org/engage/api-gateway/chemrxiv/assets/orp/resource/item/64b00532ae3d1a7b0d9cf337/original/si-size-dependent-optical-properties-of-in-p-colloidal-quantum-dots.pdf` | checksum feasible in future artifact task |

Retrieval date for this metadata review: `2026-06-06`.

Reuse posture remains metadata-only in this PR. The prior scout recorded open
article surfaces and CC-BY 4.0 posture, but this task does not commit source
files. A future artifact package should checksum-pin the selected article and
SI copies, record exact upstream filenames, and preserve the no-redistribution
decision unless the maintainer explicitly approves file commits.

## Candidate Figure Surfaces

The relevant row-candidate surface remains the article Figure 1b sizing curves
relating first absorption transition `E1s` to average tetrahedral edge length
and geometrical volume. The source also includes comparison points from Xu et
al., so any future digitization package must label per-point primary source:

- Almeida article data;
- Xu et al. comparison data;
- excluded or context-only points when provenance is not separable.

The supporting information should be treated as a source artifact for
figure/panel cross-checks and uncertainty notes, not as a direct table source
unless a future curator finds a printed size-energy table and records the table
locator.

## Schema Decision

The current `quantum_dot_size_effect` row schema requires exactly one of:

- `diameter_nm`;
- `radius_nm`.

Almeida's candidate surface is not naturally a diameter/radius surface. It is
reported as tetrahedral edge length and geometrical volume for core-only InP
nanocrystals. Converting those values into an equivalent diameter before row
curation would require an explicit morphology model and uncertainty rule.

Therefore this source is **not digitization-ready for `qd-*.yaml` rows yet**.
The next task should first add or approve schema support for at least one of:

- `edge_length_nm` with morphology label `tetrahedral`;
- `volume_nm3` with a source-derived geometry note;
- a reviewed `equivalent_diameter_nm` conversion field that preserves the
  original edge/volume value and conversion formula.

Without that extension, digitized Almeida rows would either violate the schema
or hide a morphology conversion inside a generic `diameter_nm` field.

## Outcome

`SCHEMA_EXTENSION_NEEDED`

Almeida 2023 remains a promising open, source-pinnable InP optical candidate,
but it should not proceed to coordinate digitization or row curation until the
size-axis schema decision is reviewed. The future digitization package should
target Figure 1b only after the schema can represent tetrahedral edge
length/volume or a reviewed equivalent-diameter conversion.

## Recommended Follow-Up

Open a narrow schema/readiness task for Quantum Size Effects that:

1. extends or reviews `physics_lab/schemas/quantum_dot_size_effect.schema.json`
   for non-spherical morphology size axes;
2. adds tests for valid tetrahedral `edge_length_nm` / `volume_nm3` metadata or
   for a reviewed equivalent-diameter representation;
3. updates `data/quantum_dots/source_manifest.yaml` notes only after the schema
   route is accepted;
4. then allows a separate Almeida digitization package to checksum-pin article
   and SI sources, calibrate Figure 1b axes, and export per-point provenance.

## Limitations

- No checksum was computed because no article or SI file was downloaded or
  committed in this task.
- No figure coordinates or optical transition values were transcribed.
- The license/reuse posture is metadata-only and must be rechecked by the
  future artifact package before any source file is committed.
- This decision is source-readiness only; it does not evaluate InP quantum-dot
  formulas, baselines, material design, device performance, synthesis, or
  biomedical claims.

## Output Routing Summary

- Task verdict: `SCHEMA_EXTENSION_NEEDED`.
- Canonical destination:
  `docs/reviews/quantum-almeida-2023-source-artifact-digitization-feasibility.md`.
- Review tier: `none`.
- Gate A status: `not_attempted`.
- Gate B status: `not_applicable`.
- Claim impact: `none`.
- Knowledge impact: `none`.
- Result impact: `no RESULT artifact created`.
- Publication blocker: schema support for tetrahedral edge length/volume or a
  reviewed equivalent-diameter conversion is missing.
