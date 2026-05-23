# Self-Hosted CI Runner

APL routes the heavier Python CI jobs through a repository-scoped
self-hosted GitHub Actions runner. GitHub Actions remains the orchestration
layer for pull request status checks, but lint, pytest, example workflows, and
repository validation run on the maintainer-controlled CI VPS.

## Current Routing

`.github/workflows/ci.yml` keeps the small classifier job on GitHub-hosted
infrastructure:

- `Classify change set` runs on `ubuntu-latest`.

The heavier jobs run on the self-hosted Linux x64 runner:

- `Python tests (3.12)` for pull requests;
- `Python tests (main matrix)` for pushes to `main` or `master`.

The workflow currently targets the built-in runner labels:

```yaml
runs-on: [self-hosted, linux, x64]
```

If multiple self-hosted runners are later attached to the repository, add a
dedicated label such as `apl-ci` to the runner and update the workflow to:

```yaml
runs-on: [self-hosted, linux, x64, apl-ci]
```

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

The CI workflow uses `actions/setup-python`, `pip install -e ".[dev]"`, `ruff`,
`pytest`, example workflows, and `physics_lab.cli validate-repo`.

The host should have at least:

```bash
apt install -y curl tar gzip git python3 python3-venv python3-pip build-essential
```

Do not add secrets to the workflow to make tests pass. If a test requires
external credentials, it should not run in the default PR CI path.

## Rollback

If the runner is offline or jobs stay queued, rollback is intentionally small:

```yaml
runs-on: ubuntu-latest
```

Apply that only to the affected Python job while keeping the classifier job
unchanged.
