# Exoplanet Null-Baseline Canonical Identity Scaffold

- Task: `TASK-0909`
- Campaign: `exoplanet-mass-radius`
- Decision packet: `docs/reviews/exoplanet-null-baseline-canonical-identity-decision.md`
- Gate A blocker being addressed: `docs/reviews/exoplanet-negative-control-gate-a-blocker.md`
- Verdict: `IDENTITY_SCAFFOLD_ONLY_NO_RESULT`

## What This Task Did

`TASK-0904` recommended (Option A, maintainer-gated) creating the minimal
canonical experiment and hypothesis identities needed to later package the
already-replayed Exoplanet null-baseline negative/control memory. `TASK-0888`
recorded that Gate A for that packaging is blocked only by the absence of a
canonical experiment identity and a paired hypothesis identity, not by metric
drift or weak limitations.

This task creates exactly that minimal identity pair and nothing else:

- `experiments/EXP-0021-exoplanet-null-baseline-control-sensitivity.yaml`
- `hypotheses/HYP-0021-exoplanet-null-baseline-control-sensitivity.yaml`

`EXP-0021` and `HYP-0021` were the next free canonical ids in the experiments
and hypotheses registries (highest prior ids were `EXP-0020` / `HYP-0020`; no
prior exoplanet entry existed in either registry). The identities are mutually
consistent (`EXP-0021` references `HYP-0021`; `HYP-0021` lists `EXP-0021` as its
only experiment evidence) and reference no `RESULT-*`, so `evidence.results` is
intentionally omitted.

## Evidence The Identities Bind To

The identity pair binds committed evidence only:

- `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
  (`normalized_checksum_sha256`
  `dc4d8df2d0860f87d6384a1a1bebbe8e3e51a400175593f2b48e6c64a33ae5ee`)
- `docs/reviews/exoplanet-null-baseline-family-audit.md`
- `docs/reviews/exoplanet-null-baseline-negative-memory-replay.md`
- `docs/reviews/exoplanet-negative-control-gate-a-blocker.md`

The committed negative/control memory: in the highlighted true-mass
transit-radius slices (compact `R < 1.5 Re`, sub-Neptune `1.5-4 Re`,
Jovian-radius `8-16 Re`, hot-Jupiter period `< 10 d` and `R >= 8 Re`),
deterministic nearest-radius null controls match or beat the frozen CK17-style
baseline. The apparent residual stress is therefore control-sensitive. The
minimum-mass transit-radius slices stay underpowered diagnostics and are not
pooled with true-mass rows. The four CK17 RMSE reference values encoded in the
`EXP-0021` comparison targets (`0.263350`, `0.204175`, `0.083354`, `0.069788`
dex) are transcribed from that committed evidence and its sub-`1e-12` replay;
this identity does not recompute them.

## No-Reopen Boundary

Creating these identities preserves the monitor-only posture. The identity pair
does **not** authorize any of the following, matching the boundary in the
`TASK-0904` decision packet:

- a live NASA Exoplanet Archive fetch;
- `EXO-0003` rows or value-bearing metadata scout;
- a lowered source-version or coverage trigger;
- a CK17 refit or Chen-Kipping-style rerun on unchanged snapshots;
- candidate formula search or a new residual-scoring lane;
- pooling true-mass and minimum-mass rows into a headline metric;
- composition, habitability, atmosphere, target-priority, discovery,
  prediction, or universal mass-radius wording;
- a positive mass-radius claim;
- any `RESULT-*`, `PRED-*`, `CLAIM-*`, or `KNOW-*` creation or mutation in this
  task.

The nearest-radius neighbor remains a diagnostic control that uses observed
radius; it is not a deployable predictor.

## Consequences For Gate A

With canonical `EXP-0021` and `HYP-0021` now present in the registries, a
future maintainer-approved packaging task can set `experiment_id: EXP-0021` and
`hypothesis_id: HYP-0021` on a negative/control `RESULT-*` without the
`references missing experiment_id` / `references missing hypothesis_id`
rejection from `physics_lab/registry/repository.py`. That packaging task still
independently requires a deterministic result-producing command, recorded input
hashes, explicit limitations, and `validate-repo --strict --fail-on-warnings`;
none of those are performed here. Until such a task runs, the null-baseline
memory stays review/sandbox negative/control memory and the campaign stays
monitor-only.

## Output Routing

- Task verdict: `IDENTITY_SCAFFOLD_ONLY_NO_RESULT` (treated as `not_applicable`
  for canonical result promotion).
- Canonical destination: minimal canonical experiment identity
  (`experiments/EXP-0021-*.yaml`) and paired hypothesis identity
  (`hypotheses/HYP-0021-*.yaml`), plus this `docs/reviews/` boundary note.
- Review tier: `none`.
- Gate A: unblocked for a *future* negative/control `RESULT-*` packaging task
  (canonical identities now exist); no Gate A attempted or completed here.
- Gate B: not attempted; the underlying memory already replays with sub-`1e-12`
  drift per the committed replay note.
- Claim impact: no claim change; no claim created.
- Knowledge impact: no knowledge change.
- Prediction impact: no prediction change.
- Result impact: no `RESULT-*` created or modified; no protected artifact
  touched.
- Metric impact: none; no new metric, row, or residual score produced.
- Exoplanet campaign impact: monitor-only posture preserved; true-mass /
  minimum-mass separation and nearest-radius null controls preserved.
- Remaining blocker for a canonical negative result: a separate
  maintainer-approved packaging task must supply a deterministic
  result-producing command and pass Gate A; identity absence is no longer the
  blocker.
