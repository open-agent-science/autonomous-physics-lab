# Nuclear Negative-Result Evidence Card

**Task:** `TASK-0477`  
**Campaign:** Nuclear Mass Surface  
**Evidence class:** review note / communication card  
**Claim ceiling:** no mass-formula claim, no reveal score, no `RESULT-*`,
`PRED-*`, `CLAIM-*`, or `KNOW-*` artifact.

## Short Version

The Nuclear Mass Surface campaign has produced useful negative and
inconclusive memory. The clearest current lessons are:

- `LOCAL-CURVATURE-001` was falsified under a bounded no-leakage prototype.
- The first residual-free F2 high-error-cluster taxonomy was inconclusive
  because the committed `NMD-0002` training slice is too sparse for the
  declared per-cluster leave-one-out test.
- The first Nuclear Research Factory sprint on `NMD-0002` produced no
  shortlist and should be treated as negative / underpowered memory, not as a
  formula path.

These outcomes are useful because they stop attractive residual-feature lanes
from being repeated or promoted without stronger data, controls, and source
boundaries.

## What Failed Or Stopped

| Evidence surface | Review artifact | Verdict | What it blocks |
| --- | --- | --- | --- |
| Local curvature no-leakage prototype | [nuclear-local-curvature-no-leakage-prototype.md](nuclear-local-curvature-no-leakage-prototype.md) | `FALSIFIED` | Reusing `LOCAL-CURVATURE-001` as a positive no-leakage candidate. |
| Residual-free high-error cluster audit | [nuclear-residual-free-high-error-cluster-hypothesis-audit.md](nuclear-residual-free-high-error-cluster-hypothesis-audit.md) | `INCONCLUSIVE` | Treating the first residual-free F2 taxonomy as a near-miss or promotion path. |
| First Research Factory sprint on `NMD-0002` | [nuclear-residual-factory-sprint.md](nuclear-residual-factory-sprint.md) | negative / underpowered memory | Running another broad factory sprint on the same 11-row slice as independent evidence. |
| Training-slice expansion feasibility | [nuclear-training-slice-expansion-feasibility.md](nuclear-training-slice-expansion-feasibility.md) | `BLOCKED_FOR_SOURCE_SAFE_EXPANSION` | Moving post-AME2020 holdout rows into training or fitting before a source-safe `NMD-0003` surface exists. |

## Key Metrics To Preserve

### `LOCAL-CURVATURE-001`

- Lane verdict: `FALSIFIED`.
- Candidate full-known delta MAE: `+0.019599 MeV` relative to the frozen
  baseline, so the candidate regressed the aggregate surface.
- Strongest no-leakage control: `LOCAL-NOLEAK-CTRL-002`.
- Control-minus-candidate margin: `-0.059627 MeV`.
- Subset win-rate: `0.000`.

Interpretation boundary: this falsifies the candidate under the bounded
no-leakage/control implementation. It does not make a broader statement about
all local nuclear structure features.

### Residual-Free F2 Cluster Taxonomy

- Lane verdict: `INCONCLUSIVE`.
- Training-side cluster coverage: only one declared cluster has at least two
  training rows in `NMD-0002`.
- Full-known MAE: baseline `4.4904 MeV`, candidate `5.6923 MeV`,
  matched-random control `4.5924 MeV`, smooth-A control `4.4942 MeV`.
- Candidate full-known regression vs baseline: about `1.2019 MeV`.

Interpretation boundary: the declared taxonomy was no-leakage compliant, but
the current training slice cannot support a meaningful per-cluster LOO
comparison. A future F2 retry needs either a finer predeclared taxonomy or a
larger source-gated training surface.

### First Nuclear Factory Sprint

- Candidate generation: 73 generated, 72 executed.
- Shortlist count: 0.
- Routing summary from the campaign page: 66 negative results, 6 underpowered
  inconclusive results, and 1 data-quality blocker.
- Current campaign blocker: a broader source-gated AME2020 measured-row
  training surface (`NMD-0003`) is needed before another meaningful factory
  sprint.

Interpretation boundary: the sprint demonstrates that the shared Research
Factory can generate and route bounded candidates, but it does not identify a
promotable residual law on `NMD-0002`.

## What Future Agents Should Not Repeat

- Do not reopen `LOCAL-CURVATURE-001` as a positive candidate unless a new
  maintainer-approved task changes the no-leakage implementation surface.
- Do not rerun the same coarse residual-free F2 taxonomy and call sparsity a
  near-miss.
- Do not use post-AME2020 holdout rows as training data.
- Do not run another broad Nuclear factory sprint on `NMD-0002` as if it were
  independent new evidence.
- Do not score live or future measurements outside a reviewed reveal task.

## Safe Follow-Up Shapes

- Source-curate `NMD-0003`: a broader AME2020 measured-row training surface
  with checksums, row semantics, and frozen split boundaries.
- Define a finer residual-free F2 preflight before any scoring.
- Run narrow robustness controls on `NMD-0002` only when framed as sensitivity
  analysis, not as independent evidence.
- Package additional negative/control lanes when the goal is to prevent repeat
  work and preserve failure modes.

## Output Routing

- **Task verdict:** `not_applicable` for this packaging task; it summarizes
  already committed negative and inconclusive evidence.
- **Canonical destination:** this review note under `docs/reviews/`.
- **Review tier:** `none`; no `RESULT-*`, `PRED-*`, `CLAIM-*`, or `KNOW-*`
  artifact is proposed.
- **Gate A status:** not attempted; no result or prediction artifact is
  proposed.
- **Gate B status:** not attempted; this card is not an independent replay.
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change.
- **Limitations:** the card is a concise routing and communication surface, not
  a new deterministic run. It depends on the linked review artifacts for the
  full methods, controls, and metrics.

## Limitation Line

APL has not found a nuclear mass formula, has not scored the frozen prospective
registry against future measurements, and should not describe any Nuclear
residual-feature lane here as discovery-level physics.
