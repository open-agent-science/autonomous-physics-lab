# Nuclear Prediction Registry Status After PRED-0062

**Task:** TASK-0274
**Registry scope:** `prediction_registry/nuclear_masses/PRED-0001.yaml` through `PRED-0062.yaml`
**Coverage audit:** `docs/reviews/nuclear-prediction-registry-coverage-audit.md`
**Machine summary:** `data/nuclear_masses/nuclear_prediction_registry_coverage.yaml`
**Synthetic reveal dry-run:** `docs/reviews/nuclear-prediction-synthetic-reveal-dry-run.md`
**Live external fetch allowed:** `false`

This note summarizes the Nuclear Mass Surface evidence state after the selected
feature-term registry wave. It does not reveal, score, validate, or promote any
prediction. The committed `PRED-0001` through `PRED-0062` entries are frozen
prospective records awaiting future maintainer-reviewed measurement comparison.

## Evidence Layers

| Layer | Current artifact | Interpretation boundary |
| --- | --- | --- |
| Baseline benchmark | `EXP-0012/RUN-0001` and `RESULT-0015` | Frozen measured-slice residual benchmark used as the reference surface for later sandbox and registry work. |
| Sandbox residual evidence | `AGENT-RUN-0005`, `AGENT-RUN-0007`, `AGENT-RUN-0008`, and later scout lanes | Reviewable sandbox evidence only; inconclusive or bounded outcomes stay visible and do not create claims. |
| Factory slates | `docs/reviews/nuclear-prediction-factory-slate-001.md` and `docs/reviews/nuclear-prediction-factory-slate-002-feature-terms.md` | Candidate-generation and selection evidence. Draft `PRED` ids in these slates are sandbox ids unless copied into the registry by a reviewed task. |
| Selected registry waves | `PRED-0001` through `PRED-0062` | Frozen prospective entries for later reveal comparison. They are not canonical results, claims, or accepted knowledge. |
| Coverage audit | `docs/reviews/nuclear-prediction-registry-coverage-audit.md` | Pre-reveal map of source lanes, transform classes, target-batch pressure, repeated targets, and reveal-readiness flags. |
| Synthetic reveal dry-run | `docs/reviews/nuclear-prediction-synthetic-reveal-dry-run.md` | Toy-source workflow check for future reveal plumbing. It uses fabricated values and provides no scientific score. |
| Reveal protocol | `docs/nuclear-prediction-reveal-protocol.md` | Required future boundary for any real measurement-source comparison. |

## Registry Snapshot

The current coverage audit reports:

| Metric | Value |
| --- | ---: |
| Committed registry entries | 54 |
| Target rows | 213 |
| Lowest id | `PRED-0001` |
| Highest id | `PRED-0062` |
| Quantity | `mass_excess_mev` only |
| `live_external_fetch_allowed` values | `false` only |

The numeric id range has known gaps: `PRED-0031` through `PRED-0036`,
`PRED-0039`, and `PRED-0040`. These gaps are registry-selection history, not
validation failures.

## Source-Lane Summary

| Source task | Entries | Notes |
| --- | ---: | --- |
| `TASK-0205` | 20 | First broad prospective registry wave. |
| `TASK-0265` | 12 | Selected feature-term factory wave, `PRED-0051` through `PRED-0062`. |
| `TASK-0251` | 10 | Selected coefficient-transform factory wave, `PRED-0041` through `PRED-0050`. |
| `TASK-0228` through `TASK-0232` and `TASK-0236` | 12 total | Smaller manual control families for smooth/reference, pairing, shell, neutron-excess, isotope-chain, and minimal-complexity behavior. |

The source lanes now cover baseline-style controls, selected coefficient
transforms, selected feature terms, and manual control families. This is a
prospective setup for future reveal work, not evidence that any entry has
matched later measurements.

## Coverage And Reveal-Risk Signals

The registry coverage audit marks all major planning domains as covered except
mid-mass, which remains thin:

| Domain | Entries | Planning interpretation |
| --- | ---: | --- |
| Neutron-rich / asymmetry | 23 | Broadest coverage, with first-wave, manual-control, and selected feature-term entries. |
| Frontier | 18 | Strongly represented and should not be the default target for more frozen entries. |
| Odd-even / pairing | 18 | Well represented through first-wave and control entries. |
| Shell / magic | 16 | Covered by N=50/N=82 rows, manual shell controls, and selected feature terms. |
| Isotope-chain | 6 | Present but small enough to report separately in future reveal work. |
| Mid-mass | 1 | Thin; future work should treat this as a coverage gap, not a failure. |

Repeated-target pressure is high for a few rows. `Ni-76` appears in 18 entries,
while `Ca-55`, `Ga-85`, and `Zn-80` appear in 14 each. Those repeats are useful
for sign-paired and model-paired comparisons, but they can distort future
partial-reveal interpretation if treated as independent target breadth.

`PRED-0059` through `PRED-0062` close the current registry range with a
nickel-isotope-chain feature-term quartet:

| Entry | Model family | Target batch | Coverage flags |
| --- | --- | --- | --- |
| `PRED-0059` | neutron-axis shell reviewed coefficients | `nickel-isotope-chain` | high-reuse target nuclide, feature-term selected wave |
| `PRED-0060` | neutron-axis shell sign-inverted control | `nickel-isotope-chain` | high-reuse target nuclide, feature-term selected wave |
| `PRED-0061` | asymmetric neutron-excess plus control | `nickel-isotope-chain` | high-reuse target nuclide, feature-term selected wave |
| `PRED-0062` | asymmetric neutron-excess minus control | `nickel-isotope-chain` | high-reuse target nuclide, feature-term selected wave |

These entries are useful paired controls for a future reveal, but they remain
pre-reveal records with `uncertainty_mev: null` and no current measurement
comparison.

## Contributor Guidance

Near-term contributors should prefer:

- registry coverage review and source-state audit;
- synthetic reveal dry-run maintenance;
- future reveal-task design using `docs/nuclear-prediction-reveal-protocol.md`;
- sandbox-only scout lanes that do not write new `PRED-*` entries;
- limitation notes that make repeated targets, thin domains, and partial reveal
  risks easy to review.

Contributors should avoid:

- adding more frozen registry variants before the coverage audit and synthetic
  reveal dry-run are reviewed;
- fetching live measurements or computing reveal scores outside a canonical
  reveal task;
- editing frozen prediction values;
- describing registry entries as validated predictions;
- promoting claims, results, or knowledge from pre-reveal registry state.

## Current Verdict

`PRED-0001` through `PRED-0062` form a stronger prospective setup than the
earlier registry state because the entries now include broad first-wave rows,
selected coefficient-transform controls, selected feature-term controls,
coverage audit evidence, and synthetic reveal plumbing.

The scientific verdict is still pre-reveal and conservative: `INCONCLUSIVE`
with respect to later measurements until a maintainer-reviewed reveal task pins
measurement sources, records checksums, performs a no-peek audit, and compares
eligible frozen rows without rewriting registry inputs.
