# Agent Task Protocol

This document defines the canonical task-execution protocol for Codex, Claude
Code, humans, and other agents working in this repository.

Do not invent branch names, commit formats, PR titles, or task-state
transitions locally. Use this document.

## Read Order

Before starting a task, read:

1. [../AGENTS.md](../AGENTS.md)
2. [./agent-task-protocol.md](./agent-task-protocol.md)
3. [../tasks/ACTIVE.md](../tasks/ACTIVE.md)
4. the matching `tasks/TASK-XXXX-*.yaml` file
5. [./strategy.md](./strategy.md)

Use [./agent-operating-model.md](./agent-operating-model.md) and
[./contributing-workflow.md](./contributing-workflow.md) for supporting
context, not as competing protocol definitions.

## Pick a Task

1. Start with one atomic task that is already `READY`.
2. Do not start a second task unless a human explicitly asks for it or the work
   is clearly independent.
3. Do not start `REVIEW_READY`, `BLOCKED`, or `REJECTED` tasks unless a human
   explicitly redirects you.
4. If no existing task fits, ask for or propose a new task before doing
   substantial work.

## Task Status Protocol

Use these execution states:

- `READY`: approved, scoped, and available to start.
- `IN_PROGRESS`: actively being worked on by one contributor or agent.
- `REVIEW_READY`: implementation is complete, validation ran, and maintainer
  review is required.
- `DONE`: maintainer-reviewed and accepted. Agents must not mark their own task
  `DONE`.
- `BLOCKED`: work cannot continue until a dependency, decision, or external
  action is resolved. State the blocker clearly.
- `REJECTED`: the task should not proceed in its current form.

Rules:

- An agent may move `READY -> IN_PROGRESS`.
- An agent may move `IN_PROGRESS -> REVIEW_READY`.
- Only a maintainer should move `REVIEW_READY -> DONE`.
- If blocked, set `BLOCKED` and explain why in the task file, board, or PR.
- `PROPOSED` may still appear in backlog planning, but it is not an executable
  task state for active task execution.

## Branch Naming

Use exactly this format:

`agent/<contributor-id>/<agent-id>/task-<task-number>-<short-slug>`

Examples:

- `agent/roman/codex/task-0011-numerical-audit`
- `agent/roman/claude/task-0017-dimensional-challenge`
- `agent/ihor/human/task-0032-public-result-package`

Field meanings:

- `contributor-id`: the human responsible for the PR and review loop.
- `agent-id`: the execution mode or tool, such as `codex`, `claude`,
  `cursor`, `human`, or `other`.

Rules:

- lowercase only
- no spaces
- no underscores
- include the task number
- keep the slug short
- do not invent fantasy agent identities as the canonical id

Historical note:

- older private-pilot branches may still use `agent/<agent-id>/...`
- do not rename old branches or rewrite history just to match the new format

## Commit Message Format

Use exactly this format:

`<type>(task-<task-number>): <short summary>`

Examples:

- `feat(task-0011): add numerical precision audit`
- `docs(task-0014): plan thought experiment suite`
- `fix(task-0018): support planning-only task inputs`
- `test(task-0017): add dimensional challenge tests`

Allowed commit types:

- `feat`
- `fix`
- `refactor`
- `docs`
- `test`
- `chore`

Keep commits narrow. Do not mix unrelated tasks in one commit.

## Commit Permission

Agents may commit only when explicitly instructed.

A commit means the agent believes the task is ready for maintainer review.

After committing, the task status should be `REVIEW_READY`, not `DONE`.

`DONE` is set only by the maintainer after review and merge.

## Pull Request Title Format

Use exactly this format:

`TASK-0011: Audit numerical precision vs model residual`

The PR must stay within one task scope and make the linked task easy to review.

## Open a Pull Request

After implementation and validation:

1. push the task branch only when a human or workflow expects a PR;
2. open one PR for one task branch;
3. use the required PR title format;
4. complete the repository PR template;
5. include limitations, validation results, and artifact-impact notes;
6. move the task to `REVIEW_READY`.

## Pull Request Requirements

Every PR should include:

- Task ID
- task file path
- branch name
- contributor id
- GitHub username
- agent tool
- model/version if known
- agent session id
- human reviewer
- summary
- changed files
- validation commands
- scientific claim impact
- result artifact impact
- maintainer review notes

Use the repository PR template.

## Required Validation

Run these commands before handoff:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum
python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
git diff --exit-code
```

Use `--output-dir` for routine example runs so committed canonical artifacts do
not change accidentally.

Before opening a PR, also generate a review bundle for the maintainer:

```bash
./scripts/apl_review_bundle.sh
```

This produces `_snapshots/review_<branch>_<timestamp>.md` with the full diff
vs `main`, commit list, and changed-file summary.

## Task Execution Flow

1. Read the files listed above.
2. Confirm the task is `READY` and atomic.
3. Create the branch using the required naming format.
4. Set the task status to `IN_PROGRESS` in the task file and update
   [../tasks/ACTIVE.md](../tasks/ACTIVE.md).
5. Make the smallest reproducible change that satisfies the task.
6. Run the required validation commands.
7. Set the task to `REVIEW_READY` when implementation and validation are done.
8. Leave clear maintainer review notes and limitations.

## AI Agent Attribution

AI agents (Claude Code, Codex, Cursor, or any LLM tool) are execution tools,
not git co-authors. Record them in PR metadata, not in git commit history.

Rules:

- Do **not** add `Co-Authored-By` trailers for AI agents in commit messages.
- Record agent involvement in the **Agent / Contributor Metadata** section of
  the PR description (see PR template).
- The human contributor remains the git author and the responsible reviewer.
- Git history must reflect only human authors.
- Agents must not invent their own identity format for branches, PRs, or
  attribution fields.

## Scientific Claim Restrictions

- Do not promote claims automatically.
- Do not strengthen claim status without maintainer review and evidence.
- Do not present a numerical fit as a discovery without deterministic support.
- Keep range limits, assumptions, and failure modes explicit.
- Do not change committed `results/` artifacts unless the task explicitly
  requires it and the PR explains why.

## Forbidden Actions

- do not work directly on `main`
- do not invent local branch, commit, or PR formats
- do not mark your own task `DONE`
- do not start unrelated tasks in the same branch or PR
- do not add dashboard, web API, database, ingestion, or runtime infrastructure work
- do not make the repository public
- do not promote claims or knowledge without review
- do not silently rewrite canonical scientific artifacts

## Standard Prompt

Use this prompt when assigning work to an agent:

```text
Execute TASK-0011 according to AGENTS.md and docs/agent-task-protocol.md.
Use contributor id: roman.
Use agent id: codex.
Do not start any other task.
```
