# Nuclear Magic-Distance Z×N Interaction Control Lane

**Task:** `TASK-0451`
**Agent run:** `AGENT-RUN-0045`
**Campaign:** Nuclear Mass Surface
**Verdict:** `NEGATIVE_RESULT` (custom vocabulary) / `FALSIFIED` (schema) — sandbox-only; no `PRED`/`CLAIM`/`KNOW`/`RESULT` artifact
**Gauntlet:** [`docs/notes/nuclear-controls-first-hypothesis-gauntlet.md`](../notes/nuclear-controls-first-hypothesis-gauntlet.md)

## Scope

This lane tests whether a single residual-free magic-distance Z×N
**interaction** term

```
r_corr = beta * exp(-z_dist^2/8) * exp(-n_dist^2/8)
```

fit on the NMD-0002 training slice beats four declared controls plus
a leave-one-out coefficient-stability check, without regressing the
post-AME2020 primary holdout.

It is the third Nuclear lane to comply with the controls-first
gauntlet (after `TASK-0449` INCONCLUSIVE and `TASK-0450`
NEGATIVE_RESULT) and follows the gauntlet's "one bounded family per
lane" rule.

The interaction form is **distinct from prior additive shell-axis
lanes** (TASK-0310/0316/0320/etc.), which tested `s_z` or `s_n`
individually or their sum. This lane tests the product, which is
non-zero only when both Z *and* N are simultaneously near magic
numbers.

The lane uses a **custom verdict vocabulary** capped at
`SHELL_ADJACENT_DIAGNOSTIC`. Per the TASK-0451 specification, no
registry expansion is authorized regardless of outcome; the shell-axis
post-audit decision (TASK-0333) remains in force.

The lane is sandbox-only. It does not fetch live data, score the
prediction registry, write canonical `RESULT-*` artifacts, modify
claims, or edit knowledge files.

## Candidate (declared before the run)

- Feature: `interaction = exp(-z_dist²/8) * exp(-n_dist²/8)` — a
  closed-form product of two Gaussian shell-proximity terms.
  Inputs: `Z` and `N` only.
- Fit: one scalar `beta` via least squares on the 11-row NMD-0002
  training slice against frozen RESULT-0015 baseline residuals.
- Fitted `beta = +1.7548 MeV` (positive — candidate adds binding-energy
  correction near double-magic regions).

## Aggregate MAE (MeV)

| Surface | baseline | candidate | smooth_a | asymmetry_only | parity_only | matched_degree_random |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `training_lstsq` | 2.8245 | 2.5775 | 2.8920 | 2.7951 | 2.8245 | 2.8244 |
| `primary_holdout` | 4.5526 | 4.4831 | 4.4815 | 4.4860 | 4.4910 | 4.4837 |
| `full_known` | 4.4904 | 4.4204 | 4.4501 | 4.4528 | 4.5121 | 4.4250 |

Numerical deltas vs the candidate on `full_known`:

- `candidate` vs `baseline`: **+0.0700 MeV** (candidate improves but
  far below the 0.25 MeV survival margin).
- `candidate` vs `smooth_a`: +0.0297 MeV.
- `candidate` vs `asymmetry_only`: +0.0467 MeV.
- `candidate` vs `parity_only`: +0.1187 MeV.
- `candidate` vs `matched_degree_random`: +0.0047 MeV (essentially
  tied — the shuffled-degree random control matches the candidate).

## Coefficient Stability (leave-one-out)

- LOO folds: 11.
- mean beta: +1.7710 MeV.
- std beta: 0.4706 MeV (≈ 27% relative variation).
- sign-flip count vs mean: **0** (sign is stable across all 11
  refits).

Coefficient sign is stable, but the candidate's absolute improvement
is too small to clear the survival margin.

## Verdict Rationale

- `full_known` candidate vs baseline: +0.0700 MeV.
- Candidate **fails the 0.25 MeV survival margin** on `full_known` vs
  baseline.

Per the gauntlet's failure condition declared before scoring, this
terminates the verdict at **`NEGATIVE_RESULT`**.

The control comparisons are reported for diagnostic completeness:
matched_degree_random matches the candidate to within 0.005 MeV on
`full_known`, smooth_a matches to 0.030 MeV. Even if the survival
margin were relaxed below 0.25 MeV, the lane would still demote to
`CONTROL_DOMINATED` because matched_degree_random tracks the
candidate almost exactly — the apparent "improvement" carries no
shell-specific information beyond what a randomly-shuffled-degree
feature provides at the same beta.

## Leakage Audit

- Feature uses only `Z` and `N` (via magic-distance from published
  magic-number list). No `A`, baseline residual, error rank,
  candidate-fit residual, source-status flag, or future comparison
  row enters feature construction. ✅
- `beta` is fit by closed-form least squares on the training slice
  only; no candidate-fit residual feeds the controls. ✅
- All four controls (smooth_a, asymmetry_only, parity_only,
  matched_degree_random) share the same fit and evaluation surfaces
  as the candidate. ✅
