# Private Agent Test Metrics

Use these metrics to evaluate private contributors and their agents before
opening the repository publicly.

The metrics are workflow-quality gates, not marketing claims.

## Cohort Metrics

- invited contributors or contributor-agent pairs
- total task-based PRs
- scientific sandbox PRs
- technical, docs, or test PRs
- independent replay or audit PRs
- first-time contributor PRs completed without maintainer side-channel help

## Protocol Metrics

- PRs with canonical branch format
- PRs with canonical title format
- PRs with complete Agent / Contributor Metadata
- PRs linked to an existing task, proposal, queue, or closeout lane
- PRs with review bundle generated from the PR branch
- PRs requiring protocol-only rework
- direct pushes to `main`

Target before public opening:

- 10 or more task-based PRs
- 0 direct pushes to `main`
- 0 unreviewed merges
- 0 missing task references in merged PRs

## Validation Metrics

- PRs with reported validation commands
- PRs where local validation passed before review
- PRs where GitHub CI passed before merge
- PRs where generated board/context files were synced
- PRs leaving dirty generated files after merge
- review-helper false negatives or false positives

Target before public opening:

- green CI on the release-candidate state
- 0 dirty active-board or context sync after merge
- review helper catches protocol blockers before merge

## Scientific Safety Metrics

- sandbox results preserved as sandbox evidence
- negative or overfit results preserved instead of hidden
- canonical result artifacts changed only with explicit task scope
- claims promoted automatically
- knowledge promoted automatically
- overclaim wording found during review
- local path leaks in public-facing docs

Target before public opening:

- 0 automatic claim promotions
- 0 automatic knowledge promotions
- 0 public-facing local path leaks
- all scientific PRs include limitations and verdicts

## Private Validation Snapshot

When preparing a public-readiness decision, summarize:

- number of contributors
- number and type of PRs
- number of scientific sandbox PRs
- number of replay or audit PRs
- number of protocol failures and their causes
- number of review-helper catches
- number of claim-promotion attempts blocked
- remaining blockers before public opening

