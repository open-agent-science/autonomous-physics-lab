# Nuclear Agent Scouts Vs Factory Baseline Comparison

**Task:** TASK-0295
**Method:** deterministic tabulation of committed artifacts only
**Script:** `scripts/compare_nuclear_agent_vs_factory_scouts.py`
**Factory inputs:** `docs/reviews/nuclear-prediction-factory-slate-001.md`, `docs/reviews/nuclear-prediction-factory-slate-002-feature-terms.md`, `docs/reviews/nuclear-prediction-factory-slate-002-feature-terms-ranking.md`
**Agent inputs:** `agent_runs/AGENT-RUN-0015/metrics.json`, `agent_runs/AGENT-RUN-0016/metrics.json`, `agent_runs/AGENT-RUN-0017/metrics.json`

This comparison does not fetch live measurements, score a future reveal,
register predictions, update claims, or promote any sandbox result.

## Matched Comparison Protocol

The comparison treats the deterministic factory and agent scout paths as two
different review instruments rather than as direct competitors on one scalar
score.

Matched axes:

- candidate count and coverage breadth;
- rejected-candidate handling;
- complexity and control discipline;
- primary and subset delta distributions where committed metrics exist;
- negative-control quality;
- maintainer review usefulness.

Important asymmetry: the factory slates are pre-reveal generation and ranking
surfaces, so their committed metrics are candidate deltas from the frozen
baseline and heuristic flags. The agent scouts include retrospective
post-AME2020 stress deltas from committed metrics. Those retrospective rows are
stress evidence, not future-measurement reveal evidence.

## Aggregate Summary

| Path | Candidate surface | Executed/scored surface | Rejections before execution | Review flags or verdicts | Primary delta range |
| --- | ---: | ---: | ---: | --- | --- |
| Deterministic factory slates | 84 candidates | no holdout scoring in slate reviews | 0 | 24 advisory flags | n/a |
| Agent scout lanes | 26 generated ideas | 17 executed candidates | 9 | INCONCLUSIVE: 6, OVERFITTED: 5, PARTIALLY_VALID: 6 | -0.091504 to 18.639764 MeV |

Agent primary-delta sign counts across executed candidates:

- negative primary delta: 6
- zero primary delta: 4
- positive primary delta: 7

Factory advisory-flag counts across the two reviewed slates:

- `EXTREME_SENSITIVITY`: 13
- `ALL_ZERO_DELTA`: 3
- `REDUNDANT_TARGET_BATCH`: 8

## Factory Slate Details

| Slate | Candidates | Advisory flags | Extreme sensitivity | All-zero | Redundant target batch | Largest max abs delta MeV |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| slate-001 coefficient transforms | 36 | 10 | 6 | 0 | 4 | 13.187000 |
| slate-002 feature terms | 48 | 14 | 7 | 3 | 4 | 64.182491 |

Factory value:

- broad, deterministic coverage of coefficient transforms, feature terms,
  sign-paired controls, near-null controls, and reusable target batches;
- reproducible sensitivity ranking before any registry selection;
- clear separation between sandbox `PRED-9xxx` candidates and committed
  registry entries.

Factory limitations:

- the slate reviews do not score candidates on the post-AME2020 stress
  surface;
- candidate generation does not itself reject row-memorizing or duplicate
  hypothesis shapes before they appear in the slate;
- high candidate count increases repeated-target and reviewer-load pressure
  unless a later triage step narrows the surface.

## Agent Scout Details

| Agent run | Lane | Generated | Executed | Rejected | Best primary delta MeV | Worst primary delta MeV | Verdicts |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| AGENT-RUN-0016 | shell_axis_adversarial_stress_scout | 9 | 6 | 3 | -0.091504 | 0.127005 | INCONCLUSIVE: 2, PARTIALLY_VALID: 4 |
| AGENT-RUN-0017 | asymmetry_frontier_adversarial_stress_scout | 9 | 6 | 3 | -0.024320 | 1.368811 | INCONCLUSIVE: 3, OVERFITTED: 1, PARTIALLY_VALID: 2 |
| AGENT-RUN-0015 | midmass_isotope_gap_scout | 8 | 5 | 3 | 0.000000 | 18.639764 | INCONCLUSIVE: 1, OVERFITTED: 4 |

Rejected-candidate reason classes:

- duplicate_search_or_overlap: 2, extra_free_knob: 6, row_memorization_or_per-row_fit: 1

Agent value:

- rejects several bad hypothesis shapes before execution, including
  row-memorizing, free-knob, duplicate-search, and degree-of-freedom inflation
  cases;
- preserves negative results instead of hiding them, especially the mid-mass
  and isotope-chain failures;
- adds adversarial controls around the strongest small signals, including
  sign-inverted, shuffled, clipped, and near-null checks;
- produces a more reviewable explanation of why a lane should continue,
  pause, or stay automated.

Agent limitations:

- all scout coefficients are fit on an 11-row residual slice;
- the post-AME2020 surface is retrospective stress evidence, not a strict
  blind future-measurement reveal;
- sub-MeV improvements remain sandbox triage signals;
- small subset deltas can be fragile, especially chain-neighbor and
  high-asymmetry subsets.

## Operating Split

Keep the following work in deterministic factory/search machinery:

- broad sign-paired candidate generation;
- coefficient-transform and feature-term coverage sweeps;
- target-batch reuse and sensitivity ranking;
- near-null and all-zero sanity controls;
- reproducible slate regeneration into sandbox scratch paths.

Use agent-driven hypothesis triage for:

- pre-execution rejection of row-memorizing or high-free-knob ideas;
- adversarial stress passes around a small number of promising families;
- synthesis of negative results and limitations for maintainer review;
- deciding which factory slates deserve registry-selection review and which
  should remain sandbox diagnostics.

## Verdict

`MIXED`.

The committed evidence does not support a claim that agent scouts are generally
superior to deterministic factory generation. The factory path is better for
wide, reproducible candidate coverage. The agent path adds value as a
review-and-falsification layer: it narrows factory breadth, rejects fragile
hypothesis forms, designs adversarial controls, and preserves negative
outcomes in a form maintainers can act on.

No claim, canonical result, knowledge entry, prediction registry entry, or
future-measurement comparison is promoted by this comparison.
