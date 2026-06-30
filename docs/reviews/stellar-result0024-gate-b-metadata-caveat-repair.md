# RESULT-0024 Stellar Gate B Metadata Caveat Repair

- Task: `TASK-0898`
- Result: `RESULT-0024`
- Scope: repair the replay packaging metadata caveat recorded by `TASK-0863`
- Verdict: `GATE_B_METADATA_CAVEAT_REPAIRED_HELPER_BLOCKED`

## Scope

This note records a narrow repair for the `RESULT-0024` Gate B replay path. It
does not refit the frozen `RESULT-0022` relation, change DEBCat rows, change
`RESULT-0024` metrics or verdicts, promote a claim, create knowledge, or create
a prediction artifact.

The repair targets the lifecycle packaging drift noted in
`docs/reviews/stellar-result0024-high-mass-transfer-gate-b-replay.md`: a
disposable replay copied the current `TASK-0849` task YAML instead of the
published `RESULT-0024` task-input snapshot.

## Packaging Repair

Before this task, the standalone replay command reproduced all scientific
metrics but emitted this task input hash:

`28e31cc180b12635e563bf51174268dd574deb344ea94e3b9f953eec2ef85f01`

The published `RESULT-0024` package preserves this task input hash:

`5676f0755625ad72d179e6a982b7f5abf4ef6c587b49bec85ccf3fbf11649353`

`scripts/run_stellar_ml_high_mass_transfer.py` now reuses the published input
snapshots under `results/EXP-0017/RUN-0001/inputs/` when those snapshots exist.
For first-time result generation, it falls back to the live source files. This
keeps disposable Gate B replay packages aligned with the published result
inputs without changing scientific calculations.

After the repair, the disposable replay emits the published task input hash:

`5676f0755625ad72d179e6a982b7f5abf4ef6c587b49bec85ccf3fbf11649353`

## Replay Drift Table

| Field | Published | Repaired replay | Drift |
| --- | ---: | ---: | ---: |
| frozen alpha | `4.526004` | `4.526004` | `0.000000` |
| primary holdout components | `24` | `24` | `0` |
| primary train components | `43` | `43` | `0` |
| frozen relation MAE (dex) | `0.334564` | `0.334564` | `0.000000` |
| best control MAE (dex) | `0.483879` | `0.483879` | `0.000000` |
| transfer margin (dex) | `0.149315` | `0.149315` | `0.000000` |
| predeclared margin (dex) | `0.040000` | `0.040000` | `0.000000` |
| secondary all-stage margin (dex) | `0.040282` | `0.040282` | `0.000000` |
| catalogue-logL primary subset MAE (dex) | `0.267489` | `0.267489` | `0.000000` |
| Stefan-Boltzmann primary subset MAE (dex) | `0.804088` | `0.804088` | `0.000000` |
| task input hash | `5676f0755625...` | `5676f0755625...` | match |

The result fields `best_verdict`, `best_model_id`, `code_reference`, and
`review_tier` also match the published artifact. The max numeric drift across
the checked headline fields is `0.0`.

## Helper Status

The canonical Gate B helper was run against the published result artifact:

`python scripts/apl_validate_agent_published_result.py results/EXP-0017/RUN-0001/result.yaml --root . --output-dir <disposable-output> --validator-contributor-id svitidaniuk-pixel --validator-github-username svitidaniuk-pixel --validator-agent-tool Codex --validator-model GPT-5 --json`

It returned `BLOCKED` with `unsupported-command` because the helper only
executes supported `physics-lab run` command shapes, while `RESULT-0024`
records the standalone publication command. The helper also preserved the
same-agent-tool warning. Because the helper did not produce a clean validation
record, this task does not mutate `results/EXP-0017/RUN-0001/result.yaml`.

## Limitations Preserved

- Same-source DEBCat transfer only; this is not an external-catalogue transfer.
- The primary high-mass holdout remains small: 24 components across 15 systems.
- Stage and luminosity-provenance sensitivities remain material diagnostics.
- Accuracy still degrades versus the in-domain `RESULT-0022` holdout.
- No universal stellar law, stellar-evolution claim, `CLAIM-*`, `KNOW-*`, or
  `PRED-*` promotion is licensed by this repair.

## Output Routing

- Canonical destination: this review note and the replay packaging fix in
  `scripts/run_stellar_ml_high_mass_transfer.py`.
- Review tier: `RESULT-0024` remains `AGENT_PUBLISHED`.
- Gate A: existing `PASS` for `RESULT-0024`.
- Gate B: numeric replay and input packaging now match, but formal helper
  validation remains blocked by `unsupported-command`.
- Result metadata impact: no mutation; metadata-only validation remains a
  maintainer decision after helper support or explicit override.
- Claim impact: none.
- Knowledge impact: none.
- Prediction impact: none.
- Public wording ceiling: bounded same-source high-mass DEBCat transfer only,
  with small-holdout, stage/provenance, and non-universal-law qualifiers.

## Final Verdict

The original task-input hash caveat was lifecycle packaging drift, and the
standalone replay package now preserves the published task-input snapshot. The
remaining blocker is not numeric drift; it is the canonical helper's current
inability to execute the standalone published command shape for a formal Gate B
validation record.
