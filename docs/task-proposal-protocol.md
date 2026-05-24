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

## Multiple Proposals Per PR

A single proposal PR may include more than one `tasks/proposals/*.yaml` file.

This is allowed when the PR stays clearly proposal-only and the ideas are
coherent enough to review as one batch.

Use a batched proposal PR when:

- the proposals belong to the same theme, campaign, or salvage pass;
- the maintainer asked for a batch;
- or splitting them would add review overhead without making acceptance
  meaningfully clearer.

Split the PR instead when:

- the proposals are unrelated;
- one of them is likely to need much deeper discussion than the others;
- or the diff is no longer obviously a lightweight proposal-only review.

Every proposal file in a batched PR must still:

- keep `status: PROPOSED`;
- avoid guessing canonical `TASK-XXXX` ids;
- avoid touching `tasks/ACTIVE.md` or canonical task files.

Maintainer review agents should validate every changed proposal file in the
batch and run proposal-level repository validation once for the PR. A
multi-proposal PR is a supported first-class proposal shape, not a reason to
skip validation or require a separate PR per file.

Bundling unrelated proposals is discouraged even when technically allowed.

## Salvaging Useful Ideas From Stale PRs

If an older PR is stale, superseded, or poorly shaped but still contains one
or more useful task ideas:

1. Do not keep patching the old mixed-context PR.
2. Create a fresh proposal file under `tasks/proposals/`.
3. Start a clean branch using the canonical proposal branch format:
   `agent/<contributor-id>/<agent-id>/propose-task-<short-slug>`.
4. Open a clean replacement PR titled:
   `TASK-PROPOSAL: <short title>`.
5. Close the stale PR as `superseded` or `stale` once the replacement exists.

Salvaged ideas may be grouped into one clean proposal PR when they are closely
related and the PR remains proposal-only. If the ideas are unrelated, split
them into separate proposal PRs.

## Proposal Validation

Task proposal PRs should stay lightweight.

The same validation rule applies to one proposal file or many proposal files in
the same PR. Review tooling should validate all changed
`tasks/proposals/*.yaml` files and run proposal-level repository checks once
for the batch.

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

When a maintainer or maintainer-directed task-admin agent promotes one or more
accepted ideas into canonical tasks, prefer a `TASK-QUEUE` PR:

- branch: `agent/<contributor-id>/<agent-id>/task-queue-<short-slug>`
- title: `TASK-QUEUE: <short summary>`
- queued canonical tasks remain `READY`, `BLOCKED`, or `PROPOSED`

This keeps task creation reviewable without requiring a separate canonical
curation task for every newly queued task.

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
