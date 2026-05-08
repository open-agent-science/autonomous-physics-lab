# Agent Catalog

This page is the shortest repository-native map of the agent roles, helper
flows, and maintainer automation surfaces that already exist in APL.

Use it when you want to answer:

- "Which agent should I use for this kind of work?"
- "Is this a real workflow we already support, or only a future idea?"
- "Where is the canonical documentation for this agent path?"

## Quick Split

APL currently has two broad families:

- contributor-facing task agents
- maintainer-facing review and automation agents

The contributor side helps humans and coding agents complete scoped work.
The maintainer side helps with review, queue triage, and post-merge closeout.

## Contributor-Facing Agent Paths

### 1. Canonical Task Execution Agent

Use this path when a contributor wants to pick one `READY` task and carry it
to `REVIEW_READY` on a normal task branch.

- Typical work: code, docs, workflow tasks, campaign packaging, validation
- Primary docs:
  - [AGENTS.md](../AGENTS.md)
  - [agent-task-protocol.md](./agent-task-protocol.md)
  - [agent-operating-model.md](./agent-operating-model.md)

Status: active and used routinely.

### 2. Task Proposal Agent

Use this path when no existing `READY` task fits and the contributor needs to
propose a new narrow task without guessing a canonical `TASK-XXXX` id.

- Typical work: proposal-only PRs under `tasks/proposals/`
- Primary docs:
  - [task-proposal-protocol.md](./task-proposal-protocol.md)
  - [agent-task-protocol.md](./agent-task-protocol.md)

Status: active and used routinely.

### 3. Scientific Microtask Agent

Use this path for one small queue item or a tiny same-queue batch from
`tasks/microtasks/`.

- Typical work: notes, dataset audits, challenge-set updates, small campaign
  support steps
- Primary docs:
  - [scientific-micro-task-protocol.md](./scientific-micro-task-protocol.md)
  - [agent-scientific-work-mode.md](./agent-scientific-work-mode.md)
  - [use-your-agent.md](./use-your-agent.md)

Status: active and used routinely.

### 4. New Contributor / Use-Your-Agent Path

Use this path when a human is new to the repository and wants a safe first
entrypoint before choosing a task or microtask.

- Typical work: onboarding, low-risk starter tasks, narrow contributor setup
- Primary docs:
  - [use-your-agent.md](./use-your-agent.md)
  - [agent-work-menu.md](./agent-work-menu.md)
  - [tasks/ACTIVE.md](../tasks/ACTIVE.md)

Status: active and recommended for new contributors.

## Maintainer-Facing Agent Paths

### 5. Maintainer Review And Closeout Agent

Use this path when the maintainer wants a structured PR review or post-merge
task closeout recommendation.

- Typical work: review open PRs, classify them, run closeout after merge
- Primary docs:
  - [maintainer-review-agent.md](./maintainer-review-agent.md)
  - [review-checklists/maintainer-pr-review-checklist.md](./review-checklists/maintainer-pr-review-checklist.md)
  - [review-checklists/task-closeout-checklist.md](./review-checklists/task-closeout-checklist.md)

Status: active and heavily used.

### 6. Maintainer Routine / Manual / Action Modes

These are execution modes for maintainer automation rather than separate
scientific agents.

- Routine mode: periodic queue sweep
- Manual mode: targeted maintainer request
- Action mode: bounded low-risk actions such as closeout PR preparation

Primary docs:
- [automation/maintainer-routine-mode.md](./automation/maintainer-routine-mode.md)
- [automation/maintainer-manual-mode.md](./automation/maintainer-manual-mode.md)
- [automation/maintainer-action-mode.md](./automation/maintainer-action-mode.md)

Status: active as file-backed operating modes.

### 7. Proposal Triage / PR Queue / Closeout Sweep Roles

These are documented maintainer automation roles used to organize routine work:

- proposal acceptance triage
- open PR queue triage
- task closeout sweep

Primary doc:
- [maintainer-automation-architecture.md](./maintainer-automation-architecture.md)

Status: real and documented, but best understood as automation roles layered
on top of the maintainer review system rather than completely separate product
surfaces.

## Planned Future Specialized Agents

The repository also names several future automation surfaces:

- code review sweep agent
- security sweep agent
- release readiness agent

Primary doc:
- [maintainer-automation-architecture.md](./maintainer-automation-architecture.md)

Status: planned, not the first thing a new contributor should rely on.

## Practical Reading Paths

### If you are a new human contributor

Read:

1. [use-your-agent.md](./use-your-agent.md)
2. [agent-task-protocol.md](./agent-task-protocol.md)
3. [tasks/ACTIVE.md](../tasks/ACTIVE.md)

### If you are a coding agent starting normal task work

Read:

1. [AGENTS.md](../AGENTS.md)
2. [agent-task-protocol.md](./agent-task-protocol.md)
3. [agent-operating-model.md](./agent-operating-model.md)
4. the selected `tasks/TASK-XXXX-*.yaml`

### If you are a maintainer reviewing PRs

Read:

1. [maintainer-review-agent.md](./maintainer-review-agent.md)
2. [maintainer-automation-architecture.md](./maintainer-automation-architecture.md)
3. the appropriate file in [automation/](./automation)

## One-Sentence Rule

If you are not sure which path applies:

- contributors start from `READY` tasks or microtasks
- maintainers start from the review agent and automation docs
- proposals are for ideas, not for active implementation
