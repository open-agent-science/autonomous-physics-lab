# FRB Catalog 2 Time-Resolved Exposure-Map Source Pin

Task: `TASK-0910`
Domain: Radio transients astrophysics (FRB repeater selection-effect audit)
Mode: metadata-only source-artifact pin of the time-resolved / full-sky exposure-map product
Outcome: `READY PIN` (source pinned; not `SOURCE_BLOCKED`)
Verdict: `EXPOSURE_MAP_SOURCE_PINNED_METADATA_ONLY_CHECKSUM_PENDING`
Run date: `2026-07-02`

## Scope And Non-Goals

This task pins exactly one source artifact: the CHIME/FRB Catalog 2 time-resolved /
full-sky **exposure-map** product at dataset DOI `10.11570/25.0066`. `TASK-0852`
pinned only the `chimefrbcat2.csv` catalog table, and `TASK-0877` specified a
leakage-safe T-truncated pre-T exposure view while explicitly flagging the
exposure-map product as an **additional, un-pinned source-clearance item** (its
review note, section 5, calls this "an additional source-clearance item (locator +
SHA-256 + redistribution decision) that a future step must pin before
construction"). This task is that step.

It records **metadata only**. It does **not** fetch or commit exposure-map bytes,
catalog rows, numeric truncated exposure values, morphology features, labels, `PRED`
entries, or `RESULT` artifacts. It builds or scores no model, freezes no prediction,
creates no `agent_runs/AGENT-RUN-*`, and promotes no claim or knowledge entry. It
uses no FRB-population, morphology, repeater-prediction, discovery, or claim wording.

Inputs reviewed:

- [frb-catalog2-t-truncated-exposure-split.md](frb-catalog2-t-truncated-exposure-split.md)
- [frb-catalog2-temporal-split-exposure-baseline.md](frb-catalog2-temporal-split-exposure-baseline.md)
- [frb-chime-access-reverify-readiness.md](frb-chime-access-reverify-readiness.md)
- [frb-chime-source-readiness-temporal-split-scout.md](frb-chime-source-readiness-temporal-split-scout.md)
- [../published-source-dataset-standard.md](../published-source-dataset-standard.md)
- `TASK-0852`, `TASK-0877`, `TASK-0839`

Committed outputs:

- [../../data/radio_transients/frb_catalog2_exposure_map_source_manifest.yaml](../../data/radio_transients/frb_catalog2_exposure_map_source_manifest.yaml)
- this review note
- one metadata-only entry in [../../data/DATA_LICENSES.yaml](../../data/DATA_LICENSES.yaml)

## 1. Why A Separate Source Item, And Why This Is Now Pinnable

The released `chimefrbcat2.csv` exposes per-source exposure only as **full-window**
`exp_up` / `exp_low` (integrated over the whole observing window). It carries no
per-epoch or time-resolved exposure column, so a truncated-at-T value cannot be
derived from the CSV at all. The only released materials that can be integrated up
to an arbitrary split time T at single-source sky granularity are the
**time-resolved / full-sky exposure-map products** at the same dataset DOI. Pinning
those maps is therefore the precondition for the future T-truncated construction.

Under `TASK-0839` the exposure-map product could not be pinned because the CANFAR
citation-landing page for `10.11570/25.0066` returned `404`/`500` and the CHIME
portal was `503`, so no page listing the exposure files could be reached. The
maintainer has since resolved that access blocker by reading the file identity
directly from the **CANFAR vault storage listing**, which shows the product with
Public read access. With a concrete file name, size, vault path, owner, modified
date, public-read status, DOI, deposit, and a checksum plan, the artifact identity,
access, versioning, and verification route are all reviewable — so this is a
**successful pin**, not `SOURCE_BLOCKED`.

## 2. Pinned File Identity

