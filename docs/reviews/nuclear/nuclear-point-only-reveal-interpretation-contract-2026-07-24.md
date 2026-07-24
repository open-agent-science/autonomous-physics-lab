# Nuclear Point-Only Reveal Interpretation Contract

- **Task:** `TASK-1102`
- **Contract date:** `2026-07-24`
- **Contract verdict:** `POINT_REVEAL_INTERPRETATION_READY`
- **Scope:** interpretation predeclaration for the frozen tier-1 point-only
  registry set `PRED-0069` through `PRED-0072`
- **Claim ceiling:** planning-only; no measurement, score, reveal result,
  scientific claim, or accepted knowledge is produced here

## Purpose And Boundary

This contract fixes the interpretation of a future eligible point-only partial
reveal before any later nuclear measurement source or target-adjacent
information is inspected. It uses only the committed metadata in:

- [`PRED-0069`](../../../prediction_registry/nuclear_masses/PRED-0069.yaml);
- [`PRED-0070`](../../../prediction_registry/nuclear_masses/PRED-0070.yaml);
- [`PRED-0071`](../../../prediction_registry/nuclear_masses/PRED-0071.yaml);
- [`PRED-0072`](../../../prediction_registry/nuclear_masses/PRED-0072.yaml);
- the repository's
  [nuclear prediction reveal protocol](../../nuclear-prediction-reveal-protocol.md);
  and
- the
  [nuclear reveal source readiness checklist](../../nuclear-reveal-source-readiness-checklist.md).

The four registry entries remain byte-unchanged. Their 37 target identities,
central prediction values, `2026-07-05T19:35:00Z` registration timestamp,
source commit `d2ad3d192cce50eaa08d776a39e2ed8c1c712d88`, region assignments,
reveal conditions, and unrevealed eligibility are not reselected, rewritten,
reordered, or re-timed by this task.

The input bytes reviewed for this contract were:

| Registry entry | SHA-256 |
| --- | --- |
| `PRED-0069` | `1f25c093d18fe7076ae4ac8fb49266b0a93089b37379743ce7497658e6d585d9` |
| `PRED-0070` | `04a9072f5f6836d63c623271b9addd1a25ee94b94574e4a378973ff77cc50de1` |
| `PRED-0071` | `a8e685f5c863797ea93e8564dac314ca368b8961d3a15f378ff5451931065eca` |
| `PRED-0072` | `9aa16f6b676b093138471f5f8755d5e90ee385208624e39eb32e64924a17322c` |

## Frozen Candidate And Comparator Family

`PRED-0069` is the sole primary candidate. The complete comparator family is:

1. `PRED-0070`, the frozen DZ10 published-equation variant comparator;
2. `PRED-0071`, the frozen liquid-drop baseline-of-record comparator; and
3. `PRED-0072`, the frozen smooth-`A` GP predeclared control.

Every future headline comparison must use all four entries on exactly the same
eligible target rows. No other registered model, retrospective winner,
post-reveal variant, source-specific refit, or newly selected baseline may
enter the headline. A result against only one comparator is never sufficient
for a headline verdict.

This four-way family is itself historically selected from a wider model
registry and development campaign. Even a favorable result therefore means
only that `PRED-0069` performed best within this frozen four-entry family on
the eligible revealed subset. It must not be described as broad mass-model
superiority, superiority to the historical registry, or evidence that the
model family was selected independently of earlier development evidence.

## Eligible Analysis Set

A future reveal task must first satisfy the source manifest, checksum,
source-timing, deterministic conversion, target matching, and no-peek gates in
the repository protocols. Only rows labeled `ELIGIBLE_MEASURED` may enter this
contract.

For a target to enter the paired set:

- the target identity must be one of the same 37 frozen identities in all four
  registry entries;
- one task-approved measured central value must be available under the pinned
  source manifest;
- any conversion to binding energy in MeV must use the preapproved
  deterministic repository convention;
- all four frozen point predictions must be present; and
- duplicate or ambiguous source rows must be resolved by the source manifest's
  predeclared rule, never by choosing the value that favors a model.

The paired analysis set is the exact intersection satisfying those rules. A
row may not be dropped because of its error, model rank, region, or effect on a
verdict. Unrevealed and ineligible targets stay visible and unchanged with
their exclusion labels.

## Minimum-Information Gate

The first headline interpretation is allowed only when the cumulative eligible
paired set simultaneously has:

