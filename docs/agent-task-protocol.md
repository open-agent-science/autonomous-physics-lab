# Agent Task Protocol

This document defines the canonical task-execution protocol for Codex, Claude
Code, humans, and other agents working in this repository.

Do not invent branch names, commit formats, PR titles, or task-state
transitions locally. Use this document.

## Read Order

Before starting a task, read:

1. [../AGENTS.md](../AGENTS.md)
2. [./agent-task-protocol.md](./agent-task-protocol.md)
3. [./task-proposal-protocol.md](./task-proposal-protocol.md) when proposing a new task idea
4. the relevant generated lane view under
   [./task-views/research.md](./task-views/research.md),
   [./task-views/support.md](./task-views/support.md), or
   [./task-views/release.md](./task-views/release.md)
5. [./task-views/research.md](./task-views/research.md) for the generated current-work navigation
6. the matching `tasks/TASK-XXXX-*.yaml` file when working on a canonical task
7. [./strategy.md](./strategy.md)

`docs/task-views/*.md` are the generated current-work navigation surfaces, and
`git log` is the task history. (The legacy `tasks/ACTIVE.md` full board was
retired — see TASK-0470/TASK-0473.)

Use [./agent-operating-model.md](./agent-operating-model.md) and
[./contributing-workflow.md](./contributing-workflow.md) for supporting
context, not as competing protocol definitions.

## Pick a Task

1. Start with one atomic task that is already `READY`.
2. Do not start a second task unless a human explicitly asks for it or the work
   is clearly independent.
3. Do not start `REVIEW_READY`, `BLOCKED`, `SUPERSEDED`, or `REJECTED` tasks
   unless a human explicitly redirects you.
4. If no existing task fits, ask for or propose a new task before doing
   substantial work.
5. Before substantial work on the chosen task, declare a claim per
   [./agent-task-claiming.md](./agent-task-claiming.md). The lightweight,
   GitHub-native claiming ledger prevents two agents from implementing the same
   `TASK-XXXX` or writing the same `agent_runs/`, `results/`, or
   `docs/reviews/` path.

When an executor agent reports "available tasks", it should list only
`READY` tasks. `REVIEW_READY` tasks are not available executor work; they belong
to maintainer review, merge decisions, or post-merge closeout. Mention
`REVIEW_READY` items only when the maintainer explicitly asks for review,
closeout, or queue triage.

For guided onboarding, use:

```bash
python3 scripts/apl_mission.py --output onboarding
```

The onboarding path dynamically tries to exclude `READY` tasks that already
have an open claim, an open PR, or a merged PR pending local closeout. This is
stdout-only coordination state; do not commit a generated availability cache.
When GitHub CLI or network metadata is unavailable, onboarding reports that it
is showing local registry-only options. Agents must then perform the manual
pre-claim search from `docs/agent-task-claiming.md` before starting work.

For an explicit live check from another output mode, add
`--github-availability auto` or use `--github-availability required` when a
registry-only fallback should fail clearly. If an approved Codex sandbox sets
the known loopback blocker proxy, add `--ignore-suspicious-proxy`; this clears
only blocker-valued proxy variables for the child GitHub CLI process.

## Task Proposals

If no existing `READY` task fits, do not guess the next canonical task number
during parallel work.

## Preserve External-Agent Signals

External agents should not leave actionable discoveries only in chat output,
PR prose, or private reasoning. When an agent notices a repository bug,
validation bottleneck, cross-platform failure, protocol ambiguity, optimization
opportunity, source lead, blocker, or scientific idea that is worth preserving,
it must route that signal into a durable coordination surface before handoff:

- create a `tasks/proposals/*.yaml` artifact when the idea may become future
  repository work but does not yet have a maintainer-assigned canonical task id;
- create the appropriate research proposal artifact when the signal is a new
  hypothesis, benchmark idea, source path, dataset lane, or scientific control
  rather than immediate maintenance work;
- open or reference a GitHub issue when the agent cannot safely edit the
  repository, when the signal is primarily operational coordination, or when a
  lightweight external report is the right first step;
- create a `TASK-QUEUE` item only when the maintainer explicitly asked for
  canonical future tasks.

Do not formalize every speculative thought. Formalize signals that are
actionable, likely to recur, likely to block another agent, or scientifically
useful enough that losing them would slow the project. If a signal is
intentionally advisory-only, say that explicitly in the handoff.

## Recurring Structural Bottlenecks

Agents should escalate a recurring structural bottleneck when the same blocker
class appears in two or more task attempts, PR reviews, validation loops, or
campaign handoffs and the issue is likely to keep slowing future work unless a
process, helper, protocol, source-lane, or task-shape change is reviewed.

