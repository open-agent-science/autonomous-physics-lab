# Self-Hosted CI Runner

APL routes the heavier Python CI jobs through a repository-scoped
self-hosted GitHub Actions runner. GitHub Actions remains the orchestration
layer for pull request status checks, but lint, pytest, example workflows, and
repository validation run on the maintainer-controlled CI VPS.

## Current Routing

`.github/workflows/ci.yml` keeps the small classifier job on GitHub-hosted
infrastructure:

- `Classify change set` runs on `ubuntu-latest`.

The heavier jobs default to the self-hosted Linux x64 runner:

- `Python fast tests (3.12)` for pull requests;
- `Python tests (main matrix)` for pushes to `main` or `master`.

The workflow reads runner labels from repository variables and falls back to
the built-in self-hosted labels:

```yaml
runs-on: ${{ fromJSON(vars.APL_PR_RUNNER_LABELS || '["self-hosted","linux","x64"]') }}
```

If multiple self-hosted runners are later attached to the repository, add a
dedicated label such as `apl-ci` to the runner and set:

```text
APL_PR_RUNNER_LABELS=["self-hosted","linux","x64","apl-ci"]
APL_MAIN_RUNNER_LABELS=["self-hosted","linux","x64","apl-ci"]
```

For a temporary GitHub-hosted fallback while the VPS runner is offline, set one
or both variables to `["ubuntu-latest"]`. This is an explicit operational
switch; GitHub Actions does not automatically move an already-queued
self-hosted job to a hosted runner.

## Runner Posture

The runner should be repository-scoped and run under a dedicated Linux user,
for example `github-runner`.

Recommended baseline:

- no `sudo` for the runner user;
- no project secrets in the runner user's home directory;
- no production databases, API keys, or deploy credentials on the CI host;
- no Docker group membership unless a later task explicitly designs container
  isolation;
- keep the runner as a systemd service owned by the runner user;
- keep the VPS disposable enough that it can be rebuilt if an untrusted PR
  executes unexpected code.

## Server Dependencies

The CI workflow uses Node 24-compatible GitHub actions, `actions/setup-python`,
`pip install -e ".[dev]"`, `ruff`, `pytest`, example workflows, and
`physics_lab.cli validate-repo`.

Pull requests use a faster gate on the self-hosted runner:

- docs/task-only PRs run the targeted docs/task test list;
- code PRs run `pytest -n auto --dist loadfile -m "not full_repo"`;
- `validate-repo . --strict --fail-on-warnings` still runs on every PR.

Pushes to `main` or `master` remain the full safety net and run:

```bash
pytest -n auto --dist loadfile
```

Tests marked `full_repo` are slow full-repository smoke checks. Keep them
covered by the main-matrix/full-validation path, but avoid making every PR pay
for duplicate live `validate-repo` smoke tests when the workflow already runs
strict repository validation as a separate CI step.

The host should have at least:

```bash
apt install -y curl tar gzip git python3 python3-venv python3-pip build-essential
```

Do not add secrets to the workflow to make tests pass. If a test requires
external credentials, it should not run in the default PR CI path.

## Rollback

If the runner is offline or jobs stay queued, set the repository variable:

```text
APL_PR_RUNNER_LABELS=["ubuntu-latest"]
```

Use `APL_MAIN_RUNNER_LABELS=["ubuntu-latest"]` only if the main-branch matrix
also needs to leave the self-hosted runner temporarily.

## Fast Fallback Rule

Use the self-hosted runner by default, but do not let a pull request sit in the
GitHub Actions queue silently. If `Python fast tests (3.12)` waits for a
self-hosted runner for more than about five minutes and the VPS service cannot
be confirmed healthy, switch PR CI to GitHub-hosted runners:

```text
APL_PR_RUNNER_LABELS=["ubuntu-latest"]
```

Then rerun the queued or failed workflow from GitHub. Restore the self-hosted
labels after the runner is healthy again:

```text
APL_PR_RUNNER_LABELS=["self-hosted","linux","x64"]
```

For main-branch failures, use the same pattern with `APL_MAIN_RUNNER_LABELS`,
but prefer fixing the self-hosted runner first because `main` is the full
safety net.

## Queue Visibility

Use these commands from a machine with GitHub CLI access:

```bash
gh run list --workflow CI --limit 10
gh run view <run-id> --jobs
gh run view <run-id> --log-failed
gh pr checks <pr-number>
```

Signals that point to runner availability rather than test failure:

- the job says `Waiting for a runner to pick up this job`;
- `Requested labels` are `self-hosted, linux, x64`;
- no Python test logs appear after the classifier job succeeds;
- rerunning the job leaves it queued with the same labels.

The repository helper prints the same queue and fallback checklist without
requiring a live GitHub call:

```bash
python3 scripts/apl_ci_runner_status.py
python3 scripts/apl_ci_runner_status.py --json
```

## VPS Health Checks

On the VPS, check the runner service and SSH path before changing repository
variables permanently:

```bash
cd /opt/actions-runner
./svc.sh status
systemctl status 'actions.runner.*'
journalctl -u 'actions.runner.*' -n 120 --no-pager
systemctl status ssh
ss -tlnp | grep ':22'
```

Common causes and fixes:

- SSH refused from one network but works from another: check VPN, IP reputation,
  provider firewall, and local network path before rebuilding the runner.
- `Waiting for a runner`: start the service with `./svc.sh start` or restore the
  repository variables to `["ubuntu-latest"]` while debugging.
- `Exec format error`: the wrong runner package was installed. Linux VPS hosts
  need the `actions-runner-linux-x64-*.tar.gz` package, not the macOS package.
- Duplicate runner name during `config.sh`: remove or replace the stale runner
  from GitHub settings, or register a clearly named replacement and update
  labels if needed.
- Stopped service after reboot: confirm `./svc.sh install github-runner` and
  `./svc.sh start` were run from `/opt/actions-runner` as root, with the service
  configured to run as the dedicated `github-runner` user.

Keep these diagnostics manual for now. Do not add Hetzner API automation,
auto-provisioning, Docker orchestration, or repository secrets unless a later
security-reviewed task explicitly designs that layer.
