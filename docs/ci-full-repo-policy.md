# CI full_repo Visibility Policy

`full_repo`-marked tests are heavier smoke tests (CLI status/mission smoke, core
result replays, example runs). The PR fast lane skips them
(`pytest -m "not full_repo"`), so historically a `full_repo` break merged green
and only surfaced post-merge on the main matrix — or, worse, on an unrelated
later PR. With safe auto-closeout relying on a green main, that "green" must be
honest about `full_repo`.

This policy makes `full_repo` status visible through two complementary layers.

## 1. Risk-based PR gate (`.github/workflows/ci.yml`)

The `classify` job computes `full_repo_risk` from the PR's changed paths. The
`Run full_repo smoke tests (risk-relevant PRs)` step runs `pytest -m full_repo`
only when `full_repo_risk == true`:

- **Risk-relevant** (run full_repo): `physics_lab/**`, `scripts/**`, `tests/**`,
  `examples/**`, `results/**`, `.github/workflows/**`, `pyproject.toml`,
  `missions/**`, `campaign_profiles/**`, `docs/status.md`,
  `docs/mission-control.md`, `README.md`.
- **Fast lane** (skip full_repo): pure prose docs (`docs/reviews/**`,
  `docs/notes/**`, …) and routine task-status flips (`tasks/**`).

The `Python fast tests` job is the stable required check for branch protection;
the full_repo step lives inside it and is conditional, so docs/task-only PRs stay
fast while risk-relevant PRs catch `full_repo` breakage **before** merge.

## 2. Nightly watchdog (`.github/workflows/nightly-full-repo.yml`)

A scheduled job runs `full_repo` + strict validation + core example replays on
`main`. It catches what slips past the PR gate (flaky tests, dependency drift,
main-only interactions) within a day. A failure means **main is not
full_repo-clean**.

## Interaction with safe auto-closeout

Safe auto-closeout (`docs/maintainer-review-agent.md`) commits `DONE` flips
directly to `main`. It must treat the `full_repo` signal as load-bearing: when
the latest `full_repo` status (PR gate or nightly) is red, stale, or unknown,
commit-safe auto-closeout falls back to **report-only**. This policy is the
prerequisite that makes the "green main" gate honest.

## What this is not

- Not "run full_repo on every PR" — that would slow the common docs/task lane
  for no benefit; risk classification keeps it targeted.
- Not "rely on nightly alone" — a risk-relevant PR can break `main` before the
  nightly runs, so the PR gate catches those pre-merge.
