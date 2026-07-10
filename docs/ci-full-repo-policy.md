# CI full_repo Visibility Policy

`full_repo`-marked tests are heavier smoke tests (CLI status/mission smoke, core
result replays, example runs). The PR fast lane skips them
(`pytest -m "not full_repo"`), so historically a `full_repo` break merged green
and only surfaced post-merge on the main matrix — or, worse, on an unrelated
later PR. With safe auto-closeout relying on a green main, that "green" must be
honest about `full_repo`.

This policy makes `full_repo` status visible through two complementary layers.

## 1. Required merge-queue gate (`.github/workflows/ci.yml`)

The `classify` job computes `full_repo_risk` from the PR's changed paths. The
merge queue forces `docs_task_only=false` and `full_repo_risk=true`, then the
required `Python fast tests (3.12)` check runs the heavy suite on the exact
merge-group tree that can land on `main`:

- `pytest -m "not full_repo"` runs on every merge-group entry.
- `pytest -m full_repo` runs on merge-group entries whose classified tree is
  risk-relevant. The queue path is conservatively risk-relevant by default.

Risk-relevant paths are:

- `physics_lab/**`, `scripts/**`, `tests/**`,
  `examples/**`, `results/**`, `.github/workflows/**`, `pyproject.toml`,
  `missions/**`, `campaign_profiles/**`, `docs/status.md`,
  `docs/mission-control.md`, `README.md`.

Pull-request pushes no longer run the heavy pytest layers. They stay on the
cheap deterministic feedback path: ruff, strict repository validation, and the
targeted docs/task tests when `docs_task_only == true`. This keeps review
latency low while preserving the merge gate, because branch protection requires
the merge queue and the queue reports the same required check names.

## 2. Nightly watchdog (`.github/workflows/nightly-full-repo.yml`)

A scheduled job runs `full_repo` + strict validation + core example replays on
`main`. It catches what slips past the PR gate (flaky tests, dependency drift,
main-only interactions) within a day. A failure means **main is not
full_repo-clean**.

## 3. Main push redundancy path (`.github/workflows/ci.yml`)

Pushes to `main` are also classified. Code, workflow, schema, result, example,
mission, README, and other non-doc/task changes run a 3.11 post-merge
redundancy matrix on GitHub-hosted runners. Pure docs/task/navigation pushes
run only the cheap path and rely on the merge-queue gate plus board-sync
validation. This keeps generated board-sync commits from spending the full
matrix cost after every merge while preserving validation for generated task
navigation.

Main push CI runs are not cancelled by newer `main` pushes. The CI concurrency
group uses the PR number for pull requests and the commit SHA for push runs,
with `cancel-in-progress` enabled only for pull requests. This lets stale PR
runs stop quickly while preserving two post-merge signals when both are useful:
the merge-commit full main matrix and the later board-sync docs/task lane.

## Interaction with safe auto-closeout

Safe auto-closeout (`docs/maintainer-review-agent.md`) commits `DONE` flips
directly to `main`. It must treat the `full_repo` signal as load-bearing: when
the latest `full_repo` status (PR gate or nightly) is red, stale, or unknown,
commit-safe auto-closeout falls back to **report-only**. This policy is the
prerequisite that makes the "green main" gate honest.

Because docs/task-only pushes and PR fast-lane runs no longer always run the
full main matrix,
`full_repo_signal_status` must ignore light push CI runs and look back to the
most recent completed CI run that actually included a full_repo signal.

## What this is not

- Not "run full_repo on every PR push" — that would slow review feedback and
  duplicate the required merge-queue gate.
- Not "rely on nightly alone" — the required merge queue catches heavy-suite and
  `full_repo` breakage before merge, and nightly remains the drift watchdog.
