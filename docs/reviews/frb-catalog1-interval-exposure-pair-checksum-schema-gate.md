# FRB Catalog 1 Interval Exposure Pair Checksum And Schema Gate

- Task: `TASK-0947`
- Domain: radio transients astrophysics
- Gate date: 2026-07-08
- Fixed epoch: `T = 2019-07-02`
- Verdict: `GATE_PASS`

## Scope

This gate locally fetched the two official CHIME/FRB Catalog 1
interval-bounded exposure files, pinned their exact identities, and inspected
their NPZ/NPY schemas before any exposure construction. The source bytes
remain outside Git and are not redistributed.

The gate fixes the five Decision Day D2-1 conditions for one epoch only. It
does not activate the campaign, construct per-source exposure, join catalog
rows, fit a model, register a prediction, create a result, or change a claim
or knowledge artifact.

## Source And Rights Boundary

The pair belongs to dataset DOI `10.11570/21.0007` and accompanies The First
CHIME/FRB Catalog. Public analysis with citation is allowed, but no explicit
source-byte redistribution license is recorded. The repository output is
therefore metadata-only.

Official source surfaces:

- CANFAR deposit `AstroDataCitationDOI/CISTI.CANFAR/21.0007`;
- CHIME/FRB Catalog 1 exposure tutorial:
  <https://chime-frb-open-data.github.io/exposure/>;
- paper DOI `10.3847/1538-4365/ac33ab`.

## Pinned File Identity

| Role | Exact bytes | SHA-256 | HTTP Digest match | Last-Modified |
| --- | ---: | --- | --- | --- |
| Upper (`_U_`) | 186745827 | `088a0617104e5400dc12a8bcaf12621f3c61e82cab3eadc3f842cd6da7018536` | yes, MD5 `722ae3618c44730007f25afe386c2e1c` | 2021-06-03 13:13:19 GMT |
| Lower (`_L_`) | 12800403 | `e8cc1a47b916fc5cb89f6df3ea0f07d57d5b2a1b22262e9ead57937100b5966a` | yes, MD5 `38dd9ad23783f70ffb0c7431124dfa5b` | 2021-06-03 13:11:42 GMT |

Both HTTP responses returned status 200, the expected
`application/octet-stream` content type, and exact listing sizes. Future
fetches must match both SHA-256 and byte count; changed upstream bytes require
a new source-version review.

## Deterministic NPZ Inspection

Each file is a ZIP-deflated NPZ with exactly one member:
`exposure.npy`.

| Property | Upper | Lower |
| --- | ---: | ---: |
| NPY version | 1.0 | 1.0 |
| Shape | `[118136832]` | `[118136832]` |
| Dtype | `float64` | `float64` |
| Order | C | C |
| Uncompressed bytes | 945094784 | 945094784 |
| Finite values | 118136832 | 118136832 |
| Non-finite values | 0 | 0 |
| Nonzero values | 99870905 | 5186812 |
| Fractional values | 0 | 0 |

The payload does not embed dates, transit role, NSIDE, HEALPix ordering,
coordinate frame, temporal resolution, or units. Those semantics are carried
by the checksum-pinned filenames and the official tutorial.

The tutorial fixes:

- HEALPix `NSIDE=4096`, full-sky length `201326592`;
- prefix-fill into the HEALPix array, with remaining pixels zero/UNSEEN;
- default healpy `RING` ordering;
- ICRS/celestial coordinate lookup;
- temporal resolution `4 s`;
- conversion `exposure_hours = 4 * exposure_count / 3600`.

The tutorial's example variable names swap the `_U_` and `_L_` filenames.
This gate treats the filename suffix as the role identity. The frozen score
uses their sum, so that documentation inconsistency cannot change the total
score.

## Five-Condition Decision

| D2-1 condition | Status | File-level and frozen-contract evidence |
| --- | --- | --- |
| Source identity as of T | Fixed | Exact names, bytes, SHA-256, HTTP Digest matches, Last-Modified headers, and NPZ schemas are pinned. |
| Exposure/sensitivity strictly up to T | Fixed | Both filenames encode `2018-08-28_2019-07-02`; only these two hashes are admitted. |
| No post-T leakage | Fixed | Model-visible exposure is limited to this pair. Catalog 2 full-window exposure, later morphology, and later associations are forbidden features. |
| Repeat-label reveal strictly after T | Fixed | Features freeze before labels. Labels come only from the checksum-pinned later Catalog 2 snapshot; positive status requires repeat evidence after T. |
| Exact scoring rule | Fixed | `score_pre_t = log1p(E_upper_hours + E_lower_hours)`, with `E_hours = 4 * count / 3600`. |

## Cross-Catalog Semantics

The route is fixed rather than silently harmonized:

1. Use the Catalog 1 start `2018-08-28`; do not trim it to Catalog 2's
   `2018-09-04` start.
2. Use only the Catalog 1 4-second count conversion; do not mix the Catalog 2
   12-second product.
3. Use Catalog 1-native exposure and pre-T positions as features. Catalog 2
   is a strictly later reveal surface only.
4. Support exactly one epoch, `2019-07-02`. No arbitrary-T interpolation,
   subtraction, or inferred interval series is allowed.

These choices prevent the known framework-shift caveats from being hidden.
They do not assert that Catalog 1 and Catalog 2 exposure pipelines are
scientifically equivalent.

## Verdict

`GATE_PASS`.

The official pair is checksum-pinned, structurally readable, bounded at the
single approved epoch, and sufficient to fix the five D2-1 conditions. This
is a source feasibility pass only. Full campaign activation remains a
separate maintainer decision, exactly as required by D2-1.

## Stop Conditions For The Next Stage

Stop before construction if:

1. either file's byte count or SHA-256 changes;
2. an epoch other than `2019-07-02` is requested;
3. Catalog 2 full-window exposure or morphology enters the pre-T feature
   surface;
4. labels are read before feature freeze or lack post-T repeat evidence;
5. the scoring rule differs from the frozen exposure-only formula;
6. raw NPZ bytes or bulk derived rows would be committed;
7. no explicit maintainer campaign-activation decision exists.

## Output Routing

- Task verdict: `not_applicable`; source/schema gate verdict is
  `GATE_PASS`.
- Canonical destinations: the metadata-only source manifest and this gate
  note.
- Review tier: `none`.
- Gate A / Gate B: not applicable.
- Data impact: no source bytes or derived rows committed.
- Result / PRED impact: none.
- Claim impact: none.
- Knowledge impact: none.
- Construction impact: still awaiting a separate maintainer activation
  decision.
- Limitations: one epoch only; NPZ semantics depend on the official companion
  tutorial; Catalog 1/Catalog 2 pipeline equivalence is not claimed.
