# TASK-1027: Kim 2020 CdSe source artifact preflight

**Task:** TASK-1027  
**Date:** 2026-07-13  
**Mode:** source identity and axis semantics only

## Pinned source identity

| Item | Recorded value |
|---|---|
| Citation | Kim et al., *Influence of Size and Shape Anisotropy on Optical Properties of CdSe Quantum Dots* |
| DOI | https://doi.org/10.3390/nano10081589 |
| Publisher page | https://www.mdpi.com/2079-4991/10/8/1589 |
| Full-text mirror | https://pmc.ncbi.nlm.nih.gov/articles/PMC7466547/ |
| OA metadata | NCBI PMC OA record, PMC7466547 |
| License | Creative Commons Attribution (CC BY 4.0) |
| Access observation | 2026-07-13 UTC |

The NCBI OA record identifies the article as *Nanomaterials* 10(8), 1589 (2020),
CC BY, not retracted, with package locator
`ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/f1/56/PMC7466547.tar.gz`.

## Artifact and checksum status

The exact PDF bytes could not be retrieved from the available publisher/PMC
surfaces during this preflight. The PMC PDF route returned an HTML access response,
not a PDF; MDPI's PDF route returned an access-denied response; the OA package
locator was not retrievable. These response pages are not source artifacts and are
not hashed as if they were.

Therefore:

- candidate artifact: `nanomaterials-10-01589.pdf`
- `artifact_status: not_pinned`
- `bytes_retained: false`
- `sha256: null`
- blocker: `source_bytes_unavailable`

No checksum is fabricated from a URL, HTML response, or DOI.

## Axis and figure semantics

The source surface identifies these extraction targets without transcribing values:

- Figure 1: HRTEM morphology and size/shape evidence;
- Figure 3: optical spectra;
- Figure 4: differential-absorption spectra;
- Figure 5: size-dependent transition analysis;
- four growth-time sample groups described in the source metadata.

The extraction contract must keep absorption peak energy, emission peak energy, and
band-gap quantities as separate axes. HRTEM diameter is a morphology observation,
not automatically an equivalent-sphere diameter. Shape anisotropy remains an
explicit field; model-derived sizing and uncertainty must not silently become
measured rows. Figure IDs, sample IDs, units, and axis direction must be confirmed
from pinned bytes before digitization.

## Decision

**`SOURCE_LIMITED`**

Identity, DOI, license, and the pre-digitization axis inventory are recorded, but
the exact source bytes and SHA-256 remain unavailable. Digitization is blocked
pending a retrievable, checksum-pinned artifact. No figure crop, value, quantum-dot
row, fit, metric, RESULT, CLAIM, PREDICTION, or KNOWLEDGE artifact was created.