| Field | Value |
| --- | --- |
| File name | `chimefrbcat2_exposure.h5` |
| Format | HDF5 (`.h5`) |
| Size (display) | 206.02 MB (CANFAR vault UI; exact byte count to be confirmed at first fetch) |
| Vault path | `vault:/AstroDataCitationDOI/CISTI.CANFAR/25.0066/data/exposure/chimefrbcat2_exposure.h5` |
| Vault list URL | `https://www.canfar.net/storage/vault/list/AstroDataCitationDOI/CISTI.CANFAR/25.0066/data/exposure` |
| VOSpace URI | `vos://cadc.nrc.ca~vault/AstroDataCitationDOI/CISTI.CANFAR/25.0066/data/exposure/chimefrbcat2_exposure.h5` |
| DOI | `10.11570/25.0066` |
| Deposit | `AstroDataCitationDOI/CISTI.CANFAR/25.0066` |
| Publisher / publication year | CADC / 2025 |
| Read access | Public |
| Owner | `ssiegel` |
| Last modified (UTC) | `2026-01-05T23:36:49` |
| Retrieval date | `2026-07-02` (this pin) |

Expected file list: a **single consolidated** HDF5 file, `chimefrbcat2_exposure.h5`
(HDF5, ~206.02 MB). If the first license-clear listing reveals additional or renamed
exposure files, the manifest file list and checksum plan must be updated before any
construction.

## 3. Checksum Plan (No Hash Fabricated)

No bytes were downloaded and **no SHA-256 was fabricated**. The plan is:

- **Algorithm:** SHA-256, `expected_sha256: TO_BE_PINNED_AT_FIRST_LICENSE_CLEAR_FETCH`.
- **When:** at the first license-clear fetch of `chimefrbcat2_exposure.h5`.
- **Bytes:** the 206.02 MB display value is recorded as "to be confirmed at first
  fetch"; the exact byte count is pinned alongside the hash.
- **Verify:** compute `sha256` of the fetched file, record the hash and exact byte
  count in the manifest, and freeze the manifest to `pinned_public_locator` before
  integrating any exposure value. Any later reprocessing produces a **new** pinned
  artifact rather than silently changing a frozen value, which keeps the future
  pre-T knowledge state frozen against reprocessing drift.

This mirrors the existing `chimefrbcat2.csv` posture, where the checksum was
computed only at a license-clear fetch and never fabricated at scout time.

## 4. Rights / Reuse Posture (3-Question Source-Rights Framework)

The exposure-map product carries the **same publisher-permission caveat** as the
Catalog 2 catalog rows: Public read on the CANFAR vault, but the DataCite
`rightsList` is empty and there is no explicit open-data redistribution licence on
the deposit (cite-the-paper courtesy only). Applying the repository's 3-question
framework from
[../published-source-dataset-standard.md](../published-source-dataset-standard.md):

| Question | Determination (`2026-07-02`) |
| --- | --- |
| **Local analysis** allowed? | **Yes** by default — publicly released for analysis; the CHIME/FRB open-data courtesy asks only that the relevant papers be cited. Allowed once a license-clear copy is in hand. |
| **Source-bytes redistribution** allowed? | **No** (default). No redistribution licence is recorded (empty `rightsList`; cite-the-paper courtesy only). Do **not** vendor `chimefrbcat2_exposure.h5`. |
| **Derived-rows publication**? | **Unknown / not cleared** for bulk publication. Individual factual exposure values may be treated as extractable facts with attribution, but a redistributable derived-exposure dataset needs maintainer licence clearance or recorded permission. |

Repository mapping: `blocker_type = T4_snapshot_approval` — the source is admissible
and pinnable, but any bytes need a maintainer-approved, checksum-pinned snapshot
fetch. The repository policy for this artifact is
`metadata_only_no_exposure_map_bytes_vendored`: **only metadata may be committed, not
exposure-map bytes.**

## 5. Access-Policy Nuance (Reviewable)

Recorded explicitly so a future fetch targets the working surface:

- **Citation-landing page** `https://www.canfar.net/citation/landing?doi=25.0066`
  returned a `444`/login-or-server error on `2026-07-02` (consistent with the
  `404`/`500` seen under `TASK-0839`). It is not a reliable retrieval route right now.
