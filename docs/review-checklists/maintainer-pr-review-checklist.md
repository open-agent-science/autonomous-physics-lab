# Maintainer PR Review Checklist

Use this checklist during pre-merge maintainer review.

## Task Identity

- Task id matches the PR title and task file.
- Task file path is correct.
- Task status is `REVIEW_READY`.
- The PR stays within one task scope.

## Branch / Commit / PR Format

- Branch follows `agent/<contributor-id>/<agent-id>/task-<task-number>-<short-slug>`.
- `contributor-id` is the lowercased GitHub username when available, or a stable
  maintainer-approved short id otherwise.
- PR Contributor ID metadata matches the contributor segment in the branch.
- PR title follows `TASK-XXXX: ...`.
- PR metadata block is filled in.
- Review bundle was generated from the PR branch, not `main`.

## Accepted Outputs

- Accepted outputs from the task file are present.
- Missing outputs are explained explicitly.
- Changed files match the accepted output surface.
- Routine task PRs do not edit generated `docs/task-views/*.md` unless the task itself is
  about board behavior or board-generation workflow.

## Validation

- Required validation commands are reported.
- Failures, skips, or limitations are explained.
- No unexplained artifact churn appears in the diff.

## Scientific Claim Impact

- No claim is promoted automatically.
- Claim wording remains aligned with evidence scope.
- Limitations and range bounds stay explicit.

## Result Artifact Impact

- Routine validation used `--output-dir` when appropriate.
- Committed `results/` artifacts were left untouched unless the task required
  them.
- Any canonical artifact changes are explained.

## Overclaim Language

- No "proved", "solved physics", or similar overclaim language was introduced.
- If the review helper reports overclaim terms as advisory warnings, inspect
  the nearby context. Guardrail or policy wording is acceptable; claim-like
  wording is not.
- Workflow or planning tasks stay framed as workflow or planning work.
- Review notes distinguish evidence from proposal.

## Repository Safety

- No obvious unsafe execution pattern was introduced.
- Sensitive surfaces such as `scripts/` or `.github/workflows/` received extra
  maintainer attention.
- The PR does not introduce code that could silently harm local developer
  environments or repository automation.

## Maintainer Verdict

- `MERGE_OK`
- `NEEDS_CHANGES`
- `BLOCKED`

Record the verdict with a short reason and any follow-up required before merge.

## Closeout Actions

- Confirm whether post-merge closeout is expected.
- Note whether the merged task should later update `docs/multi-agent-dry-run.md`.
- Note any follow-up task that should be created instead of stretching this PR.
