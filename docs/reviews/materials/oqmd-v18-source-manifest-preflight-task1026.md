# TASK-1026: OQMD v1.8 source-manifest preflight

**Task:** TASK-1026  
**Date:** 2026-07-13  
**Mode:** planning and source metadata only

## Scope and no-peek boundary

This packet checks the public source identity, license posture, field-semantics gate,
and a future overlap plan for MD-0002. It does not download the OQMD dump, inspect
rows, select materials, count overlaps, construct a dataset, or run metrics.

## Official source metadata

| Item | Recorded value |
|---|---|
| Official landing page | https://www.oqmd.org/download/ |
| Release | OQMD v1.8 |
| Release artifact | `qmdb__v1_8__022026.sql.gz` |
| Artifact locator | https://static.oqmd.org/static/downloads/qmdb__v1_8__022026.sql.gz |
| Advertised size | 21.1 GB |
| License | CC BY 4.0 |
| License URL | https://creativecommons.org/licenses/by/4.0/ |
| Metadata observation | HTTP 200, 2026-07-13 UTC |

The official page identifies the release, locator, advertised size, and license.
The 21.1 GB artifact was intentionally not retrieved.

## Retrieval identity and checksum

`sha256: null` and `checksum_status: not_computed` are intentional. A checksum of
the advertised artifact cannot be asserted without retrieving the exact bytes.
Any future acquisition task must record retrieval timestamp, byte size, response
metadata, and SHA-256 before parsing or row selection. No digest is inferred from
the URL or release label.

## Property-semantics gate

The download page does not provide a machine-readable field contract for candidate
computed-property fields: meanings, units, calculation provenance, and missingness
rules remain unverified. The checked official OQMD API documentation routes
(`/oqmdapi/`, `/oqmdapi/docs`) did not provide a usable contract (HTTP 404 on
2026-07-13). This is not evidence that OQMD lacks such documentation; it means the
required semantics were not established by this preflight.

Until the field contract is pinned, values must not be compared with MD-0002 or
used to define a bounded sample. Formation-energy-like fields must not be assumed
interchangeable with another provider's field.

## Future bounded-acquisition contract

After semantics are independently pinned, a follow-up task may define a small row
cap and an explicit field whitelist. It must keep computed and measured quantities
separate, bind every row to the OQMD release, and screen composition, structure,
and provider-reference overlap with MD-0002 before any scientific split. No value
overlap count or metric is authorized by this packet.

## Decision

**`BLOCKED_PROPERTY_SEMANTICS`**

The source identity and license are usable for planning, but the property contract
is not sufficiently pinned for bounded acquisition. No Gate A/B, RESULT, CLAIM,
PREDICTION, or KNOWLEDGE artifact is produced.

## Output routing

This is a maintainer-facing materials review note. It is not a dataset, result,
claim, prediction, or knowledge artifact. A future acquisition task must resolve
the semantics blocker and create a separate no-peek overlap ledger.
