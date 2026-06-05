# Atomic Pizzocaro Yb/Sr Row-Admissibility Gate

**Task:** `TASK-0567`
**Campaign:** Atomic-Clock Residuals
**Source artifact:** `ACLOCK-SRC-ARTIFACT-2020-PIZZOCARO-VLBI`
**Verdict:** `PIZZOCARO_ROW_ADMISSIBILITY_BLOCKED`

## Scope

This review decides whether the pinned Pizzocaro et al. 2020 / INRIM-NICT
Zenodo source artifacts can be promoted into a value-bearing Atomic
`Yb/Sr` direct-row dataset. It does not fit constants drift, run a
cross-source benchmark, create predictions, promote claims, or write derived
constraints.

## Inputs Reviewed

- `TASK-0567`
- `data/atomic_clocks/source_manifest.yaml`
- `data/atomic_clocks/atomic_holdout_manifest.yaml`
- `docs/reviews/atomic-pizzocaro-source-artifact-review.md`
- `docs/reviews/atomic-row-role-schema-and-beloy-assignments.md`
- `docs/reviews/atomic-first-benchmark-covariance-policy.md`
- `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/provenance.yaml`
- `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/Yb-Sr-ratio-measurements-IPPP.csv`
- `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/Yb-Sr-ratio-measuremets.csv`

## Source Surface

The pinned Zenodo artifacts are legitimate source artifacts and carry an open
CC-BY-4.0 dataset license. They are not yet curated Atomic rows.

The two Yb/Sr CSV files expose several value-bearing surfaces:

| Source file | Source sections observed | Non-comment rows |
| --- | --- | ---: |
| `Yb-Sr-ratio-measurements-IPPP.csv` | Extended Data Figure 4a `IPPP` and `PPP` time-series sections | 20 |
| `Yb-Sr-ratio-measuremets.csv` | Figure 2a `VLBI` and `IPPP` time-series sections plus Figure 2b history rows | 26 |

The Figure 2b history section includes two `Thiswork` summary rows:
`IPPP` and `VLBI`. The time-series sections also expose per-window final
`Yb/Sr` values and one-sigma uncertainties for `VLBI`, `IPPP`, and `PPP`
processing paths.

## Row-Admissibility Decision

No `ACR-0002` row is committed in this task.

The blocker is not source retrieval or redistribution. The blocker is that the
committed source artifacts do not yet provide enough row-level semantics for a
single benchmark-ready Atomic direct row without a separate extraction ledger
or publication-table reconciliation:

1. **Source-file-to-row mapping is ambiguous.** The source package contains
   time-series `VLBI`, `IPPP`, and `PPP` sections plus Figure 2b history
   summaries. The repository has not frozen which surface is the row of record:
   a Figure 2b summary row, a source time-series aggregate, or a named
   processing-path row.
2. **Direct-vs-derived class is not locked.** The exposed `Yb/Sr` values are
   final link-analysis outputs assembled through H-maser chains and VLBI/IPPP
   or PPP processing. They may still be suitable direct frequency-ratio
   evidence, but the row class must explicitly say how the link-derived
   comparison differs from a co-located direct optical-clock ratio and from a
   derived constants constraint.
3. **Uncertainty and covariance semantics remain load-bearing.** The CSV
   lists per-window statistical, comb, clock, deadtime, drift, and link
   components. A benchmark row needs a frozen rule for whether the Figure 2b
   summary uncertainty, an aggregate over time windows, or a processing-path
   covariance state is used. Shared evidence between `VLBI`, `IPPP`, and `PPP`
   must not be treated as silently independent.
4. **Campaign-window binding is not frozen.** The per-window MJD fields are
   visible, but the row should record the exact campaign window and the
   split-role binding before any value enters `data/atomic_clocks/acr-*.yaml`.

## Manifest Impact

`data/atomic_clocks/source_manifest.yaml` now records this review as
readiness evidence for the Pizzocaro source-family entry and keeps:

- `status: source_artifact_pinned_rows_blocked`
- `value_status: source_artifact_pinned_no_values`
- `readiness_state: SOURCE_ARTIFACT_PINNED_ROWS_BLOCKED`
- `dataset_path: null`
- `covariance_artifact_path: null`

`TASK-0456` remains blocked. Atomic still has no reviewed second-source
`Yb/Sr` target row.

## Recommended Next Step

If Pizzocaro remains the preferred fallback, open a narrow extraction-ledger
task before any row YAML is added. That task should freeze exactly one
version-of-record row surface, record the source table or figure locator,
declare whether the row is a link-derived direct measurement, and define the
covariance state under `docs/reviews/atomic-first-benchmark-covariance-policy.md`.

If the maintainer wants a faster path to a second-source row, try another
fallback candidate rather than deriving an Atomic row from these Pizzocaro CSVs
without the ledger.

## Output Routing Summary

- Task verdict: `PIZZOCARO_ROW_ADMISSIBILITY_BLOCKED`.
- Canonical destination:
  `docs/reviews/atomic-pizzocaro-yb-sr-row-admissibility-gate.md` and the
  Pizzocaro entry in `data/atomic_clocks/source_manifest.yaml`.
- Review tier: `none`.
- Gate A status: not attempted; no benchmark `RESULT-*` artifact is created.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Dataset impact: no `data/atomic_clocks/acr-*.yaml` row is added.
- Publication blocker: row-level source mapping, direct-vs-derived class,
  covariance semantics, and campaign-window binding remain unresolved.
