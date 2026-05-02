# Task Proposal Protocol

## Purpose

This protocol exists to keep new task creation simple without creating
canonical `TASK-XXXX` conflicts during parallel agent work.

Default rule:

- new task ideas should start as **task proposals**
- canonical `TASK-XXXX` ids should be assigned only after acceptance

This prevents the repository from needing "a task to create a task" while still
keeping canonical numbering controlled and reviewable.

## When To Create A Task Proposal

Create a task proposal when:

- no existing `READY` task fits the work;
- the maintainer has not explicitly assigned a canonical `TASK-XXXX` id;
- you want to suggest a new benchmark, workflow, documentation change, or
  contributor process improvement;
- parallel contributors or agents may be proposing ideas at the same time.

Do not guess the next canonical task number during parallel work.

## When To Create A Canonical Task Directly

Create a canonical `TASK-XXXX` file directly only when at least one of the
following is true:

- the maintainer explicitly assigned the id;
- the maintainer explicitly asked for a specific `TASK-XXXX` task;
- a maintainer-run task-admin or review agent is acting on explicit maintainer
  instruction;
- the numbering is controlled and no proposal-first step is needed.

Normal agents should prefer proposal-first.

## Proposal Files

Store task proposals under:

`tasks/proposals/`

Filename format:

`tasks/proposals/YYYYMMDD-<contributor-id>-<short-slug>.yaml`

Examples:

- `tasks/proposals/20260502-roman-koide-track.yaml`
- `tasks/proposals/20260502-ihor-rf-signal-sandbox.yaml`
- `tasks/proposals/20260502-claude-diffusion-benchmark.yaml`

Use [../tasks/proposals/TASK-PROPOSAL-TEMPLATE.yaml](../tasks/proposals/TASK-PROPOSAL-TEMPLATE.yaml)
as the starting template.

## Proposal Branch Naming

Use this branch format for task proposals:

`agent/<contributor-id>/<agent-id>/propose-task-<short-slug>`

Example:

`agent/roman/codex/propose-task-koide-track`

Do not invent alternate proposal branch formats.

## Proposal PR Title Format

Use:

`TASK-PROPOSAL: <short title>`

Example:

`TASK-PROPOSAL: Add Koide particle mass relation track`

## Proposal Validation

Task proposal PRs should stay lightweight.

Recommended validation:

```bash
./scripts/validate_quick.sh
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
./scripts/apl_review_bundle.sh
```

Use heavier benchmark execution only when the proposal PR also changes code
that genuinely requires it.

## Proposal Review Checklist

Maintainers or maintainer-run review agents should check that a proposal:

- does not invent a canonical `TASK-XXXX` id;
- uses the correct proposal filename, branch, and PR title format;
- is aligned with repository strategy;
- is atomic enough for a future canonical task;
- avoids overclaim or premature discovery language;
- has clear accepted outputs;
- does not change canonical result artifacts casually;
- does not promote claims automatically.

## Promotion To Canonical Task

A proposal becomes a canonical task only after maintainer acceptance.

Promotion flow:

1. Review the proposal PR.
2. Decide whether to accept, reject, or defer it.
3. If accepted, assign the next available canonical `TASK-XXXX` id.
4. Create `tasks/TASK-XXXX-<short-slug>.yaml`.
5. Update `tasks/ACTIVE.md`.
6. Optionally update the original proposal file status to `ACCEPTED` and record
   the canonical id, or remove the proposal after the canonical task lands.

Promotion target:

`tasks/TASK-0043-short-slug.yaml`

Only the maintainer, or a maintainer-directed task-admin/review agent, may do
this id assignment.

## Who Assigns Canonical Task IDs

Allowed:

- maintainer
- maintainer-directed task-admin agent
- maintainer-directed review or closeout agent

Not allowed by default:

- normal agents working in parallel
- contributors guessing the next free id
- proposal PRs that self-assign canonical task numbers without approval

## Canonical Task Rules Still Apply

Canonical tasks still use:

- branch format: `agent/<contributor-id>/<agent-id>/task-<task-number>-<short-slug>`
- PR title format: `TASK-XXXX: <short title>`
- canonical template:
  [../tasks/TASK-TEMPLATE.yaml](../tasks/TASK-TEMPLATE.yaml)

Task proposals do not replace canonical tasks. They simplify how new task ideas
enter the repository.
