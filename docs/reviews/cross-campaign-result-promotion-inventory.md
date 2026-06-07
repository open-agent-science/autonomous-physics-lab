# Cross-Campaign Result-Promotion Inventory

**Task:** `TASK-0659`
**Mode:** planning only (no engine run, no live fetch, no new metrics)
**Domain:** `cross_campaign_quality`
**Date:** 2026-06-07
**Verdict:** `not_applicable` (routing inventory; produces no scientific verdict)

## Purpose And Boundary

This is a **one-time** routing inventory. It maps the current recent,
high-value campaign artifacts onto the promotion vocabulary in
[`result-promotion-protocol.md`](../result-promotion-protocol.md) so the next
agent knows which artifacts should be **published** (Gate A), **replayed**
(Gate B), **preserved as negative/control memory**, **packaged as a reusable
dataset**, **left alone (do-not-promote)**, or are **source-blocked**.

It is deliberately **not** a recurring dashboard:

- It references existing result, review, prediction, and task files instead of
  duplicating their content.
- It does **not** create or promote any `RESULT-*`, `CLAIM-*`, `KNOW-*`, or
  `PRED-*` artifact.
- Live, frequently-changing state remains in its canonical dynamic sources:
  `python3 scripts/apl_mission.py --output onboarding` for READY work,
  [`results/golden-results.yaml`](../../results/golden-results.yaml) for pinned
  results, and
  [`prediction_registry/nuclear_masses/registry_summary.yaml`](../../prediction_registry/nuclear_masses/registry_summary.yaml)
  for the nuclear prediction queue. Do not regenerate this file on a schedule;
  re-run the inventory only when the promotion frontier has materially moved.

## Classification Vocabulary

Each candidate is tagged with exactly one primary class, defined against the
protocol gates and the four-tier review model:

| Class | Meaning | Protocol anchor |
| --- | --- | --- |
| **Gate A candidate** | Sandbox/diagnostic evidence that could become an `AGENT_PUBLISHED` `RESULT-*` once the mechanical Result Publication Gate passes. | Gate A |
| **Gate B replay-needed** | An `AGENT_PUBLISHED` `RESULT-*` awaiting one independent replay to reach `AGENT_VALIDATED`. | Gate B |
| **Gate C / maintainer candidate** | An `AGENT_VALIDATED` result (or a `DRAFT` claim) whose only remaining step is maintainer interpretation. Agents must not self-advance these. | Gate C |
| **Negative memory** | Negative, null, inconclusive, or control-failed evidence to preserve as do-not-repeat memory; not a claim. | Verdict-to-class (3) |
| **Dataset publication candidate** | A source-pinned reusable dataset whose value is the data surface, not a verdict. | Class 1 inputs / dataset provenance |
| **Do-not-promote** | Evidence explicitly capped at benchmark-summary level by a prior review; no claim promotion. | `global_forbidden`, per-campaign scorecards |
| **Source-blocked** | Cannot be scored or benchmarked until a source/admissibility/covariance gate clears. | Per-domain source gates |

## Canonical Artifact Frontier (Tiered RESULT-*)

These are the only `RESULT-*` artifacts that already carry an explicit
`review_tier` (i.e. the post-protocol promotion frontier). Everything else in
[`results/`](../../results) is `LEGACY_UNTIERED` (pre-protocol, no new action).

| Result | Campaign | Verdict | Current tier | Class | Next step |
| --- | --- | --- | --- | --- | --- |
| `RESULT-0016` — [anharmonic](../../results/EXP-0011/RUN-0002/result.yaml) | Anharmonic oscillator | `VALID_IN_RANGE` | `AGENT_VALIDATED` | **Gate C / maintainer candidate** | Gate B already done ([first-agent-validated-replay.md](./first-agent-validated-replay.md)); next is maintainer review of `CLAIM-0009`. |
| `RESULT-0017` — [pendulum overfit](../../results/EXP-0001/RUN-0006/result.yaml) | Pendulum | `OVERFITTED` | `AGENT_PUBLISHED` | **Gate B replay-needed** | First published negative result ([first-agent-published-negative-result-review.md](./first-agent-published-negative-result-review.md)); a second agent can replay → `AGENT_VALIDATED`. |
| `RESULT-0018` — [nuclear baseline](../../results/EXP-0012/RUN-0002/result.yaml) | Nuclear mass surface | `INCONCLUSIVE` | `AGENT_PUBLISHED` | **Gate B replay-needed** | Replay candidate for `TASK-0635`. |
| `RESULT-0019` — [textbook exact-ref](../../results/EXP-0013/RUN-0001/result.yaml) | Textbook formula audit | `VALID_IN_RANGE` | `AGENT_PUBLISHED` | **Gate B replay-needed** | Exact-reference software fixture (EXP-0013); deterministic, low-risk replay target. |

