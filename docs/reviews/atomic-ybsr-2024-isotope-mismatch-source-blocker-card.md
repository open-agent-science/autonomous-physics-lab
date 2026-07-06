# Atomic Yb/Sr 2024 Isotope-Mismatch Source-Blocker Memory Card

- Task: `TASK-0942` (packages the `TASK-0913` scout outcome)
- Campaign: `atomic-clock-residuals`
- Type: source-blocker memory card (no `RESULT`/`PRED`/`CLAIM`/`KNOW`)
- Decision lineage: `TASK-0767` (consistency memory card) → `TASK-0901`
  (McGrew/NIST blocked) → `TASK-0913` (post-2021 independent source scout) →
  `TASK-0942` (this card)
- Source evidence:
  [atomic-post2021-independent-ybsr-source-scout.md](atomic-post2021-independent-ybsr-source-scout.md)

## Why This Card Exists

The `TASK-0913` scout found a source that looks, at first glance, like exactly
what the Atomic campaign is waiting for: a prestigious, post-2021,
institutionally independent, primary neutral-lattice-clock Yb/Sr ratio
publication under CC BY. Future agents are likely to rediscover it and propose
it as the missing third row. This card records, in one place, why that would
be wrong — so the campaign does not spend another scout on the same candidate.

## The Admissible Source Role (What The Campaign Actually Needs)

One new **independent absolute `171Yb/87Sr`** frequency-ratio row — the same
isotope pair and transitions as the committed Beloy 2021 / BACON
(`ACR-0001-ROW-003`) and Nemitz 2016 / RIKEN (`ACR-0002-ROW-001`) axis — from a
primary post-2021 publication with a clock/comb/network lineage distinct from
the exhausted Beloy/BACON, Nemitz/RIKEN, Pizzocaro/INRIM, and McGrew/NIST
surfaces, and with recoverable uncertainty semantics.

## The Candidate (Independent, But Mismatched)

| Field | Value |
| --- | --- |
| Publication | P. Morzynski et al., "Intercontinental frequency ratio measurement of 171Yb and 88Sr optical lattice clocks," *Metrologia* 61, 045009 (2024) |
| DOI | `10.1088/1681-7575/ad6a1e` |
| Clock pair | neutral `171Yb` (NMIJ/AIST) and neutral **`88Sr`** (UMK) |
| Independence | clears — no clock, comb, or network overlap with the four exhausted surfaces identified |
| Rights | CC BY, attribution required |

## The Exact Blocker

The strontium endpoint is **bosonic `88Sr`, not `87Sr`**. The publication
measures `171Yb/88Sr`, which is a different frequency ratio than the committed
`171Yb/87Sr` consistency axis. Therefore it cannot be:

- appended as a third `171Yb/87Sr` row;
- compared under the existing two-row Beloy/Nemitz diagnostic;
- relabeled or converted into an `87Sr` ratio via an external
  recommended-frequency value (that would create a derived row with different
  covariance semantics, not a primary row).

Institutional independence does not cure the species mismatch. The `TASK-0913`
verdict for the required role stands: `BLOCKED_NO_INDEPENDENT_SOURCE`.

## Not A Scientific Rejection

Nothing here rejects or questions the Morzynski et al. 2024 measurement. The
source is blocked **only for the current `171Yb/87Sr` row role**. If a
maintainer ever approves a separate multi-species axis (see reopen condition
2), this publication is a natural first candidate for that different role.

## Reopen Conditions

This blocker is released only by one of:

1. a primary post-2021 **`171Yb/87Sr`** publication with a distinct
   clock/network lineage and recoverable uncertainty semantics — that reopens
   the third-row route itself; or
2. a maintainer-approved, protocol-first multi-species harmonization contract
   that defines a separate `171Yb/88Sr` (or multi-axis) benchmark **without**
   modifying the committed `171Yb/87Sr` axis or this reopen condition.

## Standing Stop Conditions (Unchanged From The Scout)

- Do not relabel `171Yb/88Sr` as `171Yb/87Sr` or derive an `87Sr` ratio by
  combination with external recommended-frequency values.
- Do not combine this source's uncertainty budget with the Beloy/Nemitz
  diagnostic.
- Do not ingest values, derive ratios, fit constants drift, or create
  `RESULT`, `PRED`, `CLAIM`, or `KNOW` artifacts from this card.
- Do not reopen the Pizzocaro/INRIM or McGrew/NIST routes; their existing
  adjudications stand.
- No constants-drift, new-constant, anomaly, or precision-new-physics wording
  is authorized by this card.

## Output Routing

- **Task verdict:** `not_applicable` (source-blocker memory packaging only).
- **Canonical destination:** this card,
  `docs/reviews/atomic-ybsr-2024-isotope-mismatch-source-blocker-card.md`,
  plus a one-line campaign-page link.
- **Review tier:** none.
- **Gate A / Gate B:** not applicable.
- **Claim impact:** none. **Knowledge impact:** none.
- **Row / metric / result impact:** none; no dataset, manifest, covariance,
  or artifact change.
- **Publication blocker:** none for this card; the campaign's third-source
  role remains blocked as recorded above.
