# Post-AME2020 Time-Split Failure-Mode Analysis

**Task:** `TASK-0203`
**Scope:** retrospective analysis of `AGENT-RUN-0008` post-AME2020 time-split
metrics, with context from `AGENT-RUN-0006` split-sensitivity replay
**Status:** sandbox-only audit; no claim, canonical result, or knowledge
promotion
**Claim boundary:** advisory; this review must not be cited as a candidate
promotion or as new physics

## Purpose

`TASK-0197` produced retrospective time-split evidence on the reviewed row-level
post-AME2020 holdout (`AGENT-RUN-0008`). The result is `INCONCLUSIVE`:

- `HYP-PROPOSAL-0021` regresses the 295-row primary MAE by `+0.0796 MeV`.
- `HYP-PROPOSAL-0022`, the prior overfit/negative-control family, improves the
  primary MAE by `-0.3886 MeV`.

This review explains *why* the candidates behave as they do, what failure modes
the post-AME2020 surface exposes, and what TASK-0200..TASK-0202 must record so
that future sandbox lanes inherit the right guardrails.

It does not run a new sandbox batch. All numbers below are taken from committed
inputs:

- `agent_runs/AGENT-RUN-0008/metrics.json`
- `agent_runs/AGENT-RUN-0006/report.md`
- `hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0021-shell-dual-heavy-anchor-odd-a.yaml`
- `hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0022-quadratic-asymmetry-refinement.yaml`
- `docs/nuclear-mass-robustness-gate.md`
- `docs/reviews/post-ame2020-time-split-benchmark-result.md`

## Subset-Level Picture

Delta MAE = candidate MAE - frozen baseline MAE. Negative is improvement.

| Subset | n | Baseline MAE (MeV) | HYP-0021 delta MAE | HYP-0022 delta MAE |
| --- | ---: | ---: | ---: | ---: |
| `primary` | 295 | 4.5526 | +0.0796 | -0.3886 |
| `ame2020_measured_comparison` | 240 | 4.4613 | +0.0586 | -0.3418 |
| `ame2020_extrapolated_comparison` | 55 | 4.9510 | +0.1714 | -0.5926 |
| `magic_any` | 18 | 5.5115 | +0.5662 | -0.2988 |
| `near_magic` | 116 | 4.7246 | +0.3652 | -0.3580 |
| `neutron_rich_delta_ge_20` | 116 | 5.8642 | +0.3887 | -0.6052 |
| `proton_rich_n_lt_z` | 28 | 1.9412 | -0.0894 | +0.7910 |
| `heavy_a_ge_100` | 153 | 5.3063 | -0.0148 | -0.4938 |
| `odd_a` | 156 | 4.6549 | +0.1506 | -0.4220 |

Two patterns dominate:

1. The retrospective surface is much harder than the pinned-slice surface.
   Frozen-baseline primary MAE is `4.55 MeV` here, compared with the much
   smaller per-row residuals seen on `NMD-0002`. The candidate gains observed
   on the structured pinned holdouts do not survive at this scale.
2. The two candidates behave in opposite directions on most subsets, with
   exactly one inversion: `proton_rich_n_lt_z`. That subset is small (`n=28`)
   and has the smallest baseline MAE (`1.94 MeV`); both candidates trade error
   between the abundant heavy/neutron-rich rows and this thin proton-rich slice.

## Why `HYP-PROPOSAL-0021` Does Not Become Robust

The candidate formula is

```text
r_corr = c1 * m2 + c2 * mh + c3 * oa
```

with fitted `c1 = +0.4848`, `c2 = +7.9689`, `c3 = -1.4559` MeV from the frozen
`NMD-0002` residual surface. The post-AME2020 activation counts are
`{magic_both: 0, heavy_double_magic: 0, odd_a: 156}` out of 295 rows.

Consequences:

- Both shell-style features (`m2`, `mh`) are dormant on every primary post-AME2020
  row. The candidate behaves like a pure odd-A intercept shift `+c3` on
  odd-A rows and identity elsewhere.