Examples include repeated source-acquisition stalls, unclear source-to-row
handoffs, stale READY-pool droughts, recurring CI or review-helper failures,
validation commands that fail for the same environment reason, or task scopes
that repeatedly push agents into duplicate audits instead of durable scientific
outputs.

Escalation means creating or recommending a proposal; it does not grant agents
authority to assign canonical task ids, change governance, bypass source or
promotion gates, weaken validation, or create work for its own sake. Prefer a
task proposal when the fix is repository work, a research/source proposal when
the fix is scientific intake, and a lightweight issue/comment when ownership is
unclear or repository edits are not safe.

A structural-bottleneck proposal should include:

- problem;
- repeated evidence, with task, PR, validation, or campaign references;
- affected workflows, helpers, or campaigns;
- proposed process or helper change;
- risks and non-goals;
- maintainer decision needed.

Default rule:

- create a proposal under `tasks/proposals/`
- let the maintainer accept it before assigning `TASK-XXXX`

Proposal file format:

`tasks/proposals/YYYYMMDD-<contributor-id>-<short-slug>.yaml`

Proposal branch format:

`agent/<contributor-id>/<agent-id>/propose-task-<short-slug>`

Proposal PR title format:

`TASK-PROPOSAL: <short title>`

Default proposal PR scope:

- one or more `tasks/proposals/*.yaml` files in a proposal-only PR

Use a multi-proposal PR when the ideas are tightly coupled, come from the same
salvage pass, or when the maintainer explicitly asks for a batch. Split the
PR when the proposals are unrelated or the batch stops being lightweight.

Use [./task-proposal-protocol.md](./task-proposal-protocol.md) and
[../tasks/proposals/TASK-PROPOSAL-TEMPLATE.yaml](../tasks/proposals/TASK-PROPOSAL-TEMPLATE.yaml).

Only the maintainer may assign canonical ids directly unless a maintainer-run
task-admin or review agent is explicitly told to do so.

When the maintainer explicitly asks an agent to create canonical `TASK-XXXX`
files for future work, use the `TASK-QUEUE` lane instead of creating a separate
"task to create tasks." The newly queued executable tasks should usually remain
`READY`, `BLOCKED`, or `PROPOSED`; they are not treated as completed by the
queue PR.

Task-queue branch format:

`agent/<contributor-id>/<agent-id>/task-queue-<short-slug>`

Task-queue PR title format:

`TASK-QUEUE: <short summary>`

Task-queue PR scope:

- new or updated canonical `tasks/TASK-XXXX-*.yaml` files;
- synced generated task navigation (`docs/task-views/*.md`);
- optional protocol or planning docs needed to explain the queue.

Do not use `TASK-QUEUE` for normal contributor ideas without maintainer
approval; those still go through `TASK-PROPOSAL`. Do not use `TASK-QUEUE` to
implement the newly queued task's accepted outputs in the same PR.

If rescuing useful ideas from a stale or superseded PR:

- create fresh proposal file(s) under `tasks/proposals/`;
- start from a clean `propose-task-...` branch immediately;
- do not reuse a generic docs/task branch just because it already exists;
- open a clean replacement `TASK-PROPOSAL` PR and then close the stale PR;
- a salvage batch is allowed when the rescued ideas are closely related and
  the replacement PR stays proposal-only.

## Scientific Microtask Queues

Default execution still starts from canonical `TASK-XXXX` items.

Exception:

- when a maintainer explicitly asks for spare token or time budget work;
- when the maintainer invokes agent scientific work mode;
- when a narrow campaign-facing contribution is better handled as a small queue
  item than as a brand-new canonical task.

In those cases, agents may work from `tasks/microtasks/*.yaml` and the rules in
[./scientific-micro-task-protocol.md](./scientific-micro-task-protocol.md).

Microtask rules:

- before selecting queue work, run
  `python3 scripts/apl_microtask_pr_helper.py status --queue-id <queue-id>` and
  pick from the effective `available` list, not from queue YAML alone;
- prefer one campaign queue at a time;
- one PR may complete a small batch of related microtasks from the same
  campaign;
- do not mix many campaigns in one microtask PR unless the maintainer asks;
- do not create many new canonical `TASK-XXXX` files just to represent tiny
  queue items;
- do not promote claims from microtask outputs;
- report limitations for every completed item;
- if uncertain, mark the output `REVIEW_NEEDED`.

Microtask branch formats:

