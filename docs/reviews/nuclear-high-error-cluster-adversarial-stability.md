# Nuclear high-error cluster adversarial stability review

**Task:** `TASK-0367`  
**Agent run:** `AGENT-RUN-0033`  
**Predecessor:** `TASK-0343` / `AGENT-RUN-0030`

## Scope

This review attacks the TASK-0343 high-error cluster sandbox signal with stronger adversarial controls: cluster-label permutation, high-error threshold perturbation, smooth-A/local-density, and near-null controls. It also records deterministic leave-one-training-row-out coefficient stability.

## Headline Result

- Lane verdict: `INCONCLUSIVE`.
- Best primary delta candidate: `HIGHCLUSTER-001` with delta MAE -0.629378 MeV.
- Primary survival margin: 0.25 MeV.

## Candidate vs Strongest Control

| Candidate | Strongest control | Margin | Subset win-rate | Flags |
| --- | --- | ---: | ---: | --- |
| `HIGHCLUSTER-001` | `HIGHCLUSTER-CONTROL-004` | +0.040234 | 0.645 | non-high-error=False, only-high-error=False |
| `HIGHCLUSTER-002` | `HIGHCLUSTER-CONTROL-004` | -0.589145 | 0.000 | non-high-error=False, only-high-error=False |
| `HIGHCLUSTER-003` | `HIGHCLUSTER-CONTROL-004` | -0.234795 | 0.161 | non-high-error=False, only-high-error=False |

## Limitations

- The audit is retrospective and uses committed full-known residual labels.
- The coefficient stability check is small-sample leave-one-training-row-out, not a blind predictive validation.
- The controls are stronger than the predecessor lane controls but are not exhaustive.
- No live data, reveal scoring, registry entry, canonical result, claim, or knowledge update is produced.

## Verdict

`INCONCLUSIVE`