The live executable task for this frontier is `TASK-0635`
(*Run first Gate B replay on an AGENT_PUBLISHED result*), which applies to
`RESULT-0017`, `RESULT-0018`, or `RESULT-0019`. `RESULT-0016` is past Gate B and
sits at the maintainer-only Gate C boundary.

## Per-Campaign Promotion Inventory

### Nuclear Mass Surface
- **Gate B replay-needed:** `RESULT-0018` (see frontier table).
- **Gate A candidate:** the F2 stratified diagnostic / negative-factory signal —
  adjudicate whether it can become a scoped `AGENT_PUBLISHED` `RESULT-*` via
  `TASK-0633`.
- **Negative memory:** local-curvature, pairing-asymmetry, magic-parity, mixed
  shell-axis transfer, and the `NMD-0003` validation-holdout regression — keep as
  do-not-repeat memory; mapped by
  `TASK-0642`.
- **Source-blocked:** all 60 `PRED-*` nuclear entries are `awaiting_source`
  (`ready_for_reveal_count: 0` in
  [registry_summary.yaml](../../prediction_registry/nuclear_masses/registry_summary.yaml)).
  Reveal scoring stays blocked until a post-AME2020 reveal-grade source passes
  the reveal gate. Reference: [nuclear-mass-surface campaign](../campaigns/nuclear-mass-surface.md).

### Exoplanet Mass-Radius
- **Do-not-promote:** the residual/failure-map evidence is capped at
  `BENCHMARK_SUMMARY_ONLY` with claim promotion `no`
  ([exoplanet-failure-map-result-promotion-scorecard.md](./exoplanet-failure-map-result-promotion-scorecard.md)).
- **Negative memory:** compact/sub-Neptune matched-control, host-context, and
  mass-quartile pilots resolved to `NO_GO_PRESERVE_NEGATIVE_CONTROL_MEMORY`
  ([exoplanet-control-aware-go-no-go-synthesis.md](./exoplanet-control-aware-go-no-go-synthesis.md)).
  Do not rerun on the current pinned snapshot.
- **Source-blocked (reopen-gated):** residual scoring stays closed until a
  materially changed snapshot or revised coverage gate; the metadata-only
  trigger scout is
  `TASK-0629`.
- **Prediction awaiting reveal:** `PRED-0001` is `REGISTERED` / `AGENT_PUBLISHED`
  with no scoring
  ([first-non-nuclear-agent-published-prediction.md](./first-non-nuclear-agent-published-prediction.md)).

### Materials Property Residuals
- **Dataset publication candidate:** `MD-0001` binary-oxide dataset is
  source-pinned, replayed, and citation-tagged
  ([materials-binary-oxides-dataset.md](./materials-binary-oxides-dataset.md),
  [materials-md0001-independent-baseline-replay.md](./materials-md0001-independent-baseline-replay.md)).
- **Do-not-promote (yet):** the benchmark/result route is deferred — the
  publication decision returned `MD0002_WIDENING_FIRST`
  ([materials-md0001-result-or-dataset-publication-decision.md](./materials-md0001-result-or-dataset-publication-decision.md)).
- **Negative memory:** band-gap split-fragility null control
  (`TASK-0646`,
  [materials-md0001-band-gap-null-control-audit.md](./materials-md0001-band-gap-null-control-audit.md)).
- Adjudication task: `TASK-0614`.

### Textbook Formula Audit
- **Gate B replay-needed:** `RESULT-0019` exact-reference fixture (frontier table).
- **Dataset publication candidate:** Stellar M-L DEBCat source artifact, packaged
  via `TASK-0628`;
  holdout/leakage protocol is the parallel READY task `TASK-0657`.
- **Source-blocked:** no empirical (non-exact-reference) metrics until the
  selected formula has a source/baseline/holdout plan. Reference:
  [textbook-formula-audit campaign](../campaigns/textbook-formula-audit.md).

### Atomic-Clock Residuals
- **Source-blocked (pre-benchmark):** no `RESULT-*` yet. Beloy 2021 rows are
  pinned sandbox-only; Pizzocaro Yb/Sr rows are blocked by shared systematics;
  the per-window diagnostic ledger is
  `TASK-0636`.
  Next is row-admissibility + covariance, then a baseline-readiness gate.
  Reference: [atomic-clock-residuals campaign](../campaigns/atomic-clock-residuals.md).

### Quantum Size Effects
- **Source-blocked (pre-benchmark):** no `RESULT-*` yet. Direct measurement rows
  are still inadmissible; the next steps are source-artifact packaging and the
  non-spherical digitization fixture. Reference:
  [quantum-size-effects campaign](../campaigns/quantum-size-effects.md).

## Cross-Cutting Classes