- The odd-A coefficient was fit on the small pinned slice. A `-1.46 MeV` global
  shift on odd-A rows is a strong constant; it improves only the small
  `proton_rich_n_lt_z` subset (where baseline mean error is negative) and
  regresses every other subset where baseline mean error is positive.
- The shell motivation in the proposal is therefore non-falsifiable on this
  surface: features that never fire cannot produce evidence for or against the
  shell-aware story. The remaining odd-A component is the only thing being
  tested, and it fails as a uniform correction.

This is the dominant failure mode. It is not a complexity problem or a
parameter-count problem. It is a *feature-activation* problem: a region-specific
correction term must actually fire on representative holdout rows, otherwise
the time-split surface only tests its incidental side terms.

The original split-sensitivity replay (`AGENT-RUN-0006`) already showed the
candidate is split-sensitive on the pinned slice: improved MAE on `28/48`,
regressed on `13/48`, mean delta MAE `-0.058 MeV`, worst delta MAE
`+0.948 MeV`, pilot split rank `18/48`. The post-AME2020 surface adds external
pressure: when the shell-style features stop firing, the candidate cannot
recover.

## Why The Negative Control Looks Strong Overall

`HYP-PROPOSAL-0022` is

```text
r_corr = a * I + b * I^2,  I = (N - Z) / A
```

with fitted `a = -14.0269`, `b = +77.0628` MeV. Activation is dense
(`{isospin_asymmetry: 292, isospin_asymmetry_sq: 292}` of 295 rows).

The structured pinned-slice review marked this family `OVERFITTED` and kept it
as a negative control because it improved one attractive subset while
threatening heavy-region collapse. On the post-AME2020 surface, two facts
change the picture without changing the verdict:

- The post-AME2020 holdout is heavily neutron-rich and heavy
  (`neutron_rich_delta_ge_20: 116/295`, `heavy_a_ge_100: 153/295`). A quadratic
  asymmetry correction has direct mathematical purchase here because baseline
  mean error grows in `I`.
- The proton-rich slice (`proton_rich_n_lt_z`) is small (`n=28`), the only place
  the family regresses (`+0.79 MeV`), and is masked by 8.5x more neutron-rich
  rows in the aggregate.

So the aggregate improvement comes from a region where the *shape* of the
baseline residual is approximately polynomial in `I`. This is a useful negative
signal — it confirms that a flexible empirical residual can absorb structural
baseline bias on a time-split surface — but it is not new asymmetry physics.

Specifically, the gate forbids promotion here for three independent reasons:

- The family was registered as a negative control before the time-split
  surface was reviewed. Treating its retrospective improvement as evidence
  would re-introduce the cherry-pick risk the gate is designed to eliminate.
- The candidate regresses the proton-rich subset by `+0.79 MeV` while
  improving the dominant subsets. Aggregate-MAE promotion would silently hide
  this subset failure.
- Frozen-baseline mean error on the post-AME2020 primary surface is
  `+0.685 MeV`; a sufficiently flexible global shift can absorb part of that
  systematic without resolving any structural failure mode.

The honest reading is that the negative control demonstrates *baseline
mis-specification on the neutron-rich tail*, not a discovered correction.

## Subset Failure Modes On The Post-AME2020 Surface

The four largest baseline residuals on the primary 295-row holdout are:

- `Ga-84` (`Z=31, N=53`): `|err| = 37.64 MeV`. Light-medium, neutron-rich
  (`delta = N-Z = 22`), not magic.
- `In-132` (`Z=49, N=83`): `|err| = 17.87 MeV`. N=82 magic plus one,
  Z=49 (one below magic).
- `In-131` (`Z=49, N=82`): `|err| = 17.52 MeV`. Right on the N=82 shell.
- `In-134` (`Z=49, N=85`): `|err| = 17.16 MeV`. Just above N=82.

