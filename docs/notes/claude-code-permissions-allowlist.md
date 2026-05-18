# Claude Code Permissions Allowlist

**Status:** IMPLEMENTED UNDER TASK-0260
**File:** [`.claude/settings.json`](../../.claude/settings.json)

---

## 1. Purpose

`.claude/settings.json` is the *shared* permission allowlist for Claude Code
sessions in this repository. Anything listed under `permissions.allow` runs
without an interactive approval prompt. Anything not listed prompts the user
per-call.

This document explains why each rule is on the allowlist and where the
safety boundary sits. Use it when reviewing PRs that touch
`.claude/settings.json` or when an agent needs an operation that is
currently denied.

The local-only counterpart `.claude/settings.local.json` is gitignored and
holds per-contributor overrides; it does not need to repeat anything that is
already in the shared file.

## 2. Safety boundary

Rules in the allowlist must be **read-only**, **idempotent**, or **safely
scoped**. Specifically:

- Read-only inspection (e.g. `git status`, `head`, `sed -n`) is always safe.
- Non-destructive git operations (`git stash push`, `git reset --mixed`)
  modify only local state and never touch published history.
- Path-scoped Read/Write rules (e.g. `Read(/tmp/apl-*)`) are limited to
  agent-generated working files; they cannot reach user data or other
  repositories.

New rules should not add destructive shortcuts. Some legacy Git/GitHub rules
are still broad enough that repository policy and maintainer review remain the
final safety layer; do not interpret a shared permission match as approval to
perform destructive or final-review actions.

Do not add dedicated shared allowlist rules for:

- `rm`, `rm -rf` — file deletion
- `git reset --hard`, `git checkout -- <path>` (without explicit path) —
  discards uncommitted work
- `git push --force`, `git push --force-with-lease` — rewrites remote
  history
- `git branch -D`, `git tag -d` — destructive branch/tag deletion
- `git clean -f` — deletes untracked work
- `gh pr merge` — final merge decision belongs to a human maintainer or an
  explicitly authorized maintainer-mode run

A contributor who genuinely needs one of these in a single session can use
`.claude/settings.local.json` for their own check-out without affecting the
shared rules. Even when a broad legacy rule would technically match, agents
must still follow `AGENTS.md` and maintainer instructions before pushing,
merging, deleting, or discarding local state.

### Unsafe mode: `Bash(*)`

This repository may intentionally enable an **unbounded** rule `Bash(*)` in
`.claude/settings.json` to remove all Claude Code approval prompts for shell
commands.

This is **maintainer-only** and should not be enabled when running untrusted
agents or external contributors. It permits arbitrary shell execution (including
destructive commands) without interactive confirmation. Repository protocol
still applies, but protocol violations are no longer prevented by Claude Code
permissions.

## 3. Rule groups

### 3.1 Python entrypoints

`python3 -m ruff *`, `python3 -m pytest *`, `python3 -m physics_lab.cli *`,
`python3 scripts/apl_*.py *`, plus the nuclear prediction batch helpers.
These are the canonical validation, mission-control, and PR-helper
commands. They are read-only with respect to scientific artifacts; the few
write-side helpers (`sync-active-board`, the PR scaffolders) only touch
generated navigation and PR body drafts.

### 3.2 Repository helper scripts

`./scripts/apl_setup_worktree.sh`, `./scripts/apl_new_worktree.sh *`,
`./scripts/apl_review_bundle.sh`, `./scripts/apl_snapshot.sh`,
`./scripts/validate_quick.sh`. Bounded internal helpers that do not call
out to the network and do not modify canonical artifacts beyond their
documented scope. `apl_new_worktree.sh` accepts a branch name and an
optional path argument; it refuses to overwrite an existing branch and
bases the new worktree on `origin/main`.

### 3.3 Git read-only inspection

`git status *`, `git log *`, `git diff *`, `git show *`, `git branch *`,
`git ls-files *`, `git rev-parse *`, `git rev-list *`, `git merge-base *`,
`git blame *`, `git diff-tree *`, `git config --get *`,
`git worktree list`, `git remote *`, `git reflog *`. These are intended for
inspection. Avoid destructive subcommands such as branch deletion even if a
legacy broad pattern could technically match them.

### 3.4 Git stash

`git stash list`, `git stash show *`, `git stash push *`,
`git stash pop *`, `git stash apply *`, `git stash drop *`. The generic
`git stash *` umbrella is deliberately not allowed because it would also cover
`git stash clear`. Stash pushes save state; pops/apply restore it; drops should
only remove a specific reviewed stash id. This group exists because cleaning
untracked artifacts before maintainer review (`apl_review_pr.py`) regularly
needs `git stash push --include-untracked`.

