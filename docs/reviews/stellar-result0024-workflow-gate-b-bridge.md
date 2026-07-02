# RESULT-0024 Stellar High-Mass Transfer Formal Workflow Gate B Bridge

- Task: `TASK-0917`
- Result: `RESULT-0024`
- Gate B route: `physics-lab run examples/stellar_ml_high_mass_transfer_benchmark.yaml`
- Verdict: `GATE_B_PASS_FORMAL_WORKFLOW_REPLAY`

## Scope

This note records the formal Gate B independent replay of the published
high-mass DEBCat transfer result through a supported `physics-lab run` workflow
route. It does not refit the frozen `RESULT-0022` relation, edit the committed
DEBCat rows, change the `RESULT-0022` main-sequence slice, change any
`RESULT-0024` metric or verdict, or promote a `CLAIM-*`, `PRED-*`, or `KNOW-*`
artifact.

`TASK-0863` and `TASK-0898` already established that `RESULT-0024` replays with
zero numeric drift from committed inputs, but the canonical Gate B helper
returned `BLOCKED` with `unsupported-command`: it only executes supported
`physics-lab run` command shapes, while `RESULT-0024` recorded the standalone
publication script command. This task closes that gap by adding a formal
workflow route so the helper can run the same supported command shape.

## What Changed

- New workflow adapter `physics_lab/workflows/stellar_ml_high_mass_transfer.py`
  regenerates the `results/EXP-0017/RUN-0001/` package from the committed
  CC-BY-4.0 DEBCat rows and the published input snapshots under
  `results/EXP-0017/RUN-0001/inputs/`. It is a thin bridge: all scientific
  numbers come from the frozen deterministic engine
  (`physics_lab/engines/stellar_ml_high_mass_transfer.py`) and are packaged by
  the shared writer that the standalone script already uses, so the workflow
  route and the standalone route produce a byte-identical scientific payload.
- New example config `examples/stellar_ml_high_mass_transfer_benchmark.yaml`
  and the `stellar_ml_high_mass_transfer_benchmark` workflow enum wired into the
  runner dispatch and the example-config schema.
- The published `RESULT-0024` `command` and `code_reference` were updated to the
  supported `physics-lab run` route so the Gate B helper can replay it. `command`
  is metadata (ignored by the golden material-hash policy); no scientific field
  changed. The disposable Gate B replay writes to a Python `tempfile` output
  directory and never overwrites the committed artifact.

The standalone script route is preserved for backward compatibility; the shared
package writer keeps its original default command and code reference.

## Metric-Drift Table

Independent replay via `physics-lab run` to a disposable temp directory,
compared against the published `RESULT-0024` at committed precision.

| Field | Published | Formal workflow replay | Drift |
| --- | ---: | ---: | ---: |
| frozen alpha | `4.526004` | `4.526004` | `0.000000` |
| rederived alpha | `4.526004` | `4.526004` | `0.000000` |
| primary holdout components | `24` | `24` | `0` |
| primary holdout systems | `15` | `15` | `0` |
| primary train components | `43` | `43` | `0` |
| frozen relation MAE (dex) | `0.334564` | `0.334564` | `0.000000` |
| best control MAE (dex) | `0.483879` | `0.483879` | `0.000000` |
| transfer margin (dex) | `0.149315` | `0.149315` | `0.000000` |
| predeclared margin (dex) | `0.040000` | `0.040000` | `0.000000` |
| beats all shuffle seeds | `true` | `true` | `0` |
| secondary all-stage components | `56` | `56` | `0` |
| secondary all-stage margin (dex) | `0.040282` | `0.040282` | `0.000000` |
| catalogue-logL primary subset MAE (dex) | `0.267489` | `0.267489` | `0.000000` |
| Stefan-Boltzmann primary subset MAE (dex) | `0.804088` | `0.804088` | `0.000000` |

The Gate B helper compared 25 numeric fields with a `1.0e-09` tolerance; the
maximum absolute delta across every compared field was `0.0`. The verdict
`VALID_IN_RANGE` and `best_model_id` were unchanged.

## Metadata Comparison

