# Private Contributor Pilot

This document explains how invited contributors should work. It originated in the
`v0.1-private-alpha` contributor pilot; the same workflow discipline applies now
that the repository is public.

The repository is public as of 2026-06-28 (v0.2 public-alpha). Contributions
should still optimize for reproducible scientific work, task clarity, and review
discipline rather than speed or broad visibility.

For the current pre-public validation gates, see
[private-contributor-validation-plan.md](./private-contributor-validation-plan.md),
[private-agent-test-metrics.md](./private-agent-test-metrics.md), and
[private-contributor-scorecard.md](./private-contributor-scorecard.md).
For a practical Level 1/2/3 onboarding ladder, use
[private-agent-challenge-pack.md](./private-agent-challenge-pack.md).

## Clone the Repository

After the maintainer grants access, clone the repository with HTTPS:

```bash
git clone https://github.com/open-agent-science/autonomous-physics-lab.git
cd autonomous-physics-lab
```

Then create and activate a local environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Pick a Task

Choose one `READY` task from [the task views](task-views/research.md).
If the maintainer asks you to start from an onboarding challenge, choose a
Level 1, Level 2, or Level 3 item from
[private-agent-challenge-pack.md](./private-agent-challenge-pack.md) and still
tie the PR to one canonical task, proposal, or approved queue item.

If no existing `READY` task fits, create a task proposal instead of guessing a
new canonical task id. Use
[task-proposal-protocol.md](./task-proposal-protocol.md).

Before starting:

1. Read [../AGENTS.md](../AGENTS.md).
2. Read [agent-task-protocol.md](./agent-task-protocol.md).
3. Read [status.md](./status.md), [strategy.md](./strategy.md), and
   [agent-operating-model.md](./agent-operating-model.md).
4. Confirm that the task is atomic and does not silently expand scope.

If a task is unclear, narrow it first. Do not combine several unrelated tasks in
one PR.

Not every task points to a concrete benchmark.

- science execution tasks should reference a real `hypothesis_id` and `experiment_id`
- planning tasks may use `mode: planning_only`
- contributor or workflow tasks may use `mode: workflow`

Do not add fake pendulum references to unrelated planning tasks just to match an
older task shape.

## Branch Naming Convention

Use the canonical format from
[agent-task-protocol.md](./agent-task-protocol.md):

`agent/<contributor-id>/<agent-id>/task-<task-number>-<short-slug>`

Example:

```bash
git checkout -b agent/gladunrv/codex/task-0011-numerical-audit
```

Rules:

- `contributor-id` SHOULD be the lowercased GitHub username for the human
  responsible for the PR when available; otherwise use a stable
  maintainer-approved short id
- use authenticated local GitHub identity first when available; local Git
  config is only a clue, and unrelated PR authors or branch examples are not a
  safe source for the current contributor id
- `agent-id` is the execution tool or mode
- lowercase only
- no spaces
- no underscores
- include the task number
- keep the slug short
- keep the separate `GitHub username` PR metadata field filled in, even when it
  matches `contributor-id`

Create and switch to this branch before editing repository files or generating
task artifacts.

Do not work directly on `main`. Do not invent alternate branch formats.
Older private-pilot branches may still use the legacy `agent/<agent-id>/...`
shape; keep them as historical records rather than renaming them.

For task proposals, use:

`agent/<contributor-id>/<agent-id>/propose-task-<short-slug>`

## Commit and Pull Request Format

Use the canonical commit and PR title formats from
[agent-task-protocol.md](./agent-task-protocol.md).

Examples:

```text
docs(task-0019): standardize agent task protocol
TASK-0019: Standardize agent branch, commit, and pull request protocol
TASK-PROPOSAL: Add contributor task proposal protocol
```

## Pull Request Requirements

Every PR must:

- link to a `TASK-*` id
- use the standard PR title format
- stay within one atomic task scope
- explain what changed and why
- state any scientific limitations clearly
- include validation results
- include the Agent / Contributor Metadata block from the PR template
- wait for maintainer review before merge
- remain `REVIEW_READY` until the maintainer completes review and merge

## Required Validation Before PR

Run all of the following for canonical task PRs:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum
python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
git diff --exit-code
```

For task proposal PRs, use the lighter validation path:

```bash
./scripts/validate_quick.sh
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
./scripts/apl_review_bundle.sh
```

Use `--output-dir` for routine example runs so committed canonical artifacts do
not change accidentally.

## What Not to Do

- do not work directly on `main`
- do not invent local branch, PR, or identity formats
- do not rewrite canonical `results/` artifacts casually
- do not expand a task into dashboard, web API, database, ingestion, or runtime work
- do not promote claims without maintainer review
- do not present a numerical fit as a scientific discovery
- do not use marketing language such as "AI solved physics"

## Overclaiming Guardrails

Keep scientific wording conservative:

- say "validated to tolerance" for numerical agreement
- do not say "100% exact" unless symbolic equality is proven
- keep range limits, assumptions, and failure modes visible
- treat generated claim updates as review suggestions, not automatic truth

Claims must not be promoted without maintainer review. Follow
[claim-promotion-policy.md](./claim-promotion-policy.md) before changing any
claim status.

## Maintainer Closeout

After merge, the maintainer may use
[maintainer-review-agent.md](./maintainer-review-agent.md) to confirm that the
accepted outputs landed in `main`, move the task to `DONE`, update
[the task views](task-views/research.md), and record a dry-run note when the PR
belongs to the private pilot.
