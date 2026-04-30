# Project Status

## Current Stage

`v0.1-public-alpha` candidate

Current working vertical slice:

`Hypothesis -> Experiment -> Result -> Claim -> Knowledge -> Next Task`

## Completed

- pendulum formula discovery workflow;
- exact pendulum reference simulator;
- deterministic candidate formula fitting and scoring;
- verification-backed pendulum checks;
- run-based result artifact generation;
- public memory registry for hypothesis, experiment, claim, task, result, and knowledge;
- repository-wide validation and referential integrity checks;
- basic CI configuration with lint, tests, example run, and repository validation.

## Current Verification Checks

- small-angle limit;
- small-angle exact-window agreement;
- small-angle curvature agreement;
- upper-range exact-window agreement;
- near-separatrix extrapolation diagnostic (non-gating);
- separatrix asymptotic-alignment diagnostic (non-gating);
- evenness;
- monotonicity;
- dimensional consistency;
- known small-angle coefficient comparison.

## Ready Now

- `python3 -m ruff check .`
- `python3 -m pytest`
- `python3 -m physics_lab.cli run examples/pendulum.yaml`
- `python3 -m physics_lab.cli validate-repo .`
- `python3 -m physics_lab.cli status .`

## Not Ready Yet

- external agent contribution flow;
- second physics benchmark;
- literature ingestion;
- public dashboard;
- theory graph.

## Public Repo Status

Suitable for public alpha once:

- local validation stays green;
- GitHub Actions is green;
- roadmap and next steps remain honest about scope.

## Snapshot Utility

Use the repository snapshot script when you want a compact project state dump:

```bash
./scripts/apl_snapshot.sh
RUN_EXPERIMENT=1 ./scripts/apl_snapshot.sh
PYTHON_BIN=python3.11 ./scripts/apl_snapshot.sh
```

Recommended times to run it:

- after a meaningful Codex task;
- before making the repository public;
- before a tag or release;
- after roadmap or architecture changes;
- after schema or result-format changes;
- after adding a new benchmark.
