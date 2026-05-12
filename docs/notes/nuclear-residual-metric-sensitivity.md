# Nuclear Residual Metric Sensitivity

**Task:** `TASK-0203`
**Status:** sandbox-only audit note; advisory for follow-up nuclear lanes
**Claim boundary:** no promotion, no canonical result update

This note captures how aggregate and subset metrics behave on the reviewed
post-AME2020 holdout (`AGENT-RUN-0008`) and on the pinned-slice split family
(`AGENT-RUN-0006`). It is a companion to
[../reviews/post-ame2020-timesplit-failure-analysis.md](../reviews/post-ame2020-timesplit-failure-analysis.md),
focused on metric mechanics rather than candidate-by-candidate review.

## Why Aggregate MAE Is Not Enough

The post-AME2020 primary holdout contains 295 rows with the following subset
overlap (rows belong to multiple subsets):

- `neutron_rich_delta_ge_20`: 116
- `proton_rich_n_lt_z`: 28
- `heavy_a_ge_100`: 153
- `near_magic`: 116
- `magic_any`: 18
- `odd_a`: 156

`neutron_rich` rows outnumber `proton_rich` rows by roughly 8.5x. A candidate
that trades error between these two subsets can show a large aggregate MAE win
while regressing the smaller subset. This is the observed behavior of
`HYP-PROPOSAL-0022`:

- improves `neutron_rich_delta_ge_20` by `-0.61 MeV`;
- regresses `proton_rich_n_lt_z` by `+0.79 MeV`;
- aggregate primary delta MAE: `-0.39 MeV`.

The aggregate win is real and reproducible, but it is a one-way trade against
the smaller subset, not a uniform correction. Aggregate-only reporting would
hide this.

## Why HYP-PROPOSAL-0020 Looks Identical To The Baseline

Active feature counts on the 295-row primary holdout for `HYP-PROPOSAL-0020`:

- `magic_both`: 0
- `heavy_double_magic`: 0

The candidate cannot change any row's prediction on this surface. Its delta MAE
is `0.0000 MeV` not because the family is null in principle, but because no row
qualifies for either feature. This is a metric-mechanics observation: a
candidate with dormant region features is statistically indistinguishable from
the baseline on the surface where it is dormant.

The lesson for follow-up batches is that feature activation counts must be
reported on every benchmark surface, otherwise the experimenter cannot tell the
difference between "candidate adds nothing" and "candidate never fired".

## Why HYP-PROPOSAL-0021 Looks Like A Constant Odd-A Shift

For `HYP-PROPOSAL-0021` on the post-AME2020 primary holdout:

- `magic_both`: 0
- `heavy_double_magic`: 0
- `odd_a`: 156

The shell-style features are dormant; only the odd-A indicator fires. With
`c3 = -1.4559 MeV`, the candidate is mathematically equivalent on this surface
to:

```text
prediction = baseline_prediction + c3   if odd_a else baseline_prediction
```

That is a constant 1.46 MeV shift downward on odd-A rows. Whether this is good
or bad depends entirely on the sign of the baseline mean error on odd-A rows.
On this surface, baseline mean error on `odd_a` is `+0.59 MeV` (positive), so a
`-1.46 MeV` shift overshoots the mean error and increases MAE.

The takeaway for future nuclear lanes: when only the simplest carrier term of a
multi-term candidate is active on the holdout, the candidate is being tested as
that simple term, with the rest of the family quiet. Reports must say so.

## Uncertainty-Normalized Error Behavior

`mean_abs_uncertainty_normalized_error` on the post-AME2020 primary surface:

- frozen baseline: `257.32`
- `HYP-PROPOSAL-0020`: `257.32`
- `HYP-PROPOSAL-0021`: `266.31`
- `HYP-PROPOSAL-0022`: `239.39`
- AME2020 source-table sanity column: `6.63`

