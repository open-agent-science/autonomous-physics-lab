# Materials MD-0002 Transfer Negative-Memory Replay

- Task: `TASK-0868`
- Source run: `AGENT-RUN-0081`
- Replay command:
  `python3 scripts/run_materials_md0002_transfer.py --config examples/benchmarks/materials_md0002_formation_energy.yaml --output-dir <untracked-replay-output> --write-report`
- Verdict: `NEGATIVE_MEMORY_REPLAY_PASS`

## Scope

This replay checks the disjoint A-site cation-family transfer failure from
`AGENT-RUN-0081`. It does not modify MD-0002 rows, holdout manifests,
`RESULT-0021`, baseline descriptors, claims, predictions, or knowledge files.

The model under test is the frozen `RESULT-0021` cation-pair mean model
(`model_cation_pair_mean`) applied unchanged to the two disjoint family-holdout
directions. The judge remains computed DFT formation energy on the committed
MD-0002 slice.

## Replay Result

The fresh replay reproduced `agent_runs/AGENT-RUN-0081/metrics.json`
byte-for-byte. The reported verdict remains `SANDBOX_FAIL` with transfer
outcome `advantage_is_family_localized`.

| Direction | Published frozen MAE | Replay frozen MAE | Published best control | Replay best control | Published margin | Replay margin | Drift |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `hold_out_alkaline_earth_transition` | `0.729781` | `0.729781` | `null_global_mean` `0.729781` | `null_global_mean` `0.729781` | `0.000000` | `0.000000` | `0.000000` |
| `hold_out_alkali_transition` | `0.791686` | `0.791686` | `per_class_median` `0.745149` | `per_class_median` `0.745149` | `-0.046537` | `-0.046537` | `0.000000` |

| Split/control field | Published | Replay | Drift |
| --- | ---: | ---: | ---: |
| `alkali_transition` rows | `225` | `225` | `0` |
| `alkaline_earth_transition` rows | `137` | `137` | `0` |
| fallback rows when holding out `alkaline_earth_transition` | `137` | `137` | `0` |
| fallback rows when holding out `alkali_transition` | `225` | `225` | `0` |
| required margin (eV/atom) | `0.050000` | `0.050000` | `0.000000` |
| `transfers_in_all_directions` | `false` | `false` | `0` |

## Interpretation

The negative result is reproduced: the frozen exact-cation-pair model has no
learned cation pair available in either disjoint held-out family, so every
held-out row falls back to the global train mean. It ties the global-mean and
shuffle controls when holding out `alkaline_earth_transition`, and it loses to
the train-family median control when holding out `alkali_transition`.

This confirms the safe wording:

> The `RESULT-0021` cation-pair advantage is family-localized on this
> computed-DFT MD-0002 slice and does not transfer across the tested disjoint
> A-site cation-family split under the predeclared controls.

## Routing Recommendation

Keep this as durable sandbox negative/control memory for now:

- canonical source remains `agent_runs/AGENT-RUN-0081/` plus the original
  transfer-benchmark review note;
- use it to constrain public wording for `RESULT-0021`, especially by avoiding
  broad transfer/generalization language;
- create a later Gate A negative `RESULT-*` task only if the maintainer wants
  this sandbox negative promoted into the canonical result ledger with
  hypothesis/experiment links.

Do not turn this replay into a material recommendation, synthesis claim,
device claim, biomedical claim, universal materials-law claim, or property
prediction artifact.

## Limitations

- Computed-DFT Materials Project formation energies only, not experimental
  measurements.
- One frozen 362-row MD-0002 slice and one disjoint A-site family axis.
- Formation energy only; band gap is not pooled into this result.
- The test is intentionally hard for the exact cation-pair descriptor because
  the two disjoint families share no cation pair.
- Negative transfer memory does not invalidate the within-split `RESULT-0021`
  benchmark; it bounds that result's public scope.

## Output Routing

- Canonical destination: `docs/reviews/materials-md0002-transfer-negative-memory-replay.md`.
- Review tier: none; replay/routing note only.
- Gate A: not attempted; no new `RESULT-*` artifact.
- Gate B-like status: `PASS` for `AGENT-RUN-0081` metric replay.
- Claim impact: none.
- Prediction impact: none.
- Knowledge impact: none.
- Result impact: no mutation.
- Publication blocker: a canonical negative `RESULT-*` would require a separate
  maintainer-approved task to link this sandbox negative into protected
  hypothesis/experiment artifacts.

## Final Verdict

`AGENT-RUN-0081` is independently replayed as a stable negative/control memory:
the cation-pair advantage is family-localized on this computed-DFT slice, with
zero replay drift and no promotion beyond sandbox memory in this task.
