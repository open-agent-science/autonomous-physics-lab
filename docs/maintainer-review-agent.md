# Maintainer Review Agent

This document defines a maintainer-run review and closeout protocol for
Autonomous Physics Lab.

The maintainer review agent helps the repository administrator review pull
requests, confirm task completeness, and close merged tasks without delegating
final authority away from the maintainer.

It is a review assistant, not an autonomous governance bot.

The intended maintainer workflow is prompt-first:

- the maintainer asks the agent to review a PR;
- the agent runs the deterministic review protocol under the hood;
- the agent returns a merge recommendation plus concrete blockers and fixes for
  the developer.

## Core Rules

- The maintainer review agent may recommend `APPROVE`, `NEEDS_CHANGES`, or
  `BLOCKED`.
- The maintainer review agent may help update task state after merge.
- The maintainer review agent must not merge pull requests.
- The maintainer review agent must not promote claims automatically.
- The maintainer review agent must not rewrite scientific verdicts.
- The maintainer review agent must not regenerate or rewrite result artifacts
  unless the task explicitly requires it and the maintainer approved that work.
- The maintainer review agent must not make the repository public.

Use this protocol together with:

- [./agent-task-protocol.md](./agent-task-protocol.md)
- [./maintainer-automation-architecture.md](./maintainer-automation-architecture.md)
- [./claim-promotion-policy.md](./claim-promotion-policy.md)
- [./review-checklists/maintainer-pr-review-checklist.md](./review-checklists/maintainer-pr-review-checklist.md)
- [./review-checklists/task-closeout-checklist.md](./review-checklists/task-closeout-checklist.md)

If this agent is executed by a periodic or reusable automation rather than by
an ad hoc prompt, also use:

- [./automation/maintainer-routine-mode.md](./automation/maintainer-routine-mode.md)
- [./automation/maintainer-manual-mode.md](./automation/maintainer-manual-mode.md)
- [./automation/maintainer-action-mode.md](./automation/maintainer-action-mode.md) when the automation is allowed to perform a bounded maintainer action

The recommended first bounded action is:

- open a closeout PR for verified merged tasks;
- run this review agent on that closeout PR;
- if the verdict is `MERGE_OK`, CI is green, the PR is pure closeout
  bookkeeping, and the maintainer already authorized closeout/merge in the
  current request chain, merge the closeout PR;
- otherwise explicitly ask: `Merge closeout PR #<number>?`;
- stop unless the maintainer authorizes merge or already authorized it in this
  request chain.

## Review To Closeout Flow

This diagram shows the maintainer-facing lifecycle from contributor PR review
through post-merge task closeout. The review helper can recommend and prepare
bounded updates, but the maintainer remains the merge and scientific-authority
decision point.

```mermaid
flowchart TD
    A["Contributor opens task PR\nTask status: REVIEW_READY"] --> B["Maintainer selects review lane\nfast review or deep review"]
    B --> C["Review helper checks\nbranch, title, metadata, scope, validation"]
    C --> D{Review verdict}
    D -->|"NEEDS_CHANGES or BLOCKED"| E["Contributor fixes blockers\nand updates the PR"]
    E --> C
    D -->|"MERGE_OK"| F["Maintainer reviews recommendation\nand decides whether to merge"]
    F -->|"Do not merge yet"| E
    F -->|"Merge PR"| G["Merged task remains REVIEW_READY\nuntil closeout"]
    G --> H["Post-merge closeout helper verifies\nmerged PR, outputs, CI, and blockers"]
    H --> I{Closeout ready?}
    I -->|"No"| J["Report blocker\nno task status promotion"]
    I -->|"Yes"| K["Maintainer closeout PR may set task DONE\nand optionally sync ACTIVE.md"]
    K --> L["Maintainer reviews and merges closeout PR"]
```

## Review Lanes

Maintainer review should not use the same heavy cycle for every PR shape.

Choose one of two lanes before running the review:

- `fast review`
  for low-risk docs, planning, task-admin, proposal-only, closeout PRs, and
  microtask PRs (`microtask(<queue-id>): ...`) that touch only challenge-set
  entries, notes, or dataset audit outputs
- `deep review`
  for engines, workflows, schemas, claims, results, maintainer scripts, CI,
  automation logic, and public-facing scientific wording

### Fast Review Lane

Use this lane when all of the following are true:

- the PR is limited to docs, notes, task files, proposal files, closeout
  updates, or maintainer-admin workflow text
- no claim, result artifact, hypothesis, or experiment semantics are being
  changed beyond already-approved task scope
- no engine, workflow, schema, maintainer script, or CI surface is touched
- there is no obvious overclaim or repository-safety risk