Pattern: the dominant baseline failures cluster near the N=82 shell closure for
Z=49 (`In`) and around the same region for Z=51 (`Sb`), with one outlier in the
light-medium neutron-rich region (`Ga-84`). None of these rows trigger the
strict double-magic features in HYP-PROPOSAL-0020 or HYP-PROPOSAL-0021. The
shell-aware features therefore miss exactly the rows where shell structure is
most likely to matter, because they require both `Z` and `N` to be canonical
magic numbers simultaneously.

This is the most important takeaway for follow-up batches: a residual family
that is motivated by shell physics but only fires on strict double-magic rows
will be silent on essentially the entire reviewed time-split surface.

## Why `HYP-PROPOSAL-0020` Ties The Baseline

`HYP-PROPOSAL-0020` uses only `magic_both` and `heavy_double_magic`. Both fire
zero times on the 295-row primary holdout, so the candidate is numerically
identical to the frozen baseline on every primary row (delta MAE = 0.0000).
This is consistent and benign; the candidate adds no leverage because no row
qualifies. It also means HYP-0020 produces no diagnostic information on this
surface and cannot be used as evidence for or against the shell-aware family.

## Cross-Run Consistency With Split-Sensitivity Context

The `AGENT-RUN-0006` 48-split same-shape enumeration of HYP-PROPOSAL-0021 found
a small mean improvement on the pinned NMD-0002 slice with a wide spread:

- improved on 28 of 48 splits;
- regressed on 13 of 48 splits;
- mean delta MAE `-0.058 MeV`, median `-0.135 MeV`;
- best delta `-0.744 MeV`, worst delta `+0.948 MeV`;
- pilot split rank `18/48`.

The post-AME2020 surface lands at `+0.080 MeV`, which is within roughly
`0.14 MeV` of the same-shape median delta and well inside the same-shape worst
delta. The retrospective time-split result therefore does not contradict the
split-sensitivity picture; both are saying the same thing — the candidate is
not stable enough to expand into a follow-up batch as a positive lead.

## What This Means For Promotion

Using `docs/nuclear-mass-robustness-gate.md`:

- `HYP-PROPOSAL-0021`: gate outcome remains `REQUIRES_TIME_SPLIT_REPLAY` or
  stricter. The time-split surface has now been evaluated and the candidate
  regresses it. Combined with same-shape split sensitivity, the appropriate
  posture is no follow-up batch promotion without a different hypothesis
  family. `BLOCK_PROMOTION` applies to any claim or canonical result update.
- `HYP-PROPOSAL-0022`: gate outcome remains `ALLOW_ONLY_AS_NEGATIVE_CONTROL`.
  Its aggregate retrospective improvement does not satisfy the leakage,
  complexity, or negative-control conditions for promotion.

No candidate is upgraded by this review. No prediction is registered. This
document does not authorize a new sandbox batch on its own; it documents the
criteria that the next batches must satisfy.

## Mandatory Checks For TASK-0200, TASK-0201, And TASK-0202

The next nuclear sandbox batches must produce evidence packages that make the
failure modes above visible by construction. The checks below are mandatory in
the sense of `docs/nuclear-mass-robustness-gate.md`: a follow-up PR that omits
them should be treated as incomplete for sandbox follow-up, not just for
claim-bearing work.

1. **Feature-activation disclosure.** For every region-specific feature
   (magic switches, shell indicators, odd-even masks, neutron-rich masks,
   chain-specific terms), report the activation count and fraction on every
   reported subset, including the post-AME2020 primary holdout. A feature
   that fires zero times on a subset must be flagged explicitly; aggregate
   metrics for that subset then describe the carrier terms only.
2. **Subset MAE table with proton-rich and near-magic rows.** Report at least
   `primary`, `magic_any`, `near_magic`, `neutron_rich_delta_ge_20`,
   `proton_rich_n_lt_z`, `heavy_a_ge_100`, and `odd_a` for the post-AME2020
   surface. Delta MAE versus the frozen baseline must be present per subset.
   No aggregate-only summaries.
3. **Worst-case region call-out.** Identify the top 5 absolute residuals on
   the post-AME2020 primary surface, including `Z`, `N`, `A`, observed value,
   predicted value, and whether the candidate's region features fired. The
   In-128..134 and Sb-133 cluster is a known stress region and must be
   reported when present.
