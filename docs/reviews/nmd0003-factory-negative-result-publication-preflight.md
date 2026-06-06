# NMD-0003 Factory Negative-Result Publication Preflight

- Task: `TASK-0639`
- Campaign: Nuclear Mass Surface
- Source lanes: `TASK-0517`/`AGENT-RUN-0053`, `TASK-0584`/`AGENT-RUN-0061`,
  `TASK-0594`/`AGENT-RUN-0062`, `TASK-0595`/`AGENT-RUN-0063`
- Verdict: `GATE_A_BLOCKED_KEEP_AS_NEGATIVE_CONTROL_MEMORY`
- Decision: do **not** create a `RESULT-*` artifact; preserve negative/control memory

## Scope

This preflight re-decides whether the NMD-0003 factory and bounded
residual-feature sprint lanes can become exactly one scoped negative/diagnostic
`AGENT_PUBLISHED` RESULT, now that the stratified baseline/split gate has been
frozen (`TASK-0552`) and independently replayed (`TASK-0583`). It reviews only
committed sprint artifacts. It does **not** rerun, tune, or add feature
families, fetch data, score the post-AME2020 holdout, or create prediction,
claim, knowledge, or result artifacts.

It updates the earlier routing of `TASK-0569`
([`nmd0003-factory-negative-result-promotion-preflight.md`](nmd0003-factory-negative-result-promotion-preflight.md))
with the post-gate bounded sprints.

## Reviewed evidence

- [`nmd0003-factory-negative-result-promotion-preflight.md`](nmd0003-factory-negative-result-promotion-preflight.md) (`TASK-0569`)
- [`nmd0003-bounded-residual-feature-sprint.md`](nmd0003-bounded-residual-feature-sprint.md) (`TASK-0584`)
- [`nmd0003-pairing-residual-feature-sprint.md`](nmd0003-pairing-residual-feature-sprint.md) (`TASK-0594`)
- [`nmd0003-isotope-chain-transfer-sprint.md`](nmd0003-isotope-chain-transfer-sprint.md) (`TASK-0595`)
- `agent_runs/AGENT-RUN-0053/factory_summary.yaml`, `AGENT-RUN-0061/`,
  `AGENT-RUN-0062/`, `AGENT-RUN-0063/` (committed sandbox metrics)
- [`result-promotion-protocol.md`](../result-promotion-protocol.md)

## Evidence summary

| Lane | Run | Verdict | Candidate vs best control (validation) | Reached shortlist/replay-ready |
| --- | --- | --- | ---: | --- |
| Factory sweep (73 gen / 72 exec) | `AGENT-RUN-0053` | `REJECTED_BY_CONTROL` (0 shortlisted) | top `CAND-0037` `+0.320` vs control `+0.301` (not surviving) | no |
| `coulomb_surface_interaction` | `AGENT-RUN-0061` | `INCONCLUSIVE_CONTROL_DOMINATED` | `-0.001146` MeV (margin not cleared) | no |
| `pairing_asymmetry_coupling` | `AGENT-RUN-0062` | `NEGATIVE_RESULT` | `-0.016156` MeV (regresses) | no |
| `neutron_excess_curvature_transfer` | `AGENT-RUN-0063` | `NEGATIVE_RESULT` | `-0.004306` MeV (regresses) | no |

Across all four lanes: zero `SHORTLIST_CANDIDATE`, zero `READY_FOR_REPLAY`, zero
`READY_FOR_PRED_FREEZE`. The strongest apparent improvement (factory `CAND-0037`)
is control-sensitive; the post-gate bounded lanes are control-dominated or
outright validation-regressing. This is durable, useful negative/control memory.

## Gate A assessment

A scoped `AGENT_PUBLISHED` negative/diagnostic RESULT is **blocked** for this
publication preflight, on the following Gate A grounds:

1. **No single result-grade deterministic artifact.** The evidence is
   distributed across four separate `AGENT-RUN-*` sandbox runs with distinct
   commands and summaries. A RESULT must map to one `experiment_id`/`run_id`
   with one deterministic `command`, one `input_file_hashes` set, and one
   `verification` block; there is no single committed artifact that faithfully
   represents the multi-lane negative sweep.
2. **No fresh deterministic-replay verification is permitted.** This task
   explicitly forbids rerunning. The one nuclear lane that was packaged as a
   diagnostic RESULT (`RESULT-0018`, `TASK-0633`, F2 component ablation) earned
   its `verification` block by re-executing its runner and hash-comparing the
   replay. Without a permitted rerun, the `deterministic_run` and
   `verification_block_populated` gates cannot be honestly satisfied here for the
   factory/bounded sweep.
3. **No promotable candidate.** No lane reached shortlist, replay-ready, or
   prediction-freeze; the top apparent gains do not survive matched controls.
   The negative outcome is real, but it is already faithfully recorded as
   negative/control memory in the `AGENT-RUN-*` artifacts and the four review
   notes.
4. **The diagnostic RESULT slot is already filled.** `RESULT-0018` already
   publishes the F2 component-ablation diagnostic as `AGENT_PUBLISHED`/
   `INCONCLUSIVE`. A second broad negative RESULT over the same surface would be
   redundant and lower-fidelity than the existing per-lane memory.

These reinforce, rather than overturn, the `TASK-0569` decision; freezing the
baseline gate (`TASK-0552`) removed one earlier blocker but did not create a
result-grade artifact.

## Allowed follow-up

- Keep the factory and bounded-sprint lanes as negative/control memory; do not
  rerun the same candidate families on the current contract.
- A future single lane that actually reaches `SHORTLIST_CANDIDATE` /
  `READY_FOR_REPLAY` under the frozen gate may be packaged as a scoped RESULT.
- Alternatively, a separately scoped, maintainer-approved task that is permitted
  to re-execute one deterministic factory/bounded run could package a single
  replay-backed negative RESULT with a real verification block; that is out of
  scope here because rerunning is forbidden.

## Stop conditions preserved

- Do not rerun, tune, or add feature families.
- Do not score the post-AME2020 holdout or any reveal source.
- Do not create prediction, claim, knowledge, or result artifacts from this
  preflight.
- Do not describe any lane as a surviving candidate or a nuclear mass-law result.

## Output routing

- Task verdict: `GATE_A_BLOCKED_KEEP_AS_NEGATIVE_CONTROL_MEMORY`.
- Canonical destination:
  `docs/reviews/nmd0003-factory-negative-result-publication-preflight.md`.
- Review tier: `none`.
- Gate A status: blocked (no single deterministic artifact, no permitted replay,
  no promotable candidate, diagnostic slot already filled by `RESULT-0018`).
- Gate B status: not applicable; no RESULT or PRED artifact produced.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Result artifact impact: no `results/` artifact created or modified.
- Limitations / blockers: routing decision over committed sandbox evidence only;
  not an independent replay; the negative/control memory remains the campaign's
  durable contribution for this surface.
