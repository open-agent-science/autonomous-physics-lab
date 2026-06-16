# Stellar M-L Route 2 Baseline-Adequacy Audit (TASK-0762)

**Task:** `TASK-0762`
**Campaign:** Textbook Formula Audit (Stellar mass-luminosity)
**Agent run:** `agent_runs/AGENT-RUN-0074/`
**Verdict:** `PIECEWISE_OR_FITTED_BASELINE_MATERIALLY_BETTER` — the textbook single
`M^3.5` is **not** the adequate baseline for this slice; a steeper exponent
(alpha ~= 4-4.5) fits better. Sandbox evidence only; no universal-law claim, no
`RESULT-*`.
**Scope note:** dated control audit, not a live board or RESULT promotion.

## Method (predeclared, no-peek)

`scripts/run_stellar_ml_baseline_adequacy.py` scores three fixed-intercept (L0=1)
exponents on the same frozen, main-sequence-restricted DEBCat holdout used by
TASK-0759: textbook single `3.5`, textbook piecewise mid-mass `4.0`, and a
train-fitted exponent (least squares on the train lane only). Raw `debs.dat` not
committed (Route 2).

## Result (main-sequence holdout, 65 rows; per-mass-band null MAE 0.332 dex)

| Baseline | alpha | Holdout MAE (dex) | vs textbook 3.5 |
| --- | ---: | ---: | ---: |
| textbook single | 3.5 | 0.185 | — |
| textbook piecewise mid-mass | 4.0 | 0.138 | −0.047 |
| train-fitted | **4.53** | **0.120** | **−0.065** |

All three beat the null, so a power-law M-L relation holds robustly. But `M^3.5`
is the **weakest**: the fitted `4.53` (and the piecewise `4.0`) are materially
better by `0.065` dex, beyond the `~0.04` dex across-seed split noise from
TASK-0759. So `single_alpha_adequate = false`.

## Interpretation

For `0.5-2.0 M_sun` main-sequence stars the mass-luminosity relation is
**steeper than the textbook single `M^3.5`** (best-fit alpha ~= 4.5). This is
consistent with standard stellar astrophysics: the classic piecewise M-L uses
alpha ~= 4 in the `0.43-2 M_sun` branch, while `M^3.5` is the higher-mass branch.
The benchmark thus (a) confirms a robust power-law signal and (b) has the
discriminating power to reject the wrong exponent.

## Updated Gate A Readiness (completes the TASK-0753 / TASK-0759 checklist)

| Criterion | State |
| --- | --- |
| Confounder control (stage) | ✅ (TASK-0759) |
| Margin robustness (split-sensitivity + shuffle) | ✅ (TASK-0759) |
| Baseline adequacy | ✅ resolved — single `3.5` inadequate; fitted/piecewise alpha ~= 4-4.5 is the adequate baseline |
| Gate A RESULT packaging | maintainer-only (not attempted) |

## Recommendation

Stellar M-L is now **control-complete** and ready for a maintainer-gated Gate A
**reusable-dataset + benchmark RESULT candidate**, with the headline reframed:

- **what it is**: a stage-controlled, split-stable, control-surviving
  main-sequence M-L benchmark on the pinned DEBCat slice, showing the relation is
  a power law that is **steeper (alpha ~= 4.5) than the textbook single `M^3.5`**
  on `0.5-2.0 M_sun`;
- **what it is not**: not a universal mass-luminosity law, not a stellar-evolution
  claim, not a "M^3.5 validated" statement (it is the opposite — `M^3.5` is
  rejected as best-fit for this slice).

Optional future refinement (not blocking): a full stage-aware piecewise baseline
across the wider mass range. Gate A packaging and any claim status remain
maintainer-only.

## Limitations

- 65 main-sequence holdout rows (small); catalogue-level luminosity provenance.
- Fitted alpha is a single fixed-intercept fit on this slice, not a global M-L law.
- Sandbox-only; raw DEBCat stays local-only (Route 2); cite DEBCat (Southworth 2015) and the original sources on any publication.

## Output-Routing Summary

- **Task verdict:** `PIECEWISE_OR_FITTED_BASELINE_MATERIALLY_BETTER`; Stellar M-L control-complete, ready for maintainer Gate A with reframed headline.
- **Canonical destination:** this dated audit + `agent_runs/AGENT-RUN-0074/`; `TASK-0762` → `REVIEW_READY`.
- **Review tier:** `none`; no `RESULT-*`/`PRED-*` promoted.
- **Gate A status:** ready (controls complete), maintainer-gated. **Gate B:** not applicable.
- **Claim impact:** none. **Knowledge impact:** none.
- **Recommendation:** maintainer-gated Gate A with the steeper-than-3.5, scope-limited reusable-dataset/benchmark framing.
