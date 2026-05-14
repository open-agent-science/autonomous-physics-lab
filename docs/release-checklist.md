# Release Checklist

## Purpose

This file is the maintainer checklist for cutting a repository opening or
public-alpha style release.

Use it before:

- creating a release tag;
- drafting GitHub release notes;
- preparing a repo-native opening pack.

## v0.2 Repository Opening Gate

Before opening the repository or tagging a future `v0.2-public-alpha`, confirm
all of the following:

- repository worktree is clean;
- local validation commands pass;
- GitHub Actions is green on the default branch;
- roadmap and status docs still describe scope honestly;
- canonical result artifacts are intentionally up to date;
- no accidental local path leaks exist in public-facing files;
- the opening-pack docs match the current repository evidence.

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
python3 scripts/check_public_path_leaks.py
git ls-files .pytest_cache .ruff_cache
```

Expected:

- no path leaks in tracked docs or artifacts;
- no cache directories tracked by git.

## Release Artifacts to Review

Confirm these are present and intentional:

- `docs/v0.2-launch-pack.md`
- `docs/releases/v0.2-public-alpha.md`
- `docs/use-your-agent.md`
- `docs/status.md`
- `docs/roadmap.md`
- `docs/mission-control.md`
- `docs/results/visual-summary.md`
- `docs/results/koide-campaign-summary.md`
- `docs/negative-results-registry.md`
- `docs/notes/v02-overclaim-audit.md`
- `docs/claim-promotion-policy.md`

## Tagging Flow

Once the branch is pushed and GitHub Actions is green:

```bash
git tag -a v0.2-public-alpha -m "Public alpha: verification-first scientific campaign opening"
git push origin v0.2-public-alpha
```

## GitHub Release

On GitHub:

1. Open `Releases`.
2. Draft a new release from `v0.2-public-alpha`.
3. Use the prepared notes from `docs/releases/v0.2-public-alpha.md`.
4. Keep the wording modest and verification-first.

## Scope Reminder

Do not present `v0.2-public-alpha` as:

- a broad physics platform;
- an autonomous multi-agent lab;
- a theory-discovery engine already operating at scale;
- a repository that already settled particle-mass questions globally.

Do present it as:

- a verification-first repository opening;
- a small set of reproducible benchmark and falsification surfaces;
- a public scientific memory prototype with contributor workflow discipline.
