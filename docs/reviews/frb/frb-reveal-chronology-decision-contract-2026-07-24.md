# FRB Reveal Chronology And Decision Contract — 2026-07-24

- Task: `TASK-1095`
- Campaign: `radio-transients-frb-pre-t-repeater-propensity`
- Registered prediction: `prediction_registry/radio_transients/PRED-0001.yaml`
- Contract verdict: `CONTRACT_READY_DUAL_CHRONOLOGY`
- Mode: planning-only, label-blind prediction preflight
- Claim issue: <https://github.com/open-agent-science/autonomous-physics-lab/issues/1669>

## Scope

This contract freezes the chronology classes and the one-shot interpretation
rule for a future reveal of `PRED-0001`. It does not choose or approve a
value-bearing reveal source, match any target, read any reveal value, or score
the prediction.

The contract preserves:

- prediction epoch `T=2019-07-02`;
- registration timestamp `2026-07-10T21:00:36Z`;
- all 479 registered target ids, point scores, and ranks;
- selected score `log1p(E_upper_hours + E_lower_hours)`;
- upper-transit comparator `log1p(E_upper_hours)`;
- lower-transit comparator `log1p(E_lower_hours)`;
- constant null `0.0`.

`PRED-0001`, its formula, target set, registration time, scores, ranks, and
payload digests are unchanged by this task.

## Inputs And Method

The chronology decision uses only committed prediction metadata, committed
official release metadata, and repository policy:

- `prediction_registry/radio_transients/PRED-0001.yaml`;
- `data/radio_transients/frb_pre_t_repeater_propensity_model_surface.yaml`;
- `data/radio_transients/frb_catalog2_source_manifest.yaml`;
- `docs/reviews/frb/frb-prediction-freeze-registration.md`;
- `docs/reviews/frb-reveal-source-admissibility-contract.md`;
- `docs/prospective-reveal-source-admissibility.md`;
- `docs/result-promotion-protocol.md`.

The method is a metadata-only chronology audit followed by a predeclared
paired-comparison design. No empirical tuning, label-prevalence estimate, or
outcome-dependent threshold enters the contract.

Code reference: no reveal-scoring code is added by this planning-only task.
The future deterministic implementation belongs to `TASK-1097`. This task
also makes the existing FRB registration writer use explicit LF newlines so
its frozen-byte reproducibility check is platform-independent.

## Frozen Chronology

| Event | Frozen timestamp or bound | Role |
| --- | --- | --- |
| Prediction epoch | `T=2019-07-02` | Separates pre-T prediction inputs from later repeat evidence. |
| Frozen model surface | `2026-07-09T00:00:00Z` | Records the selected score and comparators before registration. |
| Prediction registration | `2026-07-10T21:00:36Z` | Separates blinded-retrospective evidence from genuinely post-registration evidence. |
| Prediction anchor release | `2026-07-10T22:36:40Z` | Anchors the registered bytes; it is not a reveal-label source. |

The committed Catalog 2 metadata records an official CADC dataset identity,
DOI `10.11570/25.0066`, and a public checksum-pinned locator. Its metadata-only
manifest was generated on `2026-06-28T07:45:00Z`, before prediction
registration. That committed public-availability bound is sufficient to place
that exact snapshot in `public_before_registration`; its exact first-public
instant is not needed for the classification. Any comparison against that
snapshot can therefore be **blinded retrospective at best**, even if the APL
executor has a clean no-peek session.

## Evidence-Class Rules

Every approved reveal source must receive exactly one chronology class before
target matching or value access:

| Chronology class | Required metadata condition | Permitted interpretation |
| --- | --- | --- |
| `public_before_registration` | A stable official locator, release record, repository record, DOI metadata, or committed public-access bound demonstrates availability before `2026-07-10T21:00:36Z`. | `BLINDED_RETROSPECTIVE` only. Clean execution does not make already-public evidence prospective. |
| `first_public_after_registration` | Direct official metadata proves that the exact source version first became public strictly after `2026-07-10T21:00:36Z`, with no earlier public version carrying the same evidence. | `PROSPECTIVE_POST_REGISTRATION` for that source version only. |
| `timing_ambiguous` | First-public timing is missing, conflicting, version-ambiguous, or cannot distinguish an earlier public evidence surface from a later mirror or revision. | Stop before target matching and return `HOLD_SOURCE_TIMING_AMBIGUOUS`. |

Evidence must also be strictly post-T under the timestamp semantics frozen by
the approved source manifest. Evidence at or before `T` is ineligible for the
future comparison regardless of registration chronology.

If one future source contains both pre-registration-public and genuinely
post-registration-first-public strata, the strata must be reported separately.
They must not be pooled into a prospective headline. The primary result takes
the weaker `BLINDED_RETROSPECTIVE` evidence class unless the approved manifest
defines and preserves a standalone post-registration stratum before values are
read.

## Source And Matching Gates

`TASK-1096` must freeze exactly one metadata-only source manifest in a clean
session before any of the 479 targets are matched. The manifest must satisfy
the shared prospective-reveal policy and the FRB domain contract, including
official identity, version, chronology class, rights, checksum or immutable
record, schema semantics, target keys, association rules, ambiguity handling,
and parser identity.

The future reveal must stop before scoring if:

1. source timing is `timing_ambiguous`;
2. values or target matches were visible before manifest approval;
3. the approved source, parser, registry commit, prediction digest, or target
   payload drifts;
4. matching requires fuzzy or outcome-informed association;
5. any score, rank, target, formula, comparator, or threshold would change;
6. the minimum-information gates below are not met.

## Frozen Primary Comparison

### Analysis population

