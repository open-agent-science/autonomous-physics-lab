# Atomic Pizzocaro Yb/Sr Extraction Ledger Gate

**Task:** `TASK-0742`
**Campaign:** `atomic-clock-residuals`
**Decision:** `DIAGNOSTIC_SURFACE_AUTHORIZED_ACR_ROW_CURRATION_BLOCKED`
**Review date:** 2026-06-15

## Scope

This gate maps the committed Pizzocaro source files and derived repository
artifacts to the fields needed by a possible third Yb/Sr row. It uses no live
fetch, writes no `acr-*.yaml` row, computes no consistency metric or drift fit,
and changes no result, claim, prediction, or knowledge artifact.

The decision incorporates the later per-window, covariance, and observable
contracts that were not available to the original `TASK-0567` gate.

## Inputs

| Input | Role |
| --- | --- |
| `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/Yb-Sr-ratio-measuremets.csv` | Figure 2 VLBI/IPPP windows and history summaries |
| `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/Yb-Sr-ratio-measurements-IPPP.csv` | Extended Data Figure 4 IPPP/PPP windows |
| `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/provenance.yaml` | Version, retrieval, license, and file hashes |
| `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/vlbi_per_window_diagnostic_ledger.yaml` | Frozen ten-window VLBI field mapping |
| `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/vlbi_source_derived_psd_covariance_approximation.yaml` | Approximate PSD covariance sensitivity views |
| `docs/reviews/atomic-pizzocaro-row-admissibility-after-psd-covariance.md` | Post-covariance aggregation gate |
| `docs/reviews/atomic-pizzocaro-observable-harmonization-contract.md` | Diagnostic-only residual-axis contract |

## Extraction Ledger

| Candidate surface | Possible row fields | Campaign window | Uncertainty / covariance | Row class | Decision |
| --- | --- | --- | --- | --- | --- |
| Figure 2a VLBI, ten windows | Yb/Sr orientation; `value_yb_sr_relative`; final and component uncertainties; processing path; MJD start, stop, and median | Exact MJD fields are committed for each of ten windows | Per-window final uncertainties are committed. `ACLOCK-PIZZOCARO-VLBI-COV-APPROX-0001` supplies PSD approximate-covariance sensitivity views for `rho_clock = 0` and `1`; diagonal-only reporting remains required | `LINK_DERIVED_DIRECT_COMPARISON_CANDIDATE` on a fractional-deviation axis | **Authorized only as a ten-window diagnostic surface.** It is not an absolute-ratio row and must not be aggregated |
| Figure 2b `Thiswork VLBI` summary | Fractional deviation `y`, summary uncertainty `u`, Yb/Sr history label | No row-level campaign-window fields | No component budget or frozen propagation from the ten windows to the summary | `SUMMARY_DERIVED_HISTORY_COMPARATOR` | **Blocked as an ACR row.** It lacks campaign-window and construction semantics |
| Figure 2a / Extended Data Figure 4 IPPP windows | Yb/Sr fractional-deviation values, component uncertainties, processing path, and MJD fields | Exact per-window MJD fields are committed | Shared clock, comb, link, and cross-processing-path covariance is not frozen in a repository artifact | `LINK_DERIVED_DIRECT_COMPARISON_CANDIDATE` | **Blocked.** No admissible covariance or aggregation contract |
| Extended Data Figure 4 PPP windows | Yb/Sr fractional-deviation values, component uncertainties, processing path, and MJD fields | Exact per-window MJD fields are committed | Shared evidence with IPPP and other paths is not modeled; no PPP covariance artifact exists | `LINK_DERIVED_DIRECT_COMPARISON_CANDIDATE` | **Blocked.** No admissible covariance or aggregation contract |
| Figure 2b `Thiswork IPPP` summary | Fractional deviation `y`, summary uncertainty `u`, Yb/Sr history label | No row-level campaign-window fields | No component budget or frozen propagation from source windows | `SUMMARY_DERIVED_HISTORY_COMPARATOR` | **Blocked as an ACR row.** It is a history comparator, not a row of record |

## Field-Level Decision

The committed artifacts now resolve several earlier questions:

- source identity, version, license, retrieval date, and hashes are pinned;
- ratio orientation is `Yb/Sr`;
- the ten VLBI campaign windows and component uncertainty columns are mapped;
- a deterministic PSD approximate covariance exists for sensitivity-only use;
- a residual-axis observable contract exists for diagnostic comparison.

They do not resolve the fields required for a third benchmark row:

- no candidate surface supplies an admissible absolute Yb/Sr ratio row;
- no repository-owned rule aggregates the ten correlated VLBI windows;
- the Figure 2b summaries lack campaign-window and component-construction
  semantics;
- the residual-axis contract explicitly forbids benchmark-row admission;
- IPPP/PPP cross-path covariance remains unmodeled;
- no Pizzocaro holdout or reveal role is bound for an ACR row.

## Authorization Decision

**Future ACR row curation is blocked on the current committed evidence.**

No maintainer interpretation is needed to decide the present surface: the
existing contracts explicitly prohibit converting the diagnostic windows into
an absolute benchmark row. A later row-curation task should be opened only
after one of these new inputs exists:

1. a source-backed absolute Yb/Sr row with campaign and uncertainty semantics;
2. a maintainer-approved, repository-owned aggregation contract that also
   defines the resulting row class and uncertainty propagation; or
3. a new independent Yb/Sr source whose publication surface already matches
   the ACR absolute-ratio schema.

A diagnostic-only Beloy/Pizzocaro task is separately authorized under
`TASK-0706`, provided it keeps all ten windows visible, reports diagonal and
approximate-covariance sensitivity views side by side, performs no aggregation,
and makes no benchmark-row or promotion claim.

## Implication For The Atomic Promotion Route

Pizzocaro cannot currently serve as the third independent ACR benchmark row
envisioned by a `THIRD_SOURCE_FIRST` route. It can add a source-limited
diagnostic sensitivity surface, but that does not reduce the absolute-row
benchmark from two sources to three.

## Limitations

- Repository evidence only; no live source or publication fetch.
- No source values were copied into an ACR dataset.
- The PSD covariance is approximate and sensitivity-only, not paper-published
  exact covariance.
- This gate does not judge the completed Beloy/Nemitz consistency metric.

## Output Routing

- Task verdict:
  `DIAGNOSTIC_SURFACE_AUTHORIZED_ACR_ROW_CURRATION_BLOCKED`.
- Canonical destination:
  `docs/reviews/atomic-pizzocaro-yb-sr-extraction-ledger-gate.md`.
- Review tier: `none`.
- Gate A status: not attempted; no result or prediction artifact.
- Gate B status: not applicable.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Dataset impact: no `data/atomic_clocks/acr-*.yaml` row added.
- Publication blocker: no admissible third absolute Yb/Sr row and no authorized
  aggregation contract.
