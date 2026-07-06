# FRB Time-Indexed Exposure Source Scout After The Static-Map Blocker

- Task: `TASK-0934`
- Domain: radio transients astrophysics
- Run date: `2026-07-06`
- Builds on: `TASK-0930`
  ([frb-catalog2-exposure-map-checksum-schema-gate.md](frb-catalog2-exposure-map-checksum-schema-gate.md)),
  `TASK-0877`
  ([frb-catalog2-t-truncated-exposure-split.md](frb-catalog2-t-truncated-exposure-split.md)),
  `TASK-0910`
  ([frb-catalog2-exposure-map-source-pin.md](frb-catalog2-exposure-map-source-pin.md))
- Verdict: **`TIME_INDEXED_SOURCE_AMBIGUOUS`**

## Scope And Non-Goals

This scout searches official CHIME/FRB, CADC/CANFAR, and associated
publication/documentation surfaces for a genuinely time-indexed exposure
product, or an upstream interval-bounded operational/sensitivity source, able
to support the predeclared no-leakage `exp_up(<=T)` / `exp_low(<=T)` view from
the `TASK-0877` split specification.

Metadata only. This task fetched directory listings, DOI metadata, and
documentation pages. It did **not** fetch or commit value-bearing bulk bytes
(no `.h5`, `.npz`, or catalog-row downloads), did not construct truncated
exposure rows, did not join FRB positions, did not fit or score any model, did
not freeze a prediction, did not create a `RESULT`, and did not modify any
`CLAIM` or `KNOW` artifact. The `TASK-0930` checksum identity for
`chimefrbcat2_exposure.h5` and the recorded HTTP-versus-vault timestamp
discrepancy are preserved unchanged.

## Surfaces Checked (2026-07-06)

| Surface | Route | Status |
| --- | --- | --- |
| CANFAR vault deposit 25.0066 (Catalog 2) | VOSpace nodes API `cadc-west-01.canfar.net/vault/nodes/AstroDataCitationDOI/CISTI.CANFAR/25.0066/data` (+ `/exposure`, `/table`) | Listed: `additional_figures`, `dynamic_spectra`, `exposure`, `localizations`, `table`; `exposure/` holds exactly one file |
| CANFAR vault deposit 21.0007 (Catalog 1) | VOSpace nodes API `.../21.0007/data` (+ `/exposure`) | Listed: `additional_figures`, `exposure`, `localizations`, `waterfalls`; `exposure/` holds exactly two files |
| DataCite DOI records | `api.datacite.org/dois/10.11570/25.0066`, `.../10.11570/21.0007` | Read; no additional related data products listed |
| CHIME/FRB open-data portal | `chime-frb-open-data.github.io` (index, `data-releases/`, `exposure/`) | Read; six releases listed; no time-indexed exposure product |
| CHIME/FRB handbook | `chimefrb.github.io/handbook/frb-exposure/` | Read; per-day sensitivity metrics described as internal (pulsar metric files, Grafana) |
| `cfod` utility package | `github.com/chime-frb-open-data/chime-frb-open-data` README | Read; no exposure API, no date-range access functions |
| Catalog papers | arXiv `2601.09399` (Catalog 2), arXiv `2106.04352` (Catalog 1) | Read (abstract surfaces); Catalog 2 describes exposure as cumulative over the observing period |
| Collaboration extended-data portal | `www.chime-frb.ca/catalog2` | **HTTP 503 on two attempts**; contents unverifiable at scout time |

## Candidate-Source Table

### C1 — Catalog 2 consolidated exposure map (already pinned, blocked)

| Field | Value |
| --- | --- |
| Locator | `https://cadc-west-01.canfar.net/vault/files/AstroDataCitationDOI/CISTI.CANFAR/25.0066/data/exposure/chimefrbcat2_exposure.h5` |
| Publisher / owner | CADC / CHIME/FRB Collaboration (vault owner `ssiegel`) |
| Version / coverage | `start_date 2018-09-04`, `end_date 2023-09-15`, `t_res 12.0` (root attributes; `TASK-0930`) |
| Interval boundaries | **None.** Two cumulative full-window HEALPix datasets (`/upper`, `/lower`); no time axis, bins, or per-interval exposure |
| Transit semantics | Separate `/upper`, `/lower` datasets, seconds |
| Sky mapping | HEALPix `NSIDE=4096`, `RING`, ICRS (verified by `TASK-0930`) |
| Access / checksum | Public read; SHA-256 pinned (`cd8411f9…70d514`, 216024090 bytes) |
| Citation | CHIME/FRB Collaboration, ApJS, DOI `10.3847/1538-4365/ae3828`; dataset DOI `10.11570/25.0066` |