- **Vault storage listing**
  `https://www.canfar.net/storage/vault/list/AstroDataCitationDOI/CISTI.CANFAR/25.0066/data/exposure`
  shows `chimefrbcat2_exposure.h5` with Public read access (owner `ssiegel`). This is
  the reviewable access route the maintainer used to resolve the earlier blocker.

Reading: access is via the vault storage listing / file service, **not** the
citation-landing page. This nuance does not change the redistribution posture (still
metadata-only, empty `rightsList`); it only records which surface actually serves the
file so a future fetch does not re-trip the landing-page failure.

## 6. Source-Rights Boundary Preserved

Nothing new is vendored. The manifest records the vault list URL, the direct vault
file path, the VOSpace URI, the storage file-endpoint pattern, the DOI, the deposit,
the file name / format / display size, the owner, the last-modified date, the rights
posture, the access-policy nuance, and a checksum plan — an APL-authored,
metadata-only source artifact. No exposure-map bytes, catalog rows, numeric truncated
exposure values, morphology features, labels, or derived rows are committed. The new
manifest is declared in `data/DATA_LICENSES.yaml` under the
metadata-only-source-manifest convention even though it carries no third-party data,
matching the existing metadata-only locator precedent in that registry.

The pin is recorded as a **sibling** manifest
(`frb_catalog2_exposure_map_source_manifest.yaml`) rather than an edit to
`frb_catalog2_source_manifest.yaml`, because the CSV manifest is regenerated from a
hardcoded payload by the exposure-baseline helper script and would silently drop any
in-file addition. A sibling keeps the exposure-map pin durable and single-sourced.

## 7. Verdict

`EXPOSURE_MAP_SOURCE_PINNED_METADATA_ONLY_CHECKSUM_PENDING`.

The time-resolved / full-sky exposure-map product `chimefrbcat2_exposure.h5`
(HDF5, ~206.02 MB, DOI `10.11570/25.0066`, Public read on the CANFAR vault) is pinned
with a reviewable locator, version/deposit, file list, rights determination, access
nuance, and a SHA-256 checksum plan. No bytes were fetched or committed and no hash
was fabricated. This is a successful pin, not `SOURCE_BLOCKED`: it unblocks the future
T-truncated exposure construction specified in `TASK-0877` while preserving the
metadata-only boundary and the no-claim posture.

## Output-Routing Summary

- Task verdict: `EXPOSURE_MAP_SOURCE_PINNED_METADATA_ONLY_CHECKSUM_PENDING`
  (source-readiness pin; `not_applicable` to the VALID/FALSIFIED benchmark vocabulary
  because no benchmark was run).
- Canonical destination: a metadata-only exposure-map source manifest under
  `data/radio_transients/`, this review note, and one metadata-only
  `data/DATA_LICENSES.yaml` entry.
- Review tier: `none`. Gate A: not attempted. Gate B: not attempted (no dataset,
  metric, prediction, or result produced).
- Benchmark / morphology impact: none. No model fitted, no metric scored.
- Claim impact: no claim change. Knowledge impact: no knowledge change.
- Result / PRED impact: no `results/` artifact, no `prediction_registry/` entry, no
  `agent_runs/AGENT-RUN-*`. No truncated exposure values, morphology features, or
  labels recorded.
- Data boundary: Public-readable source; empty DataCite `rightsList`; only metadata
  may be committed, not exposure-map bytes (`blocker_type = T4_snapshot_approval`).
  Bulk derived-row publication is `unknown`; individual factual values are a
  limited factual extract with attribution.
- Limitations: the exact byte count and SHA-256 are deferred to the first
  license-clear fetch (not fabricated here); the file list assumes a single
  consolidated HDF5 file per the maintainer-provided vault listing and must be
  re-checked if additional exposure files appear; the citation-landing surface is
  unreliable (444/500) so fetch must use the vault storage / file service; Catalog 1
  vs Catalog 2 framework-shift remains a confound to control when the truncated view
  is built (out of scope for this pin).
- Unblocks: the future T-truncated `exp_up(<=T)` / `exp_low(<=T)` construction
  specified in `TASK-0877` (design), under a separate maintainer-approved
  snapshot-fetch step that preserves the metadata-only boundary.
