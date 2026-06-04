# Source Artifact Directory - Pizzocaro et al. 2020 / VLBI Yb-Sr

Task: `TASK-0542`
Campaign: Atomic-Clock Residuals
Source artifact ID: `ACLOCK-SRC-ARTIFACT-2020-PIZZOCARO-VLBI`

## Purpose

This directory pins the open Zenodo source dataset for Pizzocaro et al.,
"Intercontinental comparison of optical atomic clocks through very long
baseline interferometry." The source supports a future Atomic Yb/Sr
row-admissibility gate, but this package is not itself a curated ACR row
dataset.

The committed CSV files are source artifacts only. They are not copied into
`data/atomic_clocks/acr-*.yaml`, not benchmarked, and not promoted to a result,
claim, prediction, or knowledge artifact.

## Source Locator

- Dataset DOI: `10.5281/zenodo.5592085`
- Dataset URL: `https://zenodo.org/records/5592085`
- Related publication DOI: `10.1038/s41567-020-01038-6`
- Related publication: Nature Physics 17, 223-227
- Dataset version: `v1`
- Dataset publication date: `2020-10-05`
- Dataset license: Creative Commons Attribution 4.0 International
- Publication-of-record PDF redistributed here: no

## Committed Files

| File | Zenodo md5 | SHA-256 |
| --- | --- | --- |
| `galav-delay-resolution-function.csv` | `9c242a41929822686ced4a745ff83776` | `13170564200227bad9b6fbcca8d611069d16ed28f22dfd00000b1d3228bf01a8` |
| `Yb-Sr-ratio-measurements-IPPP.csv` | `637902ae5a73939e88b4514cede9ee21` | `afd12267bb161f408e8bbad77511de087ccf5ffca919d06161333c89259bde58` |
| `Yb-Sr-ratio-measuremets.csv` | `d742a7cf813827a1f2fb3804cfd8de57` | `fa81da6f0afadedfc5028352ed2af8c87dc64f1217eb2fb84efd0c6c064c87d2` |

The filename `Yb-Sr-ratio-measuremets.csv` preserves the spelling used by the
Zenodo record.

## Retrieval

The files were retrieved on `2026-06-04` from:

- `https://zenodo.org/records/5592085/files/galav-delay-resolution-function.csv?download=1`
- `https://zenodo.org/records/5592085/files/Yb-Sr-ratio-measurements-IPPP.csv?download=1`
- `https://zenodo.org/records/5592085/files/Yb-Sr-ratio-measuremets.csv?download=1`

The md5 hashes match the Zenodo record, and repository SHA-256 hashes are
recorded in `provenance.yaml`.

## Row-Curation Status

`TASK-0542` pins the source artifact only. A future task, currently represented
by `TASK-0567`, must still decide whether any source values are admissible as
atomic-clock rows. That later task must review at least:

- source-file-to-row mapping;
- transition labels and ratio orientation;
- campaign-window semantics;
- uncertainty and covariance semantics;
- direct-vs-derived row class;
- holdout or reveal-freeze binding;
- whether the misspelled Zenodo filename should be preserved only at the
  artifact layer or normalized in a later extraction ledger.

## Non-Goals

- No publisher PDF is committed.
- No row values are transcribed into an ACR dataset.
- No cross-source benchmark, drift fit, prediction, result, claim, or knowledge
  artifact is created.
- `TASK-0456` is not marked unblocked.
