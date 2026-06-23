# RESULT-0011 Particle-Mass Falsifier Gate B Replay

- Task: `TASK-0811`
- Result: `RESULT-0011`
- Artifact: `results/EXP-0009/RUN-0001/result.yaml`
- Replay output: `/tmp/apl-gateb-result0011`
- Verdict: `GATE_B_PASS_AGENT_VALIDATED`

## Scope

This review records an independent Gate B replay of the legacy
`LEGACY_UNTIERED` particle-mass falsifier result (`RESULT-0011`). The replay
uses the committed CLI workflow and compares regenerated metrics against the
canonical artifacts.

This task does not run a new relation search, change family verdicts to force a
pass, edit `CLAIM-0007` status, create knowledge artifacts, or treat the quark
INVALID outcomes as scheme-independent conclusions.

## Replay Command

```bash
.venv/bin/python -m physics_lab.cli run examples/particle_mass_falsifier.yaml \
  --output-dir /tmp/apl-gateb-result0011
```

This matches the canonical RESULT command:

```text
physics-lab run examples/particle_mass_falsifier.yaml
```

The automated helper `scripts/apl_validate_agent_published_result.py` cannot
run on this artifact until a `review_tier` exists; this legacy result had no
tier before TASK-0811. Manual replay plus numeric comparison was therefore used
for the first Gate B certification.

## Gate B Outcome

| Check | Outcome |
| --- | --- |
| CLI exit | success |
| `result_id` / `best_verdict` | `RESULT-0011`, `INVALID` (unchanged) |
| Pinned config / experiment / hypothesis hashes | all match canonical snapshot |
| Pinned task hash | **differs** — only `status: REVIEW_READY` in frozen snapshot vs `status: DONE` in current task file; scientific inputs unchanged |
| Numeric metrics compared | 81 fields |
| Maximum absolute drift | `3.730349362740526e-14` |
| Tolerance | `1.0e-09` |
| Family Q values | charged leptons exact; up quarks exact; down quarks drift `3.33e-16` |
| Contested report | none |

The replay confirms that the committed falsifier evidence is deterministically
reproducible from the pinned scientific inputs and workflow. It validates the
existing **INVALID** global verdict and per-family split:

- charged leptons: `VALID` (`Q = 0.6666644634145`, gap `0.43 sigma`)
- up-type quarks: `INVALID` (`Q = 0.8489807776610612`, gap `159.16 sigma`)
- down-type quarks: `INVALID` (`Q = 0.7314967575627492`, gap `8.84 sigma`)

## Mixed Quark Limitation Preserved

The encoded up-type and down-type quark triplets retain their documented mixed
scheme/scale limitations (`MS-bar` running masses at different scales; top mass
as direct measurement). Gate B replay does not resolve or remove that boundary.

## Warning Preserved

Original publisher metadata is not stored on this legacy RESULT, so the replay
records validating-agent identity but cannot mechanically compare against the
original publishing identity.

## Result Routing

- Canonical destination: `results/EXP-0009/RUN-0001/result.yaml`
- Review tier: upgraded `LEGACY_UNTIERED` → `AGENT_VALIDATED`
- Gate A status: historical maintainer merge (no explicit tier recorded at publication)
- Gate B status: `PASS`
- Claim impact: none; `CLAIM-0007` remains `DRAFT`
- Knowledge impact: none
- Result impact: review-tier and `agent_proposal_evaluation.validation_record` update only
- Publication blocker: maintainer Gate C still required before any claim-status change

## Output-Routing Summary

| Field | Value |
| --- | --- |
| Task verdict | Gate B replay PASS; scientific verdict remains `INVALID` |
| Destination | this review + `results/EXP-0009/RUN-0001/result.yaml` metadata |
| Gate B | PASS → `AGENT_VALIDATED` |
| Claim / knowledge impact | none |
| Limitations | mixed quark inputs; legacy untiered origin; task snapshot status hash drift only |
