# Nuclear Shell-Axis Full-Known Audit

## Purpose

This result note summarizes `TASK-0310`, a sandbox-only retrospective audit of
the strongest nuclear shell-axis scout family on the full committed,
reviewable measured-data surface currently available in the repository.

This is not a prospective reveal, not a `PRED-0063` through `PRED-0068` score,
and not a canonical `RESULT-*` artifact. It is a compact maintainer-facing
summary of `agent_runs/AGENT-RUN-0018/`.

## Inputs

| Input | Role |
| --- | --- |
| `RESULT-0015::model_fitted_semi_empirical` | Frozen baseline comparison. |
| `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml` | 11-row training residual slice. |
| `data/nuclear_masses/post_ame2020_holdout.yaml` | 295-row committed post-AME2020 primary holdout. |
| `scripts/run_nuclear_shell_axis_full_known_audit.py` | Deterministic audit runner. |
| `agent_runs/AGENT-RUN-0018/metrics.json` | Full metrics artifact. |

## Audit Surface

| Surface | Rows | Use |
| --- | ---: | --- |
| NMD-0002 training slice | 11 | Fits shell-axis residual coefficients. |
| Post-AME2020 primary holdout | 295 | Primary retrospective holdout behavior. |
| Full-known unique surface | 306 | Combined committed measured-data audit surface. |

No live data were fetched. No prediction registry, claim, knowledge, or
canonical result file is updated by this audit.

## Compact Outcome

Negative delta means lower retrospective MAE than the frozen baseline on that
surface or subset. Positive delta means regression.

| Candidate | Full-known ΔMAE MeV | Holdout ΔMAE MeV | Training ΔMAE MeV | Worst regression | Verdict |
| --- | ---: | ---: | ---: | --- | --- |
| `FULLKNOWN-SHELL-001` proton-axis Gaussian | -0.086092 | -0.091504 | +0.059043 | light A<50 +0.104064 | `PARTIALLY_VALID` |
| `FULLKNOWN-SHELL-002` proton x neutron product | -0.070030 | -0.071641 | -0.026837 | light A<50 +0.148840 | `PARTIALLY_VALID` |
| `FULLKNOWN-SHELL-003` neutron-axis Gaussian | -0.060145 | -0.061969 | -0.011248 | light A<50 +0.259976 | `PARTIALLY_VALID` |
| `FULLKNOWN-SHELL-004` sign-inverted control | +0.127546 | +0.127005 | +0.142063 | repeat-chain neighbor +0.824735 | `INCONCLUSIVE` |
| `FULLKNOWN-SHELL-005` shuffled-feature control | -0.000039 | -0.000047 | +0.000178 | light A<50 +0.000256 | `INCONCLUSIVE` |
| `FULLKNOWN-SHELL-006` near-null baseline reference | +0.000000 | +0.000000 | +0.000000 | none +0.000000 | `INCONCLUSIVE` |

## Interpretation

The three shell-axis candidate forms keep small sub-MeV retrospective
improvements on the full-known and primary-holdout surfaces. The strongest
form, `FULLKNOWN-SHELL-001`, improves full-known MAE by `0.086092 MeV` and
primary-holdout MAE by `0.091504 MeV`, but regresses the training slice by
`0.059043 MeV` and the light subset by `0.104064 MeV`.

The null controls behave conservatively:

- the sign-inverted control regresses the full-known and holdout surfaces;
- the shuffled-feature control collapses to near-noise-floor deltas;
- the near-null baseline-reference control returns exactly zero deltas.

This supports keeping the shell-axis lane as the strongest current
sandbox-review surface, but it still does not justify reveal scoring,
registry expansion, claim promotion, or public-facing discovery-style wording.

## Limitations

- Coefficients are still fit on only 11 NMD-0002 residual rows.
- The post-AME2020 evaluation is retrospective time-split evidence, not strict
  blind prediction.
- Full-known evaluation combines committed reviewable data, not future
  measurements.
- Some subset deltas are fragile where row counts are small.
- `TASK-0315` maps the domain of validity more explicitly in
  `docs/reviews/nuclear-shell-axis-validity-domain-after-0310.md`: light
  `A<50` is a regression zone, while double-magic and registry-repeat
  chain-neighbor behavior remain sparse diagnostics.
- `PRED-0063` through `PRED-0068` remain unscored.

## Verdict

`SANDBOX_PASS` for a conservative retrospective audit.

The shell-axis signal survives this full-known committed-data stress check as
small sandbox evidence with preserved negative controls and explicit
limitations. It should not be promoted beyond that boundary without a separate
maintainer-reviewed task.