- single item:
  `agent/<contributor-id>/<agent-id>/microtask-<microtask-id>-<short-slug>`
- small same-queue batch:
  `agent/<contributor-id>/<agent-id>/microtask-batch-<queue-id>--<short-slug>`

Microtask PR title format:

`microtask(<queue-id>): <short description>`

Examples:
- `microtask(DAV-001): add DA-017 gravitational acceleration to challenge set`
- `microtask(PFF-002): classify near-separatrix failure for gauntlet candidate`
- `microtask(PMR-001): audit electron mass dataset entry against PDG source`
- `microtask(dimensional-analysis-validator): add DAV-003 DAV-004 DAV-008 challenge entries`

Microtask PRs do not require a canonical `TASK-XXXX` file. They use the
`fast review` lane in `docs/maintainer-review-agent.md`.
Use the repository PR template, delete unused sections, and fill in the
microtask queue metadata instead of leaving canonical task placeholders in the
PR body.

Use [./agent-scientific-work-mode.md](./agent-scientific-work-mode.md) for the
practical operating pattern.

## PR Helper Map

APL has several PR shapes. Use the helper that matches the PR kind instead of
forcing every PR through the canonical task helper.

| PR kind | Use this helper | Branch shape |
| --- | --- | --- |
| Canonical `TASK-XXXX` implementation | `python3 scripts/apl_task_pr_helper.py prepare-current ...` | `agent/<contributor-id>/<agent-id>/task-XXXX-<short-slug>` |
| Task proposal | `python3 scripts/apl_proposal_pr_helper.py scaffold/preflight/create ...` | `agent/<contributor-id>/<agent-id>/propose-task-<short-slug>` |
| Microtask | `python3 scripts/apl_microtask_pr_helper.py status/scaffold/preflight ...` | `agent/<contributor-id>/<agent-id>/microtask-...` |
| Task closeout | `python3 scripts/apl_closeout_pr_helper.py scaffold/preflight ...` | `agent/<contributor-id>/<agent-id>/closeout-<short-slug>` |
| Task queue | Use the repository PR template and canonical `TASK-QUEUE` branch/title rules; do not mark newly queued tasks `REVIEW_READY` or implement them in the same PR | `agent/<contributor-id>/<agent-id>/task-queue-<short-slug>` |

The helpers are mechanical guardrails, not scientific reviewers. They format and
preflight branches, titles, bodies, metadata, and obvious PR-shape mistakes.
They do not decide whether a scientific result is true, whether a task should be
accepted, or whether a PR should merge.

For closeout behavior, task YAML may optionally set `closeout: auto` or
`closeout: review`. Omitted is equivalent to `auto`; `review` opts the task out
of safe auto-closeout and keeps it on the manual maintainer closeout path.
`TASK-CLOSEOUT` is separate: it is the PR kind marker for closeout PR titles and
metadata, not a task id and not a value for the task YAML field.

## Canonical Task PR Helper

Before opening a canonical task PR, prefer the Python helper over ad-hoc
`gh pr create` commands. The helper is cross-platform and catches the common
publication mistakes before GitHub review: wrong branch shape, mismatched task
id, missing PR template sections, missing metadata, and missing strict
validation mention.

After committing task work on the canonical task branch, run:

```bash
python3 scripts/apl_task_pr_helper.py prepare-current \
  --task-id TASK-XXXX \
  --contributor-id <contributor-id> \
  --github-username <github-username> \
  --agent-id <codex|claude|other-agent-id> \
  --human-reviewer <maintainer-github-username> \
  --summary "What changed, in narrow verification-first terms." \
  --body-file .apl-pr-body.md
```

`.apl-pr-body.md` is ignored local helper state and must not be committed.
Regenerate it whenever the PR body needs an update.

By default, `prepare-current` compares the current branch against `origin/main`
when that remote-tracking ref exists, then `upstream/main` if available, and
finally local `main`. Pass `--base <ref>` when a maintainer explicitly wants a
different base.

If `prepare-current` reports errors, fix them before creating the PR. In
particular, do not open a PR from a `feature/...` or other non-canonical branch
for canonical task work, and do not open a PR when commits ahead of the base
branch fail the required commit-message format. Use the printed expected branch
as the branch target.

Then create the draft PR using the helper-generated body:

```bash
python3 scripts/apl_task_pr_helper.py create \
  --branch agent/<contributor-id>/<agent-id>/task-XXXX-<short-slug> \
  --title "TASK-XXXX: <task title>" \
  --body-file .apl-pr-body.md
```

