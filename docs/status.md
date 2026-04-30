# Project Status

## Current Stage

`v0.1-public-alpha` candidate

Current working slices:

- `Pendulum Formula Discovery`
- `Damped Oscillator Regime Verification`

## Completed

- pendulum formula discovery workflow;
- exact pendulum reference simulator;
- deterministic candidate formula fitting and scoring;
- verification-backed pendulum checks;
- run-based result artifact generation;
- public memory registry for hypothesis, experiment, claim, task, result, and knowledge;
- repository-wide validation and referential integrity checks;
- basic CI configuration with lint, tests, example run, and repository validation;
- damped-oscillator exact-solution benchmark with run-based artifacts.

## Current Verification Checks

Pendulum:

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

Damped oscillator:

- regime classification;
- initial-condition recovery;
- underdamped energy decay;
- oscillatory vs non-oscillatory behavior;
- dimensional consistency.
- `c -> 0` undamped-limit check;
- underdamped envelope decay-rate check;
- critical damping boundary check;
- overdamped asymptotic tail check.

## Ready Now

- `python3 -m ruff check .`
- `python3 -m pytest`
- `python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum`
- `python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped`
- `python3 -m physics_lab.cli validate-repo .`
- `python3 -m physics_lab.cli status .`

## Not Ready Yet

- external agent contribution flow;
- literature ingestion;
- public dashboard;
- theory graph.

## Current Risks

- `runner.py` must stay a thin dispatcher so workflow logic does not drift back into one file.
- Canonical artifacts under `results/` can become stale if contributors run examples without `--output-dir`.
- The result schema is shared by both benchmarks, so benchmark-specific semantics still need careful wording.
- Public alpha is stable for two slices, but not yet broad enough for a wider “many benchmark” claim.

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
