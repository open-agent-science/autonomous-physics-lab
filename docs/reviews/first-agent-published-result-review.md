# First AGENT_PUBLISHED Result Review

**Task:** `TASK-0412`
**Artifact:** `results/EXP-0011/RUN-0002/result.yaml`
**Result ID:** `RESULT-0016`
**Review tier:** `AGENT_PUBLISHED`
**Gate A status:** pass after `scripts/apl_check_result_publication.py`

## Candidate Choice

The publication candidate is the anharmonic oscillator period benchmark,
`EXP-0011`, replayed as `RUN-0002`. It was chosen over Nuclear or Exoplanet
evidence because it is a mature, deterministic benchmark with a conservative
scope, clear limitations, and no reveal or source-provenance ambiguity.

The result is deliberately low-risk: it preserves the existing
`VALID_IN_RANGE` benchmark-slice verdict for a conservative 1D quartic
oscillator. It does not make a claim about driven, damped, chaotic,
softening, double-well, or large-parameter regimes.

## Method

The deterministic replay command was:

```bash
python3 -m physics_lab.cli run examples/anharmonic_agent_published_result.yaml
```

The command wrote a fresh canonical run directory:

```text
results/EXP-0011/RUN-0002/
```

The workflow generated a new `RESULT-0016` payload with repository-pinned
inputs, input hashes, code reference, engine version, and git commit. The
AGENT_PUBLISHED metadata was then added to the result payload:

- `review_tier: AGENT_PUBLISHED`
- complete `agent_proposal_evaluation.gates_checked`
- explicit trust qualifier
- no claim or knowledge status transition

## Gate A Evidence

- Deterministic run: pass.
- Verification block populated: pass.
- Input hashes recorded: pass.
- Limitations listed: pass.
- Engine version and commit pinned: pass.
- Schema validation passes: pass.
- Protected artifact rewrite avoided: pass.
- Forbidden overclaim wording avoided: pass.
- Dataset provenance valid for this benchmark replay: pass.

## Boundaries

This PR does not pin `RESULT-0016` in `results/golden-results.yaml`.

This PR does not update any `CLAIM-*` or `KNOW-*` file. The generated
`claim_update*` and `knowledge_update*` files are workflow review artifacts
only; they are not applied to public scientific memory in this task.

`HYP-0011` is updated only to reference `RESULT-0016` in its evidence list.
This prevents the new canonical result from becoming orphaned while avoiding
any claim-status or knowledge-status promotion.

`RESULT-0016` is agent-published evidence only. It is not independently
validated, maintainer-reviewed, or external-replicated. A later Gate B replay
task should use a different agent/session before any tier upgrade.

## Verdict

`VALID_IN_RANGE`, limited to the configured anharmonicity train and holdout
slices. The result is suitable as the first low-risk `AGENT_PUBLISHED`
benchmark result because it exercises the publication machinery without
changing claims, knowledge, golden results, or higher-risk campaign surfaces.
