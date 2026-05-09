# Reproducibility Capsules

This page gives reviewers a compact replay guide for the current major
canonical results. It intentionally covers the strongest public-facing result
surfaces rather than every historical run.

Use these capsules to answer four questions quickly:

- which command reruns the result;
- which inputs define the replay;
- which key metrics should remain stable;
- which caveats prevent overclaiming or byte-for-byte artifact comparison.

Run replay commands with `--output-dir` so canonical files under `results/`
are not rewritten accidentally.

## Capsule Format

Each capsule uses the same fields:

| Field | Meaning |
|---|---|
| Canonical result | Stable result/run identifiers and stored artifact path. |
| Replay command | Command to regenerate the run into a temporary output directory. |
| Main inputs | Example config plus experiment, hypothesis, task, and dataset/challenge inputs. |
| Expected key metrics | Small set of metrics to compare; drift notes split stored artifact metrics from current-source replay metrics when needed. |
| Replay caveats | Known reasons a replay is not a broader scientific claim or byte-for-byte artifact match. |

Generated timestamps, git commit hashes, absolute output paths, and copied-input
paths may differ between a replay and the committed canonical artifact. Compare
scientific metrics and verdict fields first.

Some replay commands intentionally run the current source tree rather than a
frozen historical checkout. When inputs or workflow code have evolved since the
stored artifact, the capsule records both the stored canonical metrics and the
current-source replay drift that a reviewer should expect.

## Selected Capsule Set

The first capsule set follows the "Current Major Results" list in
[Project Status](./status.md):

- `RESULT-0004` — pendulum gauntlet, strongest classical benchmark package;
- `RESULT-0007` — dimensional-analysis validator MVP benchmark;
- `RESULT-0005` — charged-lepton Koide reproduction;
- `RESULT-0006` — historical tau holdout benchmark;
- `RESULT-0009` — neutrino Koide falsification;
- `RESULT-0010` — quark Koide cascade falsification;
- `RESULT-0011` — particle-mass relation falsifier MVP.

Not included in this first flagship set:

- earlier pendulum and damped-oscillator baseline runs, which remain canonical
  but are less central to the current public-facing result surface;
- `RESULT-0012` / `EXP-0010` Muon g-2, which is intentionally framed as a
  high-risk formula-search stress test rather than a public success story.

---

## RESULT-0004 — Pendulum Gauntlet 100

**Canonical result:** `EXP-0001/RUN-0003` (`RESULT-0004`)
**Stored artifacts:** `results/EXP-0001/RUN-0003/`

### Replay Command

```bash
python3 -m physics_lab.cli run examples/pendulum_gauntlet.yaml --output-dir /tmp/apl-replay-pendulum-gauntlet
```

### Main Inputs

- `examples/pendulum_gauntlet.yaml`
- `experiments/EXP-0001-pendulum-formula-discovery.yaml`
- `hypotheses/HYP-0001-pendulum-correction.yaml`
- `tasks/TASK-0010-pendulum-hypothesis-gauntlet-100.yaml`
- exact pendulum reference computed by `physics_lab/workflows/gauntlet.py`

### Expected Key Metrics

Stored `RESULT-0004` artifact:

- `best_verdict`: `VALID_IN_RANGE`
- `best_model_id`: `model_t4_x1`
- candidates evaluated: `100`
- best test mean relative error: about `3.05e-4`
- best test max relative error: about `9.48e-4`
- precision audit confirms residual is model error, not reference-noise error

Current-source replay note:

- current gauntlet replay can select `model_t2_l0`;
- observed current-source test mean relative error: about `1.44e-5`;
- observed current-source test max relative error: about `4.46e-5`.

### Replay Caveats

- Ideal mathematical pendulum only; no damping or driving.
- Verdict applies only to the configured train/test amplitude ranges.
- Near-separatrix diagnostics fail and do not gate the in-range verdict.
- The stored artifact remains the canonical historical `RESULT-0004`; current
  replay drift reflects later gauntlet and hypothesis-source changes, not a
  mutation of the committed result.

---

## RESULT-0007 — Dimensional Analysis Validator MVP

**Canonical result:** `EXP-0006/RUN-0006` (`RESULT-0007`)
**Stored artifacts:** `results/EXP-0006/RUN-0006/`

### Replay Command

```bash
python3 -m physics_lab.cli run examples/dimensional_analysis.yaml --output-dir /tmp/apl-replay-dimensional-analysis
```