- at least **12 unique targets**;
- targets from at least **three of the four frozen regions**;
- at least **three eligible targets in every represented region**; and
- no single region contributing more than **50%** of the eligible paired set.

Counts refer to unique frozen target identities, not repeated measurements.
Rows below this gate may be tabulated as a partial reveal but receive only
`INCONCLUSIVE`; they cannot be used for model-ranking language.

The first cumulative, protocol-approved reveal wave that satisfies this gate
is the sole confirmatory headline look. Earlier underpowered waves do not spend
a test or choose a comparator. After the headline look, later waves must be
reported as dated descriptive updates alongside the original outcome and may
not silently replace, rerun, or improve the headline verdict. A future
sequential-testing amendment would require a new pre-reveal maintainer-reviewed
task.

## Metric And Comparison Hierarchy

For each eligible target \(i\), let \(y_i\) be the task-approved measured
central binding energy, \(p_{0i}\) the frozen `PRED-0069` central value, and
\(p_{ji}\) the central value for comparator \(j\).

1. Compute absolute point errors:
   \[
   a_{0i}=|p_{0i}-y_i|,\qquad a_{ji}=|p_{ji}-y_i|.
   \]
2. Compute the paired absolute-error delta:
   \[
   d_{ji}=a_{0i}-a_{ji}.
   \]
   Negative values favor `PRED-0069`.
3. The primary effect for comparator \(j\) is
   \[
   \Delta_j=\frac{1}{n}\sum_i d_{ji}
            =\operatorname{MAE}_{0069}-\operatorname{MAE}_{j}.
   \]
4. Rank all four entries by pooled MAE on that identical paired set. Rank 1 is
   the lowest MAE.
5. Report pooled MAE, all three \(\Delta_j\) values, the four-way rank, eligible
   target count, target coverage fraction, and region counts.

Calculations use the full committed and converted numeric precision. A pooled
MAE difference with absolute magnitude at most `1e-12 MeV` is an exact
operational tie and is set to zero. Tied models receive the same minimum rank;
later ranks skip the occupied positions. A tie between `PRED-0069` and any
comparator is not a primary win.

## Paired Test And Multiplicity Rule

The confirmatory family contains exactly three one-sided paired hypotheses:

\[
H_{0j}:\Delta_j\ge 0
\quad\text{against}\quad
H_{1j}:\Delta_j<0,
\]

one for each frozen comparator.

Use a paired sign-flip randomization test on the mean \(d_{ji}\):

- when \(n\le20\), enumerate all \(2^n\) sign assignments;
- when \(n>20\), use exactly `100000` sign assignments generated
  deterministically from SHA-256 of
  `TASK-1102|<comparator-id>|<draw-index>|<target-index>`;
- order targets lexicographically by `nuclide_id` before generation;
- assign `+1` when the low bit of the digest's first byte is zero and `-1`
  otherwise;
- for exact enumeration, compute the lower-tail fraction over all \(2^n\)
  assignments;
