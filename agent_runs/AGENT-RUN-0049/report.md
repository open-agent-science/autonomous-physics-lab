# Exoplanet Compact-Radius Mass-Quartile Scout

**Task:** `TASK-0480`  
**Agent run:** `AGENT-RUN-0049`  
**Verdict boundary:** sandbox benchmark diagnostic only

## Summary

This scout tests whether the compact-radius residual stress is concentrated in a predeclared mass quartile inside the `R < 1.5 R_earth` true-mass/transit-radius slice. It uses the committed PSCompPars snapshot only and does not perform a live fetch or baseline refit.

## Headline Metrics

| Quantity | Value |
| --- | ---: |
| Eligible true-mass/transit-radius rows | `1207` |
| Eligible log10 RMSE | `0.1581701926744863` |
| Compact rows | `92` |
| Compact log10 RMSE | `0.26335002767665594` |

## Quartile Results

| Quartile | Mass range M_earth | Rows | log10 RMSE | Verdict | Outcome | Adverse control | Delta vs eligible | Delta vs adverse |
| --- | ---: | ---: | ---: | --- | --- | --- | ---: | ---: |
| `CMQ-001` | `0.07`-`1.48` | `23` | `0.13605384325110495` | `INCONCLUSIVE` | `under_minimum_slice` | `None` | `None` | `None` |
| `CMQ-002` | `1.54`-`2.44` | `23` | `0.08678735588519272` | `INCONCLUSIVE` | `under_minimum_slice` | `None` | `None` | `None` |
| `CMQ-003` | `2.46`-`4.28` | `23` | `0.17265605946469456` | `INCONCLUSIVE` | `under_minimum_slice` | `None` | `None` | `None` |
| `CMQ-004` | `4.3`-`99.2` | `23` | `0.47070175274197384` | `INCONCLUSIVE` | `under_minimum_slice` | `None` | `None` | `None` |

## Interpretation Boundary

This scout may identify benchmark substructure or negative/control-sensitive memory. It does not support composition, habitability, target-priority, atmospheric, or new mass-radius-law wording.

## Output Routing

- Task verdict: sandbox benchmark diagnostic only
- Canonical destination: `agent_runs/AGENT-RUN-0049/` and `docs/reviews/exoplanet-compact-radius-mass-quartile-scout.md`
- Review tier: none
- Gate A status: not attempted
- Gate B status: not attempted
- Claim impact: no claim change
- Knowledge impact: no knowledge change
- Result artifact impact: no canonical `RESULT-*` created or edited