| Metadata field | Published (before) | Published (after) | Assessment |
| --- | --- | --- | --- |
| `command` | `python3 scripts/run_stellar_ml_high_mass_transfer.py --skip-sandbox-output --result-out-dir results/EXP-0017/RUN-0001` | `physics-lab run examples/stellar_ml_high_mass_transfer_benchmark.yaml` | supported Gate B shape (metadata, hash-ignored) |
| `code_reference` | `physics_lab/engines/stellar_ml_high_mass_transfer.py` | `physics_lab/workflows/stellar_ml_high_mass_transfer.py` | workflow adapter (matches replay) |
| `review_tier` | `AGENT_PUBLISHED` | `AGENT_VALIDATED` | metadata-only Gate B upgrade |
| `best_verdict` | `VALID_IN_RANGE` | `VALID_IN_RANGE` | unchanged |
| `best_model_id` | `model_result0022_frozen_alpha_transfer` | same | unchanged |
| config input hash | `ccf003887a0a7c56dcdd13160c8f3eff88bc6a6b60fa29a2c3b6acc3ad3cc656` | same | match |
| experiment input hash | `fffa043dec2db40980b49655994734edb09a8bb230849801033e67fa0283636a` | same | match |
| hypothesis input hash | `d58353831c1268c599846d0fed59829ae5275dbc88a6a9cc8fb5d173e92ba126` | same | match |
| task input hash | `5676f0755625ad72d179e6a982b7f5abf4ef6c587b49bec85ccf3fbf11649353` | same | match |
| DEBCat fixture hash | `7e8fe4a2359f53f7fd7c80cdba5f56dc024fa45f985879d3faecb8bc8398db08` | same | match |

The formal workflow replay reproduces the same input snapshot digests as the
published package, so the earlier task-input-hash lifecycle caveat does not
recur on this route.

## Independence Assessment

- Original publisher: `romanhladun24-dot` / `romanhladun24-dot`, agent tool
  `Codex`, model `GPT-5` (recorded in `agent_proposal_evaluation.published_by`).
- Gate B replayer: `gladunrv` / `gladunrv`, agent tool `Claude Code`, model
  `Claude Opus 4.8`.

The replayer differs from the publisher on both contributor id and agent tool,
so the replay is fully independent and the Gate B helper raised neither the
`self-validation-forbidden` error nor the `same-contributor` / `same-agent-tool`
advisory warnings. Independence for the `AGENT_PUBLISHED` to `AGENT_VALIDATED`
upgrade is satisfied under the promotion protocol.

## Metadata-Only Tier Update Applied

Because formal Gate B passed with zero drift and independence is satisfied, the
permitted metadata-only upgrade was applied to
`results/EXP-0017/RUN-0001/result.yaml`:

- `review_tier`: `AGENT_PUBLISHED` to `AGENT_VALIDATED`;
- a `validation_record` block was appended inside `agent_proposal_evaluation`
  recording the replayer, the supported replay command, the `1.0e-09` tolerance,
  `max_abs_delta: 0.0`, `metric_count: 25`, and `drift_observed: none`.

No scientific metric, verdict, model id, or input hash was changed. The trust
qualifier limitation text was updated to reflect the Gate B tier transition.
This is not maintainer endorsement; the trust qualifier remains
"agent-validated by independent replay; not yet maintainer-reviewed".

## Limitations Preserved

- Same-source DEBCat transfer only: the judge is still the committed Route-2
  DEBCat normalized rows, not an independent external catalogue.
- The primary high-mass holdout remains small: 24 components across 15 systems.
- The high-mass population is stage-confounded and luminosity-provenance mixed;
  all-stage, by-stage, and provenance splits remain sensitivity diagnostics.
- Accuracy degrades materially versus the in-domain `RESULT-0022` holdout.
- No universal stellar mass-luminosity law, stellar-evolution claim, discovery,
  `CLAIM-*`, `KNOW-*`, or `PRED-*` promotion is licensed by this replay.

## Output Routing

- Task verdict: `VALID_IN_RANGE` (unchanged; replay verdict only).
- Canonical destination: this review note plus the new workflow adapter, example
  config, and the metadata-only `RESULT-0024` update.
- Review tier: `RESULT-0024` upgraded `AGENT_PUBLISHED` to `AGENT_VALIDATED`.
- Gate A: existing `PASS` for `RESULT-0024`.
- Gate B: `PASS` via the formal `physics-lab run` workflow route; zero numeric
  drift across 25 compared fields; independent replayer.
- Claim impact: none.
- Knowledge impact: none.
- Prediction impact: none.
- Public wording ceiling: bounded same-source high-mass DEBCat transfer only,
  with small-holdout, stage/provenance, and non-universal-law qualifiers.

## Final Verdict

`RESULT-0024` now replays through a supported `physics-lab run` Gate B route with
zero numeric drift, and the independent-replay tier upgrade to `AGENT_VALIDATED`
is applied. The remaining path is maintainer review (Gate C), which is not
requested by this task.
