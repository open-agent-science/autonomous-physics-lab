# Materials MD-0001 Band-Gap Split-Fragility Negative Memory

**Task:** `TASK-0646`
**Campaign:** `materials-property-residuals`
**Mode:** planning only (negative-result memory)
**Status:** `BAND_GAP_SPLIT_FRAGILE_DO_NOT_PROMOTE`

## Purpose

This note packages the MD-0001 band-gap evidence as durable, searchable
**negative memory** so that future Materials agents do not re-promote the
composition-aware band-gap "win" as a result, prediction, claim, or factory
target. It consolidates two already-committed audits and the publication
decision that followed them. It reruns no metrics, fetches no rows, creates no
claim, and modifies no dataset values; it only summarises committed evidence
and states the condition that would reopen the band-gap lane.

The companion conclusion — that MD-0001 **formation energy** is split-robust and
is the axis to carry into a wider slice — is recorded in the inputs below and is
not weakened by this note. This memory is specifically about the **band-gap**
axis.

## Evidence Summary

### 1. Null-control audit — modest, borderline, diagnostic

`TASK-0579` (`agent_runs/AGENT-RUN-0058/`,
`docs/reviews/materials-md0001-band-gap-null-control-audit.md`) tested whether
the `cation_group_mean` composition baseline beats a null on the frozen
`TASK-0550` split (train=119, holdout=33), using two deterministic permutation
controls (seed=0, 5000 permutations).

| Predictor | Holdout MAE (eV) |
| --- | ---: |
| global-mean null | `1.371747` |
| cation-group-mean (real) | `1.247901` |
| skill vs null | `0.123846` (~9%) |

| Control (5000 perms) | fraction of permutations ≤ real holdout MAE |
| --- | ---: |
| label shuffle | `0.0428` |
| cation-group shuffle | `0.0378` |

Seed robustness (0/1/2/7): label `0.039–0.043`, group `0.035–0.041`.

Decision: `SIGNAL_SURVIVES_CONTROLS` but **modest** — ≈0.12 eV skill on a small
holdout (n=33), p ≈ 0.04. The audit is a control gate, not a benchmark result;
it explicitly does **not** justify a band-gap PRED/CLAIM, a tuned model, or
material-design guidance, and it states the margin should be re-tested on a
larger or held-out-by-design slice if band gap is ever promoted.

### 2. Split-sensitivity audit — `split_sensitive`

`TASK-0601` (`agent_runs/AGENT-RUN-0066/`,
`docs/reviews/materials-md0001-split-sensitivity-audit.md`) measured whether the
band-gap baseline ordering survives predeclared alternative splits (five
fixed-seed 70/30 random holdouts `0..4`; robustness rule: ≥4/5 seed wins **and**
seeded-mean margin over runner-up larger than the across-seed std).

| baseline | committed holdout MAE | seeded mean MAE | seeded std | seed wins |
| --- | ---: | ---: | ---: | ---: |
| `cation_group_mean` | `1.247901` | `1.207487` | `0.062044` | `3 / 5` |
| `global_median` | `1.349133` | `1.266347` | `0.064471` | `2 / 5` |
| `global_mean` | `1.371747` | `1.321399` | `0.071735` | `0 / 5` |

The committed-holdout "winner" `cation_group_mean` is the **worst** baseline on
the committed validation split, wins only a bare `3 / 5` majority across seeds,
and its margin over the runner-up (`0.058860`) is **smaller** than the
across-seed noise (`0.064471`). Verdict: `INCONCLUSIVE` — the band-gap ordering
is not stable to the choice of holdout. (Formation energy, by contrast, was
`split_robust`: `5 / 5` seed wins with a margin far exceeding split noise.)

### 3. Publication decision — band gap out of next scope

`TASK-0614` (`docs/reviews/materials-md0001-result-or-dataset-publication-decision.md`)
chose route `MD0002_WIDENING_FIRST`: do not promote the small MD-0001 benchmark;
retest the robust formation-energy axis on a larger source-pinned slice. It
records that band gap "stays diagnostic and split-fragile" and "should remain out
of the next promotion or factory scope unless a later larger slice changes the
evidence." `TASK-0566`'s frozen MD-0001 holdout manifest already disallows
RESULT/PRED/CLAIM/benchmark promotion from this slice.

## Why This Is Negative Memory

The band-gap composition signal is **not pure noise** (it survives shuffle
controls at ~4%), but it is **not a settled or promotable benchmark conclusion**:
the effect is small (~0.12 eV / ~9%), measured on a 33-row holdout at p ≈ 0.04,
and its baseline ordering does not survive resampling of that small holdout. The
"win" depends on the particular committed split.

Do **not**, on the strength of MD-0001 band gap:

- promote a band-gap `RESULT-*`, `PRED-*`, `CLAIM`, or knowledge entry;
- tune or fit a band-gap model and treat the holdout edge as validation;
- add a band-gap target to the Materials Research Factory scope;
- issue any material-design, selection, synthesis, device, or biomedical
  guidance (the rows are computed-DFT values only);
- merge band gap with formation energy under one residual metric.

## What Would Reopen The Band-Gap Lane

The band-gap lane reopens only if a **larger or held-out-by-design slice** —
preferably the planned **MD-0002 widening replication** (Materials Project stable
ternary oxides;
`docs/reviews/materials-md0002-wider-replication-slice-plan.md`) — produces a
composition-aware band-gap edge that, under predeclared rules frozen before
residual inspection:

1. **beats the global null**, and
2. **survives** deterministic label and group shuffle controls, and
3. is **split-robust** — wins ≥4/5 seeded holdouts with a seeded-mean margin over
   the runner-up that exceeds the across-seed standard deviation (the same bar
   formation energy already cleared).

A move from computed-DFT band gaps to a citation-backed **experimental** band-gap
axis could also reopen interpretation, but only as a separate provenance axis,
never merged with computed values. Until such evidence exists, MD-0001 band gap
stays diagnostic, split-fragile, and unpromoted.

## Guardrails

- No rows fetched or added; no holdout membership changed; no parameters tuned;
  no metrics rerun. This note restates committed audit numbers only.
- Computed-DFT Materials Project stable-binary-oxide values only; no measured
  band gaps are implied.
- Formation energy and band gap remain separate axes; this note constrains only
  band gap.

## Output Routing Summary

- **Task verdict:** `INCONCLUSIVE` for the band-gap axis (negative/diagnostic
  memory); no scientific claim.
- **Canonical destination:** this review note,
  `docs/reviews/materials-bandgap-split-fragility-negative-memory.md`.
- **Review tier:** `none`; no `RESULT-*` or `PRED-*` artifact is proposed.
- **Gate A status:** not attempted (no rows or metrics produced).
- **Gate B status:** not applicable.
- **Claim impact:** no claim change; band gap explicitly not promoted.
- **Knowledge impact:** no knowledge change; preserved as reviewed negative
  memory.
- **Result artifact impact:** no `results/` artifact created or modified; the
  cited `agent_runs/` evidence is unchanged.
- **Publication blocker:** band-gap promotion remains blocked by small-holdout,
  borderline, and split-fragile evidence plus the frozen MD-0001 manifest;
  reopening requires a larger/by-design slice (preferably MD-0002) that clears
  null, control, and split-robustness gates.
