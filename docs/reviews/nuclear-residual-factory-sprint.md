# Nuclear Residual-Law Factory Sprint — Review (TASK-0507)

Routing review for the first Nuclear factory sprint
([AGENT-RUN-0052](../../agent_runs/AGENT-RUN-0052/report.md)), run through the
shared Research Factory layer ([protocol](../research-factory-protocol.md),
[Nuclear sprint contract](../nuclear-residual-factory-sprint-protocol.md)).

## Result

- **Verdict: strong negative / underpowered memory. No shortlist.**
- 73 candidates generated, 72 executed across five structural families
  (`shell_distance`, `valence_z`, `valence_n`, `odd_even_pairing`, `asymmetry`);
  `local_curvature` preflight-blocked by the leakage guard.
- Routes: 66 `NEGATIVE_RESULT`, 6 `INCONCLUSIVE` (underpowered), 1
  `DATA_QUALITY_BLOCKED`, 0 `SHORTLIST_CANDIDATE`.
- The committed 11-nuclide slice gives only 3 holdout nuclides — below the
  shortlist power floor — so no candidate could be shortlisted; the top apparent
  holdout reduction (~0.12) is underpowered noise.

## Output-routing summary (per result-promotion-protocol.md)

- **Canonical destination:** none. The sprint output is sandbox evidence in
  `agent_runs/AGENT-RUN-0052/` (`factory_summary.yaml`, `metrics.json`,
  `report.md`).
- **Review tier:** not applicable (no canonical artifact published).
- **Gate A / Gate B:** not applicable (nothing promoted).
- **Claim impact:** none. No `CLAIM-*` created or changed.
- **Result impact:** none. No `RESULT-*` written; the frozen baseline
  (`results/EXP-0012/RUN-0001/result.yaml`) was read, not modified.
- **Prediction impact:** none. No `PRED-*`; no `READY_FOR_PRED_FREEZE` candidate.
- **Knowledge impact:** none.
- **Publication blocker:** the slice is too small to support any shortlist;
  a larger committed measured surface is the precondition for a future sprint.

## Controls

null-baseline, shuffled-feature, matched-random-slice, complexity penalty, and
the leakage guard were applied. post-AME2020 time-split is not applicable on
this slice and is deferred.

## Follow-up

No `READY_FOR_REPLAY` / `READY_FOR_PRED_FREEZE` candidate emerged, so no
replay or prediction-freeze proposal is created. Negative and inconclusive
families are preserved as scientific memory in the run artifacts.
