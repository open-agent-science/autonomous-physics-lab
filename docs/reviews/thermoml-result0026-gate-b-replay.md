# RESULT-0026 ThermoML Tb Gate B Replay Review

Task: `TASK-0894`
Result: `RESULT-0026`
Canonical artifact: `results/EXP-0020/RUN-0001/result.yaml`
Replay contributor / agent: `svitidaniuk-pixel` / `codex`

## Scope

This review records an independent replay attempt for the `AGENT_PUBLISHED`
ThermoML normal-boiling-temperature (`Tb`) family-stratified Joback transfer
result. The replay preserves the frozen Joback estimator, the committed 40-row
ThermoML audit fixture, the chemical-family taxonomy, the 5 K family-survival
margin, and the no-claim source-rights boundary.

This task does not refit Joback coefficients, edit `RESULT-0026` metrics, modify
fixture rows, vendor ThermoML archive bytes, create a CLAIM/KNOW/PRED artifact,
or claim broad thermophysical-property validation.

## Replay Commands

Canonical Gate B helper attempt:

```bash
python scripts/apl_validate_agent_published_result.py results/EXP-0020/RUN-0001/result.yaml --root . --output-dir .pytest-basetemp/task0894-gateb-helper --validator-contributor-id svitidaniuk-pixel --validator-github-username svitidaniuk-pixel --validator-agent-tool Codex --validator-model GPT-5 --json
```

Helper outcome: `BLOCKED` for `unsupported-command`. The helper currently accepts
safe `physics-lab run` commands, while `RESULT-0026` records the standalone
published command:

```bash
python scripts/run_thermoml_tb_family_transfer.py --write
```

The helper also emitted a non-blocking `same-agent-tool` warning: the replay used
Codex like the original publisher, but a different contributor id
(`svitidaniuk-pixel` rather than `romanhladun24-dot`).

Manual deterministic replay used the same committed runner core
(`scripts/run_thermoml_tb_family_transfer.py::compute`) and compared the replayed
metrics against `results/EXP-0020/RUN-0001/metrics.json`. This avoids overwriting
the committed original `agent_runs/AGENT-RUN-0087/` files while testing the same
frozen fixture, code references, and metric path.

## Gate B Outcome

- Numeric replay status: `PASS`
- Protocol tier-update status: `BLOCKED_BY_HELPER_UNSUPPORTED_COMMAND`
- Combined verdict for this task: `GATE_B_NUMERIC_PASS_WITH_HELPER_BLOCKER`
- Compared aggregate/per-family/run metadata fields: `255`
- Maximum absolute numeric drift: `0.0`
- Runtime input hashes: all matched
- Transfer verdict: `TRANSFER_SUPPORTED_IN_SCOPE` unchanged
- Result review tier: unchanged at `AGENT_PUBLISHED`

Because the canonical helper cannot replay the standalone command, this PR does
not update `RESULT-0026` to `AGENT_VALIDATED` and does not add a validation
record to the result artifact. The numeric evidence supports replayability of the
committed runner path, but a protocol-clean tier upgrade still needs either a
safe `physics-lab run` packaging route or maintainer acceptance of this manual
standalone-command replay.

The replay ran at current branch commit `a966c1e7d9c4e0d0b94a55696946af53defdae97`
while the published metrics record commit
`fc863667a48a3a50f196ac3a479af699e1975932`. The material runtime input hashes
listed below matched exactly, so no code/input drift was observed for the replayed
runner, fixture, or engines.

## Aggregate Metric Drift

| Metric | Published | Replayed | Drift |
| --- | ---: | ---: | ---: |
| Joback aggregate MAE (K) | `14.925825` | `14.925825` | `0.0` |
| Best non-oracle MAE (K), `molecular_weight_only` | `43.427943` | `43.427943` | `0.0` |
| Joback margin vs best non-oracle (K) | `28.502118` | `28.502118` | `0.0` |
| Families clearing 5 K margin | `7/8` | `7/8` | `0` |

Failed family remained `esters/lactones`.

## Per-Family Metric Drift