### Claims (Gate C — maintainer-only in Phase 1)
All 10 claims in [`claims/`](../../claims) are `status: DRAFT` and
`LEGACY_UNTIERED`. None may be advanced by an agent. The two strongest
Gate C candidates, in protocol-recommended order:

1. `CLAIM-0009` (anharmonic) — now backed by the `AGENT_VALIDATED` `RESULT-0016`;
   the most evidence-ready DRAFT → PARTIALLY_SUPPORTED candidate.
2. `CLAIM-0001` (pendulum) — the protocol's named "safest first target" for the
   first Gate C exercise.

### Knowledge (Class 7 — maintainer-only in Phase 1)
There are **zero** `KNOW-*` numbered artifacts. (The free-form reference
material under [`knowledge/`](../../knowledge) is legacy corpus, not the
`KNOW-XXXX` class.) No `KNOW-*` should be created until ≥2 same-domain
`MAINTAINER_REVIEWED` claims exist to distill from.

### Predictions (Class 5)
- Exoplanet `PRED-0001`: `REGISTERED`, awaiting reveal (see Exoplanet section).
- Nuclear `PRED-*` ×60: source-blocked (see Nuclear section).

## Consolidated Routing Table

| Candidate | Campaign | Class | Next owner / gate | Live task |
| --- | --- | --- | --- | --- |
| `RESULT-0017` | Pendulum | Gate B replay-needed | independent agent (Gate B) | `TASK-0635` |
| `RESULT-0018` | Nuclear | Gate B replay-needed | independent agent (Gate B) | `TASK-0635` |
| `RESULT-0019` | Textbook | Gate B replay-needed | independent agent (Gate B) | `TASK-0635` |
| `RESULT-0016` | Anharmonic | Gate C / maintainer | maintainer (Gate C) | — (`CLAIM-0009`) |
| Nuclear F2 diagnostic | Nuclear | Gate A candidate | agent preflight | `TASK-0633` |
| Nuclear do-not-repeat lanes | Nuclear | Negative memory | preserve only | `TASK-0642` |
| Nuclear `PRED-*` ×60 | Nuclear | Source-blocked | reveal-source gate | — |
| Exoplanet failure map | Exoplanet | Do-not-promote | none (capped) | — |
| Exoplanet control pilots | Exoplanet | Negative memory | preserve only | `TASK-0629` (trigger only) |
| Exoplanet `PRED-0001` | Exoplanet | Source-blocked (awaiting reveal) | reveal window | — |
| MD-0001 dataset | Materials | Dataset publication candidate | agent packaging | `TASK-0614` |
| MD-0001 band-gap null | Materials | Negative memory | preserve only | `TASK-0646` |
| Stellar M-L DEBCat | Textbook | Dataset publication candidate | agent packaging | `TASK-0628` |
| Pizzocaro rows | Atomic-clock | Source-blocked | admissibility + covariance | `TASK-0636` |
| Quantum direct rows | Quantum | Source-blocked | source artifact / digitization | — |
| `CLAIM-0009`, `CLAIM-0001` | cross-campaign | Gate C / maintainer | maintainer (Gate C) | — |

## Limitations

- **Snapshot in time.** Tiers, verdicts, and queue counts were read on
  2026-06-07; the canonical dynamic sources above supersede this file the moment
  they change.
- **Frontier scope only.** Only the tiered `RESULT-*` frontier and the
  recent/high-value campaign candidates are inventoried. The 19 `RESULT-*`
  artifacts, 70 `agent_runs/` entries, and ~249 review docs are intentionally
  *not* enumerated; `LEGACY_UNTIERED` pre-protocol results are out of scope.
- **No verdicts produced.** This inventory routes existing evidence; it does not
  re-evaluate any result and creates no new artifact.
- **Gate availability.** Gate B agent-replay tooling is Phase-1 manual; Gate C
  and all `KNOW-*` / claim-status moves remain maintainer-only.

## Output-Routing Summary

- **Task verdict:** `not_applicable` (planning-only routing inventory).
- **Canonical destination:** this review note,
  `docs/reviews/cross-campaign-result-promotion-inventory.md`.
- **Review tier:** `none` — no `AGENT_PUBLISHED`/`AGENT_VALIDATED` artifact
  created.
- **Gate A / Gate B status:** not attempted (this task publishes no result and
  runs no replay).
- **Claim impact:** no claim change. Identifies `CLAIM-0009` and `CLAIM-0001` as
  Gate C candidates for a future maintainer-authored step.
- **Knowledge impact:** no knowledge change; no `KNOW-*` created (none exist;
  maintainer-only in Phase 1).
- **Limitations / blockers:** see Limitations. No tooling blocker for this
  planning task; downstream promotion is gated as noted per candidate.
