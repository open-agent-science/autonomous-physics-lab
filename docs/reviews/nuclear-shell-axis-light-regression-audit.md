# Nuclear Shell-Axis Light-Nuclei Regression Audit

**Task:** `TASK-0320`
**Agent run:** `agent_runs/AGENT-RUN-0022/`
**Script:** `scripts/run_nuclear_shell_axis_light_regression_audit.py`
**Metrics:** `agent_runs/AGENT-RUN-0022/metrics.json`
**Evidence class:** sandbox-only retrospective light-regression audit

## Scope

This review isolates the light `A<50` regression zone that appeared in the
TASK-0310 full-known retrospective audit and the TASK-0315 validity-domain
review. It uses only committed repository inputs:

- `agent_runs/AGENT-RUN-0018/metrics.json`
- `docs/reviews/nuclear-shell-axis-validity-domain-after-0310.md`
- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`
- `results/EXP-0012/RUN-0001/result.yaml`

No live data were fetched. No prediction registry entries, reveal scores,
canonical results, claims, or knowledge artifacts were created or updated.

## Method

The audit reuses the three primary shell-axis candidates from TASK-0310:

| Candidate | Feature |
| --- | --- |
| `FULLKNOWN-SHELL-001` | proton-axis Gaussian shell proximity |
| `FULLKNOWN-SHELL-002` | proton x neutron shell-proximity product |
| `FULLKNOWN-SHELL-003` | neutron-axis Gaussian shell proximity |

Rows are split into:

- light subset: all committed full-known rows with `A < 50`;
- matched non-light subset: the first `N` committed rows with `A >= 50`, sorted
  by `A`, `Z`, `N`, and `row_id`, where `N` is the light-row count.

The matched subset is deterministic and row-count matched. It is not a
statistical bootstrap.

## Results

Positive delta means the candidate increases MAE relative to the frozen
semi-empirical baseline.

| Candidate | Light delta MAE MeV | Matched non-light delta MAE MeV | Light regress rows |
| --- | ---: | ---: | ---: |
| `FULLKNOWN-SHELL-001` | +0.104064 | -0.096672 | 15 / 24 |
| `FULLKNOWN-SHELL-002` | +0.148840 | -0.026320 | 15 / 24 |
| `FULLKNOWN-SHELL-003` | +0.259976 | +0.047315 | 15 / 24 |

All three primary candidates regress the light subset. The first two improve
the matched non-light subset, while the neutron-axis candidate also regresses
the matched non-light subset. That makes the conservative domain label a
`WARNING_ZONE`, not a clean exclusion-zone proof.

## Negative Evidence Preserved

The worst light-row regressions include near-magic and magic light rows such as
`Ca-40`, `O-17`, `Ar-36`, `S-36`, `Cl-36`, and `Ti-43`. The row-level details
are preserved in `agent_runs/AGENT-RUN-0022/metrics.json` so later work cannot
hide the light-zone failures behind aggregate full-known improvements.

## Verdict

`WARNING_ZONE`

Light `A<50` should remain outside any broad shell-axis support claim and
should be treated as a visible warning zone before future shell-axis expansion
or reveal scoring. This is sandbox-only negative evidence, not a promoted
claim.

## Limitations

- Primary shell-axis coefficients are inherited from TASK-0310 and are not
  retuned here.
- The matched non-light subset is deterministic and row-count matched, not a
  full causal control.
- The audit is retrospective over committed repository data, not a future-data
  reveal.
- No prediction registry entry, canonical result, claim, or knowledge artifact
  is promoted.
