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
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
python3 scripts/apl_mission.py --output json
python3 scripts/reproduce_core_results.py --output-dir /tmp/apl-core-reproduction --python python3
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

## Public Artifact History Checks

Before opening the repository publicly, confirm that the Phase B
source-artifact history scan has been completed and reviewed, or that a current
release-time scan proves no cleanup remains. This is a release blocker, not a
routine validation command.

Current status: `TASK-0858` verified `origin/main` at
`15a9675b097250be88e0cb3fa7a2e3acd59c8373` and found no reachable `.pdf` blobs,
no risky binary/document/archive additions, and no reachable default-branch
history for the two arXiv PDF paths named by `TASK-0732`. Treat the old
freeze-time rewrite blocker as closed for this default-branch cut. Re-run the
scan during the final exact-SHA release signoff; reopen the history-cleanup gate
if new risky paths appear.

Minimum evidence:

- all reachable refs were scanned for large blobs and historically added
  publisher/preprint/source-artifact payloads;
- candidate non-redistributable paths, if any, were recorded with evidence and
  a reviewed removal plan;
- any `git filter-repo` / force-push cleanup happened only after a maintainer
  merge freeze and was followed by fresh validation, CI, and contributor
  re-clone/rebase instructions;
- if no rewrite was needed, the signoff explains why the public default branch
  history is already clean enough for launch.

Recommended release-time commands:

```bash
git log --oneline origin/main -- data/atomic_clocks/source_artifacts/2016-nemitz-riken/arxiv-1601.04582.pdf
git log --oneline origin/main -- data/atomic_clocks/source_artifacts/2021-beloy-bacon/arxiv-2005.14694.pdf
git rev-list --objects origin/main | rg -i '\.pdf$'
git log origin/main --diff-filter=A --name-only --pretty=format: \
  | rg -i '\.(pdf|zip|tar|gz|tgz|7z|rar|xlsx|xls|docx|doc|pptx|ppt|fits|fit|h5|hdf5|parquet|nc|db|sqlite)$' \
  | sort -u
```

Expected for the current public-opening cut:

- no output for the two historical PDF path logs;
- no reachable `.pdf` blobs;
- no risky binary/document/archive additions on `origin/main`.

## GitHub Visibility And Branch Protection

If GitHub allows `main` branch protection while the repository is still
private, enable or confirm it before public opening. If the current plan only
allows branch protection after the repository becomes public, record the
intended `main` protection policy in the signoff, switch visibility only after
the other release gates pass, then enable branch protection immediately after
the public switch and before inviting external contributors or announcing the
repository broadly.

## Final Signoff

Before opening the repository, add or refresh a dated signoff artifact under
`docs/reviews/` against the exact default-branch commit that will be opened.
The signoff should record local validation, default-branch CI, public path leak
status, public wording review, and any remaining maintainer-only decisions.

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
