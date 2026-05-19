# Nuclear Adversarial Stress Synthesis After TASK-0289

**Task:** TASK-0294
**Scope:** committed-review synthesis only
**Inputs reviewed:**

- `docs/reviews/nuclear-shell-axis-stress-scout-001.md`
- `docs/reviews/nuclear-asymmetry-frontier-stress-scout-001.md`
- `docs/reviews/nuclear-scout-lane-synthesis-after-pred-0062.md`
- `docs/reviews/nuclear-midmass-isotope-gap-scout-001.md`
- `docs/reviews/nuclear-prediction-registry-coverage-audit.md`

This synthesis does not run new fits, fetch live measurements, compare future
sources, write prediction registry entries, update claims, or promote any
result. It ranks committed sandbox evidence so maintainers can decide the next
review step without expanding the registry prematurely.

## Decision Summary

| Lane | Best primary delta MAE MeV | Strongest subset signal | Control behavior | Overfit risk | Recommendation |
| --- | ---: | --- | --- | --- | --- |
| Shell-axis | -0.0915 (`STRESS-SHELL-001`) | chain-neighbor -0.825, magic_z -0.388, magic_n -0.292 | sign inversion regresses, shuffle collapses to noise floor, near-null is zero | lowest of the three lanes, but still sandbox-grade | advance to target-batch design only |
| Asymmetry-frontier | -0.0243 (`ASYM-STRESS-001`) | asymmetry>=0.25 -0.126; `ASYM-STRESS-002` reaches -0.143 on the same subset | sign inversion regresses, required quadratic/cubic neighbor overfits, above-0.25 clipped variant is dormant | medium; smaller effect and narrow subset | keep as review surface |
| Mid-mass / isotope-chain | no improving executed candidate | all executed mid-mass features regress or stay null | near-null is zero; rejected ideas preserve overfit reasons | high; primary and target-gap regressions dominate | preserve as negative evidence |

Negative delta means lower retrospective MAE than
`RESULT-0015::model_fitted_semi_empirical` on the cited holdout or subset.
Positive delta means regression. These are retrospective sandbox diagnostics,
not reveal scores.

## Lane Ranking

### 1. Shell-Axis Lane

The shell-axis stress pass is the strongest current Nuclear Mass Surface
review lane. The three re-evaluated candidates preserve the same ordering
reported by the earlier scout synthesis:

| Candidate | Origin | Primary delta MAE MeV | Key subset deltas | Local verdict |
| --- | --- | ---: | --- | --- |
| `STRESS-SHELL-001` | `SHELL-SCOUT-003`, proton-axis Gaussian | -0.091504 | magic_z -0.387579, magic_n -0.291542, heavy -0.087801, chain-neighbor -0.824735 | `PARTIALLY_VALID` |
| `STRESS-SHELL-002` | `SHELL-SCOUT-005`, proton x neutron product | -0.071641 | magic_n -0.411085, heavy -0.089679, chain-neighbor -0.382745 | `PARTIALLY_VALID` |
| `STRESS-SHELL-003` | `SHELL-SCOUT-002`, neutron-axis Gaussian | -0.061969 | magic_n -0.591750, chain-neighbor -0.611142, heavy +0.019771 | `PARTIALLY_VALID` |

The adversarial controls are directionally useful:

- the sign-inverted proton-axis control regresses the primary surface by
  +0.127005 MeV and regresses shell-related subsets;
- the cyclic-shift control collapses to near-zero deltas, with primary
  -0.000060 MeV and all reported subsets near the noise floor;
- the near-null control returns exactly zero deltas.

This pattern makes the shell-axis lane the only lane ready for target-batch
design. That does not authorize registry expansion. The next step should be a
separate target-batch design task that avoids high-repeat registry targets and
defines paired negative controls before any prospective mini-wave.

### 2. Asymmetry-Frontier Lane

The asymmetry-frontier stress pass remains useful, but it is weaker and more
subset-bound than the shell-axis lane.

| Candidate | Origin | Primary delta MAE MeV | Key subset deltas | Local verdict |
| --- | --- | ---: | --- | --- |
| `ASYM-STRESS-001` | `NR-SCOUT-003`, positive asymmetry fraction | -0.024320 | asymmetry>=0.25 -0.126016, n_z_ge_20 -0.052276, mid_mass -0.049755 | `PARTIALLY_VALID` |
| `ASYM-STRESS-002` | `NR-SCOUT-004`, frontier excess after N-Z = 20 | -0.018140 | asymmetry>=0.25 -0.143094, n_z_ge_20 -0.046132, heavy -0.029664 | `PARTIALLY_VALID` |
| `ASYM-STRESS-003` | `NR-SCOUT-005`, matched quadratic/cubic neighbor | +1.368811 | asymmetry>=0.25 +4.812167, n_z_ge_20 +1.970989 | `OVERFITTED` |

