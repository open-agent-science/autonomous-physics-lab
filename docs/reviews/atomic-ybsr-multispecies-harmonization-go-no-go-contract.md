# Atomic Yb/Sr Multi-Species Harmonization Go/No-Go Contract

**Task:** `TASK-0938`
**Campaign:** `atomic-clock-residuals`
**Verdict:** `KEEP_MONITOR_ONLY`
**Review date:** 2026-07-06

## Scope

This protocol-only contract answers the narrow question raised by `TASK-0913`:
can the independent `171Yb/88Sr` route (Morzynski et al. 2024) seed a separate,
explicitly labeled multi-species Yb/Sr axis, or does using it create a
derived-row/covariance/observable mismatch that keeps the Atomic campaign
monitor-only?

The task ingests and transcribes **no** ratio or frequency values, derives no
`87Sr` value from `88Sr`, combines no sources, fits no drift, runs no metrics,
creates no `RESULT`/`PRED`/`CLAIM`/`KNOW` artifact, and edits no ACR row. It
uses source-readiness language only.

## Inputs Reviewed

| Input | Contract role |
| --- | --- |
| [Post-2021 independent Yb/Sr source scout](atomic-post2021-independent-ybsr-source-scout.md) | The `171Yb/88Sr` candidate, its independence gates, and the species-mismatch blocker |
| `TASK-0942` source-blocker memory card (in review; `docs/reviews/atomic-ybsr-2024-isotope-mismatch-source-blocker-card.md` once merged) | Durable blocker memory and reopen conditions this contract must not weaken |
| [Yb/Sr source-limited consistency memory card](atomic-yb-sr-source-limited-consistency-memory-card.md) | The committed two-row `171Yb/87Sr` diagnostic boundary |
| [Pizzocaro aggregation/observable-harmonization contract](atomic-pizzocaro-aggregation-observable-harmonization-contract.md) | Contract-format precedent: definable requirements, conservative execution decision |
| [McGrew Yb/Sr source-route adjudication](atomic-mcgrew-ybsr-source-route-adjudication.md) | Standing blocked route that must not be reopened here |
| [Campaign page](../campaigns/atomic-clock-residuals.md) | Monitor-only posture and reopen gate |

## Observable Taxonomy (Admissible Families, Kept Separate)

| Family | Observable | Status under this contract |
| --- | --- | --- |
| **F1** | Direct absolute `171Yb/87Sr` frequency-ratio consistency (committed Beloy/BACON + Nemitz/RIKEN axis) | Unchanged. Reopen only via a third independent primary `171Yb/87Sr` row (`TASK-0942` card condition 1). Nothing in this contract feeds F1. |
| **F2** | Direct absolute `171Yb/88Sr` frequency-ratio memory (candidate seed: Morzynski et al. 2024) | **Definable but not seedable now.** A first-class measured observable, but exactly one independent source exists. A one-row axis supports no consistency diagnostic — it would be source memory with no comparison target and no falsification power. |
| **F3** | Derived/harmonized cross-isotope axis (`88Sr` ↔ `87Sr` via external conversion inputs) | **Definable but not executable now.** Every route manufactures derived rows whose covariance semantics differ from the direct axes; the required conversion inputs are not committed and their correlation structure is not visible in the committed evidence. |

Family labels are load-bearing: any future row, diagnostic, or memory artifact
must name its family explicitly, and no artifact may migrate between families
without a new maintainer-approved contract.

## Required Extra Inputs Before F3 Could Open (Cumulative)

1. **Conversion input of record.** Either a primary measured `88Sr/87Sr`
   (or `87Sr/88Sr`) optical-ratio publication, or the CIPM/BIPM recommended
   frequency values for both Sr transitions — with stated uncertainties,
   publication epochs, and a row-of-record citation. Value-blind here: no
   number is transcribed by this contract.
2. **Isotope/transition semantics.** Explicit transition identification for
   both endpoints (`171Yb` lattice clock transition; `87Sr` versus bosonic
   `88Sr` lattice transitions, including the induced-spectroscopy character of
   the `88Sr` endpoint) recorded on every derived row.
3. **Covariance propagation policy.** A frozen rule for how the conversion
   input's uncertainty enters each derived row, including the fact that every
   derived row sharing one conversion input is mutually correlated — the
   committed diagonal-only diagnostic treatment cannot absorb that silently.
