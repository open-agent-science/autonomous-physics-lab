# Claim-Review Cadence

## Purpose

Gate A (Result Publication) and Gate B (Independent Replay) exist, and the
first smoke tests demonstrated the route from agent-published evidence to
agent-validated artifacts. What is missing is a **recurring, conservative cycle**
for moving mature, low-risk evidence toward maintainer-reviewed scientific
memory — otherwise the corpus accumulates validated evidence and `DRAFT` claims
without ratified `CLAIM-*` status, and agents loop in sandbox/audit work with no
output-funnel endpoint.

This document defines that cadence. It does **not** change any claim status
itself, and it does not relax claim boundaries: every `CLAIM-*` status
transition stays maintainer-only (Gate C) per
[`claim-promotion-policy.md`](./claim-promotion-policy.md) and
[`result-promotion-protocol.md`](./result-promotion-protocol.md).

## Roles and authority

- **Agents** may *prepare* review material: assemble the evidence package,
  classify candidates against the criteria below, and recommend an outcome. They
  must never move a claim beyond `DRAFT` on their own.
- **The maintainer** runs the cycle decision (Gate C) and is the only actor who
  changes `CLAIM-*` status.
- The **Scientific Campaign Director** may surface candidates from the campaign
  output scorecard (`docs/campaign-output-scorecard.md`) and queue a cycle.

## Candidate selection criteria

Start with **low-risk, mature domains** — Pendulum, Anharmonic Oscillator,
Dimensional Analysis — before any frontier or numerology-adjacent domain
(Koide / particle-mass / g-2 lanes stay out of early cycles). A candidate
claim is cycle-eligible when **all** hold:

1. it is currently `DRAFT`;
2. its referenced evidence (`RESULT-*`) exists and passes (deterministic,
   reproducible, with verdict `VALID` / `VALID_IN_RANGE` / `PARTIALLY_VALID`,
   or a clean `FALSIFIED` for a falsification claim);
3. its scope wording is already range-aware and free of breakthrough/universal
   framing;
4. it is in a low-risk domain (numerology-adjacent or politically sensitive
   domains are deferred);
5. no open blocker (source provenance, holdout leakage, pending reveal) applies.

## Required evidence package (per candidate)

- the `CLAIM-*` file and its referenced `RESULT-*` (and `PRED-*` where relevant);
- the result's verdict, review tier, train/test range, and limitations;
- a one-line scope statement the maintainer would be ratifying;
- any matched/negative controls or replay (Gate B) status.

## Allowed outcomes (maintainer decision)

Each candidate ends one cycle in exactly one outcome:

| Outcome | Meaning |
| --- | --- |
| **promote** | maintainer moves `DRAFT` -> `PARTIALLY_SUPPORTED` / `SUPPORTED` (or `REFUTED` for a falsification claim) with `review_tier: MAINTAINER_REVIEWED` |
| **keep draft** | evidence is fine but scope/wording or replay needs more before ratification |
| **needs more replay** | requires an independent Gate B replay before promotion |
| **retire** | the claim is no longer worth maintaining; mark for removal |
| **supersede** | a newer claim/result replaces it (`SUPERSEDED`) |

## Stop conditions

- Stop the cycle and do not promote when evidence is missing, a holdout/no-peek
  gate is unmet, the domain is frontier/numerology-adjacent, or the wording
  would overclaim.
- One cycle handles a small batch (start with one domain); do not bulk-ratify.
- Agents stop at "recommend"; they never edit `CLAIM-*` status.

## Cadence

- Trigger a cycle when the campaign output scorecard shows a backlog of `DRAFT`
  claims with passing evidence (today: all 10 of `CLAIM-0001`..`CLAIM-0010`
  are `DRAFT`, several with passing low-risk evidence — see
  `docs/reviews/claim-review-cycle-001.md`).
- Otherwise run on maintainer demand after a science wave. This is **not** a
  schedule-only ritual; each cycle should move at least one mature claim toward
  a decision or explicitly defer it with a reason.

## First cycle

The first cycle template and candidate triage live in
[`docs/reviews/claim-review-cycle-001.md`](./reviews/claim-review-cycle-001.md).
It classifies the current `DRAFT` claims as cycle-eligible or deferred; it does
not promote any claim (that is the maintainer's Gate C step).

## Cross-references

- [`claim-promotion-policy.md`](./claim-promotion-policy.md) — authoritative
  status-transition rules (Gate C, maintainer-only).
- [`result-promotion-protocol.md`](./result-promotion-protocol.md) — Gate A/B/C.
- [`scientific-memory-review-tiers.md`](./scientific-memory-review-tiers.md) —
  review tiers.
- `docs/campaign-output-scorecard.md` (TASK-0498) — surfaces the DRAFT-claim
  backlog that triggers a cycle.