The older `scaffold`, `preflight`, `create`, and `ready` subcommands remain
available. `prepare-current` is the recommended final pre-publication check
because it uses the actual current branch and current diff.

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
- `SUPERSEDED`: the task was valid when created, but a newer task,
  architecture, or reviewed workflow replaced it. Do not execute it; follow the
  replacement task or create a fresh scoped task if the old idea becomes useful
  again.
- `REJECTED`: the task should not proceed in its current form.

Rules:

- An agent may move `READY -> IN_PROGRESS`.
- An agent may move `IN_PROGRESS -> REVIEW_READY`.
- A task PR may update its own `tasks/TASK-XXXX-*.yaml` lifecycle status and
  synchronize generated task navigation when that status changes.
- Do not change unrelated task statuses or generated task navigation except
  when the maintainer explicitly requested queue triage, closeout, unblock, or
  stale-task cleanup.
- Only a maintainer should move `REVIEW_READY -> DONE`.
- A maintainer may use a maintainer-run review agent to assist review and
  closeout, but the agent output is advisory rather than autonomous.
- If blocked, set `BLOCKED` and explain why in the task file, board, or PR.
- If old work is replaced by a better lane, set `SUPERSEDED` rather than
  leaving it in `BLOCKED` or marking it `REJECTED`.
- `PROPOSED` may still appear in backlog planning, but it is not an executable
  task state for active task execution.

## Branch Naming

Use exactly this format:

`agent/<contributor-id>/<agent-id>/task-<task-number>-<short-slug>`

Examples:

- `agent/gladunrv/codex/task-0011-numerical-audit`
- `agent/romanhladun24-dot/claude/task-0017-dimensional-challenge`
- `agent/ihor-github/human/task-0032-public-result-package`

Field meanings:

- `contributor-id`: SHOULD be the lowercased GitHub username for the human
  responsible for the PR and review loop when one is available; otherwise use a
  stable maintainer-approved short id.
- `agent-id`: the execution mode or tool, such as `codex`, `claude`,
  `cursor`, `human`, or `other`.

Contributor-id source of truth:

- Prefer the authenticated local GitHub identity (`gh auth status` or
  `gh api user --jq .login`) when it is available.
- If GitHub auth is unavailable, use local Git configuration only as a clue
  (`git config user.email` / `git config user.name`) and prefer a previously
  maintainer-confirmed contributor id for that checkout.
- Do not infer the current contributor id from unrelated open PR authors,
  branch history, or task examples. If the local identity signals conflict or
  only indirect clues exist, ask the maintainer before creating the branch.

Rules:

- lowercase only
- no spaces
- no underscores
- include the task number
- keep the slug short
- keep `github-username` as separate PR metadata even when it matches
  `contributor-id`
- do not invent fantasy agent identities as the canonical id

Historical note:

- older private-pilot branches may still use `agent/<agent-id>/...`
- older branches and examples may use short contributor ids such as `roman`
- do not rename old branches or rewrite history just to match the new format

For task proposals, use:

`agent/<contributor-id>/<agent-id>/propose-task-<short-slug>`

## Branch-First Rule

Before making any repository change for a task:

1. confirm the current task is `READY`;
2. create the task branch using the canonical naming format;
3. switch to that branch;
4. only then edit files, run task-related generators, or stage changes.

Agents must not implement task work on `main`.

If an agent notices that work started on `main` by mistake, it should stop and
move the current worktree state onto a correctly named task branch before
continuing.

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

Run `python3 scripts/apl_task_pr_helper.py prepare-current ...` after committing
and before `gh pr create`; it checks the commits ahead of the base branch and
fails if any subject does not follow this task-scoped format.

## Commit Permission

Agents may commit only when explicitly instructed.

For this repository, maintainer wording such as "prepare a PR", "run the task
through PR", "execute the selected task autonomously", or "full task lifecycle"
counts as explicit current-turn approval to commit on the selected task branch,
push that branch, and open a draft PR. This approval does not allow pushing
`main`, force-pushing, merging, tagging, or touching unrelated branches.

A commit means the agent believes the task is ready for maintainer review.

After committing, the task status should be `REVIEW_READY`, not `DONE`.

`DONE` is set only by the maintainer after review and merge.

## Pull Request Title Format

Use exactly this format:

`TASK-0011: Audit numerical precision vs model residual`

The PR must stay within one task scope and make the linked task easy to review.

For task proposals, use:

`TASK-PROPOSAL: <short title>`

## Open a Pull Request

"Open a PR" means creating the GitHub pull request and returning its URL when
the agent has GitHub access. It does not mean only preparing a branch, commit,
title, body, or pushed branch. When a full PR lifecycle was requested, the
final response must include either a PR URL or exact maintainer-run commands to
publish the prepared branch and PR from a local console.