### 3.5 Git mutations on the working branch

`git fetch *`, `git pull *`, `git switch *`, `git checkout *`, `git add *`,
`git commit *`, `git push *`, `git restore --staged *`, `git reset HEAD *`,
`git reset --mixed *`, `git reset --soft *`, `git merge origin/main`,
`git merge --no-edit origin/main`, `git merge origin/main --no-edit`,
`git merge --ff-only origin/main`, `git merge origin/main --ff-only`,
`git merge --abort`, `git merge --quit`. These mutate local branches
and may push them, but `--mixed` and `--soft` resets keep the working tree
intact, and `--hard`/`--keep` are *not* on the list. The shared rules do
not block agents from pushing the task branch they own — pushing to `main`
is prevented by repository policy, not by Claude Code permissions.

The merge rules are intentionally scoped to the routine operation agents need:
bringing `origin/main` into the current task branch, optionally with
`--no-edit` or `--ff-only`. `--abort` and `--quit` are explicitly listed
because they safely exit an in-progress merge. Broad `git merge *` and
strategies that silently overwrite one side of a merge (`--strategy=ours`,
`--strategy-option=theirs`) are *not* on the list; an agent that needs those
still has to ask.

### 3.6 Text inspection

`sed -n *`, `head *`, `tail *`, `wc *`, `cat *`, `ls *`, `grep *`, `rg *`,
`echo *`.

The `sed -n *` form intentionally restricts `sed` to the `-n` "no
auto-print" mode, which is the print-range form (`sed -n '10,20p'`).
Write-side `sed` (`sed -i ...` or `sed 's/.../.../'`) is not matched by
this rule and still prompts. Agents that need write-side text edits should
use the `Edit` tool with explicit before/after strings rather than scripted
substitution.

`awk *` and `find . *` are intentionally not shared rules. `awk` can execute
shell commands, and `find` has destructive forms such as `-delete`; agents can
use `rg --files`, `git ls-files`, `ls`, `head`, `tail`, or request approval for
a specific `find`/`awk` command when needed.

### 3.7 GitHub CLI

`gh pr *`, `gh run *`, `gh api repos/*`, `gh auth status`, plus the
Homebrew-path variants for sessions where `PATH` is missing
`/opt/homebrew/bin`. The `gh api repos/*` pattern restricts API calls to
the repository scope; `gh api user`, `gh api orgs/*`, etc. still prompt.
PR merge remains governed by repository protocol and explicit maintainer
authorization; a permission match is not approval to merge.

### 3.8 Agent-owned temporary paths

`Read(/tmp/apl-*)`, `Read(/tmp/apl-*/**)`, `Read(/tmp/claude-*/**)`,
`Write(/tmp/apl-*)`, `Write(/tmp/apl-*/**)`,
`Edit(/tmp/apl-*)`, `Edit(/tmp/apl-*/**)`,
plus `/private/tmp/...` mirrors for macOS where `/tmp` symlinks to
`/private/tmp`.

This covers the PR-body drafts generated by `apl_task_pr_helper.py
scaffold`, the example-run output directories used by validation commands
(`--output-dir /tmp/apl-pendulum`, etc.), and the per-session task-output
log directory used by Claude Code itself.

The rules are deliberately narrow: only paths matching `apl-*` or
`claude-*` under `/tmp` are read/write-allowed. An agent that wants to read
something else from `/tmp` still has to ask.

### 3.9 Filesystem scaffolding

`mkdir -p *` is allowed because validation paths regularly need to ensure
output directories exist. It is idempotent. Single-form `mkdir` (without
`-p`) is not on the list because it errors on existing paths, which is
strictly worse for automation.

## 4. Adding a new rule

1. Confirm the rule belongs in the *shared* `settings.json` (helps all
   contributors) rather than personal `settings.local.json`.
2. Keep it narrow — prefer `tool arg-pattern` over a blanket `tool *`.
3. Reject anything destructive or anything that escapes the repository
   scope.
4. Update this note in the same PR so the rationale is reviewable.
5. Follow the canonical task protocol — a `TASK-XXXX` and a PR are
   required for `.claude/settings.json` changes the same way as for any
   other repository file.

## 5. Parallel agent sessions

This file does *not* prevent two agents from working on the same branch
checkout. If you run multiple Claude Code or Codex sessions in parallel
against the same repository, prefer one of:

- a dedicated `git worktree` per session, created with
  `git worktree add ../<branch-slug> <branch>`;
- distinct local repository clones;
- coordinating which session "owns" the checkout for a given time window.

A separate task should add explicit worktree-per-agent guidance and a
`git status` precondition check to the agent instructions; that work is
out of scope for `TASK-0260`.
