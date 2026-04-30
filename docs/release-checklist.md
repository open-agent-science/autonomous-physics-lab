# Release Checklist

## Purpose

This file is the maintainer checklist for cutting a public-alpha release.

Use it before:

- creating a release tag;
- drafting GitHub release notes;
- writing a small public announcement.

## v0.1-public-alpha Gate

Before tagging `v0.1-public-alpha`, confirm all of the following:

- repository worktree is clean;
- local validation commands pass;
- GitHub Actions is green on the default branch;
- roadmap and status docs still describe scope honestly;
- canonical result artifacts are intentionally up to date;
- no accidental local path leaks exist in public-facing files.

## Local Validation Commands

Run:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum
python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli status .
git diff --exit-code
```

## Hygiene Checks

Run:

```bash
git grep -n "/Users/roman\\|MacBook\\|Autonomous%20Physics%20Lab" README.md AGENTS.md CODEX_TASK.md docs claims knowledge results physics_lab || true
git ls-files .pytest_cache .ruff_cache
```

Expected:

- no path leaks in tracked docs or artifacts;
- no cache directories tracked by git.

## Release Artifacts to Review

Confirm these are present and intentional:

- `results/EXP-0001/RUN-0001/`
- `results/EXP-0001/RUN-0002/`
- `results/EXP-0002/RUN-0001/`
- `docs/status.md`
- `docs/roadmap.md`
- `docs/claim-promotion-policy.md`
- `docs/contributing-workflow.md`

## Tagging Flow

Once the branch is pushed and GitHub Actions is green:

```bash
git tag -a v0.1-public-alpha -m "Public alpha: two verification-backed physics benchmarks"
git push origin v0.1-public-alpha
```

## GitHub Release

On GitHub:

1. Open `Releases`.
2. Draft a new release from `v0.1-public-alpha`.
3. Use the prepared notes from `docs/releases/v0.1-public-alpha.md`.
4. Keep the wording modest and verification-first.

## Scope Reminder

Do not present `v0.1-public-alpha` as:

- a broad physics platform;
- an autonomous multi-agent lab;
- a theory-discovery engine already operating at scale.

Do present it as:

- a verification-first public alpha;
- two reproducible benchmark slices;
- a public scientific memory prototype.
