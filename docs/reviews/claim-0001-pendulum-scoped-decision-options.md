# CLAIM-0001 Pendulum Scoped Decision Options

- Task: `TASK-0796`
- Claim: `CLAIM-0001`
- Claim status at review: `DRAFT`
- Decision authority: maintainer Gate C
- Task verdict: `MAINTAINER_DECISION_READY`

## Purpose And Boundary

This note prepares conservative maintainer options for `CLAIM-0001`. It does
not change the claim, create or modify a result, promote knowledge, rerun
formula discovery, or treat approximation accuracy as a physics discovery.

The current claim combines a qualitative ideal-pendulum statement with
benchmark evidence about finite-range approximation quality:

> For an ideal mathematical pendulum, the period increases with amplitude and
> cannot be captured exactly by the small-angle approximation alone.

The repository can support a tightly scoped version of that statement. It
cannot support an exact new formula, all-amplitude validity, a real-laboratory
pendulum conclusion, or an exhaustive formula-search conclusion.

## Evidence And Exact Supported Scope

| Evidence | Scope | Relevant outcome |
| --- | --- | --- |
| `RESULT-0001` | train `0.0100`-`1.1002` rad; test `1.1080`-`1.5708` rad | `VALID_IN_RANGE`; best-model test mean relative error `6.3495e-4`, maximum `1.8887e-3`; verification passed. |
| `RESULT-0003` | train `0.0100`-`1.1002` rad; test `1.1080`-`1.5708` rad | `VALID_IN_RANGE`; theory-aware candidate test mean relative error `1.1458e-4`, maximum `4.1721e-4`; verification passed. |
| `RESULT-0004` | train `0.0100`-`1.1002` rad; test `1.1080`-`1.5708` rad | `VALID_IN_RANGE`; 100-candidate gauntlet best-model test mean relative error `3.0525e-4`, maximum `9.4806e-4`; verification passed. |
| `RESULT-0013` | train `0.0100`-`2.1683` rad; test `2.1839`-`3.1000` rad | Strongest positive result: `VALID_IN_RANGE`; `model_asymptotic_refined` test mean relative error `2.7519e-5`, maximum `4.4038e-5`; listed in-scope checks passed. |
| `RESULT-0017` | train `0.0100`-`2.0985` rad; test `2.1135`-`3.0000` rad | Negative boundary evidence: `OVERFITTED`; test mean relative error `4.3473e-3`, maximum `2.1261e-2`. Gate B replay compared 878 metrics with maximum drift `6.8923e-13` under tolerance `1.0e-9`; verdict unchanged. |

The narrowest numeric support available for maintainer wording is therefore:

- system: ideal mathematical pendulum, without damping or driving;
- reference: exact elliptic-integral period ratio used by `EXP-0001`;
- sampled amplitude envelope: `0.01 <= theta <= 3.10` rad across the
  `RESULT-0013` train and test partitions;
- held-out approximation tolerance: maximum relative error
  `4.4037820702786206e-05` for `model_asymptotic_refined` on
  `2.1838693467336685 <= theta <= 3.10` rad;
- interpretation: range-limited approximation evidence, not exact equality
  and not validity at the separatrix `theta = pi`.

The tolerance belongs to the named approximation and held-out range. It must
not be presented as a tolerance on the broader qualitative law or transferred
to another model or amplitude interval.

## Unsupported Wording

Do not ratify wording that implies any of the following:

- APL discovered an exact or novel pendulum law;
- a fitted approximation is exact over all amplitudes;
- the benchmark includes `theta = pi` or proves behavior at the separatrix;
- the result covers damped, driven, finite-size, elastic, or laboratory
  pendulums;
- the candidate search was exhaustive;
- `RESULT-0017` is positive support for a formula;
- Gate B validation of the negative result independently validates the
  positive `RESULT-0013` metrics.

## Maintainer Decision Options

### Option 1: Leave The Claim In `DRAFT`

Choose this when the current wording is considered too broad or when the
maintainer does not want to ratify legacy positive results without an
independent replay.

- Claim impact: none.
- Knowledge impact: none.
- Blocker retained: Gate C wording and evidence review.
- Cost: the evidence remains usable, but the first pendulum claim does not
  advance beyond draft scientific memory.

### Option 2: Revise Wording And Keep `DRAFT`

Narrow the claim to the ideal mathematical pendulum and explicitly separate
the exact-reference qualitative statement from finite-range approximation
accuracy, but retain `DRAFT`.

Suggested wording:

> For the ideal mathematical pendulum benchmarked against the exact
> elliptic-integral reference, the period is amplitude-dependent. Within the
> sampled `EXP-0001` ranges, range-limited correction formulas improve on the
> small-angle approximation. This does not establish a globally exact
> approximation or a result for non-ideal pendulums.

