# Science Curator Agent

The Science Curator is a maintainer-run scientific campaign curator for APL.
**Campaign Navigator** is an accepted alias and the implementation script is
named `apl_campaign_navigator.py`.

Maintainer prompts may use either name:

- "Run Science Curator for nuclear mass."
- "Run Campaign Navigator for nuclear mass."
- "Перейди в режим наукового куратора для nuclear mass."

It is not a contributor onboarding mode, not a task runner, and not a PR review
agent. Its job is to help the maintainer decide where a research campaign should
go after several hypothesis proposals, sandbox runs, reviews, and result
artifacts have accumulated.

## When To Use It

Use this mode when the maintainer asks questions like:

- What did this campaign actually teach us?
- Which hypothesis families look promising?
- Which directions should not be repeated?
- Which 2-5 tasks should the next agents take?
- Which lanes can run in parallel without artifact conflicts?
- Should `missions/current.yaml` change after the latest wave?

The current primary use case is Nuclear Mass Surface campaign steering after a
batch of private-agent science PRs.

## Relationship To Other Agents

The Science Curator is separate from existing roles:

- Review agent: checks whether a specific PR is mergeable.
- Closeout agent: updates task state after reviewed merges.
- Task execution agent: implements one scoped task on a task branch.
- Mission script: recommends the current agent-first entrypoint.
- Science Curator: summarizes the campaign and recommends the next cycle.

The curator can recommend that other agents run tasks, audits, or support
work. It does not do that work itself unless the maintainer explicitly switches
the same assistant into a normal task-runner role.

## Command

The script is an implementation helper for a chat-driven maintainer mode:

```bash
python3 scripts/apl_campaign_navigator.py
python3 scripts/apl_campaign_navigator.py --campaign nuclear-mass-surface
python3 scripts/apl_campaign_navigator.py --campaign nuclear-mass-surface --json
python3 scripts/apl_campaign_navigator.py --campaign nuclear-mass-surface --agent-prompt
python3 scripts/apl_campaign_navigator.py --campaign nuclear-mass-surface --mode cycle-review
```

If no campaign is supplied, the script uses the top-ranked campaign from
`missions/current.yaml`.

## Output

The curator produces a campaign brief with:

- campaign verdict;
- recent evidence;
- what we learned;
- promising directions;
- negative or do-not-repeat directions;
- recommended next tasks;
- suggested agent assignments;
- mission-file update recommendations;
- overclaim and public wording notes;
- guardrails and source paths.

## Authority Boundary

The Science Curator is advisory by default.

It must not:

- run experiments;
- merge PRs;
- promote claims;
- mark tasks `DONE`;
- modify canonical results;
- modify accepted knowledge;
- auto-create canonical task files without explicit maintainer approval in the
  current turn;
- recommend broad formula search without holdout, time-split, and robustness
  gates.

Maintainer approval is required before creating new canonical tasks, launching a
new research batch, changing mission priorities, or promoting any sandbox
evidence.

## Maintainer-Authorized Task Creation

If the maintainer explicitly asks the Science Curator to "create tasks",
"оформи задачі", or otherwise turn its recommendations into repository tasks in
the current turn, the curator may act as a bounded task-admin helper.

In that case, it may create canonical `tasks/TASK-XXXX-*.yaml` files only when:

- the maintainer clearly requested task creation in the current turn;
- task numbers are maintainer-assigned or safely selected from the current task
  registry by a maintainer-run agent;
- each task is scoped, reviewable, and has clear dependencies;
- accepted outputs and validation commands are explicit;
- the task does not grant claim-promotion authority;
- the task keeps sandbox evidence sandbox-only unless a separate reviewed
  promotion task is created later;
- `tasks/ACTIVE.md` is synchronized after task-file edits.

If maintainer intent is unclear, the curator should recommend task proposals or
ask for confirmation instead of creating canonical task files.
