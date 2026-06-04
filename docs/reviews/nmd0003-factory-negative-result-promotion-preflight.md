# NMD-0003 Factory Negative-Result Promotion Preflight

**Task:** `TASK-0569`
**Source sprint:** `TASK-0517` / `AGENT-RUN-0053`
**Campaign:** Nuclear Mass Surface
**Status:** promotion preflight complete
**Decision:** keep as negative/control memory; do not promote to `RESULT-*` yet

## Reviewed Evidence

Inputs reviewed:

- `agent_runs/AGENT-RUN-0053/report.md`
- `agent_runs/AGENT-RUN-0053/metrics.json`
- `agent_runs/AGENT-RUN-0053/factory_summary.yaml`
- `docs/reviews/nuclear-residual-factory-nmd0003-sprint.md`
- `docs/reviews/nmd0003-baseline-family-gate.md`
- `tasks/TASK-0517-run-nmd-0003-nuclear-factory-sprint.yaml`
- `docs/result-promotion-protocol.md`

No new candidate generation, baseline fitting, factory run, or metric rewrite
was performed for this preflight.

## Evidence Summary

The NMD-0003 factory sprint is scientifically useful negative/control memory:

| Quantity | Value |
| --- | ---: |
| NMD-0003 measured training rows | 2309 |
| deterministic train rows | 1616 |
| deterministic holdout rows | 693 |
| generated candidates | 73 |
| preflight-rejected candidates | 1 |
| executed candidates | 72 |
| `NEGATIVE_RESULT` routes | 42 |
| `REJECTED_BY_CONTROL` routes | 30 |
| `DATA_QUALITY_BLOCKED` routes | 1 |
| `SHORTLIST_CANDIDATE` routes | 0 |
| `READY_FOR_REPLAY` routes | 0 |
| `READY_FOR_PRED_FREEZE` routes | 0 |

The strongest apparent candidate was `CAND-0037` (`valence_n`), with holdout
RMS reduced from `6.477728` MeV to `4.402568` MeV. That apparent gain was not
control-surviving: the candidate holdout reduction was `0.320353`, while the
matched random-slice control reached `0.301423`, so the route remains
`REJECTED_BY_CONTROL`.

## Promotion Decision

Do **not** package this sprint as a canonical `RESULT-*` in this PR.

The evidence is strong enough to preserve as negative/control memory, but not
strong enough for autonomous `AGENT_PUBLISHED` result promotion because:

- no candidate reached `READY_FOR_REPLAY`, `READY_FOR_PRED_FREEZE`, or
  `SHORTLIST_CANDIDATE`;
- the strongest apparent improvements were control-sensitive;
- `local_curvature` remains blocked pending a dedicated no-leakage
  implementation;
- the sprint used inherited RESULT-0015/NMD-0002 frozen baseline coefficients;
- `TASK-0535` later showed the sorted heavy-tail holdout is an extrapolation
  diagnostic and recommended a separate stratified baseline gate;
- `TASK-0552` owns the baseline/split gate that must land before another
  bounded residual-feature sprint.

This decision should prevent duplicate broad factory reruns on the same
contract while preserving the negative evidence for campaign planning.

## Allowed Follow-Up

Future Nuclear residual-feature work may proceed only after the baseline/split
contract is frozen by a dedicated readiness task such as `TASK-0552`.

Recommended next Nuclear sequence:

1. Freeze the NMD-0003 stratified baseline gate.
2. Declare the working baseline family and split contract.
3. Run only a bounded residual-feature sprint with disjoint candidate families
   and the frozen contract.

Do not rerun the TASK-0517 candidate slate unchanged on the current inherited
baseline/sorted-holdout contract.

## Output Routing Summary

- Task verdict: `DO_NOT_PROMOTE_RESULT_YET`
- Canonical destination:
  `docs/reviews/nmd0003-factory-negative-result-promotion-preflight.md`
- Review tier: `none`
- Gate A status: blocked; no replay-ready or prediction-freeze candidate,
  control-sensitive top improvements, and baseline/split gate not frozen for
  future readiness.
- Gate B status: not applicable; no prediction or reveal artifact.
- Claim impact: none.
- Knowledge impact: none.
- Result impact: no `RESULT-*` artifact created or modified.
- Limitation: this preflight is a routing decision over already committed
  sandbox evidence, not an independent replay.
