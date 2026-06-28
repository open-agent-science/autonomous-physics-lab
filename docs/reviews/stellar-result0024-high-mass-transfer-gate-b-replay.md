# RESULT-0024 Stellar High-Mass Transfer Gate B Replay

- Task: `TASK-0863`
- Result: `RESULT-0024`
- Replay command run, with a disposable untracked output directory:
  `python3 scripts/run_stellar_ml_high_mass_transfer.py --skip-sandbox-output --result-out-dir <untracked-replay-output>`
- Verdict: `GATE_B_PASS_WITH_METADATA_CAVEAT`

## Scope

This note records an independent replay of the published high-mass DEBCat
transfer result. It does not refit the frozen `RESULT-0022` relation, edit
DEBCat rows, mutate `RESULT-0022` or `RESULT-0024`, or create any `CLAIM-*`,
`PRED-*`, or `KNOW-*` artifact.

The scientific question replayed here is narrow: does the frozen
`log L = 4.526004 * log M` relation reproduce the committed `RESULT-0024`
high-mass transfer metrics against the same controls?

## Replay Outcome

The replay reproduced the core `RESULT-0024` metrics exactly at the committed
precision. The result remains `VALID_IN_RANGE` for a same-source DEBCat
transfer benchmark, not a universal stellar law or claim candidate.

| Field | Published | Replay | Drift |
| --- | ---: | ---: | ---: |
| frozen alpha | `4.526004` | `4.526004` | `0.000000` |
| rederived alpha | `4.526004` | `4.526004` | `0.000000` |
| primary holdout components | `24` | `24` | `0` |
| primary holdout systems | `15` | `15` | `0` |
| frozen relation MAE (dex) | `0.334564` | `0.334564` | `0.000000` |
| best control MAE (dex) | `0.483879` | `0.483879` | `0.000000` |
| transfer margin (dex) | `0.149315` | `0.149315` | `0.000000` |
| predeclared margin (dex) | `0.040000` | `0.040000` | `0.000000` |
| beats all shuffle seeds | `true` | `true` | `0` |
| secondary all-stage margin (dex) | `0.040282` | `0.040282` | `0.000000` |
| catalogue-logL primary subset MAE (dex) | `0.267489` | `0.267489` | `0.000000` |
| Stefan-Boltzmann primary subset MAE (dex) | `0.804088` | `0.804088` | `0.000000` |

## Metadata Comparison

| Metadata field | Published | Replay | Assessment |
| --- | --- | --- | --- |
| `best_verdict` | `VALID_IN_RANGE` | `VALID_IN_RANGE` | match |
| `code_reference` | `physics_lab/engines/stellar_ml_high_mass_transfer.py` | same | match |
| `engine_version` | `0.1.0` | `0.1.0` | match |
| config input hash | `ccf003887a0a7c56dcdd13160c8f3eff88bc6a6b60fa29a2c3b6acc3ad3cc656` | same | match |
| experiment input hash | `fffa043dec2db40980b49655994734edb09a8bb230849801033e67fa0283636a` | same | match |
| hypothesis input hash | `d58353831c1268c599846d0fed59829ae5275dbc88a6a9cc8fb5d173e92ba126` | same | match |
| DEBCat fixture hash | `7e8fe4a2359f53f7fd7c80cdba5f56dc024fa45f985879d3faecb8bc8398db08` | same | match |
| task input hash | `5676f0755625ad72d179e6a982b7f5abf4ef6c587b49bec85ccf3fbf11649353` | `28e31cc180b12635e563bf51174268dd574deb344ea94e3b9f953eec2ef85f01` | expected lifecycle drift |
| git commit | `b0a26f037a55a9eef980c74f7ae73e54e69fbc4d` | `74ccbf1eced9d710aac74f7ab7f3f47e9089773a` | replay environment drift |

The task hash drift is not a scientific-input drift: the runner copies the
current `TASK-0849` YAML when writing a disposable result package, and that task
file can change during task closeout/board synchronization after publication.
The committed result package still preserves the originally published
`results/EXP-0017/RUN-0001/inputs/task.yaml` hash. The replay matched the
fixture and all scientific metrics.

## Limitations Preserved

- Same-source DEBCat transfer: the judge is still the committed Route-2 DEBCat
  normalized rows, not an independent external catalogue.
- The primary holdout is small: 24 components across 15 systems.
- The high-mass population is stage-confounded and luminosity-provenance mixed;
  all-stage and provenance splits remain sensitivity diagnostics.
- Accuracy degrades materially versus the in-domain `RESULT-0022` holdout.
- No `CLAIM-*`, `KNOW-*`, or `PRED-*` promotion is licensed by this replay.

## Review-Tier Recommendation

Recommended path: maintainer may treat this as Gate B `PASS` for metric
reproducibility and consider a later narrow metadata update to
`review_tier: AGENT_VALIDATED` with a validation record. I did not mutate the
result artifact in this PR because the replay path is still the standalone
published script rather than a fully wired `physics-lab run` Gate B helper, and
because the current-task hash drift should be recorded rather than silently
normalized.

## Output Routing

- Canonical destination: `docs/reviews/stellar-result0024-high-mass-transfer-gate-b-replay.md`.
- Review tier: review note only; `RESULT-0024` remains unchanged in this PR.
- Gate A: previously `PASS` for `RESULT-0024`.
- Gate B: `PASS_WITH_METADATA_CAVEAT` for numeric replay; task-input hash drift
  recorded as lifecycle metadata drift, not metric drift.
- Claim impact: none.
- Prediction impact: none.
- Knowledge impact: none.
- Result impact: no mutation.
- Publication blocker: maintainer decision needed before any review-tier
  metadata mutation; public wording must keep same-source, small-holdout, and
  non-universal-law qualifiers.

## Final Verdict

`RESULT-0024` replayed successfully. The frozen `RESULT-0022` relation still
beats the best stage-matched high-mass control by `0.149315` dex against the
predeclared `0.04` dex margin, with zero numeric drift at published precision.