4. **Epoch alignment.** Campaign-window metadata for the `171Yb/88Sr`
   measurement and the conversion input, with an explicit decision on whether
   epoch mismatch is treated as a limitation or a blocker.
5. **Lab/network independence accounting.** Clock, comb, fiber/GNSS transfer,
   and institutional lineage for every contributing source, so a harmonized
   row cannot smuggle a hidden dependence into the F1 axis.
6. **Uncertainty-budget visibility.** Separable endpoint-clock systematic
   budgets and transfer-chain (for the candidate: GNSS PPP mediated)
   contributions for each source feeding the axis.
7. **Schema/row-class support.** An admitted derived-row class in the atomic
   row schema with the family label, conversion provenance, and correlation
   fields — plus a maintainer decision to accept that schema extension.

## Required Extra Inputs Before F2 Could Open

F2 needs no conversion input, but it needs what a consistency axis exists for:
**a second independent primary `171Yb/88Sr` source** with distinct
clock/comb/network lineage and a recoverable uncertainty budget. Until one
exists, seeding F2 would create a single-row axis with no diagnostic content,
duplicating the `TASK-0913` scout record already preserved by the `TASK-0942`
blocker card.

## Independence And Covariance Risks (Why The Conservative Answer Holds)

- **Derived-row correlation.** One shared conversion input correlates all F3
  rows; treating them as independent would overstate consistency exactly the
  way the existing memory cards warn against.
- **Axis contamination.** A harmonized `87Sr`-equivalent value visually
  resembles an F1 row; without hard family labels it invites silent appending
  to the committed two-row diagnostic — the precise failure mode the
  `TASK-0942` card blocks.
- **Epoch and lineage mismatch.** The candidate campaign epoch differs from
  the committed F1 sources' windows, and its transfer chain is GNSS-mediated;
  both are recordable, but neither is representable in the current committed
  row semantics without the inputs above.
- **No scientific payoff today.** With one `171Yb/88Sr` source and no
  committed conversion input, neither F2 nor F3 can produce a consistency
  statement that the committed evidence supports; opening them now would be
  structure without measurement power.

## Stop Conditions (Unchanged And Extended)

- Do not relabel `171Yb/88Sr` as `171Yb/87Sr`; do not derive an `87Sr` ratio
  by combining with any external value under this contract.
- Do not append any multi-species or derived row to the committed F1
  diagnostic or its covariance treatment.
- Do not reopen the Pizzocaro/INRIM or McGrew/NIST routes through this
  contract; their adjudications stand.
- Do not ingest values, run metrics, or create `RESULT`/`PRED`/`CLAIM`/`KNOW`
  artifacts from this contract.
- No constants-drift, new-constant, anomaly, or precision-new-physics wording
  is authorized by anything in this note.

## Verdict And Go Conditions

**`KEEP_MONITOR_ONLY`.** The multi-species contract is definable — the
taxonomy and input list above are complete enough to execute against — but the
committed evidence satisfies neither family's opening condition. The Atomic
campaign therefore stays monitor-only, exactly as the `TASK-0942` blocker card
records.

The blocker is released only by:

1. **F1 route:** a primary post-2021 `171Yb/87Sr` publication with distinct
   lineage and recoverable uncertainty semantics (unchanged reopen condition);
2. **F2 route:** a second independent primary `171Yb/88Sr` source, after which
   a maintainer may authorize a separate, explicitly labeled `171Yb/88Sr`
   consistency axis seeded by the Morzynski et al. 2024 candidate;
3. **F3 route:** all seven cumulative inputs above committed and a maintainer
   decision explicitly opening a derived axis that never feeds F1.

## Output-Routing Summary

- **Task verdict:** `not_applicable` (protocol contract; contract verdict
  `KEEP_MONITOR_ONLY`).
- **Canonical destination:** this contract note,
  `docs/reviews/atomic-ybsr-multispecies-harmonization-go-no-go-contract.md`.
- **Review tier:** none.
- **Gate A / Gate B:** not applicable.
- **Claim impact:** none. **Knowledge impact:** none.
- **Row / metric / result / prediction impact:** none; no value-bearing
  artifact touched or created.
- **Publication blocker:** none for this note; the campaign's multi-species
  routes stay closed under the go conditions above.
