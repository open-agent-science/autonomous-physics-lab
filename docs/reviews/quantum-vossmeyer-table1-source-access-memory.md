# Quantum Vossmeyer Table 1 Source-Access Memory

**Task:** `TASK-0848`
**Campaign:** Quantum Size Effects
**Source ID:** `vossmeyer-1994-jpc-cds-absorption`
**Verdict:** `METADATA_ONLY_FALLBACK_MEMORY_RECORDED`

## Scope

This note records maintainer-inspected source-access memory for the Vossmeyer
1994 CdS Table 1 surface. It is metadata-only. It does not commit the ACS PDF,
screenshots, page scans, table images, publisher table text, quantum-dot rows,
benchmark inputs, metrics, RESULT/PRED artifacts, CLAIM updates, or KNOW
promotions.

The source remains a closed-source Tier 4 fallback under the Quantum
open-licensed-first policy. The READY ZnSe transfer route is not delayed or
competed with by this note.

## Maintainer-Inspected Metadata

| field | value |
| --- | --- |
| DOI | `10.1021/j100082a044` |
| article | Vossmeyer et al. 1994, Journal of Physical Chemistry |
| source surface | Article `Table 1` |
| inspected page | `7667` |
| local filename observed by maintainer | `j100082a044.pdf` |
| byte_size | `1669226` |
| checksum_sha256 | `not_recorded` |
| repository source-byte status | `not_committed` |
| extraction status | `blocked_no_value_bearing_extraction` |

The recorded byte size and filename are source-access memory only. They are not
a repository checksum, redistribution permission marker, or row-readiness
approval.

## Policy Classification

Vossmeyer remains `closed_source_tier_4_fallback`:

- ACS publisher content is DOI-pinned metadata only.
- Value-bearing extraction requires an explicit future license/ToS decision or
  maintainer-approved row-use decision.
- A future task may record checksum-only metadata for a maintainer-local copy,
  but the ACS article, page images, crops, screenshots, and table text remain
  out of git unless a reviewed reuse route permits them.
- Any future row curation still requires a separate extraction ledger and row
  readiness review; this note does not authorize `qd-*.yaml` rows.

## Routing

`data/quantum_dots/source_manifest.yaml` and `data/acquisition_queue.yaml` now
preserve the same closed-source fallback blocker wording and point to this
metadata-only memory note.

## Output-Routing Summary

- Canonical destination: this review note,
  `docs/reviews/quantum-vossmeyer-table1-source-access-memory.md`, plus
  metadata-only blocker wording in the quantum source manifest and acquisition
  queue.
- Review tier: `none`.
- Gate A status: not applicable.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- RESULT/PRED impact: none.
- Publication blocker: future value-bearing use requires explicit license/ToS
  or maintainer row-use decision, checksum metadata for the inspected copy, a
  table-structure extraction ledger, and row-readiness review.
