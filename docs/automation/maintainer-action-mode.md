# Maintainer Action Mode

Use this file for policy-limited maintainer automation runs that should
perform a bounded action instead of only returning a report.

This mode exists because periodic automation that only recommends actions will
eventually stall. Action mode lets the automation move low-risk maintainer work
forward while still stopping before scientific or governance-sensitive
decisions.

For the first rollout, this mode should be used primarily for closeout
automation.

## Purpose

Perform limited, auditable maintainer actions when repository state is clear
enough that the action can be justified by deterministic checks and an explicit
instruction file.

## Core Rule

Action mode may act only within a pre-declared allowlist.

If the action is not explicitly listed as allowed, the automation must stop
and return a recommendation instead.

## First Enabled Action

The first enabled action for APL should be:

1. identify merged tasks that are verified and still not `DONE`
2. prepare and open a closeout PR
3. run the maintainer review agent on that closeout PR
4. if review is `MERGE_OK`, CI is green, the PR is pure closeout bookkeeping,
   and the maintainer already authorized closeout/merge in the current request
   chain, merge the closeout PR
5. otherwise ask the explicit next-step question:
   `Merge closeout PR #<number>?`
6. stop unless the maintainer explicitly authorizes merge

This gives the maintainer a real routine reduction benefit without handing
merge authority to automation.

## Good Fits For Action Mode

- post an English maintainer comment that was generated from a deterministic
  review result
- close a PR as superseded when a clean replacement PR already exists
- push a maintainer branch that contains only maintainer-workflow or
  documentation changes
- open a closeout PR for tasks already verified as merged and complete
- open a clean replacement PR for a contaminated or stale maintainer branch

## Not Allowed

- merge PRs automatically
- approve PRs on behalf of the maintainer
- promote claims automatically
- rewrite scientific verdicts
- rewrite canonical result artifacts
- make the repository public
- infer new governance policy without a file-backed instruction

## Inputs

- the specific action request or periodic action policy
- relevant PR numbers or task ids
- current `main`
- review helper output
- closeout helper output
- task YAML files
- GitHub CI state when relevant

## Required Preconditions

Before taking an action, verify all of these:

1. The action is explicitly allowed by the calling routine or policy.
2. The repository state needed for that action is deterministic and current.
3. The action does not modify claims, verdict scope, or result artifacts unless
   a maintainer explicitly authorized that exact action.
4. The action has a clear rollback or replacement story if it fails.

## Allowed Action Categories

### 1. PR Comment Posting

Allowed when:

- a review result already exists;
- the comment is operational, not scientific-governance redefining;
- the comment matches the reviewed state;
- the policy explicitly says comments may be posted.

### 2. Superseded PR Closure

Allowed when:

- the old PR is clearly replaced by a new clean PR;
- the replacement PR is linked;
- the closure reason is factual and non-ambiguous.

### 3. Closeout Preparation

Allowed when:

- the task PR is merged;
- accepted outputs are confirmed in `main`;
- task-to-PR binding is confirmed through GitHub metadata rather than merge
  commit text alone;
- closeout helper checks pass;
- no unresolved blocker remains.

Action mode may prepare and open the closeout PR and then run the maintainer
review agent on that PR. It should not silently mark a task `DONE` on `main`
outside the normal PR flow.

After a closeout PR receives `MERGE_OK` and GitHub CI is green, action mode
should be proactive rather than passive. If the maintainer already said to
close out, merge, or finish the closeout flow in the current request chain, and
the PR is pure closeout bookkeeping, merge it without asking again. If that
authorization is absent, ambiguous, or the PR includes non-closeout changes,
ask a clear yes/no merge question, for example `Closeout PR #274 is MERGE_OK
and CI green. Merge it now?`

A closeout PR is pure closeout bookkeeping only when it changes task status,
`tasks/ACTIVE.md`, generated context/snapshot files, closeout notes, or
closeout-agent instructions. Do not auto-merge when the PR changes claims,
results, experiments, hypotheses, scientific verdicts, public-release state, or
other protected artifacts unless the maintainer explicitly authorizes that exact
merge after review.

If GitHub PR metadata cannot be loaded or the PR title / head branch does not
bind back to the same canonical `TASK-XXXX`, action mode must stop and return
the candidate as blocked or needs-attention.

### 4. Maintainer-Admin PR Preparation

Allowed when:

- the change is a low-risk maintainer workflow or documentation change;
- the action is policy-backed;
- the branch is clean and scoped;
- deterministic validation has already passed.

## Output Contract

Action mode should always record:

- `Action`: what was done
- `Target`: PR number, branch, or task id
- `Why allowed`: the policy condition that authorized the action
- `Checks used`: review helper, closeout helper, validation, CI state
- `Review result`: the maintainer review verdict if a review run followed the action
- `Merge action`: whether the PR was merged under existing maintainer
  authorization or the explicit yes/no question asked when extra authorization
  was still needed
- `Follow-up`: what still needs a human or later routine

## Recommended Prompt Shape

```text
Run the maintainer automation agent in action mode.
Allowed action: <prepare closeout PR and review it | comment | close superseded PR | prepare clean replacement PR>.
Target: <PR number | TASK-XXXX>.
Use repository docs and deterministic helpers.
Act only if the action is explicitly allowed by policy and the state is unambiguous.
Otherwise stop and return a recommendation.
```

## Escalation Rules

Stop immediately and return a recommendation when:

- scientific scope is ambiguous;
- the action would touch claims or result artifacts;
- GitHub CI and local validation disagree;
- GitHub PR metadata cannot be verified for a closeout candidate;
- the branch is contaminated with unrelated work;
- the action depends on a proposal or task whose status is unclear;
- the action would effectively replace human merge or scientific authority.