Fast review should focus on:

1. branch and title protocol
2. task/proposal status correctness
3. accepted outputs roughly matching the PR scope
4. validation presence
5. obvious wording or governance issues

If the PR passes those checks, avoid escalating into a full deep review loop.

### Deep Review Lane

Use this lane whenever any of the following is true:

- the PR changes executable engine or workflow code
- the PR changes schemas, maintainer scripts, CI, or automation helpers
- the PR introduces or modifies claim, result, hypothesis, or experiment
  artifacts
- the PR changes public-facing scientific wording that could affect scope,
  verdict interpretation, or overclaim risk
- the PR has ambiguous task-contract fit or protected-artifact scope

Deep review should include the full deterministic helper cycle and content
verification appropriate to the changed surface.

### Overclaim Severity

The deterministic review helper treats overclaim language as context-sensitive:

- positive claim phrasing is a blocker, especially in public-facing summaries,
  claims, results, reports, or review conclusions;
- guardrail, policy, checklist, or "do not use this wording" contexts should
  be surfaced as advisory warnings rather than blockers;
- advisory warnings are a signal for the maintainer or review AI agent to
  inspect the surrounding text and confirm the risky word is being used as a
  restriction, not as a scientific claim.

The review AI agent should not ignore advisory warnings. It should read nearby
context and report whether the wording is safe, ambiguous, or actually
claim-like.

## Mode 1: Pre-Merge Review

Use this mode for an open pull request before merge.

This mode supports:

- canonical task PRs
- task-queue PRs
- task proposal PRs

### Inputs

- PR link, PR description, or review bundle
- task id or `TASK-PROPOSAL`
- branch name
- task file path or proposal file path
- selected review lane (`fast` or `deep`) when helpful

### Required checks

1. Branch name follows one of:
   `agent/<contributor-id>/<agent-id>/task-<task-number>-<short-slug>`
   or
   `agent/<contributor-id>/<agent-id>/task-queue-<short-slug>`
   or
   `agent/<contributor-id>/<agent-id>/propose-task-<short-slug>`
   or
   `agent/<contributor-id>/<agent-id>/microtask-<microtask-id>-<short-slug>`
   or
   `agent/<contributor-id>/<agent-id>/microtask-batch-<queue-id>--<short-slug>`
2. PR title follows one of:
   `TASK-XXXX: ...`
   or
   `TASK-QUEUE: ...`
   or
   `TASK-PROPOSAL: ...`
   or
   `microtask(<queue-id>): ...`
3. PR metadata is filled in using the repository template, and the PR body
   includes the required top-level sections from
   `.github/pull_request_template.md`:
   `PR Kind`, `Primary Reference`, `Branch Name`, `Summary`, `Changed Files`,
   `Linked Repository Memory`, `Validation Commands`,
   `Scientific Claim Impact`, `Result Artifact Impact`,
   `Agent / Contributor Metadata`, and `Maintainer Review Notes`.
4. Canonical and proposal PRs: the referenced task or proposal file exists.
   Microtask PRs: no canonical task file required; queue id must match a file
   in `tasks/microtasks/`.
5. Canonical task PRs keep task status at `REVIEW_READY`; task-queue PRs
   create or update future canonical tasks that remain `PROPOSED`, `READY`, or
   `BLOCKED`; task proposal PRs keep proposal status at `PROPOSED`.
   Microtask PRs have no task-status requirement.
6. The changed files match the task or proposal scope and accepted outputs.
7. Validation commands are reported.
8. Accepted outputs are present or clearly explained when partial.
9. No claim is promoted without explicit maintainer review.
10. No result artifacts are changed unless the task explicitly requires it.
    Human task-contract wording such as "benchmark result artifacts" or
    "canonical run artifacts" counts when it clearly authorizes that scope.
11. No overclaim language is introduced.
12. Task proposal PRs do not guess canonical `TASK-XXXX` ids or edit canonical task files.
    Maintainer-directed task-queue PRs may create or update canonical task files,
    but must not treat those newly queued tasks as completed.
13. The review bundle was generated from the PR branch, not from `main`.
14. No obvious repository-safety or security risk is introduced without
    explicit maintainer awareness.
15. The selected review lane matches the actual PR surface.
16. Proposal PRs may contain multiple proposal files, but the batch should be
    intentional, coherent, and still clearly proposal-only.
17. Salvaged ideas from stale PRs should appear in a clean replacement
    `propose-task-...` PR rather than being patched onto a generic or
    mixed-context branch.