The baseline MAE is around `4.55 MeV` and the typical AME2020 row uncertainty
is in the tens of keV. Uncertainty-normalized error is therefore dominated by
the model bias, not the experimental uncertainty. A `0.4 MeV` aggregate MAE
change still leaves uncertainty-normalized error in the hundreds.

This metric is useful for two narrow purposes:

- detecting whether any candidate approaches the AME2020 source-table baseline
  (it does not, by two orders of magnitude);
- making low-uncertainty heavy rows (where `sigma <= 0.05 MeV`) visible in
  worst-case lists. The `Sb-133` row with `sigma = 0.011 MeV` has an
  uncertainty-normalized error above `1400` on every model in the run, which
  raw MAE would understate.

## Split-Sensitivity Versus Time-Split Surface

The `AGENT-RUN-0006` 48-split enumeration of `HYP-PROPOSAL-0021` produced a
spread of pinned-slice delta MAE values:

- mean delta MAE: `-0.058 MeV`
- median delta MAE: `-0.135 MeV`
- best: `-0.744 MeV`
- worst: `+0.948 MeV`

The post-AME2020 primary delta MAE is `+0.080 MeV`. This is consistent with the
same-shape distribution: it is just above the mean and median, and well inside
the worst case. Two practical points follow:

- A new candidate that lands inside the same-shape spread on the time-split
  surface is producing no out-of-sample information; it is being reproduced
  by the existing pinned-slice variance.
- A candidate that lands far outside the same-shape spread on the time-split
  surface needs an explicit explanation. Either the candidate generalizes
  better than the pinned slice predicted, or the time-split surface contains
  systematic baseline bias that the candidate is absorbing. Both readings
  matter for follow-up classification.

## Worst-Case Residuals As A Subset Probe

Top absolute residuals on the post-AME2020 primary holdout (baseline):

- `Ga-84` (Z=31, N=53, A=84): `37.64 MeV`
- `In-132` (Z=49, N=83, A=132): `17.87 MeV`
- `In-131` (Z=49, N=82, A=131): `17.52 MeV`
- `In-134` (Z=49, N=85, A=134): `17.16 MeV`
- `In-133` (Z=49, N=84, A=133): `16.59 MeV`

This list concentrates near the N=82 shell closure for Z=49 indium isotopes. A
candidate that claims shell-aware behavior should produce a measurable effect
on these rows; a candidate that does not is not testing the shell story on the
post-AME2020 surface, regardless of what its aggregate metrics show. This is
the row-level companion to the feature-activation point above.

## Practical Reporting Implications

For TASK-0200..TASK-0202 and any future nuclear sandbox lane, the metric
mechanics above translate into the following reporting habits:

- Always report per-subset MAE and delta MAE; never aggregate-only.
- Always report feature-activation counts per subset; never assume features
  fired just because the candidate was defined.
- Report the top 5 absolute residuals on the post-AME2020 primary surface and
  whether the candidate's region features fired on each.
- Report uncertainty-normalized error on primary, neutron-rich, and near-magic
  subsets; otherwise heavy low-uncertainty residuals stay invisible.
- Place every retrospective time-split delta MAE next to the same-shape
  pinned-slice spread, so a candidate cannot look surprising or unsurprising
  without context.
- Treat one-way subset trades (improving a large subset while regressing a
  small one) as negative-control behavior unless an explicit physical reason
  is provided in the proposal.

## Limitations

- Subset counts on a 295-row holdout are small. `proton_rich_n_lt_z` has 28
  rows; delta MAE swings of `~0.4 MeV` per subset are within plausible
  per-sample noise.
- The metrics in this note are descriptive. They are not loss functions for a
  new fit and must not be used to retune candidate coefficients on the
  post-AME2020 holdout.
- This note does not introduce new metrics; it interprets the existing
  `metrics.json` schema with the goal of making subset behavior visible.

## Status

Sandbox-only audit note. No claim, knowledge artifact, or canonical result is
updated by this document. Cite as advisory context for nuclear sandbox lanes
during private-agent validation cycles.
