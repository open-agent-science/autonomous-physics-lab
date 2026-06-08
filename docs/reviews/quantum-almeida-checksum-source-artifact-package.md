# Quantum Almeida Checksum Source-Artifact Package

- Task: `TASK-0668`
- Campaign: Quantum Size Effects
- Source ID: `almeida-2023-nano-letters-inp-optical`
- Verdict: `METADATA_ONLY_BLOCKER_NO_SOURCE_FILES_STORED`

## Scope

This task packages the pre-digitization source-artifact decision for Almeida
2023 InP optical data. It does not digitize Figure 1b coordinates, transcribe
optical values, create `qd-*.yaml` rows, run size-effect baselines, or promote
claims.

## Selected Artifact Copies

The exact source copies to use in a future checksum-pinned package are:

| Role | Locator | Intended use |
| --- | --- | --- |
| Article DOI | `10.1021/acs.nanolett.3c02630` | Persistent article identity and citation anchor. |
| ACS article page | `https://pubs.acs.org/doi/10.1021/acs.nanolett.3c02630` | Publisher landing page and reuse-term recheck surface. |
| PMC mirror | `https://pmc.ncbi.nlm.nih.gov/articles/PMC10540257/` | Open article text and license cross-check surface. |
| TU Delft PDF copy | `https://research.tudelft.nl/files/160559018/acs.nanolett.3c02630.pdf` | Candidate article PDF copy for future checksum pinning. |
| Utrecht PDF copy | `https://dspace.library.uu.nl/bitstream/handle/1874/434964/almeida-et-al-2023-size-dependent-optical-properties-of-inp-colloidal-quantum-dots.pdf` | Alternate institutional article PDF copy for future checksum pinning. |
| ChemRxiv SI PDF | `https://chemrxiv.org/engage/api-gateway/chemrxiv/assets/orp/resource/item/64b00532ae3d1a7b0d9cf337/original/si-size-dependent-optical-properties-of-in-p-colloidal-quantum-dots.pdf` | Candidate supporting-information copy for future checksum pinning. |

## Package Decision

No article PDF, SI PDF, or figure raster is committed by this task. The package
therefore remains metadata-only.

Reason:

- the repository's prior reviews classify Almeida as promising but
  artifact-gated;
- the exact downloadable file copies still need a maintainer-reviewed
  reuse-term recheck at artifact-download time;
- committing publisher or mirror PDFs is unnecessary for this preflight and
  would expand the repository with source files before checksum/reuse approval
  is complete;
- the accepted task path explicitly allows preserving a metadata-only blocker
  when files cannot be committed.

`data/quantum_dots/source_manifest.yaml` already keeps
`almeida-2023-nano-letters-inp-optical` at `inclusion_decision: excluded`.
That state remains correct.

## Required Next Gate

Before any real Figure 1b digitization or row-readiness review, a future source
artifact task must:

1. download exactly one article copy and one SI copy from the selected locators;
2. recheck reuse terms on those exact copies;
3. record retrieval date, upstream filename, byte size, and SHA-256 checksum;
4. decide whether files can be committed or whether only checksums/locators
   should be stored;
5. keep Figure 1b coordinate extraction separate from this source-artifact
   gate.

## Output Routing

- Task verdict: `METADATA_ONLY_BLOCKER_NO_SOURCE_FILES_STORED`.
- Canonical destination:
  `docs/reviews/quantum-almeida-checksum-source-artifact-package.md`.
- Review tier: `none`.
- Gate A status: not attempted; no `RESULT-*`, `PRED-*`, or row artifact.
- Gate B status: not applicable.
- Claim impact: no claim created or modified.
- Knowledge impact: no knowledge artifact created or modified.
- Result impact: no `results/` artifact created or modified.
- Dataset impact: no `qd-*.yaml` row created; Almeida remains excluded from
  usable rows.
- Limitations / blockers: no source file checksum is committed; no real
  digitization export exists; no per-point provenance or row-readiness gate has
  passed.
