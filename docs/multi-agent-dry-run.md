# Private Multi-Agent Dry Run

This note records the private contributor pilot behind [TASK-0012](/private/tmp/task-0030-finish/tasks/TASK-0012-private-multi-agent-dry-run.yaml:1)
and the first friend-contributor evidence required by
[TASK-0030](/private/tmp/task-0030-finish/tasks/TASK-0030-record-friend-contributor-dry-run.yaml:1).

It is repository memory for what actually happened during the pilot:
which tasks were used, which contributors and agent tools were involved,
what friction showed up, and what workflow lessons later shaped maintainer
automation and contributor docs.

## Run #1

- Date: `2026-05-02`
- Task: `TASK-0014`
- Task file: `tasks/TASK-0014-thought-experiment-consistency-suite-planning.yaml`
- Contributor: `roman`
- Agent: `claude`
- Agent branch: `agent/claude/task-0014-thought-experiment-plan`
- Pull request: [#6](https://github.com/gladunrv/autonomous-physics-lab/pull/6)
- PR title: `TASK-0014: Plan a thought-experiment consistency suite`
- CI result: merged before the current two-job CI layout; repository validation passed for the planning artifact
- Review result: maintainer review accepted planning-only scope
- Merge commit: `9835ac6`
- Scope: planning only, with no implementation or scientific claim promotion

### Outcome

- the planning PR landed cleanly in `main`;
- the repository gained a reusable thought-experiment planning artifact;
- the pilot showed that planning-only contributions can follow the full task branch and PR protocol without needing scientific implementation code.

### Friction points

- planning outputs still needed maintainer closeout to move from `REVIEW_READY` to `DONE`;
- CI and review details were split between repo memory and GitHub UI;
- early pilot branch naming still reflected older pre-standardization conventions.

### Lessons learned

- planning work benefits from explicit claim ceilings and scope wording;
- task files and PRs can safely carry non-implementation work as long as the contract is narrow;
- the dry-run log itself needs to be updated alongside closeout so workflow memory does not drift.

## Run #2

- Date: `2026-05-02`
- Task: `TASK-0033`
- Task file: `tasks/TASK-0033-standardize-contributor-agent-identity-format.yaml`
- Contributor: `roman`
- Agent: `codex`
- Agent branch: `agent/roman/codex/task-0033-standardize-contributor-agent-identity-format`
- Pull request: [#16](https://github.com/gladunrv/autonomous-physics-lab/pull/16)
- PR title: `TASK-0033: Standardize contributor-agent identity format`
- CI result: green for repository validation and test checks at merge time
- Review result: maintainer review accepted the workflow-only change set
- Merge commit: `40d0d7d`
- Scope: contributor workflow improvement only, with no scientific artifact or claim changes

### Outcome

- the repository now records both contributor identity and agent-tool identity in canonical branch and PR metadata rules;
- agent git permissions became explicit instead of relying on maintainer convention;
- later contributor PRs inherited a cleaner branch/metadata pattern.

### Friction points

- legacy private-pilot branch names remained in history and could not be normalized retroactively;
- protocol information was still spread across several docs, which made onboarding slower than necessary.

### Lessons learned

- scaling agent-assisted review requires tracking both the human owner and the tool used;
- explicit git guardrails reduce accidental policy violations;
- workflow-improvement tasks should also be recorded in scientific memory-style notes when they affect contributor throughput.

## Run #3 — First Friend Contributor

- Date: `2026-05-03` to `2026-05-04`
- Task: `TASK-0027`
- Task file: `tasks/TASK-0027-units-and-constants-reference.yaml`
- Contributor: `akutenyov`
- Agent: `claude`
- Agent branch: `agent/akutenyov/claude/task-0027-units-and-constants-reference`
- Pull request: [#24](https://github.com/gladunrv/autonomous-physics-lab/pull/24)
- PR title: `TASK-0027: Create units and physical constants reference`
- CI result: `Python tests (3.11)` and `Python tests (3.12)` both `SUCCESS`
- Review result: maintainer review accepted the reference-data contribution after several iterative fixes and merged it on `2026-05-04`
- Merge commit: `92faa6a`
- Scope: physics reference documentation and schema hygiene, with no scientific claims

### Artifacts reviewed

- `knowledge/reference/units-and-dimensions.md`
- `knowledge/reference/physical-constants.yaml`
- `physics_lab/schemas/knowledge.schema.json`
- `tests/test_pendulum.py`
- `tasks/TASK-0027-units-and-constants-reference.yaml`

### Outcome

- the repository gained a reusable reference layer for SI units, dimensions, and physical constants;
- the first friend-contributor PR completed the full task branch, CI, maintainer review, merge, and closeout path;
- this run satisfies the core evidence target for `TASK-0030`: a real invited-contributor PR recorded with contributor, agent, branch, PR link, CI result, review result, friction, and lessons learned.

### Friction points

- working without local Claude Code integration required manual file transfer and git operations, which increased iteration cost;
- schema and knowledge-file issues were caught late, leading to several repair commits and merge-conflict cleanup;
- `tasks/ACTIVE.md` and related board synchronization still created avoidable merge noise during the pilot period;
- contributor-side repair work occasionally drifted into repo-hygiene fixes, which made review history noisier than ideal.

### Lessons learned

- contributor-friendly tasks should avoid requiring broad schema interpretation on the first pass;
- a cleaner PR preflight path would have prevented several metadata and validation iterations;
- board synchronization and closeout automation were worth hardening after this pilot;
- new contributors benefit from narrow, visible tasks with strong deterministic validation.

## Pilot Summary

Three merged dry-run events were recorded across two contributors
(`roman` and `akutenyov`) and two agent tools (`codex` and `claude`).

### PR inventory

| Run | Task | Contributor | Agent | PR | Status |
|-----|------|-------------|-------|----|--------|
| #1 | TASK-0014 | roman | claude | [#6](https://github.com/gladunrv/autonomous-physics-lab/pull/6) | merged |
| #2 | TASK-0033 | roman | codex | [#16](https://github.com/gladunrv/autonomous-physics-lab/pull/16) | merged |
| #3 | TASK-0027 | akutenyov | claude | [#24](https://github.com/gladunrv/autonomous-physics-lab/pull/24) | merged |

### Workflow strengths observed

- branch-based task protocol cleanly separated contributor work;
- CI caught schema and validation issues before final merge;
- contributor and agent identity became unambiguous once the naming rules were standardized;
- maintainer review and later closeout automation could build on real pilot evidence instead of speculation.

### Workflow friction observed

- early pilot work lacked enough preflight guidance for contributors using chat-first agents;
- active-board synchronization created recurring conflict pressure before later workflow fixes landed;
- review and closeout memory drifted unless the repo note was explicitly updated after merge;
- contributors without a strong local tooling loop paid a higher iteration cost for validation and metadata mistakes.

## Follow-Through

The pilot directly motivated several later workflow improvements:

- contributor and agent identity standardization;
- active-board synchronization and closeout-conflict reduction;
- microtask PR templates, protocol clarification, and preflight helpers;
- an agent catalog and clearer maintainer automation entrypoints.

`TASK-0030` should be considered satisfied once this cleaned note is merged and
the task itself is moved through normal maintainer closeout.