Before starting implementation for a full PR lifecycle request, optionally
check whether the environment can open a PR:

```bash
python3 scripts/apl_pr_capability_check.py
```

This check is advisory. It must never be used as a pre-edit gate. Missing
`gh`, missing GitHub auth, restricted network access, or a sandbox that cannot
push should not block local task execution or cause the agent to ask the user
whether to continue before implementation. Create the task branch first, do
the local work, run validation, and commit only after the intended files are
ready for maintainer review.

At the end, the agent should try to publish through the best available
agent-driven path before falling back to manual commands:

1. Use repository helpers such as `scripts/apl_task_pr_helper.py` where
   possible.
2. Use an available GitHub/MCP connector or GitHub CLI when configured.
3. If `git commit`, `git push`, `gh pr create`, `gh pr edit`, `gh pr view`,
   `gh pr ready`, or `python3 scripts/apl_review_pr.py` is blocked by sandbox
   permissions or missing command approval, request the needed permission or
   escalation for that specific command.
4. Provide manual maintainer-run commands only after the available tool path
   and any appropriate permission request cannot complete the publication.

Fallback commands to give the maintainer when direct publication is not
available:

```bash
git push origin agent/<contributor-id>/<agent-id>/task-XXXX-<short-slug>
gh pr create --draft --base main --head agent/<contributor-id>/<agent-id>/task-XXXX-<short-slug> --title "TASK-XXXX: <short title>" --body-file /path/to/apl-pr-body.md
python3 scripts/apl_review_pr.py --pr <number>
gh pr ready <number>
```

The agent should also offer to help the maintainer set up access, for example
by suggesting `gh auth login` or a `GH_TOKEN`/`GITHUB_TOKEN`, but setup is not
required for completing local validation work.

If Python, Git, GitHub CLI, proxy settings, or Windows shell startup look
inconsistent, run the read-only agent doctor before adding local workaround
steps:

```bash
python3 scripts/apl_agent_doctor.py
python3 scripts/apl_agent_doctor.py --worktree-runtime-preflight --no-gh-auth-check
```

The doctor reports environment diagnostics only. It does not install packages,
mutate global `PATH`, store credentials, relax validation, or replace the task
protocol. The worktree-runtime preflight prints the selected validation Python
and deterministic discovery order: active repository `.venv`, checkout `.venv`,
main-checkout `.venv` for git worktrees, then active-interpreter fallback. Use
it to identify the next safe troubleshooting step, then continue with the
standard PR helper flow.

Use the repository PR helpers instead of calling bare `gh` in Codex sessions.
Codex may omit Homebrew paths from `PATH`; the helpers search common GitHub CLI
locations such as `/opt/homebrew/bin/gh` and `/usr/local/bin/gh`.

Task PRs should start as drafts while validation, CI, and PR-number review are
still in progress. After GitHub CI is green and
`python3 scripts/apl_review_pr.py --pr <number>` returns `MERGE_OK`, mark the
PR ready for review. If the agent cannot update GitHub directly, provide the
maintainer with `gh pr ready <number>`. Keep the PR as draft if any validation,
CI, or review blocker remains.

After implementation and validation:

1. push the task branch only when a human or workflow expects a PR;
2. open one PR for one task branch;
3. use the required PR title format;
4. complete the repository PR template before creating the PR;
5. include limitations, validation results, and artifact-impact notes;
6. move the task to `REVIEW_READY`.

Do not open task PRs with a short ad hoc `--body` such as only `Summary` and
`Validation`. Prepare a body file from `.github/pull_request_template.md`, fill
the required sections, and use that body file when creating the PR:

```bash
python3 scripts/apl_task_pr_helper.py scaffold \
  --task-id TASK-XXXX \
  --contributor-id <contributor-id> \
  --github-username <github-username> \
  --agent-id <agent-id> \
  --human-reviewer <reviewer> \
  --slug <short-slug> \
  --description "<short title>" \
  --summary "<verification-first summary>" \
  --body-file /tmp/apl-pr-body.md
python3 scripts/apl_task_pr_helper.py preflight \
  --branch "agent/<contributor-id>/<agent-id>/task-XXXX-<short-slug>" \
  --title "TASK-XXXX: <short title>" \
  --body-file /tmp/apl-pr-body.md
python3 scripts/apl_task_pr_helper.py create \
  --branch "agent/<contributor-id>/<agent-id>/task-XXXX-<short-slug>" \
  --title "TASK-XXXX: <short title>" \
  --body-file /tmp/apl-pr-body.md
```

