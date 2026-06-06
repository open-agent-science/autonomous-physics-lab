# Atomic Pizzocaro Source-To-Row Extraction Ledger

Task: `TASK-0615`

Verdict: `PIZZOCARO_ROW_SURFACE_IDENTIFIED_ROW_CURATION_BLOCKED`

## Decision

The committed Pizzocaro source artifacts expose usable Yb/Sr candidate row
surfaces, but no benchmark row should be added in this task.

Recommended future row-of-record surface: Figure 2a VLBI time-series in
`Yb-Sr-ratio-measuremets.csv`.

This is the best future curation surface because it carries campaign-window
fields, the final Yb/Sr value column, component uncertainty columns, and a
specific VLBI processing path. It is still blocked for benchmark ingestion until
a future row-curation task freezes the aggregation rule and covariance state.

## Inputs

- `docs/reviews/atomic-pizzocaro-yb-sr-row-admissibility-gate.md`
- `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/provenance.yaml`
- `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/Yb-Sr-ratio-measurements-IPPP.csv`
- `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/Yb-Sr-ratio-measuremets.csv`
- `docs/reviews/atomic-first-benchmark-covariance-policy.md`
- `docs/result-promotion-protocol.md`

## Method

I inspected only the committed Pizzocaro Zenodo source artifacts. For each
visible source surface I recorded the file, section locator, row count, ratio
orientation, value and uncertainty columns, campaign-window fields, processing
path, direct-vs-derived class, and covariance blocker state.

No live fetch, ACR row creation, cross-source benchmark, constants-drift fit,
prediction, claim, or result promotion was performed.

## Candidate Surfaces

| Surface | Source file | Section locator | Row count | Ratio orientation | Value columns | Uncertainty columns | MJD/window fields | Processing path | Direct-vs-derived class | Covariance state |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| Figure 2a VLBI time-series | `Yb-Sr-ratio-measuremets.csv` | "Figure 2a: Yb/Sr ratio measurement via VLBI" | 10 | Yb/Sr | `yVLBI=Yb/Sr` plus intermediate ratio columns | `u`, `uA1`, `uB1-comb`, `uB1-clock`, `udead12`, `udrift12`, `uA2`, `uB2`, `udead23`, `udrift23`, `uA3`, `udead34`, `udrift34`, `uA4`, `uB4-comb`, `uB4-clock` | `MJDstart`, `MJDstop`, `MJDmed` | VLBI | `LINK_DERIVED_DIRECT_COMPARISON_CANDIDATE` | `COV_BLOCKED_SHARED_SYSTEMATICS` |
| Figure 2a IPPP time-series | `Yb-Sr-ratio-measuremets.csv` | "Figure 2a: Yb/Sr ratio measurement via IPPP" | 10 | Yb/Sr | `yIPPP=Yb/Sr` plus intermediate ratio columns | `u`, `uA1`, `uB1-comb`, `uB1-clock`, `udead16`, `udrift16`, `uA6`, `udead64`, `udrift64`, `uA4`, `uB4-comb`, `uB4-clock` | `MJDstart`, `MJDstop`, `MJDmed` | IPPP | `LINK_DERIVED_DIRECT_COMPARISON_CANDIDATE` | `COV_BLOCKED_SHARED_SYSTEMATICS` |
| Figure 2b history summary | `Yb-Sr-ratio-measuremets.csv` | "Figure 2b: History of Yb/Sr frequency measurements" | 6 total; 2 `Thiswork` rows | deviation relative to recommended Yb and Sr frequencies | `y` | `u` | none | history summary labels include IPPP and VLBI for `Thiswork` rows | `SUMMARY_DERIVED_HISTORY_COMPARATOR` | `COV_BLOCKED_SHARED_SYSTEMATICS` |
| Extended Data Figure 4a IPPP time-series | `Yb-Sr-ratio-measurements-IPPP.csv` | "Extended Data Figure 4a: Yb/Sr ratio measurement via IPPP" | 10 | Yb/Sr | `yIPPP=Yb/Sr` plus intermediate ratio columns | `u`, `uA1`, `uB1-comb`, `uB1-clock`, `udead16`, `udrift16`, `uA6`, `udead64`, `udrift64`, `uA4`, `uB4-comb`, `uB4-clock` | `MJDstart`, `MJDstop`, `MJDmed` | IPPP | `LINK_DERIVED_DIRECT_COMPARISON_CANDIDATE` | `COV_BLOCKED_SHARED_SYSTEMATICS` |
| Extended Data Figure 4a PPP time-series | `Yb-Sr-ratio-measurements-IPPP.csv` | "Extended Data Figure 4a: Yb/Sr ratio measurement via PPP" | 10 | Yb/Sr | `yPPP=Yb/Sr` plus intermediate ratio columns | `u`, `uA1`, `uB1-comb`, `uB1-clock`, `udead15`, `udrift15`, `uA5`, `udead54`, `udrift54`, `uA4`, `uB4-comb`, `uB4-clock` | `MJDstart`, `MJDstop`, `MJDmed` | PPP | `LINK_DERIVED_DIRECT_COMPARISON_CANDIDATE` | `COV_BLOCKED_SHARED_SYSTEMATICS` |

## Row-Of-Record Recommendation

Use at most one future row-of-record surface: Figure 2a VLBI time-series.

Future curation must define whether the row is:

- a single VLBI summary row derived from the 10 windows;
- a per-window diagnostic ledger with no cross-row aggregate metric; or
- blocked because the aggregation and covariance semantics cannot be made
  explicit from committed source artifacts.

Until that rule is frozen, the surface remains source-ready but row-blocked.
The Figure 2b history summary should remain a comparator only because it lacks
MJD/campaign-window fields and does not expose enough row construction detail
for benchmark ingestion.

## Routing

Canonical destination: review note only.

Review tier: not applicable; no `RESULT-*` artifact was proposed.

Gate A status: blocked for benchmark publication.

Gate B status: not applicable.

Claim impact: none.

Knowledge impact: none.

Publication blocker: `COV_BLOCKED_SHARED_SYSTEMATICS` plus unfinished
source-to-row aggregation semantics.

## Limitations

- This ledger does not copy source values into ACR rows.
- The direct-vs-derived labels are curation labels for future review, not
  loader-enforced schema values.
- The ledger does not resolve shared-clock or shared-campaign covariance.
- The filename `Yb-Sr-ratio-measuremets.csv` is recorded as committed.
