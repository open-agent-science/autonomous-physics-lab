# Static Agent-Facing Generated Index Postmortem

**Task:** `TASK-0510`  
**Incident surface:** `campaigns/task-index.yaml` from `TASK-0460`  
**Corrective merge:** `TASK-0509` / PR #710  
**Verdict:** `PROCESS_GUARDRAIL_NEEDED`

## Summary

`TASK-0460` introduced a useful capability: mapping active tasks to campaign
lanes, support lanes, parallel-safety hints, and accepted-output path
conflicts. The mistake was committing the rendered `campaigns/task-index.yaml`
as an agent-facing generated cache.

That file duplicated canonical `tasks/TASK-*.yaml` state, changed whenever the
active task pool changed, and created the same class of churn that APL had just
been removing from `tasks/ACTIVE.md`. `TASK-0509` fixed the architecture by
keeping the query helper and removing the committed cache.

## What Happened

1. PR #634 (`TASK-QUEUE: Add agent capacity follow-up tasks`) created
   `TASK-0460`.
2. The `TASK-0460` contract explicitly allowed a "generated or checkable"
   task-to-campaign index and named `campaigns/task-index.yaml` as an acceptable
   implementation option.
3. PR #703 implemented `TASK-0460` with:
   - `physics_lab/registry/task_campaign_index.py`;
   - `scripts/apl_task_campaign_index.py`;
   - committed `campaigns/task-index.yaml`;
   - `--write` and `--check` semantics that treated the generated file as a
     freshness artifact.
4. Review accepted the PR because the task contract authorized the generated
   artifact, validation passed, and the review focused on correctness of the
   implementation rather than whether the architecture reintroduced a
   high-churn agent-facing file.
5. Later PRs that added tasks had to refresh the generated index, confirming
   that it was becoming another board-like maintenance surface.
6. PR #710 (`TASK-0509`) removed `campaigns/task-index.yaml`, kept the dynamic
   lane query, and updated documentation to use the script output on demand.

## Who Proposed, Accepted, Implemented, And Reviewed

| Stage | Evidence | Agent / owner | Decision |
| --- | --- | --- | --- |
| Proposal / task queue | PR #634, commit `853fd2b` | Codex under maintainer-directed TASK-QUEUE flow | Created `TASK-0460` with ambiguous "generated or checkable" wording. |
| Maintainer acceptance | PR #634 merged by `gladunrv` | Maintainer assisted by review-agent | Accepted the task queue as useful capacity/coordination work. |
| Implementation | PR #703, branch `agent/roman/claude/task-0460-task-campaign-index` | Claude Code execution path; human owner `roman` | Implemented both useful query logic and committed static cache. |
| Review / merge | PR #703 merged by `gladunrv` after review-agent pass | Maintainer review workflow assisted by Codex/review-agent | Review did not challenge the architecture because the task allowed the artifact. |
| Correction | PR #710, `TASK-0509` | Codex under maintainer direction | Removed the committed cache and kept on-demand query behavior. |

This is a process/design issue, not an individual-agent failure. Each step
followed the instructions it had at the time; the instructions were missing the
right architectural distinction.

## Root Causes

1. **The task contract encoded the wrong option.**  
   `TASK-0460` explicitly allowed `campaigns/task-index.yaml`, so the executor
   could satisfy the task while still creating a bad coordination artifact.

2. **Review checked conformance more than architecture.**  
   The review-agent validated accepted outputs, tests, and safety boundaries,
   but did not ask whether a generated file was human-facing, agent-facing,
   stable, or high-churn.

3. **Instructions distinguished `docs/task-views/*.md`, but not the general
   category.**  
   APL had clear rules for generated task views and `tasks/ACTIVE.md`, but no
   generic rule saying "do not commit frequently changing agent-facing query
   output."

4. **One review checklist line was stale.**  
   `docs/maintainer-review-agent.md` still said task-queue PRs "should sync"
   `docs/task-views/*.md`, which conflicted with the newer post-merge sync
   architecture.

## Correct Rule

Generated outputs fall into three classes:

| Class | Commit? | Examples | Rule |
| --- | --- | --- | --- |
| Canonical source | Yes | `tasks/TASK-*.yaml`, `campaign_profiles/_catalog.yaml`, `missions/current.yaml` | Hand-authored or explicitly generated source of truth. |
| Human-facing stable navigation | Sometimes | `docs/task-views/*.md`, public status pages | May be committed only when a post-merge action or explicit human navigation contract owns it. |
| Agent-facing volatile query output | No | task lane index output, queue filters, conflict scans | Generate on demand via scripts/CLI/snapshot; do not commit as a static cache. |

Short version:

- Do not generate static files primarily for agents when the content changes
  frequently.
- Agents may read committed human-facing docs and may call scripts/CLI filters
  to get current state.
- Frequently changing agent context belongs in dynamic script output, snapshot
  sections, or CI artifacts, not in a committed board-like cache.

## Review Guardrail

Before approving any PR that adds a generated or checkable repository-state
file, review must ask:

1. Is this file canonical source, human-facing stable navigation, or
   agent-facing query output?
2. How often will it change relative to ordinary task PRs?
3. Who owns regeneration: humans, post-merge action, snapshot script, or nobody?
4. Can the same value be produced by a script/CLI query without committing the
   rendered output?
5. Does committing it create a second source of truth or review noise?

If the answer is "agent-facing, frequent, queryable," the PR should keep the
script and tests but avoid committing the rendered output.

## Current Correct State

After `TASK-0509`:

- `scripts/apl_task_campaign_index.py` remains available for current lane and
  conflict queries.
- `campaigns/task-index.yaml` is no longer committed.
- `tasks/TASK-*.yaml` remains the canonical task state.
- Snapshots and role-specific agents may call the script when they need current
  context.

## Follow-Up Recommendation

If future agents need additional routing views, implement them as:

- script output to stdout;
- snapshot sections generated at snapshot time;
- GitHub Action artifacts for one run;
- human-facing docs only when the maintainer explicitly wants a stable
  browseable page and defines the owning regeneration process.

Do not create another committed, frequently-changing, agent-facing cache unless
the maintainer explicitly accepts the churn and explains why a dynamic query is
insufficient.
