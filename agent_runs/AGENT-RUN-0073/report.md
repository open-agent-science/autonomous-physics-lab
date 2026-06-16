# AGENT-RUN-0073 - Stellar M-L Stage-Control and Split-Sensitivity Audit

**Task:** `TASK-0759`
**Outcome:** `CONTROLS_PASS` (stage confound resolved; margin robust)

## Scope

Controlled audit of the textbook single-alpha mass-luminosity formula
`log L = 3.5 log M` (L0=1) over the `0.5-2.0 M_sun` primary range, on the locally
regenerated, checksum-pinned DEBCat Route 2 rows. Raw `debs.dat` and full rows
are not committed. All policy (main-sequence primary, seeds, 70/30 split, null)
was predeclared in `scripts/run_stellar_ml_stage_control_audit.py` before metrics
were inspected. No fit, no new fetch, no `RESULT-*`/`PRED-*`/`CLAIM-*`.

## Stage Control (the predeclared confound control)

| Slice | Holdout rows | Formula MAE (dex) | Null MAE (dex) | Formula − null |
| --- | ---: | ---: | ---: | ---: |
| Mixed stages (original TASK-0740) | 132 | 0.347 | 0.445 | −0.098 |
| **Main-sequence only** | 65 | **0.185** | 0.332 | **−0.147** |

Restricting to `main_sequence_compatible` rows makes the M-L formula **stronger**
and grows the margin (0.098 → 0.147 dex). Per-stage holdout formula MAE confirms
the confound:

| Stage | Holdout formula MAE (dex) |
| --- | ---: |
| main_sequence_compatible | `0.185` |
| unknown | `0.238` |
| subgiant | `0.308` |
| evolved | `1.709` |

`M^3.5` badly fails for evolved stars (1.71 dex) — exactly as expected for an
off-main-sequence population. The mixed-stage benchmark was diluted by that
contamination; removing it cleans the test.

## Split-Sensitivity (5 seeded system-level 70/30 splits)

null − formula holdout margin per seed: `[0.180, 0.155, 0.127, 0.102, 0.134]`
dex. **Positive on all 5 seeds (`stable_positive`)** — the margin is not a
single-split artifact. Splits are by system (no binary-component leakage).

## Shuffle Control

Real main-sequence holdout margin `+0.147` dex. With the mass-luminosity pairing
permuted (5 seeds), margins are all negative (mean `−0.125`); the real margin
**exceeds every shuffled margin**. The formula captures real M-L structure, not
an artifact.

## Decision

`CONTROLS_PASS`. The three control gaps flagged by `TASK-0753` are resolved:
stage confound (main-sequence restriction), margin robustness (5/5 seeds), and
shuffle controls. Sandbox evidence only — no universal mass-luminosity law and
no canonical result is claimed here.

## Output Routing

- Task verdict: `CONTROLS_PASS`.
- Canonical destination: `agent_runs/AGENT-RUN-0073/metrics.json`, this report, and `docs/reviews/stellar-ml-route2-stage-control-split-audit.md`.
- Review tier: `none`. Gate A: not attempted. Gate B: not applicable.
- Claim impact: none. Knowledge impact: none.
- Publication blocker: one baseline-adequacy step remains (single-alpha vs textbook piecewise) before maintainer-gated Gate A; raw DEBCat stays local-only (Route 2).