18. Task-queue PRs should sync `tasks/ACTIVE.md` and must not change canonical
    scientific artifacts such as claims, hypotheses, experiments, results, or
    knowledge.

Branch-only review is a preflight, not a final PR-body check. If the review was
run with `--branch`, run it again with `--pr <number>` after opening the PR so
the agent can inspect the actual GitHub title, branch, metadata, and template
sections before merge.

For microtask PRs, the metadata should name the queue file and queue id
explicitly, and batch PRs should keep the branch queue id aligned with the PR
title queue id. Reviewers should also check `microtask_runs/` for duplicate
claims, duplicate completed records, stale abandoned work, and oversized batches
that should be split before merge.

Before approving a microtask PR, reviewers should run or request the effective
availability helper:

```bash
python3 scripts/apl_microtask_pr_helper.py status --queue-id <queue-id>
```

If the PR repeats a completed non-repeatable item, return `NEEDS_CHANGES`.
Repeatable items are allowed only when the PR explains novelty, metrics, and why
the new attempt is not duplicating a previous run.

### Verdicts

- `MERGE_OK`: scope, validation, review metadata, and safety checks are
  adequate for merge.
- `NEEDS_CHANGES`: work is directionally correct, but gaps remain.
- `BLOCKED`: a protocol, validation, scope, or evidence issue prevents review
  completion.

Lane mismatch rule:

- if a PR was treated as `fast review` but touches deep-review surfaces, stop
  and switch to `deep review`
- if a PR stays entirely within fast-review surfaces, do not force a full
  deep-review loop unless a real blocker appears

### Recommended output format

- `Verdict: MERGE_OK | NEEDS_CHANGES | BLOCKED`
- `Risk: low | medium | high`
- `Task: TASK-XXXX`
- `Branch: ...`
- `Changed files: ...`
- `Validation: pass | fail | not_run`
- `Security risks: [...]`
- `Blockers: [...]`
- `Required fixes: [...]`
- `Recommended action: merge | wait | request changes`

Use `Security risks` to surface repository-safety concerns even when the PR is
otherwise reviewable. Examples:

- CI workflow or maintainer script changes;
- newly introduced unsafe execution patterns;
- suspicious artifact, claim, or dependency-surface edits.

## Mode 2: Post-Merge Closeout

Use this mode only after the maintainer has already merged the PR.

### Inputs

- merged PR number or merge reference
- task id
- `main` branch state after merge

### Required checks

1. The PR was merged.
2. The task accepted outputs exist in `main`.
3. The task was `REVIEW_READY` before closeout.
4. CI passed for the merged work.
5. No unresolved follow-up blockers remain.
6. If the merged work changes the recommended execution order, release-readiness
   story, or top near-term priorities, review
   [./next-steps.md](./next-steps.md) for stale guidance before ending the
   cleanup pass.
7. If the merged work changes experiments, results, campaign profiles,
   scientific validation surfaces, mission priorities, or public-release gates,
   compare [../README.md](../README.md), [./status.md](./status.md),
   [./mission-control.md](./mission-control.md), and
   [./next-steps.md](./next-steps.md) against authoritative
   `tasks/TASK-*.yaml`, `experiments/*.yaml`, `results/*/*/result.yaml`, and
   `agent_runs/` state. Public docs sync is a closeout signal by default, not
   an automatic rewrite: update stale public docs only when the current task
   explicitly asks for public-doc sync, otherwise update an existing docs-sync
   task or record a follow-up task.
8. During larger workflow-admin or closeout batches, check whether open
   `READY`, `REVIEW_READY`, or `BLOCKED` tasks still represent real claimable
   work rather than stale or already-merged drift.
9. After applying any closeout edits, do not leave the task status, active
   board, or generated context changes only in the local worktree. Review
   `git status`/`git diff`, run the required validation and context refresh,
   then prepare a closeout commit and PR or explicitly ask the maintainer to
   publish those changes. Do not push or merge without maintainer
   authorization.
   Prefer the closeout scaffold/preflight helper instead of a short ad hoc
   `gh pr create --body ...` flow:

   ```bash
   python3 scripts/apl_closeout_pr_helper.py scaffold \
     --task-id TASK-XXXX \
     --contributor-id <contributor-id> \
     --github-username <github-username> \
     --agent-id <agent-id> \
     --human-reviewer <human-reviewer> \
     --slug <closeout-slug> \
     --description "mark task done" \
     --include-active-board \
     --include-context
   ```

   To generate a body file directly for `gh pr create --body-file`, add
   `--body-only`:

   ```bash
   python3 scripts/apl_closeout_pr_helper.py scaffold \
     --task-id TASK-XXXX \
     --contributor-id <contributor-id> \
     --github-username <github-username> \
     --agent-id <agent-id> \
     --human-reviewer <human-reviewer> \
     --slug <closeout-slug> \
     --description "mark task done" \
     --include-active-board \
     --include-context \
     --body-only > /tmp/apl-closeout-pr-body.md
   ```

   Then run preflight before opening the PR:

   ```bash
   python3 scripts/apl_closeout_pr_helper.py preflight \
     --branch agent/<contributor-id>/<agent-id>/closeout-<closeout-slug> \
     --title "TASK-CLOSEOUT: <short title>" \
     --body-file /tmp/apl-closeout-pr-body.md
   ```
