# Nuclear Scout Evidence Card

## Purpose

This card packages the current Nuclear Mass Surface scout evidence for
maintainer review and future contributor orientation. It is a compact index,
not a new benchmark, reveal, prediction registry wave, result artifact, claim,
or public launch draft.

No future-measurement reveal has happened. No nuclear mass law is claimed.
All scout rows below are sandbox or retrospective diagnostic evidence unless a
future maintainer-reviewed reveal task says otherwise.

## Evidence Layers

| Layer | Main artifacts | Current interpretation |
| --- | --- | --- |
| Baseline evidence | `EXP-0012`, `RESULT-0015`, `docs/results/nuclear-mass-baseline-summary.md` | Frozen measured-slice residual benchmark. It defines the baseline surface for later sandbox and registry work. |
| Sandbox scout evidence | `docs/reviews/nuclear-scout-lane-synthesis-after-pred-0062.md`, `docs/reviews/nuclear-shell-axis-stress-scout-001.md`, `docs/reviews/nuclear-neutron-rich-variant-scout-001.md` | Retrospective stress evidence only. Small sub-MeV improvements are review signals, not accepted physics. |
| Negative scout evidence | `docs/reviews/nuclear-midmass-isotope-gap-scout-001.md` and overfit controls in the scout reviews | Useful failure evidence. It narrows which feature families should not be promoted. |
| Prospective registry entries | `prediction_registry/nuclear_masses/PRED-0001.yaml` through `PRED-0062.yaml` and `docs/reviews/nuclear-prediction-registry-status-after-pred-0062.md` | Frozen prospective records awaiting a future source-pinned reveal. They are not current measured successes. |
| Reveal plumbing | `docs/nuclear-prediction-reveal-protocol.md`, `docs/reviews/nuclear-prediction-synthetic-reveal-dry-run.md` | Workflow guardrails only. The synthetic reveal values are fabricated toy rows and provide no scientific score. |

## Compact Leaderboard

Negative delta MAE means lower retrospective MAE than the frozen
`RESULT-0015::model_fitted_semi_empirical` baseline on the reported holdout or
subset. Positive delta MAE means regression. The values are retrospective
sandbox diagnostics, not prospective reveal scores.

| Candidate | Lane | Primary delta MAE MeV | Best cited subset signal | Local verdict | Caveat |
| --- | --- | ---: | --- | --- | --- |
| `SHELL-SCOUT-003` | shell-axis | -0.0915 | magic_z -0.388, magic_n -0.292, heavy -0.088 | `PARTIALLY_VALID` | Strongest small shell-axis signal; still fitted on an 11-row residual slice and needs future reviewed target design before any registry use. |
| `SHELL-SCOUT-005` | shell-axis cross-check | -0.0716 | magic_n -0.411, heavy -0.090 | `PARTIALLY_VALID` | Useful non-additive cross-check; should be reviewed with `SHELL-SCOUT-003`, not promoted alone. |
| `NR-SCOUT-003` | asymmetry frontier | -0.0243 | asymmetry >= 0.25: -0.126 | `PARTIALLY_VALID` | Smaller, subset-scoped signal; required negative neighbor is `NR-SCOUT-005`. |
| `MIDMASS-SCOUT-001` | mid-mass gap | +0.3725 | mid-mass +0.569 | `OVERFITTED` | Regresses the target gap; useful as a warning against naive mid-mass Gaussian corrections. |
| `MIDMASS-SCOUT-002` | mid-mass plus asymmetry | +0.7965 | mid-mass +1.205 | `OVERFITTED` | Regression is concentrated in the intended mid-mass band. |
| `MIDMASS-SCOUT-003` | isotope-chain slope | +18.6398 | heavy +34.620, Z=28 +4.811, Z=50 +6.792 | `OVERFITTED` | Strong negative result; per-Z centering does not generalize from the tiny training slice. |
| `MIDMASS-SCOUT-004` | mid-mass shell fall-off | +0.2564 | mid-mass +0.388 | `OVERFITTED` | Plausible-looking gated shell-distance feature still regresses the intended band. |
| `MIDMASS-SCOUT-005` | near-null control | +0.0000 | all reported subsets +0.000 | `INCONCLUSIVE` | Sanity control; confirms the lane preserved null behavior. |

## Why The Negative Mid-Mass Result Matters

The mid-mass and isotope-chain lane is useful because it prevents the campaign
from treating every plausible feature as a future candidate. All executed
mid-mass features either regress the primary holdout or return a null result.
The largest failure, `MIDMASS-SCOUT-003`, shows that per-chain centering fitted
on the 11-row residual slice can break badly on the larger retrospective
surface.

This is not a project failure. It is evidence that the review loop is doing
its job:

- plausible feature families can fail visibly;
- rejected candidates preserve overfit reasons before execution;
- null controls stay visible;
- future contributor effort can focus on stronger surfaces instead of
  repeating weak mid-mass or isotope-chain ideas.

## Recommended Internal Reading Order

1. `docs/results/nuclear-mass-baseline-summary.md` for the baseline surface.
2. `docs/reviews/nuclear-prediction-registry-status-after-pred-0062.md` for
   frozen prospective registry context.
3. `docs/reviews/nuclear-scout-lane-synthesis-after-pred-0062.md` for the
   first combined scout ranking.
4. `docs/reviews/nuclear-shell-axis-stress-scout-001.md` for adversarial
   shell-axis stress behavior.
5. `docs/reviews/nuclear-midmass-isotope-gap-scout-001.md` for the negative
   mid-mass and isotope-chain lane.

## Contributor Route

Near-term contributor work should stay inside conservative review surfaces:

- adversarial review of the shell-axis pair before any registry expansion;
- asymmetry-frontier stress review with `NR-SCOUT-005` retained as a required
  negative control;
- source-readiness and no-peek review before any real reveal comparison;
- evidence packaging that keeps baseline, sandbox, negative, and prospective
  registry layers separate.

Do not use this card to add `PRED-*` entries, fetch live measurement sources,
score future measurements, promote claims, or write public-facing discovery
copy.

## Wording Boundary

Allowed internal wording:

- "small retrospective shell-axis scout signal"
- "sandbox-only adversarial stress evidence"
- "useful negative mid-mass and isotope-chain result"
- "prospective registry entries awaiting future source-pinned reveal"
- "no future-measurement reveal yet"

Forbidden wording:

- "found a nuclear mass formula"
- "proved shell-aware corrections"
- "validated future predictions"
- "confirmed a nuclear mass law"
- "reveal success"

## Current Verdict

The compact evidence state is conservative:

- baseline evidence is reviewable and frozen;
- shell-axis sandbox evidence is the strongest current follow-up surface;
- asymmetry-frontier evidence is smaller and must keep its overfit control;
- naive mid-mass and isotope-chain features are negative evidence;
- registry entries remain prospective until a future maintainer-reviewed
  source-pinned reveal.

No claim, knowledge entry, canonical result, prediction registry entry, or
future-measurement comparison is created by this card.