| Held-out family | Joback MAE published | Joback MAE replayed | Best control | Margin published | Margin replayed | Clears |
| --- | ---: | ---: | --- | ---: | ---: | :---: |
| acids | `23.878` | `23.878` | `global_median` | `20.322` | `20.322` | yes |
| alcohols/phenols | `18.53` | `18.53` | `molecular_weight_only` | `39.095486` | `39.095486` | yes |
| alkanes/cycloalkanes | `11.54` | `11.54` | `molecular_weight_only` | `24.466365` | `24.466365` | yes |
| aromatic hydrocarbons | `12.3006` | `12.3006` | `molecular_weight_only` | `25.358674` | `25.358674` | yes |
| esters/lactones | `26.134` | `26.134` | `molecular_weight_only` | `-5.549755` | `-5.549755` | no |
| ethers | `7.452` | `7.452` | `molecular_weight_only` | `24.811501` | `24.811501` | yes |
| halocarbons | `14.126` | `14.126` | `global_median` | `32.88` | `32.88` | yes |
| ketones | `5.446` | `5.446` | `molecular_weight_only` | `17.991562` | `17.991562` | yes |

All compared aggregate, per-family, and model-control numeric fields matched at
absolute tolerance `1e-9`.

## Runtime Input Hash Check

| Runtime input | Published SHA-256 | Replayed SHA-256 | Status |
| --- | --- | --- | --- |
| `data/thermophysical/thermoml_tb_audit_fixture.yaml` | `c96b33b60fc07ef78b71a188cb931bff34d443549f0517ce198b0f5049ccdc7c` | `c96b33b60fc07ef78b71a188cb931bff34d443549f0517ce198b0f5049ccdc7c` | match |
| `physics_lab/engines/joback_tb.py` | `e40c60fd4b6382ab21de845896eec9809206dfa7dcde134a9a0641b55ae17212` | `e40c60fd4b6382ab21de845896eec9809206dfa7dcde134a9a0641b55ae17212` | match |
| `physics_lab/engines/thermoml_family_transfer.py` | `0d34111c97ff05070bb064fb9da525db69d18610d7643410dc6fbcb6707e4043` | `0d34111c97ff05070bb064fb9da525db69d18610d7643410dc6fbcb6707e4043` | match |
| `scripts/run_thermoml_tb_family_transfer.py` | `6e7f34f59897a4ab58da964594b91a59db75515f39aa3d781a78a307789d8091` | `6e7f34f59897a4ab58da964594b91a59db75515f39aa3d781a78a307789d8091` | match |

## Limitations

- This replay validates deterministic reproduction of the committed bounded
  40-row `Tb` transfer metrics only.
- `RESULT-0026` remains family-dependent: `esters/lactones` does not clear the
  5 K survival margin.
- The source-rights boundary is unchanged: raw ThermoML archive bytes and a
  substantial normalized corpus are not committed or vendored.
- The canonical Gate B helper did not run the RESULT command because the command
  is a standalone script rather than a safe `physics-lab run` workflow.
- Same-tool replay is recorded as a limitation; the contributor identity is
  independent, but both publication and replay used Codex.
- No chemical-design, material-recommendation, universal Joback validation, CLAIM,
  KNOW, or PRED conclusion follows from this note.

## Output Routing

- Task verdict: `VALID_IN_RANGE` evidence numerically replayed; tier update
  blocked by helper packaging.
- Canonical destination: review note only,
  `docs/reviews/thermoml-result0026-gate-b-replay.md`.
- Result impact: `RESULT-0026` unchanged; review tier remains `AGENT_PUBLISHED`.
- Gate A status: existing `PASS` from `RESULT-0026` publication package.
- Gate B status: `GATE_B_NUMERIC_PASS_WITH_HELPER_BLOCKER`.
- Claim impact: none.
- Knowledge impact: none.
- Public wording: bounded family-stratified ThermoML `Tb` transfer audit only;
  preserve the `esters/lactones` failed-family limitation and no-claim wording.

---

# TASK-0907 Amendment: Formal Gate B Replay via Workflow Bridge

Task: `TASK-0907`
Result: `RESULT-0026`
Canonical artifact: `results/EXP-0020/RUN-0001/result.yaml`
Replay contributor / agent: `gladunrv` / `claude` (Claude Code, Claude Opus 4.8)
Original publisher: `romanhladun24-dot` / Codex (Gate B independent on both the
contributor and the agent-tool axis).

## Why This Amendment Exists

The `TASK-0894` replay above numerically reproduced `RESULT-0026` with zero drift
but was `BLOCKED` at the protocol layer: the canonical Gate B helper
(`physics_lab/registry/agent_replay_validation.py`) only executes safe
`physics-lab run <config>` commands, while `RESULT-0026` recorded the standalone
runner command `python scripts/run_thermoml_tb_family_transfer.py --write`. This
amendment records the smallest safe bridge that removes that packaging blocker and
lets the canonical helper replay the result from committed inputs.

## The Bridge (Smallest Safe Change)

