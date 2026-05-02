# GitHub Branch Protection Plan

This document separates what to do now in the private repository from what to
enable later when the repository becomes public.

## Private Repository Phase

Use branch and PR discipline manually if GitHub does not yet enforce every
branch-protection rule.

Current expectations:

- no direct work on `main`
- contributors work in branches
- every meaningful change goes through a PR
- maintainer reviews PRs before merge
- CI should pass before merge

If GitHub protection settings are not fully available yet, keep the workflow
discipline manual rather than relaxing the review rules.

## After the Repository Becomes Public

Target branch:

- `main`

Enable:

- Require a pull request before merging
- Required approvals: `1`
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Required checks:
- `Python tests (3.11)`
- `Python tests (3.12)`
- Require conversation resolution before merging
- Block force pushes
- Block deletions if available
- Do not allow bypassing the above settings if available

Do not enable yet:

- signed commits
- linear history
- deployments
- code scanning gates
- automatic Copilot review

## Practical Note

Required status checks may appear only after a CI run exists or after a PR has
already been opened. If a required check is missing from the GitHub settings UI,
create or rerun the matching workflow first, then return to the protection
settings.