Leakage answer: cannot produce `exp_up(<=T)` / `exp_low(<=T)` for any interior
`T` without post-`T` leakage. Confirmed blocked; nothing new was found in the
25.0066 deposit tree (the `exposure/` directory still contains exactly the one
pinned file).

### C2 — Catalog 1 interval-bounded exposure map pair (new candidate)

| Field | Value |
| --- | --- |
| Locator (listing) | `https://cadc-west-01.canfar.net/vault/nodes/AstroDataCitationDOI/CISTI.CANFAR/21.0007/data/exposure` |
| Files | `exposure_int_20180828_20190702_transit_U_beam_FWHM-600_res_4s_0.86_arcmin.npz` (186,745,827 bytes); `exposure_int_20180828_20190702_transit_L_beam_FWHM-600_res_4s_0.86_arcmin.npz` (12,800,403 bytes) |
| Publisher / owner | CADC / CHIME/FRB Collaboration (vault owner `patelc14`, 2023-08) |
| Version / coverage | Fixed interval `2018-08-28 → 2019-07-02` encoded in the filenames; 4-second accumulation resolution; FWHM-600 beam |
| Interval boundaries | **Exactly one official boundary epoch: `2019-07-02`** (interval-bounded cumulative maps, not per-interval series) |
| Transit semantics | Separate upper (`_U_`) and lower (`_L_`) transit products; the small `L` file is consistent with a circumpolar-only lower-transit footprint (exact declination boundary unverified here) |
| Sky mapping | `0.86_arcmin` naming and the portal tutorial indicate HEALPix `NSIDE=4096`; ordering, coordinate frame, and units are **unverified** until a schema gate |
| Access / checksum | Public read via the vault file service (same `/vault/files/<path>` pattern as the pinned CSV/HDF5); SHA-256 + exact bytes computable at first license-clear fetch; HTTP Digest available per vault behaviour |
| Citation | CHIME/FRB Collaboration, The First CHIME/FRB Catalog, ApJS 257, 59 (2021), arXiv `2106.04352`; dataset DOI `10.11570/21.0007` |

Leakage answer: for the single choice `T = 2019-07-02` (a "Catalog 1 boundary
epoch", which the `TASK-0877` spec explicitly names as an admissible way to
choose `T`), these maps integrate observing time only up to `T`. No post-`T`
bytes enter the product, no missing intervals are inferred, and the cumulative
`TASK-0930` map is not reinterpreted. This is the only leakage-safe official
route found.

Semantic caveats that keep this route conditional:

- **Single epoch only.** `T` is restricted to `2019-07-02`; no other interior
  `T` is supported by any released product.
- **Window-start mismatch.** The Catalog 1 maps accumulate from `2018-08-28`,
  while the Catalog 2 exposure window starts `2018-09-04`. A pre-`T` view built
  from C2 includes ~7 days of exposure outside the Catalog 2 window; whether
  this is acceptable for the split baseline is a maintainer/semantics decision,
  not a leakage problem.
- **Pipeline-era differences.** Catalog 1 products use 4-second resolution and
  Catalog-1-era beam/sensitivity treatment (including its own bad-day
  exclusions); the Catalog 2 map records `t_res 12.0`. Cross-catalog
  equivalence of `exp_up`/`exp_low` semantics must be reviewed before
  construction.
- **Units and array layout unverified.** The `.npz` payload (`exposure` key per
  the portal tutorial), units, ordering, and coordinate frame need a
  deterministic schema gate before any construction task.

### C3 — Per-interval operational/sensitivity sources (internal only)

The CHIME/FRB handbook describes daily sensitivity tracking via reference-
pulsar metric files and Grafana metrics, and a bad-day exclusion rule
(days with relative RMS noise 10% above the median). No public release of
these per-day metrics, uptime logs, or interval tables was found on the
open-data portal, the CANFAR deposits, the DataCite records, or the `cfod`
package. Leakage answer: not evaluable — the surface is not publicly released.
Blocked as a public source unless the collaboration publishes it or the
maintainer obtains it through a recorded channel.

### C4 — Collaboration extended-data portal (`www.chime-frb.ca/catalog2`)

The Catalog 2 paper points to this portal for "extended figures and data". It
returned HTTP 503 on two attempts during this scout, so whether it exposes any
time-resolved exposure product could not be audited. Unverified; retry later.

### C5 — `cfod` utility package

Documentation/software surface only: no exposure API, no date-range access.
Not a data product; excluded as a candidate.

## Three-Question Source-Rights Framework

Applied separately per the repository convention (`TASK-0910` precedent):

