# Agent-Published Result Checklist

Use this checklist before reviewing an `AGENT_PUBLISHED` `RESULT-*` or
generic `PRED-*` publication PR. The artifact is still not independently
validated or maintainer-reviewed; Gate A only confirms that the publication is
mechanically reproducible and safely bounded.

## Run The Gate

```bash
python3 scripts/apl_check_result_publication.py path/to/result.yaml
python3 scripts/apl_check_result_publication.py path/to/PRED-XXXX.yaml
```

Use `--json` when a review helper needs machine-readable output.

## RESULT-* Gate A

- `review_tier` is `AGENT_PUBLISHED`.
- `agent_proposal_evaluation.review_tier_proposed` matches the artifact tier.
- Every Gate A key in `agent_proposal_evaluation.gates_checked` is present and
  set to `true`.
- `command`, `code_reference`, `engine_version`, and `git_commit` are populated
  with non-placeholder values.
- `verification.checks` has at least one concrete deterministic check.
- `input_file_hashes` includes source paths and 64-character SHA-256 values.
- `limitations` and `evidence_summary` are non-empty.
- The `result_id` is not already pinned in `results/golden-results.yaml`.
- The artifact does not introduce positive-context breakthrough, proof, or
  solved-physics wording.

## PRED-* Gate A

- `review_tier` is `AGENT_PUBLISHED`.
- `source_state.git_commit`, `model_reference`, target set, and reveal
  conditions are populated.
- `source_state.live_external_fetch_allowed` is `false`.
- `claim_ceiling` explicitly says this is not a claim.
- No-peek, frozen-model, named-target, reveal-condition, non-claim, schema, and
  overclaim gates are all checked.

If any Gate A item fails, keep the PR in draft and fix the artifact before
asking for maintainer merge.
