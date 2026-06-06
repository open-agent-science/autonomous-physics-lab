# Nuclear F2 Promotion Or Stop Decision

Task: `TASK-0613`

Verdict: `ABLATION_NEEDED`

## Decision

F2 is not ready for result-promotion preflight. The signal is replayable and
not explained by the current controls, but it misses the predeclared survival
margin.

The next work is exactly one ablation family: `F2_SURVIVAL_MARGIN_COMPONENT_ABLATION`.
That ablation should keep the frozen F2 candidate family, the same splits, the
same controls-first scoring rule, and the same validation-holdout no-peek
boundary, then remove or isolate F2 subcomponents to test whether the measured
gain is carried by one stable interpretable component or by a fragile aggregate.
No broad F2 search queue is recommended.

## Inputs

- `TASK-0612`
- `docs/reviews/nuclear-f2-independent-replay-and-control-ledger.md`
- `docs/reviews/nuclear-f2-controls-first-scoring.md`
- `docs/campaigns/nuclear-mass-surface.md`
- `docs/result-promotion-protocol.md`
- `agent_runs/AGENT-RUN-0067/metrics.json`

## Method

I treated `TASK-0612` as the independent replay gate for the F2 controls-first
surface, then checked whether the replayed candidate clears the campaign's
minimum promotion posture:

1. deterministic replay must match the prior F2 metrics;
2. validation-holdout performance must not regress;
3. the candidate must beat the best null/control improvement;
4. the improvement minus best control must clear the predeclared 0.25 MeV
   survival margin before result-promotion preflight is recommended.

No new code, benchmark rows, result artifacts, claims, knowledge entries, or
prediction entries were created.

## Metrics

| Surface | Baseline MAE | Corrected MAE | Improvement |
| --- | ---: | ---: | ---: |
| train LOO | 1.822262 | 1.618879 | 0.203383 |
| validation holdout | 1.899279 | 1.705814 | 0.193465 |
| full known | 1.845344 | 1.644933 | 0.200411 |

| Control | Full-known improvement |
| --- | ---: |
| F2 candidate | 0.200411 |
| asymmetry only | 0.001151 |
| matched random | -0.009373 |
| smooth A | -0.003254 |
| cluster-label shuffle | -0.006792 |

Best-control gap: 0.199260 MeV.

Predeclared survival margin: 0.250000 MeV.

Survival-margin result: fail by 0.050740 MeV.

Validation-holdout regression: false.

## Routing

Canonical destination: review note only.

Review tier: not applicable; no `RESULT-*` artifact was proposed.

Gate A status: blocked. The replay/control evidence is useful, but the margin
gate is not cleared.

Gate B status: not applicable.

Claim impact: none.

Knowledge impact: none.

Publication blocker: `CONTROL_MARGIN_NOT_CLEARED`.

## Limitations

- This is a planning-only quality gate over already committed replay/control
  evidence.
- The decision does not test a new F2 variant.
- The proposed ablation is intentionally one family only; it must not be
  expanded into open-ended feature search without a new task.

## Stop State

F2 remains diagnostic campaign memory. Promotion is blocked until the single
component-ablation family either clears the survival-margin concern or records
a durable diagnostic-only failure.