4. **Negative-control parity.** Every executed candidate must be compared
   against at least one prior negative control on the same subsets. If the
   negative control improves a subset where the proposed candidate does not,
   that fact must be preserved in the report rather than aggregated away.
5. **Split-sensitivity context.** The structured holdout split sensitivity
   (per `AGENT-RUN-0006`-style replay or an equivalent same-shape enumeration)
   must be reported with improved, regressed, tied, mean delta MAE, median
   delta MAE, and worst delta MAE. A candidate whose post-AME2020 delta MAE
   lies far outside the same-shape distribution must explain why.
6. **Activation versus inference separation.** When a region feature is
   dormant on the post-AME2020 surface, the candidate's reported MAE on that
   surface is *not* evidence for the region story. Reports must say so
   explicitly, in the limitations section, and must not claim shell-aware,
   pairing-aware, or neutron-rich behavior on subsets where the relevant
   feature did not fire.
7. **Uncertainty-normalized error where available.** Report the
   `mean_abs_uncertainty_normalized_error` per subset for at least the
   primary, neutron-rich, and near-magic subsets. A very small AME uncertainty
   on heavy/neutron-rich rows (often `<= 0.05 MeV`) means raw MAE understates
   the disagreement.
8. **Leakage and selection disclosure.** Every candidate must state whether
   it was selected before or after the time-split surface was visible, and
   whether its hypothesis family was registered before or after the failure
   modes above were documented. Post-`TASK-0203` selections must treat the
   In/Sb N=82 cluster and the proton-rich subset as known stress regions, not
   as new discoveries.
9. **No retrospective subset framing.** A subset improvement on a
   retrospective surface is not a prediction. Reports must not phrase
   post-AME2020 subset wins as prospective predictions, even when they look
   strong; the gate's `retrospective-not-blind-prediction` requirement
   applies per subset, not only at the aggregate level.
10. **Robustness-gate footer.** Every follow-up PR must include the gate
    section template at the bottom of
    `docs/nuclear-mass-robustness-gate.md`, with one of
    `ALLOW_BOUNDED_SANDBOX_FOLLOWUP`, `ALLOW_ONLY_AS_NEGATIVE_CONTROL`,
    `REQUIRES_TIME_SPLIT_REPLAY`, or `BLOCK_PROMOTION` as the outcome.

These checks are not new policies; they are the auditable form of the existing
gate, sharpened by the post-AME2020 evidence. Where the gate already names a
check, this document specifies the minimum reporting granularity that the
TASK-0200..TASK-0202 batches must meet.

## Limitations

- This analysis is retrospective. It uses committed metrics and the existing
  robustness gate; it does not run a new sandbox batch, generate new
  hypotheses, or fit new coefficients.
- The post-AME2020 surface contains 295 primary rows. Subset counts down to
  `n = 28` (proton-rich) carry real statistical noise. Subset deltas of
  `0.1 MeV` should not be over-interpreted.
- The negative-control improvement on the aggregate retrospective surface is a
  diagnostic about baseline residual shape. It is not promotion-grade evidence
  and must not be cited as such.
- This review does not classify TASK-0200..TASK-0202 candidates in advance;
  the mandatory-checks section is the auditable shape future PRs must satisfy.

## Verdict

`INCONCLUSIVE` overall, consistent with `AGENT-RUN-0008`.

- `HYP-PROPOSAL-0021`: gate outcome `BLOCK_PROMOTION` for claim or canonical
  result; sandbox-only evidence remains valuable as a documented failure
  mode (shell features dormant on the time-split surface).
- `HYP-PROPOSAL-0022`: gate outcome `ALLOW_ONLY_AS_NEGATIVE_CONTROL`. Its
  aggregate improvement is preserved as diagnostic pressure on the
  frozen-baseline residual shape, not as a candidate promotion.

No claim, knowledge artifact, or canonical result is updated by this audit.
