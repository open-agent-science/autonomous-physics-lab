# Nuclear Residual Factory NMD-0003 Sprint — Review (TASK-0517)

Routing review for the NMD-0003 Nuclear factory sprint
([AGENT-RUN-0053](../../agent_runs/AGENT-RUN-0053/report.md)), run through the
shared Research Factory layer.

## Result

- **Verdict: control-dominated negative factory memory. No shortlist.**
- Dataset: `NMD-0003`, 2309 committed AME2020 measured training rows.
- Split: deterministic 70/30 train/holdout inside NMD-0003
  (`1616` train rows, `693` holdout rows), with post-AME2020 primary holdout
  rows excluded by `data/nuclear_masses/nmd-0003-split-manifest.yaml`.
- Candidates: 73 generated, 72 executed, 1 preflight-blocked by the leakage
  guard.
- Routes: 42 `NEGATIVE_RESULT`, 30 `REJECTED_BY_CONTROL`, 1
  `DATA_QUALITY_BLOCKED`, 0 `SHORTLIST_CANDIDATE`.

The strongest apparent holdout improvements were control-sensitive. The top
effective candidate (`CAND-0037`, `valence_n`) had holdout reduction `0.320353`,
but the matched random-slice control reached `0.301423`, so the candidate was
rejected by control rather than shortlisted.

## Controls

The sprint applied frozen-baseline comparison, shuffled-feature control,
matched random-slice control, complexity penalty, leakage checks, and the
post-AME2020 boundary check. The post-AME2020 holdout was not absorbed into
training and was not reveal-scored.

## Output-Routing Summary

- **Canonical destination:** sandbox evidence in
  `agent_runs/AGENT-RUN-0053/`; this review page records the routing decision.
- **Review tier:** not applicable; no `RESULT-*`/`PRED-*` artifact published.
- **Gate A / Gate B:** not applicable.
- **Claim impact:** none. No `CLAIM-*` created or changed.
- **Result impact:** none. No canonical `RESULT-*` written.
- **Prediction impact:** none. No `PRED-*` and no
  `READY_FOR_PRED_FREEZE` candidate.
- **Knowledge impact:** none.
- **Publication blocker:** no candidate reached `READY_FOR_REPLAY` or
  `READY_FOR_PRED_FREEZE`; apparent improvements were either negative after
  penalty or rejected by controls.

## Limitations

- The frozen baseline coefficients are inherited from `RESULT-0015` / NMD-0002
  and are intentionally reused without refit, so broad-surface baseline weakness
  is a limitation.
- `local_curvature` remains blocked pending a dedicated no-leakage
  implementation.
- This sprint does not run post-AME2020 reveal scoring.

## Follow-Up

No replay or prediction-freeze proposal is created from this run. A future
Nuclear factory sprint should first freeze a broad-surface NMD-0003 baseline or
land a dedicated no-leakage implementation for the currently blocked
local-curvature family.