- Coefficient stability LOO uses only training-row exclusion; no
  candidate-fit residual feeds the stability check. ✅
- Matched_degree_random control fits beta on cyclically-shuffled
  feature values then applies to the unshuffled feature — testing
  whether the candidate's structure carries information beyond chance
  fit at the same beta magnitude. ✅

## Per-Subset Behavior (full_known)

The interaction feature is non-zero only near double-magic regions,
so most subset deltas are small or zero. Per-subset behavior is
preserved in `agent_runs/AGENT-RUN-0045/metrics.json` under
`per_subset_candidate_full_known` for `magic_n`, `magic_z`,
`double_magic`, `light_a_lt_50`, and `neutron_rich`. Sparse subsets
(e.g. `double_magic`) are treated as diagnostic only.

## Why the Lane Fails Cleanly

The product structure `s_z × s_n` is concentrated at double-magic
nuclei. The training slice has very few double-magic rows (NMD-0002
is curated for mid/heavy nuclei, not specifically magic regions), so
the fit cannot identify a strong product coefficient. The full_known
surface has more double-magic rows (in the post-AME2020 holdout), but
the candidate's per-row correction magnitude `beta × interaction` is
dominated by the Gaussian decay away from magic — for most rows the
correction is small, and the aggregate MAE improvement is correspondingly
small (+0.07 MeV).

This is consistent with the shell-axis post-audit decision
(TASK-0333): coefficient stability is fragile, aggregate gains are
real but bounded, and the lane stays diagnostic-only by both the
custom verdict cap AND the actual fit quality.

Two reasonable next moves a maintainer could choose (neither is
authorized by this PR):

1. **Hold the F3 shell-axis-interaction lane closed** at the present
   training-slice sparsity. The shell-axis classification already
   stands as `diagnostic_only`, and this negative result is
   consistent with it.
2. **Try a different functional form** of the interaction (e.g.
   asymmetric Gaussian widths for Z vs N, additive-then-product
   instead of pure product). Any variant must be declared before any
   score, per the gauntlet, and must use a separate PR.

## Output Routing (`docs/result-promotion-protocol.md`)

- **Task verdict:** `NEGATIVE_RESULT` (custom vocabulary) /
  `FALSIFIED` (agent_run.yaml schema). Candidate falsified under
  declared gauntlet.
- **Canonical destination:** this review note plus
  `agent_runs/AGENT-RUN-0045/{agent_run.yaml, metrics.json,
  report.md, limitations.md, preflight.md, review_summary.md}`.
- **Review tier:** `none` (no `RESULT/PRED` tier applies; the agent
  run is sandbox-only).
- **Gate A status:** `not_attempted` (no `RESULT/PRED` artifact
  proposed; custom verdict vocabulary explicitly caps at
  `SHELL_ADJACENT_DIAGNOSTIC` even if the gauntlet had passed).
- **Gate B status:** `not_attempted` (single-run lane).
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change. The shell-axis
  `diagnostic_only` classification under TASK-0333 is preserved and
  reinforced by this negative result.
- **Limitations and blockers:** see "Why the Lane Fails Cleanly". The
  magic-distance-interaction candidate is falsified at the declared
  scope.

## Limitations

- NMD-0002 has 11 training rows; LOO coefficient stability has only
  11 refit folds.
- Frozen RESULT-0015 baseline residuals are retrospective; this is
  not a blind prediction.
- Gaussian width (two-sigma² = 8) is declared before the run and not
  retuned.
- Custom verdict vocabulary caps at `SHELL_ADJACENT_DIAGNOSTIC`; no
  registry expansion is authorized regardless of outcome.
- Shell-axis post-audit decision (TASK-0333) remains in force; this
  lane does not reopen registry expansion.
- The matched_degree_random control uses cyclic-shift on training
  features then applies the fit beta to the true features on
  evaluation; it tests fit-strength under broken Z/N correspondence
  rather than full label-shuffle.

## What This Lane Does Not Do

- It does not add any `PRED-XXXX.yaml` entry.
- It does not score any reveal.
- It does not promote any `CLAIM-*`, `KNOW-*`, `RESULT-*`, or
  canonical hypothesis.
- It does not reuse shell-axis PRED entries, target batches, or
  reveal-scoring machinery.
- It does not relax the no-leakage contract, the freeze protocol,
  the prediction-reveal protocol, the controls-first gauntlet, or
  the shell-axis post-audit decision.
- It does not authorize a follow-up wave of functional-form variants.

## Verdict

`NEGATIVE_RESULT` (custom vocabulary) / `FALSIFIED` (schema). The
single residual-free magic-distance Z×N interaction correction is
falsified at the declared scope: it improves baseline by only 0.07
MeV (well below the 0.25 MeV survival margin), and a matched-degree
random control matches the candidate's full_known MAE to within 0.005
MeV. The shell-axis `diagnostic_only` classification under TASK-0333
and the F3 classification under
`docs/nuclear-residual-feature-no-leakage-contract.md` are preserved
and reinforced. No follow-up is authorized by this PR.