After the PR exists, run the PR-number review, not only branch preflight:

```bash
python3 scripts/apl_review_pr.py --pr <number>
```

After CI is green and the PR-number review returns `MERGE_OK`, mark the draft
ready:

```bash
python3 scripts/apl_task_pr_helper.py ready --pr <number>
```

For the bounded finish step, agents may use the repository finish gate helper
instead of repeating the review, CI, and ready commands by hand:

```bash
python3 scripts/apl_pr_finish_gate.py --pr <number>
```

The helper first runs `python3 scripts/apl_review_pr.py --pr <number>`, then
checks GitHub PR checks through `gh pr checks --json`, and only then calls
`gh pr ready <number>`. It leaves the PR draft if the review verdict is not
`MERGE_OK`, if checks are pending or failing, or if GitHub status cannot be
loaded. For a non-mutating preflight, use:

```bash
python3 scripts/apl_pr_finish_gate.py --pr <number> --dry-run
```

When `scripts/apl_agent_doctor.py` reports the known loopback blocker proxy
(`127.0.0.1:9` or `localhost:9`) and network access is allowed, add
`--ignore-suspicious-proxy` to `apl_task_pr_helper.py create` or `ready`.
The flag is opt-in, applies only to the child `gh` command, and does not remove
legitimate proxy configuration or mutate the parent shell.

## Pull Request Requirements

Every PR should include:

- Task ID
- task file path
- branch name
- contributor id
- GitHub username
- agent tool
- model/version if known
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
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
git diff --exit-code
```

Use `--output-dir` for routine example runs so committed canonical artifacts do
not change accidentally.

`python3 -m pytest` runs in parallel by default via `pytest-xdist` (part of the
dev extras: `pip install -e ".[dev]"`), matching CI on Windows, macOS, and
Linux. For a faster cross-platform inner loop use
`python3 scripts/validate_fast.py` (lint, strict repository validation, then
non-`full_repo` tests with a slowest-ten timing report). Add
`-n0` to force a serial run when debugging a single test. For a narrow task
PR, start with the validation commands declared in its task YAML and use
`python3 scripts/apl_task_validation_plan.py --task TASK-XXXX` for advisory
diff-aware guidance. If a Windows sandbox blocks parallel pytest, run
`python3 scripts/apl_agent_doctor.py --probe-pytest-runtime --no-gh-auth-check`.
Do not automatically replace a narrow PR's validation with a serial full-suite
run: use targeted `-n0` debugging and let CI provide broad cross-platform
coverage.

Treat test priority as a staged-lane concern. Run cheap deterministic gates
before the parallel pytest layer and keep slow `full_repo` smoke tests at the
end. Do not introduce dependencies between individual tests merely to control
their xdist scheduling order. Put tests with measured xdist resource or path
sensitivity in the same `xdist_group`, which keeps them on one worker while
unrelated tests continue in parallel.

Do not freeze the current task board, mission output, task-id set, or public
status text inside tests. Tests that cover registry, mission, status, or
generated-board behavior should build small fixture repositories or derive
expectations from the committed source of truth at runtime, so routine task
completion, unblock, or board sync changes do not break unrelated tests.

Before opening a PR, agents may optionally generate a review bundle for the
maintainer. This is no longer a required step and its absence is not flagged by
the PR preflight:

```bash
python3 scripts/apl_review_bundle.py
```

This produces `_snapshots/review_<branch>_<timestamp>.md` with the full diff
vs `main`, commit list, and changed-file summary.

For microtask PRs, contributors and their agents may also use
`python3 scripts/apl_microtask_pr_helper.py` to scaffold canonical branch/title
metadata and run a local preflight check before maintainer review.

For canonical task PRs, use `python3 scripts/apl_task_pr_helper.py` to scaffold
and preflight the template-based PR body before creating the draft PR.

For task proposal PRs, the lighter validation path from
[./task-proposal-protocol.md](./task-proposal-protocol.md) is acceptable.

When a task creates concrete artifact paths, replace any placeholder validation
commands in that task's YAML before moving the task to `REVIEW_READY`.
Examples include replacing `<new-result-path>` with the exact
`results/EXP-XXXX/RUN-XXXX/result.yaml` path or replacing `<queue-id>` with the
specific queue id used by the PR. Placeholders may remain only in task
templates, future `READY` tasks, or proposal files that are not being handed off
as completed work.

## Result Artifact Policy

When a task is set to `DONE`, strict scientific-memory validation expects it to
link a scientific result (`results/.../result.yaml`) or a registered `PRED-*`
artifact. A task that produces neither will raise the `done_task_without_result`
warning at closeout (and `--fail-on-warnings` turns that into a failure).

There are two ways a non-result task satisfies this rule:

1. its `type` is on the no-result exemption list in
   `physics_lab/registry/scientific_memory_integrity.py`
   (`STRICT_DONE_TASK_TYPES_WITHOUT_RESULTS`) — for example `tooling_fix`,
   `documentation`, `repository_hardening`, `test_infrastructure`; or
2. it declares an explicit `result_artifact_policy`.

Prefer the **explicit policy** for tooling, docs, workflow, infrastructure,
audit, and planning tasks whose `type` is not already exempt. Do not broaden the
exemption list to dodge the check — a blanket type exemption silently weakens the
control, while an explicit policy is an auditable per-task decision:

```yaml
result_artifact_policy:
  required: false
  reason: "Tooling/docs/workflow task; no scientific RESULT artifact is expected."
  evidence:
    - "path/to/the/code/or/doc/this/task/produced"
