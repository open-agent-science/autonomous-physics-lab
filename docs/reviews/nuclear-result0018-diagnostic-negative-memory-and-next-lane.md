# Nuclear RESULT-0018 Diagnostic Negative Memory And Next-Lane Decision

**Task:** `TASK-0743`
**Campaign:** Nuclear Mass Surface
**Mode:** planning only; no prediction scoring, no data fetch, no fitted values
**Decision:** `OPEN_ONE_NON_F2_LANE_SELECTION_NO_SCORING`

## Scope

This note converts the independently reproduced but scientifically inconclusive
`RESULT-0018` F2 component-ablation diagnostic into explicit Nuclear campaign
memory. It decides the next campaign posture after Gate B replay: do not rerun
F2, do not promote the diagnostic into a claim, and open exactly one follow-up
planning lane to select a materially non-F2 no-leakage hypothesis family.

This task does not score `PRED-*` entries, fetch nuclear data, inspect live or
post-freeze measurement values, refit a mass model, create a `RESULT-*`
artifact, update claims or knowledge, or change frozen prediction values.

## Inputs Reviewed

- [`RESULT-0018`](../../results/EXP-0012/RUN-0002/result.yaml)
- [RESULT-0018 Gate B replay](result-0018-gate-b-replay.md)
- [Nuclear F2 diagnostic result publication preflight](nuclear-f2-diagnostic-result-publication-preflight.md)
- [Nuclear F2 promotion or stop decision](nuclear-f2-promotion-or-stop-decision.md)
- [Nuclear F2 survival-margin component ablation](nuclear-f2-survival-margin-component-ablation.md)
- [Nuclear do-not-repeat diagnostic lanes](nuclear-do-not-repeat-diagnostic-lanes.md)
- [Nuclear campaign page](../campaigns/nuclear-mass-surface.md)
- `TASK-0714` and `TASK-0746`

## What RESULT-0018 Validated Reproducibly

`RESULT-0018` is now valid reproducible diagnostic memory:

| Check | Status |
| --- | --- |
| Pinned inputs and command | reproduced |
| Independent Gate B replay | pass |
| Review tier | `AGENT_VALIDATED` |
| Best verdict | `INCONCLUSIVE` |
| Drift observed | none |
| Claim impact | none |

The Gate B replay confirms that the committed F2 component-ablation result can
be reproduced by an independent agent from the pinned command and input hashes.
The replayed metrics match the committed content, the best verdict remains
`INCONCLUSIVE`, and the result is valid as deterministic campaign memory.

The diagnostic metric state is also clear:

| Metric | Value |
| --- | ---: |
| Full F2 full-known MAE improvement | 0.200411 MeV |
| Best control full-known MAE improvement | 0.001151 MeV |
| Full F2 minus best control | 0.199260 MeV |
| Predeclared survival margin | 0.250000 MeV |
| Survival-margin shortfall | 0.050740 MeV |
| Best single component | `only_magic_n_near` |
| Best single-component full-known improvement | 0.074761 MeV |
| Component variants clearing margin | 0 |

## What RESULT-0018 Did Not Validate Scientifically

Gate B reproducibility does not change the scientific verdict. `RESULT-0018`
does not validate a nuclear mass formula, does not validate F2 as a promotable
feature family, does not support a prediction reveal, and does not support a
claim or knowledge update.

The key scientific blocker is unchanged: the full F2 reference is replayable and
improves the frozen retrospective surfaces, but no ablation variant clears the
predeclared controls-first survival margin. The best single component is useful
for diagnosis only; it is not a surviving hypothesis lane. `CLAIM-0010` remains
`DRAFT`, and any Gate C or claim-status decision remains maintainer-only.

## Negative Memory And Do-Not-Repeat Boundary

The following F2 lanes are now exhausted under the current NMD-0003 contract and
must not be repeated without new evidence or a changed maintainer-approved
contract:

| Lane | Evidence | Boundary |
| --- | --- | --- |
| F2 controls-first scoring | `TASK-0553`, `TASK-0612` | Do not rerun the same F2 scoring as a fresh discovery lane. |
| F2 promotion/stop review | `TASK-0613` | The single allowed follow-up was component ablation, not open-ended F2 search. |
| F2 component ablation | `TASK-0625`, `RESULT-0018` | Do not repeat the same component slate; no variant clears the survival margin. |
| F2 diagnostic result publication | `TASK-0633`, `TASK-0713` | Gate B reproducibility preserves diagnostic memory; it does not create claim support. |
| Same F2 label taxonomy under same split/baseline | do-not-repeat map | Blocked unless a new source, baseline, or taxonomy contract changes the scientific question before scoring. |

