# Agent Discipline — Collected Learnings

**Status:** IMPLEMENTED UNDER TASK-0270
**Audience:** Claude Code, Codex, future LLM agents, and human contributors
running an agent loop in this repository.

---

## Purpose

This note is a single navigation surface for the agent-side disciplines
that accumulated during the TASK-0260..TASK-0268 contributor-experience
wave. Each rule pairs with the concrete incident it came from, and links
out to the single-topic note that owns the surface in question.

The note is intentionally short. If you find yourself wanting to expand a
section, expand the linked note instead and keep this file as the index.

---

## 1. Use a `git worktree` per task when parallel agents are plausible

**Rule.** When two or more agent sessions are (or might soon be) active in
the same checkout, do not share the working tree. Open a dedicated git
worktree per task with `./scripts/apl_new_worktree.sh <branch-name>` and
do all work there.

**Why.** TASK-0227 / TASK-0251 incident: a parallel Codex session
silently committed TASK-0251 work onto the active Claude TASK-0227
branch. Recovery required `git reset --mixed`, a selective revert, and
a re-sync of generated views. The same class of incident hit again
during TASK-0267..TASK-0268 (Codex was actively flipping `HEAD` in the
shared checkout while Claude was finishing the wave).

**How.** [`docs/notes/agent-worktree-discipline.md`](agent-worktree-discipline.md)
owns the full procedure (helper script, precondition check, cleanup
after merge). Run
`python3 scripts/apl_branch_precondition.py --expected-branch <branch>`
before any `git add` / `commit` / `push` to catch a stray `HEAD` move.

## 2. Mock-first when a test would need to "reconstruct a valid repo"

**Rule.** If a unit test seems to require copying more than ~3
directories from the real repo to reconstruct a working state, the
approach is wrong. Reach for `unittest.mock.patch` or `monkeypatch`
against the function or registry layer directly.

**Why.** TASK-0262 lost ~10 minutes and ~150 lines of test code on a
`_copy_minimal_repo()` helper that kept hitting missing dependencies
(`campaign_profiles/` missing, then `physics_lab/workflows/pendulum.py`
missing, etc.). Replacing the sandbox with two `patch(...)` calls
finished in 5 minutes and gave better tests.

**How.** Patch the closest layer above the I/O. For
`physics_lab.cli validate-repo`, mock
`physics_lab.cli.validate_repository` and
`physics_lab.cli.sync_generated_task_state`. For maintainer-review
agents, mock `git_status_clean` and `working_tree_changed_files`. The
result reads in seconds, runs in milliseconds, and exercises the
control flow rather than the filesystem.

## 3. Serialise dependent PRs; do not branch off an unmerged predecessor

**Rule.** If `PR_B` needs code from `PR_A` and `PR_A` is not yet on
`main`, wait for `PR_A` to merge before opening `PR_B` against `main`.
If you cannot wait, open `PR_B` *against* the `PR_A` branch and rebase
once `PR_A` lands.

**Why.** TASK-0263 was branched off `main` before TASK-0262 merged. By
the time TASK-0263 needed `--auto-sync` (added in TASK-0262), the
branch had to merge `origin/main`, re-run sync, re-run validation, and
re-trigger the maintainer review — adding one full cycle of friction.

**How.** Check `gh pr view <PR>` before starting follow-up work. If the
predecessor is still `OPEN`, ask whether to branch off it instead of
`main`. If an already-open PR becomes stale or conflicted after another
PR lands, sync once deliberately, resolve conflicts narrowly, rerun
validation/review, and mention the sync in the PR.

## 4. Watch for harness artifacts in `git status`

**Rule.** Treat any path matching `.claude/scheduled_tasks.lock`,
`_snapshots/`, `.claude/worktrees/`, or other harness state as
non-blocking noise. Do not commit it, do not stash it as if it were
your work, do not let it block maintainer review.

**Why.** During TASK-0227 the maintainer review agent returned
`NEEDS_CHANGES` purely because the harness lockfile was untracked.
TASK-0261 fixed this at the source (`.gitignore` + `HARNESS_IGNORE_PATHS`
defense-in-depth), but the lesson generalises to any new harness path:
the moment a file is generated *for* the agent rather than *by* the
agent's task, it belongs in `.gitignore` or in the in-process ignore list,
not in a stash dance.

**How.** [`docs/notes/claude-code-permissions-allowlist.md`](claude-code-permissions-allowlist.md)
section 3.8 documents agent-owned `/tmp/apl-*` paths. The
`HARNESS_IGNORE_PATHS` tuple in `physics_lab/registry/review_git.py`
holds the in-process defense-in-depth list. Add new entries there with
a PR, not by stashing.

Generated task navigation is similar:
`docs/task-views/*.md` are derived files. Normal task PRs should not
commit regenerated board/view updates unless the maintainer explicitly
asks for a dedicated board-sync or closeout/audit PR. The post-merge
`Sync Active Board` action handles routine regeneration through a generated
board-sync PR.

## 5. PR-helper boilerplate is duplication, not a permanent cost

**Rule.** When `apl_task_pr_helper.py scaffold` needs the same 10+
`--flag value` arguments on every PR (contributor-id, github-username,
agent-id, agent-tool, model-version, validation-command list, etc.), it
is a candidate for default-derivation, not the agent's problem to keep
repeating.

**Why.** Over the TASK-0260..TASK-0268 wave the scaffold call grew to
~15 flags per PR with ~90% repeat content. This is token cost, eye
strain, and a copy-paste hazard.

**How.** Open a separate task that teaches the scaffolder to derive
defaults from branch name, `git config`, and the canonical task YAML.
That work is out of scope for this collected-learnings note.

---

## Linked notes (canonical owners)

- [Agent worktree discipline](agent-worktree-discipline.md) — owns the
  worktree-per-task procedure, the `apl_new_worktree.sh` helper, and the
  `apl_branch_precondition.py` check.
- [Claude Code permissions allowlist](claude-code-permissions-allowlist.md)
  — owns the shared `.claude/settings.json` rules, the safety boundary,
  and the harness-path read/write scopes.

Future single-topic notes added in this lane should be linked from here
so the index stays the entry point.
