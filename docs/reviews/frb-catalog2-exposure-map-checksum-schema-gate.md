# FRB Catalog 2 Exposure-Map Checksum And HDF5 Schema Gate

Task: `TASK-0930`

Domain: radio transients astrophysics

Run date: `2026-07-04`

Verdict: `CHECKSUM_PINNED_CONSTRUCTION_BLOCKED_STATIC_FULL_WINDOW_ONLY`

## Scope

This task fetched the public-read `chimefrbcat2_exposure.h5` artifact to a
local, untracked path, verified its exact identity, and inspected its HDF5
structure before any T-truncated exposure construction. The source bytes are
not committed or redistributed.

The task does not compute per-source exposure values, construct derived rows,
fit or score a model, create a prediction or result artifact, or change a claim
or knowledge entry.

## Rights Boundary

The TASK-0910 rights decision remains controlling:

- local analysis is allowed for the public source with citation;
- source-byte redistribution is not cleared because the DataCite rights list is
  empty;
- bulk derived-row publication is not cleared;
- repository output remains metadata-only.

The downloaded file stayed at `C:\tmp\chimefrbcat2_exposure.h5`. It is not part
of this PR.

## Fetch And Identity

Source endpoint:

```text
https://cadc-west-01.canfar.net/vault/files/AstroDataCitationDOI/CISTI.CANFAR/25.0066/data/exposure/chimefrbcat2_exposure.h5
```

Observed identity:

| Field | Value |
| --- | --- |
| HTTP status | `200` |
| Exact bytes | `216024090` |
| SHA-256 | `cd8411f92d0ac31bd05dff47f62797638c354444de27a5c056113ca00470d514` |
| HTTP Digest | `md5=07nuxuH01/ftr1AE8Nmocg==` |
| Local MD5 | `d3b9eec6e1f4d7f7edaf5004f0d9a872` |
| Local MD5 in base64 | `07nuxuH01/ftr1AE8Nmocg==` |
| HTTP Last-Modified | `Fri, 12 Dec 2025 00:20:43 GMT` |
| Vault-list modified metadata | `2026-01-05T23:36:49Z` |

The local MD5 matches the HTTP Digest exactly. The HTTP object timestamp and
vault-list metadata timestamp differ, so both are retained instead of silently
choosing one as the source version.

## Deterministic Inspection

The file was inspected read-only with `h5py 3.16.0`. Checksum commands used
PowerShell `Get-FileHash` over the downloaded bytes. The structural inspection
enumerated root attributes, groups, datasets, shapes, dtypes, chunks,
compression, and dataset attributes without deriving exposure rows.

Root attributes include:

| Attribute | Value |
| --- | --- |
| `catalog` | The Second CHIME/FRB Catalog of Fast Radio Bursts |
| `datatype` | Exposure |
| `doi` | `10.11570/25.0066` |
| `instrument` | CHIME/FRB |
| `start_date` | `2018-09-04` |
| `end_date` | `2023-09-15` |
| `t_res` | `12.0` |

The root contains exactly two datasets:

| Dataset | Shape | Type | Chunk | Compression | Unit |
| --- | ---: | --- | ---: | --- | --- |
| `/upper` | `[201326592]` | `float64` | `[131072]` | gzip | seconds |
| `/lower` | `[201326592]` | `float64` | `[131072]` | gzip | seconds |

Both datasets declare:

- one dimension labelled `pixel`;
- HEALPix `NSIDE=4096`, `RING` ordering;
- ICRS celestial coordinates, equinox J2000;
- `201326592 = 12 * 4096^2` pixels;
- integrated exposure during periods when the system was operational and at
  nominal sensitivity.

## Schema-Gate Decision

`CONSTRUCTION_BLOCKED_STATIC_FULL_WINDOW_ONLY`.

The HDF5 file is a pair of cumulative full-window sky maps. It has no time
dimension, timestamp dataset, interval boundaries, or per-interval exposure
dataset. The root-level `start_date`, `end_date`, and `t_res` describe the map
production context but do not retain the time bins needed to integrate only up
to a split time `T`.

Therefore neither `exp_up(<=T)` nor `exp_low(<=T)` can be reconstructed from
this artifact without using exposure accumulated after `T`. Doing so would
violate the no-leakage contract in TASK-0877.

This reading is consistent with the official Catalog 2 description of exposure
as cumulative over the observing period and with the CHIME/FRB exposure-map
documentation, where temporal resolution is used while accumulating a final
HEALPix map rather than retained as an output axis:

- [Catalog 2 preprint](https://arxiv.org/abs/2601.09399)
- [CHIME/FRB exposure handbook](https://chimefrb.github.io/handbook/frb-exposure/)
- [CHIME/FRB exposure-map example](https://chime-frb-open-data.github.io/exposure/)

## Next Allowed Step

Do not start T-truncated construction from this HDF5 file. A future,
maintainer-approved source scout may look for either:

- a genuinely time-indexed exposure product with explicit interval boundaries;
- an upstream per-interval operational/sensitivity source from which pre-T maps
  can be reconstructed under the same rights boundary.

Because this schema gate is blocked, TASK-0930 does not create a construction
task or guess a new canonical task identifier.

## Limitations

- The audit establishes file identity and exposed HDF5 structure, not the
  scientific correctness of every pixel value.
- No exposure values were joined to FRB positions or source rows.
- No bulk source or derived bytes are committed.
- The difference between the HTTP and vault-list modification timestamps needs
  to remain visible in future source-version checks.
- A new upstream product could change the readiness decision and would require
  a new checksum pin rather than mutation of this frozen identity.

## Output Routing

- Task verdict: `CHECKSUM_PINNED_CONSTRUCTION_BLOCKED_STATIC_FULL_WINDOW_ONLY`.
- Canonical destination: metadata-only source manifest, license-registry update,
  and this review note.
- Review tier: none; this is source/schema readiness, not a scientific result.
- Gate A: not applicable.
- Gate B: not applicable.
- Result impact: no `RESULT-*` created or modified.
- Prediction impact: no `PRED-*` created or modified.
- Claim impact: none.
- Knowledge impact: none.
- Construction impact: blocked until a genuinely time-indexed source is pinned.
