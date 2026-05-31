# Retrospective: the committed `campaigns/task-index.yaml` mistake (TASK-0510)

## What happened

TASK-0460 added a task-to-campaign lane index and **committed a generated
`campaigns/task-index.yaml`** to the tree as the agent-facing data source. This
re-created the exact failure mode that TASK-0470 had just retired with
`tasks/ACTIVE.md`: a frequently-changing generated file that lives in the
committed tree, goes stale between task PRs, and forces churn. It was caught and
reverted within hours by TASK-0509 (the committed cache was removed; the mapping
is now queried on demand). This note explains *why the decision was made* so the
lesson is encoded, not just the instance fixed.

## Decision chain (who proposed, accepted, executed, reviewed)

Git author is always the maintainer (merge author); the responsible **agent** is
identified by the PR branch.

| Step | Who | Where | What |
| --- | --- | --- | --- |
| Proposed | **codex** | `agent/roman/codex/task-queue-agent-capacity-followups`, PR #634 (TASK-QUEUE) | Drafted TASK-0460 with a requirement literally offering `campaigns/task-index.yaml` (a committed generated file) as an acceptable output. |
| Accepted | maintainer | merge of #634 | The TASK-QUEUE was accepted, baking the committed-file option into the canonical task spec. |
| Executed | **claude** | `agent/roman/claude/task-0460-task-campaign-index`, PR #703 | Chose the committed-file option and even wrote "regenerated on demand; not auto-synced" — *acknowledging* the staleness risk, then committing the file anyway. |
| Reviewed | maintainer + CI | merge of #703 | Passed: branch/title/scope/validation all green. Nothing flagged a new committed generated artifact for agent consumption. |
| Corrected | **codex** | `agent/roman/codex/task-0509-decouple-campaign-task-index`, PR #710 (TASK-0509) | Removed the committed cache; kept the on-demand script and pure helpers; updated docs to query on demand. |

## Root cause

The repository already knew the rule. TASK-0470's decision note
(`generated-task-navigation-architecture-decision.md`) states the root cause
plainly: *"the churn came from one root cause: generated state lives in the
committed tree."* But that finding was recorded as a **one-off decision about
`tasks/ACTIVE.md` and `docs/task-views/`**, not promoted to a **general,
discoverable principle** in the documents agents actually read before working
(`AGENTS.md`, `docs/agent-task-protocol.md`) or into the review checklist.

So the lesson did not generalize:

1. **Proposal gap** — the task spec author (codex) offered a committed generated
   file as an acceptable output, with no rule forbidding it.
2. **Execution gap** — the executor (claude) saw the staleness risk, rationalized
   it ("not auto-synced") instead of treating it as disqualifying, because no
   instruction said "do not commit a frequently-changing agent-facing generated
   file."
3. **Review gap** — no required check or helper signal exists for "new committed
   generated/cache file intended for agent consumption."

The instance fix (TASK-0509) addressed #2's output. This task (TASK-0510)
addresses the systemic cause: it promotes the lesson to a canonical principle in
agent instructions, the task protocol's forbidden actions, the architect role,
and the maintainer review required-checks list.

## Corrective principle (now canonical)

> **Generated, frequently-changing state must not be committed as an
> agent-facing data source.** Agents obtain current state by running the
> generator/script on demand, or by reading the canonical source files
> (`tasks/TASK-*.yaml`, `campaign_profiles/*.yaml`, `missions/current.yaml`).
>
> The only committed generated files are **human-facing** navigation that the
> post-merge `Sync Active Board` action auto-regenerates (`docs/task-views/*.md`);
> agents must not hand-maintain them or depend on their freshness.
>
> Do not introduce a new committed generated or cache file for agent
> consumption (cf. the retired `tasks/ACTIVE.md` and the removed
> `campaigns/task-index.yaml`). If a generated view is useful, expose it through
> a script that prints it on demand.

See: `docs/generated-file-policy.md` (canonical statement),
`docs/notes/generated-task-navigation-architecture-decision.md` (TASK-0470),
TASK-0509 (instance fix).

## Did instructions need changing? Yes

The mistake was not an isolated lapse — two different agents (codex proposing,
claude executing) and the review flow all passed it through, because the rule
existed only as a buried one-off decision. The fix is documentation/guardrail,
not blame: encode the principle where agents and reviewers will actually see it.
