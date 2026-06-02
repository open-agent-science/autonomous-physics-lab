# AGENT-RUN-0053 — Nuclear Factory Sprint on NMD-0003 (TASK-0517)

Large-surface Nuclear residual-law factory sprint using the shared Research
Factory runner and Nuclear adapter. Sandbox evidence only: **no claim,
prediction, result, or knowledge artifact is created or promoted.**

- Factory: `nuclear-residual-factory-nmd0003-sprint-001`
- Adapter: `nuclear_residual_factory` v0.3
- Config: `examples/factories/nuclear_residual_factory_nmd0003_sprint.yaml`
- Dataset: `data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml`
  (2309 source-gated AME2020 measured rows)
- Split manifest: `data/nuclear_masses/nmd-0003-split-manifest.yaml`
- Baseline: frozen semi-empirical coefficients from
  `results/EXP-0012/RUN-0001/result.yaml` (no refit)
- Artifacts: `factory_summary.yaml` (schema-valid), `metrics.json`

## Outcome: Control-Dominated Negative Memory

| route verdict | count |
| --- | ---: |
| `NEGATIVE_RESULT` | 42 |
| `REJECTED_BY_CONTROL` | 30 |
| `DATA_QUALITY_BLOCKED` | 1 |
| `SHORTLIST_CANDIDATE` | 0 |
| `READY_FOR_REPLAY` | 0 |
| `READY_FOR_PRED_FREEZE` | 0 |

The run generated 73 candidates and executed 72 across five structural families
(`shell_distance`, `valence_z`, `valence_n`, `odd_even_pairing`, `asymmetry`).
The leakage-sensitive `local_curvature` family was preflight-blocked, as
required by the no-leakage contract.

No candidate was shortlisted. Several candidates improved the deterministic
holdout RMS against the frozen baseline, but the strongest apparent gains were
matched by the random-slice control. The top effective candidate,
`CAND-0037` (`valence_n`), reduced holdout RMS from 6.477728 MeV to
4.402568 MeV, but the matched random-slice control produced a comparable
reduction (`0.301423` versus the candidate's `0.320353`). It therefore routes
to `REJECTED_BY_CONTROL`, not to a shortlist.

## Controls Applied

- frozen baseline comparison against the committed semi-empirical coefficients;
- deterministic 70/30 train/holdout split within the NMD-0003 training surface;
- shuffled-feature control;
- matched random-slice control;
- complexity penalty;
- leakage guard for unsupported residual-sensitive families;
- post-AME2020 boundary check through the NMD-0003 split manifest.

The post-AME2020 holdout remains excluded from training and is not reveal-scored
in this sprint.

## Interpretation

This run strengthens the TASK-0507 result: the factory is no longer failing only
because the surface has 11 rows. On the broader NMD-0003 measured-row surface,
the bounded structural families still produce no control-surviving shortlist.
The useful scientific memory is negative/control-dominated: apparent
large-surface residual improvements are not robust to the declared controls.

## Limitations

- The frozen baseline coefficients are inherited from the small NMD-0002
  benchmark and are reused without refit; broad-surface baseline weakness must
  not be interpreted as a new residual law.
- `valence_z` and `valence_n` are adapter-supported structural shell-distance
  axes from the prior factory sprint, not independently reviewed physics claims.
- Leakage-sensitive local-curvature features remain blocked until a dedicated
  no-leakage implementation lands.
- No post-AME2020 reveal scoring was performed.
- Sandbox evidence only; no canonical `RESULT-*`, `PRED-*`, `CLAIM-*`, or
  `KNOW-*` artifact is promoted.

## Output-Routing Summary

- **Verdict:** control-dominated negative factory memory; no shortlist.
- **Canonical destination:** sandbox evidence in
  `agent_runs/AGENT-RUN-0053/` plus review summary in
  `docs/reviews/nuclear-residual-factory-nmd0003-sprint.md`.
- **Review tier:** not applicable; no canonical result/prediction artifact is
  published.
- **Gate A / Gate B:** not applicable; nothing promoted.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Publication blocker:** no candidate reached `READY_FOR_REPLAY` or
  `READY_FOR_PRED_FREEZE`; strongest apparent gains were rejected by controls.

## Next Step

No replay or prediction-freeze task is warranted from this sprint. The highest
value follow-up is a baseline-readiness task that freezes a broad-surface
baseline explicitly for NMD-0003 before running more expressive residual
families.
