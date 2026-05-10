# Public Release Gates

This repository stays private until all gates below are satisfied.

The goal is not to optimize for a fast public launch. The goal is to confirm
that the private-alpha workflow works with invited contributors, branch-based
review, reproducible validation, and at least one honest scientific result.

The detailed private validation plan lives in
[private-contributor-validation-plan.md](./private-contributor-validation-plan.md).
Use [private-agent-test-metrics.md](./private-agent-test-metrics.md) and
[private-contributor-scorecard.md](./private-contributor-scorecard.md) to collect
evidence for Gate 2.

## Gate 1 — Technical Stability

All of the following must be true:

- clean git state
- CI green
- `python3 -m physics_lab.cli validate-repo .` green
- `python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings` green
- no local path leaks
- no tracked cache, OS, or agent-local files

Suggested evidence:

- latest CI run link
- maintainer validation log
- repository snapshot without local-only files

## Gate 2 — Multi-Agent Contributor Pilot

All of the following must be true:

- 3-5 invited contributors or contributor-agent pairs
- 10 or more task-based PRs
- 3 or more scientific sandbox PRs
- 2 or more technical, docs, or test PRs
- 2 or more independent replay or audit PRs
- each PR links to a task
- each PR passes CI
- maintainer review happens before merge
- no direct pushes to `main`
- no automatic claim or knowledge promotion
- no dirty active-board or context sync after merge

Suggested evidence:

- PR list with linked `TASK-*` ids
- validation logs per PR
- short maintainer summary of what worked and what caused friction

## Gate 3 — Measurable Scientific Result

At least one public-facing result must exist. Examples:

- 100 candidate formulas tested
- failure modes classified
- leaderboard generated
- report explains limitations
- no global or exact discovery claim

At least one clear falsification surface should also remain visible as
first-class evidence rather than being hidden behind successful reproductions
only.

Required wording discipline:

- do not claim final physics answers from APL outputs
- do not claim "new physics" without exceptional evidence and review
- do not say "100% exact" unless symbolic equality is proven
- prefer "validated to tolerance" for numerical agreement

## Gate 4 — Public Narrative

All of the following must be true:

- `README.md` has a result summary
- an announcement draft exists
- no final-answer, universal-theory, or discovery-level overclaim
- claims remain review-gated
- guarded stress-test outputs are not presented as flagship public successes

## Release Decision

The repository may become public only when all four gates are satisfied and a
maintainer explicitly decides that the current docs, task board, and scientific
claims are aligned with the evidence.