- Claim impact: maintainer-authored wording change only; status remains
  `DRAFT`.
- Knowledge impact: none.
- Benefit: removes global/exact ambiguity before a later status decision.

### Option 3: Request Positive-Result Replay Before Promotion

Keep the claim in `DRAFT` and request an independent replay of
`RESULT-0013`, the strongest positive evidence. `RESULT-0017` already has Gate
B `PASS`, but that replay validates only the reproducibility of the negative
`OVERFITTED` result.

The replay should preserve the committed inputs and command, compare the
reported metrics under a declared tolerance, and leave the verdict and metrics
unchanged unless drift is recorded through the contested-result path.

- Claim impact: none until a later Gate C decision.
- Knowledge impact: none.
- Blocker cleared if successful: independent reproducibility of the strongest
  positive approximation result.
- Remaining blocker: maintainer Gate C wording and status review.

### Option 4: Promote A Tightly Scoped Statement After Gate C

This is the shortest policy-compliant route to a scoped conclusion. The
maintainer may revise the statement, update its result references, and move
`DRAFT -> PARTIALLY_SUPPORTED` in a maintainer-controlled change.

Suggested wording:

> For the ideal mathematical pendulum benchmarked against the exact
> elliptic-integral reference, the period is amplitude-dependent, and the
> small-angle approximation alone is not exact away from its limiting regime.
> Within the sampled `EXP-0001` amplitude ranges up to `3.10` rad,
> range-limited correction formulas improve approximation accuracy. The
> strongest referenced held-out result has maximum relative error
> `4.4038e-5` on `2.1839`-`3.1000` rad. This does not establish a globally
> exact approximation, validity at `theta = pi`, or a result for non-ideal
> pendulums.

Required maintainer actions:

1. Confirm the wording does not transfer the `RESULT-0013` tolerance outside
   its named held-out range.
2. Add the positive `RESULT-0013` reference and the negative boundary
   `RESULT-0017` reference to the claim evidence map as appropriate.
3. Record `PARTIALLY_SUPPORTED` only, not `SUPPORTED`.
4. Record maintainer Gate C review according to the current review-tier
   convention.

- Claim impact: maintainer-only transition to `PARTIALLY_SUPPORTED`.
- Knowledge impact: none; no `KNOW-*` creation or edit is justified.
- Remaining limitation: the strongest positive result is legacy untiered and
  has not received the independent Gate B replay recorded for `RESULT-0017`.

## Recommendation

Recommend **Option 4** only if the maintainer accepts the reproducible,
verification-passing legacy positive evidence for Gate C and adopts the
range/tolerance qualifiers above. `PARTIALLY_SUPPORTED` is the ceiling because
the evidence is benchmark-, model-, and range-limited.

If the maintainer requires independent replay of the strongest positive result
before endorsing a claim, choose **Option 3**, then return to Option 4 after a
successful replay. Option 2 is preferable to retaining the current wording
unchanged if no status decision is made.

## Blockers And Decision Boundary

- Agent blocker: agents cannot change an existing claim status in Phase 1.
- Promotion blocker: maintainer Gate C review is mandatory.
- Evidence-map blocker: the current claim references `RESULT-0001` and
  `RESULT-0003`, but not the strongest positive `RESULT-0013` or validated
  negative `RESULT-0017`.
- Replay caveat: `RESULT-0017` Gate B `PASS` does not substitute for a positive
  replay of `RESULT-0013`.
- Scope blocker: no available result supports exact all-amplitude,
  separatrix-inclusive, non-ideal, or real-laboratory wording.

## Output Routing

- Task verdict: `not_applicable` as a new scientific result; decision packet
  verdict is `MAINTAINER_DECISION_READY`.
- Canonical destination:
  `docs/reviews/claim-0001-pendulum-scoped-decision-options.md`.
- Review tier: `none`; this note is planning/review material, not a canonical
  `RESULT-*`, `CLAIM-*`, or `KNOW-*` artifact.
- Gate A status: not attempted; no result was created or changed.
- Gate B status: not attempted by this task; existing `RESULT-0017` Gate B
  status is `PASS`, while `RESULT-0013` has no independent replay recorded.
- Gate C status: pending maintainer decision.
- Claim impact: no claim file or status change in this task.
- Knowledge impact: no knowledge change.
- Result impact: no result change.
- Publication blocker: maintainer Gate C review and, if required by the
  maintainer, independent replay of `RESULT-0013`.

## Final Verdict

`CLAIM-0001` is eligible for a maintainer decision with
`PARTIALLY_SUPPORTED` as the maximum defensible status. Promotion is
supportable only with explicit ideal-system, sampled-range, approximation,
tolerance, and non-separatrix qualifiers; otherwise retain `DRAFT`.
