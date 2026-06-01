# Factory Summary Artifact (TASK-0505)

The machine-readable per-run output of a bounded research factory, defined by
[Research Factory Protocol](research-factory-protocol.md). One `factory_summary`
records what a factory run generated, how candidates were controlled, and how
each was routed — **without promoting any claim**.

- Schema: `physics_lab/schemas/factory_summary.schema.json`
- Validation kind: `factory_summary` (see `physics_lab/registry/validation.py`)
- Location: a per-run sandbox artifact under `agent_runs/AGENT-RUN-*/` (it is
  sandbox evidence, not a canonical `results/` artifact).

## Shape

Campaign-agnostic core fields, with an optional `campaign_specific` block that
each adapter contract defines (Nuclear, Exoplanet, Quantum, Atomic, Textbook).

- **Identity**: `schema_version`, `factory_id`, `campaign_id`, `adapter_id`,
  `adapter_version`, `task_id`.
- **Inputs**: `dataset` (pinned snapshot ref, retrieval policy, checksum policy),
  `baseline` (`frozen` or `null`), optional `splits`, `candidate_cap`.
- **Candidate accounting**: `candidate_counts` distinguishes `generated`,
  `preflight_rejected`, `executed`, `shortlisted`, and `rejected_by_control` —
  the required explicit state distinction.
- **Controls**: a list of applied controls and outcomes.
- **Candidates**: per-candidate `family`, `parameters`, train/holdout/stress
  `metrics`, `control_outcomes`, `complexity`, `leakage_status`
  (`CHECKED_CLEAN` / `NOT_CHECKED` / `LEAKAGE_FOUND`), `candidate_state`, and
  `route_verdict`.
- **Routing**: `route_verdict_summary` counts per canonical route verdict.
- **Honesty**: non-empty `limitations`, plus `reproducibility`
  (`code_reference`, `command`, `run_date`, optional `seed`).

## Route verdicts and result-promotion compatibility

The `route_verdict` enum is the canonical set from the factory protocol:
`NEGATIVE_RESULT`, `INCONCLUSIVE`, `SHORTLIST_CANDIDATE`, `READY_FOR_REPLAY`,
`READY_FOR_PRED_FREEZE`, `REJECTED_BY_CONTROL`, `LOCAL_ONLY`,
`DATA_QUALITY_BLOCKED`.

A route verdict is a **routing signal, not a promotion**. Compatibility with
[result-promotion-protocol.md](result-promotion-protocol.md):

- `NEGATIVE_RESULT` / `INCONCLUSIVE` describe negative or inconclusive evidence
  that may later become a `RESULT-*` (`best_verdict: INVALID` / `INCONCLUSIVE`)
  only through a separate maintainer-gated promotion task;
- `SHORTLIST_CANDIDATE` / `READY_FOR_REPLAY` stay sandbox evidence until a replay
  or promotion task runs;
- `READY_FOR_PRED_FREEZE` is blocked by default and needs a no-peek
  prediction-freeze task plus maintainer approval;
- no `factory_summary` field creates a `RESULT-*`, `PRED-*`, `CLAIM-*`, or
  `KNOW-*` on its own.

## Boundaries

- This task adds the schema and docs only; it does not implement a runner
  (TASK-0506) or run a sprint (TASK-0507).
- A `factory_summary` is not committed as an agent-facing board or cache; it is a
  per-run artifact (see the generated-state postmortem).