- Added a physics-lab workflow adapter,
  `physics_lab/workflows/thermoml_tb_family_transfer.py`, that regenerates the
  `RESULT-0026` payload from the committed 40-row fixture by calling the frozen
  deterministic engine (`physics_lab.engines.thermoml_family_transfer.run_fixture`,
  which reuses the frozen `TASK-0851` Joback estimator). It writes to the caller's
  `--output-dir` (a disposable temporary directory under Gate B), never over the
  committed canonical artifact.
- Added the runnable config `examples/thermoml_tb_family_transfer_benchmark.yaml`
  (workflow `thermoml_tb_family_transfer_benchmark`) and registered the workflow in
  the runner dispatch and the `example_config` schema enum.
- Updated only `RESULT-0026` routing metadata: `command` now reads
  `physics-lab run examples/thermoml_tb_family_transfer_benchmark.yaml` and
  `code_reference` points at the workflow module, mirroring the `RESULT-0021` /
  `RESULT-0022` Gate B workflow bridges.

No Joback coefficient was refit, the chemical-family taxonomy is unchanged, the
fixture rows are not edited, no raw ThermoML archive bytes are vendored, scope
stays `Tb`-only, and no committed `agent_runs/AGENT-RUN-*` artifact was created.
The result `input_file_hashes`, metrics, `best_verdict`, and `best_model_id` are
unchanged, so the material scientific payload is preserved.

## Formal Gate B Outcome

Canonical helper command:

```bash
python scripts/apl_validate_agent_published_result.py results/EXP-0020/RUN-0001/result.yaml --root . --output-dir <temp> --validator-contributor-id gladunrv --validator-github-username gladunrv --validator-agent-tool "Claude Code" --validator-model "Claude Opus 4.8" --json
```

- Helper status: `PASS` (no blocking issues; no independence warnings — the
  replayer differs from the publisher on both contributor and agent tool).
- Compared numeric fields: `23`; maximum absolute numeric drift: `0.0` at absolute
  tolerance `1e-9`.
- Stable string fields (`result_id`, `experiment_id`, `hypothesis_id`, `task_id`,
  `run_id`, `best_model_id`, `best_verdict`): all matched.
- Transfer verdict: `TRANSFER_SUPPORTED_IN_SCOPE` / `VALID_IN_RANGE` unchanged.
- Tier update applied: `AGENT_PUBLISHED` to `AGENT_VALIDATED` (metadata-only), with
  a `validation_record` recording the independent replay. No metric or verdict was
  edited.

## Headline Metric Drift (Formal Replay)

| Metric | Published | Replayed | Drift |
| --- | ---: | ---: | ---: |
| Joback aggregate MAE (K) | `14.925825` | `14.925825` | `0.0` |
| Best non-oracle MAE (K), `molecular_weight_only` | `43.427943` | `43.427943` | `0.0` |
| Joback margin vs best non-oracle (K) | `28.502118` | `28.502118` | `0.0` |
| Families clearing 5 K margin | `7/8` | `7/8` | `0` |
| Failed family | `esters/lactones` | `esters/lactones` | unchanged |

## TASK-0907 Limitations

- The formal Gate B pass certifies deterministic reproduction of the committed
  bounded 40-row `Tb` transfer metrics only; it is not maintainer review.
- `RESULT-0026` remains family-dependent: `esters/lactones` still does not clear the
  5 K survival margin.
- The source-rights boundary is unchanged: raw ThermoML archive bytes and a
  substantial normalized corpus are not committed or vendored.
- The standalone runner `scripts/run_thermoml_tb_family_transfer.py` and its
  sandbox `AGENT-RUN-0087` output are retained unchanged; the workflow adapter is an
  additional replay entry point, not a replacement for the sandbox history.
- No chemical-design, material-recommendation, universal Joback validation, CLAIM,
  KNOW, or PRED conclusion follows from this amendment.

## TASK-0907 Output Routing

- Task verdict: `VALID_IN_RANGE` formally replayed with zero drift.
- Canonical destination: this review note plus a metadata-only `RESULT-0026` tier
  update; no new RESULT, prediction, claim, or knowledge artifact.
- Gate A status: existing `PASS` from the `RESULT-0026` publication package.
- Gate B status: `PASS` (formal canonical-helper replay; tier upgraded to
  `AGENT_VALIDATED`).
- Claim impact: none. Knowledge impact: none.
- Public wording: bounded family-stratified ThermoML `Tb` transfer audit only;
  preserve the `esters/lactones` failed-family limitation and the no-claim wording.
