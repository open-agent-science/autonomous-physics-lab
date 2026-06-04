# Materials MD-0001 Baseline Residual Benchmark

**Task:** `TASK-0550`
**Agent run:** `AGENT-RUN-0057`
**Campaign:** Materials Property Residuals
**Verdict:** `INCONCLUSIVE`

## Scope

This task runs the first conservative baseline/residual benchmark over the
committed `MD-0001` Materials Project stable-binary-oxides pilot. It uses no
live external fetch and does not propose material candidates, train complex ML
models, infer synthesis/design guidance, write predictions, or promote claims.

Formation energy and band gap are evaluated as separate computed-DFT property
axes. Metrics are not pooled.

## Baselines And Split

Baselines were declared before metrics:

- `global_mean`;
- `global_median`;
- `cation_group_mean`.

The benchmark binds to `data/materials/holdout_manifest.yaml` and uses a
deterministic material-id split:

- `119` train rows per axis;
- `17` validation rows per axis;
- `33` holdout rows per axis.

## Result Summary

Formation energy per atom:

- best validation baseline: `cation_group_mean`, MAE `0.664637`;
- best holdout baseline: `cation_group_mean`, MAE `0.646030`;
- global median holdout MAE: `0.967090`.

Band gap:

- best validation baseline: `global_median`, MAE `1.214165`;
- best holdout baseline: `cation_group_mean`, MAE `1.247901`;
- global median holdout MAE: `1.349133`.

The formation-energy axis shows a clear composition-aware baseline advantage.
The band-gap axis is mixed: cation grouping helps the holdout but not the
validation split. The result is therefore useful benchmark evidence, not a
claim that cation grouping is a robust universal Materials baseline.

## Output Routing Summary

- Task verdict: `INCONCLUSIVE`
- Canonical destination:
  `agent_runs/AGENT-RUN-0057/metrics.json`,
  `agent_runs/AGENT-RUN-0057/report.md`, and this review note.
- Review tier: `none`
- Gate A status: not attempted; no benchmark `RESULT-*` artifact is published.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Result impact: no `RESULT-*` artifact created or modified.
- Publication blocker: first-run benchmark evidence requires maintainer review
  and/or a dedicated result-promotion preflight before any public result
  wording.

## Recommended Follow-Up

Run the blocked follow-up `TASK-0566` once this PR is accepted: decide whether
the MD-0001 benchmark remains a review note, becomes a scoped result candidate,
needs independent replay, or should not be promoted.
