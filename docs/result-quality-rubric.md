# Scientific Result Quality Rubric

## Purpose

This rubric helps maintainers decide how confidently a result can be used in
status docs, release reviews, public summaries, and follow-up planning.

It is decision support, not a pseudo-objective score. A result with a higher
assessment is not automatically a public claim, and a lower assessment is not a
failure. Negative and inconclusive results can be high quality when they are
reproducible, falsifiable, and honestly scoped.

## Assessment Levels

Use these levels per dimension:

| Level | Meaning |
| --- | --- |
| Strong | Evidence is explicit, reproducible, and review-ready for its stated scope. |
| Moderate | Evidence is useful but has a known limitation, drift risk, or narrower review surface. |
| Weak | Evidence is preliminary, hard to reproduce, underspecified, or too easy to overclaim. |
| Not applicable | The dimension does not apply to this result type. |

Do not average levels into a single number. The weakest material dimension
should guide public-facing wording.

## Dimensions

### Reproducibility

Ask whether a reviewer can rerun or inspect the result without guessing.

Strong signals:

- committed `RESULT-*` artifacts exist;
- replay command or capsule exists;
- inputs are version-controlled;
- validation passes without local-only assumptions.

Weak signals:

- result depends on mutable external state;
- replay rewrites canonical artifacts accidentally;
- current-source replay materially drifts without explanation.

### Falsifiability

Ask whether the result could have failed under the stated method.

Strong signals:

- pass and fail conditions are explicit;
- negative results are preserved;
- out-of-scope failure modes are named.

Weak signals:

- method only demonstrates agreement after the target is known;
- no baseline or rejection condition exists;
- failure cases are hidden or converted into success wording.

### Baseline Strength

Ask whether the comparison target is meaningful for the claim ceiling.

Strong signals:

- baseline is deterministic, documented, and hard enough to matter;
- null or negative-control comparison exists;
- random or simple-fit baselines are calibrated where relevant.

Weak signals:

- result is compared only to no model at all;
- baseline is weaker than the intended public story;
- candidate search space is broad but not penalized or bounded.

### Uncertainty Handling

Ask whether numerical uncertainty and data scope are treated explicitly.

Strong signals:

- propagated uncertainty or tolerance is reported where relevant;
- deterministic numerical precision is audited or bounded;
- dataset, unit-system, or sampled-range limits are visible.

Weak signals:

- exact-looking numbers are shown without tolerance;
- statistical or numerical uncertainty is absent where it matters;
- known dataset limitations are not connected to the verdict.

### Overclaim Risk

Ask how easily the result could be misread as stronger than it is.

Strong signals:

- claim ceiling is explicit;
- public wording forbids discovery, exactness, or universal-scope language;
- limitations appear near the result summary, not only in a deep appendix.

Weak signals:

- result invites "AI solved physics" or "new physics" framing;
- benchmark success is phrased as explanation;
- stress-test or exploratory output is presented as a flagship success.

## First-Pass Flagship Assessment

This table summarizes the current major result surface. It should be revised
when a result is rebaselined, replay-hardened, or promoted through maintainer
review.

| Result | Reproducibility | Falsifiability | Baseline Strength | Uncertainty Handling | Overclaim Risk | Maintainer Use |
| --- | --- | --- | --- | --- | --- | --- |
| `RESULT-0004` Pendulum Gauntlet 100 | Moderate | Strong | Strong | Moderate | Moderate | Strong benchmark story, but replay drift must stay visible until frozen or rebaselined. |
| `RESULT-0007` Dimensional Analysis Validator MVP | Strong | Strong | Moderate | Moderate | Low | Packaging-ready as a narrow 50-item validator benchmark. |
| `RESULT-0005` Charged-Lepton Koide Reproduction | Strong | Moderate | Moderate | Strong | Moderate | Useful scoped reproduction; never explanation evidence. |
| `RESULT-0006` Historical Tau Holdout | Strong | Strong | Moderate | Strong | Moderate | Stronger than a pure fit because it is holdout-style, but still charged-lepton-only. |
| `RESULT-0009` Neutrino Koide Falsification | Strong | Strong | Strong | Strong | Low | High-quality negative result within encoded oscillation assumptions. |
| `RESULT-0010` Quark Koide Cascade Falsification | Moderate | Strong | Strong | Moderate | Low | Useful negative result; dataset and scale assumptions should stay adjacent to summaries. |
| `RESULT-0011` Particle-Mass Relation Falsifier MVP | Strong | Strong | Strong | Strong | Moderate | Strong falsifier workflow for one fixed target; does not rule out all mass-relation formulas. |
| `RESULT-0012` Muon g-2 Formula-Search Stress Test | Moderate | Moderate | Weak | Moderate | High | Keep as guarded stress test only, not public success evidence. |

## Release-Readiness Guidance

For public or release-facing summaries:

- Lead with results whose weakest material dimension is `Moderate` or better.
- Keep at least one high-quality negative result visible beside successful
  reproductions.
- Treat any result with `High` overclaim risk as internal, stress-test, or
  heavily caveated evidence.
- Do not promote sandbox-only autonomous runs, proposals, or exploratory notes
  without a later canonical result and claim-promotion review.
- When a result has known replay drift, state whether the intended path is
  frozen replay, explicit versioning, or reviewed rebaselining.
