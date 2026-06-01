# AGENT-RUN-0052 — Nuclear Residual-Law Factory Sprint (TASK-0507)

First real sprint of the bounded Research Factory layer through the Nuclear
adapter. Sandbox evidence only: **no claim, prediction, result, or knowledge
artifact is created or promoted.**

- Factory: `nuclear-residual-factory-sprint-001`
- Adapter: `nuclear_residual_factory` v0.2 (shared runner, not a one-off script)
- Config: `examples/factories/nuclear_residual_factory_sprint.yaml`
- Dataset: `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml` (11 nuclides)
- Baseline: frozen semi-empirical coefficients from
  `results/EXP-0012/RUN-0001/result.yaml` (no refit)
- Artifacts: `factory_summary.yaml` (schema-valid), `metrics.json`

## Outcome: strong negative / underpowered memory

| route verdict | count |
| --- | --- |
| NEGATIVE_RESULT | 66 |
| INCONCLUSIVE (underpowered) | 6 |
| DATA_QUALITY_BLOCKED | 1 |
| SHORTLIST_CANDIDATE | 0 |

73 candidates generated, 72 executed across five structural feature families
(`shell_distance`, `valence_z`, `valence_n`, `odd_even_pairing`, `asymmetry`);
one leakage-sensitive family (`local_curvature`) was preflight-blocked by the
leakage guard.

**No candidate was shortlisted.** The committed slice has only 3 holdout
nuclides, which is below the shortlist power floor (`MIN_SHORTLIST_HOLDOUT_ROWS`),
so even the few candidates that survived the null / shuffled / matched-random
controls were routed `INCONCLUSIVE` rather than `SHORTLIST_CANDIDATE`. A holdout
of 3 cannot support a residual-law shortlist; the top apparent holdout reduction
(~0.12) is underpowered noise, not evidence.

## Controls applied

null-baseline, shuffled-feature, matched-random-slice, complexity penalty, and
the leakage guard. The post-AME2020 time-split check is **not applicable** on
this slice (no time-split rows) and is deferred.

## Interpretation

This is exactly the kind of negative/underpowered memory the factory exists to
preserve: a high-throughput, controlled sweep that produces no false positive on
a small slice. The factory plumbing (generation, controls, leakage guard,
routing, schema-valid summary) is exercised end-to-end.

## Limitations

- 11-nuclide slice; holdout underpowered. No shortlist is possible at this size.
- Frozen baseline coefficients are slice-specific (RESULT-0012), not a
  holdout-validated surface.
- post-AME2020 time-split check deferred (the 296-row holdout dataset uses a
  different schema and is out of scope for this bounded sprint).
- Sandbox evidence only; promotion to any canonical artifact requires a separate
  maintainer-gated task.

## Next steps

No `READY_FOR_REPLAY` or `READY_FOR_PRED_FREEZE` candidate emerged, so no
follow-up replay or prediction-freeze proposal is warranted from this run. A
larger committed measured surface (not the 11-nuclide slice) would be the
precondition for any future sprint that could produce a real shortlist.