10. After the closeout PR is open and the review agent reports `MERGE_OK` with
    green CI, do not end with a passive status update. If the maintainer already
    authorized closeout/merge in the current request chain and the PR is pure
    closeout bookkeeping, merge it. Otherwise ask the maintainer a clear yes/no
    question: `Merge closeout PR #<number>?`

### Allowed actions

- set task status to `DONE`
- optionally run `python3 -m physics_lab.cli sync-active-board .` in a later
  dedicated board-sync step so generated task navigation
  ([../tasks/ACTIVE.md](../tasks/ACTIVE.md),
  [./task-views/research.md](./task-views/research.md),
  [./task-views/support.md](./task-views/support.md), and
  [./task-views/release.md](./task-views/release.md)) reflects current task
  statuses without becoming a conflict surface in every per-task closeout PR
- update [./next-steps.md](./next-steps.md) when the recorded immediate queue
  is stale after the merged work
- update [./status.md](./status.md) and
  [./mission-control.md](./mission-control.md) when authoritative experiment,
  result, campaign, or mission state changed
- update [../README.md](../README.md), [./status.md](./status.md),
  [./mission-control.md](./mission-control.md), or
  [./next-steps.md](./next-steps.md) only when the current task explicitly
  includes public-doc sync; otherwise add or update a follow-up task
- add a short closeout note when helpful
- add an entry to [./multi-agent-dry-run.md](./multi-agent-dry-run.md) when the
  merged PR is part of a dry run or contributor pilot
- flag stale open tasks for follow-up closeout, reopening, or curation when a
  cleanup pass reveals that the board no longer matches reality
- unblock directly dependent tasks by moving them from `BLOCKED` to `READY`
  when the merged task wave has satisfied their explicit prerequisites; the
  closeout PR title or body must say this is an unblock, and the unblocked task
  must remain reviewable work rather than a claim, result, or promotion
- close stale, superseded, or no-longer-relevant tasks by moving them to
  `REJECTED` when the maintainer has approved that cleanup; this is optional
  queue hygiene, not a required closeout step

Pure closeout bookkeeping means task status transitions, generated task
navigation (`tasks/ACTIVE.md` plus `docs/task-views/*.md`), generated
context/snapshot files, closeout notes, dependent-task unblocks, optional
stale-task closures, and closeout-agent instructions. Do not
auto-merge closeout PRs that touch claims, results, experiments, hypotheses,
scientific verdicts, public-release state, or other protected scientific
artifacts unless the maintainer explicitly authorizes that exact merge after
review.

### Not allowed

- merge pull requests
- delete branches
- promote claims
- rewrite result artifacts
- change scientific verdicts
- make the repository public

## Deterministic Helper

The agent may use the scripts below internally when following this protocol.
The maintainer does not need to remember the scripts if they prefer prompt-only
usage.

The helper is organized into explicit review layers:

- `review_git.py` collects local git and diff facts without deciding policy.
- `review_policy.py` parses branch and PR-title protocol lanes and exposes
  isolated policy helpers for task, proposal, closeout, and microtask reviews.
- `review_checks.py` evaluates content, protected-artifact, claim-promotion,
  overclaim, and repository-safety rules.
- `maintainer_review.py` orchestrates those layers and renders the final review
  or closeout report.

When adding new protocol rules, prefer extending the narrow layer that owns the
rule and adding regression coverage there before changing report orchestration.

### Pre-merge review helper

```bash
python3 scripts/apl_review_pr.py --pr 18
python3 scripts/apl_review_pr.py --pr <number> --task TASK-XXXX
python3 scripts/apl_review_pr.py --branch agent/<contributor-id>/<agent-id>/task-<task-number>-<short-slug> --task TASK-XXXX
```

### Post-merge closeout helper

```bash
python3 scripts/apl_closeout_task.py --task TASK-XXXX --pr <number>
python3 scripts/apl_closeout_task.py --task TASK-XXXX --pr <number> --apply
python3 scripts/apl_closeout_task.py --task TASK-XXXX --pr <number> --apply --sync-board
```

