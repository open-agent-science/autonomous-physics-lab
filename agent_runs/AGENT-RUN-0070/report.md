# AGENT-RUN-0070 - Atomic Yb/Sr Cross-Source Consistency Diagnostic (Exploratory)

**Task:** `TASK-0456`
**Outcome:** `CONSISTENT_WITHIN_UNCERTAINTY_EXPLORATORY_SOURCE_LIMITED`

## Summary

This run computes the first Atomic Yb/Sr cross-source diagnostic authorized by
the `TASK-0705` baseline-readiness gate. It compares the two committed
independent direct Yb/Sr frequency-ratio rows and reports a normalized
difference under the `COV_DIAGONAL_ONLY_DECLARED` independence policy. It is an
exploratory diagnostic: no constants-drift fit, new-physics inference,
prediction entry, claim, or canonical result is produced.

The computation is deterministic
(`scripts/atomic_yb_sr_consistency_diagnostic.py`). The two ratio values agree
to ~15 leading digits and differ at the ~1e-17 level, which is below float64
precision relative to a value near 1.2075, so the ratio difference is computed
with exact `Decimal` arithmetic from the committed value strings.

## Independence Banner

Beloy 2021 / BACON and Nemitz 2016 / RIKEN are fully independent: no shared
clock, frequency comb, network link, or geopotential systematic couples them, so
the cross-source off-diagonal is defensibly zero and the combined 1-sigma is a
diagonal quadrature sum. Under `COV_DIAGONAL_ONLY_DECLARED` this is an
exploratory diagnostic, **not** a headline cross-source consistency claim.

## Rows Compared

| Role | Row | Source | Yb/Sr ratio (committed) | Total 1σ (fractional) |
| --- | --- | --- | --- | --- |
| `cross_source_reference` | `ACR-0001-ROW-003` | Beloy 2021 / BACON | `1.2075070393433378482` | `6.8e-18` |
| `cross_source_target` | `ACR-0002-ROW-001` | Nemitz 2016 / RIKEN | `1.207507039343337749` | `4.56e-17` |

## Diagnostic Result

| Quantity | Value |
| --- | ---: |
| Difference (reference − target), absolute | `9.92e-17` |
| Difference (reference − target), fractional | `8.215e-17` |
| Combined 1σ (diagonal-only), absolute | `5.567e-17` |
| Combined 1σ (diagonal-only), fractional | `4.610e-17` |
| `|z|` | `1.782` |
| Uncertainty dominance (target / reference) | `6.71` |

**Interpretation:** the two independent Yb/Sr ratios agree at `|z| = 1.78`,
within the `2σ` no-tension threshold declared before inspection. There is no
tension at the probed precision. The comparison is dominated and limited by the
Nemitz 2016 uncertainty (~6.7× the Beloy 2021 uncertainty): it does not test
Beloy's 18-digit precision, so the diagnostic is explicitly source-limited.

## Limitations

- Exploratory diagonal-only diagnostic; `COV_DIAGONAL_ONLY_DECLARED` forbids a headline cross-source consistency verdict.
- Source-limited: the Nemitz 2016 total uncertainty dominates; Beloy 2021 precision is not tested by this comparison.
- Two rows only (one per source); not a population-level consistency test.
- Both source PDFs (arXiv preprints and the Nature / Nature Photonics versions of record) are not redistributed; only metadata, checksums, and committed values are used.
- No constants-drift fit, new-physics inference, prediction entry, RESULT/CLAIM artifact, or knowledge promotion.

## Output Routing Summary

- Task verdict: `PARTIALLY_VALID` (valid exploratory diagnostic, source-limited).
- Benchmark-level reading: `CONSISTENT_WITHIN_UNCERTAINTY` (exploratory, diagonal-only, source-limited).
- Canonical destination: `agent_runs/AGENT-RUN-0070/metrics.json`, `agent_runs/AGENT-RUN-0070/report.md`, `docs/reviews/atomic-yb-sr-cross-source-consistency-benchmark.md`.
- Review tier: `none`.
- Gate A status: `not_attempted`. Gate B status: `not_applicable`.
- Claim impact: `none`. Knowledge impact: `none`. Result impact: `no RESULT artifact created`.
- Publication blocker: exploratory diagonal-only and source-limited; no canonical consistency promotion without a maintainer-approved Gate A path.
