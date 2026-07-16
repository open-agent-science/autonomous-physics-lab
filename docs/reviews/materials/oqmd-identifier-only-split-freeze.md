# OQMD identifier-only split freeze (TASK-1053)

## Decision

**Verdict: `SPLIT_READY_FOR_BENCHMARK_PREFLIGHT`**

The deterministic split contains **172 rows in 172 reduced-composition groups**. Assigned row counts are **train 120**, **validation 26**, and **holdout 26**. The holdout minimum of 24 rows is satisfied, and no reduced composition crosses a partition boundary.

## Frozen method

- Algorithm: `composition_group_sha256_greedy_total_absolute_deficit`, version `1`.
- Salt: `oqmd-task1053-v1`.
- Grouping key: exact `reduced_composition`; all spacegroup variants of a composition are atomic.
- Group ordering: ascending SHA-256 of UTF-8 `oqmd-task1053-v1|<reduced_composition>`, with composition UTF-8 bytes as a collision tie-break.
- In-group row ordering: UTF-8 byte order of the decimal/text representation of `entry_id`.
- Target row counts: train `120`, validation `26`, holdout `26`.
- Greedy assignment: try each partition and minimize the total absolute deficit across all partitions after assigning the whole group; ties use train, validation, holdout order.

The YAML 1.2 file uses JSON-compatible serialization and records every ordered group and row assignment plus per-partition ordered manifests.

## Source identity

- Snapshot: `oqmd-live-api-2026-07-14`.
- Contract-declared upstream source SHA-256: `af8991aefda6f408a3ad33251aa5564f5fed37a7d527b696d68442971bc978a4`.
- Allowed identifier-only input: `C:\tmp\oqmd-identities-task1053.json`.
- Identifier-only envelope SHA-256: `17b0f9b8b59b1acfe1e97d48e4fa435ddc58a10f14417fd5ebea1b79595a16cd`.
- Input schema: exactly `entry_id`, `reduced_composition`, and `spacegroup` for each of 172 rows.

The upstream provenance hash and clean identifier-envelope hash have distinct scopes and are recorded separately.

## Verification

| Check | Result |
|---|---:|
| Unique entry IDs | 172 / 172 |
| Atomic reduced-composition groups | pass |
| Same-composition spacegroup variants coassigned | pass |
| Cross-partition composition leakage | none |
| Holdout rows | 26 (minimum 24) |
| Exact target counts | pass |

## Session identity and no-target attestation

Session identity: `task1053-clean-no-target-execution-v1`.

This was a clean no-target execution. The only dataset input accessed was `C:\tmp\oqmd-identities-task1053.json`. No target field, target value, target summary, or target metric was accessed or computed. Repository normalized/raw files, git, GitHub, and network resources were not accessed. Split membership depends only on the three permitted identifier fields and the frozen algorithm above.