Default behavior:

- `--apply` updates the canonical task YAML to `DONE`
- `--sync-board` is optional and should usually be reserved for a dedicated or
  serialized board-sync step rather than every per-task closeout PR
- if the merged PR or the applied board-sync step touched `CONTEXT.md` source
  files, the helper should suggest rerunning
  `python3 scripts/generate_context_bundle.py` in a later maintainer branch
- if the merged PR touched scientific state or its task payload references
  experiment/result/campaign/mission changes, the helper should emit a public
  docs drift checklist for `README.md`, `docs/status.md`,
  `docs/mission-control.md`, and `docs/next-steps.md`
- closeout helpers may automatically update task status, generated task
  navigation (`tasks/ACTIVE.md` and `docs/task-views/*.md`), and `CONTEXT.md`;
  they should treat public narrative docs as check-and-follow-up surfaces
  unless an explicit docs-sync task authorizes editing them
- after applying closeout edits, the helper should remind the operator to
  publish the local closeout diff through a closeout commit and PR, or ask the
  maintainer to do it, so task-state changes do not remain only local

### Closeout sweep helper

Use this helper to find tasks that are still `REVIEW_READY` but already have a
merged canonical task PR in local `main` history.

It performs a minimal closeout-protocol gate before calling something a
closeout candidate. It does not just trust that a PR was merged.

The sweep may use merge history as a first-pass discovery source, but action
mode must not trust merge commit text alone as the task-to-PR source of truth.
Before a candidate can be treated as verified for closeout preparation, the
automation must also confirm the binding through GitHub PR metadata, such as:

- the PR title still resolves to the same `TASK-XXXX`; and/or
- the PR head branch still resolves to the same canonical task id.

If GitHub PR metadata cannot be loaded, the candidate must not advance to
closeout preparation.

```bash
python3 scripts/apl_closeout_sweep.py
```

Expected behavior:

- on a non-`main` or dirty branch, candidates will usually stay blocked with a
  clear reason;
- on a clean `main` checkout, verified tasks can become ready closeout
  candidates for the next action step;
- if GitHub PR metadata is unavailable or does not match the expected task id,
  the candidate must stay blocked or needs-attention rather than advancing to
  an automatic closeout PR.

For a quick local closeout snapshot, run:

```bash
python3 scripts/apl_task_closeout_check.py --task TASK-XXXX
```

This helper is intentionally lightweight. It reports the task file path, task
status, `tasks/ACTIVE.md` presence, accepted outputs, warnings, and suggested
closeout actions. It does not edit files.

Use `--suggest` for additional closeout suggestions without applying changes.

## Context Bundle

After major batches of merges, regenerate the single-file context bundle so
it stays current for chat-LLM users and agents reading `CONTEXT.md`:

```bash
python3 scripts/generate_context_bundle.py
git add CONTEXT.md && git commit -m "chore: regenerate context bundle"
git push origin main
```

The generator is intentionally idempotent for timestamp-only differences. If
the only possible change is the `Generated:` line, it leaves `CONTEXT.md`
untouched so snapshot and review runs do not create a false dirty worktree.
Treat any remaining `CONTEXT.md` diff after regeneration as meaningful source
drift that should be reviewed before PR merge or closeout.

Run this after:
- merging several tasks in a batch;
- updating `docs/strategy.md` or `docs/mission-control.md`;
- significant changes to `tasks/ACTIVE.md` beyond a routine board sync.

## Maintainer Prompts

### Pre-merge review

```text
Review PR #<number> according to docs/maintainer-review-agent.md.
Task: TASK-XXXX.
Use the review bundle and PR metadata.
Return MERGE_OK / NEEDS_CHANGES / BLOCKED.
Include risk, security risks, blockers, and required fixes for the developer.
Do not edit files.
```

### Pre-merge review for a task proposal

```text
Review PR #<number> according to docs/maintainer-review-agent.md.
Task: TASK-PROPOSAL.
Check branch, proposal file, PR title, proposal scope, review bundle, and overclaim risk.
Return MERGE_OK / NEEDS_CHANGES / BLOCKED.
Do not create a canonical TASK id unless I explicitly ask.
Do not edit files.
```

### Post-merge closeout

```text
Run task closeout for TASK-XXXX according to docs/maintainer-review-agent.md.
Check that the PR is merged and accepted outputs exist in main.
If valid, update task status to DONE.
Only run `python3 -m physics_lab.cli sync-active-board .` when we are doing a dedicated board-sync step.
```
