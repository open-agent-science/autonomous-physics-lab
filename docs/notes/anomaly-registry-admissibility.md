# Anomaly Registry Admissibility And Evaluation Contract

## Purpose

This note defines the admissibility rules for a future anomaly registry and
the evaluation contract that must exist before any joint anomaly fit can be
proposed.

It is a planning and safety artifact only. It does not add anomaly rows,
does not run a likelihood fit, does not move any WATCHLIST anomaly topic
into active evaluation, and does not promote claims.

Use this note with:

- [Anomaly Registry Campaign](../campaigns/anomaly-registry.md)
- [`data/anomalies/anomaly.schema.json`](../../data/anomalies/anomaly.schema.json)
- [Prediction Registry Policy](../prediction-registry-policy.md)
- [Negative Results Registry](../negative-results-registry.md)
- [Claim Promotion Policy](../claim-promotion-policy.md)
- [Blind Holdout Benchmark Protocol](../blind-holdout-benchmark-protocol.md)

## Entry Admissibility Rules

A future anomaly entry is admissible only when all of the following hold:

1. **Primary source class.** The source is a primary collaboration release,
   peer-reviewed measurement, canonical evaluation, or archived primary
   dataset. Secondary summaries, review articles, news posts, conference
   slides without archival backing, and LLM-recalled values are not
   admissible as the sole source.
2. **Observable definition.** The entry defines the exact observable,
   units, scheme, fiducial model, and scale where relevant. Broad labels
   such as "Hubble tension" or "muon anomaly" are not enough.
3. **Uncertainty semantics.** The source records uncertainty components and
   a combination rule. If covariance is required but unavailable, the entry
   is blocked or explicitly limited.
4. **Correlation handling.** Known correlations must be cited. Unknown
   correlations must be labelled as `UNKNOWN_BLOCKING` or
   `UNKNOWN_LIMITATION`; they must not be silently treated as independent.
5. **Holdout freeze.** The entry records the frozen value, freeze timestamp,
   source version, and later measurements excluded from candidate fitting.
6. **Status vocabulary.** Entries use one of `PROPOSED`, `FROZEN`, `LIVE`,
   `RESOLVED`, `DOWNGRADED`, `DISPUTED`, or `REJECTED`.
7. **No claim promotion.** Registry inclusion is not evidence that an
   anomaly is real, explanatory, or connected to any other anomaly.

If any required field is missing, the entry remains `BLOCKED_*` or
`WATCHLIST_ONLY` rather than being forced into the registry.

## Disallowed Source Shortcuts

The following are explicitly disallowed:

- copying central values from a secondary summary when the primary source is
  available;
- using a plot screenshot or social-media table as the only source;
- combining measurements with incompatible schemes or fiducial assumptions;
- treating asymmetric uncertainties as symmetric without a predeclared rule;
- dropping covariance because it makes the likelihood easier;
- fitting against values that were not frozen before model selection;
- treating a discrepancy count as a likelihood.

## Joint-Likelihood Evaluation Contract

A future task that proposes a joint anomaly fit must define the following
before running code:

| Contract item | Required content |
| --- | --- |
| Included entries | Exact `ANOM-*` ids and frozen registry commit. |
| Null model | Baseline model and source for each observable. |
| Candidate model | Equations, parameters, priors or bounds, and code path. |
| Free-parameter penalty | Fixed penalty rule such as AIC/BIC-style cost or a task-specific predeclared alternative. |
| Correlation treatment | Covariance matrices where known; blocking or limitation language where unknown. |
| Holdout split | Which measurements are fit inputs and which later measurements are reserved for evaluation. |
| Metrics | Log-likelihood delta, per-observable residuals, parameter penalty, and null-model comparison. |
| Negative-result rule | Explicit reporting when the candidate improves no tension, improves only one tension, or pays more parameters than it earns. |
| Claim boundary | No claim promotion in the fit task; promotion requires a separate maintainer-reviewed claim task. |

The evaluator must be deterministic Python or another reviewed deterministic
code path. LLM prose is allowed only to summarize validated outputs.

## Relationship To Other Registries

The anomaly registry does not replace existing APL registries:

- **Prediction registry:** stores prospective predictions or forecasts
  frozen before later comparison. An anomaly entry may later be paired with a
  prediction entry, but the two artifacts serve different roles.
- **Negative-results registry:** stores clean falsifications. A joint anomaly
  fit that fails should preserve its result there when it reaches canonical
  result quality.
- **Claims:** remain maintainer-reviewed scientific memory. A registry entry
  or failed fit does not automatically create or promote a claim.

## WATCHLIST Boundary

This task deliberately keeps the following topics in WATCHLIST:

- Hubble tension;
- muon g-2 follow-up;
- W-mass tension;
- broad physical-constants derivation;
- broad mass-relation searches.

Future tasks may cite this scaffold, but they must not start a fit or move a
specific anomaly into active work without a new maintainer-approved task.

## Stop Conditions

Stop before adding an entry or running a fit when:

- the only source is secondary-summary-only;
- the observable definition is ambiguous;
- uncertainty or covariance semantics are missing;
- the value was not frozen before candidate selection;
- the task would require claim-promotion or discovery-style language;
- multiple entries share data products but no correlation treatment exists;
- the model uses hidden or uncounted free parameters.

## Verdict Vocabulary

Use conservative readiness labels:

- `ADMISSIBLE`
- `ADMISSIBLE_WITH_LIMITATIONS`
- `BLOCKED_SOURCE_POLICY`
- `BLOCKED_CORRELATION_POLICY`
- `BLOCKED_HOLDOUT_POLICY`
- `WATCHLIST_ONLY`

For future evaluated fits, preserve negative outcomes explicitly:

- `NO_IMPROVEMENT`
- `ONE_TENSION_ONLY`
- `PARAMETER_PENALTY_DOMINATES`
- `CORRELATION_BLOCKED`
- `INCONCLUSIVE`

None of these labels is a discovery claim.