The primary analysis uses only eligible targets matched by the approved
manifest and the predeclared identity rules. Missing, ambiguous, ineligible,
and unrevealed targets remain in a complete eligibility ledger and are not
silently dropped.

Minimum information is frozen as:

- matched eligible coverage: at least `384 / 479` targets (the ceiling of
  80% coverage);
- positive post-T evidence: at least `20` eligible targets;
- comparison class: at least `20` eligible targets without post-T evidence as
  of the pinned source version.

Failure of any minimum-information gate yields `INCONCLUSIVE` without a
predictive-success interpretation.

### Primary metric

The sole primary metric is rank AUC. For a positive-negative target pair:

- concordant score order contributes `1`;
- discordant score order contributes `0`;
- an equal-score tie contributes `0.5`.

This definition is applied identically to the selected total-exposure score,
both frozen single-transit comparators, and the constant null. With both
outcome classes present, the constant-null AUC is `0.5`.

The three required paired primary contrasts are:

1. `AUC(total exposure) - AUC(upper transit only)`;
2. `AUC(total exposure) - AUC(lower transit only)`;
3. `AUC(total exposure) - AUC(constant null)`.

Success cannot be selected against whichever comparator is easiest after
reveal. All three contrasts are mandatory.

### Minimum effects and uncertainty

The frozen minimum effects are:

- at least `0.02` AUC above the upper-transit comparator;
- at least `0.02` AUC above the lower-transit comparator;
- at least `0.05` AUC above the constant null, equivalent to selected AUC of
  at least `0.55`.

Uncertainty uses a paired stratified bootstrap:

- deterministic seed: `1095`;
- `20,000` replicates;
- resample eligible positive targets with replacement within the positive
  stratum and eligible comparison targets with replacement within the
  comparison stratum;
- keep all four frozen score columns paired within each sampled target;
- recompute all four AUC values and all three contrasts in every replicate.

The three primary contrasts form one multiplicity family. Use one-sided
Bonferroni-corrected percentile-bootstrap lower confidence bounds at familywise
alpha `0.05`: for each contrast, the lower bound is the `1.666666...` percentile
of its bootstrap distribution, giving `98.333333...%` one-sided confidence.
No secondary metric can rescue a failed or inconclusive primary rule.

## Exact Future Verdict Mapping

Apply these rules in order:

1. If chronology is ambiguous or a source/no-peek/identity gate fails, do not
   score; return the applicable pre-score blocker.
2. If any minimum-information gate fails, return `INCONCLUSIVE`.
3. Return `PASS` only when the simultaneous lower bound for every primary
   contrast is strictly above its frozen minimum effect.
4. Return `FAIL` when the selected point AUC is at or below `0.5`, or when its
   point AUC is at or below either single-transit comparator.
5. Otherwise return `INCONCLUSIVE`.

Future repository routing maps a mechanically complete `PASS` to a scoped
`VALID_IN_RANGE` result, `FAIL` to `INVALID`, and the primary
`INCONCLUSIVE` outcome to `INCONCLUSIVE`. These result words describe one
observation/detection ranking on one pinned source; they do not establish
intrinsic repeater propensity or FRB physics.

## Secondary Outputs

Average precision and top-k positive counts for `k in {10, 25, 50}` remain
secondary descriptive outputs for all four frozen scores.

- Average precision is computed over complete equal-score threshold blocks;
  tied targets enter the same threshold block.
- Top-k counts use the already registered frozen rank order; ranks are not
  recomputed after reveal.
- All comparator, null, negative, and inconclusive outputs are preserved.
- Secondary metrics have no PASS/FAIL role and cannot override the primary
  verdict.

## No-Label Attestation

This task did not fetch or open the value-bearing Catalog 2 bytes or any other
reveal source. It did not inspect, search for, summarize, count, match, or infer
per-target repeat labels, repeat outcomes, or repeat-evidence values. It did
not inspect web-search snippets. Only committed prediction metadata and
committed official source/release metadata were used.

No label prevalence, matched coverage outcome, positive count, target
association, reveal metric, or score comparison was available when the
chronology classes, minimum-information gates, metric, thresholds,
uncertainty method, multiplicity rule, and verdict mapping were frozen.

## Limitations And No-Claim Boundary

- The current Catalog 2 snapshot is eligible only for blinded-retrospective
  evidence because its public availability predates registration.
- A genuinely prospective comparison remains possible only for an exact
  source version proven first public after registration.
- The fixed sample and information thresholds are design choices made before
  labels; they do not guarantee power for every future prevalence.
- AUC tests ranking discrimination, not calibrated probability, causal
  exposure effects, intrinsic source behavior, or population prevalence.
- This contract does not show that exposure predicts repetition, identify any
  repeater, establish intrinsic FRB physics, or convert pre-registration public
  evidence into prospective evidence.

## Output Routing

- Task verdict: `CONTRACT_READY_DUAL_CHRONOLOGY`.
- Canonical destination:
  `docs/reviews/frb/frb-reveal-chronology-decision-contract-2026-07-24.md`.
- Review tier: `none` — planning contract, not a RESULT or PRED promotion.
- Prediction impact: none; `PRED-0001` remains registered and byte-unchanged.
- Future source-manifest gate: `TASK-1096` remains required and must merge
  before any target matching or value access.
- Future result evidence class: `BLINDED_RETROSPECTIVE` for the current
  pre-registration-public snapshot; `PROSPECTIVE_POST_REGISTRATION` only for a
  separately pinned source proven first public after registration.
- Gate A: not applicable; no result or prediction artifact is produced.
- Gate B: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Publication blockers: no source manifest approved for reveal, no value-access
  approval, and no one-shot `TASK-1097` comparison has run.