The lane passes a narrow adversarial check: sign inversion regresses the
subsets that the positive-asymmetry candidate improves, the required
quadratic/cubic neighbor remains a large negative-control example, and the
near-null control is zero. The clipped-above-0.25 variant is dormant because
the training slice has no row above that threshold, which limits what this
surface can resolve.

Recommendation: keep this lane as a review surface for future analysis, not
as the next target-batch design. It should remain paired with
`ASYM-STRESS-003` / `NR-SCOUT-005` as the required overfit neighbor.

### 3. Mid-Mass / Isotope-Chain Lane

The mid-mass and isotope-chain lane should be preserved as negative evidence.
It is useful because it rules out a family of plausible but fragile feature
ideas.

| Candidate | Primary delta MAE MeV | Intended-surface behavior | Local verdict |
| --- | ---: | --- | --- |
| `MIDMASS-SCOUT-001` | +0.372488 | mid-mass +0.569391 | `OVERFITTED` |
| `MIDMASS-SCOUT-002` | +0.796498 | mid-mass +1.204959 | `OVERFITTED` |
| `MIDMASS-SCOUT-003` | +18.639764 | heavy +34.619944, Z=28 +4.810704, Z=50 +6.791602 | `OVERFITTED` |
| `MIDMASS-SCOUT-004` | +0.256400 | mid-mass +0.387888 | `OVERFITTED` |
| `MIDMASS-SCOUT-005` | +0.000000 | all reported subsets zero | `INCONCLUSIVE` |

This lane should not advance to target-batch design. It should remain
documented so future agents do not rerun the same weak mid-mass Gaussian,
mid-mass-asymmetry, or per-chain centering ideas without a substantially
better pre-registered reason.

## Registry And Coverage Constraints

The registry coverage audit remains the main guardrail against premature
registry expansion:

- `Ni-76` appears in 18 registry entries;
- `Ca-55`, `Ga-85`, and `Zn-80` appear in 14 entries each;
- `frontier-next-row` is the most reused target batch;
- mid-mass coverage remains thin, with only one direct committed registry
  entry in that domain.

The shell-axis stress scout reports that the high-repeat registry targets are
absent from the post-AME2020 holdout, but chain-neighbor subsets are small.
That is a planning constraint, not a failure. Any future shell-axis
target-batch design should avoid simply adding more rows around the already
overused target set unless the task explicitly justifies the reuse and pairs
it with controls.

## Maintainer Decision Surface

| Lane | Decision | Rationale | Next task shape |
| --- | --- | --- | --- |
| Shell-axis | `advance_to_target_batch_design` | strongest primary deltas, coherent subset behavior, sign/shuffle/null controls behave as expected | design targets and controls only; no registry writes |
| Asymmetry-frontier | `keep_as_review_surface` | consistent but smaller and subset-bound; required overfit neighbor remains important | compare against deterministic factory or revisit after shell-axis design |
| Mid-mass / isotope-chain | `preserve_negative_evidence` | all executed candidates regress or stay null; rejected ideas expose overfit paths | no follow-up unless a new task introduces a different evidence basis |

Recommended immediate order:

1. Use `TASK-0295` to compare agent-designed scouts against deterministic
   factory or grid baselines under matched complexity and evidence budgets.
2. Keep `TASK-0296` blocked until maintainers review this synthesis and the
   agent-vs-factory comparison.
3. Keep `TASK-0297` blocked until target-batch design is reviewed and
   explicitly authorizes a small prospective mini-wave.

## Boundary

- No live measurement source was fetched.
- No reveal comparison was scored.
- No `PRED-*` entry was created or edited.
- No claim, knowledge, or canonical result artifact was promoted.
- All decisions are maintainer-facing planning recommendations over committed
  sandbox evidence.

## Verdict

`REVIEW_READY` as a conservative synthesis. The shell-axis lane is the only
lane recommended for target-batch design. The asymmetry-frontier lane should
remain a smaller review surface. The mid-mass / isotope-chain lane should be
kept as preserved negative evidence.