### Main Inputs

- `examples/dimensional_analysis.yaml`
- `experiments/EXP-0006-dimensional-analysis-validator.yaml`
- `hypotheses/HYP-0006-dimensional-analysis-validator.yaml`
- `tasks/TASK-0064-implement-dimensional-analysis-validator-mvp.yaml`
- `knowledge/challenge_sets/dimensional_analysis_challenge_set_mvp_50.yaml`

### Expected Key Metrics

Stored `RESULT-0007` artifact:

- `best_verdict`: `VALID`
- challenge items loaded: `50`
- agreement: `49/50`
- agreement fraction: `0.98`
- threshold: `0.90`
- inconclusive count: `0`

Current-source replay note:

- current replay is pinned to the frozen 50-item MVP benchmark scope;
- the live curation surface remains in
  `knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml`;
- live curation additions must not silently change `RESULT-0007` replay
  metrics.

### Replay Caveats

- Dimensional consistency only; numerical correctness is not checked.
- SI and common derived units are covered; natural-unit and Gaussian-unit
  formulas remain outside this MVP scope.
- SUSPICIOUS items with explicit dimensional mismatch are classified `INVALID`.
- The stored artifact and current replay both use the canonical 50-item
  `RESULT-0007` scope; expanded challenge-set curation is follow-on work, not
  a benchmark redefinition.

---

## RESULT-0005 — Charged-Lepton Koide Reproduction

**Canonical result:** `EXP-0004/RUN-0004` (`RESULT-0005`)
**Stored artifacts:** `results/EXP-0004/RUN-0004/`

### Replay Command

```bash
python3 -m physics_lab.cli run examples/koide_charged_lepton.yaml --output-dir /tmp/apl-replay-koide-charged-lepton
```

### Main Inputs

- `examples/koide_charged_lepton.yaml`
- `experiments/EXP-0004-koide-charged-lepton-reproduction.yaml`
- `hypotheses/HYP-0004-koide-charged-lepton-reproduction.yaml`
- `tasks/TASK-0037-reproduce-koide-charged-lepton-relation.yaml`
- `data/particle_masses/charged_leptons.yaml`

### Expected Key Metrics

- `best_verdict`: `VALID`
- observed charged-lepton `Q`: about `0.6666644634145`
- reference `Q`: `2/3`
- absolute difference: about `2.20e-6`
- relative difference: about `3.30e-6`
- propagated `Q` uncertainty: about `5.08e-6`
- z-score: about `0.434`

### Replay Caveats

- Charged-lepton scope only.
- This is a reproduction benchmark, not an explanation of mass generation.
- Agreement does not imply the relation applies to neutrinos, quarks, or
  modified cross-family triplets.

---

## RESULT-0006 — Historical Tau Holdout

**Canonical result:** `EXP-0005/RUN-0005` (`RESULT-0006`)
**Stored artifacts:** `results/EXP-0005/RUN-0005/`

### Replay Command

```bash
python3 -m physics_lab.cli run examples/koide_tau_holdout.yaml --output-dir /tmp/apl-replay-koide-tau-holdout
```

### Main Inputs

- `examples/koide_tau_holdout.yaml`
- `experiments/EXP-0005-koide-tau-holdout.yaml`
- `hypotheses/HYP-0005-koide-tau-holdout.yaml`
- `tasks/TASK-0038-historical-tau-holdout-prediction.yaml`
- `data/particle_masses/charged_leptons.yaml`

### Expected Key Metrics

- `best_verdict`: `VALID_IN_RANGE`
- input particles: `electron,muon`
- holdout particle: `tau`
- predicted tau mass: about `1776.969027` MeV
- measured tau mass: `1776.93` MeV
- absolute difference: about `0.0390` MeV
- z-score against measured uncertainty: about `0.434`

### Replay Caveats

- The exact Koide assumption is an input to the holdout benchmark.
- The result is not an independent physical mechanism or discovery claim.
- Formula residual dominates propagated electron/muon input uncertainty.
- Scope remains charged-lepton only.

---

## RESULT-0009 — Neutrino Koide Falsification

**Canonical result:** `EXP-0007/RUN-0001` (`RESULT-0009`)
**Stored artifacts:** `results/EXP-0007/RUN-0001/`

### Replay Command

```bash
python3 -m physics_lab.cli run examples/koide_neutrino.yaml --output-dir /tmp/apl-replay-koide-neutrino
```

