# Private Contributor Scorecard

Use this scorecard for private contributor or contributor-agent test PRs.

The goal is not to rank people. The goal is to see whether the repository
workflow is clear enough for a new contributor to succeed without hidden
maintainer context.

## Score Levels

- `PASS` - acceptable for private validation evidence
- `PASS_WITH_NOTES` - usable, but the docs or helper tooling should improve
- `NEEDS_REWORK` - contributor can continue after protocol or artifact fixes
- `BLOCKED` - task or repository instructions are unclear or unsafe

## Review Questions

### Orientation

- Did the contributor find the right starting docs?
- Did they choose a task that matched their scope and skill level?
- Did they avoid side-channel assumptions not present in the repository?

### Protocol

- Did the branch follow the canonical format?
- Did the PR title follow the canonical format?
- Did the PR body include task and contributor metadata?
- Did the PR stay inside one task or one approved batch?

### Validation

- Were validation commands run and reported?
- Did local validation pass before review?
- Did CI pass before merge?
- Were generated files such as `docs/task-views/*.md` and `CONTEXT.md` synced when
  needed?

### Scientific Safety

- Did the PR avoid automatic claim or knowledge promotion?
- Were sandbox outputs kept out of canonical `results/` unless explicitly
  scoped?
- Were limitations, verdicts, and failure cases visible?
- Were negative or overfit outcomes preserved when relevant?

### Reviewability

- Could a maintainer understand the artifact trail quickly?
- Did the review helper identify real risks?
- Were requested changes small and actionable?
- Did closeout work cleanly after merge?

## Per-PR Record

For each private-validation PR, record:

```text
PR:
Contributor ID:
Agent tool:
Task:
Track: docs | technical | replay | audit | sandbox science | closeout
Score:
Protocol issues:
Validation issues:
Scientific safety issues:
Review-helper result:
Maintainer notes:
Follow-up task needed:
```

## Readiness Signal

The private validation phase is healthy when most PRs score `PASS` or
`PASS_WITH_NOTES`, recurring failures are turned into docs or tooling tasks, and
scientific PRs remain reviewable without automatic claim promotion.