```

Add this block while the task is still `READY`/`IN_PROGRESS` — the closeout
report (`build_closeout_report`) now warns when a non-exempt task links no
result/`PRED` artifact and declares no policy, so the gap surfaces before `DONE`
rather than at closeout strict validation. Tasks that genuinely produce a result
need no policy block; keep `required: false` only for the no-result case.

## Cross-Platform Compatibility

APL must run on Linux, macOS, and Windows so third-party agents can contribute,
even though CI runs on Linux only. When a task touches code or tooling, keep it
portable:

- build paths with `pathlib.Path` / `os.path.join`, never hardcoded `/`;
- use `tempfile` for temporary paths, never hardcoded `/tmp`;
- use `Path.home()` (not `HOME`) and `sys.executable` (not literal `python3`);
- call subprocesses with an argument list and `shell=False`; avoid shell-only
  features;
- always pass `encoding="utf-8"` to file reads and writes;
- do not add a `.sh` script on the task-execution or review critical path
  without a cross-platform (Python) equivalent — and do not add a `.sh` script
  that is merely a thin wrapper around one or two commands.

See [./cross-platform-compatibility.md](./cross-platform-compatibility.md) for
the full standard and the audit of existing shell scripts.

## End-Of-Task Output Routing

At the end of any research, validation, benchmark, source-curation, prediction,
or claim-facing task, add a short output-routing summary before handoff. This
summary tells the maintainer what the task produced and where it belongs in
the scientific memory.

Use [./result-promotion-protocol.md](./result-promotion-protocol.md) as the
canonical routing rule. The summary should state:

- task verdict: `VALID`, `VALID_IN_RANGE`, `PARTIALLY_VALID`, `INCONCLUSIVE`,
  `OVERFITTED`, `FALSIFIED`, or `not_applicable`;
- canonical destination: sandbox-only `agent_runs/`, `results/`, `prediction_registry/`,
  `claims/`, `knowledge/`, source artifact, review note, or task proposal;
- review tier when applicable: `AGENT_PUBLISHED`, `AGENT_VALIDATED`,
  `MAINTAINER_REVIEWED`, `EXTERNAL_REPLICATED`, `LEGACY_UNTIERED`, or `none`;
- Gate status when applicable: Gate A pass/fail/not attempted, Gate B
  pass/fail/not attempted;
- claim impact: no claim change, new `DRAFT` claim only, evidence reference
  only, or maintainer-only status transition requested;
- knowledge impact: no knowledge change, task proposal only, or maintainer-only
  knowledge entry requested;
- limitations and blockers, especially missing tooling, source provenance, or
  validation gaps.

If the task produced only sandbox evidence, say so explicitly. Do not turn a
sandbox note into a prose claim. If Gate A or Gate B tooling is missing or
fails, report the publication as blocked instead of bypassing the gate with
unsupported wording.

Agents may create `AGENT_PUBLISHED` or `AGENT_VALIDATED` artifacts only when
the task scope and [./result-promotion-protocol.md](./result-promotion-protocol.md)
allow it. Claim status transitions remain maintainer-only in Phase 1. Do not
auto-merge PRs that publish tiered artifacts.

## Maintainer Review And Closeout

Maintainers may use [./maintainer-review-agent.md](./maintainer-review-agent.md)
for two explicit modes:

1. pre-merge review for an open PR;
2. post-merge closeout for moving a merged task to `DONE`.

The maintainer review agent may:

- verify PR metadata, scope, validation, accepted outputs, and review bundle
  integrity;
- surface repository-safety and security-sensitive changes for maintainer review;
- return `MERGE_OK`, `NEEDS_CHANGES`, or `BLOCKED`;
- help close a merged task by updating the task file and synchronizing
  generated task navigation
  ([./task-views/research.md](./task-views/research.md),
  [./task-views/support.md](./task-views/support.md), and
  [./task-views/release.md](./task-views/release.md)).

The maintainer review agent must not:

- merge PRs;
- promote claims automatically;
- rewrite scientific verdicts;
- rewrite result artifacts unless the task explicitly required it and the
  maintainer approved that scope.

## Task Execution Flow

1. Read the files listed above.
2. Confirm the task is `READY` and atomic.
3. Create and switch to the branch using the required naming format before any
   repository edits.
4. Set the task status to `IN_PROGRESS` in the task file.
5. Do not hand-edit the generated `docs/task-views/*.md` for routine task
   status transitions. Task YAML is the canonical source of truth; the views
   are a maintainer-synchronized snapshot regenerated automatically by the
   post-merge `Sync Active Board` GitHub Action after each merge to `main`.
6. Do not commit regenerated versions of `docs/task-views/*.md` from a task PR.
   They are generated from canonical task YAML files and the post-merge action
   keeps them in sync on `main`.
7. Agents may run `python3 -m physics_lab.cli sync-active-board .` locally
   for visual confirmation of how their task YAML change will render, but
   should **not** stage or commit the resulting regeneration on a task PR
   branch. `validate-repo --strict --fail-on-warnings` reports a stale
   `docs/task-views/*.md` as `INFO` (not `ERROR`) by
   default, so a non-regenerated branch passes strict validation. Set
   `APL_ENFORCE_BOARD_STALENESS=1` only when explicitly auditing the
   action's output. If strict validation ever reports generated board
   staleness as an error during a routine task PR, treat that as a validation
   configuration issue to report or fix, not as permission to commit generated
   navigation churn. If a local sync or validation comparison leaves generated
   board files dirty, do not stage them; remove those generated diffs before
   creating the review bundle.
8. Do not add committed static files whose primary consumer is another agent
   and whose content changes with ordinary task churn. For agent routing,
   queue filtering, campaign-lane mapping, conflict scans, or current-state
   summaries, prefer scripts/CLI output, snapshot sections, or CI artifacts.
   Commit generated output only when it is canonical source or explicit
   human-facing navigation with a defined regeneration owner. See
   [static-agent-facing-generated-index-postmortem.md](./reviews/static-agent-facing-generated-index-postmortem.md).
9. Make the smallest reproducible change that satisfies the task.
10. Run the required validation commands.
11. Set the task to `REVIEW_READY` when implementation and validation are
    done.
12. Leave clear maintainer review notes and limitations.

After merge, maintainer closeout may also:

13. set the task to `DONE`;
14. let the post-merge `Sync Active Board` GitHub Action regenerate
    the generated task views
    ([./task-views/research.md](./task-views/research.md),
    [./task-views/support.md](./task-views/support.md), and
    [./task-views/release.md](./task-views/release.md)). The action runs on
    every push to `main` that touches `tasks/**` or `missions/current.yaml`
    and pushes a `chore(board-sync): … [skip-board-sync]` commit only when a
    regeneration diff exists. Maintainers may still run
    `python3 -m physics_lab.cli sync-active-board .` by hand in a dedicated
    board-sync PR when the action is disabled or needs a manual audit;
15. add a dry-run note when the merged PR belongs to a contributor pilot.

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
- do not begin task implementation before creating and switching to a task branch
- do not invent local branch, commit, or PR formats
- do not mark your own task `DONE`
- do not use a review agent to bypass maintainer merge or claim-review authority
- do not start unrelated tasks in the same branch or PR
- do not add dashboard, web API, database, ingestion, or runtime infrastructure work
- do not make the repository public
- do not promote claims or knowledge without review
- do not silently rewrite canonical scientific artifacts
- do not introduce platform-specific code (bash-only critical-path scripts,
  hardcoded `/tmp`, hardcoded `python3`, hardcoded `/` paths, or `HOME` reads)
  without a cross-platform equivalent; see
  [./cross-platform-compatibility.md](./cross-platform-compatibility.md)

## Standard Prompt

Use this prompt when assigning work to an agent:

```text
Execute TASK-0011 according to AGENTS.md and docs/agent-task-protocol.md.
Use contributor id: roman.
Use agent id: codex.
Create the task branch before making any repository changes.
Do not start any other task.
```
