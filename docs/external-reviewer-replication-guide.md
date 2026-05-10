# External Reviewer Replication Guide

This guide gives a cautious outside reviewer a short path for sanity-checking
APL's strongest current evidence without first learning the maintainer task
workflow.

It is not a contributor onboarding guide and it is not a public-launch
announcement. It explains how to replay the bounded core result surface, where
to inspect canonical artifacts, and which interpretations remain out of scope.

## Review Scope

Start with the current core result surface:

| Surface | Canonical Result | Why Review It |
|---|---|---|
| Pendulum gauntlet | `EXP-0001/RUN-0003` (`RESULT-0004`) | strongest classical benchmark package with leaderboard, diagnostics, and precision audit |
| Dimensional-analysis validator | `EXP-0006/RUN-0006` (`RESULT-0007`) | frozen 50-item MVP benchmark with explicit limitations |
| Charged-lepton Koide reproduction | `EXP-0004/RUN-0004` (`RESULT-0005`) | narrow dataset-based reproduction with uncertainty-aware comparison |
| Historical tau holdout | `EXP-0005/RUN-0005` (`RESULT-0006`) | scoped holdout-style benchmark, not a mass-generation explanation |
| Neutrino Koide falsification | `EXP-0007/RUN-0001` (`RESULT-0009`) | first-class negative particle-mass result under encoded assumptions |
| Quark Koide falsification | `EXP-0008/RUN-0001` (`RESULT-0010`) | quark-sector negative result under stored dataset and scale assumptions |
| Particle-mass falsifier MVP | `EXP-0009/RUN-0001` (`RESULT-0011`) | fixed-target falsifier workflow with baseline and complexity-penalty reporting |

The default replication path intentionally excludes `EXP-0010` / Muon g-2. That
run is a guarded empirical formula-search stress test with multiple-testing and
numerology limitations, not a flagship success surface.

## Quick Replication Path

From a fresh checkout:

```bash
git clone https://github.com/gladunrv/autonomous-physics-lab.git
cd autonomous-physics-lab

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"

python3 scripts/reproduce_core_results.py
```

The replay writes regenerated artifacts outside the canonical `results/` tree,
under `/tmp/apl-core-reproduction` by default. It also writes:

```text
/tmp/apl-core-reproduction/CORE_REPRODUCTION_SUMMARY.md
```

A passing replay means each selected regenerated `result.yaml` has the expected
canonical result id and verdict. It does not mean byte-for-byte equality with
the committed artifacts.

Useful variants:

```bash
python3 scripts/reproduce_core_results.py --list
python3 scripts/reproduce_core_results.py --only pendulum-gauntlet
python3 scripts/reproduce_core_results.py --output-dir /tmp/apl-review
```

## What To Compare

Compare stable scientific fields first:

- `result_id`, `experiment_id`, and `run_id`;
- `best_verdict`;
- core metrics listed in [reproducibility-capsules.md](./reproducibility-capsules.md);
- verification checks and limitation wording;
- whether negative results stay visible as negative results.

Do not treat these as material drift by themselves:

- generated timestamps;
- local output paths;
- copied-input snapshot paths;
- git commit metadata;
- harmless report formatting around unchanged metrics and verdicts.

## Canonical Artifacts To Inspect

- [Project status](./status.md) lists the current major result surface.
- [Reproducibility capsules](./reproducibility-capsules.md) provide replay
  commands, expected metrics, and caveats.
- [Result artifacts index](./result-artifacts-index.md) maps canonical result
  ids to stored run folders.
- [Negative results registry](./negative-results-registry.md) keeps
  falsifications visible alongside successful reproductions.
- [Scientific result quality rubric](./result-quality-rubric.md) records the
  maintainer-facing quality assessment for current flagship surfaces.

For raw artifacts, inspect:

```text
results/<experiment-id>/<run-id>/
```

Each canonical run should include `result.yaml`, `metrics.json`, `report.md`,
review metadata, and input snapshots where strict validation requires them.

## Validation Commands

For a lightweight repository sanity check:

```bash
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
```

For the full Python test suite:

```bash
python3 -m pytest
```

The strict repository validation checks structured scientific memory, required
run artifacts, and cross-references. It is not a substitute for reading the
result caveats.

## Out Of Scope

Do not infer any of the following from a passing replay:

- discovery-level physics claims;
- exact symbolic formulas for pendulum dynamics;
- universal validity outside configured benchmark ranges;
- explanations of particle mass generation;
- a claim that all possible Koide-like formulas are false;
- public-release readiness by itself.

APL's current evidence is useful because it is reproducible, falsifiable, and
reviewable. It should remain scoped to the encoded assumptions, datasets,
validation commands, and limitation wording stored in the repository.

## Reviewer Checklist

1. Run `python3 scripts/reproduce_core_results.py --list` and confirm the
   intended scope.
2. Run the default replay into a temporary output directory.
3. Read `CORE_REPRODUCTION_SUMMARY.md`.
4. Compare key metrics against [reproducibility-capsules.md](./reproducibility-capsules.md).
5. Run strict repository validation.
6. Inspect at least one positive benchmark and one negative-result surface.
7. Record any material drift, unclear limitation wording, or missing artifact
   as a review finding rather than silently rebaselining the result.
