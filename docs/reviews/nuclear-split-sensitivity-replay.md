# Nuclear Split-Sensitivity Replay

**Task:** `TASK-0183`
**Agent run:** `AGENT-RUN-0006`
**Candidate:** `HYP-PROPOSAL-0021`
**Status:** `REVIEW_READY`
**Boundary:** sandbox-only review evidence

## Recommendation

`HYP-PROPOSAL-0021` should remain sandbox-only partial evidence.

It is reproducible and still interesting, but the split-sensitivity replay
shows enough variation that it should not be promoted to a canonical nuclear
mass result or claim.

## Inputs Reviewed

- `hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0021-shell-dual-heavy-anchor-odd-a.yaml`
- `agent_runs/AGENT-RUN-0005/metrics.json`
- `agent_runs/AGENT-RUN-0006/metrics.json`
- `results/EXP-0012/RUN-0001/result.yaml`
- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `docs/nuclear-mass-holdout-protocol.md`

## Replay Result

The original pilot split remains favorable on MAE:

- holdout: `He-4`, `Fe-57`, `Pb-208`;
- `delta_mae_mev`: `-0.2551303671269771`;
- `delta_rmse_mev`: `0.09828158067497306`.

The replay also evaluates three frozen alternatives:

| Split | Holdout | Delta MAE (MeV) | Reading |
| --- | --- | ---: | --- |
| `alt_split_light_medium_heavy_a` | `N-14`, `Fe-56`, `Sn-120` | 0.000000 | Tie. |
| `alt_split_light_medium_heavy_b` | `O-17`, `Ca-48`, `U-238` | -0.382875 | Improvement. |
| `alt_split_magic_stress` | `O-16`, `Ca-40`, `Pb-208` | 0.312559 | Regression. |

This satisfies the split replay requirement and shows that the candidate is not
stable across all same-shape alternatives.

## Full Same-Shape Summary

Across 48 same-shape light/medium/heavy holdout configurations:

- improved MAE on `28/48`;
- regressed MAE on `13/48`;
- tied MAE on `7/48`;
- median `delta_mae_mev`: `-0.135265169994792`;
- worst `delta_mae_mev`: `0.9480738911860487`;
- pilot split rank: `18/48` by MAE delta.

Compared with `HYP-PROPOSAL-0020`, the odd-A term improves `18/48` splits,
regresses `0/48`, and ties `30/48`.

## Leakage, Cherry-Pick, Complexity, And Overfit Notes

The deterministic replay is clean, but the research design is not blind:
`HYP-PROPOSAL-0021` was selected after the active holdout package from
`AGENT-RUN-0005` was visible.

The pilot split is not the luckiest enumerated split. That reduces the
strongest cherry-pick concern, but it does not remove selection risk because
some same-shape alternatives regress.

The complexity increase over `HYP-PROPOSAL-0020` is modest: one odd-A feature
and one parameter. The risk is not excessive formula size; the risk is that the
odd-A benefit is narrow and tied to a tiny pinned slice.

## Verdict

**Verdict:** split-sensitive partial signal.

The candidate remains useful as review-gated sandbox evidence and can inform a
second bounded nuclear batch. It is not ready for claim promotion, public
result promotion, or broad nuclear-mass language.
