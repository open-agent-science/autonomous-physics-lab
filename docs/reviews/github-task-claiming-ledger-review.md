# GitHub Task Claiming Ledger Review

## Scope

This review note documents the `TASK-0421` implementation of a lightweight
GitHub-native task claiming ledger.

The change adds:

- `docs/agent-task-claiming.md`
- `.github/ISSUE_TEMPLATE/task-claim.yml`

It does not add a custom server, database, scheduler, dashboard, or autonomous
multi-agent runtime.

## Problem Addressed

APL can run multiple agents in parallel, but duplicate task execution can create
conflicting pull requests and overlapping write surfaces. A recent failure mode
is two agents implementing the same canonical task and writing the same
`agent_runs/` or `docs/reviews/` paths.

The claiming ledger makes agents declare:

- the canonical `TASK-XXXX` being worked;
- the responsible contributor and agent;
- the planned branch;
- expected write surfaces;
- artifact tier or sandbox boundary;
- existing PR and claim search results;
- claim expiry.

## Design Choice

The ledger is GitHub-native. It uses PR metadata, issue-template claims, labels,
or maintainer comments instead of a new coordination database.

This keeps coordination close to:

- canonical task files;
- task PRs;
- issue search;
- branch names;
- maintainer review.

## Duplicate Resolution Policy

When duplicate PRs already exist for the same task, the policy recommends:

1. prefer the maintainer-designated PR;
2. otherwise prefer the earlier passing, smaller-scope PR;
3. avoid overwriting existing artifact paths;
4. close the duplicate with a comment linking the kept PR;
5. salvage useful changes only through review comments or follow-up tasks.

## Boundary

The claiming ledger is workflow coordination only.

It does not:

- assign scientific truth;
- promote claims;
- approve results;
- create canonical scientific artifacts;
- replace maintainer review;
- decide merge readiness.

## Validation Plan

Expected validation:

```bash
python -m ruff check .
python -m pytest
python -m physics_lab.cli validate-repo . --strict --fail-on-warnings
```

The issue template is YAML-only and should be covered by repository-level link
and strict validation checks.
