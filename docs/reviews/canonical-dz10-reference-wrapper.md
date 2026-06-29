# Canonical DZ10 Reference Wrapper

**Task:** `TASK-0878`
**Domain:** nuclear physics
**Depends on:** `TASK-0853`
**Verdict:** `PARITY_REFERENCE_WRAPPER_READY_FULL_TABLE_PARITY_NOT_CLAIMED`

## Scope

This task implements the metadata-only wrapper route allowed by the canonical
DZ10 parity scout. It does not vendor AMDC source bytes, does not modify the
existing TASK-0823 published-variant code path, does not mutate `RESULT-0025`,
and does not create any prediction, reveal, CLAIM, or KNOW artifact.

The implementation adds `physics_lab.engines.nmd0003_canonical_dz10_reference`,
which records the accepted AMDC DZ10 locator/checksum metadata, parses a local
DZ10 mass-excess table copy when one is supplied, exposes a strict `(Z, A)`
lookup, and validates the accepted smoke fixture from `TASK-0853`.

## Source-Rights Boundary

The reference remains metadata-only by default:

| Artifact | Locator | SHA-256 | Policy |
| --- | --- | --- | --- |
| DZ10 table | `https://www-nds.iaea.org/amdc/theory/du_zu_10.feb96` | `b80d64caf878ed837b5544d22920e4499d4869053d934d0068c5aab0bcc7ea7b` | source bytes not vendored |
| DZ10 Fortran | `https://www-nds.iaea.org/amdc/theory/du_zu_10.feb96fort` | `cccc8406cfdd0fb79c11ace0dcae2b06df443fa4c4fc852f3114b657a125a25a` | source bytes not vendored |

The wrapper accepts a local externally supplied table copy and parses the AMDC
format `i5, i5, f10.3` (`Z`, `A`, mass excess in MeV). The repository commits
only a six-row smoke fixture already printed in the scout note, not the full
9311-row table.

## Smoke Fixture

The parser test covers the accepted scout rows:

| Z | A | Mass excess (MeV) |
| ---: | ---: | ---: |
| 8 | 16 | -5.150 |
| 37 | 90 | -78.959 |
| 50 | 132 | -76.052 |
| 82 | 208 | -22.621 |
| 92 | 238 | 47.483 |
| 122 | 297 | 223.211 |

`validate_dz10_smoke_fixture` requires all six keys to be present and to match
within `0.0005 MeV`, half of the table's printed `0.001 MeV` precision.

## Diagnostic Against TASK-0823 Variant

The wrapper also includes a diagnostic conversion from the existing TASK-0823
published-equation binding-energy variant to mass excess on supplied rows. On
the smoke fixture this diagnostic is intentionally not a parity pass: the max
absolute difference is larger than `1 MeV` (the local smoke test only asserts
this broad non-parity condition). This preserves the TASK-0823 boundary: the
published-equation variant remains useful, but it is not canonical AMDC parity.

## Remaining Full-Parity Gate

A future benchmark task can now use this wrapper to run full parity once one of
the following is available:

1. a local/generated cache containing the AMDC DZ10 table and Fortran bytes with
   the recorded SHA-256 checksums; or
2. maintainer approval to vendor the source bytes or a normalized fixture.

That future task should require all supported generated mass-excess values to
match the 9311-row table to the printed `0.001 MeV` precision, then package a
separate benchmark result only if authorized. This PR does not attempt that full
formula parity gate.

## Output Routing

- **Task verdict:** `PARITY_REFERENCE_WRAPPER_READY_FULL_TABLE_PARITY_NOT_CLAIMED`.
- **Canonical destination:** code wrapper, tests, and this review note.
- **Review tier:** `none`; no RESULT/PRED/CLAIM/KNOW artifact.
- **Gate A status:** not attempted. **Gate B status:** not attempted.
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change.
- **Result impact:** no result mutation, no benchmark packaging, no prediction
  freeze, no reveal scoring.
- **Publication blocker:** full 9311-row parity still requires AMDC source bytes
  through a local/generated cache or a maintainer-approved vendoring decision.

## No-Claim Wording

This wrapper is a source-reference and parser surface only. It does not claim a
canonical DZ10 formula reproduction, a new nuclear-mass result, or improved
prediction quality.