| Question | C1 (25.0066) | C2 (21.0007) |
| --- | --- | --- |
| Local analysis | Allowed for the public source with citation (unchanged `TASK-0910` decision) | Allowed: DataCite record carries an explicit statement that the dataset is publicly available with a cite-the-paper/DOI request |
| Source-byte redistribution | Not cleared (empty DataCite `rightsList`; no open-data license) | Not cleared by default: the rights statement requests acknowledgement/citation but names **no** explicit redistribution license, so vendoring the `.npz` bytes stays blocked pending maintainer clearance |
| Bulk derived-row publication | Not cleared without maintainer permission or license | Not cleared without maintainer permission or license; individual factual exposure values with attribution remain the only default-safe extraction |

C2's rights posture is slightly stronger than C1's (an explicit public-
availability + citation statement instead of an empty rights list), but it is
still not an explicit open-data license; the repository's metadata-only
posture stays in force for both.

## Readiness Verdict

**`TIME_INDEXED_SOURCE_AMBIGUOUS`.**

- No genuinely time-indexed exposure product (per-day, per-interval, or
  arbitrary-`T`) exists on any official surface checked. In that narrow sense
  the original blocker stands.
- However, one bounded, leakage-safe official route exists: fix
  `T = 2019-07-02` and read `exp_up(<=T)` / `exp_low(<=T)` from the official
  Catalog 1 interval-bounded map pair (C2). The route is real but conditional
  on maintainer review of the cross-catalog semantics (window start, pipeline
  era, units) — and `T` cannot be varied.
- One official surface (C4) was unreachable at scout time, so the scout cannot
  certify that no further product exists there.

`READY` would overstate (no arbitrary-`T` product; C2 needs a semantics
decision); `BLOCKED` would understate (C2 is a genuine leakage-safe single-`T`
route the split spec explicitly anticipated). Ambiguous, with the stop
conditions below, is the honest reading.

## Stop Conditions Against Premature Construction

1. Do **not** start any T-truncated construction from the C1 static map
   (unchanged `TASK-0930` decision).
2. Do **not** construct from C2 until a maintainer accepts the single-epoch
   `T = 2019-07-02` route and its cross-catalog caveats, and a checksum/schema
   gate pins the two `.npz` files.
3. Do **not** infer per-interval exposure from root attributes, filenames, or
   any subtraction of C1-family maps across different windows.
4. A changed upstream object (new files in either deposit, a revived C4 portal
   with new products, or a future time-indexed release) requires a fresh
   source-version identity, not mutation of the pinned ones.

## Minimal Future Task Shape (Only If The Maintainer Clears The C2 Route)

One bounded checksum/schema-gate task, mirroring `TASK-0910`/`TASK-0930`:

- license-clear local fetch of the two Catalog 1 exposure `.npz` files; record
  exact bytes, SHA-256, and HTTP Digest against the vault listing sizes
  (186,745,827 and 12,800,403 bytes);
- deterministic read-only schema inspection: array keys, shapes, dtype,
  HEALPix `NSIDE`/ordering/coordinate frame, units, and upper/lower transit
  footprints;
- an explicit maintainer decision record on the `T = 2019-07-02` single-epoch
  semantics (window-start mismatch and pipeline-era differences) **before** any
  truncated-view construction task is queued;
- metadata-only outputs: a source manifest for the C2 pair plus a
  `data/DATA_LICENSES.yaml` entry; no bytes vendored, no rows derived.

## Limitations

- The scout audited public metadata surfaces on one date (2026-07-06); it
  cannot prove the non-existence of unreleased or portal-hosted products,
  especially with C4 returning 503.
- C2 schema facts (units, ordering, coordinate frame, exact lower-transit
  footprint) come from filenames and portal tutorial conventions and remain
  unverified until the schema gate.
- Deposit listings were read through the VOSpace nodes API; vault UI metadata
  (e.g., displayed sizes) can lag the file service and must be re-checked at
  fetch time.
- No statement here bears on FRB repeater classification, population claims,
  or any scientific hypothesis; this is source readiness and leakage control
  only.

## Output-Routing Summary

- **Task verdict:** `not_applicable` (source-readiness scout; the scout's
  single readiness verdict is `TIME_INDEXED_SOURCE_AMBIGUOUS`).
- **Canonical destination:** this review note,
  `docs/reviews/frb-time-indexed-exposure-source-scout.md`.
- **Review tier:** none (no tiered artifact produced).
- **Gate A / Gate B:** not applicable.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Dataset / benchmark / prediction / result impact:** none produced or
  modified; no value-bearing bytes fetched or committed.
- **Publication blocker:** none for this note; construction remains blocked
  pending the maintainer decision and the C2 checksum/schema gate described
  above.
