# Materials Research Factory Adapter Fit Review

Task: `TASK-0616`

Verdict: `MATERIALS_SECOND_ADAPTER_RECOMMENDED_FORMATION_ENERGY_ONLY`

## Decision

Materials is the better second executable Research Factory adapter candidate
right now. Exoplanet should remain contract-only until its reopen gate changes.

The recommended smoke sprint is a narrow MD-0001 formation-energy adapter
contract. Band-gap should stay out of the first Materials factory sprint because
the current evidence is split-sensitive.

## Inputs

- `docs/research-factory-protocol.md`
- `docs/notes/research-factory-layer-plan.md`
- `docs/reviews/research-factory-core-and-nuclear-adapter.md`
- `docs/campaigns/materials-property-residuals.md`
- `docs/reviews/materials-md0001-baseline-residual-benchmark.md`
- `docs/reviews/materials-md0001-independent-baseline-replay.md`
- `docs/reviews/materials-md0001-formation-energy-null-control-audit.md`
- `docs/reviews/materials-md0001-band-gap-null-control-audit.md`
- `docs/reviews/materials-md0001-split-sensitivity-audit.md`
- `data/materials/MD-0001/`

## Candidate Comparison

| Criterion | Exoplanet | Materials |
| --- | --- | --- |
| Source state | Contract exists, but current residual lane is closed pending a materially changed snapshot | MD-0001 is source-pinned and committed |
| Baseline state | Prior benchmark surface exists, but reopen is gated | Baseline, independent replay, controls, and split-sensitivity reviews exist |
| Holdout state | Useful historically, but current factory sprint would wait for new snapshot trigger | MD-0001 already has train/validation/holdout splits |
| Controls | Contract-only until reopen | Formation-energy null controls and split sensitivity are already reviewed |
| Publication posture | Closed lane; avoid sprint churn | Diagnostic adapter smoke sprint can improve negative/replay/control memory without claims |

## Recommended Adapter Scope

Adapter: `materials_md0001_formation_energy_factory`.

Dataset: MD-0001 only.

Target axis: formation energy only.

Frozen baseline: existing MD-0001 baseline surface; do not refit the baseline in
the adapter task.

Candidate cap: 12 executed candidates.

Allowed factory families:

- `cation_group_residual_offsets`;
- `anion_oxygen_stoichiometry_residual_offsets`;
- `binary_oxide_formula_family_residual_offsets`;
- `formation_energy_baseline_error_bucket_flags`.

The families must use only source-pinned, target-independent structure or
baseline residual diagnostics already available inside MD-0001. They must not
import external descriptors, chemistry knowledge graphs, DFT metadata not
already pinned, or band-gap target information.

## Required Controls

- frozen split replay against the current baseline;
- validation-holdout no-peek scoring;
- label shuffle;
- cation-group shuffle;
- matched random feature or matched random bucket control;
- seed split sensitivity check using the existing MD-0001 split-sensitivity
  pattern;
- complexity penalty by candidate family and parameter count;
- factory summary artifact with route verdicts and limitations.

## Stop Rules

Stop the smoke sprint if any of these occur:

- validation or holdout MAE regresses against the frozen formation-energy
  baseline;
- best matched control equals or beats the best candidate within the declared
  margin;
- a candidate uses the target value, split label, future holdout information, or
  another leakage-prone feature;
- more than 12 candidates would be executed;
- the adapter needs a new dataset, external fetch, or broad framework rewrite;
- band-gap is pulled into the first smoke sprint;
- route wording implies a physical materials claim instead of diagnostic
  residual memory.

## Forbidden Outputs

- no `RESULT-*` artifact from the adapter-contract task;
- no claims, accepted knowledge, or prediction entries;
- no external data repository migration;
- no new live source acquisition;
- no band-gap factory sprint;
- no automatic dataset publication.

## Concrete Scientific Output Path

The next useful output is a bounded adapter-contract or smoke-sprint task that
emits a factory summary and routes candidates into one of:

- negative memory if controls dominate;
- replay/control review memory if a small diagnostic candidate survives;
- scoped result preflight only if a later task explicitly passes publication
  gates.

## Routing

Canonical destination: review note only.

Review tier: not applicable; no `RESULT-*` artifact was proposed.

Gate A status: not attempted.

Gate B status: not applicable.

Claim impact: none.

Knowledge impact: none.

Publication blocker: adapter not implemented or replayed; this task is a
planning-only fit review.

## Limitations

- This review does not implement the Materials adapter.
- This review does not run a factory sprint.
- Formation-energy suitability is narrower than full Materials-campaign
  suitability.
- Band-gap remains excluded from the recommended first adapter sprint.
