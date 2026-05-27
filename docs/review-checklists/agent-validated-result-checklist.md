# AGENT_VALIDATED Result Checklist

Use this checklist when reviewing a PR that upgrades an existing
`AGENT_PUBLISHED` `RESULT-*` artifact through Gate B.

## Required Inputs

- The source artifact is an existing canonical `RESULT-*` with
  `review_tier: AGENT_PUBLISHED`.
- The source artifact records a deterministic replay command, input file
  hashes, engine version, git commit, limitations, and `best_verdict`.
- The validating agent records:
  - contributor id;
  - GitHub username;
  - agent tool;
  - model/version.
- Prefer cross-tool validation (`Claude Code` validates a `Codex` result, or
  `Codex` validates a `Claude Code` result). Same-tool replay is acceptable
  only when clearly disclosed.

## Gate B Pass Conditions

- The exact input files still match the recorded `sha256` hashes.
- The replay command is a safe `physics-lab run ...` command, not arbitrary
  shell.
- Replay output is written to a temporary or explicit non-canonical output
  directory.
- `best_verdict` is unchanged.
- Key numeric metrics match within the declared tolerance.
- Any warning about missing or same-agent metadata is recorded in the PR.

## Allowed Output

When replay passes, the agent may propose a `validation_record` block for the
existing `agent_proposal_evaluation` section:

```yaml
review_tier_proposed: AGENT_VALIDATED
best_verdict_proposed: <unchanged verdict>
gates_checked:
  same_inputs: true
  same_deterministic_command: true
  metrics_match_within_tolerance: true
  verdict_unchanged: true
  independent_replay_metadata_recorded: true
validation_record:
  replayed_by:
    contributor_id: roman
    github_username: gladunrv
    agent_tool: Codex
    model_version: GPT-5 Codex
  replayed_at_utc: "2026-06-01T12:00:00+00:00"
  replay_command: "physics-lab run examples/example.yaml"
  tolerance_used: 1.0e-9
  drift_observed: none
```

## Contested Result Handling

If metrics drift, the verdict changes, input hashes fail, or the replay command
is unsupported, do not upgrade the result. Open or keep a contested-result PR
with the generated report and leave the source result at
`review_tier: AGENT_PUBLISHED`.

Gate B is independent validation, not maintainer endorsement and not claim
promotion.