### Main Inputs

- `examples/koide_neutrino.yaml`
- `experiments/EXP-0007-neutrino-koide-consistency.yaml`
- `hypotheses/HYP-0007-neutrino-koide-consistency.yaml`
- `tasks/TASK-0093-neutrino-koide-extension.yaml`
- `data/particle_physics/neutrino_oscillations.yaml`

### Expected Key Metrics

- `best_verdict`: `INVALID`
- normal hierarchy `Q_max`: about `0.583994`
- normal hierarchy gap to `2/3`: about `0.082672`
- normal hierarchy gap: about `70.7` sigma
- inverted hierarchy `Q_max`: about `0.500007`
- inverted hierarchy gap: about `421889` sigma

### Replay Caveats

- Tests the original charged-lepton Koide form only.
- Does not rule out phase-modified, target-shifted, or other neutrino-specific
  extensions.
- Uses encoded PDG 2024 / NuFIT 5.3 oscillation assumptions.

---

## RESULT-0010 — Quark Koide Cascade Falsification

**Canonical result:** `EXP-0008/RUN-0001` (`RESULT-0010`)
**Stored artifacts:** `results/EXP-0008/RUN-0001/`

### Replay Command

```bash
python3 -m physics_lab.cli run examples/koide_quark.yaml --output-dir /tmp/apl-replay-koide-quark
```

### Main Inputs

- `examples/koide_quark.yaml`
- `experiments/EXP-0008-quark-koide-cascade.yaml`
- `hypotheses/HYP-0008-quark-koide-brannen.yaml`
- `tasks/TASK-0088-quark-koide-cascade.yaml`
- `knowledge/particle_physics/quark_masses.yaml`

### Expected Key Metrics

- `best_verdict`: `INVALID`
- up-sector `Q_std`: about `0.848981`
- up-sector gap to `2/3`: about `0.182314` (`159.2` sigma)
- down-sector `Q_std`: about `0.731497`
- down-sector gap to `2/3`: about `0.064830` (`8.8` sigma)

### Replay Caveats

- Quark masses retain mixed renormalization-scale limitations.
- No RGE running is applied to a common scale.
- Only one phase-modified Koide family is tested.
- Does not test quark mixing or GUT-scale mass relations.

---

## RESULT-0011 — Particle-Mass Relation Falsifier MVP

**Canonical result:** `EXP-0009/RUN-0001` (`RESULT-0011`)
**Stored artifacts:** `results/EXP-0009/RUN-0001/`

### Replay Command

```bash
python3 -m physics_lab.cli run examples/particle_mass_falsifier.yaml --output-dir /tmp/apl-replay-particle-mass-falsifier
```

### Main Inputs

- `examples/particle_mass_falsifier.yaml`
- `experiments/EXP-0009-particle-mass-relation-falsifier.yaml`
- `hypotheses/HYP-0009-particle-mass-koide-family-survival.yaml`
- `tasks/TASK-0040-particle-mass-relation-falsifier-mvp.yaml`
- `data/particle_masses/fundamental_fermion_families.yaml`

### Expected Key Metrics

- `best_verdict`: `INVALID`
- evaluated family count: `3`
- evaluated particle count: `9`
- charged-lepton family verdict: `VALID`, `Q ~= 0.666664`
- up-quark family verdict: `INVALID`, `Q ~= 0.848981`
- down-quark family verdict: `INVALID`, `Q ~= 0.731497`
- random-baseline minimum sample count: `10000`
- fixed complexity penalty total: `1.0`

### Replay Caveats

- MVP tests only the standard Koide relation with fixed target `Q = 2/3`.
- Guardrail-compliant within-family charged-fermion triplets only.
- Cross-family triplets, neutrino scenarios, alternate target values, and
  phase extensions remain out of scope.
- Random log-uniform baseline is deterministic calibration, not a physical
  particle-mass prior.

## Reviewer Workflow

For a fast replay spot-check, choose one classical capsule, one validator
capsule, and one particle-mass falsification capsule. A fuller review can run
all seven commands into separate `/tmp/apl-replay-*` directories, then compare
`result.yaml`, `metrics.json`, and `report.md` against the stored artifacts
or documented current-source drift listed above.

Do not promote claims from a successful replay alone. Replays establish that
the current repository can rerun benchmark workflows and expose drift; claim
promotion still follows [claim-promotion-policy.md](./claim-promotion-policy.md).
