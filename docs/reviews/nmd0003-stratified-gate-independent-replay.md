# NMD-0003 Stratified Gate Independent Replay

**Task:** `TASK-0583`
**Campaign:** Nuclear Mass Surface
**Verdict:** `REPLAY_MATCH_WITH_PORTABILITY_FIX`

## Scope

This task independently replays the frozen NMD-0003 stratified readiness gate
before further residual-feature scoring relies on it. It uses only committed
NMD-0003 data, split manifests, and gate artifacts. It does not generate
candidates, alter split membership, create prediction entries, score
post-AME2020 reveal rows, or promote claims.

## Inputs Reviewed

- `tasks/TASK-0552-freeze-nmd0003-stratified-baseline-gate.yaml`
- `data/nuclear_masses/nmd-0003-stratified-baseline-gate.yaml`
- `data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml`
- `data/nuclear_masses/nmd-0003-split-manifest.yaml`
- `examples/benchmarks/nuclear_mass_baseline_family_nmd0003.yaml`
- `docs/reviews/nmd0003-stratified-baseline-gate.md`
- `docs/reviews/nmd0003-baseline-family-gate.md`
- `physics_lab/engines/nmd0003_baseline_family_gate.py`

## Method

1. Re-read the frozen gate manifest and review note from TASK-0552.
2. Attempted to replay the committed baseline-family helper against the
   committed NMD-0003 family-gate config.
3. The first Windows replay attempt stopped at the helper's split-manifest
   source-dataset guard because the manifest stores
   `data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml` while
   `pathlib.Path` stringification on Windows yields backslashes.
4. Applied a narrow portability fix so the manifest and config source paths are
   compared with POSIX-normalized relative-path strings in both NMD-0003 replay
   helpers.
5. Re-ran the helper without bypassing the guard and compared replayed counts
   and metrics against
   `data/nuclear_masses/nmd-0003-stratified-baseline-gate.yaml`.

## Replay Command

Before the portability fix, the raw helper invocation on Windows:

```text
C:\Users\sviti\Documents\autonomous-physics-lab\.venv\Scripts\python.exe -c "from pathlib import Path; from physics_lab.engines.nmd0003_baseline_family_gate import run_nmd0003_baseline_family_gate; run_nmd0003_baseline_family_gate(Path('examples/benchmarks/nuclear_mass_baseline_family_nmd0003.yaml'))"
```

stopped with:

```text
ValueError: NMD-0003 split manifest source_dataset does not match config dataset.
```

After the portability fix, the metric replay uses the same helper normally.

```text
C:\Users\sviti\Documents\autonomous-physics-lab\.venv\Scripts\python.exe -c "from pathlib import Path; import json; from physics_lab.engines.nmd0003_baseline_family_gate import run_nmd0003_baseline_family_gate; m=run_nmd0003_baseline_family_gate(Path('examples/benchmarks/nuclear_mass_baseline_family_nmd0003.yaml')); ..."
```

The code change is limited to manifest/config path normalization in
`physics_lab/engines/nmd0003_baseline_freeze.py` and
`physics_lab/engines/nmd0003_baseline_family_gate.py`.

## Metric Comparison

| Field | Frozen manifest | Replay | Status |
| --- | ---: | ---: | --- |
| train rows | 1617 | 1617 | match |
| validation rows | 692 | 692 | match |
| region-stratified validation MAE | 1.899279 | 1.899279 | match |
| region-stratified validation RMSE | 2.587583 | 2.587583 | match |
| region-stratified MAE relative improvement | 0.618566 | 0.618566 | match |
| global OLS validation MAE | 2.614320 | 2.614320 | match |
| global OLS validation RMSE | 3.804107 | 3.804107 | match |
| global OLS MAE relative improvement | 0.474964 | 0.474964 | match |
| inherited validation MAE | 4.979318 | 4.979318 | match |
| inherited validation RMSE | 6.253063 | 6.253063 | match |

Replay verdict from the family-gate helper remains `INCONCLUSIVE`, matching
the sandbox diagnostic status of the underlying baseline-family evidence. The
TASK-0552 frozen gate itself remains a readiness contract, not a benchmark
result or residual-feature claim.

## Decision

The scientific gate values are reproducible: split counts and all required
stratified baseline metrics match the frozen manifest exactly at six decimals.
The Windows path-normalization blocker was fixed without changing the NMD-0003
row set, split membership, model families, coefficients, or metrics.

Future residual-feature sprints may rely on the frozen gate values, while still
treating this artifact as a readiness replay rather than residual-feature
evidence.

## Limitations

- No post-AME2020 holdout rows were scored.
- No residual-feature candidates were generated or evaluated.
- The replay did not create a `RESULT-*` artifact.
- The portability fix is intentionally narrow and only changes manifest/config
  path comparison; it does not alter scientific calculations.

## Output Routing Summary

- Task verdict: `REPLAY_MATCH_WITH_PORTABILITY_FIX`
- Canonical destination:
  `docs/reviews/nmd0003-stratified-gate-independent-replay.md`
- Review tier: `none`
- Gate A status: not attempted; no result artifact was produced.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Result impact: no `RESULT-*` artifact created or modified.
- Publication blocker: none for the scoped replay note; this remains a
  readiness-gate replay, not a `RESULT-*` artifact or claim.
