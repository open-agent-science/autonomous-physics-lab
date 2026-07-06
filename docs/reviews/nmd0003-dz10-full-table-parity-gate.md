# NMD-0003 Canonical DZ10 Full-Table Parity Gate (Local-Only)

- Task: `TASK-0911`
- Domain: nuclear physics (source/parity readiness only)
- Run date: `2026-07-06`
- Builds on: `TASK-0878`
  ([canonical-dz10-reference-wrapper.md](canonical-dz10-reference-wrapper.md)),
  `TASK-0853` ([canonical-dz-parity-reference-scout.md](canonical-dz-parity-reference-scout.md))
- Verdict: **`DZ10_FULL_TABLE_PARITY_PASS`**

## Scope

This gate validates a license-clear, local, externally supplied copy of the
canonical AMDC DZ10 artifacts against the `TASK-0878` pinned identity and runs
full-table parser-coverage, printed-precision, smoke-fixture, and lookup checks
over all rows. The existing `TASK-0823` published-equation variant is compared
**only as a diagnostic**.

It does **not** vendor AMDC bytes, port the DZ10 Fortran, claim canonical
model parity, create a residual benchmark, freeze predictions, or mutate
`TASK-0823` code paths, `RESULT-0025`, or any `CLAIM`/`KNOW`/`PRED` artifact.

## Source Identity (License-Clear Local Fetch, Not Vendored)

Both artifacts were fetched from the official IAEA-NDS AMDC theory directory
to a disposable local cache and verified against the `TASK-0878` pins before
any parsing. The bytes stay outside the repository, matching the recorded
`source_bytes_redistribution: not_cleared` posture (local analysis with
citation; no re-hosting).

| Artifact | Locator | Expected / observed bytes | SHA-256 match |
| --- | --- | --- | --- |
| DZ10 table | `https://www-nds.iaea.org/amdc/theory/du_zu_10.feb96` | 196,049 / 196,049 | yes (`b80d64ca…c7ea7b`) |
| DZ10 Fortran | `https://www-nds.iaea.org/amdc/theory/du_zu_10.feb96fort` | 12,231 / 12,231 | yes (`cccc8406…5a25a`) |

## Gate Checks (Full Table)

Runner:

```bash
python3 scripts/run_nmd0003_dz10_full_table_parity_gate.py --cache-dir <local-amdc-cache>
```

| Check | Result |
| --- | --- |
| Row count | **9,311 parsed = 9,311 expected**; strict (Z, A) uniqueness enforced by the parser |
| Coverage | Z ∈ [2, 122], A ∈ [4, 297], N ∈ [1, 207] |
| Printed-precision round-trip | re-rendering every row at the advertised `i5, i5, f10.3` format and re-parsing reproduces all 9,311 rows exactly (max abs delta `0.0` ≤ 0.001 MeV) |
| Smoke fixture (`TASK-0853`, 6 rows) | 6/6 present, max abs delta `0.0` MeV (tolerance 5.0e-4) |
| Lookup (`lookup_dz10_mass_excess_mev`) | all fixture keys return the printed table values |

All checks pass, so the wrapper's parser and lookup path are validated against
the complete canonical table at the printed 0.001 MeV precision.

## Published-Variant Diagnostic (Not Parity)

The `TASK-0823` published-equation variant
(`PUBLISHED_DZ10_FULL_COEFFICIENTS` → binding energy → mass excess) was
compared against all 9,311 table rows, as a diagnostic only:

| Statistic | Value (MeV, abs delta) |
| --- | ---: |
| Mean | 44.51 |
| Median (p50) | 38.21 |
| p90 | 92.88 |
| p99 | 138.87 |
| Max | 160.51 (Z=70, A=252) |

The worst rows sit in the far-from-stability heavy region (Z=70–72,
A=251–256). These magnitudes confirm the standing `TASK-0878` reading: the
published-equation variant is **not** the canonical table generator
(`diagnostic_only_not_canonical_parity`), and nothing in this gate upgrades
it. Canonical model parity would require a maintainer-approved port of the
pinned DZ10 Fortran in a separate task; this gate only establishes that the
canonical table itself is now locally verifiable end-to-end.

## New Deterministic Tooling (Committed)

- `physics_lab/engines/nmd0003_dz10_full_table_parity_gate.py` — pure gate
  logic: pinned-identity verification, byte-independent
  `evaluate_parsed_table` checks, and the diagnostic summary.
- `scripts/run_nmd0003_dz10_full_table_parity_gate.py` — local-only CLI
  runner; exits 0 with `SOURCE_BYTES_NOT_AVAILABLE` when the cache is absent,
  exits 1 only on a contested identity or failed check.
- `tests/test_dz10_full_table_parity_gate.py` — covers the clean skip without
  bytes, the contested unpinned-bytes path, pin metadata, and the check logic
  on the committed smoke fixture; a full-table integration test runs only when
  `APL_DZ10_CACHE_DIR` points at a valid local cache and skips cleanly
  otherwise (verified in both modes).

## Limitations

- The gate validates table identity, parser coverage, printed-precision
  round-trip, and lookup behaviour; it does not validate the physical
  correctness of DZ10 values or provide a canonical model implementation.
- The published-variant deltas are diagnostic context only; no threshold is
  attached and no verdict depends on them.
- The local cache is disposable; any future upstream change to the AMDC files
  requires a fresh scout and new pinned identity, not a mutation of the
  `TASK-0878` metadata.

## Output-Routing Summary

- **Task verdict:** `not_applicable` (source/parity readiness; the gate
  verdict is `DZ10_FULL_TABLE_PARITY_PASS`).
- **Canonical destination:** this review note plus the committed gate engine,
  runner, and tests listed above.
- **Review tier:** none (no tiered artifact produced).
- **Gate A / Gate B:** not applicable (no RESULT packaged).
- **Claim impact:** none. **Knowledge impact:** none.
- **Result artifact impact:** none; `RESULT-0025` and all nuclear artifacts
  are byte-unchanged.
- **Publication blocker:** none for this gate. Canonical DZ10 **model** parity
  (Fortran port) remains open as a separate maintainer-approved follow-up;
  bulk redistribution of AMDC bytes remains not cleared.
- **Follow-up status:** the Fortran-port recommendation is advisory only; this
  task intentionally files no proposal or queue item, and the maintainer may
  queue it (or not) at closeout.