This boundary is narrow. It blocks another F2 loop on the same dataset,
split, baseline, labels, controls, and survival rule. It does not block
source-gated reveal scouting, prediction-readiness hygiene, or one materially
non-F2 no-leakage planning lane.

## Next-Lane Decision

Recommended posture: **open one non-F2 no-leakage lane-selection task**, not an
execution sprint.

`TASK-0746` is the right next task to unblock. It should select exactly one
bounded hypothesis family that is materially disjoint from F2 and define the
future sprint contract. It must not run the sprint, fit a model, fetch reveal
data, or promote claims.

Rationale:

- **Do not wait only for reveal data.** Reveal scoring remains blocked until a
  post-freeze source passes the no-peek source gate, but that does not prevent
  source-safe planning over committed NMD-0003 artifacts.
- **Do not preserve a broad no-go.** F2 is exhausted, but the NMD-0003 measured
  training surface, frozen split manifest, and controls-first gauntlet still
  allow one carefully bounded non-F2 planning lane.
- **Do not reopen F2.** RESULT-0018 has already filled the diagnostic result
  slot and gives a clear do-not-repeat boundary for the current F2 contract.

## Requirements For TASK-0746

The next lane-selection task should use these prerequisites and controls:

| Area | Requirement |
| --- | --- |
| Source/data | Use only committed `NMD-0003` measured training rows, the committed split manifest, the frozen stratified baseline gate, and committed Nuclear review notes. |
| No reveal leakage | Do not fetch, inspect, or score post-AME2020 reveal data; do not touch frozen `PRED-*` values. |
| Family disjointness | Reject any family that reuses F2 labels, F2 component-ablation wording, shell-axis re-audit wording, or a completed do-not-repeat feature family as its core evidence. |
| No-leakage contract | Predeclare allowed inputs and forbid residual-derived, target-derived, future-source-status, and holdout-inspected features. |
| Controls | Require at least two negative controls before execution: one matched-complexity or same-degree random control, and one simple physics/baseline-adjacent control appropriate to the selected family. Use shuffle controls when a taxonomy/label family is selected. |
| Split discipline | Keep train/validation/holdout membership frozen before any scoring; do not select the family after looking at validation residual wins. |
| Stop conditions | Stop if the selected family is not materially disjoint, if any input leaks target or reveal information, if controls match the candidate, or if the predeclared survival margin is not cleared. |
| Output routing | Planning review only for `TASK-0746`; any later sprint must be a separate task and must still avoid `RESULT-*`, `PRED-*`, `CLAIM-*`, or knowledge promotion unless a later review explicitly authorizes it. |

## Campaign Page Update

The campaign page should no longer describe F2 result-publication preflight as
the next active Nuclear result. That step has happened: `TASK-0633` packaged
`RESULT-0018`, and `TASK-0713` independently replayed it. The campaign posture
should now say F2 is validated diagnostic/negative memory and that the next
source-safe work is `TASK-0746` lane selection plus separate reveal-source
readiness hygiene.

## Output Routing Summary

- **Task verdict:** `REVIEW_READY`.
- **Canonical destination:** this review note,
  `docs/reviews/nuclear-result0018-diagnostic-negative-memory-and-next-lane.md`.
- **Task-status recommendation:** `TASK-0746` may move from `BLOCKED` to
  `READY` because the TASK-0743 blocker is resolved by this decision.
- **Review tier:** planning/negative-memory review; no `RESULT-*` artifact.
- **Gate A status:** not attempted.
- **Gate B status:** not applicable for this task; `RESULT-0018` itself already
  has Gate B pass via `TASK-0713`.
- **Claim impact:** none; `CLAIM-0010` remains `DRAFT`.
- **Knowledge impact:** none.
- **Publication blocker:** no claim or broad Nuclear formula may be promoted
  from F2; future non-F2 work must be separately selected, controlled, and
  reviewed before execution.