- for the deterministic sample, compute
  \(p=(1+\#\{\Delta_j^{*}\le\Delta_j\})/(100000+1)\);
- zero paired deltas remain zero under sign flips.

The test is a paired finite-sample stability check whose interpretation
inherits the sign-symmetry assumption; it is not a statement about predictive
intervals. Record the method, target order, number of assignments, test
statistic, and unadjusted p-values.

Control the three-comparator family at one-sided family-wise
\(\alpha=0.05\) using Holm's step-down correction. Sort the three p-values and
compare them in order with `0.05/3`, `0.05/2`, and `0.05`. Stop at the first
non-rejection. No comparator may be removed from the family, and no region,
target, alternate metric, or later reveal wave creates another confirmatory
test family under this contract.

## Pooled And Regional Roles

The pooled paired analysis is the only headline decision surface. For every
represented region, report:

- eligible unique-target count and frozen-region coverage fraction;
- each model's regional MAE and rank;
- each `PRED-0069` paired mean delta; and
- the complete per-target absolute-error table.

A regional MAE or rank is descriptive only. A region with fewer than three
eligible targets is table-only. Regional results may expose concentration,
sign reversals, or failure modes, but they may neither rescue a failed pooled
verdict nor upgrade an inconclusive pooled verdict. No region may be selected
after reveal as the new headline.

## Exact Future Scientific Verdict Mapping

Apply these rules in order and return exactly one of the four scientific
verdicts for the sole headline look:

1. **`INCONCLUSIVE`** — source/no-peek eligibility does not authorize scoring,
   the minimum-information gate is not met, or all three \(\Delta_j<0\) but
   none of the three hypotheses survives Holm correction.
2. **`INVALID`** — after the minimum-information gate passes, any
   \(\Delta_j\ge0\), including an operational tie. This means the primary
   candidate did not beat the complete frozen comparator family on pooled MAE.
3. **`PARTIALLY_VALID`** — all three \(\Delta_j<0\), `PRED-0069` is the unique
   pooled rank-1 entry, and at least one but fewer than all three hypotheses
   survives Holm correction.
4. **`VALID`** — all three \(\Delta_j<0\), `PRED-0069` is the unique pooled
   rank-1 entry, and all three hypotheses survive Holm correction.

These are bounded point-error verdicts only. `VALID` does not validate the full
37-target list when coverage is partial, does not validate predictive
uncertainty, and does not authorize claim promotion.

## Point-Only Prohibitions

This contract and any reveal task using it may report measured central values,
frozen central predictions, signed errors, absolute errors, MAE, paired
absolute-error deltas, counts, coverage fractions, randomization p-values, and
rank.

It must not report or imply:

- interval coverage or an interval-bearing score;
- calibration, sharpness, posterior uncertainty, or a calibrated error band;
- sigma-based wording or standardized-residual claims;
- uncertainty-normalized residuals;
- prediction-readiness or interval-readiness;
- a successful prediction before an admissible reveal is scored;
- a validated nuclear-mass model, new mass law, or new physics; or
- broad superiority beyond the frozen four-entry family and eligible subset.

Measurement-source uncertainty fields may be preserved as source metadata, but
they do not weight, normalize, filter, or alter the point-only metric.

## Fail-Closed Conditions

The interpretation freeze must stop without a readiness verdict if any primary
hierarchy, information threshold, comparator role, multiplicity rule, or
point-only boundary cannot be fixed before source contact.

If any target-adjacent reveal-source information enters a contract-authoring
session, that session is retired from source selection, target matching,
scoring, and interpretation. No exposed content is recorded. The task follows
the repository contamination path and requires a clean-session retry; exposure
never authorizes a retrospective contract.

## Zero-Source Attestation

For `TASK-1102`, no external nuclear measurement source was searched, fetched,
opened, cited, summarized, target-matched, or inspected. No search-result
snippet, later evaluation metadata, target measured-status flag, measured
value, or target-adjacent source information was used. Work was limited to the
four committed frozen registry entries and the repository protocols named
above.

No prediction value, registry timestamp, source commit, target identity,
region, or reveal condition was changed. No source manifest, measurement
dataset, comparison table, reveal result, `RESULT`, `CLAIM`, or `KNOW` artifact
was created.

## Future Handoff And Output Routing

A future qualifying official metadata signal may route only to the standing
pipeline's independent metadata-only source-manifest decision. If that gate is
approved, separate reviewed tasks must pin source bytes or immutable references
and checksums, freeze a registry snapshot, complete target matching and the
no-peek audit, and only then authorize the one headline comparison under this
contract.

- **Canonical destination:** this dated planning contract under
  `docs/reviews/nuclear/`.
- **Future destination:** a task-specific source manifest, registry snapshot,
  eligibility ledger, and reveal review note created only by separately
  authorized tasks.
- **Review tier:** not applicable; no scientific result or prediction entry is
  produced.
- **Gate A:** not attempted.
- **Gate B:** not attempted.
- **Prediction impact:** none; `PRED-0069` through `PRED-0072` remain unchanged
  and registered.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Publication blocker:** no admissible source is asserted or contacted here;
  source manifest approval, checksums, deterministic matching, no-peek review,
  minimum information, and the separate scoring authorization remain required.

## Task Output Record

- **Task id:** `TASK-1102`
- **Input references:** the four committed registry entries and the two
  repository nuclear reveal protocols listed above
- **Method:** pre-reveal deterministic decision-contract freeze
- **Code reference:** none; planning-only documentation
- **Metrics:** future pooled MAE, four-way rank, and three paired
  absolute-error deltas with a single Holm-corrected sign-flip family
- **Limitations:** point-only; one selected four-model family; at most 37 frozen
  targets across four regions; no source, measurement, score, or scientific
  result in this task
- **Verdict:** `POINT_REVEAL_INTERPRETATION_READY`
